# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tests for Go language support across project_inspect, ast_analyze, runtime_check, pentest, and migration."""

from __future__ import annotations

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
from pni._actions.runtime_check.parsers import parse_go_coverprofile, parse_go_test_output
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_go_image_version,
    select_harness_tool,
)
from pni._actions.runtime_check.smoke import build_smoke_plan
from pni._dockerfiles import ensure_target_dockerfile
from pni._rules.manager import detect_active_language
from pni._workflows import load_workflow
from pni.cli import init_project


def test_go_project_inspect_and_archetypes(tmp_path: Path) -> None:
    """Inspect a Go module repository, verifying go.mod parsing, framework detection, and test separation."""
    (tmp_path / "go.mod").write_text(
        """module github.com/acme/order-svc

go 1.22

require (
\tgithub.com/gin-gonic/gin v1.10.0
\tgithub.com/spf13/cobra v1.8.1
\tgithub.com/acme/experimental v0.0.0
)
""",
        encoding="utf-8",
    )
    (tmp_path / "go.sum").write_text("github.com/gin-gonic/gin v1.10.0 h1:abc=\n", encoding="utf-8")
    (tmp_path / ".golangci.yml").write_text("linters:\n  enable:\n    - govet\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Order Service\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("/bin/\n/vendor/\n", encoding="utf-8")

    cmd_dir = tmp_path / "cmd" / "server"
    cmd_dir.mkdir(parents=True)
    (cmd_dir / "main.go").write_text(
        "package main\nfunc main() {}\n",
        encoding="utf-8",
    )

    pkg_dir = tmp_path / "pkg" / "order"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "service.go").write_text(
        "package order\nfunc CreateOrder() string { return \"ok\" }\n",
        encoding="utf-8",
    )
    (pkg_dir / "service_test.go").write_text(
        "package order\nimport \"testing\"\nfunc TestCreateOrder(t *testing.T) {}\n",
        encoding="utf-8",
    )

    # Vendor directory files must never be counted as application source or test files
    vendor_dir = tmp_path / "vendor" / "github.com" / "gin-gonic" / "gin"
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "gin.go").write_text("package gin\n", encoding="utf-8")
    (vendor_dir / "gin_test.go").write_text("package gin\n", encoding="utf-8")

    assert detect_active_language(tmp_path) == "go"
    facts = run_project_inspect(tmp_path)
    assert facts.language == "go"
    assert facts.build_system == "go_mod"
    assert facts.project_name == "order-svc"
    assert facts.language_version_constraint == "1.22"
    assert "go.sum" in facts.lockfiles_found
    assert "gin" in facts.detected_frameworks
    assert "cobra" in facts.detected_frameworks
    assert any("github.com/acme/experimental" in u for u in facts.unpinned_dependencies)
    assert facts.source_files_count == 2
    assert facts.test_files_count == 1
    assert facts.tooling_modernization_issues == []
    assert "web_api" in facts.runtime_types
    assert "cli" in facts.runtime_types


def test_go_ast_clean_service_and_tests(tmp_path: Path) -> None:
    """Verify clean idiomatic Go code with doc comments and table-driven tests achieves top AST metrics."""
    (tmp_path / "go.mod").write_text(
        "module github.com/acme/clean-go\n\ngo 1.22\n\nrequire github.com/stretchr/testify v1.9.0\n",
        encoding="utf-8",
    )
    pkg_dir = tmp_path / "internal" / "billing"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "calculator.go").write_text(
        """package billing

import (
\t"context"
\t"errors"
)

// Invoice represents an immutable billing invoice.
type Invoice struct {
\tAmountCents int64
}

// ComputeTotal calculates the total invoice amount with tax.
func ComputeTotal(ctx context.Context, inv Invoice, taxRateBps int64) (int64, error) {
\tif inv.AmountCents < 0 {
\t\treturn 0, errors.New("negative amount")
\t}
\t_ = ctx
\treturn inv.AmountCents + (inv.AmountCents*taxRateBps)/10000, nil
}
""",
        encoding="utf-8",
    )
    (pkg_dir / "calculator_test.go").write_text(
        """package billing

import (
\t"context"
\t"testing"

\t"github.com/stretchr/testify/require"
)

func TestComputeTotal(t *testing.T) {
\tcases := []struct {
\t\tname string
\t\tamt  int64
\t\twant int64
\t}{
\t\t{name: "basic", amt: 1000, want: 1100},
\t\t{name: "zero", amt: 0, want: 0},
\t}
\tfor _, tc := range cases {
\t\tt.Run(tc.name, func(t *testing.T) {
\t\t\tgot, err := ComputeTotal(context.Background(), Invoice{AmountCents: tc.amt}, 1000)
\t\t\trequire.NoError(t, err)
\t\t\trequire.Equal(t, tc.want, got)
\t\t})
\t}
}
""",
        encoding="utf-8",
    )

    ast_facts = run_ast_analyze(tmp_path, lang="go")
    assert ast_facts.language == "go"
    assert ast_facts.total_files == 1
    assert ast_facts.total_functions == 1
    assert ast_facts.type_safety_coverage_pct == 100.0
    assert ast_facts.docstring_coverage_pct == 100.0
    assert ast_facts.bug_risk_idioms == []
    assert ast_facts.type_safety_issues == []
    assert ast_facts.dangerous_sinks == []
    assert ast_facts.framework_issues == []
    assert ast_facts.test_functions_count >= 1
    assert ast_facts.assertion_free_tests == []


