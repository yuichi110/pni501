"""Unit tests for all 35-language Docker execution harnesses, selectors, smoke plans, and parsers."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from pni._actions import ProjectFacts, RuntimeCheckOptions, run_runtime_check
from pni._actions.ast_analyze._cst import parse_cst
from pni._actions.runtime_check.engine_detect import CommandExecResult
from pni._actions.runtime_check.polyglot import (
    EXTENDED_HARNESS_SPECS,
    select_dart_image_version,
    select_dotnet_image_version,
    select_elixir_image_version,
    select_julia_image_version,
    select_perl_image_version,
    select_r_image_version,
    select_ruby_image_version,
    select_rust_image_version,
    select_swift_image_version,
)
from pni._actions.runtime_check.polyglot_parsers import (
    parse_cobertura_xml,
    parse_dart_test_output,
    parse_dotnet_test_output,
    parse_dotnet_trx_xml,
    parse_elixir_test_output,
    parse_generic_test_output,
    parse_polyglot_coverage,
    parse_polyglot_test_results,
    parse_r_test_output,
    parse_ruby_test_output,
    parse_rust_test_output,
    parse_scala_test_output,
    parse_swift_test_output,
    parse_tap_output,
)
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_harness_tool,
)
from pni._actions.runtime_check.smoke import build_smoke_plan, classify_boot_failure
from pni._dockerfiles import (
    BUILTIN_DOCKERFILES_DIR,
    has_builtin_dockerfile,
    list_builtin_dockerfiles,
    resolve_template_dockerfile,
)
from pni._languages import LANGUAGE_REGISTRY

EXPECTED_35_HARNESS_LANGS = {
    # Core 6
    "python",
    "java",
    "php",
    "go",
    "typescript",
    "javascript",
    # Tier A additions (14 -> 20/20 Tier A)
    "rust",
    "csharp",
    "ruby",
    "kotlin",
    "swift",
    "c",
    "cpp",
    "scala",
    "dart",
    "elixir",
    "vue",
    "perl",
    "r",
    "cobol",
    # Tier B Linux-native additions (15)
    "bash",
    "powershell",
    "groovy",
    "lua",
    "haskell",
    "fsharp",
    "ocaml",
    "zig",
    "julia",
    "fortran",
    "svelte",
    "ada",
    "commonlisp",
    "verilog",
    "vhdl",
}


def test_registry_and_builtin_dockerfiles_in_sync(tmp_path: Path) -> None:
    """Every language's LanguageSpec.has_runtime_harness matches built-in Dockerfiles 1:1."""
    registry_harness_langs = {lid for lid, spec in LANGUAGE_REGISTRY.items() if spec.has_runtime_harness}
    assert registry_harness_langs == EXPECTED_35_HARNESS_LANGS
    assert len(EXTENDED_HARNESS_SPECS) == 29

    for lid, spec in LANGUAGE_REGISTRY.items():
        assert has_builtin_dockerfile(lid) is spec.has_runtime_harness, f"Mismatch for {lid}"

    templates = list_builtin_dockerfiles()
    assert len(templates) == 40
    for rel_tpl in templates:
        df_path = BUILTIN_DOCKERFILES_DIR / rel_tpl
        assert df_path.is_file()
        text = df_path.read_text(encoding="utf-8")
        root = parse_cst(text, "dockerfile")
        assert not root.has(kind="ERROR"), f"Tree-sitter parse error in {rel_tpl}"
        assert "\nUSER " in text, f"Missing non-root USER in {rel_tpl}"
        assert "/out" in text, f"Missing /out mount dir in {rel_tpl}"

    # Verify every harness language resolves cleanly through select_harness_tool + resolve_template_dockerfile
    for lang in sorted(EXPECTED_35_HARNESS_LANGS):
        pf = ProjectFacts(project_name=f"demo-{lang}", language=lang, runtime_types=["library"])
        tool = select_harness_tool(pf)
        tpl_path, tpl_id = resolve_template_dockerfile(tmp_path, lang, tool)
        assert tpl_path.is_file()
        assert tpl_id.startswith(f"{lang}/")
        build_args = compute_harness_build_args(pf, extra_apt_packages="curl", harness_dockerfile=tpl_path)
        assert isinstance(build_args, dict)
        cmd = build_test_and_coverage_command(pf, tool, ["src"], ["tests"])
        assert len(cmd) >= 2
        arch, smoke_cmd = build_smoke_plan(tmp_path, pf, ["src"])
        assert arch == "library"
        if lang not in {"python", "php", "go", "typescript", "javascript"}:
            assert smoke_cmd is not None


