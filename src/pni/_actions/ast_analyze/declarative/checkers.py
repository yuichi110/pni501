# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative profile-driven AST checker implementations for all Tier A/B/C languages."""

from __future__ import annotations

import re
from pathlib import Path
from typing import ClassVar, Final

from pni._actions.ast_analyze._cst import CstNode
from pni._actions.ast_analyze.base import (
    BaseDependencyChecker,
    BaseDocChecker,
    BaseImportChecker,
    BaseOperationalChecker,
    BaseQualityChecker,
    BaseSecurityChecker,
    BaseTestChecker,
    BaseTypingChecker,
)
from pni._actions.ast_analyze.declarative.profile import (
    CustomHookResult,
    CweSinkRule,
    LanguageGrammarProfile,
)
from pni._actions.ast_analyze.models import (
    ApiEndpointFact,
    CodeLocation,
    DependencyResult,
    DocResult,
    ImportResult,
    ParsedUnit,
    QualityResult,
    SecuritySinkLocation,
    TestAstResult,
    TypingResult,
    UnitDocStats,
    UnitImportStats,
    UnitTypingStats,
)
from pni._actions.ast_analyze.runner import LanguageAnalyzerSuite

_IDENT_RE: Final[re.Pattern[str]] = re.compile(r"[A-Za-z_][A-Za-z0-9_$-]*")
_IMPORT_PATH_RE: Final[re.Pattern[str]] = re.compile(r"""['"]([^'"]+)['"]|\b([A-Za-z_][A-Za-z0-9_.:/-]*)""")
_TEST_FN_NAME_RE: Final[re.Pattern[str]] = re.compile(r"(?i)^(?:test|spec|should|it_|check_)|(?:_test|_spec|test)$")


def _run_hook(profile: LanguageGrammarProfile, unit: ParsedUnit) -> CustomHookResult:
    """Invoke optional language-specific custom CST hook."""
    if profile.custom_hook is None:
        return CustomHookResult()
    return profile.custom_hook(unit)


_WRAPPER_NAME_KINDS: Final[frozenset[str]] = frozenset(
    {
        "function_declarator",
        "function_declaration_left",
        "function_signature",
        "procedure_specification",
        "defun_header",
        "signature",
    }
)


def _extract_symbol_from_fields(node: CstNode, profile: LanguageGrammarProfile) -> str | None:
    """Try extracting a symbol identifier from grammar-named fields on node."""
    for field_name in profile.callable_name_fields:
        sub = node.field(field_name)
        if sub is None:
            continue
        if sub.kind() in {"function_declarator", "pointer_declarator"}:
            inner = sub.field("declarator") or sub.find(kind="identifier") or sub.find(kind="field_identifier")
            if inner is not None:
                return inner.text().strip()
        txt = sub.text().strip()
        if txt:
            m = _IDENT_RE.search(txt)
            return m.group(0) if m else txt[:48]
    return None


def _extract_symbol_from_children(node: CstNode, profile: LanguageGrammarProfile) -> str | None:
    """Try extracting a symbol identifier from direct or wrapped child nodes."""
    for child in node.named_children():
        if child.kind() in profile.callable_name_child_kinds and child.text().strip():
            return child.text().strip()[:48]
        if child.kind() not in _WRAPPER_NAME_KINDS:
            continue
        for nested_kind in profile.callable_name_child_kinds:
            found = child.find(kind=nested_kind)
            if found is not None and found.text().strip():
                return found.text().strip()[:48]
    return None


def _extract_symbol_name(node: CstNode, profile: LanguageGrammarProfile) -> str:
    """Extract a readable symbol identifier from a declaration CST node."""
    from_field = _extract_symbol_from_fields(node, profile)
    if from_field:
        return from_field
    from_child = _extract_symbol_from_children(node, profile)
    if from_child:
        return from_child
    first_line = node.text().splitlines()[0] if node.text() else ""
    m = _IDENT_RE.search(first_line)
    return m.group(0) if m else node.kind()


