# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for Plan 1 diagnostic accuracy and report refinement workstreams (WS1..WS5)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pni._actions import (
    CategoryScores,
    CodeLocation,
    ContainerBuildResult,
    Finding,
    RuntimeFacts,
    ScoreResult,
    SecurityFacts,
    VulnerabilityItem,
    extract_verbatim_error_excerpt,
    run_ast_analyze,
)
from pni._actions.ast_analyze.version_compat import (
    parse_java_target_major,
    parse_min_language_version,
)
from pni._actions.security_scan import (
    UNPINNED_RESOLUTION_NOTE,
    is_symbolic_or_unpinned_version,
    parse_trivy_reports,
)
from pni._reporter import compile_report_project, lint_drawlib_chapters
from pni._reporter.blueprint import build_report_blueprint
from pni._reporter.drawlib_guide import render_drawlib_report_guide
from pni._workflows.aggregator import consolidate_findings_by_location


def test_ws1_is_symbolic_or_unpinned_version() -> None:
    """Verify symbolic/wildcard/snapshot specifiers are flagged while concrete versions are not."""
    for symbolic in ("LATEST", "RELEASE", "*", "dev-main", "1.0.0-SNAPSHOT", "main", "HEAD", "^2.4", ">=1.0"):
        assert is_symbolic_or_unpinned_version(symbolic) is True, f"Expected {symbolic!r} to be flagged"

    for concrete in ("2.7.0", "5.3.18.RELEASE", "4.2.0-RC1", "1.2.3.Final", "3.11.4"):
        assert is_symbolic_or_unpinned_version(concrete) is False, f"Expected {concrete!r} to be concrete"


def test_ws1_parse_trivy_reports_attaches_unpinned_metadata(tmp_path: Path) -> None:
    """Verify parse_trivy_reports stamps is_unpinned_specifier and version_resolution_note on LATEST."""
    fs_json = tmp_path / "trivy_fs.json"
    fs_payload = {
        "Results": [
            {
                "Target": "pom.xml",
                "Class": "lang-pkgs",
                "Type": "pom",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2022-22965",
                        "PkgName": "org.springframework.boot:spring-boot-starter-web",
                        "InstalledVersion": "LATEST",
                        "FixedVersion": "2.6.6, 2.5.12",
                        "Severity": "CRITICAL",
                        "Title": "Spring4Shell RCE via DataBinder",
                    },
                    {
                        "VulnerabilityID": "CVE-2020-11022",
                        "PkgName": "jquery",
                        "InstalledVersion": "3.4.1",
                        "FixedVersion": "3.5.0",
                        "Severity": "MEDIUM",
                        "Title": "jQuery XSS",
                    },
                ],
            }
        ]
    }
    fs_json.write_text(json.dumps(fs_payload), encoding="utf-8")

    bundle = parse_trivy_reports(fs_json_path=fs_json)
    assert len(bundle.vulnerabilities) == 2

    spring_vuln = bundle.vulnerabilities[0]
    assert spring_vuln.vuln_id == "CVE-2022-22965"
    assert spring_vuln.is_unpinned_specifier is True
    assert spring_vuln.version_resolution_note == UNPINNED_RESOLUTION_NOTE

    jquery_vuln = bundle.vulnerabilities[1]
    assert jquery_vuln.is_unpinned_specifier is False
    assert jquery_vuln.version_resolution_note == ""


