# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Deterministic selector mapping ProjectFacts to harness Dockerfiles, build args, and test commands."""

from __future__ import annotations

import re
import shlex
from collections.abc import Sequence
from typing import Optional

from pni._actions.project_inspect import ProjectFacts

_PY_VER_RE = re.compile(r"3\.(\d+)")
_PHP_VER_RE = re.compile(r"8\.(\d+)")


def select_python_image_version(constraint: Optional[str]) -> str:
    """Select a supported CPython container tag ('3.11', '3.12', '3.13') from requires-python."""
    if not constraint:
        return "3.12"
    text = constraint.strip()
    if "<3.12" in text or "==3.11" in text or "~=3.11" in text:
        return "3.11"
    matches = [int(m) for m in _PY_VER_RE.findall(text)]
    if matches and min(matches) >= 13:
        return "3.13"
    return "3.12"


def select_java_image_version(constraint: Optional[str]) -> str:
    """Select an Eclipse Temurin JDK container tag ('8', '11', '17', '21') from Java version."""
    if not constraint:
        return "21"
    raw = constraint.strip()
    if raw in {"1.8", "8"}:
        return "8"
    if raw == "11":
        return "11"
    if raw == "17":
        return "17"
    return "21"


def _select_single_php_branch_version(branch: str) -> str:
    """Select an active PHP CLI container tag ('8.1', '8.2', '8.3', '8.4') for a single constraint branch."""
    if re.search(r"(?:^|\D)(?:5\.\d+|7\.\d+)(?:\D|$)", branch) or re.search(
        r"(?:~|==|=|<)\s*8\.0\b|\b8\.0\.\*", branch
    ):
        return "8.2"
    if "<8.2" in branch or "~8.1" in branch or "==8.1" in branch or "8.1.*" in branch:
        return "8.1"
    if "<8.3" in branch or "~8.2" in branch or "==8.2" in branch or "8.2.*" in branch:
        return "8.2"
    if "<8.4" in branch or "~8.3" in branch or "==8.3" in branch or "8.3.*" in branch:
        return "8.3"
    matches = [int(m) for m in _PHP_VER_RE.findall(branch)]
    if matches and max(matches) >= 4:
        return "8.4"
    return "8.3"


def select_php_image_version(constraint: Optional[str]) -> str:
    """Select an active official PHP CLI container tag ('8.1', '8.2', '8.3', '8.4') from version constraint."""
    if not constraint or not constraint.strip():
        return "8.3"
    branches = [b.strip() for b in re.split(r"\|\|?", constraint.strip()) if b.strip()]
    if not branches:
        return "8.3"
    candidates = [_select_single_php_branch_version(b) for b in branches]
    return max(candidates, key=lambda ver: tuple(int(part) for part in ver.split(".")))


def select_harness_tool(pf: ProjectFacts) -> str:
    """Determine the built-in harness Dockerfile tool name ('uv', 'poetry', 'pip', 'maven', 'composer', etc.)."""
    if pf.language == "java":
        is_gradle = pf.build_system == "gradle" or any("gradle" in m for m in pf.manifest_files)
        return "gradle" if is_gradle else "maven"
    if pf.language == "php":
        is_composer = pf.build_system == "composer" or "composer.json" in pf.manifest_files
        return "composer" if is_composer else "raw"

    if pf.build_system == "uv" or "uv.lock" in pf.lockfiles_found:
        return "uv"
    if pf.build_system == "poetry" or "poetry.lock" in pf.lockfiles_found:
        return "poetry"
    return "pip"


def compute_harness_build_args(
    pf: ProjectFacts,
    *,
    extra_apt_packages: str = "",
) -> dict[str, str]:
    """Build --build-arg key-value dictionary for the selected language harness."""
    if pf.language == "java":
        return {"JAVA_VERSION": select_java_image_version(pf.language_version_constraint)}
    if pf.language == "php":
        php_args: dict[str, str] = {
            "PHP_VERSION": select_php_image_version(pf.language_version_constraint),
        }
        if extra_apt_packages.strip():
            php_args["EXTRA_APT_PACKAGES"] = extra_apt_packages.strip()
        return php_args

    args: dict[str, str] = {
        "PYTHON_VERSION": select_python_image_version(pf.language_version_constraint),
    }
    if extra_apt_packages.strip():
        args["EXTRA_APT_PACKAGES"] = extra_apt_packages.strip()
    return args


