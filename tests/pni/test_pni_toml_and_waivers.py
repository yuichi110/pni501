# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for .pni/pni.toml manifest, [scan] gitignore filtering, [[opt_out]] waivers, and [report] publishing."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from pni._actions import (
    CategoryScores,
    Finding,
    InterpretationInput,
    PrimitiveType,
    RuleCheckResult,
    ScoreResult,
    run_ast_analyze,
    run_project_inspect,
)
from pni._actions.security_scan.parsers import parse_trivy_reports
from pni._config import (
    OptOutEntry,
    discover_gitignored_paths,
    load_pni_config,
    match_opt_out,
    scaffold_pni_config,
)
from pni._reporter import compile_report_project, scaffold_report_project
from pni._reporter.blueprint import build_report_blueprint
from pni._workflows import ActionRunRecord
from pni._workflows.aggregator import WorkflowFactsBundle, compile_workflow_digest
from pni._workflows.base_model import (
    RunStatus,
    WorkflowDefinition,
    WorkflowOutputs,
    WorkflowStepSpec,
    WorkflowTargets,
)
from pni._workflows.manager import normalize_workflow_steps
from pni.cli import app

runner = CliRunner()


def test_pni_toml_scaffold_and_opt_out_validation(tmp_path: Path) -> None:
    """Verify .pni/pni.toml scaffolding, pni init CLI, and OptOutEntry mandatory reason validation."""
    created = scaffold_pni_config(tmp_path, lang="python")
    assert len(created) == 1
    assert (tmp_path / ".pni" / "pni.toml").is_file()

    # Second call without force=True is a no-op
    assert scaffold_pni_config(tmp_path, lang="python", force=False) == []

    cfg = load_pni_config(tmp_path)
    assert cfg.scan.respect_gitignore is True
    assert "uv.lock" in cfg.scan.include_gitignored
    assert cfg.report.src_dir == "reports_src"

    # OptOutEntry requires non-empty id and reason >= 10 non-whitespace chars
    with pytest.raises(ValidationError):
        OptOutEntry(id="DS-0026", reason="too short")

    with pytest.raises(ValidationError):
        OptOutEntry(id="   ", reason="Valid engineering rationale with more than ten chars.")

    valid = OptOutEntry(
        id="DS-0026",
        scope=["Dockerfile*"],
        reason="Batch CLI container exits upon completion; daemon HEALTHCHECK is not applicable.",
    )
    assert valid.id == "DS-0026"

    # Verify `pni init` (init_project) creates .pni/pni.toml alongside workflows
    cli_dir = tmp_path / "cli_init_proj"
    cli_dir.mkdir()
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.chdir(cli_dir)
    try:
        res = runner.invoke(app, ["init", "--lang", "python"])
    finally:
        monkeypatch.undo()
    assert res.exit_code == 0
    assert (cli_dir / ".pni" / "pni.toml").is_file()


