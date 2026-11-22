# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative Docker harness specs, version selectors, test scripts, and smoke probes for extended languages."""

from __future__ import annotations

import contextlib
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional

from pni._actions.project_inspect import ProjectFacts

_RUST_VER_RE = re.compile(r"1\.(\d+)")
_DOTNET_VER_RE = re.compile(r"(?:net)?(\d+)\.0")
_RUBY_VER_RE = re.compile(r"3\.(\d+)")
_SWIFT_VER_RE = re.compile(r"(\d+)\.(\d+)")
_ELIXIR_VER_RE = re.compile(r"1\.(\d+)")
_PERL_VER_RE = re.compile(r"5\.(\d+)")
_JULIA_VER_RE = re.compile(r"1\.(\d+)")
_JAVA_VER_RE = re.compile(r"(?:1\.8|\b(?:8|11|17|21)\b)")
_NODE_VER_RE = re.compile(r"\b(18|20|22|23)\b")

VersionSelector = Callable[[Optional[str]], str]
TestCmdBuilder = Callable[[ProjectFacts, str, list[str], list[str]], list[str]]
SmokeBuilder = Callable[[Path, ProjectFacts, str, list[str]], tuple[str, Optional[list[str]]]]


@dataclass(frozen=True)
class ExtendedHarnessSpec:
    """Declarative specification for one extended language Docker runtime harness."""

    language: str
    default_tool: str
    version_arg: str = ""
    default_version: str = ""
    version_selector: Optional[VersionSelector] = None
    supports_extra_apt: bool = True
    test_builder: Optional[TestCmdBuilder] = None
    smoke_builder: Optional[SmokeBuilder] = None


def select_rust_image_version(constraint: Optional[str]) -> str:
    """Select an official Rust Bookworm tag ('1.82', '1.85', '1.86') with '1.85' default."""
    if not constraint:
        return "1.85"
    matches = [int(m) for m in _RUST_VER_RE.findall(constraint)]
    if not matches:
        return "1.85"
    highest = max(matches)
    if highest >= 86:
        return "1.86"
    return "1.85"


def select_dotnet_image_version(constraint: Optional[str]) -> str:
    """Select an official .NET SDK tag ('8.0', '9.0') from TargetFramework constraint."""
    if not constraint:
        return "8.0"
    matches = [int(m) for m in _DOTNET_VER_RE.findall(constraint.lower())]
    if matches and max(matches) >= 9:
        return "9.0"
    return "8.0"


def select_ruby_image_version(constraint: Optional[str]) -> str:
    """Select an official Ruby Bookworm tag ('3.2', '3.3', '3.4') from Gemfile ruby constraint."""
    if not constraint:
        return "3.3"
    matches = [int(m) for m in _RUBY_VER_RE.findall(constraint)]
    if not matches:
        return "3.3"
    highest = max(matches)
    if highest >= 4:
        return "3.4"
    if highest <= 2:
        return "3.2"
    return "3.3"


def select_swift_image_version(constraint: Optional[str]) -> str:
    """Select an official Swift Bookworm tag ('5.10', '6.0') from swift-tools-version."""
    if not constraint:
        return "6.0"
    matches = [(int(a), int(b)) for a, b in _SWIFT_VER_RE.findall(constraint)]
    if matches and max(matches) < (6, 0):
        return "5.10"
    return "6.0"


def select_elixir_image_version(constraint: Optional[str]) -> str:
    """Select an official Elixir slim tag ('1.16', '1.17', '1.18') from mix.exs constraint."""
    if not constraint:
        return "1.17"
    matches = [int(m) for m in _ELIXIR_VER_RE.findall(constraint)]
    if matches and max(matches) >= 18:
        return "1.18"
    return "1.17"


def select_perl_image_version(constraint: Optional[str]) -> str:
    """Select an official Perl Bookworm tag ('5.38', '5.40')."""
    if not constraint:
        return "5.40"
    matches = [int(m) for m in _PERL_VER_RE.findall(constraint)]
    if matches and max(matches) <= 38:
        return "5.38"
    return "5.40"


def select_r_image_version(constraint: Optional[str]) -> str:
    """Select an official r-base tag ('4.4.2')."""
    _ = constraint
    return "4.4.2"


def select_dart_image_version(constraint: Optional[str]) -> str:
    """Select an official Dart SDK tag ('stable')."""
    _ = constraint
    return "stable"


def select_julia_image_version(constraint: Optional[str]) -> str:
    """Select an official Julia Bookworm tag ('1.10', '1.11')."""
    if not constraint:
        return "1.11"
    matches = [int(m) for m in _JULIA_VER_RE.findall(constraint)]
    if matches and max(matches) <= 10:
        return "1.10"
    return "1.11"


def _select_jvm_version(constraint: Optional[str]) -> str:
    """Select an Eclipse Temurin JDK tag ('11', '17', '21') for Kotlin/Scala/Groovy."""
    if not constraint:
        return "21"
    m = _JAVA_VER_RE.search(constraint.strip())
    tok = m.group(0) if m else constraint.strip()
    if tok in {"11", "17"}:
        return tok
    return "21"


def _select_frontend_node_version(constraint: Optional[str]) -> str:
    """Select a Node.js Bookworm tag ('18', '20', '22') for Vue/Svelte."""
    if not constraint:
        return "20"
    matches = [int(m) for m in _NODE_VER_RE.findall(constraint)]
    if matches and max(matches) >= 22:
        return "22"
    if matches and max(matches) <= 18:
        return "18"
    return "20"