def test_extended_version_selectors_and_kotlin_tool_selection(tmp_path: Path) -> None:
    """Verify image tag selectors and Kotlin Maven vs Gradle selection."""
    assert select_rust_image_version(None) == "1.85"
    assert select_rust_image_version("1.86.0") == "1.86"
    assert select_dotnet_image_version("net8.0") == "8.0"
    assert select_dotnet_image_version("net9.0") == "9.0"
    assert select_ruby_image_version("3.2.2") == "3.2"
    assert select_ruby_image_version("3.3.0") == "3.3"
    assert select_ruby_image_version("3.4.1") == "3.4"
    assert select_swift_image_version("5.10") == "5.10"
    assert select_swift_image_version("6.0") == "6.0"
    assert select_elixir_image_version("~> 1.16") == "1.17"
    assert select_elixir_image_version("~> 1.18") == "1.18"
    assert select_perl_image_version("5.38") == "5.38"
    assert select_perl_image_version("5.40") == "5.40"
    assert select_r_image_version("4.4.0") == "4.4.2"
    assert select_dart_image_version(">=3.4.0") == "stable"
    assert select_julia_image_version("1.10") == "1.10"
    assert select_julia_image_version("1.11") == "1.11"

    kt_gradle = ProjectFacts(project_name="kt", language="kotlin", manifest_files=["build.gradle.kts"])
    assert select_harness_tool(kt_gradle) == "gradle"
    kt_maven = ProjectFacts(project_name="kt", language="kotlin", manifest_files=["pom.xml"])
    assert select_harness_tool(kt_maven) == "maven"
    _, kt_mvn_tpl = resolve_template_dockerfile(tmp_path, "kotlin", "maven")
    assert kt_mvn_tpl == "kotlin/maven.dockerfile"

    # Extended boot failure classifications
    assert classify_boot_failure("error[E0432]: unresolved import `foo::bar`", timed_out=False) == "import_or_di_error"
    assert classify_boot_failure("error CS0246: The type or namespace name could not be found", timed_out=False) == (
        "import_or_di_error"
    )
    assert classify_boot_failure("LoadError: cannot load such file -- rack", timed_out=False) == "import_or_di_error"


