# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit tests for the unified Tree-sitter CST layer and central LanguageSpec registry."""

from __future__ import annotations

import importlib
import sys

import pytest
from typer.testing import CliRunner

from pni._actions.ast_analyze import CstNode, parse_cst
from pni._languages import (
    get_grammar_provider,
    get_language_spec,
    iter_language_specs,
    list_supported_languages,
)


def test_language_registry_core_specs() -> None:
    """Verify the central LanguageSpec registry covers all active Tier A languages and grammar providers."""
    langs = list_supported_languages()
    assert langs == ("python", "java", "php", "go", "typescript", "javascript")
    assert len(iter_language_specs(tier="full_audit")) == 6

    py = get_language_spec("PYTHON")
    assert py is not None
    assert py.display_name == "Python"
    assert py.default_grammar == "python"
    assert get_grammar_provider("tsx") is not None
    assert get_grammar_provider("nonexistent") is None


def test_cst_node_indexed_traversal_and_semantics() -> None:
    """Verify CstNode find/find_all, inside, prev, field_children, has(ERROR), and punctuation fallback."""
    src = "import os, sys\n\n# top doc\ndef outer(a, b):\n    def inner():\n        return a + b\n    return inner()\n"
    root = parse_cst(src, "python")
    assert isinstance(root, CstNode)
    assert root.kind() == "module"
    assert not root.has(kind="ERROR")

    fns = root.find_all(kind="function_definition")
    assert len(fns) == 2
    outer, inner = fns[0], fns[1]

    # find() and find_all() include self, matching prior SgNode semantics
    assert outer.find(kind="function_definition") == outer
    assert len(outer.find_all(kind="function_definition")) == 2
    assert len(inner.find_all(kind="function_definition")) == 1

    # inside() checks strict ancestors only
    assert not outer.inside(kind="function_definition")
    assert inner.inside(kind="function_definition")
    assert inner.inside(kind="block")

    # prev() returns immediately preceding sibling (named or unnamed)
    prev_outer = outer.prev()
    assert prev_outer is not None and prev_outer.kind() == "comment"
    params = outer.field("parameters")
    assert params is not None
    param_nodes = params.named_children()
    assert len(param_nodes) == 2
    comma = param_nodes[1].prev()
    assert comma is not None and comma.kind() == "," and not comma.is_named()

    # Unnamed punctuation fallback scan works cleanly
    assert len(params.find_all(kind=",")) == 1

    # field_children() returns all multi-bound field nodes
    imp = root.find(kind="import_statement")
    assert imp is not None
    assert [n.text() for n in imp.field_children("name")] == ["os", "sys"]

    # Syntax errors surface via has(kind="ERROR")
    broken = parse_cst("def broken(:\n", "python")
    assert broken.has(kind="ERROR")

    # Unknown grammar raises clear ValueError
    with pytest.raises(ValueError, match="Unsupported Tree-sitter grammar"):
        parse_cst("x = 1", "does_not_exist")


def test_tree_sitter_lazy_import_not_loaded_on_cli_startup() -> None:
    """Verify importing pni.cli and running non-AST commands does not load tree_sitter C extensions."""
    saved_ts = {
        name: mod
        for name, mod in list(sys.modules.items())
        if name == "tree_sitter" or name.startswith("tree_sitter_")
    }
    try:
        for name in saved_ts:
            sys.modules.pop(name, None)

        cst_mod = importlib.import_module("pni._actions.ast_analyze._cst")
        cli_mod = importlib.import_module("pni.cli")
        importlib.reload(cst_mod)
        importlib.reload(cli_mod)

        assert "tree_sitter" not in sys.modules
        assert not any(m.startswith("tree_sitter_") for m in sys.modules)

        runner = CliRunner()
        assert runner.invoke(cli_mod.app, ["version"]).exit_code == 0
        assert runner.invoke(cli_mod.app, ["rules", "list"]).exit_code == 0
        assert "tree_sitter" not in sys.modules
        assert not any(m.startswith("tree_sitter_") for m in sys.modules)
    finally:
        sys.modules.update(saved_ts)