def test_go_ast_smells_security_and_frameworks(tmp_path: Path) -> None:
    """Detect Go AST smells, CWE security sinks, Gin/HTTP framework issues, and version mismatches."""
    (tmp_path / "go.mod").write_text(
        "module github.com/acme/legacy-go\n\ngo 1.19\n\nrequire github.com/gin-gonic/gin v1.10.0\n",
        encoding="utf-8",
    )
    (tmp_path / "handler.go").write_text(
        """package handler

import (
\t"crypto/md5"
\t"crypto/tls"
\t"database/sql"
\t"fmt"
\t"log/slog"
\t"math/rand"
\t"net/http"
\t"os/exec"
\t. "strings"
\t"unsafe"

\t"github.com/gin-gonic/gin"
\t"github.com/undeclared/pkg"
)

var globalState = map[string]string{}

func init() {
\tglobalState["boot"] = "1"
}

func ExportedWithoutDoc(c *gin.Context, db *sql.DB, raw interface{}) any {
\tvar payload map[string]any
\tc.BindJSON(&payload)
\tuser := TrimSpace(c.Query("user"))
\t_ = db.QueryRow("SELECT * FROM users WHERE name = '" + user + "'")
\t_ = exec.Command("sh", "-c", user).Run()
\t_ = &tls.Config{InsecureSkipVerify: true}
\t_ = md5.New()
\t_ = rand.Intn(100)
\t_ = unsafe.Pointer(&payload)
\t_ = pkg.Call()
\tfmt.Println("debug log")
\tslog.Info("using go 1.21 slog in go 1.19 module")
\tgo func() {
\t\tresp, _ := http.Get("https://example.com/" + user)
\t\t_ = resp
\t}()
\tif user == "panic" {
\t\tpanic("unexpected panic in handler")
\t}
\treturn payload
}

func startServer() {
\tr := gin.Default()
\tr.GET("/api/v1/users", func(c *gin.Context) {})
\t_ = http.ListenAndServe(":8080", r)
}
""",
        encoding="utf-8",
    )
    (tmp_path / "handler_test.go").write_text(
        """package handler

import (
\t"testing"
\t"time"
)

func TestNoAssertionsAndSleep(t *testing.T) {
\ttime.Sleep(10 * time.Millisecond)
}
""",
        encoding="utf-8",
    )

    facts = run_ast_analyze(tmp_path, lang="go")
    assert len(facts.wildcard_imports) == 1
    assert len(facts.bug_risk_idioms) >= 1
    assert len(facts.weak_type_usages) >= 1
    assert len(facts.type_safety_issues) >= 1
    assert len(facts.missing_docstrings) >= 1
    assert len(facts.undeclared_dependencies) == 1
    assert facts.undeclared_dependencies[0].symbol == "github.com/undeclared/pkg"
    assert len(facts.global_state_usages) >= 1
    assert len(facts.unstructured_logging) >= 1
    assert len(facts.missing_io_timeouts) >= 1
    assert len(facts.dangerous_sinks) >= 4
    assert any(ep.path == "/api/v1/users" and ep.http_method == "GET" for ep in facts.api_endpoints)
    assert len(facts.framework_issues) >= 1
    assert len(facts.modernization_hints) >= 1
    assert len(facts.language_version_mismatches) >= 1
    assert len(facts.assertion_free_tests) == 1
    assert any("time.Sleep" in note for note in facts.test_harness_notes)