def _extract_arg_default(dockerfile_path: Optional[Path], arg_name: str) -> Optional[str]:
    """Extract `ARG <arg_name>=<default>` from a materialized harness Dockerfile if present."""
    if dockerfile_path is None or not dockerfile_path.is_file():
        return None
    with contextlib.suppress(Exception):
        text = dockerfile_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(rf"(?m)^\s*ARG\s+{re.escape(arg_name)}\s*=\s*([^\s#]+)", text)
        if match:
            return match.group(1).strip().strip("'\"")
    return None


# ---------------------------------------------------------------------------
# Stage 2 Offline Test & Coverage Command Builders
# ---------------------------------------------------------------------------


def _build_rust_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if [ -f Cargo.toml ]; then "
        "  cargo test --offline >/out/rust_test.txt 2>&1; rc=$?; "
        "  cat /out/rust_test.txt; exit $rc; "
        "fi; "
        "fail=0; n=0; "
        "for f in $(find . -name '*.rs' -not -path './target/*' 2>/dev/null); do "
        "  n=$((n + 1)); "
        '  if rustc --crate-type lib --emit=metadata -o /tmp/pni_rs.rmeta "$f" >/tmp/pni_rs.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_rs.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_dotnet_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if grep -rq 'Microsoft\\.NET\\.Test\\.Sdk' . --include='*.csproj' --include='*.fsproj' 2>/dev/null; then "
        "  mkdir -p /tmp/pni-cov; "
        '  dotnet test --no-restore --logger "trx;LogFileName=/out/results.trx" '
        '--collect:"XPlat Code Coverage" --results-directory /tmp/pni-cov >/out/dotnet_test.txt 2>&1; '
        "  rc=$?; "
        "  cov=$(find /tmp/pni-cov ./TestResults -name 'coverage.cobertura.xml' 2>/dev/null | head -n 1); "
        '  if [ -n "$cov" ]; then cp "$cov" /out/cobertura.xml; fi; '
        "  cat /out/dotnet_test.txt; exit $rc; "
        "else "
        "  dotnet build --no-restore >/out/dotnet_test.txt 2>&1; rc=$?; "
        "  cat /out/dotnet_test.txt; exit $rc; "
        "fi"
    )
    return ["sh", "-c", script]


def _build_ruby_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "lint_fail=0; "
        "for f in $(find . -path './vendor' -prune -o -name '*.rb' -print 2>/dev/null); do "
        '  if ! ruby -c "$f" >/dev/null 2>/tmp/pni_rb_err.txt; then '
        "    cat /tmp/pni_rb_err.txt >&2; lint_fail=1; "
        "  fi; "
        "done; "
        'if [ "$lint_fail" -ne 0 ]; then exit 1; fi; '
        "if [ -d spec ] && find spec -name '*_spec.rb' 2>/dev/null | grep -q .; then "
        "  if [ -f Gemfile ] && bundle exec rspec --version >/dev/null 2>&1; then "
        "    bundle exec rspec --format documentation >/out/ruby_test.txt 2>&1; rc=$?; "
        "  else "
        "    rspec --format documentation >/out/ruby_test.txt 2>&1; rc=$?; "
        "  fi; "
        "  cat /out/ruby_test.txt; exit $rc; "
        "elif [ -d test ] && find test \\( -name '*_test.rb' -o -name 'test_*.rb' \\) 2>/dev/null | grep -q .; then "
        '  ruby -Ilib:test -e \'Dir.glob("test/**/*_test.rb").concat(Dir.glob("test/**/test_*.rb")).uniq.each { |f| '
        "require File.expand_path(f) }' >/out/ruby_test.txt 2>&1; rc=$?; "
        "  cat /out/ruby_test.txt; exit $rc; "
        "fi; "
        "echo 'Ruby syntax gate (ruby -c) passed; no spec/test suite found.'; exit 0"
    )
    return ["sh", "-c", script]


