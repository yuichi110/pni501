# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Comprehensive tests for Python & Java AST health checkers, framework plugins, and legacy inspection."""

from __future__ import annotations

from pathlib import Path

from pni._actions import run_ast_analyze, run_project_inspect

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_pni501_self_dogfooding_zero_false_positives() -> None:
    """Verify pni501's own src/pni passes isort, typing, docstring, deptry, and operational AST checks cleanly."""
    pf = run_project_inspect(REPO_ROOT, source_dirs=["src/pni"], test_dirs=["tests"])
    assert pf.language == "python"
    assert pf.runtime_types == ["cli"]
    assert pf.build_system == "uv"
    assert pf.has_type_marker is True
    assert pf.has_license is True
    assert pf.committed_secret_files == []
    assert pf.legacy_language_findings == []
    assert pf.tooling_modernization_issues == []

    af = run_ast_analyze(REPO_ROOT, targets=["src/pni"], test_targets=["tests"], lang="python")
    assert af.import_hygiene_coverage_pct == 100.0, f"Unexpected unsorted/wildcard imports: {af.unsorted_imports}"
    assert af.wildcard_imports == []
    assert af.type_safety_coverage_pct == 100.0, f"Unexpected typing issues: {af.type_safety_issues}"
    assert af.unscoped_type_ignores == []
    assert af.docstring_coverage_pct == 100.0, f"Unexpected missing docs: {af.missing_docstrings}"
    assert af.empty_docstrings == []
    assert af.doc_signature_mismatches == []
    assert af.unused_dependencies == []
    assert af.undeclared_dependencies == []
    assert af.missing_io_timeouts == []
    assert af.scattered_env_access == []
    assert af.unstructured_logging == []
    assert af.hardcoded_secrets == []
    assert af.assertion_free_tests == []
    assert af.test_functions_count >= 35


def test_python_import_checker_isort_wildcards_and_late_imports(tmp_path: Path) -> None:
    """Verify PythonImportChecker catches group order, blank lines, symbol order, wildcards, and late imports."""
    src = tmp_path / "src" / "app"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('"""App package."""\n', encoding="utf-8")

    # Clean Ruff/isort file (header comment + docstring + __future__ + CONSTANT_CASE < PascalCase < snake_case)
    (src / "clean_imports.py").write_text(
        "# Copyright header\n"
        '"""Clean module."""\n\n'
        "from __future__ import annotations\n\n"
        "import os\n"
        "import sys\n\n"
        "from pydantic import MAX_LENGTH, BaseModel, create_model\n\n"
        "from app import __doc__\n\n"
        "def ok() -> int:\n"
        '    """Return zero."""\n'
        "    _ = (os, sys, MAX_LENGTH, BaseModel, create_model, __doc__)\n"
        "    return 0\n",
        encoding="utf-8",
    )

    # Messy imports: third-party before stdlib, missing blank line, unsorted symbols, wildcard, late import
    (src / "bad_imports.py").write_text(
        '"""Messy imports module."""\n\n'
        "import pydantic\n"
        "import os\n"
        "from typing import snake_helper, BaseCls, CONST_VAL\n"
        "from math import *\n\n"
        "X: int = 1\n"
        "import json\n\n"
        "def run() -> int:\n"
        '    """Run lazy."""\n'
        "    import re\n"
        "    _ = (pydantic, os, json, re)\n"
        "    return X\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src"])
    # 2 of 3 files (__init__.py, clean_imports.py) are clean -> 66.7%
    assert af.import_hygiene_coverage_pct == 66.7
    assert len(af.unsorted_imports) >= 2
    assert len(af.wildcard_imports) == 1
    assert all("clean_imports.py" not in loc.file for loc in af.late_imports)
    assert any("E402" in loc.detail for loc in af.late_imports)
    assert any("PLC0415" in loc.detail for loc in af.late_imports)


