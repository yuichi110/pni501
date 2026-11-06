# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Python code quality, cognitive complexity, global state, and Bugbear/security AST checker."""

from __future__ import annotations

from typing import ClassVar, Final

from ast_grep_py import SgNode

from pni._actions.ast_analyze.base import BaseQualityChecker
from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
)
from pni._actions.ast_analyze.python._helpers import (
    extract_callable_param_names,
    extract_param_name,
    function_symbol_name,
)

_MUTABLE_DEFAULT_KINDS: Final[frozenset[str]] = frozenset({"list", "dictionary", "set"})
_MUTABLE_CALL_NAMES: Final[frozenset[str]] = frozenset({"list", "dict", "set", "defaultdict", "deque"})
_DANGEROUS_DIRECT_CALLS: Final[frozenset[str]] = frozenset({"eval", "exec"})


def _find_mutable_default_args(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect mutable default parameter values (Ruff B006: [], {}, set(), etc.)."""
    findings: list[CodeLocation] = []
    for fn_node in unit.root.find_all(kind="function_definition"):
        params = fn_node.field("parameters")
        if params is None:
            continue
        fn_name = function_symbol_name(fn_node)
        for param in params.named_children():
            if param.kind() not in {"default_parameter", "typed_default_parameter"}:
                continue
            val = param.field("value")
            if val is None:
                continue
            is_mut = val.kind() in _MUTABLE_DEFAULT_KINDS or (
                val.kind() == "call"
                and (fn_part := val.field("function")) is not None
                and fn_part.text() in _MUTABLE_CALL_NAMES
            )
            if is_mut:
                pname = extract_param_name(param)
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=param.range().start.line + 1,
                        symbol=fn_name,
                        detail=f"Mutable default argument '{pname}={val.text()}' (B006)",
                    )
                )
    return findings


def _find_exception_antipatterns(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect bare 'except:' clauses and silent 'except Exception: pass' blocks."""
    findings: list[CodeLocation] = []
    for exc_node in unit.root.find_all(kind="except_clause"):
        header = exc_node.text().split(":", maxsplit=1)[0].strip()
        if header == "except":
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=exc_node.range().start.line + 1,
                    symbol="except:",
                    detail="Bare 'except:' catches BaseException/KeyboardInterrupt (E722)",
                )
            )
            continue
        children = [c for c in exc_node.named_children() if c.kind() == "block"]
        if children:
            stmts = [s for s in children[0].named_children() if s.kind() != "comment"]
            if len(stmts) == 1 and stmts[0].kind() == "pass_statement":
                findings.append(
                    CodeLocation(
                        file=unit.rel_path,
                        line=exc_node.range().start.line + 1,
                        symbol=header,
                        detail="Silent 'try-except-pass' swallows exceptions without logging (S110)",
                    )
                )
    return findings


def _find_dangerous_calls(unit: ParsedUnit) -> list[CodeLocation]:
    """Detect eval/exec, subprocess(..., shell=True), pickle.loads, and unsafe yaml.load."""
    findings: list[CodeLocation] = []
    for call in unit.root.find_all(kind="call"):
        fn = call.field("function")
        if fn is None:
            continue
        fn_text = fn.text().strip()
        args_node = call.field("arguments")
        args_text = args_node.text() if args_node is not None else ""
        lineno = call.range().start.line + 1

        if fn_text in _DANGEROUS_DIRECT_CALLS:
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=lineno,
                    symbol=fn_text,
                    detail=f"Dangerous dynamic code execution '{fn_text}(...)' (S307)",
                )
            )
        elif fn_text.startswith("subprocess.") and "shell=True" in args_text.replace(" ", ""):
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=lineno,
                    symbol=fn_text,
                    detail="Subprocess call with 'shell=True' risks command injection (S602)",
                )
            )
        elif fn_text in {"pickle.loads", "pickle.load"}:
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=lineno,
                    symbol=fn_text,
                    detail="Untrusted pickle deserialization risk (S301)",
                )
            )
        elif fn_text == "yaml.load" and "Loader" not in args_text:
            findings.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=lineno,
                    symbol=fn_text,
                    detail="Unsafe 'yaml.load()' without SafeLoader — use 'yaml.safe_load()' (S506)",
                )
            )
    return findings


class PythonQualityChecker(BaseQualityChecker):
    """Inspect Python LOC, module inventory, cognitive complexity, globals, and bug idioms."""

    branch_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "elif_clause",
            "for_statement",
            "while_statement",
            "try_statement",
            "except_clause",
            "conditional_expression",
            "match_statement",
            "case_clause",
        }
    )
    nesting_node_kinds: ClassVar[frozenset[str]] = frozenset(
        {
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "match_statement",
            "with_statement",
        }
    )

    def count_loc(self, unit: ParsedUnit) -> int:
        """Count non-empty, non-comment lines in a Python file."""
        return sum(1 for ln in unit.source.splitlines() if ln.strip() and not ln.strip().startswith("#"))

    def count_classes(self, unit: ParsedUnit) -> int:
        """Count class_definition nodes in a Python file."""
        return len(unit.root.find_all(kind="class_definition"))

    def iter_callables(self, unit: ParsedUnit) -> list[tuple[str, SgNode]]:
        """Return (function_name, function_definition_node) pairs."""
        return [(function_symbol_name(fn), fn) for fn in unit.root.find_all(kind="function_definition")]

    def count_callable_params(self, node: SgNode) -> int:
        """Count Python function parameters excluding 'self', 'cls', and bare separators."""
        return len(extract_callable_param_names(node))

    def extract_public_symbols(self, unit: ParsedUnit) -> tuple[list[str], list[str]]:
        """Return sorted public class names and public top-level function names."""
        pub_classes: list[str] = []
        for cls_node in unit.root.find_all(kind="class_definition"):
            cname_node = cls_node.field("name")
            if cname_node is not None and not cname_node.text().startswith("_"):
                pub_classes.append(cname_node.text())

        pub_funcs: list[str] = []
        for child in unit.root.named_children():
            target = child
            if child.kind() == "decorated_definition":
                fn_children = [c for c in child.named_children() if c.kind() == "function_definition"]
                target = fn_children[0] if fn_children else child
            if target.kind() == "function_definition":
                fname = function_symbol_name(target)
                if not fname.startswith("_") and fname not in pub_funcs:
                    pub_funcs.append(fname)
        return sorted(pub_classes), pub_funcs

    def find_global_state(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect explicit 'global' mutation statements inside Python functions."""
        usages: list[CodeLocation] = []
        for glob_node in unit.root.find_all(kind="global_statement"):
            names = [c.text() for c in glob_node.named_children() if c.kind() == "identifier"]
            joined = ", ".join(names)
            usages.append(
                CodeLocation(
                    file=unit.rel_path,
                    line=glob_node.range().start.line + 1,
                    symbol=joined,
                    detail=f"Mutable global statement: global {joined}",
                )
            )
        return usages

    def find_bug_risk_idioms(self, unit: ParsedUnit) -> list[CodeLocation]:
        """Detect Python Bugbear mutable defaults, bare excepts, and dangerous runtime calls."""
        return [
            *_find_mutable_default_args(unit),
            *_find_exception_antipatterns(unit),
            *_find_dangerous_calls(unit),
        ]
