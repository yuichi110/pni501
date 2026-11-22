# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""CLI commands for inspecting, triggering, and syncing extra Tree-sitter grammar release assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.panel import Panel
from rich.table import Table

from pni._languages._grammar_assets import (
    DEFAULT_GRAMMAR_RELEASE_TAG,
    PINNED_GRAMMAR_ASSETS,
)
from tools.pcli.common import PROJECT_ROOT, console, err_console
from tools.pcli.release_assets.client import (
    GitHubGrammarAssetsClient,
    resolve_github_token,
    sync_manifest_into_source,
)

app = typer.Typer(
    name="release-assets",
    help="Inspect, trigger GitHub Actions builds, and sync pinned SHA-256 digests for extra grammar assets.",
    no_args_is_help=True,
)

TARGET_SOURCE_PY = PROJECT_ROOT / "src" / "pni" / "_languages" / "_grammar_assets.py"


@app.command("list")
def list_pinned_assets() -> None:
    """List all pinned (grammar × platform) release assets in _grammar_assets.py."""
    table = Table(
        title=f"Pinned Grammar Release Assets (tag={DEFAULT_GRAMMAR_RELEASE_TAG}, count={len(PINNED_GRAMMAR_ASSETS)})",
        title_style="bold green",
        header_style="bold blue",
    )
    table.add_column("Asset ID", style="bold yellow")
    table.add_column("Platform", style="cyan")
    table.add_column("Archive Name", style="white")
    table.add_column("Size", style="dim", justify="right")
    table.add_column("SHA-256", style="green")

    for (_, _), asset in sorted(PINNED_GRAMMAR_ASSETS.items()):
        size_kb = f"{asset.size / 1024:.1f} KB" if asset.size else "-"
        sha_short = f"{asset.sha256[:12]}...{asset.sha256[-8:]}" if asset.sha256 else "-"
        table.add_row(asset.asset_id, asset.platform_tag, asset.archive_name, size_kb, sha_short)

    console.print(table)
    if not PINNED_GRAMMAR_ASSETS:
        console.print(
            "[yellow]No pinned hashes recorded yet. Run GitHub Actions build and then "
            "'./pcli release-assets sync'.[/yellow]"
        )


@app.command("remote")
def inspect_remote(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="GitHub Release tag (defaults to pinned tag)."),
    token: Optional[str] = typer.Option(None, "--token", help="Optional GitHub token."),
) -> None:
    """Inspect published GitHub Release assets and compare hashes against local _grammar_assets.py."""
    resolved_tag = tag or DEFAULT_GRAMMAR_RELEASE_TAG
    client = GitHubGrammarAssetsClient(token=resolve_github_token(token))
    console.print(f"[bold cyan]Querying GitHub Release '{resolved_tag}'...[/bold cyan]")

    release = client.get_release_by_tag(resolved_tag)
    if release is None:
        console.print(
            Panel(
                f"[yellow]GitHub Release '[bold]{resolved_tag}[/bold]' does not exist yet.[/yellow]\n"
                f"Push tag [bold]{resolved_tag}[/bold] or run [bold]./pcli release-assets trigger --tag {resolved_tag}[/bold].",
                title="Remote Grammar Release Status",
                border_style="yellow",
            )
        )
        return

    remote_assets = {a["name"]: a for a in release.get("assets", [])}
    manifest = client.fetch_remote_manifest(resolved_tag)
    entries = manifest.get("assets", [])

    table = Table(
        title=f"Remote GitHub Release '{resolved_tag}' ({len(entries)} manifest entries, {len(remote_assets)} files)",
        title_style="bold green",
        header_style="bold blue",
    )
    table.add_column("Asset", style="bold yellow")
    table.add_column("Platform", style="cyan")
    table.add_column("Archive", style="white")
    table.add_column("Size", style="dim", justify="right")
    table.add_column("Sync Status", style="bold")

    for entry in entries:
        key = (str(entry["asset_id"]), str(entry["platform"]))
        archive = str(entry["archive_name"])
        remote_file = remote_assets.get(archive)
        size_kb = f"{int(entry.get('size', 0)) / 1024:.1f} KB"
        pinned = PINNED_GRAMMAR_ASSETS.get(key)
        if remote_file is None:
            status = "[red]Missing file on release[/red]"
        elif pinned is None:
            status = "[yellow]Not pinned locally[/yellow]"
        elif pinned.sha256.lower() == str(entry["sha256"]).lower():
            status = "[green]Synchronized[/green]"
        else:
            status = "[yellow]Hash mismatch[/yellow]"
        table.add_row(key[0], key[1], archive, size_kb, status)

    console.print(table)