def test_python_typing_doc_and_quality_enhancements(tmp_path: Path) -> None:
    """Verify bare generics, class attrs, unscoped ignore, @overload, Args mismatch, cognitive & Bugbear checks."""
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "sample.py").write_text(
        '"""Sample module."""\n\n'
        "from __future__ import annotations\n\n"
        "import subprocess\n"
        "from typing import overload\n\n\n"
        "class ConfigHolder:\n"
        '    """TODO."""\n\n'
        "    model_config = {'frozen': True}\n"
        "    untyped_attr = 42\n"
        "    typed_attr: int = 1\n\n\n"
        "@overload\n"
        "def convert(val: int) -> int: ...\n\n\n"
        "@overload\n"
        "def convert(val: str) -> str: ...\n\n\n"
        "def convert(val: int | str) -> int | str:\n"
        '    """Convert value properly."""\n'
        "    return val  # type: ignore\n\n\n"
        "def bad_api(items: list, count: int, cache=[]) -> dict:\n"
        '    """Process items with mismatched docstring.\n\n'
        "    Args:\n"
        "        items: Input items.\n"
        "        wrong_param: Ghost parameter.\n"
        '    """\n'
        "    try:\n"
        "        subprocess.run('ls', shell=True, check=False)\n"
        "    except:\n"
        "        pass\n"
        "    if count > 0:\n"
        "        for x in items:\n"
        "            if x:\n"
        "                while count > 1:\n"
        "                    if count == 2:\n"
        "                        count -= 1\n"
        "    return {}\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src"])
    # @overload stubs skipped -> only convert + bad_api counted for callables
    assert any("unparameterized 'list'" in loc.detail for loc in af.weak_type_usages)
    assert any(loc.symbol == "bad_api" for loc in af.type_safety_issues)
    assert any(loc.symbol == "ConfigHolder.untyped_attr" for loc in af.type_safety_issues)
    assert not any("model_config" in loc.symbol for loc in af.type_safety_issues)
    assert len(af.unscoped_type_ignores) == 1

    # ConfigHolder has stub "TODO." docstring -> empty_docstrings; @overload not flagged in missing_docstrings
    assert any(loc.symbol == "ConfigHolder" for loc in af.empty_docstrings)
    assert not any(loc.symbol == "convert" for loc in af.missing_docstrings)
    assert len(af.doc_signature_mismatches) == 1
    assert "count" in af.doc_signature_mismatches[0].detail
    assert "wrong_param" in af.doc_signature_mismatches[0].detail

    # Cognitive complexity > 15 despite <= 7 branches + Bugbear/Bandit idioms
    assert any(loc.symbol == "bad_api" for loc in af.complex_functions)
    idiom_details = " | ".join(loc.detail for loc in af.bug_risk_idioms)
    assert "B006" in idiom_details
    assert "E722" in idiom_details
    assert "shell=True" in idiom_details


