# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for TypeScript and JavaScript language support across all PNI501 subsystems."""

from __future__ import annotations

import json
from pathlib import Path

from pni._actions import (
    list_actions,
    load_composite_action,
    run_ast_analyze,
    run_project_inspect,
)
from pni._actions.migration_analyze.codemods import match_codemod_recipes
from pni._actions.migration_analyze.contracts import extract_implicit_and_env_contracts
from pni._actions.migration_analyze.models import MigrationOptions
from pni._actions.migration_analyze.touchpoints import extract_boundary_touchpoints
from pni._actions.pentest.server_plan import build_live_server_plan
from pni._actions.runtime_check.parsers import (
    parse_istanbul_coverage_summary,
    parse_lcov_info,
    parse_node_test_output,
)
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_harness_tool,
    select_node_image_version,
)
from pni._actions.runtime_check.smoke import build_smoke_plan
from pni._actions.security_scan.dep_scopes import discover_non_core_packages
from pni._actions.security_scan.parsers import parse_trivy_reports
from pni._dockerfiles import ensure_target_dockerfile
from pni._reporter.compiler import lint_drawlib_chapters
from pni._reporter.drawlib_guide import render_drawlib_report_guide
from pni._rules.manager import detect_active_language
from pni._workflows import load_workflow
from pni.cli import init_project