@app.command("sync")
def sync_assets(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="GitHub Release tag to sync manifest from."),
    manifest_file: Optional[Path] = typer.Option(
        None,
        "--manifest",
        "-m",
        help="Optional local manifest.json path instead of downloading from GitHub Releases.",
    ),
    check: bool = typer.Option(False, "--check", "-c", help="Check synchronization without modifying source file."),
    token: Optional[str] = typer.Option(None, "--token", help="Optional GitHub token."),
) -> None:
    """Sync published manifest.json SHA-256 digests into src/pni/_languages/_grammar_assets.py."""
    resolved_tag = tag or DEFAULT_GRAMMAR_RELEASE_TAG
    if manifest_file is not None:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    else:
        client = GitHubGrammarAssetsClient(token=resolve_github_token(token))
        console.print(f"[bold cyan]Fetching manifest.json from GitHub Release '{resolved_tag}'...[/bold cyan]")
        try:
            manifest = client.fetch_remote_manifest(resolved_tag)
        except Exception as exc:
            err_console.print(f"[bold red]Failed to fetch manifest.json for '{resolved_tag}': {exc}[/bold red]")
            raise typer.Exit(code=1) from exc

    in_sync = sync_manifest_into_source(manifest, TARGET_SOURCE_PY, check_only=check)
    if check:
        if not in_sync:
            err_console.print(
                "[bold red]src/pni/_languages/_grammar_assets.py is out of sync. "
                "Run './pcli release-assets sync' to update.[/bold red]"
            )
            raise typer.Exit(code=1)
        console.print("[bold green]✓ _grammar_assets.py is synchronized with manifest.json![/bold green]")
        return

    count = len(manifest.get("assets", []))
    console.print(f"[bold green]★ Synchronized {count} pinned grammar assets into {TARGET_SOURCE_PY}![/bold green]")


@app.command("runs")
def list_workflow_runs(
    limit: int = typer.Option(5, "--limit", "-n", help="Maximum number of recent workflow runs to show."),
    token: Optional[str] = typer.Option(None, "--token", help="Optional GitHub token."),
) -> None:
    """Show recent GitHub Actions runs of build-grammar-assets.yml."""
    client = GitHubGrammarAssetsClient(token=resolve_github_token(token))
    runs = client.list_workflow_runs(per_page=limit)
    table = Table(title="Recent Grammar Asset Build Runs", title_style="bold green", header_style="bold blue")
    table.add_column("Run ID", style="cyan")
    table.add_column("Status", style="bold yellow")
    table.add_column("Conclusion", style="bold")
    table.add_column("Branch / Tag", style="white")
    table.add_column("Created", style="dim")
    for r in runs:
        concl = r.get("conclusion") or "-"
        concl_style = "[green]success[/green]" if concl == "success" else concl
        table.add_row(
            str(r.get("id", "")),
            str(r.get("status", "")),
            concl_style,
            str(r.get("head_branch", "")),
            str(r.get("created_at", ""))[:19],
        )
    console.print(table)


@app.command("trigger")
def trigger_build(
    tag: str = typer.Option(
        DEFAULT_GRAMMAR_RELEASE_TAG,
        "--tag",
        "-t",
        help="GitHub Release tag to build and publish.",
    ),
    ref: str = typer.Option("main", "--ref", help="Git ref (branch or tag) to run the workflow from."),
    token: Optional[str] = typer.Option(None, "--token", help="GitHub token with workflow write permission."),
) -> None:
    """Trigger build-grammar-assets.yml on GitHub Actions via REST API."""
    client = GitHubGrammarAssetsClient(token=resolve_github_token(token))
    try:
        client.trigger_workflow(tag, ref=ref, publish_release=True)
    except Exception as exc:
        err_console.print(f"[bold red]Failed to trigger workflow: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc
    console.print(
        f"[bold green]✓ Dispatched build-grammar-assets.yml[/bold green] (ref={ref}, release_tag={tag})"
    )
