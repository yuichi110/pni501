# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for language-agnostic engineering standards (OpenSSF, 12-Factor, SRE PRR, SIG, clig.dev, Diátaxis)."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    CategoryScores,
    ScoreResult,
    list_actions,
    load_composite_action,
    run_ast_analyze,
    run_project_inspect,
)
from pni._rules import get_rule_content, list_rules
from pni._workflows import (
    get_workflow_action,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    start_workflow_run,
)


def test_openssf_supply_chain_dockerfile_and_diataxis_inspection(tmp_path: Path) -> None:
    """Verify GitHub Actions permissions/pinning, secret files, Dockerfile hygiene, and Diátaxis doc extraction."""
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "lib-demo"\nversion = "0.2.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["pydantic==2.8.2"]\n',
        encoding="utf-8",
    )
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("Apache-2.0\n", encoding="utf-8")
    (tmp_path / "SECURITY.md").write_text("# Security Policy\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")

    gh_dir = tmp_path / ".github" / "workflows"
    gh_dir.mkdir(parents=True)
    (tmp_path / ".github" / "dependabot.yml").write_text("version: 2\n", encoding="utf-8")
    (gh_dir / "ci.yml").write_text(
        "name: CI\n"
        "on: pull_request_target\n"
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@main\n",
        encoding="utf-8",
    )
    (gh_dir / "hardened.yml").write_text(
        "name: Hardened\n"
        "on: [push]\n"
        "permissions:\n"
        "  contents: read\n"
        "jobs:\n"
        "  lint:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    # Committed secrets vs safe templates and test fixtures
    (tmp_path / ".env").write_text("DB_URL=postgres://localhost/db\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("DB_URL=\n", encoding="utf-8")
    (tmp_path / "server.pem").write_text("-----BEGIN KEY-----\n", encoding="utf-8")
    fixture_dir = tmp_path / "tests" / "fixtures"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "fake_credentials.json").write_text("{}\n", encoding="utf-8")

    # Unhardened Dockerfile (latest tag, root user, no .dockerignore)
    (tmp_path / "Dockerfile").write_text(
        "FROM python:latest\n"
        "COPY . /app\n"
        "CMD [\"python\", \"-m\", \"app\"]\n",
        encoding="utf-8",
    )

    # README with fenced code comment (must not be parsed as heading) + Diátaxis docs/
    (tmp_path / "README.md").write_text(
        "# Lib Demo\n\n"
        "```bash\n"
        "# shell comment inside fence\n"
        "uv sync\n"
        "```\n\n"
        "## Installation\n\n"
        "### Quickstart\n",
        encoding="utf-8",
    )
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "tutorial.md").write_text("# Tutorial\n", encoding="utf-8")
    (docs_dir / "architecture.md").write_text("# Architecture\n", encoding="utf-8")

    pf = run_project_inspect(tmp_path)
    assert pf.runtime_types == ["library"]
    assert pf.has_license is True
    assert pf.has_security_policy is True
    assert pf.has_dependency_automation is True
    assert len(pf.ci_workflows_found) == 2

    ci_joined = " | ".join(pf.ci_supply_chain_issues)
    assert "ci.yml: uses privileged 'pull_request_target'" in ci_joined
    assert "ci.yml: missing explicit GITHUB_TOKEN 'permissions:'" in ci_joined
    assert "actions/checkout@main" in ci_joined
    assert "hardened.yml" not in ci_joined

    assert ".env" in pf.committed_secret_files
    assert "server.pem" in pf.committed_secret_files
    assert ".env.example" not in pf.committed_secret_files
    assert not any("fake_credentials.json" in s for s in pf.committed_secret_files)

    assert pf.has_dockerfile is True
    docker_joined = " | ".join(pf.container_hygiene_issues)
    assert "python:latest" in docker_joined
    assert "runs as root" in docker_joined
    assert ".dockerignore" in docker_joined

    assert pf.readme_headings == ["# Lib Demo", "## Installation", "### Quickstart"]
    assert "docs/tutorial.md" in pf.docs_inventory
    assert "docs/architecture.md" in pf.docs_inventory
    assert "CHANGELOG.md" in pf.docs_inventory
    assert any("strict '==' pins" in issue for issue in pf.tooling_modernization_issues)


