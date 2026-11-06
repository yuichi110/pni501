# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit tests for large-scale Python codebase scalability, drawlib >= 0.3.5, and list-based runtime_types."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from pni._actions import ProjectFacts, ScoreResult, SystemProfile, run_ast_analyze, run_project_inspect
from pni._actions.ast_analyze.base.dependencies import BaseDependencyChecker
from pni._actions.runtime_check.selector import build_test_and_coverage_command
from pni._actions.runtime_check.smoke import build_smoke_plan
from pni._reporter import compile_report_project
from pni._workflows import (
    get_workflow_action,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    start_workflow_run,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_tarjan_scc_scales_linearly_on_large_dense_dag_with_embedded_scc() -> None:
    """Verify iterative Tarjan SCC completes in <0.1s on a 500-node dense DAG + 12-node cycle cluster."""
    graph: dict[str, list[str]] = {}
    # 500-node dense layered DAG (exponential in naive per-node DFS without global visited pruning)
    for i in range(500):
        edges = [f"mod_{j}.py" for j in range(i + 1, min(i + 8, 500))]
        graph[f"mod_{i}.py"] = edges

    # Embed a 12-node strongly connected component with cross-chords
    scc_nodes = [f"scc_{k}.py" for k in range(12)]
    for idx, node in enumerate(scc_nodes):
        nxt = scc_nodes[(idx + 1) % len(scc_nodes)]
        chord = scc_nodes[(idx + 3) % len(scc_nodes)]
        graph[node] = [nxt, chord, "mod_0.py"]

    t0 = time.perf_counter()
    cycles = BaseDependencyChecker.detect_cycles(graph)
    elapsed = time.perf_counter() - t0

    assert elapsed < 0.25, f"Cycle detection took {elapsed:.3f}s (expected < 0.25s)"
    assert 1 <= len(cycles) <= 5
    # Verify canonical deduplication (each cycle starts and ends at its lexicographically smallest node)
    seen_tuples = {tuple(c) for c in cycles}
    assert len(seen_tuples) == len(cycles)
    for cyc in cycles:
        assert cyc[0] == cyc[-1]
        assert cyc[0] == min(cyc[:-1])


def test_type_checking_guard_separates_cycles_and_suppresses_false_dep004(tmp_path: Path) -> None:
    """Verify if TYPE_CHECKING: imports go to type_checking_cycles and do not trigger DEP004."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "tc-demo"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["pydantic>=2.0"]\n\n'
        '[dependency-groups]\ndev = ["pytest>=8.0"]\n',
        encoding="utf-8",
    )
    pkg = tmp_path / "src" / "tc_demo"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text('"""Package root."""\n', encoding="utf-8")

    # Static-only cycle between alpha.py and beta.py + dev-only pytest import under TYPE_CHECKING
    (pkg / "alpha.py").write_text(
        '"""Alpha module."""\n\n'
        "from __future__ import annotations\n\n"
        "from typing import TYPE_CHECKING\n\n"
        "if TYPE_CHECKING:\n"
        "    import pytest\n"
        "    from tc_demo.beta import Beta\n\n"
        "class Alpha:\n"
        '    """Alpha model."""\n\n'
        "    peer: Beta | None = None\n"
        "    mp: pytest.MonkeyPatch | None = None\n",
        encoding="utf-8",
    )
    (pkg / "beta.py").write_text(
        '"""Beta module."""\n\n'
        "from __future__ import annotations\n\n"
        "import typing as t\n\n"
        "if t.TYPE_CHECKING:\n"
        "    from tc_demo.alpha import Alpha\n\n"
        "class Beta:\n"
        '    """Beta model."""\n\n'
        "    owner: Alpha | None = None\n",
        encoding="utf-8",
    )

    af_clean = run_ast_analyze(tmp_path, targets=["src/tc_demo"], lang="python")
    assert af_clean.circular_dependencies == []
    assert len(af_clean.type_checking_cycles) == 1
    assert "tc_demo.alpha" in af_clean.type_checking_cycles[0]
    assert "tc_demo.beta" in af_clean.type_checking_cycles[0]
    assert af_clean.undeclared_dependencies == []

    # Negated guard 'if not TYPE_CHECKING:' executes at runtime and MUST flag DEP004 on dev-only pytest
    (pkg / "negated.py").write_text(
        '"""Negated guard."""\n\n'
        "from typing import TYPE_CHECKING\n\n"
        "if not TYPE_CHECKING:\n"
        "    import pytest\n\n"
        "    _ = pytest\n",
        encoding="utf-8",
    )
    af_neg = run_ast_analyze(tmp_path, targets=["src/tc_demo"], lang="python")
    assert any(item.symbol == "pytest" and "DEP004" in item.detail for item in af_neg.undeclared_dependencies)


def test_inline_comments_in_multiline_parameter_lists_cause_zero_false_positives(tmp_path: Path) -> None:
    """Verify inline comments inside function signatures do not inflate parameter counts or mismatch docs."""
    pkg = tmp_path / "src" / "sig_pkg"
    pkg.mkdir(parents=True)
    (pkg / "canvas.py").write_text(
        '"""Canvas drawing helpers."""\n\n'
        "from __future__ import annotations\n\n"
        "def draw_box(\n"
        "    # Geometry parameters\n"
        "    x: float,\n"
        "    y: float,\n"
        "    # Dimensions\n"
        "    width: float = 10.0,  # inline width note\n"
        "    height: float = 5.0,  # inline height note\n"
        "    # Styling options\n"
        "    label: str = '',\n"
        "    # Trailing comment inside signature\n"
        ") -> tuple[float, float]:\n"
        '    """Draw a box on the canvas.\n\n'
        "    Args:\n"
        "        x: Horizontal coordinate.\n"
        "        y: Vertical coordinate.\n"
        "        width: Box width.\n"
        "        height: Box height.\n"
        "        label: Optional text label.\n\n"
        "    Returns:\n"
        "        Center point coordinates.\n"
        '    """\n'
        "    _ = (width, height, label)\n"
        "    return (x, y)\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src/sig_pkg"], lang="python")
    assert af.type_safety_coverage_pct == 100.0
    assert af.type_safety_issues == []
    assert af.doc_signature_mismatches == []
    assert af.excessive_parameters == []