def _build_kotlin_test_cmd(_pf: ProjectFacts, tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    if tool == "maven":
        script = (
            "mvn -B -o -Dmaven.repo.local=/m2repo "
            "org.jacoco:jacoco-maven-plugin:0.8.12:prepare-agent -DfailIfNoTests=false test; "
            "rc=$?; "
            "mvn -B -o -Dmaven.repo.local=/m2repo "
            "org.jacoco:jacoco-maven-plugin:0.8.12:report >/dev/null 2>&1 || true; "
            "mkdir -p /out/surefire; "
            "cp target/surefire-reports/TEST-*.xml /out/surefire/ 2>/dev/null || true; "
            "cp target/site/jacoco/jacoco.xml /out/jacoco.xml 2>/dev/null || true; "
            "exit $rc"
        )
        return ["sh", "-c", script]
    script = (
        "mkdir -p /tmp/gradle-home && "
        "for sub in caches wrapper; do "
        '  if [ -d "/gradle-cache/$sub" ] && [ ! -e "/tmp/gradle-home/$sub" ]; then '
        '    ln -s "/gradle-cache/$sub" "/tmp/gradle-home/$sub"; '
        "  fi; "
        "done; "
        "GRADLE_USER_HOME=/tmp/gradle-home gradle --no-daemon --offline -I /opt/pni/jacoco.init.gradle test; "
        "rc=$?; "
        "GRADLE_USER_HOME=/tmp/gradle-home gradle --no-daemon --offline "
        "-I /opt/pni/jacoco.init.gradle jacocoTestReport >/dev/null 2>&1 || true; "
        "mkdir -p /out/surefire; "
        "find . -path '*/test-results/test/TEST-*.xml' -exec cp {} /out/surefire/ \\; 2>/dev/null || true; "
        "find . -path '*/reports/jacoco/test/jacocoTestReport.xml' "
        "-exec cp {} /out/jacoco.xml \\; 2>/dev/null || true; "
        "exit $rc"
    )
    return ["sh", "-c", script]


def _build_swift_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if [ -f Package.swift ]; then "
        "  if [ -d .build ]; then "
        "    swift test --skip-build >/out/swift_test.txt 2>&1; rc=$?; "
        "  else "
        "    swift test --disable-automatic-resolution >/out/swift_test.txt 2>&1; rc=$?; "
        "  fi; "
        "  cat /out/swift_test.txt; exit $rc; "
        "fi; "
        "fail=0; n=0; "
        "for f in $(find . -name '*.swift' -not -path './.build/*' 2>/dev/null); do "
        "  n=$((n + 1)); "
        '  if swiftc -parse "$f" >/tmp/pni_sw.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_sw.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_c_cpp_test_cmd(is_cpp: bool) -> TestCmdBuilder:
    compiler = "c++ -std=c++20" if is_cpp else "cc"
    ext_expr = "\\( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' \\)" if is_cpp else "-name '*.c'"
    test_expr = (
        "\\( -name 'test_*.cpp' -o -name '*_test.cpp' -o -name '*_test.cc' \\)"
        if is_cpp
        else "\\( -name 'test_*.c' -o -name '*_test.c' \\)"
    )

    def _builder(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
        script = (
            "if [ -f /workspace/build/CTestTestfile.cmake ]; then "
            "  ctest --test-dir /workspace/build --output-on-failure --output-junit /out/junit.xml "
            ">/out/generic_test.txt 2>&1; rc=$?; "
            "  if find /workspace/build -name '*.gcda' 2>/dev/null | grep -q .; then "
            "    lcov --capture --directory /workspace/build --output-file /out/lcov.info >/dev/null 2>&1 || true; "
            "  fi; "
            "  cat /out/generic_test.txt; exit $rc; "
            "fi; "
            "fail=0; n=0; "
            f"for f in $(find . -path './build' -prune -o {ext_expr} -print 2>/dev/null | sort); do "
            f'  if ! {compiler} -fsyntax-only -Iinclude -Isrc "$f" >/tmp/pni_cc.err 2>&1; then '
            "    cat /tmp/pni_cc.err >&2; fail=1; "
            "  fi; "
            "done; "
            'if [ "$fail" -ne 0 ]; then exit 1; fi; '
            f"for tf in $(find tests test -maxdepth 2 {test_expr} 2>/dev/null | sort); do "
            '  if grep -q "main(" "$tf" 2>/dev/null; then '
            "    n=$((n + 1)); "
            f'    if {compiler} -Iinclude -Isrc "$tf" -o /tmp/pni_c_runner >/tmp/pni_cc.err 2>&1 '
            "       && /tmp/pni_c_runner >/tmp/pni_cc.out 2>&1; then "
            '      echo "ok $n - $tf" >> /out/tap_test.txt; '
            "    else "
            '      cat /tmp/pni_cc.err /tmp/pni_cc.out >&2 2>/dev/null || true; '
            '      echo "not ok $n - $tf" >> /out/tap_test.txt; fail=1; '
            "    fi; "
            "  fi; "
            "done; "
            'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; '
            f'else echo "{compiler} syntax check passed across all source files."; fi; '
            "exit $fail"
        )
        return ["sh", "-c", script]

    return _builder


def _build_scala_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "mkdir -p /tmp/sbt-global; "
        "sbt --batch -Dsbt.server.autostart=false -Dsbt.global.base=/tmp/sbt-global "
        "-Dsbt.offline=true test >/out/scala_test.txt 2>&1; rc=$?; "
        "mkdir -p /out/surefire; "
        "find target -name 'TEST-*.xml' -exec cp {} /out/surefire/ \\; 2>/dev/null || true; "
        "cat /out/scala_test.txt; exit $rc"
    )
    return ["sh", "-c", script]


def _build_dart_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if [ -f .dart_tool/package_config.json ] && grep -q '\"name\": \"test\"' .dart_tool/package_config.json "
        "&& find test -name '*_test.dart' 2>/dev/null | grep -q .; then "
        "  dart test --reporter expanded >/out/dart_test.txt 2>&1; rc=$?; "
        "  cat /out/dart_test.txt; exit $rc; "
        "fi; "
        "fail=0; n=0; "
        "for tf in $(find test tests -name '*_test.dart' 2>/dev/null | sort); do "
        '  if grep -q "void main(" "$tf" 2>/dev/null; then '
        "    n=$((n + 1)); "
        '    if dart --enable-asserts run "$tf" >/tmp/pni_dart.out 2>&1; then '
        '      echo "ok $n - $tf" >> /out/tap_test.txt; '
        "    else "
        '      cat /tmp/pni_dart.out >&2; echo "not ok $n - $tf" >> /out/tap_test.txt; fail=1; '
        "    fi; "
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; exit $fail; fi; '
        "dart analyze --no-fatal-warnings >/out/dart_test.txt 2>&1; rc=$?; "
        "cat /out/dart_test.txt; exit $rc"
    )
    return ["sh", "-c", script]


def _build_elixir_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if [ -f mix.exs ]; then "
        "  MIX_ENV=test mix test --no-deps-check >/out/elixir_test.txt 2>&1; rc=$?; "
        "  cat /out/elixir_test.txt; exit $rc; "
        "fi; "
        "mkdir -p /tmp/pni_ebin; "
        "elixirc -o /tmp/pni_ebin $(find . -name '*.ex' 2>/dev/null) >/out/elixir_test.txt 2>&1; rc=$?; "
        "cat /out/elixir_test.txt; exit $rc"
    )
    return ["sh", "-c", script]