def _iter_macro_declarations(
    unit: ParsedUnit,
    target_macros: tuple[str, ...],
    call_kind: str,
) -> list[tuple[str, CstNode]]:
    """Extract macro-defined classes/callables (e.g., Elixir defmodule/def/defp)."""
    if not target_macros:
        return []
    wanted = set(target_macros)
    results: list[tuple[str, CstNode]] = []
    for call in unit.root.find_all(kind=call_kind):
        children = call.named_children()
        if not children:
            continue
        macro_name = children[0].text().strip()
        if macro_name not in wanted:
            continue
        sym = macro_name
        if len(children) > 1:
            arg_txt = children[1].text().strip()
            m = _IDENT_RE.search(arg_txt)
            if m:
                sym = m.group(0)
        results.append((sym, call))
    return results


def _iter_profile_callables(unit: ParsedUnit, profile: LanguageGrammarProfile) -> list[tuple[str, CstNode]]:
    """Collect (symbol_name, cst_node) pairs for all callable declarations in unit."""
    items: list[tuple[str, CstNode]] = []
    seen_spans: set[tuple[int, int]] = set()
    for ckind in profile.callable_node_kinds:
        for node in unit.root.find_all(kind=ckind):
            span = (node.range().start.index, node.range().end.index)
            if span in seen_spans:
                continue
            seen_spans.add(span)
            items.append((_extract_symbol_name(node, profile), node))
    for sym, node in _iter_macro_declarations(unit, profile.macro_callable_names, profile.macro_call_node_kind):
        span = (node.range().start.index, node.range().end.index)
        if span not in seen_spans:
            seen_spans.add(span)
            items.append((sym, node))
    return items


def _iter_profile_classes(unit: ParsedUnit, profile: LanguageGrammarProfile) -> list[tuple[str, CstNode]]:
    """Collect (symbol_name, cst_node) pairs for all class/struct/module declarations in unit."""
    items: list[tuple[str, CstNode]] = []
    seen_spans: set[tuple[int, int]] = set()
    for ckind in profile.class_node_kinds:
        for node in unit.root.find_all(kind=ckind):
            span = (node.range().start.index, node.range().end.index)
            if span in seen_spans:
                continue
            seen_spans.add(span)
            items.append((_extract_symbol_name(node, profile), node))
    for sym, node in _iter_macro_declarations(unit, profile.macro_class_names, profile.macro_call_node_kind):
        span = (node.range().start.index, node.range().end.index)
        if span not in seen_spans:
            seen_spans.add(span)
            items.append((sym, node))
    return items


class DeclarativeImportChecker(BaseImportChecker):
    """Profile-driven import hygiene checker detecting wildcard imports and sorting hygiene."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind checker to a LanguageGrammarProfile."""
        self._profile = profile

    def check(self, units: list[ParsedUnit], project_root: Path) -> ImportResult:
        """Skip import checks when profile marks imports as not applicable."""
        if not self._profile.import_applicable:
            return ImportResult(import_hygiene_coverage_pct=None)
        return super().check(units, project_root)

    def inspect_unit_imports(self, unit: ParsedUnit, root_packages: set[str]) -> UnitImportStats:
        """Inspect import statements in unit for wildcard imports."""
        _ = root_packages
        wildcards: list[CodeLocation] = []
        seen_lines: set[int] = set()

        for wkind in self._profile.wildcard_import_kinds:
            for node in unit.root.find_all(kind=wkind):
                line_no = node.range().start.line + 1
                if line_no not in seen_lines:
                    seen_lines.add(line_no)
                    wildcards.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=node.text().strip()[:40],
                            detail="Wildcard import pollutes namespace and obscures symbol provenance",
                        )
                    )

        if self._profile.wildcard_import_pattern is not None:
            for ikind in self._profile.import_node_kinds:
                for node in unit.root.find_all(kind=ikind):
                    line_no = node.range().start.line + 1
                    if line_no not in seen_lines and self._profile.wildcard_import_pattern.search(node.text()):
                        seen_lines.add(line_no)
                        wildcards.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=node.text().splitlines()[0].strip()[:40],
                                detail="Wildcard import pollutes namespace and obscures symbol provenance",
                            )
                        )

        return UnitImportStats(is_clean=not wildcards, wildcard_imports=wildcards)