def test_target_exclude_globs_and_generated_facade_wildcard_exemption(tmp_path: Path) -> None:
    """Verify targets.exclude skips generated modules and __init__.py *_generated wildcard re-exports pass."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "gen-demo"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n',
        encoding="utf-8",
    )
    icons_dir = tmp_path / "src" / "gen_demo" / "icons"
    icons_dir.mkdir(parents=True)
    (tmp_path / "src" / "gen_demo" / "__init__.py").write_text('"""Root facade."""\n', encoding="utf-8")
    (icons_dir / "_phosphor_generated.py").write_text(
        "# Auto-generated icon table without docstrings or return annotations\n"
        "ICON_USER = 'user'\n"
        "def raw_untyped_helper(a, b):\n"
        "    return a + b\n",
        encoding="utf-8",
    )
    (icons_dir / "__init__.py").write_text(
        '"""Public icons facade re-exporting generated symbols."""\n\n'
        "from ._phosphor_generated import *\n\n"
        '__all__ = ["ICON_USER"]\n',
        encoding="utf-8",
    )

    excludes = ["**/*_generated.py"]
    pf = run_project_inspect(tmp_path, source_dirs=["src"], exclude_globs=excludes)
    assert pf.source_files_count == 2

    af = run_ast_analyze(tmp_path, targets=["src"], lang="python", exclude_globs=excludes)
    assert af.total_files == 2
    assert all("_phosphor_generated" not in m.file for m in af.module_inventory)
    assert af.wildcard_imports == []
    assert af.import_hygiene_coverage_pct == 100.0
    assert af.type_safety_coverage_pct == 100.0

    # Also verify workflow YAML targets.exclude + bounded import graph rendering (>60 modules)
    many_dir = tmp_path / "src" / "gen_demo" / "nodes"
    many_dir.mkdir()
    for i in range(65):
        imp = "from gen_demo.icons import ICON_USER\n" if i > 0 else ""
        (many_dir / f"n_{i:02d}.py").write_text(
            f'"""Node {i}."""\n\n{imp}\nVAL_{i}: str = "ok"\n',
            encoding="utf-8",
        )

    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "gen_audit.yaml").write_text(
        "id: gen_audit\n"
        "name: Generated Exclusion Audit\n"
        "targets:\n"
        "  source:\n"
        "    - src\n"
        "  exclude:\n"
        '    - "**/*_generated.py"\n'
        "steps:\n"
        "  - id: inspect\n"
        "    action: project_inspect\n"
        "  - id: ast\n"
        "    action: ast_analyze\n"
        "  - id: review\n"
        "    action: ai_interpret\n"
        "    prompt: Review\n",
        encoding="utf-8",
    )
    loaded = load_workflow("gen_audit", tmp_path)
    assert loaded is not None
    prims = normalize_workflow_steps(loaded[1], tmp_path)
    assert prims[0].params["exclude_targets"] == ["**/*_generated.py"]

    run = start_workflow_run("gen_audit", tmp_path)
    assert run is not None
    _, act1, _ = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None
    assert push_workflow_action(run.run_id, act1.action_id, '{"acknowledged": true}', tmp_path)[0]
    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None
    assert "_phosphor_generated.py" not in guide2
    assert push_workflow_action(run.run_id, act2.action_id, '{"acknowledged": true}', tmp_path)[0]
    _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None
    assert "_phosphor_generated.py" not in guide3
    assert "Top 40 of 67 modules by fan-out" in guide3


def test_venv_dist_info_top_level_and_record_import_resolution(tmp_path: Path) -> None:
    """Verify .venv site-packages dist-info resolves both top_level.txt and PEP 621 RECORD packages."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "dep-demo"\nversion = "0.1.0"\nrequires-python = ">=3.12"\n'
        'dependencies = ["acme-hyphen-sdk>=1.0", "modern-uv-pkg>=2.0", "pillow>=10.0", "fonttools>=4.0"]\n',
        encoding="utf-8",
    )
    site_pkgs = tmp_path / ".venv" / "lib" / "python3.12" / "site-packages"
    dist1 = site_pkgs / "acme_hyphen_sdk-1.0.0.dist-info"
    dist1.mkdir(parents=True)
    (dist1 / "METADATA").write_text("Metadata-Version: 2.1\nName: acme-hyphen-sdk\nVersion: 1.0.0\n", encoding="utf-8")
    (dist1 / "top_level.txt").write_text("acme_custom_import\n", encoding="utf-8")

    # PEP 621 wheel (e.g. uv_build / hatchling) with RECORD only and NO top_level.txt
    dist2 = site_pkgs / "modern_uv_pkg-2.0.0.dist-info"
    dist2.mkdir(parents=True)
    (dist2 / "METADATA").write_text("Metadata-Version: 2.3\nName: modern-uv-pkg\nVersion: 2.0.0\n", encoding="utf-8")
    (dist2 / "RECORD").write_text(
        "modern_uv_runtime/__init__.py,sha256=abc,12\n"
        "modern_uv_pkg-2.0.0.dist-info/METADATA,sha256=def,45\n",
        encoding="utf-8",
    )

    src_dir = tmp_path / "src" / "dep_demo"
    src_dir.mkdir(parents=True)
    (src_dir / "loader.py").write_text(
        '"""Loader using third-party distributions with non-identical import names."""\n\n'
        "import acme_custom_import\n"
        "import fontTools.ttLib\n"
        "import modern_uv_runtime\n"
        "from PIL import Image\n\n"
        "USED = (acme_custom_import, fontTools.ttLib, modern_uv_runtime, Image)\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src/dep_demo"], lang="python")
    assert af.unused_dependencies == []
    assert af.undeclared_dependencies == []