def test_runtime_types_archetypes_and_clean_multistage_dockerfile(tmp_path: Path) -> None:
    """Verify runtime_types enumerates web_api, worker, cli, and multi-archetype lists accurately."""
    web_dir = tmp_path / "web"
    web_dir.mkdir()
    (web_dir / "pyproject.toml").write_text(
        '[project]\nname = "api"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["fastapi>=0.115.0"]\n',
        encoding="utf-8",
    )
    (web_dir / ".dockerignore").write_text(".git\n.env\n", encoding="utf-8")
    (web_dir / "Dockerfile").write_text(
        "FROM python:3.12-slim AS builder\n"
        "RUN echo build\n"
        "FROM builder\n"
        "USER appuser\n"
        "CMD [\"uvicorn\", \"app:app\"]\n",
        encoding="utf-8",
    )
    pf_web = run_project_inspect(web_dir)
    assert pf_web.runtime_types == ["web_api"]
    assert pf_web.has_dockerfile is True
    assert pf_web.container_hygiene_issues == []

    worker_dir = tmp_path / "worker"
    worker_dir.mkdir()
    (worker_dir / "pyproject.toml").write_text(
        '[project]\nname = "worker"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["celery>=5.4.0"]\n',
        encoding="utf-8",
    )
    assert run_project_inspect(worker_dir).runtime_types == ["worker"]

    multi_dir = tmp_path / "multi"
    multi_dir.mkdir()
    (multi_dir / "pyproject.toml").write_text(
        '[project]\nname = "multi"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["fastapi>=0.115.0", "typer>=0.12.0"]\n'
        '[project.scripts]\napp-cli = "multi.cli:main"\n',
        encoding="utf-8",
    )
    assert run_project_inspect(multi_dir).runtime_types == ["web_api", "cli"]


