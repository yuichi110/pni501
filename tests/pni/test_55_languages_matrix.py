# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""End-to-end 55-language Tree-sitter matrix, defect detection, manifest, and companion scanner tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from pni._actions import copy_action_templates, run_project_inspect
from pni._actions.ast_analyze import (
    DEFAULT_COMPANION_LANGUAGES,
    SUITE_REGISTRY,
    _cst,
    parse_cst,
    run_ast_analyze,
    scan_companion_languages,
)
from pni._languages import (
    GRAMMAR_PROVIDERS,
    get_language_spec,
    list_supported_languages,
    resolve_language_id,
)
from pni._rules import copy_rule_templates, detect_active_language, list_rules
from pni._workflows import copy_workflow_templates

CLEAN_FIXTURES: dict[str, tuple[str, str]] = {
    # Core 6
    "python": ("app.py", 'def add(a: int, b: int) -> int:\n    """Add."""\n    return a + b\n'),
    "java": ("App.java", "public class App { public int add(int a, int b) { return a + b; } }\n"),
    "php": ("app.php", "<?php\nfunction add(int $a, int $b): int { return $a + $b; }\n"),
    "go": ("app.go", "package app\nfunc Add(a int, b int) int { return a + b }\n"),
    "typescript": ("app.ts", "export function add(a: number, b: number): number { return a + b; }\n"),
    "javascript": ("app.js", "export function add(a, b) { return a + b; }\n"),
    # Tier A (14 new)
    "csharp": (
        "Service.cs",
        "using System;\nnamespace Demo {\n  /// Doc\n  public class Service {\n"
        "    /// Run\n    public int Run(int x) { return x + 1; }\n  }\n}\n",
    ),
    "rust": (
        "lib.rs",
        "/// Point\npub struct Point { pub x: i32 }\n/// Add\npub fn add(a: i32, b: i32) -> i32 { a + b }\n",
    ),
    "ruby": ("service.rb", "# Service\nclass Service\n  # Run\n  def run(x)\n    x + 1\n  end\nend\n"),
    "kotlin": ("Service.kt", "/** Service */\nclass Service {\n  /** Run */\n  fun run(x: Int): Int = x + 1\n}\n"),
    "swift": (
        "Service.swift",
        "/// Service\nclass Service {\n  /// Run\n  func run(x: Int) -> Int { return x + 1 }\n}\n",
    ),
    "c": ("math.c", "/** Add */\nint add(int a, int b) { return a + b; }\n"),
    "cpp": (
        "math.cpp",
        "/// Service\nclass Service {\npublic:\n  /// Add\n  int add(int a, int b) { return a + b; }\n};\n",
    ),
    "scala": (
        "Service.scala",
        "/** Service */\nclass Service {\n  /** Add */\n  def add(a: Int, b: Int): Int = a + b\n}\n",
    ),
    "dart": ("service.dart", "/// Service\nclass Service {\n  /// Add\n  int add(int a, int b) => a + b;\n}\n"),
    "elixir": ("service.ex", "# Service\ndefmodule Service do\n  # Add\n  def add(a, b), do: a + b\nend\n"),
    "vue": (
        "App.vue",
        '<template><div>{{ msg }}</div></template>\n<script setup lang="ts">\n'
        "const msg = 'ok';\nfunction greet(name: string): string { return name; }\n</script>\n",
    ),
    "perl": (
        "service.pm",
        "use strict;\nuse warnings;\npackage Service;\n# Add\n"
        "sub add { my ($a, $b) = @_; return $a + $b; }\n1;\n",
    ),
    "cobol": (
        "HELLO.cob",
        "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. HELLO.\n"
        "       PROCEDURE DIVISION.\n       MAIN-PARA.\n           STOP RUN.\n",
    ),
    "r": ("analysis.R", "#' Add two numbers\nadd_vals <- function(a, b) {\n  a + b\n}\n"),
    # Tier B (20)
    "bash": ("deploy.sh", '#!/usr/bin/env bash\n# Greet\ngreet() {\n  printf \'%s\\n\' "$1"\n}\n'),
    "powershell": ("Run.ps1", "# Run\nfunction Invoke-Add {\n  param($a, $b)\n  return $a + $b\n}\n"),
    "groovy": ("Service.groovy", "class Service {\n  int add(int a, int b) {\n    return a + b\n  }\n}\n"),
    "objc": (
        "Service.m",
        "@interface Service\n- (int)add:(int)a;\n@end\n"
        "@implementation Service\n- (int)add:(int)a { return a + 1; }\n@end\n",
    ),
    "lua": ("math.lua", "--- Add\nlocal function add(a, b)\n  return a + b\nend\n"),
    "haskell": ("Math.hs", "module Math where\n-- | Add\nadd :: Int -> Int -> Int\nadd x y = x + y\n"),
    "fsharp": ("Math.fs", "module Math\n/// Add\nlet add x y = x + y\n"),
    "ocaml": ("math.ml", "(** Add *)\nlet add x y = x + y\n"),
    "zig": ("math.zig", "/// Add\npub fn add(a: i32, b: i32) i32 {\n  return a + b;\n}\n"),
    "julia": ("math.jl", "# Add\nfunction add(a::Int, b::Int)\n  return a + b\nend\n"),
    "fortran": (
        "math.f90",
        "module math\ncontains\n  integer function add(a, b)\n"
        "    integer, intent(in) :: a, b\n    add = a + b\n  end function add\nend module math\n",
    ),
    "matlab": ("add.m", "% Add\nfunction y = add(a, b)\n  y = a + b;\nend\n"),
    "svelte": (
        "App.svelte",
        '<script lang="ts">\n  export function add(a: number, b: number): number { return a + b; }\n'
        "</script>\n<p>ok</p>\n",
    ),
    "solidity": (
        "Vault.sol",
        "pragma solidity ^0.8.20;\n/// Vault\ncontract Vault {\n"
        "  /// Ping\n  function ping() external pure returns (uint256) { return 1; }\n}\n",
    ),
    "cuda": (
        "kernel.cu",
        "/// Kernel\n__global__ void scale(float* a, int n) {\n"
        "  int i = threadIdx.x;\n  if (i < n) { a[i] = a[i] * 2.0f; }\n}\n",
    ),
    "verilog": (
        "adder.sv",
        "// Adder\nmodule adder(input logic a, input logic b, output logic y);\n"
        "  assign y = a & b;\nendmodule\n",
    ),
    "vhdl": (
        "adder.vhd",
        "-- Adder\nentity adder is\nend entity adder;\n"
        "architecture rtl of adder is\nbegin\nend architecture rtl;\n",
    ),
    "ada": ("main.adb", "-- Main\nprocedure Main is\nbegin\n  null;\nend Main;\n"),
    "odin": ("math.odin", "package math\n// Add\nadd :: proc(a, b: int) -> int {\n  return a + b\n}\n"),
    "commonlisp": ("math.lisp", ";; Add\n(defun add (a b) (+ a b))\n"),
    # Tier C (15)
    "dockerfile": (
        "Dockerfile",
        'FROM python:3.12-slim\nWORKDIR /app\nUSER appuser\nCOPY . .\nCMD ["python", "app.py"]\n',
    ),
    "hcl": ("main.tf", 'resource "aws_s3_bucket" "logs" {\n  bucket = "demo-logs"\n}\n'),
    "bicep": (
        "main.bicep",
        "param location string = 'eastus'\n"
        "resource stg 'Microsoft.Storage/storageAccounts@2023-01-01' = {\n"
        "  name: 'demostg'\n  location: location\n}\n",
    ),
    "nix": ("default.nix", "{ pkgs }: pkgs.hello\n"),
    "make": ("Makefile", "all:\n\techo ok\n"),
    "starlark": ("BUILD.bazel", "def my_rule(name):\n    return name\n"),
    "protobuf": ("user.proto", 'syntax = "proto3";\npackage demo.v1;\nmessage User {\n  string user_id = 1;\n}\n'),
    "sql": ("schema.sql", "CREATE TABLE users (id INT PRIMARY KEY, name TEXT);\nSELECT id, name FROM users;\n"),
    "html": (
        "index.html",
        '<!DOCTYPE html><html><body><a href="https://example.com" target="_blank" '
        'rel="noopener noreferrer">Safe</a></body></html>\n',
    ),
    "css": ("site.css", ".card { color: #111; padding: 8px; }\n"),
    "scss": ("site.scss", "@use 'base';\n.card { color: #111; }\n"),
    "yaml": (
        "ci.yml",
        "name: ci\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        "    permissions:\n      contents: read\n    steps:\n"
        "      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n",
    ),
    "json": ("config.json", '{"name": "pni501", "ok": true}\n'),
    "toml": ("config.toml", '[service]\nname = "pni501"\n'),
    "xml": ("pom.xml", "<project><name>pni501</name></project>\n"),
}