class DeclarativeQualityChecker(BaseQualityChecker):
    """Profile-driven LOC, symbol inventory, complexity, parameter, global-state, and bug-idiom checker."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset()

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind quality checker to profile CST node definitions."""
        self._profile = profile
        self._branch_kinds: frozenset[str] = frozenset(profile.branch_node_kinds)
        self._nesting_kinds: frozenset[str] = frozenset(profile.nesting_node_kinds or profile.branch_node_kinds)

    def compute_cognitive_complexity(self, node: CstNode) -> int:
        """Compute nesting-weighted cognitive complexity using profile branch/nesting CST kinds."""
        callable_start = node.range().start.index
        score = 0
        for bkind in self._branch_kinds:
            for bnode in node.find_all(kind=bkind):
                depth = 0
                curr = bnode.parent()
                while curr is not None and curr.range().start.index > callable_start:
                    if curr.kind() in self._nesting_kinds:
                        depth += 1
                    curr = curr.parent()
                score += 1 + depth
        return score

    def evaluate_complexity(self, node: CstNode, symbol: str, rel_path: str) -> CodeLocation | None:
        """Check whether a callable exceeds line length, McCabe branch, or cognitive thresholds."""
        func_len = self.effective_callable_lines(node)
        branches = sum(len(node.find_all(kind=bkind)) for bkind in self._branch_kinds)
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

    def check(self, units: list[ParsedUnit]) -> QualityResult:
        """Execute BaseQualityChecker pipeline and merge optional custom hook findings."""
        base_res = super().check(units)
        if self._profile.custom_hook is None:
            return base_res

        extra_classes = 0
        extra_functions = 0
        complex_fns = list(base_res.complex_functions)
        excessive_params = list(base_res.excessive_parameters)
        globals_found = list(base_res.global_state_usages)
        idioms = list(base_res.bug_risk_idioms)
        inventory = list(base_res.module_inventory)
        inv_by_file = {item.file: idx for idx, item in enumerate(inventory)}

        for unit in units:
            hook = _run_hook(self._profile, unit)
            extra_classes += hook.extra_classes
            extra_functions += hook.extra_functions
            complex_fns.extend(hook.complex_functions)
            excessive_params.extend(hook.excessive_parameters)
            globals_found.extend(hook.global_state_usages)
            idioms.extend(hook.bug_risk_idioms)
            if (hook.extra_public_types or hook.extra_public_callables) and unit.rel_path in inv_by_file:
                idx = inv_by_file[unit.rel_path]
                existing = inventory[idx]
                inventory[idx] = existing.model_copy(
                    update={
                        "public_types": sorted(set([*existing.public_types, *hook.extra_public_types])),
                        "public_callables": sorted(set([*existing.public_callables, *hook.extra_public_callables])),
                    }
                )

        return QualityResult(
            total_loc=base_res.total_loc,
            total_classes=base_res.total_classes + extra_classes,
            total_functions=base_res.total_functions + extra_functions,
            module_inventory=inventory,
            complex_functions=complex_fns,
            excessive_parameters=excessive_params,
            global_state_usages=globals_found,
            bug_risk_idioms=idioms,
        )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment source lines using profile comment delimiters."""
        loc = 0
        in_block = False
        b_start = self._profile.block_comment_start
        b_end = self._profile.block_comment_end
        prefixes = self._profile.comment_prefixes

        for raw in unit.source.splitlines():
            s = raw.strip()
            if not s:
                continue
            if in_block:
                if b_end and b_end in s:
                    in_block = False
                continue
            if b_start and s.startswith(b_start):
                if not b_end or b_end not in s[len(b_start) :]:
                    in_block = True
                continue
            if prefixes and any(s.startswith(pfx) for pfx in prefixes):
                continue
            loc += 1
        return loc

    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class/struct/interface/module declarations matching profile kinds."""
        return len(_iter_profile_classes(unit, self._profile))

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, CstNode]]:
        """Return (symbol_name, cst_node) pairs for all functions/methods/procedures."""
        return _iter_profile_callables(unit, self._profile)

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Extract sorted public type and callable names for architecture inventory."""
        types = sorted(
            {name for name, _ in _iter_profile_classes(unit, self._profile) if name and not name.startswith("_")}
        )
        callables = sorted(
            {name for name, _ in _iter_profile_callables(unit, self._profile) if name and not name.startswith("_")}
        )
        return types, callables

    def count_callable_params(self, node: CstNode) -> int:
        """Count effective parameters on a callable CST node excluding receiver self/this."""
        for pkind in self._profile.param_container_kinds:
            container = node.find(kind=pkind)
            if container is None:
                continue
            if self._profile.param_item_kinds:
                items = [
                    p
                    for p in container.named_children()
                    if p.kind() in self._profile.param_item_kinds
                    and p.text().strip() not in self._profile.self_param_names
                ]
                if items:
                    return len(items)
            named = [c for c in container.named_children() if c.text().strip() not in self._profile.self_param_names]
            return len(named)
        if self._profile.param_item_kinds:
            direct = [
                c
                for c in node.named_children()
                if c.kind() in self._profile.param_item_kinds
                and c.text().strip() not in self._profile.self_param_names
            ]
            if direct:
                return len(direct)
        return 0

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect mutable global state declarations via CST node kinds or regex pattern."""
        found: list[CodeLocation] = []
        seen_lines: set[int] = set()
        for gkind in self._profile.global_state_node_kinds:
            for node in unit.root.find_all(kind=gkind):
                line_no = node.range().start.line + 1
                if line_no in seen_lines:
                    continue
                if self._profile.global_state_pattern is not None and not self._profile.global_state_pattern.search(
                    node.text()
                ):
                    continue
                seen_lines.add(line_no)
                found.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol=_extract_symbol_name(node, self._profile),
                        detail="Mutable global/static state reduces testability and concurrency safety",
                    )
                )
        return found

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Evaluate declarative bug-risk idiom rules across CST nodes or source lines."""
        found: list[CodeLocation] = []
        for rule in self._profile.bug_idiom_rules:
            if rule.node_kinds:
                for nkind in rule.node_kinds:
                    for node in unit.root.find_all(kind=nkind):
                        if rule.pattern.search(node.text()):
                            found.append(
                                CodeLocation(
                                    file=unit.rel_path,
                                    line=node.range().start.line + 1,
                                    symbol=rule.symbol or nkind,
                                    detail=rule.detail,
                                )
                            )
            else:
                for line_no, line in enumerate(unit.source.splitlines(), start=1):
                    stripped = line.strip()
                    if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                        continue
                    if rule.pattern.search(line):
                        found.append(
                            CodeLocation(
                                file=unit.rel_path,
                                line=line_no,
                                symbol=rule.symbol or self._profile.language_id,
                                detail=rule.detail,
                            )
                        )
        return found


class DeclarativeTypingChecker(BaseTypingChecker):
    """Profile-driven type-safety checker for weak types and unscoped suppression pragmas."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind typing checker to profile applicability and escape-hatch patterns."""
        self._profile = profile

    def check(self, units: list[ParsedUnit]) -> TypingResult:
        """Skip typing checks when profile marks static typing as not applicable."""
        if not self._profile.typing_applicable:
            return TypingResult(type_safety_coverage_pct=None)
        return super().check(units)

    def inspect_unit_typing(self, unit: ParsedUnit) -> UnitTypingStats:
        """Inspect weak type usages and unscoped compiler/type-checker suppressions."""
        callables = _iter_profile_callables(unit, self._profile)
        weak: list[CodeLocation] = []
        ignores: list[CodeLocation] = []

        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if self._profile.type_ignore_pattern is not None and self._profile.type_ignore_pattern.search(line):
                ignores.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="suppress",
                        detail="Unscoped static-analysis or type-safety suppression directive",
                    )
                )
            if any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            if self._profile.weak_type_pattern is not None:
                m = self._profile.weak_type_pattern.search(line)
                if m is not None:
                    weak.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=m.group(0).strip()[:32],
                            detail="Weak or unchecked type escape hatch weakens static guarantees",
                        )
                    )

        total = len(callables)
        safe = max(0, total - len(weak))
        return UnitTypingStats(
            total_callables=total,
            type_safe_callables=safe,
            weak_type_usages=weak,
            unscoped_type_ignores=ignores,
        )


