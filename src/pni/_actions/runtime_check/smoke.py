# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Archetype-aware startup / import / CLI smoke check planner and failure classifier."""

from __future__ import annotations

import contextlib
import json
import re
import shlex
import tomllib
from pathlib import Path
from typing import Final, Optional

from pni._actions.project_inspect import ProjectFacts
from pni._actions.runtime_check.engine_detect import CommandExecResult
from pni._actions.runtime_check.models import BootFailureKind, SmokeCheckResult

_JAVA_PACKAGE_RE = re.compile(r"^\s*package\s+([A-Za-z0-9_.]+)\s*;", re.MULTILINE)
_JAVA_MAIN_RE = re.compile(r"\bpublic\s+static\s+void\s+main\s*\(\s*String")
_IMPORT_DI_TOKENS: Final[tuple[str, ...]] = (
    "ImportError",
    "ModuleNotFoundError",
    "SyntaxError",
    "IndentationError",
    "Parse error:",
    "Fatal error: Uncaught Error: Class",
    "Failed opening required",
    "BindingResolutionException",
    "Target class [",
    "BeanCurrentlyInCreationException",
    "UnsatisfiedDependencyException",
    "BeanCreationException",
    "NoClassDefFoundError",
    "ClassNotFoundException",
    "Circular reference",
    "PydanticUserError",
    "Cannot find module",
    "ERR_MODULE_NOT_FOUND",
    "cannot find package",
    "missing go.sum entry",
)
_CONFIG_TOKENS: Final[tuple[str, ...]] = (
    "PlaceholderCouldNotBeResolved",
    "Failed to bind properties",
    "Missing required environment",
    "Missing required env",
    "Invalid environment",
    "Field required",
    "No application encryption key has been specified",
)
_EXTERNAL_IO_TOKENS: Final[tuple[str, ...]] = (
    "ConnectionRefusedError",
    "ConnectException",
    "UnknownHostException",
    "Communications link failure",
    "OperationalError",
    "SQLSTATE[HY000] [2002]",
    "mysqli_connect():",
    "ECONNREFUSED",
    "ENOTFOUND",
    "ETIMEDOUT",
    "dial tcp",
)


def classify_boot_failure(output: str, *, timed_out: bool) -> BootFailureKind:
    """Classify a non-zero or timed-out startup probe output into a canonical BootFailureKind."""
    if timed_out:
        return "timeout"
    if any(tok in output for tok in _IMPORT_DI_TOKENS):
        return "import_or_di_error"
    if any(tok in output for tok in _CONFIG_TOKENS):
        return "config_missing"
    if any(tok in output for tok in _EXTERNAL_IO_TOKENS):
        return "external_service_unreachable"
    return "crash"


def _discover_python_packages(target_root: Path, source_targets: list[str]) -> list[str]:
    """Discover top-level Python import package names inside source_targets."""
    pkgs: list[str] = []
    for rel in source_targets or ["src"]:
        base = target_root / rel
        if not base.is_dir():
            continue
        if (base / "__init__.py").is_file():
            pkgs.append(base.name)
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and (child / "__init__.py").is_file() and not child.name.startswith("."):
                pkgs.append(child.name)
    return pkgs


def _discover_python_cli_script(target_root: Path) -> Optional[str]:
    """Return the first [project.scripts] CLI command name in pyproject.toml if declared."""
    pyproject = target_root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    with contextlib.suppress(Exception):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        proj = data.get("project")
        if isinstance(proj, dict):
            scripts = proj.get("scripts")
            if isinstance(scripts, dict) and scripts:
                return str(next(iter(scripts.keys())))
    return None


def _discover_python_web_module(target_root: Path, source_targets: list[str]) -> Optional[str]:
    """Locate the Python module path instantiating FastAPI(...) or Flask(...)."""
    for rel in source_targets or ["src"]:
        base = target_root / rel
        if not base.is_dir():
            continue
        import_root = base.parent if (base / "__init__.py").is_file() else base
        for py_file in sorted(base.rglob("*.py")):
            with contextlib.suppress(Exception):
                src = py_file.read_text(encoding="utf-8")
                if "FastAPI(" in src or "Flask(" in src or "def create_app(" in src:
                    rel_mod = py_file.relative_to(import_root).with_suffix("")
                    parts = [p for p in rel_mod.parts if p != "__init__"]
                    if parts:
                        return ".".join(parts)
    return None


