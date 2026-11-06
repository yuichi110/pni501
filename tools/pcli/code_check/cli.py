# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Code quality and static analysis toolset (Ruff, Ty, line count)."""

from __future__ import annotations

import os
from pathlib import Path

import typer

from tools.pcli.code_check.lines import run_count_lines
from tools.pcli.common import PROJECT_ROOT, console, run_command

app = typer.Typer(
    name="code-check",
    help="Perform linting, static type checking, and line counts.",
    no_args_is_help=True,
)


@app.command("lint")
def lint(
    fix: bool = typer.Option(False, "--fix", "-f", help="Automatically fix fixable lint issues."),
) -> None:
    """Run Ruff linter and formatter across project targets.

    Args:
        fix: If True, automatically fix fixable lint issues.
    """
    targets = ["src", "tests", "tools"]
    existing_targets = [t for t in targets if (PROJECT_ROOT / t).exists()]
    for target in existing_targets:
        cmd = ["uv", "run", "ruff", "check"]
        if fix:
            cmd.append("--fix")
        cmd.append(target)
        run_command(cmd, desc=f"Running Ruff on {target}...")
    console.print("[bold green]✓ All lint checks passed![/bold green]")


@app.command("type")
def type_check() -> None:
    """Run Ty static type checker across project targets."""
    targets = ["src/pni", "tests", "tools"]
    existing_targets = [t for t in targets if (PROJECT_ROOT / t).exists()]
    for target in existing_targets:
        run_command(
            ["uv", "run", "ty", "check", target],
            desc=f"Running Ty type checker on {target}...",
        )
    console.print("[bold green]✓ All type checks passed![/bold green]")


@app.command("lines")
def count_lines() -> None:
    """Count source code lines in the project."""
    run_count_lines()


@app.command("all")
def check_all(
    fix: bool = typer.Option(False, "--fix", "-f", help="Automatically fix fixable lint issues."),
) -> None:
    """Run all primary checks (lint, type).

    Args:
        fix: If True, automatically fix fixable lint issues.
    """
    console.print("[bold cyan]Running all code quality checks...[/bold cyan]")
    lint(fix=fix)
    type_check()
    console.print("\n[bold green]★ All quality checks passed successfully![/bold green]\n")


if __name__ == "__main__":
    app()