def test_typescript_and_javascript_language_detection_and_inspect(tmp_path: Path) -> None:
    """Verify TypeScript vs JavaScript auto-detection, package.json/tsconfig inspection, and test partitioning."""
    ts_dir = tmp_path / "ts_service"
    ts_dir.mkdir()
    (ts_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "@acme/checkout-api",
                "version": "2.1.0",
                "engines": {"node": ">=20.0.0"},
                "main": "dist/index.js",
                "bin": {"checkout-cli": "dist/cli.js"},
                "dependencies": {
                    "express": "^4.19.2",
                    "zod": "^3.23.0",
                    "legacy-sdk": "latest",
                },
                "devDependencies": {
                    "typescript": "^5.5.0",
                    "vitest": "^2.0.0",
                    "eslint": "^9.0.0",
                },
            }
        ),
        encoding="utf-8",
    )
    (ts_dir / "tsconfig.json").write_text(
        '// TypeScript config with JSONC comment\n'
        '{\n  "compilerOptions": {\n    "strict": true,\n    "target": "ES2022",\n  }\n}\n',
        encoding="utf-8",
    )
    (ts_dir / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n", encoding="utf-8")
    (ts_dir / "src").mkdir()
    (ts_dir / "src" / "app.ts").write_text("export const x: number = 1;\n", encoding="utf-8")
    (ts_dir / "src" / "app.test.ts").write_text("import { expect, test } from 'vitest';\n", encoding="utf-8")
    (ts_dir / "src" / "types.d.ts").write_text("export interface GlobalCfg {}\n", encoding="utf-8")

    # node_modules must never be counted as application source or test files
    nm_dir = ts_dir / "node_modules" / "express"
    nm_dir.mkdir(parents=True)
    (nm_dir / "index.js").write_text("module.exports = {};\n", encoding="utf-8")

    assert detect_active_language(ts_dir) == "typescript"
    ts_facts = run_project_inspect(ts_dir)
    assert ts_facts.language == "typescript"
    assert ts_facts.build_system == "pnpm"
    assert ts_facts.project_name == "@acme/checkout-api"
    assert ts_facts.version == "2.1.0"
    assert ts_facts.language_version_constraint == ">=20.0.0"
    assert "pnpm-lock.yaml" in ts_facts.lockfiles_found
    assert "express" in ts_facts.detected_frameworks
    assert "vitest" in ts_facts.detected_frameworks
    assert "legacy-sdk" in ts_facts.unpinned_dependencies
    assert ts_facts.source_files_count == 1
    assert ts_facts.test_files_count == 1
    assert ts_facts.tooling_modernization_issues == []
    assert "web_api" in ts_facts.runtime_types
    assert "cli" in ts_facts.runtime_types

    non_core = discover_non_core_packages(ts_dir)
    assert "vitest" in non_core
    assert "express" not in non_core

    # Pure JavaScript project (package.json + .js files, no tsconfig.json or .ts files)
    js_dir = tmp_path / "js_worker"
    js_dir.mkdir()
    (js_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "js-worker",
                "version": "0.5.0",
                "dependencies": {"bullmq": "^5.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (js_dir / "src").mkdir()
    (js_dir / "src" / "worker.js").write_text("console.log('worker');\n", encoding="utf-8")
    (js_dir / "src" / "worker.spec.js").write_text("console.log('spec');\n", encoding="utf-8")

    assert detect_active_language(js_dir) == "javascript"
    js_facts = run_project_inspect(js_dir)
    assert js_facts.language == "javascript"
    assert js_facts.build_system == "npm"
    assert js_facts.source_files_count == 1
    assert js_facts.test_files_count == 1
    assert "worker" in js_facts.runtime_types
    assert any("lockfile" in issue.lower() for issue in js_facts.tooling_modernization_issues)
    assert any("linter" in issue.lower() for issue in js_facts.tooling_modernization_issues)


def test_typescript_ast_clean_and_defective(tmp_path: Path) -> None:
    """Verify TypeScript AST analysis on clean strict code and defective TS/TSX code."""
    clean_dir = tmp_path / "clean_ts"
    clean_dir.mkdir()
    (clean_dir / "package.json").write_text(
        json.dumps({"name": "clean-ts", "dependencies": {}, "devDependencies": {"vitest": "^2.0.0"}}),
        encoding="utf-8",
    )
    (clean_dir / "src").mkdir()
    (clean_dir / "src" / "math.ts").write_text(
        """/**
 * Multiply two numbers safely.
 */
export function multiply(a: number, b: number): number {
  return a * b;
}
""",
        encoding="utf-8",
    )
    (clean_dir / "src" / "math.test.ts").write_text(
        """import { describe, expect, it } from 'vitest';
import { multiply } from './math';

describe('multiply', () => {
  it('computes product', () => {
    expect(multiply(3, 4)).toBe(12);
  });
});
""",
        encoding="utf-8",
    )

    clean_facts = run_ast_analyze(clean_dir, lang="typescript")
    assert clean_facts.language == "typescript"
    assert clean_facts.total_files == 1
    assert clean_facts.total_functions == 1
    assert clean_facts.type_safety_coverage_pct == 100.0
    assert clean_facts.docstring_coverage_pct == 100.0
    assert clean_facts.type_safety_issues == []
    assert clean_facts.weak_type_usages == []
    assert clean_facts.dangerous_sinks == []
    assert clean_facts.test_functions_count == 1
    assert clean_facts.assertion_free_tests == []

    # Defective TypeScript + React TSX + Express project
    bad_dir = tmp_path / "bad_ts"
    bad_dir.mkdir()
    (bad_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "bad-ts",
                "dependencies": {
                    "express": "^4.19.0",
                    "react": "^18.3.0",
                    "next": "^14.2.0",
                },
            }
        ),
        encoding="utf-8",
    )
    (bad_dir / "src").mkdir()
    (bad_dir / "src" / "server.tsx").write_text(
        """'use client';
import * as fs from 'fs';
import { exec } from 'child_process';
import crypto from 'crypto';
import express from 'express';
import cors from 'cors';
import * as undeclaredPkg from 'undeclared-lib';

var legacyGlobal = 1;

// @ts-ignore
export async function handleRequest(req: any, res) {
  const secret = process.env.NEXT_PUBLIC_OK || process.env.STRIPE_SECRET_KEY;
  const userId = (req.query as any).id!;
  if (userId == 'admin') {
    console.log('admin login', secret, legacyGlobal, undeclaredPkg);
    debugger;
  }
  try {
    const data = fs.readFileSync('/tmp/cfg.json', 'utf8');
    await fetch('https://api.example.com/items');
    await req.db.query(`SELECT * FROM users WHERE id = ${userId}`);
    exec(`ls ${userId}`);
    eval(data);
    crypto.createHash('md5').update(userId).digest('hex');
    const tok = Math.random().toString(36);
    res.send(tok);
  } catch (err) {}
}

export function UserList(props: { items: string[]; rawHtml: string }) {
  return (
    <div>
      <div dangerouslySetInnerHTML={{ __html: props.rawHtml }} />
      {props.items.map((item, idx) => (
        <span key={idx}>{item}</span>
      ))}
    </div>
  );
}

const app = express();
app.use(cors());
app.get('/api/users', handleRequest);
""",
        encoding="utf-8",
    )
    (bad_dir / "src" / "server.test.ts").write_text(
        """import { it, vi } from 'vitest';

it.only('focused test without assertions and many mocks', () => {
  const m1 = vi.fn();
  const m2 = vi.fn();
  const m3 = vi.fn();
  const m4 = vi.fn();
  const m5 = vi.fn();
  const m6 = vi.fn();
  m1(); m2(); m3(); m4(); m5(); m6();
});
""",
        encoding="utf-8",
    )

    bad_facts = run_ast_analyze(bad_dir, lang="typescript")
    assert len(bad_facts.wildcard_imports) >= 1
    assert len(bad_facts.type_safety_issues) >= 1
    assert len(bad_facts.weak_type_usages) >= 2
    assert len(bad_facts.unscoped_type_ignores) >= 1
    assert len(bad_facts.bug_risk_idioms) >= 3
    assert len(bad_facts.undeclared_dependencies) >= 1
    assert any(u.symbol == "undeclared-lib" for u in bad_facts.undeclared_dependencies)
    assert len(bad_facts.unstructured_logging) >= 1
    assert len(bad_facts.missing_io_timeouts) >= 1
    assert len(bad_facts.dangerous_sinks) >= 6
    assert any(ep.path == "/api/users" and ep.http_method == "GET" for ep in bad_facts.api_endpoints)
    assert len(bad_facts.framework_issues) >= 2
    assert len(bad_facts.assertion_free_tests) == 1
    assert any(".only" in note for note in bad_facts.test_harness_notes)
    assert any("mock" in note.lower() for note in bad_facts.test_harness_notes)


def test_javascript_ast_jsdoc_and_cjs_esm_mixing(tmp_path: Path) -> None:
    """Verify JavaScript JSDoc @param/@returns typing coverage and CJS/ESM mixing detection."""
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "js-app", "dependencies": {"express": "^4.19.0"}}),
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "documented.js").write_text(
        """/**
 * Format user greeting.
 * @param {string} name
 * @returns {string}
 */
export function greet(name) {
  return `Hello, ${name}`;
}
""",
        encoding="utf-8",
    )
    clean_js = run_ast_analyze(tmp_path, lang="javascript")
    assert clean_js.language == "javascript"
    assert clean_js.type_safety_coverage_pct == 100.0
    assert clean_js.docstring_coverage_pct == 100.0

    # Add a second file mixing import and require() without JSDoc
    (tmp_path / "src" / "mixed.js").write_text(
        """import express from 'express';
const path = require('path');

export function untypedHelper(a, b) {
  return path.join(a, b, String( Boolean(express) ));
}
""",
        encoding="utf-8",
    )
    mixed_js = run_ast_analyze(tmp_path, lang="javascript")
    assert mixed_js.type_safety_coverage_pct is not None
    assert mixed_js.type_safety_coverage_pct < 100.0
    assert len(mixed_js.unsorted_imports) >= 1
    assert len(mixed_js.type_safety_issues) >= 1