def test_55_languages_and_57_grammars_registered() -> None:
    """Verify exact 55-language registration, suite coverage, and alias resolution."""
    all_langs = list_supported_languages()
    assert len(all_langs) == 55
    assert set(all_langs) == set(CLEAN_FIXTURES)
    assert set(SUITE_REGISTRY) == set(all_langs)
    assert len(GRAMMAR_PROVIDERS) == 57
    assert len(DEFAULT_COMPANION_LANGUAGES) == 15

    assert resolve_language_id("C#") == "csharp"
    assert resolve_language_id("c++") == "cpp"
    assert resolve_language_id("terraform") == "hcl"
    assert resolve_language_id("proto") == "protobuf"
    assert resolve_language_id("sh") == "bash"
    assert resolve_language_id("golang") == "go"
    assert resolve_language_id("COBOL") == "cobol"


@pytest.mark.parametrize("lang_id", list_supported_languages())
def test_every_language_end_to_end_ast_analyze(lang_id: str, tmp_path: Path) -> None:
    """Verify every one of the 55 languages parses cleanly and produces valid AstFacts."""
    filename, code = CLEAN_FIXTURES[lang_id]
    target_file = tmp_path / filename
    target_file.write_text(code, encoding="utf-8")

    spec = get_language_spec(lang_id)
    assert spec is not None
    root = parse_cst(code, spec.default_grammar)
    assert not root.has(kind="ERROR"), f"Unexpected CST ERROR for {lang_id}"

    facts = run_ast_analyze(
        tmp_path,
        targets=["."],
        lang=lang_id,
        detected_frameworks=[],
        declared_lang_version="",
    )
    assert facts.language == lang_id
    assert facts.total_files == 1
    assert facts.total_loc >= 1


