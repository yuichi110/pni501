# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit and workflow integration tests for AST security checkers, Trivy security_scan, and 6-chapter Blueprint."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pni._actions import (
    ActionItem,
    CategoryScores,
    Finding,
    InterpretationInput,
    PrimitiveType,
    RuleCheckResult,
    ScoreResult,
    SecurityScanOptions,
    run_ast_analyze,
    run_security_scan,
)
from pni._actions.runtime_check.engine_detect import CommandExecResult
from pni._actions.security_scan.models import (
    MisconfigItem,
    SecretFindingItem,
    SecurityFacts,
    VulnerabilityItem,
    VulnerabilitySummaryCounts,
)
from pni._actions.security_scan.parsers import (
    is_os_package_type,
    normalize_severity,
    parse_trivy_reports,
    redact_secret_match,
)
from pni._actions.security_scan.trivy_runner import (
    has_cached_trivy_db,
    is_infra_or_db_unavailable_error,
    run_trivy_fs_scan,
    run_trivy_image_scan,
)
from pni._cache import default_security_facts_rel_path
from pni._reporter.blueprint import build_report_blueprint
from pni._workflows import get_workflow_action, push_workflow_action, start_workflow_run
from pni._workflows.aggregator import compute_module_hotspots
from pni.cli import init_project


def test_python_security_checker_sinks_and_false_positive_guards(tmp_path: Path) -> None:
    """Verify Python CWE sink extraction and safe-pattern false-positive suppression."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "vuln_service.py").write_text(
        '"""Sample service with vulnerable and safe calls."""\n'
        "import hashlib\n"
        "import os\n"
        "import pickle\n"
        "import subprocess\n"
        "import requests\n"
        "import yaml\n\n"
        "def bad_calls(cur, uid: str, raw: bytes, cmd: str) -> None:\n"
        '    cur.execute(f"SELECT * FROM users WHERE id = {uid}")\n'
        '    cur.execute("SELECT * FROM users WHERE id = " + uid)\n'
        '    cur.execute("SELECT * FROM {}".format(uid))\n'
        "    os.system(cmd)\n"
        "    subprocess.run(cmd, shell=True)\n"
        "    eval(uid)\n"
        "    pickle.loads(raw)\n"
        "    yaml.load(raw)\n"
        "    hashlib.md5(raw)\n"
        '    requests.get("https://example.com", verify=False)\n\n'
        "def safe_calls(cur, uid: str, raw: bytes) -> None:\n"
        '    cur.execute("SELECT * FROM users WHERE id = %s", (uid,))\n'
        '    subprocess.run(["ls", "-la"], check=True)\n'
        "    yaml.load(raw, Loader=yaml.SafeLoader)\n"
        "    hashlib.md5(raw, usedforsecurity=False)\n",
        encoding="utf-8",
    )
    (src_dir / "web_cfg.py").write_text(
        '"""CORS and debug config."""\n'
        "def configure(app, flask_app) -> None:\n"
        '    app.add_middleware(object, allow_origins=["*"])\n'
        "    flask_app.run(debug=True)\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["src"], lang="python")
    cwes = [s.cwe_id for s in facts.dangerous_sinks]
    assert cwes.count("CWE-89") == 3
    assert cwes.count("CWE-78") == 2
    assert "CWE-94" in cwes
    assert cwes.count("CWE-502") == 2
    assert cwes.count("CWE-327") == 1
    assert "CWE-295" in cwes
    assert "CWE-942" in cwes
    assert "CWE-489" in cwes
    assert all(s.line < 21 for s in facts.dangerous_sinks if s.file.endswith("vuln_service.py"))


def test_python_api_endpoints_fastapi_and_flask_extraction(tmp_path: Path) -> None:
    """Verify FastAPI APIRouter and Flask Blueprint endpoint and auth hint extraction."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "routes.py").write_text(
        '"""FastAPI and Flask routes."""\n'
        "from fastapi import APIRouter, Depends\n"
        "from flask import Blueprint\n\n"
        'router = APIRouter(prefix="/v1")\n'
        'bp = Blueprint("adm", __name__, url_prefix="/admin")\n\n'
        '@router.get("/health")\n'
        "def health() -> dict[str, str]:\n"
        '    return {"ok": "true"}\n\n'
        '@router.post("/orders")\n'
        "def create_order(user=Depends(get_current_user)) -> dict[str, str]:\n"
        '    return {"user": str(user)}\n\n'
        '@bp.route("/users", methods=["GET", "DELETE"])\n'
        "@login_required\n"
        "def manage_users() -> str:\n"
        '    return "ok"\n',
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["src"], lang="python")
    by_route = {(ep.http_method, ep.path): ep for ep in facts.api_endpoints}
    assert ("GET", "/v1/health") in by_route
    assert by_route[("GET", "/v1/health")].has_auth_hint is False
    assert ("POST", "/v1/orders") in by_route
    assert by_route[("POST", "/v1/orders")].has_auth_hint is True
    assert ("GET", "/admin/users") in by_route
    assert ("DELETE", "/admin/users") in by_route
    assert by_route[("DELETE", "/admin/users")].has_auth_hint is True


