# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative profile models for Tree-sitter multi-language AST auditing."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from pni._actions.ast_analyze.models import (
    CodeLocation,
    ParsedUnit,
    SecuritySinkCategory,
    SecuritySinkLocation,
    SinkSeverity,
)


@dataclass(frozen=True)
class CweSinkRule:
    """Declarative CWE dangerous sink rule evaluated over CST nodes or source lines."""

    category: SecuritySinkCategory
    cwe_id: str
    severity: SinkSeverity
    pattern: re.Pattern[str]
    detail: str
    node_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class BugIdiomRule:
    """Declarative bug-risk idiom rule evaluated over CST nodes or source lines."""

    pattern: re.Pattern[str]
    detail: str
    symbol: str = ""
    node_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class CustomHookResult:
    """Additional deterministic metrics and findings emitted by a language-specific CST hook."""

    extra_classes: int = 0
    extra_functions: int = 0
    extra_public_types: tuple[str, ...] = ()
    extra_public_callables: tuple[str, ...] = ()
    complex_functions: tuple[CodeLocation, ...] = ()
    excessive_parameters: tuple[CodeLocation, ...] = ()
    global_state_usages: tuple[CodeLocation, ...] = ()
    bug_risk_idioms: tuple[CodeLocation, ...] = ()
    dangerous_sinks: tuple[SecuritySinkLocation, ...] = ()
    hardcoded_secrets: tuple[CodeLocation, ...] = ()
    missing_io_timeouts: tuple[CodeLocation, ...] = ()
    scattered_env_access: tuple[CodeLocation, ...] = ()
    unstructured_logging: tuple[CodeLocation, ...] = ()
    import_targets: tuple[str, ...] = ()


CustomAuditHook = Callable[[ParsedUnit], CustomHookResult]


@dataclass(frozen=True)
class LanguageGrammarProfile:
    """Declarative Tree-sitter AST grammar profile driving all 8 PNI checker dimensions."""

    language_id: str
    grammar_id: str
    file_extensions: tuple[str, ...] = ()
    filenames: tuple[str, ...] = ()
    ext_grammars: tuple[tuple[str, str], ...] = ()
    default_target_dirs: tuple[str, ...] = ("src", ".")
    fallback_dirs: tuple[str, ...] = (".",)
    default_test_dirs: tuple[str, ...] = ("tests",)
    test_file_patterns: tuple[str, ...] = ()
    excluded_source_suffixes: tuple[str, ...] = ()

    # LOC & comments
    comment_prefixes: tuple[str, ...] = ("//", "#")
    block_comment_start: str = "/*"
    block_comment_end: str = "*/"

    # Structural declarations
    class_node_kinds: tuple[str, ...] = ()
    callable_node_kinds: tuple[str, ...] = ()
    callable_name_fields: tuple[str, ...] = ("name", "declarator")
    callable_name_child_kinds: tuple[str, ...] = ("identifier", "simple_identifier", "word", "name", "sym_lit")
    macro_class_names: tuple[str, ...] = ()
    macro_callable_names: tuple[str, ...] = ()
    macro_call_node_kind: str = "call"

    # Parameters (SIG Unit Interfacing)
    param_container_kinds: tuple[str, ...] = ("parameters", "parameter_list", "formal_parameters")
    param_item_kinds: tuple[str, ...] = ("parameter", "parameter_declaration", "formal_parameter")
    self_param_names: frozenset[str] = field(default_factory=lambda: frozenset({"self", "this", "&self", "&mut self"}))

    # Complexity
    branch_node_kinds: tuple[str, ...] = ("if_statement", "for_statement", "while_statement", "switch_statement")
    nesting_node_kinds: tuple[str, ...] = ()

    # Imports & dependencies
    import_applicable: bool = True
    import_node_kinds: tuple[str, ...] = ()
    wildcard_import_kinds: tuple[str, ...] = ()
    wildcard_import_pattern: re.Pattern[str] | None = None

    # Globals
    global_state_node_kinds: tuple[str, ...] = ()
    global_state_pattern: re.Pattern[str] | None = None

    # Typing
    typing_applicable: bool = False
    weak_type_pattern: re.Pattern[str] | None = None
    type_ignore_pattern: re.Pattern[str] | None = None

    # Docs
    doc_applicable: bool = True
    doc_comment_prefixes: tuple[str, ...] = ("///", "/**", "##", "--|", ";;")

    # Testing
    test_applicable: bool = True
    assertion_pattern: re.Pattern[str] | None = None

    # Operational signals
    console_log_pattern: re.Pattern[str] | None = None
    env_access_pattern: re.Pattern[str] | None = None
    http_call_pattern: re.Pattern[str] | None = None
    timeout_token_pattern: re.Pattern[str] | None = None
    secret_assign_pattern: re.Pattern[str] | None = None

    # Security sinks & bug idioms
    security_sink_rules: tuple[CweSinkRule, ...] = ()
    bug_idiom_rules: tuple[BugIdiomRule, ...] = ()

    # Optional preprocessor & custom CST hook
    source_preprocessor: Callable[[str], str] | None = None
    custom_hook: CustomAuditHook | None = None