def test_tier_a_defective_fixtures_detection(tmp_path: Path) -> None:
    """Verify Tier A languages detect real security sinks, bug idioms, globals, and SFC/legacy risks."""
    rs_dir = tmp_path / "rust_proj"
    rs_dir.mkdir()
    (rs_dir / "lib.rs").write_text(
        "use std::io::*;\nstatic mut CNT: i32 = 0;\n"
        "pub fn bad(x: Option<i32>) -> i32 {\n"
        "  let _ = reqwest::Client::builder().danger_accept_invalid_certs(true);\n"
        "  unsafe { CNT += 1; }\n"
        "  x.unwrap()\n"
        "}\n",
        encoding="utf-8",
    )
    rs_facts = run_ast_analyze(rs_dir, targets=["."], lang="rust", detected_frameworks=[], declared_lang_version="")
    assert rs_facts.total_functions == 1
    assert len(rs_facts.wildcard_imports) == 1
    assert len(rs_facts.global_state_usages) == 1
    assert any("unwrap" in b.symbol for b in rs_facts.bug_risk_idioms)
    assert any("unsafe" in b.symbol for b in rs_facts.bug_risk_idioms)
    assert any(s.cwe_id == "CWE-295" for s in rs_facts.dangerous_sinks)

    vue_dir = tmp_path / "vue_proj"
    vue_dir.mkdir()
    (vue_dir / "Bad.vue").write_text(
        '<template><div v-html="userHtml"></div></template>\n'
        '<script setup lang="ts">\n'
        "function renderUnsafe(raw: string): string { return eval(raw); }\n"
        "</script>\n",
        encoding="utf-8",
    )
    vue_facts = run_ast_analyze(vue_dir, targets=["."], lang="vue", detected_frameworks=[], declared_lang_version="")
    assert vue_facts.total_functions == 1
    assert {"CWE-79", "CWE-94"} <= {s.cwe_id for s in vue_facts.dangerous_sinks}

    cob_dir = tmp_path / "cobol_proj"
    cob_dir.mkdir()
    (cob_dir / "PAYROLL.cob").write_text(
        "000100 IDENTIFICATION DIVISION.\n"
        "000200 PROGRAM-ID. PAYROLL.\n"
        "000300 PROCEDURE DIVISION.\n"
        "000400 MAIN-PARA.\n"
        "000500     GO TO END-PARA.\n"
        "000600 END-PARA.\n"
        "000700     STOP RUN.\n",
        encoding="utf-8",
    )
    cob_facts = run_ast_analyze(cob_dir, targets=["."], lang="cobol", detected_frameworks=[], declared_lang_version="")
    assert cob_facts.total_classes >= 1
    assert cob_facts.total_functions >= 2
    assert any(b.symbol == "GO TO" for b in cob_facts.bug_risk_idioms)

    pl_dir = tmp_path / "perl_proj"
    pl_dir.mkdir()
    (pl_dir / "legacy.pl").write_text(
        'sub run {\n  my ($cmd) = @_;\n  open($fh, "|$cmd");\n  eval($cmd);\n}\n',
        encoding="utf-8",
    )
    pl_facts = run_ast_analyze(pl_dir, targets=["."], lang="perl", detected_frameworks=[], declared_lang_version="")
    assert pl_facts.total_functions == 1
    assert any("use strict" in b.symbol for b in pl_facts.bug_risk_idioms)
    assert {"CWE-78", "CWE-94"} <= {s.cwe_id for s in pl_facts.dangerous_sinks}

    r_dir = tmp_path / "r_proj"
    r_dir.mkdir()
    (r_dir / "bad.R").write_text(
        "library(dplyr)\n"
        "attach(mtcars)\n"
        "run_bad <- function(cmd) {\n"
        "  g_val <<- 42\n"
        "  eval(parse(text = cmd))\n"
        "  system(cmd)\n"
        "}\n",
        encoding="utf-8",
    )
    r_facts = run_ast_analyze(r_dir, targets=["."], lang="r", detected_frameworks=[], declared_lang_version="")
    assert r_facts.total_functions == 1
    assert len(r_facts.global_state_usages) >= 1
    assert any("<<-" in b.symbol for b in r_facts.bug_risk_idioms)
    assert {"CWE-94", "CWE-78"} <= {s.cwe_id for s in r_facts.dangerous_sinks}