def test_python_deptry_boundaries_tests_and_frameworks(tmp_path: Path) -> None:
    """Verify deptry manifest cross-check, boundary rules, assertion-free tests, and FastAPI/Flask/Pydantic checks."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "web-svc"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["fastapi>=0.115.0", "pydantic>=2.8.0", "unused-ghost-lib>=1.0.0"]\n'
        '[dependency-groups]\ndev = ["pytest>=8.0.0"]\n',
        encoding="utf-8",
    )
    domain_dir = tmp_path / "src" / "svc" / "domain"
    api_dir = tmp_path / "src" / "svc" / "api"
    tests_dir = tmp_path / "tests"
    domain_dir.mkdir(parents=True)
    api_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)

    (domain_dir / "models.py").write_text(
        '"""Domain models."""\n\n'
        "from typing import List\n\n"
        "from pydantic import BaseModel, validator\n"
        "import pytest\n\n"
        "from svc.api import routes\n\n\n"
        "class Item(BaseModel):\n"
        '    """Domain item."""\n\n'
        "    tags: List[str] = []\n\n"
        "    class Config:\n"
        '        """Legacy v1 config."""\n\n'
        "        frozen = True\n\n"
        "    @validator('tags')\n"
        "    def check_tags(cls, v: List[str]) -> List[str]:\n"
        '        """Validate."""\n'
        "        _ = (pytest, routes)\n"
        "        return v\n",
        encoding="utf-8",
    )
    (api_dir / "routes.py").write_text(
        '"""API routes."""\n\n'
        "import os.path\n"
        "import time\n\n"
        "from fastapi import FastAPI\n"
        "from flask import Flask\n"
        "import requests\n\n"
        "app = FastAPI()\n"
        "legacy_flask = Flask(__name__)\n\n\n"
        "@app.on_event('startup')\n"
        "async def on_start() -> None:\n"
        '    """Legacy startup."""\n'
        "    _ = os.path.join('a', 'b')\n\n\n"
        "@app.get('/ping')\n"
        "async def ping() -> dict[str, str]:\n"
        '    """Blocking async route."""\n'
        "    time.sleep(1)\n"
        "    requests.get('https://example.com', timeout=1)\n"
        "    return {'ok': '1'}\n\n\n"
        "@legacy_flask.route('/old')\n"
        "def old_route() -> str:\n"
        '    """Legacy Flask route."""\n'
        "    return 'ok'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_svc.py").write_text(
        "from svc.domain import models\n\n"
        "def test_real() -> None:\n"
        "    assert models.Item(tags=['a']).tags == ['a']\n\n"
        "def test_fake_no_assert() -> None:\n"
        "    models.Item(tags=['b'])\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src"], test_targets=["tests"])
    assert "unused_ghost_lib" in af.unused_dependencies
    undeclared_syms = {loc.symbol for loc in af.undeclared_dependencies}
    assert "requests" in undeclared_syms
    assert "flask" in undeclared_syms
    assert "pytest" in undeclared_syms  # Dev dependency imported in production src/
    assert len(af.boundary_violations) == 1  # domain importing api

    assert af.test_functions_count == 2
    assert len(af.assertion_free_tests) == 1
    assert af.assertion_free_tests[0].symbol == "test_fake_no_assert"

    assert len(af.framework_issues) >= 2  # time.sleep + requests.get inside async route
    hint_text = " | ".join(loc.detail for loc in af.modernization_hints)
    assert "lifespan" in hint_text
    assert "ConfigDict" in hint_text
    assert "field_validator" in hint_text
    assert "Flask" in hint_text
    assert "pathlib.Path" in hint_text
    assert "PEP 585" in hint_text


def test_legacy_languages_and_java_expanded_checkers(tmp_path: Path) -> None:
    """Verify Perl/Batch/Fat-Bash legacy detection and expanded Java import/doc/quality/test/Spring checks."""
    (tmp_path / "setup.py").write_text("from setuptools import setup\nsetup(name='old')\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "etl.pl").write_text("use strict;\nprint 'hi';\n", encoding="utf-8")
    (tmp_path / "scripts" / "deploy.bat").write_text("@echo off\necho deploy\n", encoding="utf-8")
    (tmp_path / "scripts" / "small.sh").write_text("#!/bin/bash\necho ok\n", encoding="utf-8")
    fat_lines = ["#!/bin/bash", *[f"echo line_{i}" for i in range(110)]]
    (tmp_path / "scripts" / "giant_pipeline.sh").write_text("\n".join(fat_lines) + "\n", encoding="utf-8")

    pf = run_project_inspect(tmp_path)
    legacy_joined = " | ".join(pf.legacy_language_findings)
    assert "Perl scripts detected" in legacy_joined
    assert "Legacy Batch/VBScript files detected" in legacy_joined
    assert "giant_pipeline.sh" in legacy_joined
    assert "small.sh" not in legacy_joined
    assert pf.tooling_modernization_issues  # setup.py without pyproject.toml

    # Java expanded AST checks
    jmain = tmp_path / "src" / "main" / "java" / "com" / "demo"
    jtest = tmp_path / "src" / "test" / "java" / "com" / "demo"
    jmain.mkdir(parents=True)
    jtest.mkdir(parents=True)
    (jmain / "UserController.java").write_text(
        """package com.demo;

import java.util.Vector;
import java.util.Date;
import java.io.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * TODO
 */
@SuppressWarnings("all")
public class UserController {
    @Autowired
    private Object repo;

    /**
     * Fetch user record.
     * @param wrongName stale param tag
     */
    @RequestMapping("/users")
    public Date getUser(String userId) {
        try {
            if (userId == "admin") {
                System.out.println(userId);
            }
        } catch (Exception e) {
        }
        Vector<String> v = new Vector<>();
        return new Date();
    }
}
""",
        encoding="utf-8",
    )
    (jtest / "UserControllerTest.java").write_text(
        """package com.demo;

import org.junit.jupiter.api.Test;

class UserControllerTest {
    @Test
    void smokeWithoutAssert() {
        UserController c = new UserController();
    }

    @Test
    void properTest() {
        assertEquals(1, 1);
    }
}
""",
        encoding="utf-8",
    )

    jfacts = run_ast_analyze(tmp_path, targets=["src/main/java"], test_targets=["src/test/java"], lang="java")
    assert jfacts.import_hygiene_coverage_pct == 0.0
    assert len(jfacts.unsorted_imports) >= 1
    assert len(jfacts.wildcard_imports) == 1
    assert len(jfacts.unscoped_type_ignores) == 1
    assert len(jfacts.empty_docstrings) == 1
    assert len(jfacts.doc_signature_mismatches) == 1
    assert len(jfacts.bug_risk_idioms) >= 3  # empty catch + == "admin" + System.out
    assert jfacts.test_functions_count == 2
    assert len(jfacts.assertion_free_tests) == 1
    assert jfacts.module_test_coverage_pct == 100.0
    assert len(jfacts.framework_issues) == 1  # @Autowired field injection
    assert len(jfacts.modernization_hints) >= 2  # @RequestMapping + Date/Vector
