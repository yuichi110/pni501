# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for LOC, module inventory, cognitive complexity, global state, and bug idioms."""

from __future__ import annotations

import contextlib
from abc import ABC, abstractmethod
from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.models import (
    MAX_BRANCH_COUNT,
    MAX_CALLABLE_PARAMS,
    MAX_COGNITIVE_COMPLEXITY,
    MAX_FUNCTION_LINES,
    CodeLocation,
    ModuleAstSummary,
    ParsedUnit,
    QualityResult,
)

_NESTED_CALLABLE_BOUNDARY_KINDS: Final[frozenset[str]] = frozenset(
    {
        "function_definition",
        "method_declaration",
        "constructor_declaration",
        "anonymous_class",
    }
)


def _is_owned_by_callable(node: SgNode, callable_start_index: int) -> bool:
    """Return True if `node` is not enclosed by a nested callable or anonymous class inside the outer callable."""
    curr = node.parent()
    while curr is not None and curr.range().start.index > callable_start_index:
        if curr.kind() in _NESTED_CALLABLE_BOUNDARY_KINDS:
            return False
        curr = curr.parent()
    return True


def _effective_callable_lines(node: SgNode) -> int:
    """Return line span of `node` excluding lines belonging to nested `method_declaration` or `anonymous_class`."""
    total_lines = node.range().end.line - node.range().start.line + 1
    if node.kind() != "method_declaration":
        return total_lines
    callable_start = node.range().start.index
    nested_lines: set[int] = set()
    for nkind in ("method_declaration", "anonymous_class"):
        with contextlib.suppress(RuntimeError):
            for sub in node.find_all(kind=nkind):
                if sub.range().start.index <= callable_start:
                    continue
                nested_lines.update(range(sub.range().start.line + 1, sub.range().end.line + 1))
    return max(1, total_lines - len(nested_lines))


class BaseQualityChecker(ABC):
    """Template-method base class for language code-quality, complexity, and bug-risk checkers."""

    branch_node_kinds: ClassVar[frozenset[str]]
    nesting_node_kinds: ClassVar[frozenset[str]] = frozenset()
    max_function_lines: ClassVar[int] = MAX_FUNCTION_LINES
    max_branch_count: ClassVar[int] = MAX_BRANCH_COUNT
    max_cognitive_complexity: ClassVar[int] = MAX_COGNITIVE_COMPLEXITY
    max_callable_params: ClassVar[int] = MAX_CALLABLE_PARAMS

    def check(self, units: list[ParsedUnit]) -> QualityResult:
        """Evaluate LOC, module inventory, complexity, parameter count, global state, and bug idioms.

        Args:
            units: Parsed compilation units in the target project.

        Returns:
            QualityResult: Aggregated deterministic quality metrics and hotspot locations.
        """
        total_loc = 0
        total_classes = 0
        total_functions = 0
        inventory: list[ModuleAstSummary] = []
        complex_functions: list[CodeLocation] = []
        excessive_parameters: list[CodeLocation] = []
        global_usages: list[CodeLocation] = []
        bug_idioms: list[CodeLocation] = []

        for unit in units:
            loc = self.count_loc(unit)
            total_loc += loc
            total_classes += self.count_classes(unit)
            callables = self.iter_callables(unit)
            total_functions += len(callables)
            pub_types, pub_callables = self.extract_public_symbols(unit)
            inventory.append(
                ModuleAstSummary(
                    file=unit.rel_path,
                    loc=loc,
                    public_types=pub_types,
                    public_callables=pub_callables,
                )
            )
            for symbol, node in callables:
                complex_loc = self.evaluate_complexity(node, symbol, unit.rel_path)
                if complex_loc is not None:
                    complex_functions.append(complex_loc)
                param_count = self.count_callable_params(node)
                if param_count > self.max_callable_params:
                    excessive_parameters.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=node.range().start.line + 1,
                            symbol=symbol,
                            detail=f"params={param_count} (> {self.max_callable_params}, SIG Unit Interfacing)",
                        )
                    )
            global_usages.extend(self.find_global_state(unit))
            bug_idioms.extend(self.find_bug_risk_idioms(unit))

        return QualityResult(
            total_loc=total_loc,
            total_classes=total_classes,
            total_functions=total_functions,
            module_inventory=inventory,
            complex_functions=complex_functions,
            excessive_parameters=excessive_parameters,
            global_state_usages=global_usages,
            bug_risk_idioms=bug_idioms,
        )

    def compute_cognitive_complexity(self, node: SgNode) -> int:
        """Compute nesting-weighted cognitive complexity for a callable CST node."""
        nesting_kinds = self.nesting_node_kinds or self.branch_node_kinds
        callable_start = node.range().start.index
        score = 0
        for bkind in self.branch_node_kinds:
            for bnode in node.find_all(kind=bkind):
                if not _is_owned_by_callable(bnode, callable_start):
                    continue
                depth = 0
                curr = bnode.parent()
                while curr is not None and curr.range().start.index > callable_start:
                    if curr.kind() in nesting_kinds:
                        depth += 1
                    curr = curr.parent()
                score += 1 + depth
        return score

    def evaluate_complexity(self, node: SgNode, symbol: str, rel_path: str) -> CodeLocation | None:
        """Check whether a callable exceeds line length, McCabe branch, or cognitive thresholds."""
        callable_start = node.range().start.index
        func_len = _effective_callable_lines(node)
        branches = sum(
            1
            for bkind in self.branch_node_kinds
            for bnode in node.find_all(kind=bkind)
            if _is_owned_by_callable(bnode, callable_start)
        )
        cognitive = self.compute_cognitive_complexity(node)
        if (
            func_len > self.max_function_lines
            or branches > self.max_branch_count
            or cognitive > self.max_cognitive_complexity
        ):
            return CodeLocation(
                file=rel_path,
                line=node.range().start.line + 1,
                symbol=symbol,
                detail=f"length={func_len} lines, branches={branches}, cognitive={cognitive}",
            )
        return None

    def count_callable_params(self, node: SgNode) -> int:
        """Count effective parameters on a callable CST node (excluding receiver 'self'/'cls')."""
        _ = node
        return 0

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Extract sorted (public_type_names, public_callable_names) for module_inventory."""
        _ = unit
        return [], []

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Return language-specific bug-risk or dangerous API anti-patterns in unit."""
        _ = unit
        return []

    @abstractmethod
    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment source lines in unit."""

    @abstractmethod
    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class/interface/enum/record type declarations in unit."""

    @abstractmethod
    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return (symbol_name, cst_node) pairs for all functions/methods/constructors in unit."""

    @abstractmethod
    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Return mutable global or non-final static state usages in unit."""