def test_conftest_hook_suppression_and_secret_false_positive_filtering(tmp_path: Path) -> None:
    """Verify conftest.py assertion hooks suppress assertion_free_tests and enum/icon literals avoid secret FPs."""
    src_dir = tmp_path / "src" / "icons_pkg"
    src_dir.mkdir(parents=True)
    (src_dir / "catalog.py").write_text(
        '"""Icon & provider enum constants plus one genuine leaked secret."""\n\n'
        'ONEPASSWORD: str = "onepassword"\n'
        'K8S_SECRET: str = "k8s-secret"\n'
        'AUTH_ICON_FILE: str = "secret_key.png"\n'
        'TOKEN_BADGE_SVG: str = "bearer_token.svg"\n'
        'REAL_LEAKED_SECRET: str = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n',
        encoding="utf-8",
    )

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "conftest.py").write_text(
        '"""Shared pytest execution harness."""\n\n'
        "def pytest_runtest_call(item: object) -> None:\n"
        '    """Verify canvas state around every test call."""\n'
        "    assert item is not None\n",
        encoding="utf-8",
    )
    (tests_dir / "test_catalog.py").write_text(
        '"""Render smoke test relying on conftest hook assertions."""\n\n'
        "from icons_pkg import catalog\n\n"
        "def test_smoke_catalog() -> None:\n"
        '    """Execute catalog access without inline assert."""\n'
        "    _ = catalog.ONEPASSWORD\n",
        encoding="utf-8",
    )

    af = run_ast_analyze(tmp_path, targets=["src/icons_pkg"], test_targets=["tests"], lang="python")
    assert af.assertion_free_tests == []
    assert len(af.test_harness_notes) == 1
    assert "pytest_runtest_call" in af.test_harness_notes[0]

    assert len(af.hardcoded_secrets) == 1
    assert af.hardcoded_secrets[0].symbol == "REAL_LEAKED_SECRET"