def test_java_security_checker_sinks_and_spring_endpoints(tmp_path: Path) -> None:
    """Verify Java CWE sink detection and Spring @RestController endpoint extraction."""
    pkg_dir = tmp_path / "src" / "main" / "java" / "com" / "acme"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "OrderController.java").write_text(
        "package com.acme;\n"
        "import java.io.ObjectInputStream;\n"
        "import java.security.MessageDigest;\n"
        "import java.security.Principal;\n"
        "import javax.crypto.Cipher;\n"
        "import org.springframework.security.access.prepost.PreAuthorize;\n"
        "import org.springframework.web.bind.annotation.*;\n\n"
        "@CrossOrigin\n"
        "@RestController\n"
        '@RequestMapping("/api/v1")\n'
        "public class OrderController {\n"
        '    @GetMapping("/public")\n'
        "    public String pub(String id, java.sql.Statement st) throws Exception {\n"
        '        st.executeQuery("SELECT * FROM orders WHERE id=" + id);\n'
        '        st.executeQuery(String.format("SELECT * FROM %s", id));\n'
        '        st.executeQuery("SELECT * FROM orders WHERE id=1");\n'
        "        Runtime.getRuntime().exec(id);\n"
        '        new ProcessBuilder("sh", "-c", id);\n'
        "        new ObjectInputStream(null);\n"
        '        MessageDigest.getInstance("MD5");\n'
        '        Cipher.getInstance("AES/ECB/PKCS5Padding");\n'
        "        return id;\n"
        "    }\n\n"
        "    @PreAuthorize(\"hasRole('ADMIN')\")\n"
        '    @PostMapping(path = "/orders")\n'
        "    public String create() { return \"ok\"; }\n\n"
        '    @RequestMapping(value = "/me", method = RequestMethod.PUT)\n'
        "    public String updateMe(Principal principal) { return principal.getName(); }\n"
        "}\n",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, targets=["src/main/java"], lang="java")
    cwes = [s.cwe_id for s in facts.dangerous_sinks]
    assert cwes.count("CWE-89") == 2
    assert cwes.count("CWE-78") == 2
    assert "CWE-502" in cwes
    assert cwes.count("CWE-327") == 2
    assert "CWE-942" in cwes

    by_route = {(ep.http_method, ep.path): ep for ep in facts.api_endpoints}
    assert by_route[("GET", "/api/v1/public")].has_auth_hint is False
    assert by_route[("POST", "/api/v1/orders")].has_auth_hint is True
    assert "@PreAuthorize" in by_route[("POST", "/api/v1/orders")].auth_mechanisms
    assert by_route[("PUT", "/api/v1/me")].has_auth_hint is True
    assert "Principal" in by_route[("PUT", "/api/v1/me")].auth_mechanisms


