# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for _rules, _instructions, and project initialization."""

import shutil
from pathlib import Path

from pni._instructions import get_instructions_content
from pni._rules import (
    detect_active_language,
    get_rule_content,
    list_rules,
)
from pni._workflows import WorkflowStateDB
from pni.cli import init_project


def test_detect_active_language(tmp_path: Path) -> None:
    """Test language auto-detection logic across Python, Java, and TypeScript."""
    assert detect_active_language(tmp_path) == "python"

    java_maven = tmp_path / "maven_app"
    java_maven.mkdir()
    (java_maven / "pom.xml").write_text("<project/>", encoding="utf-8")
    assert detect_active_language(java_maven) == "java"

    java_gradle = tmp_path / "gradle_app"
    java_gradle.mkdir()
    (java_gradle / "build.gradle.kts").write_text("", encoding="utf-8")
    assert detect_active_language(java_gradle) == "java"

    java_layout = tmp_path / "layout_app"
    (java_layout / "src" / "main" / "java").mkdir(parents=True)
    assert detect_active_language(java_layout) == "java"

    ts_app = tmp_path / "ts_app"
    ts_app.mkdir()
    (ts_app / "package.json").write_text("{}", encoding="utf-8")
    assert detect_active_language(ts_app) == "typescript"

    py_app = tmp_path / "py_app"
    py_app.mkdir()
    (py_app / "pyproject.toml").write_text("", encoding="utf-8")
    assert detect_active_language(py_app) == "python"


def test_list_rules(tmp_path: Path) -> None:
    """Test listing rules with scoping."""
    rules = list_rules(tmp_path, lang="python", include_all=False)
    scopes = {r.scope for r in rules}
    assert "common" in scopes
    assert "python" in scopes
    assert "java" not in scopes
    assert all(not r.is_local for r in rules)

    identifiers = [r.identifier for r in rules]
    assert "common/architecture" in identifiers
    assert "python/testing" in identifiers

    all_rules = list_rules(tmp_path, lang="python", include_all=True)
    all_scopes = {r.scope for r in all_rules}
    assert {"common", "python", "java"}.issubset(all_scopes)


def test_get_rule_content(tmp_path: Path) -> None:
    """Test retrieving rule content with smart lookup."""
    res1 = get_rule_content("testing", tmp_path, lang="python")
    assert res1 is not None
    info1, content1 = res1
    assert info1.identifier == "python/testing"
    assert "Pytest Framework" in content1

    res_java = get_rule_content("testing", tmp_path, lang="java")
    assert res_java is not None
    info_java, content_java = res_java
    assert info_java.identifier == "java/testing"
    assert "JUnit 5" in content_java

    res2 = get_rule_content("common/architecture", tmp_path)
    assert res2 is not None
    info2, content2 = res2
    assert info2.identifier == "common/architecture"
    assert "Separation of Concerns" in content2

    res_missing = get_rule_content("nonexistent_rule", tmp_path)
    assert res_missing is None


def test_get_instructions_content(tmp_path: Path) -> None:
    """Test getting instructions with local override."""
    default_content = get_instructions_content(tmp_path)
    assert "PNI (Project Nemesis Index) Agent Instructions" in default_content

    pni_dir = tmp_path / ".pni"
    pni_dir.mkdir()
    (pni_dir / "instructions.md").write_text("# Custom Local Instructions", encoding="utf-8")

    custom_content = get_instructions_content(tmp_path)
    assert custom_content == "# Custom Local Instructions"


def test_init_project(tmp_path: Path) -> None:
    """Test initializing .pni directory and cascade templates for Python and Java."""
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")

    created = init_project(tmp_path, lang="python", force=False)
    assert len(created) > 0

    assert (tmp_path / ".pni" / "rules" / "common" / "architecture.md").exists()
    assert (tmp_path / ".pni" / "rules" / "python" / "testing.md").exists()
    assert not (tmp_path / ".pni" / "rules" / "java").exists()
    assert (tmp_path / ".pni" / "actions" / "python_ast_audit.yaml").exists()
    assert not (tmp_path / ".pni" / "actions" / "java_ast_audit.yaml").exists()
    assert (tmp_path / ".pni" / "instructions.md").exists()
    assert (tmp_path / ".pni" / "workflows" / "quick_check.yaml").exists()

    # Second init without force returns empty list
    created2 = init_project(tmp_path, lang="python", force=False)
    assert len(created2) == 0

    # With force overwrites
    created3 = init_project(tmp_path, lang="python", force=True)
    assert len(created3) > 0

    # Verify root .gitignore is NOT modified, while .pni/cache/.gitignore and CACHEDIR.TAG are created
    gitignore_content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert gitignore_content == "node_modules/\n"
    cache_gitignore = tmp_path / ".pni" / "cache" / ".gitignore"
    assert cache_gitignore.is_file()
    assert "*" in cache_gitignore.read_text(encoding="utf-8")
    assert (tmp_path / ".pni" / "cache" / "CACHEDIR.TAG").is_file()

    # Verify Java initialization scaffolds only common + java templates
    java_root = tmp_path / "java_proj"
    java_root.mkdir()
    java_created = init_project(java_root, lang="java", force=False)
    assert len(java_created) > 0
    assert (java_root / ".pni" / "rules" / "java" / "typing.md").exists()
    assert not (java_root / ".pni" / "rules" / "python").exists()
    assert (java_root / ".pni" / "actions" / "java_ast_audit.yaml").exists()
    assert (java_root / ".pni" / "actions" / "java_test_audit.yaml").exists()
    assert (java_root / ".pni" / "actions" / "emit_score.yaml").exists()
    assert not (java_root / ".pni" / "actions" / "python_ast_audit.yaml").exists()
    java_wf = (java_root / ".pni" / "workflows" / "full_audit.yaml").read_text(encoding="utf-8")
    assert "src/main/java" in java_wf
    assert "java_ast_audit" in java_wf

    # Verify self-healing .pni/cache/.gitignore recreation if user deletes .pni/cache/
    shutil.rmtree(tmp_path / ".pni" / "cache")
    assert not (tmp_path / ".pni" / "cache").exists()
    WorkflowStateDB(tmp_path)
    assert (tmp_path / ".pni" / "cache" / ".gitignore").is_file()
    assert (tmp_path / ".pni" / "cache" / "CACHEDIR.TAG").is_file()
    assert (tmp_path / ".pni" / "cache" / "workflow_state.db").is_file()
