# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Regression and feature tests covering FastAPI audit feedback across Phases 1-3."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

import pni._actions.runtime_check.models as rt_models
from pni._actions import (
    CategoryScores,
    PrimitiveType,
    RuntimeFacts,
    ScoreResult,
    SecurityScanOptions,
    get_expected_input_schema_json,
    run_ast_analyze,
    run_security_scan,
)
from pni._actions.runtime_check.engine_detect import CommandExecResult
from pni._actions.security_scan.parsers import parse_trivy_reports
from pni._reporter.blueprint import build_report_blueprint
from pni._workflows import (
    WorkflowStateDB,
    get_workflow_action,
    push_workflow_action,
    rewind_workflow_run,
    start_workflow_run,
)
from pni.cli import app, init_project

runner = CliRunner()


def test_pyproject_exposes_pni501_cli_entrypoint_alias() -> None:
    """Verify [project.scripts] registers both `pni` and `pni501` entrypoints for `uvx pni501`."""
    repo_root = Path(__file__).resolve().parents[2]
    data = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = data["project"]["scripts"]
    assert scripts["pni"] == "pni.cli:main"
    assert scripts["pni501"] == "pni.cli:main"


def test_schema_descriptions_and_parenthetical_path_rejection(tmp_path: Path) -> None:
    """Verify path-grounded schemas warn against parenthetical notes and push-action rejects prose suffixes."""
    flow_schema = json.loads(
        get_expected_input_schema_json(PrimitiveType.RECORD_ARCHITECTURE, {"aspect": "flows_and_state"})
    )
    ep_desc = flow_schema["properties"]["entry_points"]["description"]
    assert "no parenthetical" in ep_desc.lower()

    layer_schema = json.loads(
        get_expected_input_schema_json(PrimitiveType.RECORD_ARCHITECTURE, {"aspect": "layers_and_modules"})
    )
    mod_desc = layer_schema["$defs"]["ModuleSummary"]["properties"]["path"]["description"]
    assert "no parenthetical" in mod_desc.lower()

    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""FastAPI package."""\n', encoding="utf-8")
    (pkg / "applications.py").write_text(
        '"""App module."""\nclass FastAPI:\n    """ASGI app."""\n',
        encoding="utf-8",
    )
    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "arch_ux.yaml").write_text(
        "id: arch_ux\n"
        "name: Arch UX\n"
        "targets:\n"
        '  root: "."\n'
        '  source: ["fastapi"]\n'
        "steps:\n"
        "  - id: ast\n"
        "    action: ast_analyze\n"
        "  - id: flows\n"
        "    action: record_architecture\n"
        "    with:\n"
        '      aspect: "flows_and_state"\n',
        encoding="utf-8",
    )

    run = start_workflow_run("arch_ux", tmp_path)
    assert run is not None
    get_workflow_action(run.run_id, tmp_path)
    assert push_workflow_action(run.run_id, "act-01", '{"acknowledged": true}', tmp_path)[0] is True

    get_workflow_action(run.run_id, tmp_path)
    bad_payload = json.dumps(
        {
            "entry_points": ["fastapi/applications.py:FastAPI (Public ASGI class)"],
            "execution_flows": [],
        }
    )
    ok_bad, err_msg = push_workflow_action(run.run_id, "act-02", bad_payload, tmp_path)
    assert ok_bad is False
    assert "without parenthetical descriptions" in err_msg

    clean_payload = json.dumps(
        {
            "entry_points": ["fastapi/applications.py:FastAPI"],
            "execution_flows": [],
        }
    )
    ok_clean, _ = push_workflow_action(run.run_id, "act-02", clean_payload, tmp_path)
    assert ok_clean is True


def test_python_import_checker_respects_ruff_and_standalone_isort_config(tmp_path: Path) -> None:
    """Verify [tool.ruff.lint.isort] known-third-party eliminates false-positive I001 warnings."""
    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""FastAPI."""\n', encoding="utf-8")
    (pkg / "params.py").write_text('"""Params."""\nclass Depends:\n    """Dep."""\n', encoding="utf-8")
    (pkg / "routing.py").write_text(
        '"""Routing."""\n'
        "from typing import Any\n\n"
        "from fastapi.params import Depends\n"
        "from pydantic import BaseModel\n"
        "from starlette.routing import Route\n\n"
        "USED = (Any, Depends, BaseModel, Route)\n",
        encoding="utf-8",
    )

    without_cfg = run_ast_analyze(tmp_path, targets=["fastapi"], lang="python")
    assert len(without_cfg.unsorted_imports) >= 1

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "fastapi"\nversion = "0.162.2"\n\n'
        "[tool.ruff.lint.isort]\n"
        'known-third-party = ["fastapi", "pydantic", "starlette"]\n',
        encoding="utf-8",
    )
    with_cfg = run_ast_analyze(tmp_path, targets=["fastapi"], lang="python")
    assert with_cfg.unsorted_imports == []
    assert with_cfg.import_hygiene_coverage_pct == 100.0