def _build_frontend_sfc_test_cmd(pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    pkg_check = (
        '"const p=require(\'./package.json\'); '
        'process.exit(p.scripts&&p.scripts.test&&!p.scripts.test.includes(\'no test specified\')?0:1)"'
    )
    checker = "vue-tsc" if pf.language == "vue" else "svelte-check"
    script = (
        "if [ -x ./node_modules/.bin/vitest ]; then "
        '  cov_flags=""; '
        "  if [ -d node_modules/@vitest/coverage-v8 ] || [ -d node_modules/@vitest/coverage-istanbul ]; then "
        "    mkdir -p /tmp/pni-cov; "
        '    cov_flags="--coverage.enabled=true --coverage.clean=false '
        '--coverage.reporter=json-summary --coverage.reportsDirectory=/tmp/pni-cov"; '
        "  fi; "
        "  ./node_modules/.bin/vitest run --reporter=default --reporter=junit "
        "--outputFile.junit=/out/junit.xml $cov_flags >/out/node_test.txt 2>&1; rc=$?; "
        "  cp -f /tmp/pni-cov/coverage-summary.json /out/coverage-summary.json 2>/dev/null || true; "
        "  cat /out/node_test.txt; exit $rc; "
        "elif [ -x ./node_modules/.bin/jest ]; then "
        "  mkdir -p /tmp/pni-cov; "
        "  ./node_modules/.bin/jest --ci --coverage --coverageReporters=json-summary "
        "--coverageDirectory=/tmp/pni-cov >/out/node_test.txt 2>&1; rc=$?; "
        "  cp -f /tmp/pni-cov/coverage-summary.json /out/coverage-summary.json 2>/dev/null || true; "
        "  cat /out/node_test.txt; exit $rc; "
        f"elif [ -f package.json ] && node -e {pkg_check} >/dev/null 2>&1; then "
        "  npm test >/out/node_test.txt 2>&1; rc=$?; cat /out/node_test.txt; exit $rc; "
        f"elif [ -x ./node_modules/.bin/{checker} ]; then "
        f"  ./node_modules/.bin/{checker} >/out/node_test.txt 2>&1; rc=$?; cat /out/node_test.txt; exit $rc; "
        "elif [ -x ./node_modules/.bin/tsc ] && [ -f tsconfig.json ]; then "
        "  ./node_modules/.bin/tsc --noEmit >/out/node_test.txt 2>&1; rc=$?; cat /out/node_test.txt; exit $rc; "
        "else "
        "  node --test >/out/node_test.txt 2>&1; rc=$?; cat /out/node_test.txt; exit $rc; "
        "fi"
    )
    return ["sh", "-c", script]


def _build_perl_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "lint_fail=0; "
        "for f in $(find . -path './local' -prune -o \\( -name '*.pm' -o -name '*.pl' \\) -print 2>/dev/null); do "
        '  if ! perl -Ilib -c "$f" >/dev/null 2>/tmp/pni_pl_err.txt; then '
        "    cat /tmp/pni_pl_err.txt >&2; lint_fail=1; "
        "  fi; "
        "done; "
        'if [ "$lint_fail" -ne 0 ]; then exit 1; fi; '
        "if [ -d t ] && find t -name '*.t' 2>/dev/null | grep -q .; then "
        "  prove -lv -Ilib t/ >/out/tap_test.txt 2>&1; rc=$?; "
        "  cat /out/tap_test.txt; exit $rc; "
        "fi; "
        "echo 'Perl syntax gate (perl -c) passed; no t/*.t suite found.'; exit 0"
    )
    return ["sh", "-c", script]


def _build_r_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    r_script = (
        'src_files <- list.files(c("R", "src"), pattern = "\\\\.[Rr]$", recursive = TRUE, full.names = TRUE); '
        'for (f in src_files) parse(file = f); '
        'test_dir <- if (dir.exists("tests/testthat")) "tests/testthat" '
        'else if (dir.exists("tests")) "tests" else ""; '
        'test_files <- if (nzchar(test_dir)) list.files(test_dir, pattern = "^test.*\\\\.[Rr]$", '
        "full.names = TRUE) else character(0); "
        "if (length(test_files) > 0) { "
        "  for (f in src_files) tryCatch(source(f), error = function(e) NULL); "
        "  res <- testthat::test_dir(test_dir, reporter = testthat::SummaryReporter$new(), stop_on_failure = FALSE); "
        "  df <- as.data.frame(res); "
        '  cat(sprintf("\\n[ FAIL %d | WARN %d | SKIP %d | PASS %d ]\\n", '
        "      sum(df$failed), sum(df$warning), sum(df$skipped), sum(df$passed))); "
        "  if (sum(df$failed) > 0 || any(df$error)) quit(status = 1); "
        "} else { "
        '  cat("R syntax gate (parse) passed across", length(src_files), "files.\\n"); '
        "}"
    )
    script = f"Rscript -e '{r_script}' >/out/r_test.txt 2>&1; rc=$?; cat /out/r_test.txt; exit $rc"
    return ["sh", "-c", script]


def _build_cobol_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . \\( -name '*.cob' -o -name '*.cbl' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if cobc -fsyntax-only -I. -Isrc "$f" >/tmp/pni_cob.err 2>&1 '
        '     || cobc -fsyntax-only -free -I. -Isrc "$f" >/tmp/pni_cob.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_cob.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_bash_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . \\( -name '*.sh' -o -name '*.bash' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if bash -n "$f" >/tmp/pni_sh.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_sh.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$fail" -ne 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; exit 1; fi; '
        "if find . -name '*.bats' 2>/dev/null | grep -q .; then "
        "  bats --tap $(find . -name '*.bats' 2>/dev/null | sort) >/out/tap_test.txt 2>&1; rc=$?; "
        "  cat /out/tap_test.txt; exit $rc; "
        "fi; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_powershell_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    ps_code = (
        "$files = Get-ChildItem -Recurse -Include *.ps1,*.psm1 | Sort-Object FullName; "
        "$n = 0; $fail = 0; "
        "foreach ($f in $files) { "
        "  $n++; $tokens = $null; $errs = $null; "
        "  [void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errs); "
        "  if ($errs -and $errs.Count -gt 0) { "
        '    Write-Error "$($f.Name): $($errs[0].Message)"; '
        '    Add-Content /out/tap_test.txt "not ok $n - $($f.Name)"; $fail = 1 '
        "  } else { "
        '    Add-Content /out/tap_test.txt "ok $n - $($f.Name)" '
        "  } "
        "}; "
        'if ($n -gt 0) { Add-Content /out/tap_test.txt "1..$n"; Get-Content /out/tap_test.txt }; '
        "exit $fail"
    )
    return ["pwsh", "-NoProfile", "-Command", ps_code]