def test_go_runtime_selector_parsers_smoke_and_scaffolding(tmp_path: Path) -> None:
    """Verify Go runtime selectors, test/coverprofile parsers, smoke plan, pentest plan, and CLI init."""
    assert select_go_image_version(None) == "1.22"
    assert select_go_image_version("1.15") == "1.22"
    assert select_go_image_version(">=1.21, <1.22") == "1.22"
    assert select_go_image_version(">=1.23") == "1.23"
    assert select_go_image_version(">=1.24") == "1.24"

    (tmp_path / "go.mod").write_text("module github.com/acme/svc\n\ngo 1.23\n", encoding="utf-8")
    (tmp_path / "main.go").write_text(
        """package main

import (
\t"database/sql"
\t"net/http"
\t"os"
)

func handler(w http.ResponseWriter, r *http.Request) {
\torderID := r.URL.Query().Get("order_id")
\tapiKey := os.Getenv("PAYMENT_API_KEY")
\t_, _ = sql.Open("postgres", apiKey)
\t_, _ = http.Get("https://api.example.com/" + orderID)
}

func main() {
\thttp.HandleFunc("/orders", handler)
}
""",
        encoding="utf-8",
    )

    pf = run_project_inspect(tmp_path, lang="go")
    tool = select_harness_tool(pf)
    assert tool == "go"
    build_args = compute_harness_build_args(pf)
    assert build_args == {"GO_VERSION": "1.23"}

    cmd = build_test_and_coverage_command(pf, tool, ["."], ["."])
    assert "go vet ./..." in cmd[2]
    assert "go test -v -coverprofile=/out/coverage.out ./..." in cmd[2]

    archetype, smoke_cmd = build_smoke_plan(tmp_path, pf, ["."])
    assert smoke_cmd is not None
    assert "go build ./..." in smoke_cmd[2]

    ast_facts = run_ast_analyze(tmp_path, lang="go")
    live_cmd, reason = build_live_server_plan(tmp_path, pf, ["."], ast_facts=ast_facts, container_port=18080)
    assert reason == ""
    assert live_cmd is not None
    assert "go run ." in live_cmd[2]

    # Parse `go test -v` output and Go coverprofile
    go_test_file = tmp_path / "go_test.txt"
    go_test_file.write_text(
        """=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
=== RUN   TestSub
--- FAIL: TestSub (0.01s)
=== RUN   TestSkip
--- SKIP: TestSkip (0.00s)
FAIL
""",
        encoding="utf-8",
    )
    total, passed, failed, errors, skipped, failures = parse_go_test_output(go_test_file)
    assert (total, passed, failed, errors, skipped) == (3, 1, 1, 0, 1)
    assert len(failures) == 1
    assert failures[0].name == "TestSub"

    cover_file = tmp_path / "coverage.out"
    cover_file.write_text(
        """mode: set
github.com/acme/svc/main.go:10.2,14.16 4 1
github.com/acme/svc/main.go:15.2,18.10 2 0
""",
        encoding="utf-8",
    )
    cov = parse_go_coverprofile(cover_file, module_prefix="github.com/acme/svc")
    assert cov.measured is True
    assert cov.tool == "go-cover"
    assert cov.covered_lines == 4
    assert cov.total_statements == 6
    assert cov.line_coverage_pct == 66.7
    assert cov.lowest_covered_modules[0].file_path == "main.go"
    assert cov.lowest_covered_modules[0].missing_lines_preview == [15]

    # Migration touchpoints, contracts, and codemods
    src_map = {"main.go": (tmp_path / "main.go").read_text(encoding="utf-8")}
    touchpoints = extract_boundary_touchpoints(src_map, "go", ast_facts)
    assert any(tp.kind == "persistence_db" for tp in touchpoints)
    assert any(tp.kind == "external_http_rpc" for tp in touchpoints)

    implicit_contracts, env_contracts = extract_implicit_and_env_contracts(src_map, "go", ast_facts)
    assert len(implicit_contracts) == 1
    assert implicit_contracts[0].input_fields[0].key == "order_id"
    assert any(e.name == "PAYMENT_API_KEY" for e in env_contracts)

    recipes = match_codemod_recipes("go", MigrationOptions(), "Upgrade Go service", ast_facts)
    assert len(recipes) == 1
    assert recipes[0].tool == "gofix"

    # Scaffolding & workflow loading
    init_project(tmp_path, lang="go")
    assert any(a.id == "go_ast_audit" for a in list_actions(tmp_path))
    action_def = load_composite_action("go_ast_audit", tmp_path)
    assert action_def is not None
    assert action_def.id == "go_ast_audit"
    wf = load_workflow("full_audit", tmp_path)
    assert wf is not None
    assert wf[0].id == "full_audit"
    df_path, template_id = ensure_target_dockerfile(tmp_path, ".", "go", "go")
    assert df_path.is_file()
    assert template_id == "go/go.dockerfile"
    df_text = df_path.read_text(encoding="utf-8")
    assert "USER pni" in df_text
    assert "chmod -R a+rwX /workspace /go /out" in df_text