def test_python_dependency_checker_namespace_packages_and_multipart_aliases(tmp_path: Path) -> None:
    """Verify opentelemetry-* namespace packages and python-multipart resolve cleanly without .venv."""
    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "fastapi"\n'
        'version = "0.162.2"\n'
        "dependencies = [\n"
        '    "opentelemetry-api>=1.20.0",\n'
        '    "python-multipart>=0.0.9",\n'
        "]\n",
        encoding="utf-8",
    )
    (pkg / "telemetry.py").write_text(
        '"""Telemetry."""\n'
        "import multipart\n"
        "import opentelemetry\n\n"
        "USED = (multipart, opentelemetry)\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["fastapi"], lang="python")
    assert facts.unused_dependencies == []
    assert facts.undeclared_dependencies == []


def test_python_typing_checker_separates_init_missing_return_none(tmp_path: Path) -> None:
    """Verify typed `__init__` omitting `-> None` is separated from untyped parameter/return issues."""
    pkg = tmp_path / "app"
    pkg.mkdir()
    (pkg / "models.py").write_text(
        '"""Models."""\n'
        "class CleanService:\n"
        '    """Service with typed __init__ omitting -> None."""\n'
        "    def __init__(self, debug: bool = False, title: str = 'api'):\n"
        "        self.debug = debug\n"
        "        self.title = title\n\n"
        "    def run(self) -> bool:\n"
        "        return self.debug\n\n"
        "class BrokenService:\n"
        '    """Service with untyped __init__ parameter."""\n'
        "    def __init__(self, mystery):\n"
        "        self.mystery = mystery\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["app"], lang="python")
    assert len(facts.omitted_init_return_annotations) == 1
    assert facts.omitted_init_return_annotations[0].symbol == "__init__"
    assert len(facts.type_safety_issues) == 1
    assert "mystery" in facts.type_safety_issues[0].detail
    # 2 of 3 callables (CleanService.__init__ and CleanService.run) are type-safe -> 66.7%
    assert facts.type_safety_coverage_pct == 66.7


def test_python_doc_checker_recognizes_pep727_annotated_doc(tmp_path: Path) -> None:
    """Verify PEP 727 `Annotated[..., Doc("...")]` counts toward API doc coverage and Args checks."""
    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (pkg / "param_functions.py").write_text(
        '"""Parameter functions."""\n'
        "from typing import Annotated, Any\n"
        "from annotated_doc import Doc\n\n"
        "def Query(\n"
        "    default: Annotated[\n"
        "        Any,\n"
        '        Doc("Default value if the parameter is not provided."),\n'
        "    ] = None,\n"
        ") -> Any:\n"
        "    return default\n\n"
        "def hybrid_fn(\n"
        "    x: int,\n"
        '    y: Annotated[str, Doc("Documented inline via PEP 727.")] = "ok",\n'
        ") -> str:\n"
        '    """Combine Google Args and Annotated Doc.\n\n'
        "    Args:\n"
        "        x: Integer input.\n"
        '    """\n'
        "    return f'{x}:{y}'\n\n"
        'def placeholder_fn(v: Annotated[int, Doc("TODO")]) -> int:\n'
        "    return v\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["fastapi"], lang="python")
    assert facts.missing_docstrings == []
    assert facts.doc_signature_mismatches == []
    assert facts.annotated_doc_functions_count == 2
    assert len(facts.empty_docstrings) == 1
    assert facts.empty_docstrings[0].symbol == "placeholder_fn"
    # Candidates: <module>, Query, hybrid_fn, placeholder_fn -> 3/4 documented = 75.0%
    assert facts.docstring_coverage_pct == 75.0


def test_security_scan_separates_core_dev_and_harness_os_vulnerabilities(tmp_path: Path) -> None:
    """Verify 3-tier core vs dev/optional vs harness OS separation and non-truncated app_vulnerabilities."""
    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""FastAPI."""\n', encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "fastapi"\n'
        'version = "0.162.2"\n'
        'dependencies = ["starlette>=0.40.0"]\n\n'
        "[project.optional-dependencies]\n"
        'standard = ["email-validator>=2.0.0"]\n\n'
        "[dependency-groups]\n"
        'dev = ["mkdocs>=1.5.0"]\n',
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text(
        "version = 1\n\n"
        "[[package]]\n"
        'name = "fastapi"\n'
        'version = "0.162.2"\n'
        'dependencies = [{ name = "starlette" }]\n'
        "[package.optional-dependencies]\n"
        'standard = [{ name = "email-validator" }]\n\n'
        "[[package]]\n"
        'name = "starlette"\n'
        'version = "0.41.0"\n\n'
        "[[package]]\n"
        'name = "email-validator"\n'
        'version = "2.2.0"\n'
        'dependencies = [{ name = "dnspython" }]\n\n'
        "[[package]]\n"
        'name = "dnspython"\n'
        'version = "2.8.0"\n\n'
        "[[package]]\n"
        'name = "mkdocs"\n'
        'version = "1.5.0"\n',
        encoding="utf-8",
    )

    def fake_fs_scan(
        _eng: str,
        _bin: str,
        _img: str,
        _target: Path,
        _cache: Path,
        sec_dir: Path,
        *,
        timeout_sec: float = 240.0,
        **_kwargs: object,
    ) -> CommandExecResult:
        _ = timeout_sec
        app_vulns = [
            {
                "VulnerabilityID": f"CVE-2026-100{idx}",
                "PkgName": "dnspython",
                "InstalledVersion": "2.8.0",
                "FixedVersion": "2.8.1",
                "Severity": "MEDIUM",
                "Title": f"DNS resolver issue #{idx}",
            }
            for idx in range(6)
        ]
        app_vulns.append(
            {
                "VulnerabilityID": "CVE-2026-2000",
                "PkgName": "mkdocs",
                "InstalledVersion": "1.5.0",
                "FixedVersion": "1.6.0",
                "Severity": "HIGH",
                "Title": "Docs dev server issue",
            }
        )
        (sec_dir / "trivy_fs.json").write_text(
            json.dumps({"Results": [{"Target": "uv.lock", "Type": "uv", "Vulnerabilities": app_vulns}]}),
            encoding="utf-8",
        )
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.2, stdout="ok", stderr="")

    def fake_img_scan(
        _eng: str,
        _bin: str,
        _img: str,
        _tag: str,
        _cache: Path,
        sec_dir: Path,
        *,
        timeout_sec: float = 240.0,
    ) -> CommandExecResult:
        _ = timeout_sec
        os_vulns = [
            {
                "VulnerabilityID": f"CVE-2025-9{idx:03d}",
                "PkgName": f"libdeb{idx}",
                "InstalledVersion": "1.0.0",
                "FixedVersion": "1.0.1",
                "Severity": "CRITICAL",
                "Title": f"Debian base OS CVE #{idx}",
            }
            for idx in range(25)
        ]
        img_payload = {
            "Results": [
                {
                    "Target": "debian 12.13",
                    "Class": "os-pkgs",
                    "Type": "debian",
                    "Vulnerabilities": os_vulns,
                }
            ]
        }
        (sec_dir / "trivy_image.json").write_text(json.dumps(img_payload), encoding="utf-8")
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.2, stdout="ok", stderr="")

    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch("pni._actions.security_scan.runner.run_trivy_fs_scan", side_effect=fake_fs_scan),
        patch(
            "pni._actions.security_scan.runner.build_container_image",
            return_value=CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="ok", stderr=""),
        ),
        patch("pni._actions.security_scan.runner.run_trivy_image_scan", side_effect=fake_img_scan),
        patch("pni._actions.security_scan.runner.remove_container_images"),
    ):
        facts = run_security_scan(tmp_path, "fastapi_sec", source_targets=["fastapi"])
        assert facts.status == "passed"
        assert facts.core_app_vuln_counts.total == 0
        assert facts.dev_app_vuln_counts.total == 7
        assert facts.dev_app_vuln_counts.high == 1
        assert facts.dev_app_vuln_counts.medium == 6
        assert facts.os_vuln_counts.total == 0
        assert facts.harness_os_vuln_counts.total == 25
        assert len(facts.app_vulnerabilities) == 7
        assert all(v.scope == "dev_or_optional" for v in facts.app_vulnerabilities)

        strict_facts = run_security_scan(
            tmp_path,
            "fastapi_sec_strict",
            source_targets=["fastapi"],
            options=SecurityScanOptions(fail_on_dev_dependencies=True),
        )
        assert strict_facts.status == "failed"

    # Also verify non-harness project Dockerfile OS CVEs never truncate app_vulnerabilities in Blueprint
    proj_bundle = parse_trivy_reports(
        tmp_path / ".pni" / "cache" / "fastapi_sec" / "security" / "trivy_fs.json",
        tmp_path / ".pni" / "cache" / "fastapi_sec" / "security" / "trivy_image.json",
        is_harness_image=False,
    )
    assert len(proj_bundle.app_vulnerabilities) == 7
    assert len(proj_bundle.os_vulnerabilities) == 25

    score = ScoreResult(
        project_name="fastapi",
        workflow_id="fastapi_sec",
        language="python",
        overall_score=92,
        category_scores=CategoryScores(
            architecture=95,
            code_quality=92,
            typing=95,
            testing=90,
            dependencies=90,
            security=88,
            documentation=92,
        ),
        security_facts=facts,
        summary="Clean core dependencies.",
    )
    bp = build_report_blueprint(score, lang="en", target="fastapi_sec")
    ch6_md = "\n".join(bp.chapters[6].sorted_data_markdown)
    assert "CVE-2026-1005" in ch6_md
    assert "[dev_or_optional]" in ch6_md
    assert "Test Harness Base-OS" in ch6_md


def test_workflow_rewind_and_retry_action_resyncs_yaml_and_clears_downstream(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Verify `pni workflows retry-action` / `rewind` re-syncs YAML edits and updates active run state."""
    monkeypatch.chdir(tmp_path)
    pkg = tmp_path / "fastapi"
    pkg.mkdir()
    (pkg / "app.py").write_text('"""App."""\ndef ok() -> int:\n    """Return 1."""\n    return 1\n', encoding="utf-8")
    init_project(tmp_path, lang="python", force=True)

    wf_file = tmp_path / ".pni" / "workflows" / "pni501.yaml"
    wf_file.write_text(
        "id: pni501\n"
        "name: FastAPI Audit\n"
        "targets:\n"
        '  root: "."\n'
        '  source: ["fastapi"]\n'
        "steps:\n"
        "  - id: inspect\n"
        "    action: project_inspect\n"
        "  - id: runtime_verification\n"
        "    action: run_check\n"
        "    with:\n"
        "      pytest_extra_args: []\n",
        encoding="utf-8",
    )

    run = start_workflow_run("pni501", tmp_path)
    assert run is not None

    # Complete act-01
    get_workflow_action(run.run_id, tmp_path)
    assert push_workflow_action(run.run_id, "act-01", '{"acknowledged": true}', tmp_path)[0] is True

    # First attempt at act-02 fails (exit_code=2)
    failed_rf = RuntimeFacts(
        status="failed",
        container_engine="docker",
        engine_available=True,
        harness_build=rt_models.ContainerBuildResult(status="passed", exit_code=0),
        test_execution=rt_models.TestExecutionResult(status="failed", exit_code=2, error_tests=1),
    )
    with patch("pni._workflows.engine.run_runtime_check", return_value=failed_rf):
        _, act2, guide_fail = get_workflow_action(run.run_id, tmp_path)
        assert act2 is not None and act2.action_id == "act-02"
        assert "status=`failed`" in guide_fail
        assert push_workflow_action(run.run_id, "act-02", '{"acknowledged": true}', tmp_path)[0] is True

    # User updates .pni/workflows/pni501.yaml with exclude & pytest_extra_args, then runs retry-action CLI
    wf_file.write_text(
        "id: pni501\n"
        "name: FastAPI Audit\n"
        "targets:\n"
        '  root: "."\n'
        '  source: ["fastapi"]\n'
        '  exclude: ["tests/test_prepare_release.py"]\n'
        "steps:\n"
        "  - id: inspect\n"
        "    action: project_inspect\n"
        "  - id: runtime_verification\n"
        "    action: run_check\n"
        "    with:\n"
        '      pytest_extra_args: ["--ignore=tests/test_prepare_release.py"]\n',
        encoding="utf-8",
    )

    passed_rf = RuntimeFacts(
        status="passed",
        container_engine="docker",
        engine_available=True,
        harness_build=rt_models.ContainerBuildResult(status="passed", exit_code=0),
        test_execution=rt_models.TestExecutionResult(status="passed", exit_code=0, total_tests=42, passed_tests=42),
    )
    with patch("pni._workflows.engine.run_runtime_check", return_value=passed_rf) as mock_rc:
        res = runner.invoke(app, ["workflows", "retry-action", run.run_id, "act-02", "--pull"])
        assert res.exit_code == 0, res.output
        assert "Rewound workflow run" in res.output
        assert "status=`passed`" in res.output
        called_opts = mock_rc.call_args.kwargs["options"]
        assert called_opts.pytest_extra_args == ("--ignore=tests/test_prepare_release.py",)

    db = WorkflowStateDB(tmp_path)
    updated_run = db.get_run(run.run_id)
    assert updated_run is not None
    assert updated_run.targets.exclude == ["tests/test_prepare_release.py"]
    actions = db.get_actions(run.run_id)
    assert actions[0].status.value == "completed"
    assert actions[1].status.value == "in_progress"
    assert '"passed_tests": 42' in (actions[1].deterministic_output_json or "")

    # Programmatic rewind by workflow_id + primitive selector also works
    outcome = rewind_workflow_run("pni501", "run_check", tmp_path)
    assert outcome.target_action_id == "act-02"
    assert outcome.yaml_resynced is True