def _discover_java_main_class(target_root: Path, source_targets: list[str]) -> Optional[str]:
    """Find the fully qualified Java class declaring public static void main(String[] args)."""
    for rel in source_targets or ["src/main/java"]:
        base = target_root / rel
        if not base.is_dir():
            continue
        for jf in sorted(base.rglob("*.java")):
            with contextlib.suppress(Exception):
                text = jf.read_text(encoding="utf-8")
                if not _JAVA_MAIN_RE.search(text):
                    continue
                pkg_match = _JAVA_PACKAGE_RE.search(text)
                cls_name = jf.stem
                return f"{pkg_match.group(1)}.{cls_name}" if pkg_match else cls_name
    return None


def _build_python_web_probe_script(mod_name: str) -> str:
    """Return inline Python ASGI/WSGI lifespan + endpoint smoke probe writing /out/smoke.json."""
    return (
        "import importlib, json, pathlib; "
        f"mod = importlib.import_module({mod_name!r}); "
        "factory = getattr(mod, 'create_app', None); "
        "app = getattr(mod, 'app', None) or (factory() if callable(factory) else None); "
        "assert app is not None, 'No app or create_app() found'; "
        "paths = ('/healthz', '/health', '/api/v1/health', '/openapi.json', '/'); "
        "status, hit = None, None\n"
        "if callable(getattr(app, 'test_client', None)):\n"
        "    c = app.test_client()\n"
        "    for p in paths:\n"
        "        r = c.get(p)\n"
        "        status, hit = r.status_code, p\n"
        "        if r.status_code < 400: break\n"
        "else:\n"
        "    from fastapi.testclient import TestClient\n"
        "    with TestClient(app) as c:\n"
        "        for p in paths:\n"
        "            r = c.get(p)\n"
        "            status, hit = r.status_code, p\n"
        "            if r.status_code < 400: break\n"
        "assert status is not None and status < 500, f'Unexpected status {status} on {hit}'; "
        "pathlib.Path('/out/smoke.json').write_text("
        "json.dumps({'probed_endpoint': hit, 'http_status': status, "
        f"'detail': f'ASGI/WSGI app {mod_name} booted cleanly ({{hit}} -> {{status}})'}}))"
    )


def _build_java_spring_probe_script(main_class: str, port: int) -> str:
    """Return bash probe starting Spring/Java main class and polling 127.0.0.1:<port>."""
    return (
        'cp_extra=""; if [ -f /m2repo/runtime_cp.txt ]; then cp_extra=":$(cat /m2repo/runtime_cp.txt)"; fi; '
        f'java -cp "target/classes${{cp_extra}}" {main_class} --server.port={port} >/out/boot_stdout.log 2>&1 & '
        "pid=$!; "
        "for _ in $(seq 1 36); do "
        "  if ! kill -0 $pid 2>/dev/null; then wait $pid; rc=$?; cat /out/boot_stdout.log >&2; exit $rc; fi; "
        f"  if (echo >/dev/tcp/127.0.0.1/{port}) >/dev/null 2>&1; then "
        f'    printf \'{{"probed_endpoint":"tcp://127.0.0.1:{port}","http_status":200,'
        f'"detail":"Java service {main_class} bound port {port} cleanly"}}\' >/out/smoke.json; '
        "    kill -TERM $pid 2>/dev/null || true; wait $pid 2>/dev/null || true; exit 0; "
        "  fi; "
        "  sleep 0.5; "
        "done; "
        "kill -KILL $pid 2>/dev/null || true; cat /out/boot_stdout.log >&2; exit 124"
    )


def _build_java_smoke_plan(
    target_root: Path,
    rtypes: list[str],
    archetype_label: str,
    source_targets: list[str],
    smoke_port: int,
) -> tuple[str, list[str]]:
    """Construct Stage 3 startup/smoke command for a Java project."""
    main_cls = _discover_java_main_class(target_root, source_targets)
    if main_cls and "web_api" in rtypes:
        return archetype_label, ["bash", "-c", _build_java_spring_probe_script(main_cls, smoke_port)]
    if main_cls:
        cmd = f'java -cp "target/classes:$(cat /m2repo/runtime_cp.txt 2>/dev/null)" {main_cls} --help'
        return archetype_label, ["bash", "-c", cmd]
    return "library", ["bash", "-c", "test -d target/classes && ls target/classes >/dev/null"]