def test_scan_gitignore_and_skip_files_exclude_local_env(tmp_path: Path) -> None:
    """Ensure untracked .gitignore'd .env files are excluded from project_inspect and security_scan."""
    (tmp_path / ".gitignore").write_text(".env\n.env.*\nuv.lock\nbuild_cache/\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "demo"\nversion = "0.1.0"\n', encoding="utf-8")
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-test-secret-1234567890\n", encoding="utf-8")
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / ".env.local").write_text("TOKEN=secret\n", encoding="utf-8")
    cache_dir = tmp_path / "build_cache"
    cache_dir.mkdir()
    (cache_dir / "temp.txt").write_text("ignored\n", encoding="utf-8")

    ignored_files, ignored_dirs = discover_gitignored_paths(tmp_path, include_gitignored=("uv.lock",))
    assert ".env" in ignored_files
    assert "sub/.env.local" in ignored_files
    assert "uv.lock" not in ignored_files
    assert "build_cache" in ignored_dirs

    facts = run_project_inspect(tmp_path)
    assert facts.committed_secret_files == []
    assert "uv.lock" in facts.lockfiles_found

    # Trivy report post-filtering also removes skipped/gitignored secret targets
    trivy_fs_json = tmp_path / "trivy-fs.json"
    trivy_fs_json.write_text(
        json.dumps(
            {
                "Results": [
                    {
                        "Target": ".env",
                        "Secrets": [
                            {
                                "RuleID": "generic-api-key",
                                "Category": "General",
                                "Severity": "HIGH",
                                "Title": "Generic API Key",
                                "StartLine": 1,
                                "Match": "OPENAI_API_KEY=sk-test",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    parsed = parse_trivy_reports(trivy_fs_json, skip_files=ignored_files, skip_dirs=ignored_dirs)
    assert parsed.secrets == []


def test_opt_out_filtering_across_project_ast_and_trivy(tmp_path: Path) -> None:
    """Verify [[opt_out]] suppresses targeted findings across project_inspect, ast_analyze, and Trivy."""
    pni_dir = tmp_path / ".pni"
    pni_dir.mkdir()
    (pni_dir / "pni.toml").write_text(
        """
[[opt_out]]
id = "python/lockfile_committed"
reason = "Pure library package intentionally omits lockfile to test newest compatible dependencies in CI."

[[opt_out]]
id = "CWE-94"
scope = ["src/pkg/runner.py"]
reason = "Core Illustration-as-Code execution engine intentionally runs user script via exec()."

[[opt_out]]
id = "ast/private_submodule_import"
scope = ["src/pkg/public_api.py"]
reason = "Public facade module intentionally re-exports internal symbols from private submodule."

[[opt_out]]
id = "DS-0026"
scope = ["Dockerfile*"]
reason = "Batch CLI container exits upon completion; daemon HEALTHCHECK is not applicable."
""",
        encoding="utf-8",
    )

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "pkg"\nversion = "0.1.0"\ndependencies = ["pydantic>=2.0"]\n',
        encoding="utf-8",
    )
    pkg_dir = tmp_path / "src" / "pkg"
    sub_b_dir = pkg_dir / "sub_b"
    sub_b_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (sub_b_dir / "__init__.py").write_text("", encoding="utf-8")
    (sub_b_dir / "_internal.py").write_text("X = 1\n", encoding="utf-8")
    (pkg_dir / "public_api.py").write_text("from pkg.sub_b._internal import X\n", encoding="utf-8")
    (pkg_dir / "runner.py").write_text(
        "def run_script(code: str) -> None:\n    exec(code)\n",
        encoding="utf-8",
    )
    (pkg_dir / "other.py").write_text(
        "def unwaived(code: str) -> None:\n    exec(code)\n",
        encoding="utf-8",
    )

    proj_facts = run_project_inspect(tmp_path, source_dirs=["src"])
    assert not any("Missing lockfile" in d for d in proj_facts.tooling_modernization_issues)
    assert proj_facts.opt_out_counts.get("python/lockfile_committed") == 1

    ast_facts = run_ast_analyze(tmp_path, targets=["src"], lang="python")
    # runner.py exec() is waived by CWE-94 scope=["src/pkg/runner.py"], but other.py exec() remains!
    sink_files = [s.file for s in ast_facts.dangerous_sinks]
    assert "src/pkg/runner.py" not in sink_files
    assert "src/pkg/other.py" in sink_files
    idiom_files = [b.file for b in ast_facts.bug_risk_idioms if "S307" in b.detail or b.symbol == "exec"]
    assert "src/pkg/runner.py" not in idiom_files
    assert "src/pkg/other.py" in idiom_files
    assert ast_facts.opt_out_counts.get("CWE-94") == 1

    # Boundary violation in public_api.py is waived
    assert not any(v.file == "src/pkg/public_api.py" for v in ast_facts.boundary_violations)
    assert ast_facts.opt_out_counts.get("ast/private_submodule_import") == 1

    # Trivy DS-0026 misconfiguration is waived
    cfg = load_pni_config(tmp_path)
    trivy_fs_json = tmp_path / "trivy-misconfig.json"
    trivy_fs_json.write_text(
        json.dumps(
            {
                "Results": [
                    {
                        "Target": "Dockerfile",
                        "Misconfigurations": [
                            {
                                "ID": "DS-0026",
                                "AVDID": "AVD-DS-0026",
                                "Title": "No HEALTHCHECK defined",
                                "Severity": "LOW",
                                "Status": "FAIL",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    parsed = parse_trivy_reports(trivy_fs_json, opt_outs=cfg.opt_out)
    assert parsed.misconfigurations == []
    assert parsed.opt_out_counts.get("DS-0026") == 1


def test_aggregator_and_chapter4_blueprint_render_opt_outs(tmp_path: Path) -> None:
    """Verify compile_workflow_digest populates AppliedOptOut and Chapter 4 renders the waiver table."""
    pni_dir = tmp_path / ".pni"
    pni_dir.mkdir()
    (pni_dir / "pni.toml").write_text(
        """
[[opt_out]]
id = "CWE-94"
scope = ["src/pkg/runner.py"]
reason = "Core Illustration-as-Code execution engine intentionally runs user script via exec()."
""",
        encoding="utf-8",
    )
    cfg = load_pni_config(tmp_path)
    proj_facts = run_project_inspect(tmp_path)
    ast_facts = run_ast_analyze(tmp_path, targets=["."], lang="python")
    ast_facts.opt_out_counts["CWE-94"] = 1

    bundle = WorkflowFactsBundle(
        workflow_id="full_audit",
        targets=WorkflowTargets(),
        outputs=WorkflowOutputs(),
        project_facts=proj_facts,
        ast_facts=ast_facts,
    )
    ai_input = InterpretationInput(
        summary="Security check with waived runner exec.",
        step_score=95,
        rule_checks=[
            RuleCheckResult(
                rule_id="CWE-94",
                status="fail",
                evidence="src/pkg/runner.py uses exec()",
            )
        ],
        findings=[
            Finding(
                severity="high",
                category="security",
                rule_id="CWE-94",
                file_path="src/pkg/runner.py",
                line=12,
                description="exec() in runner.py",
                recommendation="Avoid exec()",
            )
        ],
    )
    act_record = ActionRunRecord(
        action_id="step-1",
        run_id="run_test",
        seq=1,
        name="Security Audit",
        primitive_type=PrimitiveType.AI_INTERPRET,
        status=RunStatus.COMPLETED,
        agent_input_json=ai_input.model_dump_json(),
    )

    digest = compile_workflow_digest([act_record], bundle, opt_outs=cfg.opt_out)
    assert digest.findings == []
    assert len(digest.opt_outs) == 1
    assert digest.opt_outs[0].id == "CWE-94"
    assert digest.opt_outs[0].matched_count == 1

    score = ScoreResult(
        project_name="pkg",
        workflow_id="full_audit",
        language="python",
        overall_score=95,
        grade="S",
        category_scores=CategoryScores(
            architecture=95,
            code_quality=95,
            typing=95,
            testing=95,
            dependencies=95,
            documentation=95,
            security=95,
        ),
        summary="Excellent package.",
        opt_outs=digest.opt_outs,
    )
    blueprint = build_report_blueprint(score, target="pkg", lang="en")
    ch4 = next(ch for ch in blueprint.chapters if ch.filename == "04_standards_and_findings.md")
    ch4_text = "\n".join(ch4.sorted_data_markdown)
    assert "Configured Scope & Accepted Design Waivers" in ch4_text
    assert "`CWE-94`" in ch4_text
    assert "src/pkg/runner.py" in ch4_text


def test_report_html_output_dir_print_css_and_workflow_precedence(tmp_path: Path) -> None:
    """Verify @media print table CSS, html_output_dir routing, and pni.toml workflow precedence."""
    pni_dir = tmp_path / ".pni"
    pni_dir.mkdir()
    (pni_dir / "pni.toml").write_text(
        """
[targets]
exclude = ["reports/**", "reports_src/**"]

[report]
src_dir = "custom_reports_src"
output_dir = "custom_reports"
html_output_dir = "docs/published_audit"
formats = ["pdf", "html"]
lang = "ja"
style = "claude"
""",
        encoding="utf-8",
    )

    # 1. Verify workflow step normalization applies [report] & [targets] defaults over composite defaults
    wf = WorkflowDefinition(
        id="full_audit",
        name="Full Audit",
        steps=[
            WorkflowStepSpec(id="audit", uses="python_ast_audit"),
            WorkflowStepSpec(id="report", uses="write_drawlib_report", with_params={"style": "openai"}),
        ],
    )
    normalized = normalize_workflow_steps(wf, tmp_path, lang="python")
    report_step = next(s for s in normalized if s.type == PrimitiveType.WRITE_DRAWLIB_REPORT)
    assert report_step.params["src_dir"] == "custom_reports_src"
    assert report_step.params["output_dir"] == "custom_reports"
    assert report_step.params["html_output_dir"] == "docs/published_audit"
    assert report_step.params["formats"] == ["pdf", "html"]
    assert report_step.params["lang"] == "ja"
    # Explicit step `with:` overrides pni.toml (`openai` > `claude`)
    assert report_step.params["style"] == "openai"

    # 2. Verify scaffold_report_project appends @media print wide-table rules to style.css
    src_base = tmp_path / "reports_src"
    out_dir = tmp_path / "reports"
    html_dir = tmp_path / "docs" / "reports" / "pni-audit"
    scaffold = scaffold_report_project(
        "demo",
        src_base_dir=src_base,
        lang="en",
        style="google",
        clean_sample_chapters=False,
        force=True,
    )
    style_css = (scaffold.src_dir / "style.css").read_text(encoding="utf-8")
    assert "@media print" in style_css
    assert "overflow-wrap: anywhere" in style_css

    # 3. Verify compile_report_project routes HTML directly into html_output_dir
    built = compile_report_project(
        "demo",
        src_base_dir=src_base,
        output_dir=out_dir,
        html_output_dir=html_dir,
        formats=("html",),
        no_cache=True,
    )
    assert built.html_dir == html_dir.resolve()
    assert built.html_index == (html_dir / "index.html").resolve()
    assert (html_dir / "index.html").is_file()
    assert not (out_dir / "demo_html").exists()


def test_match_opt_out_alias_resolution() -> None:
    """Ensure CWE-94 <-> S307 and DS-0026 <-> AVD-DS-0026 aliases match bidirectionally."""
    waivers = [
        OptOutEntry(
            id="CWE-94",
            scope=["src/drawlib/**"],
            reason="Illustration-as-Code intentionally executes user Python diagram scripts.",
        ),
        OptOutEntry(
            id="DS-0026",
            scope=["Dockerfile*"],
            reason="Batch container exits after CLI run; HEALTHCHECK is not applicable.",
        ),
    ]
    assert match_opt_out(waivers, "S307", "src/drawlib/runner.py") is not None
    assert match_opt_out(waivers, "S307", "src/other/runner.py") is None
    assert match_opt_out(waivers, "AVD-DS-0026", "Dockerfile.prod") is not None