class DeclarativeDocChecker(BaseDocChecker):
    """Profile-driven documentation comment coverage checker above public types and callables."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind doc checker to profile comment conventions."""
        self._profile = profile

    def check(self, units: list[ParsedUnit]) -> DocResult:
        """Skip doc checks when profile marks documentation comments as not applicable."""
        if not self._profile.doc_applicable:
            return DocResult(docstring_coverage_pct=None)
        return super().check(units)

    def _has_preceding_doc(self, lines: list[str], start_line_0: int) -> bool:
        """Return True if a doc or comment line appears immediately above start_line_0."""
        idx = start_line_0 - 1
        while idx >= 0 and not lines[idx].strip():
            idx -= 1
            if start_line_0 - idx > 2:
                return False
        if idx < 0:
            return False
        prev = lines[idx].strip()
        all_prefixes = (*self._profile.doc_comment_prefixes, *self._profile.comment_prefixes)
        if any(prev.startswith(p) for p in all_prefixes):
            return True
        return bool(self._profile.block_comment_end and prev.endswith(self._profile.block_comment_end))

    def inspect_unit_docs(self, unit: ParsedUnit) -> UnitDocStats:
        """Count public declarations and check for adjacent header/doc comments."""
        lines = unit.source.splitlines()
        targets = [
            *[(name, node) for name, node in _iter_profile_classes(unit, self._profile) if not name.startswith("_")],
            *[(name, node) for name, node in _iter_profile_callables(unit, self._profile) if not name.startswith("_")],
        ]
        documented = 0
        missing: list[CodeLocation] = []
        for name, node in targets:
            line0 = node.range().start.line
            if self._has_preceding_doc(lines, line0):
                documented += 1
            else:
                missing.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line0 + 1,
                        symbol=name,
                        detail="Missing doc comment on public declaration",
                    )
                )
        return UnitDocStats(
            candidates=len(targets),
            documented=documented,
            missing_docstrings=missing,
        )