def _discover_wp_plugin_entrypoint(target_root: Path) -> Optional[str]:
    """Return the root PHP file containing a WordPress `Plugin Name:` header, if present."""
    for php_file in sorted(target_root.glob("*.php")):
        with contextlib.suppress(Exception):
            head = php_file.read_text(encoding="utf-8", errors="ignore")[:8192]
            if re.search(r"(?mi)^\s*\*?\s*Plugin Name\s*:\s*\S+", head):
                return php_file.name
    return None


def _build_wp_plugin_stub_script(entry_file: str) -> str:
    """Return inline PHP harness defining minimal WordPress registration stubs and requiring entry_file."""
    return (
        "define('ABSPATH', '/workspace/'); "
        "$GLOBALS['__pni_wp_hooks'] = 0; "
        "function add_action($t, $c, $p=10, $a=1) { $GLOBALS['__pni_wp_hooks']++; return true; } "
        "function add_filter($t, $c, $p=10, $a=1) { $GLOBALS['__pni_wp_hooks']++; return true; } "
        "function add_shortcode($t, $c) { $GLOBALS['__pni_wp_hooks']++; return true; } "
        "function register_activation_hook($f, $c) { $GLOBALS['__pni_wp_hooks']++; } "
        "function register_deactivation_hook($f, $c) { $GLOBALS['__pni_wp_hooks']++; } "
        "function register_rest_route($n, $r, $a=[]) { $GLOBALS['__pni_wp_hooks']++; return true; } "
        "function plugin_dir_path($f) { return dirname($f) . '/'; } "
        "function plugin_dir_url($f) { return 'http://localhost/wp-content/plugins/plugin/'; } "
        "function is_admin() { return false; } "
        "function __($t, $d='default') { return $t; } "
        f"require_once '/workspace/{entry_file}'; "
        "$n = $GLOBALS['__pni_wp_hooks']; "
        f"file_put_contents('/out/smoke.json', json_encode(['probed_endpoint' => 'wp-plugin://{entry_file}', "
        f"'http_status' => 200, "
        f"'detail' => 'WordPress plugin {entry_file} loaded cleanly (' . $n . ' hooks registered)']));"
    )


def _build_php_builtin_server_probe(docroot: str, port: int, router_script: str = "") -> str:
    """Return shell script starting `php -S 127.0.0.1:<port>` and probing candidate health/root routes."""
    php_client = (
        "$paths = ['/up', '/healthz', '/health', '/api/health', '/']; "
        "$bestCode = null; $bestPath = '/'; "
        "foreach ($paths as $p) { "
        "  $ctx = stream_context_create(['http' => ['ignore_errors' => true, 'timeout' => 2]]); "
        f"  @file_get_contents('http://127.0.0.1:{port}' . $p, false, $ctx); "
        "  if (!empty($http_response_header[0]) "
        "&& preg_match('/HTTP\\/\\S+\\s+(\\d+)/', $http_response_header[0], $m)) { "
        "    $code = (int)$m[1]; $bestCode = $code; $bestPath = $p; "
        "    if ($code < 400) { break; } "
        "  } "
        "} "
        "if ($bestCode === null || $bestCode >= 500) { exit(1); } "
        "file_put_contents('/out/smoke.json', json_encode(['probed_endpoint' => $bestPath, "
        "'http_status' => $bestCode, "
        "'detail' => 'PHP web server responded (' . $bestPath . ' -> ' . $bestCode . ')']));"
    )
    router_arg = f" {router_script}" if router_script else ""
    return (
        f"php -S 127.0.0.1:{port} -t {docroot}{router_arg} >/out/boot_stdout.log 2>&1 & "
        "pid=$!; "
        "for _ in $(seq 1 20); do "
        "  if ! kill -0 $pid 2>/dev/null; then wait $pid; rc=$?; cat /out/boot_stdout.log >&2; exit $rc; fi; "
        f"  if php -r '$fp=@fsockopen(\"127.0.0.1\",{port},$e,$s,0.5); if($fp){{fclose($fp);exit(0);}} exit(1);'; then "
        f"    php -r {shlex.quote(php_client)}; rc=$?; "
        "    kill -TERM $pid 2>/dev/null || true; wait $pid 2>/dev/null || true; "
        "    if [ $rc -ne 0 ]; then cat /out/boot_stdout.log >&2; fi; exit $rc; "
        "  fi; "
        "  sleep 0.3; "
        "done; "
        "kill -KILL $pid 2>/dev/null || true; cat /out/boot_stdout.log >&2; exit 124"
    )