def test_polyglot_test_and_coverage_parsers(tmp_path: Path) -> None:
    """Verify deterministic parsing across all extended polyglot test and coverage formats."""
    # Rust cargo test (multiple test binaries)
    rs_out = tmp_path / "rust_test.txt"
    rs_out.write_text(
        "running 3 tests\n"
        "test orders::test_ok ... ok\n"
        "test orders::test_bad ... FAILED\n"
        "test orders::test_skip ... ignored\n"
        "test result: FAILED. 1 passed; 1 failed; 1 ignored; 0 measured; 0 filtered out\n"
        "test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out\n",
        encoding="utf-8",
    )
    tot, pas, fal, err, skp, fails = parse_rust_test_output(rs_out)
    assert (tot, pas, fal, err, skp) == (5, 3, 1, 0, 1)
    assert len(fails) == 1 and fails[0].name == "orders::test_bad"

    # .NET TRX XML + XXE rejection + console fallback
    trx = tmp_path / "results.trx"
    trx.write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<TestRun xmlns="http://microsoft.com/schemas/VisualStudio/TeamTest/2010">'
        "<Results>"
        '<UnitTestResult testName="TestPass" outcome="Passed" />'
        '<UnitTestResult testName="TestSkip" outcome="NotExecuted" />'
        '<UnitTestResult testName="TestFail" outcome="Failed">'
        "<Output><ErrorInfo><Message>Expected true</Message></ErrorInfo></Output>"
        "</UnitTestResult>"
        "</Results></TestRun>",
        encoding="utf-8",
    )
    assert parse_dotnet_trx_xml(trx)[:5] == (3, 1, 1, 0, 1)
    assert parse_dotnet_trx_xml(trx)[5][0].message == "Expected true"

    xxe_trx = tmp_path / "xxe.trx"
    xxe_trx.write_text('<!DOCTYPE foo [<!ENTITY xxe "evil">]><TestRun/>', encoding="utf-8")
    assert parse_dotnet_trx_xml(xxe_trx)[:5] == (0, 0, 0, 0, 0)

    dn_txt = tmp_path / "dotnet_test.txt"
    dn_txt.write_text("Failed!  - Failed:     1, Passed:     4, Skipped:     1, Total:     6\n", encoding="utf-8")
    assert parse_dotnet_test_output(dn_txt)[:5] == (6, 4, 1, 0, 1)

    # Cobertura XML
    cob_xml = tmp_path / "cobertura.xml"
    cob_xml.write_text(
        '<coverage lines-valid="4" lines-covered="3">'
        "<packages><package><classes>"
        '<class name="OrderService" filename="/workspace/src/OrderService.cs">'
        "<lines>"
        '<line number="10" hits="2" branch="true" condition-coverage="50% (1/2)"/>'
        '<line number="11" hits="1" branch="false"/>'
        '<line number="12" hits="0" branch="false"/>'
        '<line number="13" hits="1" branch="false"/>'
        "</lines></class></classes></package></packages></coverage>",
        encoding="utf-8",
    )
    cov = parse_cobertura_xml(cob_xml)
    assert cov.measured is True and cov.tool == "cobertura"
    assert cov.line_coverage_pct == 75.0
    assert cov.branch_coverage_pct == 50.0
    assert cov.lowest_covered_modules[0].file_path == "src/OrderService.cs"
    assert cov.lowest_covered_modules[0].missing_lines_preview == [12]

    # Ruby RSpec & Minitest
    rspec = tmp_path / "rspec.txt"
    rspec.write_text("5 examples, 1 failure, 1 pending\nrspec ./spec/orders_spec.rb:12\n", encoding="utf-8")
    assert parse_ruby_test_output(rspec)[:5] == (5, 3, 1, 0, 1)
    mini = tmp_path / "minitest.txt"
    mini.write_text("4 runs, 8 assertions, 0 failures, 0 errors, 1 skips\n", encoding="utf-8")
    assert parse_ruby_test_output(mini)[:5] == (4, 3, 0, 0, 1)

    # Swift XCTest & Swift Testing
    sw_xc = tmp_path / "swift_xc.txt"
    sw_xc.write_text(
        "Test Case 'OrderTests.testBad' failed (0.01 seconds).\n"
        "Executed 3 tests, with 1 failure (0 unexpected) in 0.02 seconds\n",
        encoding="utf-8",
    )
    assert parse_swift_test_output(sw_xc)[:5] == (3, 2, 1, 0, 0)
    sw_st = tmp_path / "swift_st.txt"
    sw_st.write_text("Test run with 4 tests passed after 0.01 seconds.\n", encoding="utf-8")
    assert parse_swift_test_output(sw_st)[:5] == (4, 4, 0, 0, 0)

    # Elixir ExUnit
    ex_out = tmp_path / "elixir_test.txt"
    ex_out.write_text("1) test fails (OrdersTest)\n6 tests, 1 failure, 1 skipped\n", encoding="utf-8")
    assert parse_elixir_test_output(ex_out)[:5] == (6, 4, 1, 0, 1)

    # Dart test
    dart_out = tmp_path / "dart_test.txt"
    dart_out.write_text("00:01 +4 ~1 -1: Some tests failed.\n", encoding="utf-8")
    assert parse_dart_test_output(dart_out)[:5] == (6, 4, 1, 0, 1)

    # TAP (Perl prove / Bash bats / C / COBOL / etc.)
    tap_out = tmp_path / "tap_test.txt"
    tap_out.write_text(
        "ok 1 - orders compute\n"
        "not ok 2 - billing fail\n"
        "ok 3 - legacy # skip not supported\n"
        "1..3\n",
        encoding="utf-8",
    )
    assert parse_tap_output(tap_out)[:5] == (3, 1, 1, 0, 1)
    assert parse_tap_output(tap_out)[5][0].name == "billing fail"

    # R testthat
    r_out = tmp_path / "r_test.txt"
    r_out.write_text("[ FAIL 1 | WARN 0 | SKIP 2 | PASS 7 ]\n", encoding="utf-8")
    assert parse_r_test_output(r_out)[:5] == (10, 7, 1, 0, 2)

    # Scala sbt & ScalaTest
    sc_out = tmp_path / "scala_test.txt"
    sc_out.write_text("[info] Passed: Total 5, Failed 1, Errors 0, Passed 4, Ignored 0\n", encoding="utf-8")
    assert parse_scala_test_output(sc_out)[:5] == (5, 4, 1, 0, 0)

    # Generic fallback + polyglot dispatchers
    gen_out = tmp_path / "generic_test.txt"
    gen_out.write_text("Summary: 8 passed, 0 failed\n", encoding="utf-8")
    assert parse_generic_test_output(gen_out)[:5] == (8, 8, 0, 0, 0)
    assert parse_polyglot_test_results("rust", tmp_path)[:5] == (5, 3, 1, 0, 1)
    assert parse_polyglot_test_results("csharp", tmp_path)[:5] == (3, 1, 1, 0, 1)
    assert parse_polyglot_coverage("csharp", ["src"], tmp_path).tool == "cobertura"


