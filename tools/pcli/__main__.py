# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""PNI501 Development CLI (pcli) Master Launcher.

Acts as the entry point when pcli is executed without specifying a toolset.
Discovers available toolset modules in tools/pcli and renders a formatted summary.
"""

from __future__ import annotations

import contextlib
import importlib
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tools.pcli.common import discover_toolsets

app = typer.Typer(help="PNI501 Development CLI Launcher")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,  # noqa: ARG001
    invalid_toolset: Optional[str] = typer.Option(
        None,
        "--invalid-toolset",
        hidden=True,
        help="Internal option to display formatted error for invalid toolset names.",
    ),
) -> None:
    """PNI501 CLI Master Launcher.

    Args:
        ctx: Typer context object.
        invalid_toolset: Optional invalid toolset name provided via internal delegation.

    Raises:
        typer.Exit: Exits with code 1 if invalid_toolset is set.
    """
    console = Console()

    if invalid_toolset:
        console.print()
        console.print(
            Panel(
                f"[red]Toolset [bold]{invalid_toolset}[/bold] is not a valid toolset under 'tools/pcli/'.[/red]\n\n"
                f"Run [bold]./pcli[/bold] without arguments to view all active toolsets.",
                title="Error: Invalid Toolset",
                border_style="red",
                expand=False,
            )
        )
        console.print()
        raise typer.Exit(code=1)

    available_toolsets = discover_toolsets()

    console.print()
    console.print("[bold cyan]PNI501 Development CLI (pcli)[/bold cyan]")
    console.print("[dim]Usage: ./pcli <toolset> [command] [options][/dim]")
    console.print()

    table = Table(title="Available Toolsets", title_style="bold green", show_header=True, header_style="bold blue")
    table.add_column("Toolset", style="bold yellow", width=16)
    table.add_column("Description", style="white")

    for toolset in available_toolsets:
        desc = "No description available."
        with contextlib.suppress(Exception):
            mod_name = toolset.replace("-", "_")
            mod = importlib.import_module(f"tools.pcli.{mod_name}")
            if mod.__doc__:
                lines = [line.strip() for line in mod.__doc__.splitlines() if line.strip()]
                if lines:
                    desc = lines[0]
        table.add_row(toolset, desc)

    console.print(table)
    console.print()
    console.print("[dim]Example: ./pcli code-check all[/dim]")
    console.print("[dim]         ./pcli test all[/dim]")
    console.print("[dim]         ./pcli pypi check-version[/dim]")
    console.print()


if __name__ == "__main__":
    app()