def test_ts_js_runtime_selector_parsers_smoke_and_migration(tmp_path: Path) -> None:
    """Verify Node.js image version selector, test/coverage parsers, smoke plan, pentest plan, and migration."""
    assert select_node_image_version(None) == "20"
    assert select_node_image_version("^18.18.0") == "18"
    assert select_node_image_version(">=22.0.0") == "22"

    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "ts-web",
                "engines": {"node": ">=22.0.0"},
                "scripts": {"start": "node dist/server.js", "test": "vitest run"},
                "dependencies": {"express": "^4.19.0", "@prisma/client": "^5.0.0"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "tsconfig.json").write_text('{"compilerOptions": {"strict": true}}\n', encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "server.ts").write_text(
        """import express from 'express';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
const app = express();

app.post('/checkout', async (req, res) => {
  const amount = req.body.amount ?? 100;
  const apiKey = process.env.STRIPE_API_KEY ?? 'sk_test_123';
  await fetch('https://api.stripe.com/v1/charges');
  res.json({ ok: true, amount, hasKey: Boolean(apiKey), db: Boolean(prisma) });
});
""",
        encoding="utf-8",
    )

    pf = run_project_inspect(tmp_path, lang="typescript")
    tool = select_harness_tool(pf)
    assert tool == "node"
    assert compute_harness_build_args(pf) == {"NODE_VERSION": "22"}

    test_cmd = build_test_and_coverage_command(pf, tool, ["src"], ["src"])
    assert "vitest" in test_cmd[2]
    assert "jest" in test_cmd[2]

    _arch, smoke_cmd = build_smoke_plan(tmp_path, pf, ["src"])
    assert smoke_cmd is not None
    assert "tsc --noEmit" in smoke_cmd[2]

    ast_facts = run_ast_analyze(tmp_path, lang="typescript")
    live_cmd, reason = build_live_server_plan(tmp_path, pf, ["src"], ast_facts=ast_facts, container_port=18080)
    assert reason == ""
    assert live_cmd is not None
    assert "npm run start" in live_cmd[2]

    # Jest/Vitest and node --test output parsers
    jest_out = tmp_path / "node_test.txt"
    jest_out.write_text(
        """ FAIL  src/server.test.ts
  ✕ rejects negative amount (5 ms)
Tests:       1 failed, 1 skipped, 4 passed, 6 total
""",
        encoding="utf-8",
    )
    total, passed, failed, errors, skipped, failures = parse_node_test_output(jest_out)
    assert (total, passed, failed, errors, skipped) == (6, 4, 1, 0, 1)
    assert len(failures) == 1

    tap_out = tmp_path / "tap_test.txt"
    tap_out.write_text("ℹ tests 5\nℹ pass 5\nℹ fail 0\nℹ skipped 0\n", encoding="utf-8")
    assert parse_node_test_output(tap_out)[:5] == (5, 5, 0, 0, 0)

    # Istanbul coverage-summary.json parser
    cov_summary = tmp_path / "coverage-summary.json"
    cov_summary.write_text(
        json.dumps(
            {
                "total": {
                    "lines": {"total": 50, "covered": 40, "skipped": 0, "pct": 80},
                    "branches": {"total": 10, "covered": 7, "skipped": 0, "pct": 70},
                },
                "/workspace/src/server.ts": {
                    "lines": {"total": 50, "covered": 40, "skipped": 0, "pct": 80},
                    "branches": {"total": 10, "covered": 7, "skipped": 0, "pct": 70},
                },
            }
        ),
        encoding="utf-8",
    )
    cov = parse_istanbul_coverage_summary(cov_summary)
    assert cov.measured is True
    assert cov.tool == "istanbul-summary"
    assert cov.line_coverage_pct == 80.0
    assert cov.branch_coverage_pct == 70.0
    assert cov.lowest_covered_modules[0].file_path == "src/server.ts"

    # Migration touchpoints, contracts, and codemods
    src_map = {"src/server.ts": (tmp_path / "src" / "server.ts").read_text(encoding="utf-8")}
    touchpoints = extract_boundary_touchpoints(src_map, "typescript", ast_facts)
    assert any(tp.kind == "persistence_db" for tp in touchpoints)
    assert any(tp.kind == "external_http_rpc" for tp in touchpoints)

    implicit_contracts, env_contracts = extract_implicit_and_env_contracts(src_map, "typescript", ast_facts)
    assert len(implicit_contracts) == 1
    assert implicit_contracts[0].input_fields[0].key == "amount"
    assert any(e.name == "STRIPE_API_KEY" and e.default_value == "<REDACTED>" for e in env_contracts)

    js_recipes = match_codemod_recipes("javascript", MigrationOptions(), "Migrate JS to TS", ast_facts)
    assert len(js_recipes) == 2

    # Scaffolding & workflow loading for both TypeScript and JavaScript
    init_project(tmp_path, lang="typescript")
    assert any(a.id == "typescript_ast_audit" for a in list_actions(tmp_path))
    ts_act = load_composite_action("typescript_ast_audit", tmp_path)
    assert ts_act is not None
    ts_wf = load_workflow("full_audit", tmp_path)
    assert ts_wf is not None
    df_path, template_id = ensure_target_dockerfile(tmp_path, ".", "typescript", "node")
    assert df_path.is_file()
    assert template_id == "typescript/node.dockerfile"

    js_init_dir = tmp_path / "js_init"
    js_init_dir.mkdir()
    init_project(js_init_dir, lang="javascript")
    assert any(a.id == "javascript_ast_audit" for a in list_actions(js_init_dir))


