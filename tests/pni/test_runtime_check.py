# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit tests for containerized runtime verification, cache Dockerfiles, parsers, and workflow integration."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from pni._actions import (
    AstFacts,
    CategoryScores,
    ModuleAstSummary,
    ModuleCoverageItem,
    ProjectFacts,
    RuntimeCheckOptions,
    ScoreResult,
    run_runtime_check,
)
from pni._actions.runtime_check.engine_detect import (
    CommandExecResult,
    build_container_image,
    detect_container_engine,
    remove_container_images,
    run_container_command,
    run_safe_command,
)
from pni._actions.runtime_check.parsers import (
    parse_jacoco_xml,
    parse_junit_xml_files,
    parse_pytest_coverage_json,
)
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_harness_tool,
    select_java_image_version,
    select_python_image_version,
)
from pni._actions.runtime_check.smoke import (
    build_smoke_plan,
    classify_boot_failure,
    evaluate_smoke_outcome,
)
from pni._cache import (
    default_runtime_facts_rel_path,
    default_target_dockerfile_rel_path,
    normalize_target_subpath,
)
from pni._dockerfiles import (
    ensure_target_dockerfile,
    list_builtin_dockerfiles,
    resolve_template_dockerfile,
)
from pni._reporter.blueprint import build_report_blueprint
from pni._workflows import get_workflow_action, push_workflow_action, start_workflow_run
from pni._workflows.aggregator import compute_module_hotspots
from pni.cli import init_project


def test_target_dockerfile_paths_and_manager(tmp_path: Path) -> None:
    """Verify target-scoped .pni/dockerfiles/ materialization, sidecar .dockerignore, reuse, and security checks."""
    assert normalize_target_subpath(".") == ""
    assert normalize_target_subpath("./examples/python/lib_clean/") == "examples/python/lib_clean"
    with pytest.raises(ValueError, match="Parent traversal"):
        normalize_target_subpath("../outside")

    assert default_target_dockerfile_rel_path(".") == ".pni/dockerfiles/Dockerfile"
    assert (
        default_target_dockerfile_rel_path("examples/python/lib_clean")
        == ".pni/dockerfiles/examples/python/lib_clean/Dockerfile"
    )

    templates = list_builtin_dockerfiles()
    assert {
        "python/uv.dockerfile",
        "python/poetry.dockerfile",
        "python/pip.dockerfile",
        "java/maven.dockerfile",
        "java/gradle.dockerfile",
    } <= set(templates)

    # Materialize for root '.' (outside .pni/cache/) and verify fallback tool
    root_df, tpl_id = ensure_target_dockerfile(tmp_path, ".", "python", "uv")
    assert tpl_id == "python/uv.dockerfile"
    assert root_df == tmp_path / ".pni" / "dockerfiles" / "Dockerfile"
    assert root_df.with_name("Dockerfile.dockerignore").is_file()
    assert not (tmp_path / ".pni" / "cache").exists()

    _, fb_id = resolve_template_dockerfile(tmp_path, "python", "unknown_tool")
    assert fb_id == "python/pip.dockerfile"
    with pytest.raises(FileNotFoundError):
        resolve_template_dockerfile(tmp_path, "cobol", "none")

    # Reuse preserves user/AI customization unless force_regenerate=True
    root_df.write_text("# custom tweak\nFROM python:3.12-slim\n", encoding="utf-8")
    reused_df, _ = ensure_target_dockerfile(tmp_path, ".", "python", "uv", force_regenerate=False)
    assert "# custom tweak" in reused_df.read_text(encoding="utf-8")

    regen_df, _ = ensure_target_dockerfile(tmp_path, ".", "python", "uv", force_regenerate=True)
    assert "# custom tweak" not in regen_df.read_text(encoding="utf-8")

    # Local .pni/dockerfiles/_templates/ override and explicit path checks
    local_override = tmp_path / ".pni" / "dockerfiles" / "_templates" / "python" / "uv.dockerfile"
    local_override.parent.mkdir(parents=True)
    local_override.write_text("FROM python:3.13-slim\n", encoding="utf-8")
    resolved_path, resolved_label = resolve_template_dockerfile(tmp_path, "python", "uv")
    assert resolved_path == local_override
    assert resolved_label.startswith("local:")

    custom_df, custom_label = ensure_target_dockerfile(
        tmp_path,
        ".",
        "python",
        "uv",
        explicit_dockerfile=".pni/dockerfiles/_templates/python/uv.dockerfile",
    )
    assert custom_df == local_override and custom_label.startswith("custom:")

    with pytest.raises(ValueError, match="must stay within workspace"):
        ensure_target_dockerfile(tmp_path, ".", "python", "uv", explicit_dockerfile="../bad.dockerfile")
    with pytest.raises(FileNotFoundError):
        ensure_target_dockerfile(tmp_path, ".", "python", "uv", explicit_dockerfile="missing.dockerfile")


