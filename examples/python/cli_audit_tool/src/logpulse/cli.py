"""Typer CLI entry point adhering to clig.dev stdout/stderr and exit-code conventions."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import typer
from rich.console import Console

from logpulse.analyzer import build_scan_report
from logpulse.formatter import build_rich_table, render_json_report
from logpulse.parser import parse_jsonl_lines, parse_severity

app = typer.Typer(name="logpulse", help="Triage structured JSONL logs for recurring error bursts.", no_args_is_help=True)


@app.command("scan")
def scan_cmd(
    log_file: Path = typer.Argument(..., help="Path to input .jsonl log file."),
    min_level: str = typer.Option("ERROR", "--min-level", "-l", help="Minimum severity (WARN, ERROR, CRITICAL)."),
    output_format: Literal["table", "json"] = typer.Option("table", "--format", "-f", help="Output format."),
    fail_above: int = typer.Option(0, "--fail-above", help="Exit with code 1 when matched events exceed threshold."),
    no_color: bool = typer.Option(False, "--no-color", help="Disable ANSI colors for CI environments."),
) -> None:
    """Scan a JSONL log file and print grouped error signatures to stdout."""
    out_console = Console(no_color=no_color)
    err_console = Console(stderr=True, no_color=no_color)

    if not log_file.is_file():
        err_console.print(f"Error: Log file '{log_file}' does not exist.")
        raise typer.Exit(code=2)

    lines = log_file.read_text(encoding="utf-8").splitlines()
    events, skipped = parse_jsonl_lines(lines)
    if skipped > 0:
        err_console.print(f"Warning: Skipped {skipped} malformed JSONL line(s).")

    report = build_scan_report(events, skipped_lines=skipped, min_level=parse_severity(min_level))
    if output_format == "json":
        print(render_json_report(report))
    else:
        out_console.print(build_rich_table(report))

    if fail_above > 0 and report.matched_events > fail_above:
        raise typer.Exit(code=1)
