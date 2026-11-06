# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Test execution and test coverage toolset."""

from __future__ import annotations

from typing import Optional

import typer

from tools.pcli.common import console, run_command

app = typer.Typer(
    name="test",
    help="Run unit, integration, and coverage tests using pytest.",
    no_args_is_help=True,
)


def _run_pytest(
    target: str,
    cov: bool = False,
    cov_report: bool = False,
    parallel: bool = False,
    extra_args: Optional[list[str]] = None,
) -> None:
    """Helper to construct and execute pytest commands.

    Args:
        target: Target test file or directory path.
        cov: Whether to collect coverage for pni.
        cov_report: Whether to print coverage report in terminal.
        parallel: Whether to run tests in parallel using pytest-xdist.
        extra_args: Additional arguments forwarded to pytest.
    """
    cmd = ["uv", "run", "pytest", "-s"]
    if parallel:
        cmd.extend(["-n", "auto", "--dist", "loadfile"])
    if cov:
        cmd.append("--cov=pni")
        if cov_report:
            cmd.append("--cov-report=term-missing")
    cmd.append(target)
    if extra_args:
        cmd.extend(extra_args)

    run_command(cmd, desc=f"Running pytest on {target}...")


@app.command("all")
def test_all(
    cov: bool = typer.Option(True, "--cov/--no-cov", help="Enable/disable coverage tracking."),
    cov_report: bool = typer.Option(False, "--cov-report", help="Show line-by-line coverage report."),
    parallel: bool = typer.Option(False, "--parallel/--no-parallel", help="Run tests in parallel via pytest-xdist."),
) -> None:
    """Run the complete test suite across all tests (pni + pcli).

    Args:
        cov: Whether to run coverage.
        cov_report: Whether to output terminal coverage report.
        parallel: Whether to run tests in parallel.
    """
    _run_pytest("tests/", cov=cov, cov_report=cov_report, parallel=parallel)
    console.print("[bold green]✓ All tests passed successfully![/bold green]")


@app.command("pni")
def test_pni(
    cov: bool = typer.Option(True, "--cov/--no-cov", help="Enable/disable coverage tracking."),
    cov_report: bool = typer.Option(False, "--cov-report", help="Show line-by-line coverage report."),
    parallel: bool = typer.Option(False, "--parallel/--no-parallel", help="Run tests in parallel via pytest-xdist."),
) -> None:
    """Run unit tests for pni package.

    Args:
        cov: Whether to run coverage.
        cov_report: Whether to output terminal coverage report.
        parallel: Whether to run tests in parallel.
    """
    _run_pytest("tests/pni/", cov=cov, cov_report=cov_report, parallel=parallel)
    console.print("[bold green]✓ All pni tests passed successfully![/bold green]")


@app.command("pcli")
def test_pcli(
    cov: bool = typer.Option(False, "--cov/--no-cov", help="Enable/disable coverage tracking."),
) -> None:
    """Run tests for pcli developer CLI tools.

    Args:
        cov: Whether to collect coverage.
    """
    _run_pytest("tests/pcli/", cov=cov)
    console.print("[bold green]✓ All pcli tests passed successfully![/bold green]")


MODULE_SHORTCUTS: dict[str, str] = {
    "pni": "tests/pni/",
    "pcli": "tests/pcli/",
}


@app.command("target")
def test_target(
    target: str = typer.Argument(
        ...,
        help="Module shortcut keyword (e.g. 'pni', 'pcli') or test file/directory path.",
    ),
    cov: bool = typer.Option(False, "--cov/--no-cov", help="Enable/disable coverage tracking."),
    cov_report: bool = typer.Option(False, "--cov-report", help="Show line-by-line coverage report."),
    parallel: bool = typer.Option(False, "--parallel/--no-parallel", help="Run tests in parallel via pytest-xdist."),
) -> None:
    """Run pytest targeting a specific module shortcut or file/directory path.

    Args:
        target: Shorthand module name or path.
        cov: Whether to run coverage.
        cov_report: Whether to output terminal coverage report.
        parallel: Whether to run tests in parallel.
    """
    resolved_target = MODULE_SHORTCUTS.get(target, target)
    _run_pytest(resolved_target, cov=cov, cov_report=cov_report, parallel=parallel)
    console.print(f"[bold green]✓ Target tests for '{target}' passed successfully![/bold green]")


if __name__ == "__main__":
    app()