def _build_php_test_and_lint_script(source_targets: list[str], test_targets: list[str]) -> str:
    """Build offline shell script running `php -l` syntax gate followed by PHPUnit/Pest + PCOV Clover."""
    eff_srcs = source_targets or ["."]
    eff_src = " ".join(eff_srcs)
    eff_tst = " ".join(test_targets or ["tests"])
    dirs_xml = "".join(f"<directory>{s}</directory>" for s in eff_srcs)
    fallback_xml = (
        f"<phpunit><source><include>{dirs_xml}</include>"
        "<exclude><directory>vendor</directory><directory>tests</directory></exclude>"
        "</source></phpunit>"
    )
    return (
        "lint_fail=0; "
        f"for p in $(find {eff_src} -path '*/vendor' -prune "
        "-o \\( -name '*.php' -o -name '*.phtml' \\) -print 2>/dev/null); do "
        '  if ! php -l "$p" >/tmp/pni_lint_err.txt 2>&1; then '
        "    cat /tmp/pni_lint_err.txt >&2; lint_fail=1; "
        "  fi; "
        "done; "
        'if [ "$lint_fail" -ne 0 ]; then exit 1; fi; '
        "has_tests=0; "
        f"for td in {eff_tst}; do "
        '  if [ -d "$td" ] && [ -n "$(find "$td" -name \'*Test.php\' -o -name \'*_test.php\' 2>/dev/null)" ]; then '
        "    has_tests=1; "
        "  fi; "
        "done; "
        'if [ "$has_tests" -eq 1 ] && command -v phpunit >/dev/null 2>&1; then '
        '  cfg_flag=""; '
        '  tst_arg=""; '
        "  if [ ! -f phpunit.xml ] && [ ! -f phpunit.xml.dist ] && [ ! -f phpunit.dist.xml ]; then "
        f"    printf '%s' '{fallback_xml}' >/tmp/pni_phpunit.xml; "
        '    cfg_flag="-c /tmp/pni_phpunit.xml"; '
        f'    tst_arg="{eff_tst}"; '
        "  fi; "
        "  phpunit $cfg_flag -d pcov.enabled=1 -d pcov.directory=. "
        "--log-junit /out/junit.xml --coverage-clover /out/clover.xml $tst_arg; "
        "  exit $?; "
        "fi; "
        "echo 'PHP syntax gate (php -l) passed; no PHPUnit tests executed.'; exit 0"
    )


def _prepend_pre_test_cmd(cmd: list[str], pre_test_cmd: str) -> list[str]:
    """Prepend an optional setup shell command before executing the Stage 2 test command."""
    clean_pre = pre_test_cmd.strip()
    if not clean_pre:
        return cmd
    if len(cmd) == 3 and cmd[0] in {"sh", "bash"} and cmd[1] == "-c":
        return [cmd[0], "-c", f"{clean_pre} && ({cmd[2]})"]
    return ["sh", "-c", f"{clean_pre} && {shlex.join(cmd)}"]


def _build_java_test_command(tool: str) -> list[str]:
    """Build offline Gradle or Maven test + JaCoCo report command."""
    if tool == "gradle":
        script = (
            "gradle --no-daemon --offline -I /opt/pni/jacoco.init.gradle test; "
            "rc=$?; "
            "gradle --no-daemon --offline -I /opt/pni/jacoco.init.gradle jacocoTestReport "
            ">/dev/null 2>&1 || true; "
            "mkdir -p /out/surefire; "
            "find . -path '*/test-results/test/TEST-*.xml' -exec cp {} /out/surefire/ \\; 2>/dev/null || true; "
            "find . -path '*/reports/jacoco/test/jacocoTestReport.xml' "
            "-exec cp {} /out/jacoco.xml \\; 2>/dev/null || true; "
            "exit $rc"
        )
        return ["sh", "-c", script]

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


def build_test_and_coverage_command(
    pf: ProjectFacts,
    tool: str,
    source_targets: list[str],
    test_targets: list[str],
    *,
    override_cmd: str = "",
    pytest_extra_args: Sequence[str] = (),
    pre_test_cmd: str = "",
) -> list[str]:
    """Construct the offline Stage 2 command executing unit tests and emitting coverage artifacts."""
    if override_cmd.strip():
        return _prepend_pre_test_cmd(["sh", "-c", override_cmd.strip()], pre_test_cmd)

    if pf.language == "php":
        php_cmd = ["sh", "-c", _build_php_test_and_lint_script(source_targets, test_targets)]
        return _prepend_pre_test_cmd(php_cmd, pre_test_cmd)

    if pf.language == "java":
        return _prepend_pre_test_cmd(_build_java_test_command(tool), pre_test_cmd)

    eff_sources = source_targets or ["src"]
    eff_tests = test_targets or ["tests"]
    cov_flags = [f"--cov={src}" for src in eff_sources]
    extra = [arg for arg in pytest_extra_args if arg.strip()]
    py_cmd = [
        "pytest",
        "-o",
        "junit_family=xunit2",
        "--junitxml=/out/junit.xml",
        *cov_flags,
        "--cov-branch",
        "--cov-report=json:/out/coverage.json",
        *extra,
        *eff_tests,
    ]
    return _prepend_pre_test_cmd(py_cmd, pre_test_cmd)