def test_ws2_version_parsers_and_ast_compatibility(tmp_path: Path) -> None:
    """Verify Java, PHP, and Python version-compatibility AST checks catch newer syntax/APIs."""
    assert parse_java_target_major("1.8") == 8
    assert parse_java_target_major("17 (source=17, target=17)") == 17
    assert parse_min_language_version("^7.4") == (7, 4)
    assert parse_min_language_version(">=3.9,<3.13") == (3, 9)

    # PHP 7.4 using PHP 8.0+ match & attribute and PHP 8.1+ enum
    php_dir = tmp_path / "php_app"
    php_dir.mkdir()
    php_file = php_dir / "OrderStatus.php"
    php_file.write_text(
        "<?php\n"
        "enum OrderStatus: string { case Pending = 'pending'; }\n"
        "class OrderHelper {\n"
        "    #[Deprecated]\n"
        "    public function label(string $code): string {\n"
        "        return match ($code) { 'p' => 'Pending', default => 'Other' };\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    php_facts = run_ast_analyze(php_dir, lang="php", declared_lang_version="^7.4")
    php_details = "\n".join(m.detail for m in php_facts.language_version_mismatches)
    assert "PHP 8.1+ 'enum'" in php_details
    assert "PHP 8.0+ '#[Attribute]'" in php_details
    assert "PHP 8.0+ 'match'" in php_details

    # Python >=3.9 using Python 3.10 match/case and Python 3.11 tomllib
    py_dir = tmp_path / "py_app"
    py_dir.mkdir()
    py_file = py_dir / "config_loader.py"
    py_file.write_text(
        "import tomllib\n\n"
        "def parse_mode(mode: str) -> int:\n"
        "    match mode:\n"
        "        case 'fast':\n"
        "            return 1\n"
        "        case _:\n"
        "            return 0\n",
        encoding="utf-8",
    )
    py_facts = run_ast_analyze(py_dir, lang="python", declared_lang_version=">=3.9")
    py_details = "\n".join(m.detail for m in py_facts.language_version_mismatches)
    assert "Python 3.10+ 'match/case'" in py_details
    assert "Python 3.11+ stdlib 'tomllib'" in py_details


def test_ws2_java_spring_messy_ast_catches_http_client_and_undeclared_transactional() -> None:
    """Verify run_ast_analyze on examples/java/api_spring_messy catches Java 11 HttpClient and missing spring-tx."""
    repo_root = Path(__file__).resolve().parents[2]
    target = repo_root / "examples" / "java" / "api_spring_messy"

    facts = run_ast_analyze(target, lang="java", declared_lang_version="1.8 (source=1.8, target=1.8)")

    mismatch_pairs = [(m.file, m.detail) for m in facts.language_version_mismatches]
    assert any("GatewayClient.java" in file_path and "java.net.http" in detail for file_path, detail in mismatch_pairs)

    undeclared = "\n".join(str(u) for u in facts.undeclared_dependencies)
    assert "org.springframework.transaction.annotation.Transactional" in undeclared


def test_ws2_extract_verbatim_error_excerpt_prioritizes_compiler_diagnostics() -> None:
    """Verify extract_verbatim_error_excerpt extracts javac class version errors ahead of BuildKit noise."""
    buildkit_tail = [
        "#8 12.49 [ERROR] COMPILATION ERROR : ",
        "#8 12.49 [INFO] -------------------------------------------------------------",
        "#8 12.49 [ERROR] /app/src/BillingController.java:[9,32] cannot access SpringApplication",
        "  bad class file: /root/.m2/spring-boot-4.2.0-RC1.jar(/SpringApplication.class)",
        "    class file has wrong version 61.0, should be 52.0",
        "#8 12.50 [ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException",
        "------",
        "Dockerfile:16",
        "--------------------",
        "  15 |     COPY src ./src",
        "  16 | >>> RUN mvn -B package -DskipTests",
        "--------------------",
        "ERROR: failed to build: failed to solve: process '/bin/sh -c mvn -B package' did not complete",
    ]
    excerpt = extract_verbatim_error_excerpt(buildkit_tail, max_lines=5)
    joined = "\n".join(excerpt)
    assert "bad class file" in joined
    assert "wrong version 61.0, should be 52.0" in joined
    assert "cwiki.apache.org" not in joined


def test_ws3_consolidate_findings_by_location_and_blueprint_rendering() -> None:
    """Verify Dockerfile:1 findings collapse into 1 ConsolidatedFinding while keeping ScoreResult.findings."""
    raw_findings = [
        Finding(
            severity="critical",
            category="security",
            rule_id="common/security/SEC-03",
            file_path="Dockerfile",
            line=1,
            description="Container runs as root without USER directive.",
            recommendation="Add non-root USER.",
        ),
        Finding(
            severity="high",
            category="security",
            rule_id="common/supply_chain/SC-02",
            file_path="Dockerfile",
            line=1,
            description="Unpinned maven:3.8-jdk-8 base image tag without sha256 digest.",
            recommendation="Pin sha256 digest and migrate to Eclipse Temurin 21 JRE.",
        ),
        Finding(
            severity="medium",
            category="ops",
            rule_id="common/production_readiness/OPS-02",
            file_path="Dockerfile",
            line=1,
            description="Single-stage Maven image ships JDK + source in runtime container.",
            recommendation="Split into multi-stage builder and slim JRE runtime.",
        ),
    ]
    consolidated = consolidate_findings_by_location(raw_findings)
    assert len(consolidated) == 1
    row = consolidated[0]
    assert row.file_path == "Dockerfile"
    assert row.line == 1
    assert row.severity == "critical"
    assert row.rule_ids == [
        "common/security/SEC-03",
        "common/supply_chain/SC-02",
        "common/production_readiness/OPS-02",
    ]
    assert "Container runs as root" in row.combined_evidence

    score = ScoreResult(
        project_name="api_spring_messy",
        workflow_id="java_api_spring_messy",
        language="java",
        target_root="examples/java/api_spring_messy",
        overall_score=31,
        grade="D",
        category_scores=CategoryScores(
            architecture=34,
            code_quality=28,
            typing=54,
            testing=15,
            dependencies=20,
            security=22,
            documentation=38,
        ),
        findings=raw_findings,
        consolidated_findings=consolidated,
        language_version_mismatches=[
            CodeLocation(
                file="src/main/java/com/acme/messy/service/GatewayClient.java",
                line=5,
                symbol="java.net.http.HttpClient",
                detail="Java 11+ 'java.net.http' API imported while declared target is Java 1.8",
            )
        ],
        runtime_facts=RuntimeFacts(
            status="failed",
            container_engine="docker",
            harness_build=ContainerBuildResult(
                attempted=True,
                status="failed",
                error_tail=[
                    "bad class file: spring-boot-4.2.0-RC1.jar",
                    "class file has wrong version 61.0, should be 52.0",
                ],
            ),
        ),
        security_facts=SecurityFacts(
            status="failed",
            scanned_filesystem=True,
            vulnerabilities=[
                VulnerabilityItem(
                    vuln_id="CVE-2022-22965",
                    pkg_name="org.springframework.boot:spring-boot-starter-web",
                    pkg_type="pom",
                    installed_version="LATEST",
                    fixed_version="2.6.6",
                    severity="CRITICAL",
                    target="pom.xml",
                    is_unpinned_specifier=True,
                    version_resolution_note=UNPINNED_RESOLUTION_NOTE,
                )
            ],
        ),
        summary="Diagnostic test summary",
    )
    assert len(score.findings) == 3
    assert len(score.consolidated_findings) == 1

    blueprint = build_report_blueprint(score, target="java/api_spring_messy")
    ch4 = next(ch for ch in blueprint.chapters if ch.filename.startswith("04_"))
    ch5 = next(ch for ch in blueprint.chapters if ch.filename.startswith("05_"))
    ch6 = next(ch for ch in blueprint.chapters if ch.filename.startswith("06_"))

    ch4_md = "\n".join(ch4.sorted_data_markdown)
    ch5_md = "\n".join(ch5.sorted_data_markdown)
    ch6_md = "\n".join(ch6.sorted_data_markdown)

    assert "common/security/SEC-03, common/supply_chain/SC-02" in ch4_md
    assert "AST Declared Language-Version API / Syntax Mismatches" in ch5_md
    assert "Harness Build / Compiler Verbatim Failure Excerpt" in ch5_md
    assert "UNPINNED SPECIFIER RANGE MATCH" in ch6_md


def test_ws5_lint_drawlib_chapters_and_strict_preflight(tmp_path: Path) -> None:
    """Verify lint_drawlib_chapters catches missing multi-series legends and contour-line collisions."""
    src_dir = tmp_path / "reports_src" / "demo_src"
    en_dir = src_dir / "en"
    en_dir.mkdir(parents=True)
    (src_dir / "drawlib.toml").write_text(
        '[project]\ntype = "doc"\n\n[i18n]\ndefault_lang = "en"\nlangs = ["en"]\n',
        encoding="utf-8",
    )
    out_dir = tmp_path / "reports"

    bad_ch2 = en_dir / "02_architecture.md"
    bad_ch2.write_text(
        "# 2. Architecture\n\n"
        '```drawlib file=arch.png caption="Arch"\n'
        "diag = ClassDiagram(x=6, y=8, width=134, height=64)\n"
        "hm = HeatmapOverlay(x=6, y=8, width=134, height=64, show_contour_lines=True)\n"
        "```\n",
        encoding="utf-8",
    )
    bad_ch6 = en_dir / "06_security.md"
    bad_ch6.write_text(
        "# 6. Security\n\n"
        '```drawlib file=sec.png caption="Sec"\n'
        "chart = BarChart(xy=(12, 10), width=124, height=44)\n"
        "chart.add_series('Critical', [1, 0])\n"
        "chart.add_series('High', [2, 1])\n"
        "chart.draw()\n"
        "```\n",
        encoding="utf-8",
    )

    warnings = lint_drawlib_chapters([bad_ch2, bad_ch6])
    assert len(warnings) == 2
    assert any("show_contour_lines=False" in w for w in warnings)
    assert any("chart.draw_legend" in w for w in warnings)

    with pytest.raises(ValueError, match="Drawlib preflight visual check failed"):
        compile_report_project("demo", src_base_dir=tmp_path / "reports_src", output_dir=out_dir, strict_preflight=True)

    # Fix both issues and verify zero warnings + clean compile_report_project with mocked drawlib.tools
    bad_ch2.write_text(
        "# 2. Architecture\n\n"
        '```drawlib file=arch.png caption="Arch"\n'
        "diag = ClassDiagram(x=6, y=8, width=134, height=82)\n"
        "hm = HeatmapOverlay(x=6, y=8, width=134, height=82, show_contour_lines=False)\n"
        "```\n",
        encoding="utf-8",
    )
    fake_tok = "-".join(("xoxb", "123456789012", "ABCDEFGHIJKLMN"))
    bad_ch6.write_text(
        "# 6. Security\n\n"
        f"Example Slack token: `{fake_tok}`\n\n"
        '```drawlib file=sec.png caption="Sec"\n'
        "chart = BarChart(xy=(12, 10), width=124, height=44)\n"
        "chart.add_series('Critical', [1, 0])\n"
        "chart.add_series('High', [2, 1])\n"
        "chart.draw()\n"
        "chart.draw_legend(xy=(14, 56), orientation='horizontal')\n"
        "```\n",
        encoding="utf-8",
    )
    token_warnings = lint_drawlib_chapters([bad_ch2, bad_ch6])
    assert len(token_warnings) == 1
    assert "GitHub Push Protection" in token_warnings[0]

    bad_ch6.write_text(
        bad_ch6.read_text(encoding="utf-8").replace(fake_tok, "<REDACTED_SLACK_TOKEN>"),
        encoding="utf-8",
    )
    assert lint_drawlib_chapters([bad_ch2, bad_ch6]) == []

    fake_tools = MagicMock()
    with patch("pni._reporter.compiler._get_drawlib_tools", return_value=fake_tools):
        res = compile_report_project(
            "demo",
            src_base_dir=tmp_path / "reports_src",
            output_dir=out_dir,
            strict_preflight=True,
        )
    assert res.preflight_warnings == []
    assert (src_dir / "_assets" / "ogp.png").is_file()

    guide = render_drawlib_report_guide(
        target="demo",
        score_path="reports/demo_score.json",
        facts_path=".pni/cache/demo/facts.json",
        target_root="examples/demo",
        source_targets=["src"],
        doc_targets=["README.md"],
    )
    assert "chart.draw_legend" in guide
    assert "show_contour_lines=False" in guide