def test_go_cobra_idioms_and_init_scaffolding(tmp_path: Path) -> None:
    """Verify Go AST false-positive fixes (t.Run delegation, chained blank discard, raw string LOC, Printf variadic)."""
    (tmp_path / "go.mod").write_text("module github.com/spf13/cobra\n\ngo 1.15\n", encoding="utf-8")
    # Even if a docs requirements.txt exists, go.mod must take precedence as a Go repository
    (tmp_path / "requirements.txt").write_text("mkdocs>=1.5.0\n", encoding="utf-8")

    raw_lines = "\n".join(f"# bash completion line {i}" for i in range(70))
    (tmp_path / "command.go").write_text(
        f"""package cobra

import "fmt"

// FlagSet holds command flags.
type FlagSet struct{{}}

// MarkHidden marks a flag hidden.
func (f *FlagSet) MarkHidden(name string) error {{
\treturn nil
}}

// GetString returns a flag value and error.
func (f *FlagSet) GetString(name string) (string, error) {{
\treturn name, nil
}}

// Command represents a CLI command.
type Command struct{{}}

// Flags returns the command FlagSet.
func (c *Command) Flags() *FlagSet {{
\treturn &FlagSet{{}}
}}

// Printf formats and prints output using fmt-compatible variadic arguments.
func (c *Command) Printf(format string, i ...interface{{}}) {{
\tfmt.Printf(format, i...)
}}

// Println prints output using fmt-compatible variadic arguments.
func (c *Command) Println(i ...any) {{
\tfmt.Println(i...)
}}

// Configure sets up flags and reads a value with partial blank error discard.
func (c *Command) Configure() string {{
\t_ = c.Flags().MarkHidden("secret")
\tval, _ := c.Flags().GetString("name")
\treturn val
}}

// GenBashComp returns a long multiline raw string template with minimal branching.
func GenBashComp(includeDesc bool) string {{
\tif includeDesc {{
\t\treturn `{raw_lines}`
\t}}
\treturn ""
}}
""",
        encoding="utf-8",
    )
    (tmp_path / "command_test.go").write_text(
        """package cobra

import "testing"

type calledAsTestcase struct {
\twant string
}

func (tc calledAsTestcase) test(t *testing.T) {
\tif tc.want == "" {
\t\tt.Errorf("unexpected empty want")
\t}
}

func assertEqual(t *testing.T, got, want string) {
\tif got != want {
\t\tt.Fatalf("got %q, want %q", got, want)
\t}
}

func TestCalledAsMethodValue(t *testing.T) {
\ttests := map[string]calledAsTestcase{"ok": {want: "run"}}
\tfor name, tc := range tests {
\t\tt.Run(name, tc.test)
\t}
}

func TestDelegatedHelperArg(t *testing.T) {
\tc := &Command{}
\tassertEqual(t, c.Configure(), "name")
}
""",
        encoding="utf-8",
    )

    assert detect_active_language(tmp_path) == "go"
    init_project(tmp_path)
    toml_text = (tmp_path / ".pni" / "pni.toml").read_text(encoding="utf-8")
    assert 'source = ["."]' in toml_text
    assert 'tests = ["."]' in toml_text
    assert 'include_gitignored = ["go.sum"]' in toml_text
    assert '"docs/**"' in toml_text

    facts = run_ast_analyze(tmp_path, targets=["."], test_targets=["."], lang="go")
    assert facts.assertion_free_tests == []
    assert facts.complex_functions == []
    assert facts.weak_type_usages == []
    assert facts.type_safety_coverage_pct == 100.0
    assert len(facts.bug_risk_idioms) == 1
    assert "c.Flags().GetString" in facts.bug_risk_idioms[0].detail
    assert "c.Flags(...)" not in facts.bug_risk_idioms[0].detail