def test_ts_js_monorepo_zod_refinements(tmp_path: Path) -> None:
    """Verify Vitest /tmp/pni-cov, pnpm-lock monorepo scope, expectTypeOf<T>, and barrel cycle separation."""
    mono_dir = tmp_path / "zod_mono"
    pkg_zod = mono_dir / "packages" / "zod" / "src"
    pkg_docs = mono_dir / "packages" / "docs"
    pkg_zod.mkdir(parents=True)
    pkg_docs.mkdir(parents=True)

    (mono_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "zod-monorepo",
                "private": True,
                "packageManager": "nub@0.8.3",
                "scripts": {"prepare": "husky", "test": "vitest run"},
                "devDependencies": {"vitest": "^3.0.0", "typescript": "^5.5.0"},
            }
        ),
        encoding="utf-8",
    )
    (mono_dir / "packages" / "zod" / "package.json").write_text(
        json.dumps({"name": "zod", "version": "4.6.7", "dependencies": {}}),
        encoding="utf-8",
    )
    (mono_dir / "packages" / "zod" / "tsconfig.json").write_text(
        '{"compilerOptions": {"strict": true}}\n',
        encoding="utf-8",
    )
    (pkg_docs / "package.json").write_text(
        json.dumps({"name": "zod-docs", "dependencies": {"next": "14.1.0", "postcss": "8.4.30"}}),
        encoding="utf-8",
    )
    (mono_dir / "pnpm-lock.yaml").write_text(
        """lockfileVersion: '9.0'
importers:
  .:
    devDependencies:
      vitest:
        specifier: ^3.0.0
        version: 3.0.0
  packages/zod: {}
  packages/docs:
    dependencies:
      next:
        specifier: 14.1.0
        version: 14.1.0
packages:
  'next@14.1.0':
    resolution: {integrity: sha512-abc}
  '@next/env@14.1.0':
    resolution: {integrity: sha512-def}
  'vitest@3.0.0':
    dev: true
snapshots:
  'next@14.1.0':
    dependencies:
      '@next/env': 14.1.0
""",
        encoding="utf-8",
    )

    # 1. Monorepo zero-dependency target package classifies workspace/docs lockfile deps as non-core
    non_core = discover_non_core_packages(mono_dir, source_targets=["packages/zod/src"])
    assert "next" in non_core
    assert "@next/env" in non_core
    assert "postcss" in non_core
    assert "vitest" in non_core

    # 2. Barrel index.ts re-export cycle vs implementation cycle + expectTypeOf<T> / assertType<T>
    (pkg_zod / "index.ts").write_text(
        'export * from "./schemas.js";\nexport * from "./checks.js";\n',
        encoding="utf-8",
    )
    (pkg_zod / "schemas.ts").write_text(
        """import { runCheck } from "./index.js";
import { type CheckMeta } from "./checks.js";

/**
 * Parse schema value.
 */
export function parseSchema(val: string): string {
  const _meta: CheckMeta | undefined = undefined;
  return runCheck(val) + (_meta ? "" : "");
}
""",
        encoding="utf-8",
    )
    (pkg_zod / "checks.ts").write_text(
        """export interface CheckMeta {
  id: string;
}

/**
 * Run validation check.
 */
export function runCheck(input: string): string {
  return input.trim();
}
""",
        encoding="utf-8",
    )
    (pkg_zod / "schemas.test.ts").write_text(
        """import { assertType, expectTypeOf, test } from "vitest";
import { parseSchema } from "./schemas.js";

test("generic expectTypeOf and assertType assertions", () => {
  const out = parseSchema("ok");
  expectTypeOf<string>(out).toEqualTypeOf<string>();
  assertType<string>(out);
});

test("negative compile-time type check", () => {
  // @ts-expect-error number is not assignable to string parameter
  parseSchema(123);
});
""",
        encoding="utf-8",
    )

    ast_facts = run_ast_analyze(
        mono_dir,
        targets=["packages/zod/src"],
        test_targets=["packages/zod/src"],
        lang="typescript",
    )
    assert ast_facts.test_functions_count == 2
    assert ast_facts.assertion_free_tests == []
    assert ast_facts.circular_dependencies == []
    assert len(ast_facts.type_checking_cycles) >= 1

    # 3. Runtime check commands and Dockerfile hardening
    pf = run_project_inspect(mono_dir, source_dirs=["packages/zod/src"], lang="typescript")
    test_cmd = build_test_and_coverage_command(pf, "node", ["packages/zod/src"], ["packages/zod/src"])
    assert "--coverage.clean=false" in test_cmd[2]
    assert "pni-cov" in test_cmd[2]

    _arch, smoke_cmd = build_smoke_plan(mono_dir, pf, ["packages/zod/src"])
    assert smoke_cmd is not None
    assert "packages/zod/tsconfig.json" in smoke_cmd[2]

    df_path, _ = ensure_target_dockerfile(mono_dir, ".", "typescript", "node")
    df_text = df_path.read_text(encoding="utf-8")
    assert "COREPACK_ENABLE_STRICT=0" in df_text
    assert "@vitest/coverage-v8" in df_text
    assert "USER pni" in df_text