class DeclarativeDependencyChecker(BaseDependencyChecker):
    """Profile-driven internal import graph builder supporting Tarjan SCC cycle detection."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind dependency checker to language import node kinds."""
        self._profile = profile

    def check(self, units: list[ParsedUnit], project_root: Path) -> DependencyResult:
        """Skip cycle checks when profile marks imports as not applicable."""
        if not self._profile.import_applicable:
            return DependencyResult()
        return super().check(units, project_root)

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Build sorted internal module adjacency graph from CST import statements and hooks."""
        _ = project_root
        module_by_stem: dict[str, str] = {}
        for unit in units:
            mod_id = Path(unit.rel_path).with_suffix("").as_posix()
            module_by_stem[Path(unit.rel_path).stem.lower()] = mod_id
            module_by_stem[mod_id.lower()] = mod_id

        graph: dict[str, list[str]] = {}
        for unit in units:
            src_mod = Path(unit.rel_path).with_suffix("").as_posix()
            edges: set[str] = set()
            for ikind in self._profile.import_node_kinds:
                for node in unit.root.find_all(kind=ikind):
                    for m in _IMPORT_PATH_RE.finditer(node.text()):
                        tok = (m.group(1) or m.group(2) or "").strip().lower()
                        leaf = tok.rsplit("/", 1)[-1].rsplit("::", 1)[-1].rsplit(".", 1)[-1]
                        target = module_by_stem.get(tok) or module_by_stem.get(leaf)
                        if target is not None and target != src_mod:
                            edges.add(target)
            hook = _run_hook(self._profile, unit)
            for target_tok in hook.import_targets:
                target = module_by_stem.get(target_tok.lower())
                if target is not None and target != src_mod:
                    edges.add(target)
            graph[src_mod] = sorted(edges)
        return graph


class DeclarativeTestChecker(BaseTestChecker):
    """Profile-driven test-suite health checker verifying assertion presence and module coverage."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind test checker to language assertion patterns."""
        self._profile = profile

    def check(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Skip test inspection when not applicable or when no test units exist."""
        if not self._profile.test_applicable or not test_units:
            return TestAstResult()
        return super().check(test_units, source_units, project_root)

    def inspect_test_suite(
        self,
        test_units: list[ParsedUnit],
        source_units: list[ParsedUnit],
        project_root: Path,
    ) -> TestAstResult:
        """Count test callables, flag assertion-free tests, and estimate source module coverage."""
        _ = project_root
        test_count = 0
        assertion_free: list[CodeLocation] = []
        assert_re = self._profile.assertion_pattern or re.compile(
            r"(?i)\b(?:assert|expect|should|check|verify|require|equal|fail)\w*\b"
        )
        all_test_text = "\n".join(u.source.lower() for u in test_units)

        for unit in test_units:
            callables = _iter_profile_callables(unit, self._profile)
            for name, node in callables:
                if not _TEST_FN_NAME_RE.search(name):
                    continue
                test_count += 1
                if not assert_re.search(node.text()):
                    assertion_free.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=node.range().start.line + 1,
                            symbol=name,
                            detail="Test callable contains no detectable assertion statement",
                        )
                    )

        src_stems = [Path(u.rel_path).stem.lower() for u in source_units if Path(u.rel_path).stem != "__init__"]
        covered = sum(1 for stem in src_stems if stem and stem in all_test_text)
        cov_pct = round((covered / len(src_stems)) * 100.0, 1) if src_stems else None
        return TestAstResult(
            test_functions_count=test_count,
            module_test_coverage_pct=cov_pct,
            assertion_free_tests=assertion_free,
        )


class DeclarativeOperationalChecker(BaseOperationalChecker):
    """Profile-driven 12-Factor, SRE PRR, and OWASP ASVS operational signal checker."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind operational checker to language-specific network/env/logging/secret patterns."""
        self._profile = profile

    def find_missing_io_timeouts(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Flag external HTTP/network calls missing an explicit timeout token."""
        found: list[CodeLocation] = list(_run_hook(self._profile, unit).missing_io_timeouts)
        if self._profile.http_call_pattern is None:
            return found
        timeout_re = self._profile.timeout_token_pattern or re.compile(r"(?i)\btimeout\b")
        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            if self._profile.http_call_pattern.search(line) and not timeout_re.search(line):
                found.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="http_call",
                        detail="Outbound network/HTTP call lacks an explicit timeout parameter (SRE PRR)",
                    )
                )
        return found

    def find_scattered_env_access(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Flag direct environment reads outside dedicated config/settings files."""
        found: list[CodeLocation] = list(_run_hook(self._profile, unit).scattered_env_access)
        if self._profile.env_access_pattern is None:
            return found
        low_path = unit.rel_path.lower()
        if any(tok in low_path for tok in ("config", "settings", "env", "main")):
            return found
        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            if self._profile.env_access_pattern.search(line):
                found.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="env",
                        detail="Direct environment variable read outside configuration module (12-Factor III)",
                    )
                )
        return found

    def find_unstructured_logging(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Flag raw stdout/stderr console prints outside CLI/entrypoint modules."""
        found: list[CodeLocation] = list(_run_hook(self._profile, unit).unstructured_logging)
        if self._profile.console_log_pattern is None:
            return found
        low_path = unit.rel_path.lower()
        if any(tok in low_path for tok in ("cli", "cmd", "console")):
            return found
        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            if self._profile.console_log_pattern.search(line):
                found.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=line_no,
                        symbol="stdout",
                        detail="Raw console output instead of structured logger (12-Factor XI)",
                    )
                )
        return found

    def find_hardcoded_secrets(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Flag hardcoded credential/secret literals using BaseOperationalChecker heuristics."""
        found: list[CodeLocation] = list(_run_hook(self._profile, unit).hardcoded_secrets)
        seen_lines = {loc.line for loc in found}
        pat = self._profile.secret_assign_pattern or re.compile(
            r"""(?i)\b([A-Za-z_][A-Za-z0-9_]*(?:password|passwd|secret|api_?key|token|private_?key)[A-Za-z0-9_]*)\s*(?::?=|<-|:)\s*['"]([^'"]{8,})['"]"""
        )
        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            if line_no in seen_lines:
                continue
            stripped = line.strip()
            if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            for m in pat.finditer(line):
                if self.is_likely_secret_literal(m.group(1), m.group(2)):
                    seen_lines.add(line_no)
                    found.append(
                        CodeLocation(
                            file=unit.rel_path,
                            line=line_no,
                            symbol=m.group(1),
                            detail="Hardcoded credential/secret literal detected (CWE-798)",
                        )
                    )
                    break
        return found


class DeclarativeSecurityChecker(BaseSecurityChecker):
    """Profile-driven CWE dangerous sink extractor combining declarative rules and custom hooks."""

    def __init__(self, profile: LanguageGrammarProfile) -> None:
        """Bind security checker to profile CWE sink rules."""
        self._profile = profile

    def _scan_rule_nodes(
        self,
        unit: ParsedUnit,
        rule: CweSinkRule,
        seen: set[tuple[int, str]],
        sinks: list[SecuritySinkLocation],
    ) -> None:
        """Evaluate a CweSinkRule targeting specific CST node kinds."""
        for nkind in rule.node_kinds:
            for node in unit.root.find_all(kind=nkind):
                line_no = node.range().start.line + 1
                if (line_no, rule.cwe_id) in seen or not rule.pattern.search(node.text()):
                    continue
                seen.add((line_no, rule.cwe_id))
                sinks.append(
                    SecuritySinkLocation(
                        category=rule.category,
                        cwe_id=rule.cwe_id,
                        severity=rule.severity,
                        file=unit.rel_path,
                        line=line_no,
                        symbol=nkind,
                        detail=rule.detail,
                    )
                )

    def _scan_rule_lines(
        self,
        unit: ParsedUnit,
        rule: CweSinkRule,
        seen: set[tuple[int, str]],
        sinks: list[SecuritySinkLocation],
    ) -> None:
        """Evaluate a line-oriented CweSinkRule skipping profile comments."""
        for line_no, line in enumerate(unit.source.splitlines(), start=1):
            if (line_no, rule.cwe_id) in seen:
                continue
            stripped = line.strip()
            if not stripped or any(stripped.startswith(p) for p in self._profile.comment_prefixes):
                continue
            if rule.pattern.search(line):
                seen.add((line_no, rule.cwe_id))
                sinks.append(
                    SecuritySinkLocation(
                        category=rule.category,
                        cwe_id=rule.cwe_id,
                        severity=rule.severity,
                        file=unit.rel_path,
                        line=line_no,
                        symbol=rule.category,
                        detail=rule.detail,
                    )
                )

    def find_dangerous_sinks(self, unit: ParsedUnit) -> list[SecuritySinkLocation]:
        """Extract CWE-classified dangerous sinks across CST nodes, lines, and custom hooks."""
        sinks: list[SecuritySinkLocation] = list(_run_hook(self._profile, unit).dangerous_sinks)
        seen: set[tuple[int, str]] = {(s.line, s.cwe_id) for s in sinks}
        for rule in self._profile.security_sink_rules:
            if rule.node_kinds:
                self._scan_rule_nodes(unit, rule, seen, sinks)
            else:
                self._scan_rule_lines(unit, rule, seen, sinks)
        return sinks

    def find_api_endpoints(self, unit: ParsedUnit) -> list[ApiEndpointFact]:
        """Return API route definitions when applicable (empty default for declarative suites)."""
        _ = unit
        return []


def build_declarative_suite(profile: LanguageGrammarProfile) -> LanguageAnalyzerSuite:
    """Assemble a complete LanguageAnalyzerSuite from a declarative LanguageGrammarProfile."""
    return LanguageAnalyzerSuite(
        language=profile.language_id,
        ast_grep_lang=profile.grammar_id,
        file_extensions=profile.file_extensions,
        default_target_dirs=profile.default_target_dirs,
        fallback_dirs=profile.fallback_dirs,
        import_checker=DeclarativeImportChecker(profile),
        quality_checker=DeclarativeQualityChecker(profile),
        typing_checker=DeclarativeTypingChecker(profile),
        doc_checker=DeclarativeDocChecker(profile),
        dependency_checker=DeclarativeDependencyChecker(profile),
        test_checker=DeclarativeTestChecker(profile),
        operational_checker=DeclarativeOperationalChecker(profile),
        security_checker=DeclarativeSecurityChecker(profile),
        default_test_dirs=profile.default_test_dirs,
        test_file_patterns=profile.test_file_patterns,
        excluded_source_suffixes=profile.excluded_source_suffixes,
        source_preprocessor=profile.source_preprocessor,
        filenames=profile.filenames,
        ext_grammars=profile.ext_grammars,
    )