def test_parsers_junit_pytest_cov_and_jacoco(tmp_path: Path) -> None:
    """Verify JUnit XML, pytest-cov JSON, JaCoCo XML parsers, and XXE DTD rejection."""
    junit_ok = tmp_path / "junit.xml"
    junit_ok.write_text(
        '<testsuites><testsuite name="s1" tests="3" failures="1" errors="0" skipped="1">'
        '<testcase classname="pkg.test_a" name="test_pass"/>'
        '<testcase classname="pkg.test_a" name="test_fail"><failure message="boom">AssertionError</failure></testcase>'
        '<testcase classname="pkg.test_a" name="test_skip"><skipped/></testcase>'
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    xxe_xml = tmp_path / "xxe.xml"
    xxe_xml.write_text('<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><testsuite/>', encoding="utf-8")

    total, passed, failed, errors, skipped, failures = parse_junit_xml_files([junit_ok, xxe_xml])
    assert (total, passed, failed, errors, skipped) == (3, 1, 1, 0, 1)
    assert len(failures) == 1
    assert failures[0].name == "test_fail"

    cov_json = tmp_path / "coverage.json"
    cov_json.write_text(
        json.dumps(
            {
                "totals": {
                    "covered_lines": 15,
                    "num_statements": 20,
                    "percent_covered": 75.0,
                    "num_branches": 10,
                    "covered_branches": 6,
                },
                "files": {
                    "src/pkg/high.py": {
                        "summary": {
                            "covered_lines": 10,
                            "num_statements": 10,
                            "percent_covered": 100.0,
                            "num_branches": 4,
                            "covered_branches": 4,
                        },
                        "missing_lines": [],
                    },
                    "src/pkg/low.py": {
                        "summary": {
                            "covered_lines": 5,
                            "num_statements": 10,
                            "percent_covered": 50.0,
                            "num_branches": 6,
                            "covered_branches": 2,
                        },
                        "missing_lines": [12, 13, 14, 15, 16],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    py_cov = parse_pytest_coverage_json(cov_json)
    assert py_cov.measured is True
    assert py_cov.line_coverage_pct == 75.0
    assert py_cov.branch_coverage_pct == 60.0
    assert py_cov.lowest_covered_modules[0].file_path == "src/pkg/low.py"
    assert py_cov.lowest_covered_modules[0].missing_lines_preview == [12, 13, 14, 15, 16]

    jacoco_xml = tmp_path / "jacoco.xml"
    jacoco_xml.write_text(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">'
        '<report name="demo">'
        '<package name="com/example/billing">'
        '<sourcefile name="InvoiceService.java">'
        '<line nr="10" mi="0" ci="3" mb="0" cb="0"/>'
        '<line nr="14" mi="2" ci="0" mb="2" cb="0"/>'
        '<counter type="LINE" missed="4" covered="6"/>'
        '<counter type="BRANCH" missed="2" covered="2"/>'
        "</sourcefile>"
        "</package>"
        '<counter type="LINE" missed="4" covered="6"/>'
        '<counter type="BRANCH" missed="2" covered="2"/>'
        "</report>",
        encoding="utf-8",
    )
    ja_cov = parse_jacoco_xml(jacoco_xml, source_root_prefix="src/main/java")
    assert ja_cov.measured is True
    assert ja_cov.line_coverage_pct == 60.0
    assert ja_cov.branch_coverage_pct == 50.0
    assert ja_cov.lowest_covered_modules[0].file_path == "src/main/java/com/example/billing/InvoiceService.java"
    assert ja_cov.lowest_covered_modules[0].missing_lines_preview == [14]

    xxe_jacoco = tmp_path / "xxe_jacoco.xml"
    xxe_jacoco.write_text(
        '<!DOCTYPE report [ <!ENTITY xxe "evil"> ]><report name="demo"/>',
        encoding="utf-8",
    )
    assert parse_jacoco_xml(xxe_jacoco).measured is False


def test_selector_and_smoke_planning(tmp_path: Path) -> None:
    """Verify runtime version selection, harness command building, and smoke classification."""
    assert select_python_image_version(None) == "3.12"
    assert select_python_image_version(">=3.11") == "3.12"
    assert select_python_image_version("==3.11.*") == "3.11"
    assert select_python_image_version(">=3.13") == "3.13"
    assert select_java_image_version(None) == "21"
    assert select_java_image_version("1.8") == "8"
    assert select_java_image_version("11") == "11"
    assert select_java_image_version("17") == "17"
    assert select_java_image_version("21") == "21"

    pf_uv = ProjectFacts(
        project_name="app",
        language="python",
        build_system="hatchling",
        lockfiles_found=["uv.lock"],
        language_version_constraint=">=3.12",
        runtime_types=["web_api"],
    )
    assert select_harness_tool(pf_uv) == "uv"
    assert select_harness_tool(ProjectFacts(project_name="p", language="python", lockfiles_found=["poetry.lock"])) == (
        "poetry"
    )
    assert select_harness_tool(ProjectFacts(project_name="g", language="java", build_system="gradle")) == "gradle"
    assert compute_harness_build_args(pf_uv, extra_apt_packages="libpq-dev") == {
        "PYTHON_VERSION": "3.12",
        "EXTRA_APT_PACKAGES": "libpq-dev",
    }
    cmd = build_test_and_coverage_command(pf_uv, "uv", ["src"], ["tests"])
    assert "--cov=src" in " ".join(cmd)
    assert build_test_and_coverage_command(pf_uv, "uv", ["src"], ["tests"], override_cmd="pytest -q") == [
        "sh",
        "-c",
        "pytest -q",
    ]

    pf_java = ProjectFacts(
        project_name="svc",
        language="java",
        build_system="maven",
        language_version_constraint="21",
        runtime_types=["web_api"],
    )
    assert select_harness_tool(pf_java) == "maven"
    assert compute_harness_build_args(pf_java) == {"JAVA_VERSION": "21"}
    java_cmd = build_test_and_coverage_command(pf_java, "maven", ["src/main/java"], ["src/test/java"])
    assert "jacoco" in " ".join(java_cmd)
    gradle_cmd = build_test_and_coverage_command(pf_java, "gradle", ["src/main/java"], ["src/test/java"])
    assert "jacocoTestReport" in " ".join(gradle_cmd)

    # Failure classification
    assert classify_boot_failure("", timed_out=True) == "timeout"
    assert classify_boot_failure("BeanCurrentlyInCreationException: cycle", timed_out=False) == "import_or_di_error"
    assert classify_boot_failure("PlaceholderCouldNotBeResolved", timed_out=False) == "config_missing"
    assert (
        classify_boot_failure("ConnectionRefusedError: [Errno 111]", timed_out=False)
        == "external_service_unreachable"
    )
    assert classify_boot_failure("Segmentation fault", timed_out=False) == "crash"

    # Python web_api, cli, and Java web_api smoke discovery
    app_dir = tmp_path / "src" / "demo_api"
    app_dir.mkdir(parents=True)
    (app_dir / "__init__.py").write_text("", encoding="utf-8")
    (app_dir / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
    arch, smoke_cmd = build_smoke_plan(tmp_path, pf_uv, ["src"])
    assert arch == "web_api"
    assert smoke_cmd is not None and "demo_api.main" in " ".join(smoke_cmd)

    (tmp_path / "pyproject.toml").write_text('[project.scripts]\ndemo-cli = "demo_api.main:run"\n', encoding="utf-8")
    pf_cli = ProjectFacts(project_name="cli", language="python", runtime_types=["cli"])
    cli_arch, cli_cmd = build_smoke_plan(tmp_path, pf_cli, ["src"])
    assert cli_arch == "cli" and cli_cmd is not None and "demo-cli --help" in " ".join(cli_cmd)

    java_pkg = tmp_path / "src" / "main" / "java" / "com" / "acme"
    java_pkg.mkdir(parents=True)
    (java_pkg / "App.java").write_text(
        "package com.acme;\npublic class App { public static void main(String[] args) {} }\n",
        encoding="utf-8",
    )
    j_arch, j_cmd = build_smoke_plan(tmp_path, pf_java, ["src/main/java"])
    assert j_arch == "web_api" and j_cmd is not None and "com.acme.App" in " ".join(j_cmd)

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "smoke.json").write_text(
        json.dumps({"probed_endpoint": "/healthz", "http_status": 200, "detail": "ok"}),
        encoding="utf-8",
    )
    ok_res = CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.4, stdout="", stderr="")
    smoke_eval = evaluate_smoke_outcome("web_api", smoke_cmd, ok_res, out_dir)
    assert smoke_eval.status == "passed"
    assert smoke_eval.http_status == 200

    fail_res = CommandExecResult(
        exit_code=1,
        timed_out=False,
        duration_sec=0.2,
        stdout="",
        stderr="ImportError: No module named foo",
    )
    fail_eval = evaluate_smoke_outcome("library", ["python", "-c", "import foo"], fail_res, tmp_path)
    assert fail_eval.status == "failed" and fail_eval.failure_kind == "import_or_di_error"


def test_engine_detect_and_runner_mocked(tmp_path: Path) -> None:
    """Verify engine detection flags, skip/fail modes, build-failure blocking, and full Stage 0-4 pass."""
    src_dir = tmp_path / "src" / "pkg"
    tests_dir = tmp_path / "tests"
    src_dir.mkdir(parents=True)
    tests_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "pkg"\nversion = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (src_dir / "__init__.py").write_text('"""Pkg."""\nX = 1\n', encoding="utf-8")
    (tests_dir / "test_pkg.py").write_text("def test_x():\n    assert 1 == 1\n", encoding="utf-8")

    # 1. Explicit container_engine="none" -> skipped (or RuntimeError when on_missing_runtime="fail")
    name, binary, _ = detect_container_engine("none")
    assert name is None and binary is None

    skipped = run_runtime_check(
        tmp_path,
        "wf_skip",
        options=RuntimeCheckOptions(container_engine="none", on_missing_runtime="skip"),
    )
    assert skipped.status == "skipped"
    assert skipped.harness_dockerfile_path == ".pni/dockerfiles/Dockerfile"
    assert (tmp_path / default_runtime_facts_rel_path("wf_skip")).is_file()
    assert (tmp_path / ".pni" / "dockerfiles" / "Dockerfile").is_file()

    with pytest.raises(RuntimeError, match="on_missing_runtime='fail'"):
        run_runtime_check(
            tmp_path,
            "wf_fail_mode",
            options=RuntimeCheckOptions(container_engine="none", on_missing_runtime="fail"),
        )

    # 2. Verify podman volume :Z and --network=none flags in run_container_command / build_container_image
    with patch("pni._actions.runtime_check.engine_detect.run_safe_command") as mock_cmd:
        mock_cmd.return_value = CommandExecResult(
            exit_code=0,
            timed_out=False,
            duration_sec=0.1,
            stdout="ok",
            stderr="",
        )
        build_container_image("/usr/bin/docker", "tag:1", tmp_path / "Dockerfile", tmp_path, {"PYTHON_VERSION": "3.12"})
        build_args_sent = mock_cmd.call_args[0][0]
        assert "--build-arg" in build_args_sent and "PYTHON_VERSION=3.12" in build_args_sent

        run_container_command("podman", "/usr/bin/podman", "tag:1", ["pytest"], tmp_path / "out", allow_network=False)
        run_args_sent = mock_cmd.call_args[0][0]
        assert "--network=none" in run_args_sent
        assert "--userns=keep-id" in run_args_sent
        assert any(arg.endswith(":/out:rw,Z") for arg in run_args_sent)

    # 3. Harness build failure blocks Stage 2 & Stage 3 cleanly
    with (
        patch(
            "pni._actions.runtime_check.runner.detect_container_engine",
            return_value=("docker", "/usr/bin/docker", ""),
        ),
        patch(
            "pni._actions.runtime_check.runner.build_container_image",
            return_value=CommandExecResult(exit_code=1, timed_out=False, duration_sec=0.3, stdout="", stderr="apt err"),
        ),
        patch("pni._actions.runtime_check.runner.remove_container_images"),
    ):
        blocked = run_runtime_check(tmp_path, "wf_blocked")
        assert blocked.status == "failed"
        assert blocked.test_execution.status == "blocked"
        assert blocked.smoke_check.status == "blocked"

    # 4. Mocked full Stage 0 -> 1A -> 1B -> 2 -> 3 -> 4 pass
    def fake_run_container(
        _eng_name: str,
        _eng_bin: str,
        _tag: str,
        cmd_args: list[str],
        out_dir: Path,
        *,
        allow_network: bool = False,
        timeout_sec: float = 120.0,
    ) -> CommandExecResult:
        _ = (allow_network, timeout_sec)
        joined = " ".join(cmd_args)
        if "pytest" in joined:
            (out_dir / "junit.xml").write_text('<testsuite tests="2" failures="0" errors="0"/>', encoding="utf-8")
            (out_dir / "coverage.json").write_text(
                json.dumps(
                    {
                        "totals": {
                            "covered_lines": 8,
                            "num_statements": 10,
                            "percent_covered": 80.0,
                            "num_branches": 0,
                            "covered_branches": 0,
                        },
                        "files": {},
                    }
                ),
                encoding="utf-8",
            )
        else:
            (out_dir / "smoke.json").write_text(json.dumps({"detail": "Imported pkg cleanly"}), encoding="utf-8")
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.2, stdout="ok", stderr="")

    with (
        patch(
            "pni._actions.runtime_check.runner.detect_container_engine",
            return_value=("docker", "/usr/bin/docker", ""),
        ),
        patch(
            "pni._actions.runtime_check.runner.build_container_image",
            return_value=CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.5, stdout="built", stderr=""),
        ),
        patch("pni._actions.runtime_check.runner.run_container_command", side_effect=fake_run_container),
        patch("pni._actions.runtime_check.runner.remove_container_images") as mock_rmi,
    ):
        passed = run_runtime_check(tmp_path, "wf_pass")
        assert passed.status == "passed"
        assert passed.project_dockerfile_build is not None and passed.project_dockerfile_build.status == "passed"
        assert passed.test_execution.passed_tests == 2
        assert passed.coverage.line_coverage_pct == 80.0
        assert passed.smoke_check.status == "passed"
        assert mock_rmi.called


def test_stateful_workflow_run_check_and_blueprint_integration(tmp_path: Path) -> None:
    """Verify stateful RUN_CHECK action execution, low-coverage hotspot bonus, and ReportBlueprint output."""
    pkg_dir = tmp_path / "src" / "demo"
    pkg_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    (pkg_dir / "service.py").write_text(
        '"""Service."""\n\ndef compute(x: int) -> int:\n    """Compute."""\n    return x * 2\n',
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "rt_flow.yaml").write_text(
        "id: rt_flow\n"
        "name: Runtime Flow\n"
        "steps:\n"
        "  - id: s1\n"
        "    action: project_inspect\n"
        "  - id: s2\n"
        "    action: run_check\n"
        "    with:\n"
        '      container_engine: "none"\n'
        '      on_missing_runtime: "skip"\n'
        "  - id: s3\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )

    run = start_workflow_run("rt_flow", tmp_path)
    assert run is not None

    # Step 1: project_inspect
    _, act1, _ = get_workflow_action(run.run_id, tmp_path)
    assert act1 is not None and act1.action_id == "act-01"
    ok1, _ = push_workflow_action(run.run_id, "act-01", '{"acknowledged": true}', tmp_path)
    assert ok1

    # Step 2: run_check
    _, act2, guide2 = get_workflow_action(run.run_id, tmp_path)
    assert act2 is not None and act2.action_id == "act-02"
    assert "Containerized Runtime Verification" in guide2
    ok2, _ = push_workflow_action(run.run_id, "act-02", '{"acknowledged": true}', tmp_path)
    assert ok2

    # Step 3: emit_score
    _, act3, _ = get_workflow_action(run.run_id, tmp_path)
    assert act3 is not None and act3.action_id == "act-03"
    score_payload = ScoreResult(
        project_name="demo",
        workflow_id="rt_flow",
        language="python",
        overall_score=90,
        category_scores=CategoryScores(
            architecture=90,
            code_quality=90,
            typing=90,
            testing=90,
            dependencies=90,
            documentation=90,
        ),
        summary="Verified runtime flow.",
    ).model_dump_json()
    ok3, _ = push_workflow_action(run.run_id, "act-03", score_payload, tmp_path)
    assert ok3

    saved_score = ScoreResult.model_validate_json(
        (tmp_path / "reports" / "rt_flow_score.json").read_text(encoding="utf-8")
    )
    assert saved_score.runtime_facts is not None
    assert saved_score.metrics_snapshot["runtime_status"] == "skipped"

    # Verify low-coverage hotspot bonus & blueprint rendering when coverage is measured
    saved_score.runtime_facts.coverage.measured = True
    saved_score.runtime_facts.coverage.line_coverage_pct = 20.0
    saved_score.runtime_facts.coverage.lowest_covered_modules = [
        ModuleCoverageItem(
            file_path="src/demo/service.py",
            line_coverage_pct=0.0,
            covered_lines=0,
            total_statements=10,
            missing_lines_preview=[3, 5],
        )
    ]
    ast_facts = AstFacts(
        language="python",
        total_files=1,
        total_loc=10,
        module_inventory=[ModuleAstSummary(file="src/demo/service.py", loc=10)],
    )
    hotspots = compute_module_hotspots([], ast_facts, saved_score.runtime_facts, ".")
    assert hotspots[0].risk_score >= 0.16

    bp = build_report_blueprint(saved_score, target="rt_flow")
    assert any("Container Runtime Verification" in line for line in bp.chapters[1].sorted_data_markdown)
    assert any("Lowest-Covered Modules" in line for line in bp.chapters[5].sorted_data_markdown)


def test_engine_detect_subprocess_and_cleanup_branches() -> None:
    """Verify run_safe_command execution/timeout, detect_container_engine branches, and image cleanup."""
    ok = run_safe_command([sys.executable, "-c", "print('hello')"], timeout_sec=5.0)
    assert ok.exit_code == 0 and not ok.timed_out and "hello" in ok.combined_output
    assert ok.tail_lines(5) == ["hello"]

    timed_out = run_safe_command([sys.executable, "-c", "import time; time.sleep(2)"], timeout_sec=0.05)
    assert timed_out.timed_out is True and timed_out.exit_code is None

    with patch("pni._actions.runtime_check.engine_detect.shutil.which", return_value=None):
        eng, binary, reason = detect_container_engine("auto")
        assert eng is None and binary is None and "not found" in reason

    with (
        patch("pni._actions.runtime_check.engine_detect.shutil.which", return_value="/usr/bin/docker"),
        patch(
            "pni._actions.runtime_check.engine_detect.run_safe_command",
            return_value=CommandExecResult(exit_code=1, timed_out=False, duration_sec=0.1, stdout="", stderr="down"),
        ),
    ):
        eng2, binary2, reason2 = detect_container_engine("docker")
        assert eng2 is None and binary2 is None and "exit=1" in reason2

    with patch("pni._actions.runtime_check.engine_detect.run_safe_command") as mock_cmd:
        remove_container_images("/usr/bin/docker", [])
        assert not mock_cmd.called
        remove_container_images("/usr/bin/docker", ["img:1", "img:1", "img:2"])
        assert mock_cmd.call_args[0][0] == ["/usr/bin/docker", "rmi", "-f", "img:1", "img:2"]