def test_tier_b_and_c_defective_fixtures_and_companion_scanner(tmp_path: Path) -> None:
    """Verify Tier B (Solidity/Svelte) and Tier C companion scanner (Dockerfile/HCL/Proto/YAML/SQL/HTML)."""
    sol_dir = tmp_path / "sol"
    sol_dir.mkdir()
    (sol_dir / "Bad.sol").write_text(
        "pragma solidity ^0.8.20;\ncontract Bad {\n  function run(address t) external {\n"
        '    require(tx.origin == msg.sender);\n    t.delegatecall("");\n  }\n}\n',
        encoding="utf-8",
    )
    sol_facts = run_ast_analyze(
        sol_dir, targets=["."], lang="solidity", detected_frameworks=[], declared_lang_version=""
    )
    assert {"CWE-287", "CWE-829"} <= {s.cwe_id for s in sol_facts.dangerous_sinks}

    sv_dir = tmp_path / "svelte"
    sv_dir.mkdir()
    (sv_dir / "Bad.svelte").write_text("<script>let x = '<img />';</script>{@html x}\n", encoding="utf-8")
    sv_facts = run_ast_analyze(sv_dir, targets=["."], lang="svelte", detected_frameworks=[], declared_lang_version="")
    assert any(s.cwe_id == "CWE-79" for s in sv_facts.dangerous_sinks)

    comp_dir = tmp_path / "polyglot_repo"
    comp_dir.mkdir()
    (comp_dir / "Dockerfile").write_text(
        "FROM python:latest\nRUN curl -fsSL https://example.com/install.sh | sh\nUSER root\n",
        encoding="utf-8",
    )
    (comp_dir / "main.tf").write_text(
        'resource "aws_security_group" "open" {\n  cidr_blocks = ["0.0.0.0/0"]\n  encrypted = false\n}\n',
        encoding="utf-8",
    )
    (comp_dir / "api.proto").write_text(
        'syntax = "proto2";\nmessage bad_msg {\n  string BadField = 1;\n  string other = 1;\n}\n',
        encoding="utf-8",
    )
    (comp_dir / "migration.sql").write_text("DROP TABLE users;\nSELECT * FROM users;\n", encoding="utf-8")
    (comp_dir / "ci.yml").write_text(
        "name: ci\npermissions: write-all\njobs:\n  build:\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )
    (comp_dir / "page.html").write_text(
        '<!DOCTYPE html><html><body><a href="https://x.com" target="_blank">x</a>'
        '<button onclick="go()">go</button></body></html>\n',
        encoding="utf-8",
    )

    companion = scan_companion_languages(comp_dir)
    assert {"dockerfile", "hcl", "protobuf", "sql", "yaml", "html"} <= set(companion)

    df_facts = companion["dockerfile"]
    assert any("AVD-DS-0001" in b.detail for b in df_facts.bug_risk_idioms)
    assert any("AVD-DS-0002" in b.detail for b in df_facts.bug_risk_idioms)
    assert any(s.cwe_id == "CWE-829" for s in df_facts.dangerous_sinks)

    hcl_facts = companion["hcl"]
    assert {"CWE-284", "CWE-311"} <= {s.cwe_id for s in hcl_facts.dangerous_sinks}

    proto_facts = companion["protobuf"]
    assert any("package" in b.symbol for b in proto_facts.bug_risk_idioms)
    assert any("Duplicate" in b.detail for b in proto_facts.bug_risk_idioms)

    sql_facts = companion["sql"]
    assert len(sql_facts.bug_risk_idioms) >= 2

    yaml_facts = companion["yaml"]
    assert any(s.cwe_id == "CWE-269" for s in yaml_facts.dangerous_sinks)
    assert any("commit SHA" in b.detail for b in yaml_facts.bug_risk_idioms)

    html_facts = companion["html"]
    assert any("noopener" in b.detail for b in html_facts.bug_risk_idioms)
    assert any(s.cwe_id == "CWE-79" for s in html_facts.dangerous_sinks)


def test_extended_manifest_detection_and_scaffolding(tmp_path: Path) -> None:
    """Verify auto-detection, project_inspect, and generic rules/actions/workflows scaffolding for extended langs."""
    rust_repo = tmp_path / "rust_app"
    (rust_repo / "src").mkdir(parents=True)
    (rust_repo / "Cargo.toml").write_text(
        '[package]\nname = "demo-rs"\nversion = "0.2.0"\nedition = "2021"\n\n[dependencies]\nserde = "1.0"\n',
        encoding="utf-8",
    )
    (rust_repo / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")

    assert detect_active_language(rust_repo) == "rust"
    pf = run_project_inspect(rust_repo)
    assert pf.language == "rust"
    assert pf.project_name == "demo-rs"
    assert pf.version == "0.2.0"
    assert pf.build_system == "cargo"
    assert "serde" in pf.dependencies
    assert any("Cargo.lock" in issue for issue in pf.tooling_modernization_issues)
    assert not any("pyproject.toml" in issue for issue in pf.tooling_modernization_issues)

    for lang in ("rust", "cobol", "r", "vue", "dockerfile"):
        ws = tmp_path / f"scaffold_{lang}"
        ws.mkdir()
        rules = list_rules(ws, lang=lang)
        assert any(r.scope == lang for r in rules)
        assert len(copy_rule_templates(ws, lang=lang)) > 0
        assert len(copy_action_templates(ws, lang=lang)) > 0
        assert len(copy_workflow_templates(ws, lang=lang)) > 0

    cs_repo = tmp_path / "cs_app"
    cs_repo.mkdir()
    (cs_repo / "Demo.csproj").write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup>'
        '<ItemGroup><PackageReference Include="Newtonsoft.Json" Version="13.0.3" /></ItemGroup></Project>\n',
        encoding="utf-8",
    )
    assert detect_active_language(cs_repo) == "csharp"
    cs_pf = run_project_inspect(cs_repo)
    assert cs_pf.build_system == "dotnet"
    assert cs_pf.language_version_constraint == "net8.0"
    assert "Newtonsoft.Json" in cs_pf.dependencies

    r_repo = tmp_path / "r_pkg"
    r_repo.mkdir()
    (r_repo / "DESCRIPTION").write_text("Package: demor\nVersion: 1.0.0\nImports: dplyr, tidyr\n", encoding="utf-8")
    assert detect_active_language(r_repo) == "r"
    r_pf = run_project_inspect(r_repo)
    assert r_pf.project_name == "demor"
    assert "dplyr" in r_pf.dependencies


def test_extra_grammars_per_language_lazy_isolation() -> None:
    """Verify parsing Dockerfile does NOT eagerly load the 12.5 MB COBOL C extension."""
    saved = {k: v for k, v in list(sys.modules.items()) if k.startswith("pni._cached_grammars._")}
    try:
        for k in saved:
            sys.modules.pop(k, None)
        _cst._LANGUAGE_CACHE.pop("dockerfile", None)
        _cst._PARSER_CACHE.pop("dockerfile", None)

        root = parse_cst("FROM python:3.12-slim\n", "dockerfile")
        assert not root.has(kind="ERROR")
        assert "pni._cached_grammars._dockerfile" in sys.modules
        assert "pni._cached_grammars._cobol" not in sys.modules
    finally:
        sys.modules.update(saved)