def test_python_and_java_sig_interfacing_and_operational_checkers(tmp_path: Path) -> None:
    """Verify SIG excessive_parameters (>6) and 12-Factor/SRE/OWASP operational checks in Python and Java."""
    py_src = tmp_path / "src" / "svc"
    py_src.mkdir(parents=True)

    # Centralized config.py and cli.py must NOT trigger scattered_env_access or unstructured_logging
    (py_src / "config.py").write_text(
        '"""Central config."""\n\nimport os\n\nAPI_URL: str = os.getenv("API_URL", "https://api.example.com")\n',
        encoding="utf-8",
    )
    (py_src / "cli.py").write_text(
        '"""CLI presentation."""\n\ndef main() -> None:\n    """Run CLI."""\n    print("Hello CLI")\n',
        encoding="utf-8",
    )

    # Domain service violating SIG (>6 params), SRE PRR (no timeout), 12-Factor III & XI, and OWASP ASVS
    (py_src / "orders.py").write_text(
        '"""Order service."""\n\n'
        "import os\n"
        "import requests\n\n"
        'API_KEY_HEADER: str = "X-Api-Key"\n'
        'PLACEHOLDER_SECRET: str = "changeme"\n'
        'STRIPE_API_KEY: str = "sk_live_9876543210abcdef"\n\n'
        "def create_order(\n"
        "    user_id: str,\n"
        "    sku: str,\n"
        "    qty: int,\n"
        "    price: float,\n"
        "    currency: str,\n"
        "    coupon: str,\n"
        "    region: str,\n"
        ") -> dict[str, str]:\n"
        '    """Create order."""\n'
        '    region_override = os.getenv("ORDER_REGION", region)\n'
        "    print(region_override)\n"
        '    requests.post("https://pay.example.com/charge")\n'
        '    requests.get("https://pay.example.com/ok", timeout=5)\n'
        "    return {}\n",
        encoding="utf-8",
    )

    py_facts = run_ast_analyze(tmp_path, targets=["src"], lang="python")
    assert len(py_facts.excessive_parameters) == 1
    assert py_facts.excessive_parameters[0].symbol == "create_order"
    assert len(py_facts.missing_io_timeouts) == 1
    assert py_facts.missing_io_timeouts[0].symbol == "requests.post"
    assert len(py_facts.scattered_env_access) == 1
    assert "orders.py" in py_facts.scattered_env_access[0].file
    assert len(py_facts.unstructured_logging) == 1
    assert "orders.py" in py_facts.unstructured_logging[0].file
    assert len(py_facts.hardcoded_secrets) == 1
    assert py_facts.hardcoded_secrets[0].symbol == "STRIPE_API_KEY"

    # Java operational & SIG parameter checks
    j_src = tmp_path / "src" / "main" / "java" / "com" / "acme"
    j_src.mkdir(parents=True)
    (j_src / "AppConfig.java").write_text(
        "package com.acme;\n"
        "/** App config. */\n"
        "public class AppConfig {\n"
        "    public String region() { return System.getenv(\"APP_REGION\"); }\n"
        "}\n",
        encoding="utf-8",
    )
    (j_src / "PaymentService.java").write_text(
        "package com.acme;\n"
        "import java.net.http.HttpClient;\n"
        "/** Payment service. */\n"
        "public class PaymentService {\n"
        '    private static final String CLIENT_SECRET = "sec_prod_A1B2C3D4E5F6";\n'
        "    /** Charge customer. */\n"
        "    public void charge(String a, String b, String c, int d, int e, boolean f, String g) {\n"
        "        String mode = System.getenv(\"PAY_MODE\");\n"
        "        HttpClient client = HttpClient.newHttpClient();\n"
        "        try { System.out.println(mode + client); } catch (Exception ex) { ex.printStackTrace(); }\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )

    j_facts = run_ast_analyze(tmp_path, targets=["src/main/java"], lang="java")
    assert len(j_facts.excessive_parameters) == 1
    assert j_facts.excessive_parameters[0].symbol == "charge"
    assert len(j_facts.missing_io_timeouts) == 1
    assert j_facts.missing_io_timeouts[0].symbol == "HttpClient.newHttpClient"
    assert len(j_facts.scattered_env_access) == 1
    assert "PaymentService.java" in j_facts.scattered_env_access[0].file
    assert len(j_facts.unstructured_logging) == 2  # System.out + printStackTrace
    assert len(j_facts.hardcoded_secrets) == 1
    assert j_facts.hardcoded_secrets[0].symbol == "CLIENT_SECRET"


def test_universal_rules_archetype_actions_and_engine_metrics(tmp_path: Path) -> None:
    """Verify common universal/archetype rules, composite actions, and workflow metrics_snapshot integration."""
    rule_ids = {r.identifier for r in list_rules(tmp_path, lang="python", include_all=True)}
    expected_rules = {
        "common/supply_chain",
        "common/maintainability",
        "common/security",
        "common/documentation",
        "common/twelve_factor",
        "common/production_readiness",
        "common/cli_guidelines",
        "common/library_guidelines",
        "common/workflow_guide",
    }
    assert expected_rules.issubset(rule_ids)
    wf_guide = get_rule_content("common/workflow_guide", tmp_path)
    assert wf_guide is not None
    assert "service_readiness_audit" in wf_guide[1]
    assert "cli_guidelines_audit" in wf_guide[1]
    assert "library_hygiene_audit" in wf_guide[1]

    action_ids = {a.id for a in list_actions(tmp_path)}
    for aid in ("supply_chain_audit", "service_readiness_audit", "cli_guidelines_audit", "library_hygiene_audit"):
        assert aid in action_ids
        assert load_composite_action(aid, tmp_path) is not None

    # End-to-end workflow composing repo_structure_audit + python_ast_audit + service_readiness_audit + emit_score
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "svc"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
        'dependencies = ["fastapi>=0.115.0"]\n',
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "api.py").write_text(
        '"""API module."""\n\nimport requests\n\ndef ping() -> None:\n    """Ping."""\n    requests.get("https://example.com")\n',
        encoding="utf-8",
    )
    wf_dir = tmp_path / ".pni" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "svc_audit.yaml").write_text(
        "id: svc_audit\n"
        "name: Service Readiness Audit\n"
        "steps:\n"
        "  - id: s1\n"
        "    uses: repo_structure_audit\n"
        "  - id: s2\n"
        "    uses: python_ast_audit\n"
        "  - id: s3\n"
        "    uses: service_readiness_audit\n"
        "  - id: s4\n"
        "    uses: emit_score\n",
        encoding="utf-8",
    )

    loaded = load_workflow("svc_audit", tmp_path)
    assert loaded is not None
    prims = normalize_workflow_steps(loaded[1], tmp_path)
    assert len(prims) == 6

    run = start_workflow_run("svc_audit", tmp_path)
    assert run is not None

    # Step 1: project_inspect -> Step 2: ai_interpret -> Step 3: ast_analyze -> Step 4-5: ai_interpret -> emit_score
    _, a1, g1 = get_workflow_action(run.run_id, tmp_path)
    assert a1 is not None and "runtime_types: `['web_api']`" in g1
    push_workflow_action(run.run_id, "act-01", '{"acknowledged": true}', tmp_path)

    get_workflow_action(run.run_id, tmp_path)
    push_workflow_action(run.run_id, "act-02", json.dumps({"summary": "Repo checked."}), tmp_path)

    _, a3, g3 = get_workflow_action(run.run_id, tmp_path)
    assert a3 is not None and "Missing External I/O Timeouts (SRE PRR)" in g3
    push_workflow_action(run.run_id, "act-03", '{"acknowledged": true}', tmp_path)

    get_workflow_action(run.run_id, tmp_path)
    push_workflow_action(run.run_id, "act-04", json.dumps({"summary": "AST checked."}), tmp_path)

    _, a5, g5 = get_workflow_action(run.run_id, tmp_path)
    assert a5 is not None and "common/twelve_factor" in g5 and "common/production_readiness" in g5
    push_workflow_action(run.run_id, "act-05", json.dumps({"summary": "12-Factor & SRE PRR checked."}), tmp_path)

    get_workflow_action(run.run_id, tmp_path)
    score_json = ScoreResult(
        project_name="svc",
        workflow_id="svc_audit",
        language="python",
        overall_score=80,
        category_scores=CategoryScores(
            architecture=80,
            code_quality=75,
            typing=100,
            testing=70,
            dependencies=80,
            documentation=85,
        ),
        summary="Service evaluated.",
    ).model_dump_json()
    ok, _ = push_workflow_action(run.run_id, "act-06", score_json, tmp_path)
    assert ok is True

    score_text = (tmp_path / "reports" / "svc_audit_score.json").read_text(encoding="utf-8")
    emitted = ScoreResult.model_validate_json(score_text)
    assert emitted.metrics_snapshot["runtime_types"] == ["web_api"]
    assert emitted.metrics_snapshot["missing_io_timeouts_count"] == 1
    assert emitted.metrics_snapshot["excessive_parameters_count"] == 0