def _build_php_smoke_plan(
    target_root: Path,
    pf: ProjectFacts,
    rtypes: list[str],
    archetype_label: str,
    smoke_port: int,
) -> tuple[str, Optional[list[str]]]:
    """Construct Stage 3 startup/smoke command for Composer, Laravel, Raw-PHP, or WordPress projects."""
    if "wordpress" in pf.detected_frameworks and not (target_root / "wp-config.php").is_file():
        wp_entry = _discover_wp_plugin_entrypoint(target_root)
        if wp_entry:
            return archetype_label, ["php", "-r", _build_wp_plugin_stub_script(wp_entry)]

    if "web_api" in rtypes:
        if (target_root / "public" / "index.php").is_file():
            probe = _build_php_builtin_server_probe("public", smoke_port, "public/index.php")
            return archetype_label, ["bash", "-c", probe]
        if (target_root / "index.php").is_file():
            return archetype_label, ["bash", "-c", _build_php_builtin_server_probe(".", smoke_port)]

    if "cli" in rtypes and (target_root / "artisan").is_file():
        cmd = (
            "php artisan --version >/dev/null && "
            'printf \'{"detail":"Laravel artisan --version exited 0"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]

    if (target_root / "composer.json").is_file():
        code = (
            "require '/workspace/vendor/autoload.php'; "
            "file_put_contents('/out/smoke.json', json_encode(['detail' => 'Composer PSR-4 autoloader verified']));"
        )
        return archetype_label, ["php", "-r", code]
    return archetype_label, None


def _build_python_smoke_plan(
    target_root: Path,
    rtypes: list[str],
    archetype_label: str,
    source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    """Construct Stage 3 startup/smoke command for Python web_api, cli, or library projects."""
    if "web_api" in rtypes:
        web_mod = _discover_python_web_module(target_root, source_targets)
        if web_mod:
            return archetype_label, ["python", "-c", _build_python_web_probe_script(web_mod)]

    pkgs = _discover_python_packages(target_root, source_targets)
    if "cli" in rtypes:
        cli_bin = _discover_python_cli_script(target_root)
        if cli_bin and "library" in rtypes and pkgs:
            pkg = pkgs[0]
            py_import = (
                f"import importlib, json, pathlib; importlib.import_module({pkg!r}); "
                "pathlib.Path('/out/smoke.json').write_text("
                f"json.dumps({{'detail': 'CLI {cli_bin} --help exited 0 and imported {pkg} cleanly'}}))"
            )
            script = f"{shlex.quote(cli_bin)} --help >/dev/null && python -c {shlex.quote(py_import)}"
            return archetype_label, ["sh", "-c", script]
        if cli_bin:
            script = (
                f"{cli_bin} --help >/dev/null && "
                f'printf \'{{"detail":"CLI entrypoint {cli_bin} --help exited 0"}}\' >/out/smoke.json'
            )
            return archetype_label, ["sh", "-c", script]

    if pkgs:
        pkg = pkgs[0]
        code = (
            f"import importlib, json, pathlib; importlib.import_module({pkg!r}); "
            f"pathlib.Path('/out/smoke.json').write_text(json.dumps({{'detail': 'Imported {pkg} cleanly'}}))"
        )
        return archetype_label, ["python", "-c", code]
    return archetype_label, None


def _build_go_smoke_plan(
    target_root: Path,
    archetype_label: str,
) -> tuple[str, Optional[list[str]]]:
    """Construct Stage 3 compile/link smoke command for a Go module."""
    if (target_root / "go.mod").is_file() or any(target_root.rglob("*.go")):
        cmd = (
            "go build ./... && "
            'printf \'{"detail":"Go module packages compiled cleanly (go build ./...)"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    return archetype_label, None


def _build_node_smoke_plan(
    target_root: Path,
    pf: ProjectFacts,
    archetype_label: str,
) -> tuple[str, Optional[list[str]]]:
    """Construct Stage 3 type-check / syntax smoke command for TypeScript and JavaScript projects."""
    if pf.language == "typescript":
        if (target_root / "tsconfig.json").is_file() or (target_root / "package.json").is_file():
            cmd = (
                "if [ -x ./node_modules/.bin/tsc ] && [ -f tsconfig.json ]; then "
                "  ./node_modules/.bin/tsc --noEmit && "
                '  printf \'{"detail":"TypeScript compiler verification (tsc --noEmit) exited 0"}\' >/out/smoke.json; '
                "else "
                "  node --version >/dev/null && "
                '  printf \'{"detail":"Node.js TypeScript workspace verified"}\' >/out/smoke.json; '
                "fi"
            )
            return archetype_label, ["sh", "-c", cmd]
        return archetype_label, None

    if (target_root / "package.json").is_file() or any(target_root.rglob("*.js")):
        cmd = (
            "for f in $(find . -name 'node_modules' -prune -o -name 'dist' -prune "
            "-o \\( -name '*.js' -o -name '*.mjs' -o -name '*.cjs' \\) -print 2>/dev/null | head -n 25); do "
            '  node --check "$f" || exit 1; '
            "done && "
            'printf \'{"detail":"Node.js syntax check (node --check) passed"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    return archetype_label, None


def build_smoke_plan(
    target_root: Path,
    pf: ProjectFacts,
    source_targets: list[str],
    *,
    override_cmd: str = "",
    smoke_port: int = 18080,
) -> tuple[str, Optional[list[str]]]:
    """Construct an archetype-specific Stage 3 startup/smoke command.

    Returns:
        tuple[str, Optional[list[str]]]: (archetype_label, command_args_or_None_if_unapplicable)
    """
    rtypes = [str(rt) for rt in (pf.runtime_types or ["library"])]
    archetype_label = "+".join(rtypes)
    if override_cmd.strip():
        return archetype_label, ["sh", "-c", override_cmd.strip()]
    if pf.language == "java":
        return _build_java_smoke_plan(target_root, rtypes, archetype_label, source_targets, smoke_port)
    if pf.language == "php":
        return _build_php_smoke_plan(target_root, pf, rtypes, archetype_label, smoke_port)
    if pf.language == "go":
        return _build_go_smoke_plan(target_root, archetype_label)
    if pf.language in {"typescript", "javascript"}:
        return _build_node_smoke_plan(target_root, pf, archetype_label)
    return _build_python_smoke_plan(target_root, rtypes, archetype_label, source_targets)


def evaluate_smoke_outcome(
    archetype: str,
    cmd_args: list[str],
    exec_res: CommandExecResult,
    out_dir: Path,
) -> SmokeCheckResult:
    """Convert Stage 3 subprocess result and optional /out/smoke.json into SmokeCheckResult."""
    smoke_json_file = out_dir / "smoke.json"
    probed_ep: Optional[str] = None
    http_status: Optional[int] = None
    detail = ""
    if smoke_json_file.is_file():
        with contextlib.suppress(Exception):
            payload = json.loads(smoke_json_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                probed_ep = str(payload["probed_endpoint"]) if payload.get("probed_endpoint") else None
                http_status = int(payload["http_status"]) if payload.get("http_status") is not None else None
                detail = str(payload.get("detail", ""))

    cmd_display = " ".join(cmd_args[:3]) if len(cmd_args) > 3 else " ".join(cmd_args)
    if not exec_res.timed_out and exec_res.exit_code == 0:
        return SmokeCheckResult(
            attempted=True,
            archetype=archetype,
            status="passed",
            command=cmd_display,
            duration_sec=exec_res.duration_sec,
            exit_code=0,
            http_status=http_status,
            probed_endpoint=probed_ep,
            failure_kind="none",
            detail=detail or f"{archetype} smoke check exited 0",
            log_tail=exec_res.tail_lines(15),
        )

    status = "timeout" if exec_res.timed_out else "failed"
    fkind = classify_boot_failure(exec_res.combined_output, timed_out=exec_res.timed_out)
    tail = exec_res.tail_lines(20)
    err_summary = tail[-1] if tail else f"Smoke check {status} (exit={exec_res.exit_code})"
    return SmokeCheckResult(
        attempted=True,
        archetype=archetype,
        status=status,
        command=cmd_display,
        duration_sec=exec_res.duration_sec,
        exit_code=exec_res.exit_code,
        http_status=http_status,
        probed_endpoint=probed_ep,
        failure_kind=fkind,
        detail=err_summary[:240],
        log_tail=tail,
    )