def test_runner_polyglot_end_to_end_and_non_harness_skip(tmp_path: Path) -> None:
    """Verify mocked Stage 0-4 pass for Rust and clean skipped status for non-harness languages like HCL."""
    # 1. Non-harness language (HCL) skips cleanly without raising FileNotFoundError
    hcl_dir = tmp_path / "infra"
    hcl_dir.mkdir()
    (hcl_dir / "main.tf").write_text('resource "null_resource" "a" {}\n', encoding="utf-8")
    hcl_res = run_runtime_check(
        tmp_path,
        "wf_hcl",
        target_root="infra",
        source_targets=["."],
        test_targets=[],
        lang="hcl",
    )
    assert hcl_res.status == "skipped"
    assert "No built-in container harness" in hcl_res.skip_reason

    # 2. Mocked Rust full Stage 0-4 pass
    rs_dir = tmp_path / "rust_app"
    (rs_dir / "src").mkdir(parents=True)
    (rs_dir / "Cargo.toml").write_text(
        '[package]\nname = "demo"\nversion = "0.1.0"\nedition = "2021"\n',
        encoding="utf-8",
    )
    (rs_dir / "src" / "lib.rs").write_text("pub fn add(a: i32, b: i32) -> i32 { a + b }\n", encoding="utf-8")

    def fake_run(
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
        if "cargo test" in joined:
            (out_dir / "rust_test.txt").write_text(
                "test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out\n",
                encoding="utf-8",
            )
        else:
            (out_dir / "smoke.json").write_text(json.dumps({"detail": "cargo check ok"}), encoding="utf-8")
        return CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.1, stdout="ok", stderr="")

    with (
        patch(
            "pni._actions.runtime_check.runner.detect_container_engine",
            return_value=("docker", "/usr/bin/docker", "ok"),
        ),
        patch(
            "pni._actions.runtime_check.runner.build_container_image",
            return_value=CommandExecResult(exit_code=0, timed_out=False, duration_sec=0.3, stdout="ok", stderr=""),
        ),
        patch("pni._actions.runtime_check.runner.run_container_command", side_effect=fake_run),
        patch("pni._actions.runtime_check.runner.remove_container_images"),
    ):
        rs_res = run_runtime_check(
            tmp_path,
            "wf_rust",
            target_root="rust_app",
            source_targets=["src"],
            test_targets=["tests"],
            lang="rust",
            options=RuntimeCheckOptions(),
        )
        assert rs_res.status == "passed"
        assert rs_res.selected_dockerfile_template == "rust/cargo.dockerfile"
        assert rs_res.test_execution.passed_tests == 3
        assert rs_res.smoke_check.status == "passed"