def test_trivy_parsers_deduplication_classification_and_secret_redaction(tmp_path: Path) -> None:
    """Verify Trivy JSON parsing, App-vs-OS CVE separation, fixed_version upgrade, and secret redaction."""
    assert normalize_severity("critical") == "CRITICAL"
    assert normalize_severity("weird") == "UNKNOWN"
    assert is_os_package_type("debian") is True
    assert is_os_package_type("custom", "os-pkgs") is True
    assert is_os_package_type("python-pkg", "lang-pkgs") is False

    assert redact_secret_match("") == "***REDACTED***"
    assert redact_secret_match("key=***") == "key=***"
    assert redact_secret_match("API_KEY = sk_live_123456789") == "API_KEY=***REDACTED***"
    assert redact_secret_match("password: super_secret_value") == "password: ***REDACTED***"
    assert redact_secret_match("ghp_rawtoken123456") == "***REDACTED***"

    fs_json = tmp_path / "trivy_fs.json"
    img_json = tmp_path / "trivy_image.json"
    fs_json.write_text(
        json.dumps(
            {
                "Results": [
                    {
                        "Target": "uv.lock",
                        "Class": "lang-pkgs",
                        "Type": "uv",
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-2024-1111",
                                "PkgName": "urllib3",
                                "InstalledVersion": "1.26.5",
                                "FixedVersion": "",
                                "Severity": "HIGH",
                                "Title": "Redirect header leak",
                                "CVSS": {"nvd": {"V3Score": 7.5}},
                            }
                        ],
                    },
                    {
                        "Target": "Dockerfile",
                        "Class": "config",
                        "Misconfigurations": [
                            {"ID": "DS001", "Status": "PASS", "Severity": "LOW", "Title": "Passed check"},
                            {
                                "ID": "DS002",
                                "Status": "FAIL",
                                "Severity": "HIGH",
                                "Title": "Image user should not be root",
                                "CauseMetadata": {"StartLine": 4},
                            },
                        ],
                    },
                    {
                        "Target": ".env.sample",
                        "Class": "secret",
                        "Secrets": [
                            {
                                "RuleID": "aws-access-key-id",
                                "Category": "AWS",
                                "Severity": "CRITICAL",
                                "Title": "AWS Access Key ID",
                                "StartLine": 2,
                                "Match": "AWS_SECRET=AKIAIOSFODNN7EXAMPLE_RAW",
                            }
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    img_json.write_text(
        json.dumps(
            {
                "Results": [
                    {
                        "Target": "Python",
                        "Class": "lang-pkgs",
                        "Type": "python-pkg",
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-2024-1111",
                                "PkgName": "urllib3",
                                "InstalledVersion": "1.26.5",
                                "FixedVersion": "1.26.19",
                                "Severity": "HIGH",
                                "Title": "Redirect header leak",
                            }
                        ],
                    },
                    {
                        "Target": "debian 12.9",
                        "Class": "os-pkgs",
                        "Type": "debian",
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-2025-0002",
                                "PkgName": "openssl",
                                "InstalledVersion": "3.0.11",
                                "FixedVersion": "3.0.15",
                                "Severity": "CRITICAL",
                                "Title": "OpenSSL buffer issue",
                            }
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    bundle = parse_trivy_reports(fs_json, img_json)
    assert bundle.vuln_counts.total == 2
    assert bundle.app_vuln_counts.total == 1 and bundle.app_vuln_counts.high == 1
    assert bundle.os_vuln_counts.total == 1 and bundle.os_vuln_counts.critical == 1

    urllib_vuln = next(v for v in bundle.vulnerabilities if v.pkg_name == "urllib3")
    assert urllib_vuln.fixed_version == "1.26.19"
    assert len(bundle.misconfigurations) == 1 and bundle.misconfigurations[0].check_id == "DS002"
    assert len(bundle.secrets) == 1
    assert "AKIAIOSFODNN7EXAMPLE_RAW" not in bundle.secrets[0].redacted_match
    assert bundle.secrets[0].redacted_match == "AWS_SECRET=***REDACTED***"

    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not-json", encoding="utf-8")
    empty_bundle = parse_trivy_reports(corrupt, tmp_path / "missing.json")
    assert empty_bundle.vuln_counts.total == 0


def test_trivy_runner_socketless_commands_and_offline_retry(tmp_path: Path) -> None:
    """Verify socketless volume mounts, offline DB retry, and guaranteed image.tar deletion."""
    target_dir = tmp_path / "app"
    cache_dir = tmp_path / "trivy-cache"
    sec_dir = tmp_path / "sec"
    target_dir.mkdir()
    (cache_dir / "db").mkdir(parents=True)
    (cache_dir / "db" / "metadata.json").write_text("{}", encoding="utf-8")
    assert has_cached_trivy_db(cache_dir) is True
    assert is_infra_or_db_unavailable_error("FATAL failed to download vulnerability DB: dial tcp") is True

    fail_net = CommandExecResult(exit_code=1, timed_out=False, duration_sec=0.2, stdout="", stderr="dial tcp err")
    ok_offline = CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="ok", stderr="")

    with patch("pni._actions.security_scan.trivy_runner.run_safe_command", side_effect=[fail_net, ok_offline]) as m_cmd:
        res_fs = run_trivy_fs_scan("podman", "/usr/bin/podman", "trivy:0.69.3", target_dir, cache_dir, sec_dir)
        assert res_fs.exit_code == 0
        assert m_cmd.call_count == 2
        first_call = m_cmd.call_args_list[0][0][0]
        retry_call = m_cmd.call_args_list[1][0][0]
        assert not any("docker.sock" in arg for arg in first_call)
        assert "--userns=keep-id" in first_call
        assert any(arg.endswith(":/target:ro,Z") for arg in first_call)
        assert "--network=none" in retry_call and "--offline-scan" in retry_call

    def fake_img_commands(cmd: list[str], *, timeout_sec: float = 120.0) -> CommandExecResult:
        _ = timeout_sec
        if "save" in cmd:
            (sec_dir / "image.tar").write_bytes(b"fake-tar-bytes")
            return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.1, stdout="", stderr="")
        assert (sec_dir / "image.tar").is_file()
        assert not any("docker.sock" in arg for arg in cmd)
        return CommandExecResult(exit_code=1, timed_out=False, duration_sec=0.1, stdout="", stderr="scan err")

    with patch("pni._actions.security_scan.trivy_runner.run_safe_command", side_effect=fake_img_commands):
        run_trivy_image_scan("docker", "/usr/bin/docker", "trivy:0.69.3", "pni-sec:scan", cache_dir, sec_dir)
        assert not (sec_dir / "image.tar").exists()


def test_run_security_scan_skip_fail_offline_and_image_stages(tmp_path: Path) -> None:
    """Verify run_security_scan skip/fail modes, offline DB fallback, image stage, and rmi cleanup."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (src_dir / "app.py").write_text("X = 1\n", encoding="utf-8")

    skipped = run_security_scan(
        tmp_path,
        "sec_skip",
        options=SecurityScanOptions(container_engine="none", on_missing_runtime="skip"),
    )
    assert skipped.status == "skipped"
    assert (tmp_path / default_security_facts_rel_path("sec_skip")).is_file()

    with pytest.raises(RuntimeError, match="on_missing_runtime='fail'"):
        run_security_scan(
            tmp_path,
            "sec_fail_mode",
            options=SecurityScanOptions(container_engine="none", on_missing_runtime="fail"),
        )

    # Offline DB unavailable -> status='skipped'
    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch(
            "pni._actions.security_scan.runner.run_trivy_fs_scan",
            return_value=CommandExecResult(
                exit_code=1,
                timed_out=False,
                duration_sec=0.2,
                stdout="",
                stderr="failed to download vulnerability DB: dial tcp",
            ),
        ),
    ):
        db_skip = run_security_scan(tmp_path, "sec_offline")
        assert db_skip.status == "skipped"
        assert "unavailable" in db_skip.skip_reason

    # Full S0-S3 scan with HIGH app CVE -> status='failed' and temporary image cleaned up
    def fake_fs_scan(
        _eng: str,
        _bin: str,
        _img: str,
        _target: Path,
        _cache: Path,
        sec_dir: Path,
        *,
        timeout_sec: float = 240.0,
    ) -> CommandExecResult:
        _ = timeout_sec
        (sec_dir / "trivy_fs.json").write_text(
            json.dumps(
                {
                    "Results": [
                        {
                            "Target": "pyproject.toml",
                            "Type": "python-pkg",
                            "Vulnerabilities": [
                                {
                                    "VulnerabilityID": "CVE-2025-9999",
                                    "PkgName": "Werkzeug",
                                    "InstalledVersion": "2.2.0",
                                    "FixedVersion": "3.0.6",
                                    "Severity": "HIGH",
                                    "Title": "Debugger pin bypass",
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="fs ok", stderr="")

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
        (sec_dir / "trivy_image.json").write_text(json.dumps({"Results": []}), encoding="utf-8")
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="img ok", stderr="")

    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch("pni._actions.security_scan.runner.run_trivy_fs_scan", side_effect=fake_fs_scan),
        patch(
            "pni._actions.security_scan.runner.build_container_image",
            return_value=CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.4, stdout="built", stderr=""),
        ),
        patch("pni._actions.security_scan.runner.run_trivy_image_scan", side_effect=fake_img_scan),
        patch("pni._actions.security_scan.runner.remove_container_images") as mock_rmi,
    ):
        facts = run_security_scan(tmp_path, "sec_full")
        assert facts.status == "failed"
        assert facts.scanned_filesystem is True
        assert facts.scanned_resolved_image is True
        assert facts.resolved_image_source == "Dockerfile"
        assert facts.app_vuln_counts.high == 1
        assert mock_rmi.called


def test_stateful_workflow_security_scan_hotspot_and_seven_file_blueprint(tmp_path: Path) -> None:
    """Verify stateful SECURITY_SCAN workflow step, security hotspot bonuses, and 7-file Blueprint (ja/en)."""
    pkg_dir = tmp_path / "src" / "app"
    pkg_dir.mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "sec-app"\nversion = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\nUSER root\n", encoding="utf-8")
    (pkg_dir / "api.py").write_text(
        '"""API module with sink and endpoint."""\n'
        "from fastapi import APIRouter\n\n"
        'router = APIRouter(prefix="/v1")\n\n'
        '@router.post("/pay")\n'
        "def pay(cur, card: str) -> str:\n"
        '    cur.execute(f"INSERT INTO payments VALUES ({card})")\n'
        "    return card\n",
        encoding="utf-8",
    )

    init_project(tmp_path, lang="python", force=True)
    (tmp_path / ".pni" / "workflows" / "sec_flow.yaml").write_text(
        "id: sec_flow\n"
        "name: Security Audit Flow\n"
        "targets:\n"
        '  root: "."\n'
        '  source: ["src"]\n'
        "steps:\n"
        "  - id: inspect\n"
        "    action: project_inspect\n"
        "  - id: ast\n"
        "    action: ast_analyze\n"
        "    with:\n"
        '      lang: "python"\n'
        "  - id: sec\n"
        "    uses: security_vulnerability_audit\n"
        "  - id: score\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )

    mocked_sec = SecurityFacts(
        status="failed",
        container_engine="docker",
        engine_available=True,
        trivy_image="ghcr.io/aquasecurity/trivy:0.69.3",
        scanned_filesystem=True,
        scanned_resolved_image=True,
        resolved_image_source="Dockerfile",
        vuln_counts=VulnerabilitySummaryCounts(critical=1, total=1),
        app_vuln_counts=VulnerabilitySummaryCounts(critical=1, total=1),
        vulnerabilities=[
            VulnerabilityItem(
                vuln_id="CVE-2024-9000",
                pkg_name="fastapi",
                pkg_type="python-pkg",
                installed_version="0.95.0",
                fixed_version="0.109.1",
                severity="CRITICAL",
                title="ReDoS in multipart parser",
            )
        ],
        misconfigurations=[
            MisconfigItem(
                check_id="DS002",
                severity="HIGH",
                title="Root user in container",
                file_path="src/app/api.py",
                start_line=1,
            )
        ],
        secrets=[
            SecretFindingItem(
                rule_id="generic-api-key",
                category="general",
                severity="CRITICAL",
                title="Generic API Key",
                file_path="src/app/api.py",
                start_line=2,
                redacted_match="KEY=***REDACTED***",
            )
        ],
    )

    run = start_workflow_run("sec_flow", tmp_path)
    assert run is not None

    # act-01: project_inspect, act-02: ast_analyze
    for expected_id in ("act-01", "act-02"):
        _, act, _ = get_workflow_action(run.run_id, tmp_path)
        assert act is not None and act.action_id == expected_id
        assert push_workflow_action(run.run_id, expected_id, '{"acknowledged": true}', tmp_path)[0] is True

    # act-03: security_scan (inside security_vulnerability_audit composite action)
    with patch("pni._workflows.engine.run_security_scan", return_value=mocked_sec):
        _, act3, guide3 = get_workflow_action(run.run_id, tmp_path)
        assert act3 is not None and act3.primitive_type == PrimitiveType.SECURITY_SCAN
        assert "Containerized Security & Supply-Chain Scan" in guide3
        assert push_workflow_action(run.run_id, act3.action_id, '{"acknowledged": true}', tmp_path)[0] is True

    # act-04: ai_interpret for security_vulnerability_audit
    _, act4, guide4 = get_workflow_action(run.run_id, tmp_path)
    assert act4 is not None and act4.primitive_type == PrimitiveType.AI_INTERPRET
    assert "CVE-2024-9000" in guide4
    assert "CWE-89" in guide4
    assert "POST /v1/pay" in guide4

    sec_interp = InterpretationInput(
        summary="Critical CVE and SQLi on unauthenticated /v1/pay endpoint.",
        step_score=35,
        rule_checks=[
            RuleCheckResult(
                rule_id="common/security_vulnerability",
                status="fail",
                evidence="CVE-2024-9000 + CWE-89 at src/app/api.py:8",
            )
        ],
        findings=[
            Finding(
                severity="critical",
                category="security",
                rule_id="common/security_vulnerability",
                file_path="src/app/api.py",
                line=8,
                description="SQL injection in unauthenticated payment endpoint",
                recommendation="Use parameterized SQL and authentication guard",
            )
        ],
        action_items=[
            ActionItem(
                priority="P0",
                title="Parameterize SQL and upgrade fastapi",
                category="security",
                target_files=["src/app/api.py", "pyproject.toml"],
                action="Replace f-string SQL with bound parameters and bump fastapi>=0.109.1.",
                expected_impact="Eliminates SQLi and CRITICAL CVE",
                related_rules=["common/security_vulnerability"],
            )
        ],
    ).model_dump_json()
    assert push_workflow_action(run.run_id, act4.action_id, sec_interp, tmp_path)[0] is True

    # act-05: emit_score
    _, act5, _ = get_workflow_action(run.run_id, tmp_path)
    assert act5 is not None and act5.primitive_type == PrimitiveType.EMIT_SCORE
    score_payload = ScoreResult(
        project_name="sec-app",
        workflow_id="sec_flow",
        language="python",
        overall_score=58,
        category_scores=CategoryScores(
            architecture=80,
            code_quality=75,
            typing=85,
            testing=50,
            dependencies=40,
            security=30,
            documentation=70,
        ),
        summary="Critical SQLi and supply-chain vulnerabilities detected.",
    ).model_dump_json()
    assert push_workflow_action(run.run_id, act5.action_id, score_payload, tmp_path)[0] is True

    saved = ScoreResult.model_validate_json((tmp_path / "reports" / "sec_flow_score.json").read_text(encoding="utf-8"))
    assert saved.category_scores.security == 30
    assert saved.security_facts is not None and saved.security_facts.app_vuln_counts.critical == 1
    assert len(saved.dangerous_sinks) == 1 and saved.dangerous_sinks[0].cwe_id == "CWE-89"
    assert len(saved.api_endpoints) == 1 and saved.api_endpoints[0].path == "/v1/pay"

    ast_for_hs = run_ast_analyze(tmp_path, targets=["src"], lang="python")
    base_hotspots = compute_module_hotspots(saved.findings, ast_for_hs, None, ".", None)
    hotspots = compute_module_hotspots(saved.findings, ast_for_hs, None, ".", saved.security_facts)
    assert hotspots[0].file_path == "src/app/api.py"
    assert hotspots[0].risk_score == 0.87
    assert hotspots[0].risk_score > base_hotspots[0].risk_score

    bp_ja = build_report_blueprint(saved, lang="ja", target="sec_flow")
    bp_en = build_report_blueprint(saved, lang="en", target="sec_flow")
    assert len(bp_ja.chapters) == 7 and len(bp_en.chapters) == 7
    assert "security=30" in "\n".join(bp_ja.chapters[1].sorted_data_markdown)
    ch6_md = "\n".join(bp_ja.chapters[6].sorted_data_markdown)
    assert "CVE-2024-9000" in ch6_md
    assert "CWE-89" in ch6_md
    assert "`POST /v1/pay`" in ch6_md
    assert "KEY=***REDACTED***" in ch6_md


def test_run_security_scan_timeout_error_and_harness_fallback(tmp_path: Path) -> None:
    """Verify timeout/error status handling and cached harness Dockerfile fallback when no project Dockerfile exists."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "clean"\nversion = "0.1.0"\n', encoding="utf-8")
    (src_dir / "mod.py").write_text("VAL = 42\n", encoding="utf-8")

    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch(
            "pni._actions.security_scan.runner.run_trivy_fs_scan",
            return_value=CommandExecResult(exit_code=None, timed_out=True, duration_sec=15.0, stdout="", stderr=""),
        ),
    ):
        assert run_security_scan(tmp_path, "sec_to").status == "timeout"

    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch(
            "pni._actions.security_scan.runner.run_trivy_fs_scan",
            return_value=CommandExecResult(exit_code=2, timed_out=False, duration_sec=0.1, stdout="", stderr="bad arg"),
        ),
    ):
        assert run_security_scan(tmp_path, "sec_err").status == "error"

    def clean_img_scan(
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
        (sec_dir / "trivy_image.json").write_text(json.dumps({"Results": []}), encoding="utf-8")
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.2, stdout="ok", stderr="")

    with (
        patch("pni._actions.security_scan.runner.detect_container_engine", return_value=("docker", "/bin/docker", "")),
        patch(
            "pni._actions.security_scan.runner.build_container_image",
            return_value=CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="ok", stderr=""),
        ),
        patch("pni._actions.security_scan.runner.run_trivy_image_scan", side_effect=clean_img_scan),
        patch("pni._actions.security_scan.runner.remove_container_images"),
    ):
        passed = run_security_scan(
            tmp_path,
            "sec_harness",
            options=SecurityScanOptions(scan_filesystem=False, scan_resolved_image=True),
        )
        assert passed.status == "passed"
        assert passed.resolved_image_source.startswith(".pni/dockerfiles/")