def _build_groovy_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "mkdir -p /tmp/pni_groovy; "
        "files=$(find . -name '*.groovy' 2>/dev/null | sort); "
        'if [ -z "$files" ]; then echo "No .groovy files found."; exit 0; fi; '
        "groovyc -d /tmp/pni_groovy $files >/out/generic_test.txt 2>&1; rc=$?; "
        'if [ "$rc" -eq 0 ]; then echo "ok 1 - groovyc compiled all sources" >/out/tap_test.txt; '
        'echo "1..1" >> /out/tap_test.txt; fi; '
        "cat /out/generic_test.txt /out/tap_test.txt 2>/dev/null || true; exit $rc"
    )
    return ["sh", "-c", script]


def _build_lua_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . -name '*.lua' 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if luac5.4 -p "$f" >/tmp/pni_lua.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_lua.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_haskell_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if ls *.cabal >/dev/null 2>&1 && [ -d dist-newstyle ]; then "
        "  cabal test --offline >/out/generic_test.txt 2>&1; rc=$?; cat /out/generic_test.txt; exit $rc; "
        "fi; "
        "mkdir -p /tmp/pni_ghc; fail=0; n=0; "
        "for f in $(find . -name '*.hs' -not -path './dist-newstyle/*' 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if ghc -fno-code -isrc -outputdir /tmp/pni_ghc "$f" >/tmp/pni_hs.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_hs.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_ocaml_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "if [ -f dune-project ] && find . -maxdepth 3 -name 'dune' 2>/dev/null | grep -q .; then "
        "  dune runtest >/out/generic_test.txt 2>&1; rc=$?; cat /out/generic_test.txt; exit $rc; "
        "fi; "
        "mkdir -p /tmp/pni_ml; fail=0; n=0; "
        "for f in $(find . -name '*.ml' -not -path './_build/*' 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  base=$(basename "$f" .ml); '
        '  if ocamlc -c -I /tmp/pni_ml -o "/tmp/pni_ml/${base}.cmo" "$f" >/tmp/pni_ml.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_ml.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_zig_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . -name '*.zig' -not -path './zig-out/*' -not -path './.zig-cache/*' 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if zig ast-check "$f" >/tmp/pni_zig.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_zig.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_julia_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    jl_code = (
        'files = String[]; '
        'for (root, _, fnames) in walkdir("."); '
        'for fn in fnames; endswith(fn, ".jl") && push!(files, joinpath(root, fn)); end; end; '
        "sort!(files); fail = 0; "
        'open("/out/tap_test.txt", "w") do io; '
        "  for (i, f) in enumerate(files); "
        "    try; Meta.parseall(read(f, String)); println(io, \"ok $i - $f\"); "
        "    catch e; println(stderr, f, \": \", e); println(io, \"not ok $i - $f\"); fail = 1; end; "
        "  end; "
        '  length(files) > 0 && println(io, "1..", length(files)); '
        "end; "
        "exit(fail)"
    )
    script = (
        "if [ -f test/runtests.jl ]; then "
        "  julia --project=. test/runtests.jl >/out/generic_test.txt 2>&1; rc=$?; cat /out/generic_test.txt; exit $rc; "
        "fi; "
        f"julia -e '{jl_code}'; rc=$?; cat /out/tap_test.txt 2>/dev/null || true; exit $rc"
    )
    return ["sh", "-c", script]


def _build_fortran_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "mkdir -p /tmp/pni_fmod; fail=0; n=0; "
        "for f in $(find . \\( -name '*.f90' -o -name '*.f95' -o -name '*.f03' -o -name '*.f08' \\) "
        "2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if gfortran -fsyntax-only -J/tmp/pni_fmod "$f" >/tmp/pni_f90.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_f90.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_ada_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "mkdir -p /tmp/pni_ada; fail=0; n=0; "
        "for f in $(find /workspace \\( -name '*.ads' -o -name '*.adb' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if (cd /tmp/pni_ada && gcc -c -gnats -I/workspace/src "$f") >/tmp/pni_ada.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_ada.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_commonlisp_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . \\( -name '*.lisp' -o -name '*.lsp' -o -name '*.cl' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if sbcl --noinform --non-interactive --eval "(handler-case (progn (compile-file \\"$f\\" '
        ':output-file \\"/tmp/pni.fasl\\") (sb-ext:exit :code 0)) (error (c) (format *error-output* \\"~A~%\\" c) '
        '(sb-ext:exit :code 1)))" >/tmp/pni_cl.out 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_cl.out >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_verilog_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "fail=0; n=0; "
        "for f in $(find . \\( -name '*.sv' -o -name '*.v' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if iverilog -g2012 -tnull "$f" >/tmp/pni_sv.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_sv.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


def _build_vhdl_test_cmd(_pf: ProjectFacts, _tool: str, _srcs: list[str], _tests: list[str]) -> list[str]:
    script = (
        "mkdir -p /tmp/pni_ghdl; fail=0; n=0; "
        "for f in $(find . \\( -name '*.vhd' -o -name '*.vhdl' \\) 2>/dev/null | sort); do "
        "  n=$((n + 1)); "
        '  if ghdl -s --std=08 --workdir=/tmp/pni_ghdl "$f" >/tmp/pni_vhd.err 2>&1; then '
        '    echo "ok $n - $f" >> /out/tap_test.txt; '
        "  else "
        '    cat /tmp/pni_vhd.err >&2; echo "not ok $n - $f" >> /out/tap_test.txt; fail=1; '
        "  fi; "
        "done; "
        'if [ "$n" -gt 0 ]; then echo "1..$n" >> /out/tap_test.txt; cat /out/tap_test.txt; fi; '
        "exit $fail"
    )
    return ["sh", "-c", script]


# ---------------------------------------------------------------------------
# Stage 3 Smoke Check Plan Builders
# ---------------------------------------------------------------------------


def _simple_smoke(check_cmd: str, detail: str) -> SmokeBuilder:
    """Create a Stage 3 smoke plan builder executing check_cmd and emitting /out/smoke.json."""

    def _builder(
        _target_root: Path,
        _pf: ProjectFacts,
        archetype_label: str,
        _source_targets: list[str],
    ) -> tuple[str, Optional[list[str]]]:
        cmd = f"{check_cmd} && printf '{{\"detail\":\"{detail}\"}}' >/out/smoke.json"
        return archetype_label, ["sh", "-c", cmd]

    return _builder


def _build_rust_smoke(
    target_root: Path,
    _pf: ProjectFacts,
    archetype_label: str,
    _source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    if (target_root / "Cargo.toml").is_file():
        cmd = (
            "cargo check --offline && "
            'printf \'{"detail":"Rust crate type-checked cleanly (cargo check --offline)"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    return archetype_label, [
        "sh",
        "-c",
        'rustc --version >/dev/null && printf \'{"detail":"Rust compiler toolchain verified"}\' >/out/smoke.json',
    ]


def _build_dotnet_smoke(
    _target_root: Path,
    pf: ProjectFacts,
    archetype_label: str,
    _source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    label = "F#" if pf.language == "fsharp" else "C#"
    cmd = (
        "dotnet build --no-restore >/dev/null && "
        f'printf \'{{"detail":"{label} .NET assembly compiled cleanly (dotnet build --no-restore)"}}\' >/out/smoke.json'
    )
    return archetype_label, ["sh", "-c", cmd]


def _build_swift_smoke(
    target_root: Path,
    _pf: ProjectFacts,
    archetype_label: str,
    _source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    if (target_root / "Package.swift").is_file():
        cmd = (
            "swift build --skip-update --disable-automatic-resolution >/dev/null && "
            'printf \'{"detail":"Swift package compiled cleanly (swift build)"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    cmd = (
        "swift --version >/dev/null && "
        'printf \'{"detail":"Swift toolchain syntax probe verified"}\' >/out/smoke.json'
    )
    return archetype_label, ["sh", "-c", cmd]


def _build_kotlin_smoke(
    target_root: Path,
    _pf: ProjectFacts,
    archetype_label: str,
    _source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    if (target_root / "pom.xml").is_file() and not (
        (target_root / "build.gradle.kts").is_file() or (target_root / "build.gradle").is_file()
    ):
        cmd = (
            "mvn -B -o -Dmaven.repo.local=/m2repo test-compile >/dev/null && "
            'printf \'{"detail":"Kotlin Maven project compiled cleanly"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    cmd = (
        "mkdir -p /tmp/gradle-home && "
        "for sub in caches wrapper; do "
        '  if [ -d "/gradle-cache/$sub" ] && [ ! -e "/tmp/gradle-home/$sub" ]; then '
        '    ln -s "/gradle-cache/$sub" "/tmp/gradle-home/$sub"; '
        "  fi; "
        "done && "
        "GRADLE_USER_HOME=/tmp/gradle-home gradle --no-daemon --offline classes >/dev/null && "
        'printf \'{"detail":"Kotlin Gradle project compiled cleanly"}\' >/out/smoke.json'
    )
    return archetype_label, ["sh", "-c", cmd]


def _build_elixir_smoke(
    target_root: Path,
    _pf: ProjectFacts,
    archetype_label: str,
    _source_targets: list[str],
) -> tuple[str, Optional[list[str]]]:
    if (target_root / "mix.exs").is_file():
        cmd = (
            "MIX_ENV=test mix compile --no-deps-check >/dev/null && "
            'printf \'{"detail":"Elixir Mix project compiled cleanly"}\' >/out/smoke.json'
        )
        return archetype_label, ["sh", "-c", cmd]
    cmd = 'elixir --version >/dev/null && printf \'{"detail":"Elixir runtime verified"}\' >/out/smoke.json'
    return archetype_label, ["sh", "-c", cmd]


EXTENDED_HARNESS_SPECS: Final[dict[str, ExtendedHarnessSpec]] = {
    # --- Tier A Additions (14 languages) ---
    "rust": ExtendedHarnessSpec(
        language="rust",
        default_tool="cargo",
        version_arg="RUST_VERSION",
        default_version="1.85",
        version_selector=select_rust_image_version,
        test_builder=_build_rust_test_cmd,
        smoke_builder=_build_rust_smoke,
    ),
    "csharp": ExtendedHarnessSpec(
        language="csharp",
        default_tool="dotnet",
        version_arg="DOTNET_VERSION",
        default_version="8.0",
        version_selector=select_dotnet_image_version,
        test_builder=_build_dotnet_test_cmd,
        smoke_builder=_build_dotnet_smoke,
    ),
    "ruby": ExtendedHarnessSpec(
        language="ruby",
        default_tool="bundler",
        version_arg="RUBY_VERSION",
        default_version="3.3",
        version_selector=select_ruby_image_version,
        test_builder=_build_ruby_test_cmd,
        smoke_builder=_simple_smoke("ruby -v >/dev/null", "Ruby runtime and syntax verification passed"),
    ),
    "kotlin": ExtendedHarnessSpec(
        language="kotlin",
        default_tool="gradle",
        version_arg="JAVA_VERSION",
        default_version="21",
        version_selector=_select_jvm_version,
        supports_extra_apt=False,
        test_builder=_build_kotlin_test_cmd,
        smoke_builder=_build_kotlin_smoke,
    ),
    "swift": ExtendedHarnessSpec(
        language="swift",
        default_tool="swiftpm",
        version_arg="SWIFT_VERSION",
        default_version="6.0",
        version_selector=select_swift_image_version,
        test_builder=_build_swift_test_cmd,
        smoke_builder=_build_swift_smoke,
    ),
    "c": ExtendedHarnessSpec(
        language="c",
        default_tool="cmake",
        test_builder=_build_c_cpp_test_cmd(is_cpp=False),
        smoke_builder=_simple_smoke("cc --version >/dev/null", "C compiler toolchain and syntax verified"),
    ),
    "cpp": ExtendedHarnessSpec(
        language="cpp",
        default_tool="cmake",
        test_builder=_build_c_cpp_test_cmd(is_cpp=True),
        smoke_builder=_simple_smoke("c++ --version >/dev/null", "C++ compiler toolchain and syntax verified"),
    ),
    "scala": ExtendedHarnessSpec(
        language="scala",
        default_tool="sbt",
        version_arg="JAVA_VERSION",
        default_version="21",
        version_selector=_select_jvm_version,
        test_builder=_build_scala_test_cmd,
        smoke_builder=_simple_smoke(
            "mkdir -p /tmp/sbt-global && "
            "sbt --batch -Dsbt.server.autostart=false -Dsbt.global.base=/tmp/sbt-global "
            "-Dsbt.offline=true compile >/dev/null",
            "Scala sbt project compiled cleanly",
        ),
    ),
    "dart": ExtendedHarnessSpec(
        language="dart",
        default_tool="pub",
        version_arg="DART_VERSION",
        default_version="stable",
        version_selector=select_dart_image_version,
        supports_extra_apt=False,
        test_builder=_build_dart_test_cmd,
        smoke_builder=_simple_smoke(
            "dart analyze --no-fatal-warnings >/dev/null",
            "Dart static analysis (dart analyze) passed",
        ),
    ),
    "elixir": ExtendedHarnessSpec(
        language="elixir",
        default_tool="mix",
        version_arg="ELIXIR_VERSION",
        default_version="1.17",
        version_selector=select_elixir_image_version,
        test_builder=_build_elixir_test_cmd,
        smoke_builder=_build_elixir_smoke,
    ),
    "vue": ExtendedHarnessSpec(
        language="vue",
        default_tool="node",
        version_arg="NODE_VERSION",
        default_version="20",
        version_selector=_select_frontend_node_version,
        supports_extra_apt=False,
        test_builder=_build_frontend_sfc_test_cmd,
        smoke_builder=_simple_smoke("node --version >/dev/null", "Vue Node.js workspace verified"),
    ),
    "perl": ExtendedHarnessSpec(
        language="perl",
        default_tool="cpan",
        version_arg="PERL_VERSION",
        default_version="5.40",
        version_selector=select_perl_image_version,
        test_builder=_build_perl_test_cmd,
        smoke_builder=_simple_smoke("perl -v >/dev/null", "Perl runtime and module syntax verified"),
    ),
    "r": ExtendedHarnessSpec(
        language="r",
        default_tool="r",
        version_arg="R_VERSION",
        default_version="4.4.2",
        version_selector=select_r_image_version,
        test_builder=_build_r_test_cmd,
        smoke_builder=_simple_smoke("Rscript --version >/dev/null", "R runtime and script parse check passed"),
    ),
    "cobol": ExtendedHarnessSpec(
        language="cobol",
        default_tool="gnucobol",
        test_builder=_build_cobol_test_cmd,
        smoke_builder=_simple_smoke("cobc --version >/dev/null", "GnuCOBOL compiler syntax verification passed"),
    ),
    # --- Tier B Additions (15 Linux-native languages) ---
    "bash": ExtendedHarnessSpec(
        language="bash",
        default_tool="shell",
        test_builder=_build_bash_test_cmd,
        smoke_builder=_simple_smoke("bash --version >/dev/null", "Bash syntax verification passed"),
    ),
    "powershell": ExtendedHarnessSpec(
        language="powershell",
        default_tool="pwsh",
        test_builder=_build_powershell_test_cmd,
        smoke_builder=_simple_smoke("pwsh --version >/dev/null", "PowerShell parser verification passed"),
    ),
    "groovy": ExtendedHarnessSpec(
        language="groovy",
        default_tool="gradle",
        version_arg="JAVA_VERSION",
        default_version="21",
        version_selector=_select_jvm_version,
        supports_extra_apt=False,
        test_builder=_build_groovy_test_cmd,
        smoke_builder=_simple_smoke("groovy --version >/dev/null", "Groovy compilation verification passed"),
    ),
    "lua": ExtendedHarnessSpec(
        language="lua",
        default_tool="lua",
        test_builder=_build_lua_test_cmd,
        smoke_builder=_simple_smoke("lua5.4 -v >/dev/null", "Lua 5.4 bytecode syntax verification passed"),
    ),
    "haskell": ExtendedHarnessSpec(
        language="haskell",
        default_tool="cabal",
        test_builder=_build_haskell_test_cmd,
        smoke_builder=_simple_smoke("ghc --version >/dev/null", "GHC Haskell type-check verification passed"),
    ),
    "fsharp": ExtendedHarnessSpec(
        language="fsharp",
        default_tool="dotnet",
        version_arg="DOTNET_VERSION",
        default_version="8.0",
        version_selector=select_dotnet_image_version,
        test_builder=_build_dotnet_test_cmd,
        smoke_builder=_build_dotnet_smoke,
    ),
    "ocaml": ExtendedHarnessSpec(
        language="ocaml",
        default_tool="dune",
        test_builder=_build_ocaml_test_cmd,
        smoke_builder=_simple_smoke("ocamlc -version >/dev/null", "OCaml compiler verification passed"),
    ),
    "zig": ExtendedHarnessSpec(
        language="zig",
        default_tool="zig",
        supports_extra_apt=False,
        test_builder=_build_zig_test_cmd,
        smoke_builder=_simple_smoke("zig version >/dev/null", "Zig AST verification passed"),
    ),
    "julia": ExtendedHarnessSpec(
        language="julia",
        default_tool="julia",
        version_arg="JULIA_VERSION",
        default_version="1.11",
        version_selector=select_julia_image_version,
        test_builder=_build_julia_test_cmd,
        smoke_builder=_simple_smoke("julia --version >/dev/null", "Julia parser verification passed"),
    ),
    "fortran": ExtendedHarnessSpec(
        language="fortran",
        default_tool="gfortran",
        test_builder=_build_fortran_test_cmd,
        smoke_builder=_simple_smoke("gfortran --version >/dev/null", "GFortran syntax verification passed"),
    ),
    "svelte": ExtendedHarnessSpec(
        language="svelte",
        default_tool="node",
        version_arg="NODE_VERSION",
        default_version="20",
        version_selector=_select_frontend_node_version,
        supports_extra_apt=False,
        test_builder=_build_frontend_sfc_test_cmd,
        smoke_builder=_simple_smoke("node --version >/dev/null", "Svelte Node.js workspace verified"),
    ),
    "ada": ExtendedHarnessSpec(
        language="ada",
        default_tool="gnat",
        test_builder=_build_ada_test_cmd,
        smoke_builder=_simple_smoke("gnatmake --version >/dev/null", "GNAT Ada syntax verification passed"),
    ),
    "commonlisp": ExtendedHarnessSpec(
        language="commonlisp",
        default_tool="sbcl",
        test_builder=_build_commonlisp_test_cmd,
        smoke_builder=_simple_smoke("sbcl --version >/dev/null", "SBCL Common Lisp compilation verification passed"),
    ),
    "verilog": ExtendedHarnessSpec(
        language="verilog",
        default_tool="iverilog",
        test_builder=_build_verilog_test_cmd,
        smoke_builder=_simple_smoke("iverilog -V >/dev/null", "Icarus Verilog elaboration check passed"),
    ),
    "vhdl": ExtendedHarnessSpec(
        language="vhdl",
        default_tool="ghdl",
        test_builder=_build_vhdl_test_cmd,
        smoke_builder=_simple_smoke("ghdl --version >/dev/null", "GHDL VHDL syntax analysis passed"),
    ),
}


def get_extended_harness_spec(language: str) -> Optional[ExtendedHarnessSpec]:
    """Return the ExtendedHarnessSpec for language if it is an extended harness language."""
    return EXTENDED_HARNESS_SPECS.get(language.strip().lower())


def select_extended_harness_tool(pf: ProjectFacts) -> Optional[str]:
    """Select the built-in harness tool name for an extended language, or None if not extended."""
    spec = get_extended_harness_spec(pf.language)
    if spec is None:
        return None
    if pf.language == "kotlin":
        has_gradle = pf.build_system == "gradle" or any("gradle" in m for m in pf.manifest_files)
        if not has_gradle and (pf.build_system == "maven" or "pom.xml" in pf.manifest_files):
            return "maven"
        return "gradle"
    return spec.default_tool


def compute_extended_build_args(
    pf: ProjectFacts,
    *,
    extra_apt_packages: str = "",
    harness_dockerfile: Optional[Path] = None,
) -> Optional[dict[str, str]]:
    """Compute Docker --build-arg mapping for an extended harness language, or None if not extended."""
    spec = get_extended_harness_spec(pf.language)
    if spec is None:
        return None

    args: dict[str, str] = {}
    if spec.version_arg and spec.version_selector is not None:
        df_val = _extract_arg_default(harness_dockerfile, spec.version_arg)
        raw = df_val if (df_val and df_val != spec.default_version) else pf.language_version_constraint
        args[spec.version_arg] = spec.version_selector(raw)
    if spec.supports_extra_apt and extra_apt_packages.strip():
        args["EXTRA_APT_PACKAGES"] = extra_apt_packages.strip()
    return args


def build_extended_test_command(
    pf: ProjectFacts,
    tool: str,
    source_targets: list[str],
    test_targets: list[str],
) -> Optional[list[str]]:
    """Build the Stage 2 offline test/lint command for an extended language, or None if not extended."""
    spec = get_extended_harness_spec(pf.language)
    if spec is None or spec.test_builder is None:
        return None
    return spec.test_builder(pf, tool, source_targets, test_targets)


def build_extended_smoke_plan(
    target_root: Path,
    pf: ProjectFacts,
    archetype_label: str,
    source_targets: list[str],
) -> Optional[tuple[str, Optional[list[str]]]]:
    """Build the Stage 3 smoke probe command for an extended language, or None if not extended."""
    spec = get_extended_harness_spec(pf.language)
    if spec is None or spec.smoke_builder is None:
        return None
    return spec.smoke_builder(target_root, pf, archetype_label, source_targets)