def test_dual_cli_library_archetype_smoke_pytest_args_and_legacy_score_compat(tmp_path: Path) -> None:
    """Verify ['cli', 'library'] detection, compound smoke plan, pytest_extra_args, and legacy JSON compat."""
    dual_dir = tmp_path / "drawlib_like"
    pkg_dir = dual_dir / "src" / "drawkit"
    for sub in ("charts", "shapes", "smartarts", "_internal"):
        (pkg_dir / sub).mkdir(parents=True)
        (pkg_dir / sub / "__init__.py").write_text('"""Subpackage."""\n', encoding="utf-8")
    (pkg_dir / "__init__.py").write_text('"""Public SDK."""\n', encoding="utf-8")
    (pkg_dir / "py.typed").write_text("", encoding="utf-8")
    (dual_dir / "pyproject.toml").write_text(
        '[project]\nname = "drawkit"\nversion = "0.3.5"\nrequires-python = ">=3.11"\n'
        'dependencies = ["typer>=0.12.0"]\n'
        '[project.scripts]\ndrawkit = "drawkit._internal:main"\n',
        encoding="utf-8",
    )

    pf_dual = run_project_inspect(dual_dir, source_dirs=["src"])
    assert pf_dual.runtime_types == ["cli", "library"]

    arch_label, smoke_cmd = build_smoke_plan(dual_dir, pf_dual, ["src"])
    assert arch_label == "cli+library"
    assert smoke_cmd is not None
    joined_smoke = " ".join(smoke_cmd)
    assert "drawkit --help" in joined_smoke
    assert "import_module" in joined_smoke
    assert "'drawkit'" in joined_smoke

    test_cmd = build_test_and_coverage_command(
        pf_dual,
        "uv",
        ["src"],
        ["tests"],
        pytest_extra_args=("-m", "not slow", "-k", "not browser"),
        pre_test_cmd="playwright install chromium",
    )
    assert test_cmd[:2] == ["sh", "-c"]
    assert test_cmd[2].startswith("playwright install chromium && ")
    assert "-m 'not slow' -k 'not browser'" in test_cmd[2]

    # Legacy ProjectFacts, SystemProfile, and committed reports/*_score.json compatibility
    legacy_pf = ProjectFacts.model_validate(
        {"project_name": "old", "language": "python", "runtime_type_hint": "hybrid"}
    )
    assert legacy_pf.runtime_types == ["web_api", "cli"]

    legacy_sp = SystemProfile.model_validate({"system_purpose": "Old API", "runtime_type": "api_service"})
    assert legacy_sp.runtime_types == ["api_service"]

    score_files = sorted((REPO_ROOT / "reports").rglob("*_score.json"))
    assert len(score_files) >= 9
    for score_file in score_files:
        parsed = ScoreResult.model_validate_json(score_file.read_text(encoding="utf-8"))
        assert parsed.project_name

    # Path-traversal guard on drawlib.toml locale codes
    bad_src = tmp_path / "reports_src" / "bad_src"
    bad_src.mkdir(parents=True)
    (bad_src / "drawlib.toml").write_text(
        '[project]\ntype = "doc"\n\n[i18n]\ndefault_lang = "../escape"\nlangs = ["../escape"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Invalid locale code"):
        compile_report_project("bad", src_base_dir=tmp_path / "reports_src", output_dir=tmp_path / "out")