def test_javascript_iife_htmx_refinements(tmp_path: Path) -> None:
    """Verify IIFE + ES2022 class AST extraction, .d.ts companions, test/ discovery, and Trivy/lcov fixes."""
    htmx_dir = tmp_path / "htmx_proj"
    src_dir = htmx_dir / "src"
    test_unit_dir = htmx_dir / "test" / "tests" / "unit"
    test_attr_dir = htmx_dir / "test" / "tests" / "attributes"
    test_util_dir = htmx_dir / "test" / "util"
    src_dir.mkdir(parents=True)
    test_unit_dir.mkdir(parents=True)
    test_attr_dir.mkdir(parents=True)
    test_util_dir.mkdir(parents=True)

    (htmx_dir / "package.json").write_text(
        json.dumps(
            {
                "name": "htmx.org",
                "version": "4.0.1",
                "types": "./dist/htmx.d.ts",
                "dependencies": {},
                "devDependencies": {
                    "@web/test-runner": "^0.18.0",
                    "@web/test-runner-playwright": "^0.11.0",
                    "chai": "^4.3.0",
                },
            }
        ),
        encoding="utf-8",
    )
    (htmx_dir / "package-lock.json").write_text(
        json.dumps(
            {
                "lockfileVersion": 3,
                "packages": {
                    "": {"name": "htmx.org", "devDependencies": {"@web/test-runner": "^0.18.0"}},
                    "node_modules/@web/test-runner": {"version": "0.18.0"},
                    "node_modules/koa": {"version": "2.15.0"},
                },
            }
        ),
        encoding="utf-8",
    )
    (htmx_dir / "yarn.lock").write_text(
        '"sinon@^15.0.0":\n  version "15.2.0"\n',
        encoding="utf-8",
    )

    # Task 1: Zero-dependency lockfiles + Trivy image global toolchain path scope
    non_core = discover_non_core_packages(htmx_dir)
    assert "@web/test-runner" in non_core
    assert "koa" in non_core
    assert "sinon" in non_core

    trivy_img = tmp_path / "trivy_img.json"
    trivy_img.write_text(
        json.dumps(
            {
                "Results": [
                    {
                        "Target": "Node.js",
                        "Class": "lang-pkgs",
                        "Type": "node-pkg",
                        "Vulnerabilities": [
                            {
                                "VulnerabilityID": "CVE-2026-0001",
                                "PkgName": "tar",
                                "InstalledVersion": "6.2.1",
                                "FixedVersion": "6.2.2",
                                "Severity": "HIGH",
                                "PkgPath": "usr/local/lib/node_modules/npm/node_modules/tar/package.json",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    bundle = parse_trivy_reports(image_json_path=trivy_img, is_harness_image=True)
    assert bundle.core_app_vuln_counts.high == 0
    assert bundle.harness_os_vuln_counts.high == 1

    # Task 2: IIFE + ES2022 classes (#private methods) + companion .d.ts
    (src_dir / "htmx.js").write_text(
        """var htmx = (() => {
  class HCON {
    parse(str) {
      return str ? str.trim() : "";
    }
  }

  class Htmx {
    #resolveTarget(elt, sel) {
      if (!sel) {
        return elt;
      }
      return document.querySelector(sel) || elt;
    }

    /**
     * Issue an AJAX request.
     */
    ajax(method, path, context) {
      if (!method || !path) {
        return Promise.resolve();
      }
      const target = this.#resolveTarget(context, "body");
      return fetch(path, { method, signal: AbortSignal.timeout(5000), headers: { "X-Target": String(target) } });
    }
  }

  return new Htmx();
})();
""",
        encoding="utf-8",
    )
    (src_dir / "htmx.d.ts").write_text(
        """export interface HtmxConfig {
  defaultSwapStyle: string;
}

export declare class HCON {
  parse(str: string): string;
}

export declare class Htmx {
  ajax(method: string, path: string, context?: unknown): Promise<Response | void>;
}
""",
        encoding="utf-8",
    )

    # Task 3: Suffix-less test files under test/, excluded helper.js, custom assert*/verify*/check*
    (htmx_dir / "web-test-runner.config.js").write_text(
        'export default { testRunnerHtml: (f) => `<script src="https://unpkg.com/idiomorph@0.7.3"></script>` };\n',
        encoding="utf-8",
    )
    (test_util_dir / "helper.js").write_text(
        """export function assertTextContentIs(el, expected) {
  if (el !== expected) throw new Error("Mismatch");
}
""",
        encoding="utf-8",
    )
    (test_unit_dir / "morph.js").write_text(
        """describe("htmx morph unit tests", () => {
  it("parses HCON and verifies state", () => {
    const res = htmx.ajax("GET", "/items");
    assertTextContentIs(String(Boolean(res)), "true");
  });
});
""",
        encoding="utf-8",
    )
    (test_attr_dir / "hx-get.js").write_text(
        """describe("hx-get attribute", () => {
  it("checks GET request handling", () => {
    htmx.ajax("GET", "/test");
    verifyRequest("/test");
  });
});
""",
        encoding="utf-8",
    )

    pf = run_project_inspect(htmx_dir, lang="javascript")
    assert pf.has_type_marker is True
    assert pf.source_files_count == 1
    assert pf.test_files_count == 2

    ast_facts = run_ast_analyze(htmx_dir, lang="javascript")
    assert ast_facts.total_classes == 3
    assert ast_facts.total_functions == 3
    assert ast_facts.type_safety_coverage_pct == 100.0
    assert "HtmxConfig" in ast_facts.module_inventory[0].public_types
    assert "Htmx.ajax" in ast_facts.module_inventory[0].public_callables
    assert ast_facts.test_functions_count == 2
    assert ast_facts.assertion_free_tests == []
    assert ast_facts.module_test_coverage_pct == 100.0
    assert any("External CDN" in note for note in ast_facts.test_harness_notes)

    # Task 4: Playwright auto-install in Dockerfile, lcov.info parser, WTR/Mocha test parser
    df_path, _ = ensure_target_dockerfile(htmx_dir, ".", "javascript", "node")
    df_text = df_path.read_text(encoding="utf-8")
    assert "PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in df_text
    assert "playwright install --with-deps chromium" in df_text

    wtr_out = tmp_path / "wtr.txt"
    wtr_out.write_text("Chrome: |████████████████████| 18/18 test files | 256 passed, 2 skipped\n", encoding="utf-8")
    assert parse_node_test_output(wtr_out)[:5] == (258, 256, 0, 0, 2)

    mocha_out = tmp_path / "mocha.txt"
    mocha_out.write_text("  256 passing (4s)\n  1 pending\n  2 failing\n", encoding="utf-8")
    assert parse_node_test_output(mocha_out)[:5] == (259, 256, 2, 0, 1)

    lcov_file = tmp_path / "lcov.info"
    lcov_file.write_text(
        """TN:
SF:/workspace/src/htmx.js
DA:1,1
DA:2,1
DA:3,0
LF:3
LH:2
BRDA:2,0,0,1
BRDA:2,0,1,0
BRF:2
BRH:1
end_of_record
""",
        encoding="utf-8",
    )
    lcov_cov = parse_lcov_info(lcov_file)
    assert lcov_cov.measured is True
    assert lcov_cov.tool == "lcov"
    assert lcov_cov.total_statements == 3
    assert lcov_cov.covered_lines == 2
    assert lcov_cov.line_coverage_pct == 66.7
    assert lcov_cov.branch_coverage_pct == 50.0
    assert lcov_cov.lowest_covered_modules[0].file_path == "src/htmx.js"

    # Task 5: Drawlib report guide + lint_drawlib_chapters ClassDiagram Styles.White warning
    guide = render_drawlib_report_guide(
        target="full_audit",
        score_path=".pni/cache/score/full_audit.json",
        facts_path=".pni/cache/facts/full_audit.json",
        target_root=".",
        source_targets=["src"],
        doc_targets=["README.md"],
    )
    assert "Styles.Neutral" in guide
    assert "--link-check-root" in guide

    ch_dir = tmp_path / "chapters"
    ch_dir.mkdir()
    bad_ch = ch_dir / "01_uml.md"
    bad_ch.write_text(
        """# UML
```drawlib
from drawlib.v0_2.apis import *
d = ClassDiagram(style=Styles.White)
```
""",
        encoding="utf-8",
    )
    warnings = lint_drawlib_chapters([bad_ch])
    assert any("Styles.White" in w for w in warnings)


