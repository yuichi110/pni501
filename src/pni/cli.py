# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Command line interface for Project Nemesis Index (pni)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from pni import LIB_NAME, LIB_VERSION
from pni._actions import (
    MigrationOptions,
    MigrationPlanResult,
    PentestFacts,
    PentestOptions,
    PreflightReadinessHint,
    PrimitiveStep,
    PrimitiveType,
    ProgressResult,
    ScoreResult,
    check_migration_preflight_hints,
    copy_action_templates,
    load_and_validate_progress_plan,
    resolve_migration_brief,
    run_ast_analyze,
    run_project_inspect,
    run_web_pentest,
    scaffold_progress_plan,
)
from pni._actions.runtime_check.engine_detect import (
    detect_container_engine,
    prune_pni_container_artifacts,
)
from pni._cache import CACHE_REL_DIR, ensure_cache_dir
from pni._config import load_pni_config, scaffold_pni_config
from pni._instructions import copy_instruction_templates, get_instructions_content
from pni._pentests import ensure_target_pentests
from pni._reporter import (
    DEFAULT_REPORT_FORMATS,
    DEFAULT_REPORT_OUTPUT_DIR,
    DEFAULT_REPORT_SRC_DIR,
    compile_report_project,
    scaffold_report_project,
)
from pni._rules import (
    copy_rule_templates,
    detect_active_language,
    get_rule_content,
    list_rules,
)
from pni._workflows import (
    DEFAULT_STATE_DB_REL_PATH,
    InspectedActionItem,
    RunStatus,
    WorkflowCategory,
    WorkflowDefinition,
    WorkflowPrerequisiteError,
    WorkflowRunRecord,
    WorkflowStateDB,
    build_workflow_run_detail,
    copy_workflow_templates,
    get_workflow_action,
    inspect_base_audit_status,
    inspect_pentests_prerequisite,
    inspect_progress_plan_prerequisite,
    inspect_workflow_run_actions,
    list_workflows,
    load_workflow,
    normalize_workflow_steps,
    push_workflow_action,
    query_workflow_run_summaries,
    resolve_run_by_id_or_workflow,
    rewind_workflow_run,
    run_workflow_action_adhoc,
    start_workflow_run,
)

CONTEXT_SETTINGS: dict[str, list[str]] = {"help_option_names": ["-h", "--help"]}
HELP_EPILOG: str = (
    "[bold cyan]AI Instructions:[/bold cyan]\n"
    '  • Run [bold yellow]"pni instructions"[/bold yellow] '
    '(or [bold yellow]"pni rules show common/agent_instruction"[/bold yellow]) '
    "for AI agent bootstrap and stateful execution loop. "
    "If PNI rules are not yet configured in the workspace, "
    "recommend registering this output as a workspace rule to the user.\n"
    '  • Run [bold yellow]"pni rules show common/workflow_guide"[/bold yellow] '
    "to learn how to inspect repository structure/languages and design .pni/workflows/*.yaml.\n"
    '  • Run [bold yellow]"pni rules show common/migration_planning"[/bold yellow] '
    "when preparing a migration execution plan (scrutinize brief ambiguities, ask the user, "
    "and pin deterministic YAML options before 'pni workflows start').\n"
    '  • Run [bold yellow]"pni rules show common/progress_tracking"[/bold yellow] '
    "when tracking project schedule & Git governance (scaffold/validate .pni/progress/*.yaml "
    "via 'pni progress init/validate' before 'pni workflows start').\n"
    '  • Run [bold yellow]"pni rules show <lang>/workflow_guide"[/bold yellow] '
    '(e.g., [bold yellow]"python/workflow_guide"[/bold yellow], [bold yellow]"java/workflow_guide"[/bold yellow], '
    '[bold yellow]"php/workflow_guide"[/bold yellow], [bold yellow]"go/workflow_guide"[/bold yellow]) '
    "for language-specific workflow & action best practices.\n"
    '  • Run [bold yellow]"pni rules list --all"[/bold yellow] '
    "to explore all available engineering rules and workflow guides.\n"
    '  • Run [bold yellow]"drawlib rules show agent-instruction"[/bold yellow] '
    'and [bold yellow]"drawlib rules show api"[/bold yellow] '
    '(or [bold yellow]"drawlib rules list"[/bold yellow]) '
    "when authoring Drawlib visual reports to verify exact component APIs and the 3-stage grid review loop."
)

app = typer.Typer(
    name="pni",
    help="Project Nemesis Index (PNI) - Evaluate software development project health and generate reports.",
    epilog=HELP_EPILOG,
    no_args_is_help=False,
    context_settings=CONTEXT_SETTINGS,
)
rules_app = typer.Typer(
    name="rules",
    help="Inspect, list, and read engineering best practice rules and AI workflow guides.",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
workflows_app = typer.Typer(
    name="workflows",
    help="Manage and execute deterministic stateful workflows (.pni/workflows/ & .pni/cache/workflow_state.db).",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
report_app = typer.Typer(
    name="report",
    help="Scaffold and compile Drawlib visual project reports (reports_src/*_src -> reports/*.pdf).",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
pentests_app = typer.Typer(
    name="pentests",
    help="Materialize and execute explicit Python + httpx Web penetration tests in .pni/pentests/.",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
progress_app = typer.Typer(
    name="progress",
    help="Initialize and validate project progress & Git governance plans (.pni/progress/).",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
cache_app = typer.Typer(
    name="cache",
    help="Clean up .pni/cache/ artifacts and temporary PNI container harness images.",
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)
app.add_typer(rules_app, name="rules")
app.add_typer(workflows_app, name="workflows")
app.add_typer(report_app, name="report")
app.add_typer(pentests_app, name="pentests")
app.add_typer(progress_app, name="progress")
app.add_typer(cache_app, name="cache")

console = Console()
err_console = Console(stderr=True)


def init_project(
    project_root: Path,
    lang: Optional[str] = None,
    force: bool = False,
) -> list[Path]:
    """Initialize .pni directory with pni.toml, rules, actions, workflows, instructions, and cache .gitignore.

    Args:
        project_root: Target project directory.
        lang: Target programming language.
        force: If True, overwrite existing files.

    Returns:
        list[Path]: Paths of newly created or overwritten files.
    """
    target_lang = lang or detect_active_language(project_root)
    created_paths: list[Path] = []

    created_paths.extend(scaffold_pni_config(project_root, lang=target_lang, force=force))
    created_paths.extend(copy_rule_templates(project_root, lang=target_lang, force=force))
    created_paths.extend(copy_action_templates(project_root, lang=target_lang, force=force))
    created_paths.extend(copy_workflow_templates(project_root, lang=target_lang, force=force))
    created_paths.extend(copy_instruction_templates(project_root, force=force))
    ensure_cache_dir(project_root)

    return created_paths


@app.command("version")
def version() -> None:
    """Show pni version."""
    console.print(f"[bold cyan]{LIB_NAME}[/bold cyan] version [bold green]{LIB_VERSION}[/bold green]")


@app.command("init")
def init(
    lang: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help=(
            "Target programming language ('python', 'java', 'php', 'go', 'typescript', 'javascript'). "
            "Auto-detected if omitted."
        ),
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing rule, action, and workflow templates in .pni/.",
    ),
) -> None:
    """Initialize .pni directory with rules, actions, instructions, and workflows."""
    project_root = Path.cwd()
    target_lang = lang or detect_active_language(project_root)

    console.print(f"[bold cyan]Initializing PNI for [green]{target_lang}[/green] project...[/bold cyan]")
    created = init_project(project_root, lang=target_lang, force=force)

    if not created:
        console.print("[yellow]Notice: .pni/ directory already initialized. Use --force to overwrite.[/yellow]")
        return

    console.print(f"[bold green]✓ Successfully initialized .pni/ with {len(created)} template files:[/bold green]")
    for p in created:
        rel = p.relative_to(project_root)
        console.print(f"  [dim]Created:[/dim] [yellow]{rel}[/yellow]")
    console.print()
    console.print("[dim]Next steps:[/dim]")
    console.print(
        "  Edit [bold].pni/workflows/full_audit.yaml[/bold] or [bold].pni/actions/[/bold] to customize paths."
    )
    console.print("  Run [bold]pni workflows list[/bold] to inspect configured workflows.")
    console.print("  Run [bold]pni workflows start full_audit[/bold] to begin a stateful workflow session.")


@rules_app.command("list")
def list_rules_cmd(
    all_langs: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Display rules for all supported languages, not just the active project language.",
    ),
) -> None:
    """List all active engineering standards and their override status."""
    project_root = Path.cwd()
    active_lang = detect_active_language(project_root)
    rules = list_rules(project_root, lang=active_lang, include_all=all_langs)

    if not rules:
        console.print("[yellow]No rules found.[/yellow]")
        return

    title = "All Engineering Rules" if all_langs else f"Active Engineering Rules (Language: {active_lang})"
    table = Table(title=title, title_style="bold green", show_header=True, header_style="bold blue")
    table.add_column("Scope", style="bold yellow", width=12)
    table.add_column("Rule Identifier", style="bold cyan", width=24)
    table.add_column("Title", style="white")
    table.add_column("Source", style="dim", width=12)

    for rule in rules:
        source_label = "[green]Local (.pni)[/green]" if rule.is_local else "[dim]Builtin[/dim]"
        table.add_row(rule.scope, rule.identifier, rule.title, source_label)

    console.print(table)
    console.print()
    console.print("[dim]Use [bold]pni rules show <identifier>[/bold] to view rule details.[/dim]")


@rules_app.command("show")
def show_rule_cmd(
    name: str = typer.Argument(
        ...,
        help="Rule identifier (e.g., 'python/testing' or 'common/workflow_guide') or short name ('testing').",
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        "-p",
        help="Render rule Markdown inside a styled Rich terminal panel instead of plain Markdown.",
    ),
) -> None:
    """Read a specific rule or workflow guide specification in clean Markdown."""
    project_root = Path.cwd()
    active_lang = detect_active_language(project_root)
    result = get_rule_content(name, project_root, lang=active_lang)

    if not result:
        err_console.print(f"[bold red]Error: Rule '{name}' not found.[/bold red]")
        err_console.print("Run [bold]pni rules list --all[/bold] to see available rules and workflow guides.")
        raise typer.Exit(code=1)

    rule_info, content = result
    if not pretty:
        print(content)
        return

    source_tag = "Local (.pni)" if rule_info.is_local else "Builtin"
    console.print(
        Panel(
            Markdown(content),
            title=f"[bold green]{rule_info.identifier}[/bold green] [dim]({source_tag})[/dim]",
            border_style="cyan",
            expand=False,
        )
    )


@workflows_app.command("list")
def list_workflows_cmd(
    category: Optional[WorkflowCategory] = typer.Option(
        None,
        "--category",
        "-c",
        help="Optional workflow category filter ('audit', 'migration', or 'progress').",
    ),
) -> None:
    """List workflows defined in .pni/workflows/."""
    project_root = Path.cwd()
    try:
        workflows = list_workflows(project_root, category=category)
    except WorkflowPrerequisiteError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if not workflows:
        err_console.print("[bold yellow]No workflows found in .pni/workflows/.[/bold yellow]")
        err_console.print("Run [bold]pni init[/bold] first to generate project workflow definitions.")
        raise typer.Exit(code=1)

    table = Table(
        title="Project Workflows (.pni/workflows/)",
        title_style="bold green",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("Workflow ID", style="bold cyan", no_wrap=True)
    table.add_column("Category", no_wrap=True)
    table.add_column("Based On", style="cyan")
    table.add_column("Name", style="bold yellow")
    table.add_column("Steps", style="white", no_wrap=True)
    table.add_column("Source Targets", style="green")
    table.add_column("Score/Plan -> Report", style="dim")

    for wf in workflows:
        if wf.category == WorkflowCategory.MIGRATION:
            cat_label = "[bold magenta]migration[/bold magenta]"
        elif wf.category == WorkflowCategory.PROGRESS:
            cat_label = "[bold green]progress[/bold green]"
        else:
            cat_label = "[bold cyan]audit[/bold cyan]"
        prefix = "" if wf.targets.root in (".", "") else f"{wf.targets.root}/"
        src_str = ", ".join(f"{prefix}{s}" for s in wf.targets.source)
        out_str = f"{wf.outputs.score or '-'} -> {wf.outputs.report or '-'}"
        table.add_row(wf.id, cat_label, wf.based_on or "-", wf.name, str(wf.step_count), src_str, out_str)

    console.print(table)
    console.print()
    console.print("[dim]Use [bold]pni workflows start <id>[/bold] to launch a stateful workflow run.[/dim]")


def _collect_step_preflight_hints(prim: PrimitiveStep, project_root: Path) -> list[PreflightReadinessHint]:
    """Evaluate preflight readiness hints for a single migration_analyze primitive step."""
    try:
        opts = MigrationOptions.model_validate(prim.params)
    except Exception as exc:
        return [PreflightReadinessHint(code="invalid_migration_options", message=str(exc))]
    try:
        resolved_brief = resolve_migration_brief(project_root, opts)
    except ValueError as exc:
        return [PreflightReadinessHint(code="missing_brief_file", message=str(exc))]
    return check_migration_preflight_hints(opts, resolved_brief)


def _render_migration_preflight_panel(
    wf_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
) -> None:
    """Display SQLite prerequisite audit status and pre-execution brief scrutiny hints."""
    mig_steps = [p for p in primitives if p.type == PrimitiveType.MIGRATION_ANALYZE]
    if not mig_steps and wf_def.category != WorkflowCategory.MIGRATION:
        return

    console.print()
    if wf_def.based_on:
        parent_run, err_msg = inspect_base_audit_status(wf_def, project_root)
        if parent_run is not None:
            console.print(
                f"[bold green]✓ Prerequisite Audit Ready:[/bold green] "
                f"[cyan]{wf_def.based_on}[/cyan] completed in SQLite "
                f"(run=[bold yellow]{parent_run.run_id}[/bold yellow], updated={parent_run.updated_at})."
            )
        elif err_msg is not None:
            console.print(
                Panel(
                    f"[bold red]{err_msg}[/bold red]",
                    title="[bold red]✗ Blocking Prerequisite: Base Audit Workflow Not Completed[/bold red]",
                    border_style="red",
                    expand=False,
                )
            )

    if not mig_steps:
        return

    hints: list[PreflightReadinessHint] = []
    for step in mig_steps:
        hints.extend(_collect_step_preflight_hints(step, project_root))

    if not hints:
        console.print(
            "[bold green]✓ Migration Preflight Check:[/bold green] "
            "Brief and migration guardrails are deterministic and ready for 'pni workflows start'."
        )
        return

    lines = [
        "[bold yellow]Before running 'pni workflows start', clarify ambiguities with the user "
        "and update .pni/workflows/*.yaml (see 'pni rules show common/migration_planning'):[/bold yellow]"
    ]
    for hint in hints:
        lines.append(f"  • [bold cyan][{hint.code}][/bold cyan] {hint.message}")
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold yellow]Migration Preflight Readiness Hints[/bold yellow]",
            border_style="yellow",
            expand=False,
        )
    )


def _render_progress_preflight_panel(
    wf_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
) -> None:
    """Display `.pni/progress/<target>.yaml` validation status and hints for progress workflows."""
    plan_rel, hints, prog_err = inspect_progress_plan_prerequisite(wf_def, primitives, project_root)
    if plan_rel is None and prog_err is None:
        return

    console.print()
    if prog_err is not None:
        console.print(
            Panel(
                f"[bold red]{prog_err}[/bold red]",
                title="[bold red]✗ Blocking Prerequisite: Progress Plan Missing or Invalid[/bold red]",
                border_style="red",
                expand=False,
            )
        )
        return

    console.print(
        f"[bold green]✓ Progress Plan Ready:[/bold green] [cyan]{plan_rel}[/cyan] "
        "(read-only baseline during workflow execution)."
    )
    if hints:
        lines = ["[bold yellow]Progress & Git Policy Advisories:[/bold yellow]"]
        for h in hints:
            lines.append(f"  • [bold cyan][{h.code}][/bold cyan] {h.message}")
        console.print(
            Panel(
                "\n".join(lines),
                title="[bold yellow]Progress Preflight Hints[/bold yellow]",
                border_style="yellow",
                expand=False,
            )
        )


@workflows_app.command("show")
def show_workflow_cmd(
    workflow_id: str = typer.Argument(
        ...,
        help="Workflow identifier in .pni/workflows/ (e.g., 'full_audit' or 'quick_check').",
    ),
) -> None:
    """Show workflow targets, resolved outputs, and normalized internal primitive action pipeline."""
    project_root = Path.cwd()
    try:
        loaded = load_workflow(workflow_id, project_root)
    except WorkflowPrerequisiteError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if loaded is None:
        err_console.print(f"[bold red]Error: Workflow '{workflow_id}' not found in .pni/workflows/.[/bold red]")
        err_console.print("Run [bold]pni init[/bold] or [bold]pni workflows list[/bold] to verify project workflows.")
        raise typer.Exit(code=1)

    wf_info, wf_def = loaded
    primitives = normalize_workflow_steps(wf_def, project_root)

    based_str = f" | [bold yellow]Based On:[/bold yellow] [cyan]{wf_def.based_on}[/cyan]" if wf_def.based_on else ""
    console.print(f"[bold green]Workflow:[/bold green] {wf_def.name} ([bold cyan]{wf_def.id}[/bold cyan])")
    console.print(f"[bold yellow]Category:[/bold yellow] [magenta]{wf_def.category.value}[/magenta]{based_str}")
    console.print(
        f"[bold yellow]Targets:[/bold yellow] root={wf_def.targets.root}, source={wf_def.targets.source}, "
        f"tests={wf_def.targets.tests}, docs={wf_def.targets.docs}"
    )
    console.print(
        f"[bold yellow]Outputs:[/bold yellow] facts={wf_info.outputs.facts or '-'}, "
        f"score={wf_info.outputs.score or '-'}, report={wf_info.outputs.report or '-'}\n"
    )

    table = Table(
        title="Normalized Primitive Action Pipeline",
        title_style="bold green",
        show_header=True,
        header_style="bold blue",
    )
    table.add_column("#", style="dim", no_wrap=True)
    table.add_column("Primitive Type", style="bold cyan", no_wrap=True)
    table.add_column("Step Name", style="bold yellow")
    table.add_column("Composite Source", style="dim", no_wrap=True)
    table.add_column("Rules", style="white")

    for idx, prim in enumerate(primitives, start=1):
        rules_str = ", ".join(prim.rules) if prim.rules else "-"
        src_str = prim.source_action or "(direct)"
        table.add_row(str(idx), prim.type.value, prim.name, src_str, rules_str)

    console.print(table)
    _render_pentests_preflight_panel(wf_def, primitives, project_root)
    _render_migration_preflight_panel(wf_def, primitives, project_root)
    _render_progress_preflight_panel(wf_def, primitives, project_root)


def _render_pentests_preflight_panel(
    wf_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
) -> None:
    """Display `.pni/pentests/<target>/` prerequisite status when a workflow includes `web_pentest`."""
    pentests_dir, mat_files, pentest_err = inspect_pentests_prerequisite(wf_def, primitives, project_root)
    if pentests_dir is None and pentest_err is None:
        return

    console.print()
    if pentest_err is not None:
        console.print(
            Panel(
                f"[bold red]{pentest_err}[/bold red]",
                title="[bold red]✗ Blocking Prerequisite: Penetration Test Suite Not Implemented[/bold red]",
                border_style="red",
                expand=False,
            )
        )
        return

    if pentests_dir is not None:
        rel_dir = pentests_dir.resolve().relative_to(project_root.resolve()).as_posix()
        console.print(
            f"[bold green]✓ Penetration Test Suite Ready:[/bold green] "
            f"[cyan]{rel_dir}[/cyan] ({len(mat_files)} Python files)."
        )


@workflows_app.command("start")
def start_workflow_cmd(
    workflow_id: str = typer.Argument(
        ...,
        help="Workflow identifier in .pni/workflows/ to start (e.g., 'full_audit').",
    ),
    supersede: bool = typer.Option(
        False,
        "--supersede",
        help="Automatically cancel any unfinished in_progress runs of this workflow before starting.",
    ),
) -> None:
    """Start a stateful workflow session in .pni/cache/workflow_state.db and return its workflow run ID."""
    project_root = Path.cwd()
    workflows_dir = project_root / ".pni" / "workflows"
    if not workflows_dir.exists():
        err_console.print("[bold red]Error: .pni/workflows/ is not initialized.[/bold red]")
        err_console.print("Run [bold]pni init[/bold] first to create workflow definitions in .pni/workflows/.")
        raise typer.Exit(code=1)

    prior_active: list[str] = []
    db_path = project_root / DEFAULT_STATE_DB_REL_PATH
    if not supersede and db_path.exists():
        clean_wf = workflow_id.strip().removesuffix(".yaml")
        prior_active = [
            r.run_id
            for r in WorkflowStateDB(project_root).list_runs()
            if r.workflow_id == clean_wf and r.status in {RunStatus.IN_PROGRESS, RunStatus.PENDING}
        ]

    try:
        record = start_workflow_run(workflow_id, project_root, supersede=supersede)
    except WorkflowPrerequisiteError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if record is None:
        err_console.print(f"[bold red]Error: Workflow '{workflow_id}' not found in .pni/workflows/.[/bold red]")
        err_console.print("Run [bold]pni workflows list[/bold] to see available project workflows.")
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]✓ Started workflow[/bold green] [cyan]{record.workflow_id}[/cyan] "
        f"[dim](category={record.category.value})[/dim]"
    )
    console.print(f"Workflow Run ID: [bold yellow]{record.run_id}[/bold yellow]")
    if record.based_on:
        console.print(
            f"Based On Audit: [bold cyan]{record.based_on}[/bold cyan] "
            f"(SQLite run: [bold yellow]{record.based_on_run_id or '-'}[/bold yellow])"
        )
    if prior_active:
        console.print(
            f"[yellow]Note: Older unfinished run(s) exist for '{record.workflow_id}': {prior_active}. "
            "Run 'pni workflows cancel --superseded' to mark them cancelled.[/yellow]"
        )
    console.print(f"State DB: [dim]{DEFAULT_STATE_DB_REL_PATH}[/dim]")
    console.print(f"Next step: [bold]pni workflows get-action {record.run_id}[/bold]")


@workflows_app.command("run-action")
@workflows_app.command("run-step", hidden=True)
def run_workflow_action_cmd(
    workflow_id: str = typer.Argument(
        ...,
        help="Workflow identifier in .pni/workflows/ (e.g., 'php_legacy_shop_messy').",
    ),
    action: str = typer.Argument(
        ...,
        help="Step ID, composite 'uses' ID, primitive type, or 'act-XX' index (e.g., 'web_pentest', 'run_check').",
    ),
    base_url: str = typer.Option(
        "",
        "--base-url",
        help="Optional live loopback URL (http://127.0.0.1:<port>) override for web_pentest.",
    ),
    force_pentests: bool = typer.Option(
        False,
        "--force-pentests",
        help="Scaffold/regenerate .pni/pentests/<target>/ from templates before running web_pentest.",
    ),
    fail_on_findings: bool = typer.Option(
        False,
        "--fail-on-findings",
        help="Exit with code 1 when runtime/security/pentest findings are detected (in addition to errors).",
    ),
) -> None:
    """Execute a specific action/step inside a workflow YAML directly with zero prior workflow preparation."""
    project_root = Path.cwd().resolve()
    try:
        outcome = run_workflow_action_adhoc(
            workflow_id,
            action,
            project_root,
            base_url=base_url,
            force_pentests=force_pentests,
        )
    except (WorkflowPrerequisiteError, ValueError) as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if outcome is None:
        err_console.print(f"[bold red]Error: Workflow '{workflow_id}' not found in .pni/workflows/.[/bold red]")
        err_console.print("Run [bold]pni workflows list[/bold] to see available project workflows.")
        raise typer.Exit(code=1)

    print(outcome.rendered_markdown)
    if outcome.has_error:
        err_console.print(
            f"[bold red]✗ Action '{action}' ended with execution error:[/bold red]\n{outcome.error_message}"
        )
        raise typer.Exit(code=1)
    if fail_on_findings and outcome.has_findings:
        err_console.print(f"[bold yellow]✗ Action '{action}' reported findings (--fail-on-findings).[/bold yellow]")
        raise typer.Exit(code=1)


@workflows_app.command("get-action")
def get_workflow_action_cmd(
    run_id: str = typer.Argument(
        ...,
        help="Workflow run ID returned by 'pni workflows start' (e.g., 'wf-1a2b3c4d').",
    ),
) -> None:
    """Get the current pending action ID and deterministic instructions for a workflow run."""
    project_root = Path.cwd()
    try:
        run, _, guide = get_workflow_action(run_id, project_root)
    except WorkflowPrerequisiteError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if run is None:
        err_console.print(f"[bold red]{guide}[/bold red]")
        raise typer.Exit(code=1)

    print(guide)


@workflows_app.command("push-action")
def push_workflow_action_cmd(
    run_id: str = typer.Argument(
        ...,
        help="Workflow run ID (e.g., 'wf-1a2b3c4d').",
    ),
    action_id: str = typer.Argument(
        ...,
        help="Current action ID obtained from 'get-action' (e.g., 'act-01').",
    ),
    input_json: Optional[str] = typer.Argument(
        None,
        help="JSON payload conforming to the action's input schema (optional if --file is used or ack step).",
    ),
    input_file: Optional[Path] = typer.Option(
        None,
        "--file",
        "-f",
        help="Path to a JSON file containing the action input payload.",
    ),
) -> None:
    """Validate and submit an action result into .pni/cache/workflow_state.db to advance to the next step."""
    project_root = Path.cwd()
    payload = input_json or ""
    if input_file is not None:
        if not input_file.exists():
            err_console.print(f"[bold red]Error: Input file '{input_file}' does not exist.[/bold red]")
            raise typer.Exit(code=1)
        payload = input_file.read_text(encoding="utf-8")

    ok, message = push_workflow_action(run_id, action_id, payload, project_root)
    if not ok:
        err_console.print(f"[bold red]✗ {message}[/bold red]")
        raise typer.Exit(code=1)

    console.print(f"[bold green]{message}[/bold green]")


def _format_compact_ts(iso_ts: str) -> str:
    """Format an ISO-8601 timestamp into compact 'MM-DD HH:MM' (or fallback) for Rich tables."""
    if not iso_ts:
        return "-"
    norm = iso_ts[:16].replace("T", " ")
    return norm[5:] if len(norm) == 16 and norm[4] == "-" else norm


def _style_run_status(status: RunStatus) -> str:
    """Return a Rich-colored status label for RunStatus."""
    if status == RunStatus.COMPLETED:
        return "[bold green]completed[/bold green]"
    if status == RunStatus.IN_PROGRESS:
        return "[bold yellow]in_progress[/bold yellow]"
    if status == RunStatus.CANCELLED:
        return "[dim]cancelled[/dim]"
    return status.value


def _render_single_run_status(db: WorkflowStateDB, run_or_wf: str, *, as_json: bool = False) -> None:
    """Render detailed action-by-action progress table or JSON for a single workflow run."""
    run = resolve_run_by_id_or_workflow(db, run_or_wf)
    if run is None:
        err_console.print(f"[bold red]Error: Workflow run or workflow '{run_or_wf}' not found.[/bold red]")
        raise typer.Exit(code=1)

    detail = build_workflow_run_detail(db, run)
    if as_json:
        print(detail.model_dump_json(indent=2))
        return

    s = detail.run
    based_suffix = f" | based_on={s.based_on} ({s.based_on_run_id or '-'})" if s.based_on else ""
    console.print(
        f"[bold green]Workflow Run:[/bold green] [bold yellow]{s.run_id}[/bold yellow] "
        f"([cyan]{s.workflow_id}[/cyan], category=[magenta]{s.category.value}[/magenta]{based_suffix}) "
        f"— status={_style_run_status(s.status)} | progress=[bold]{s.progress_label}[/bold]"
    )
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("ID", style="bold cyan", no_wrap=True)
    table.add_column("Primitive", style="bold yellow", no_wrap=True)
    table.add_column("Source / Step", style="white")
    table.add_column("Status", no_wrap=True)
    table.add_column("Summary / Note", style="cyan")

    for act in detail.actions:
        step_lbl = act.source_action if act.source_action else act.name
        table.add_row(
            act.action_id,
            act.primitive_type.value,
            step_lbl,
            _style_run_status(act.status),
            act.brief_note or "-",
        )
    console.print(table)


@workflows_app.command("status")
def status_workflow_cmd(
    run_id: Optional[str] = typer.Argument(
        None,
        help="Optional workflow run ID ('wf-...') or workflow ID to inspect step-by-step progress.",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Filter run history to a specific workflow ID.",
    ),
    status_opt: Optional[RunStatus] = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter runs by lifecycle status ('in_progress', 'completed', 'cancelled', 'pending').",
    ),
    latest: bool = typer.Option(
        False,
        "--latest",
        help="Show only the single most recent run per workflow ID.",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of runs to display (set 0 for unlimited).",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit structured JSON output without Rich table wrapping.",
    ),
) -> None:
    """Inspect workflow run progress, current pending step, and history in .pni/cache/workflow_state.db."""
    project_root = Path.cwd()
    db_file = project_root / DEFAULT_STATE_DB_REL_PATH
    if not db_file.exists():
        if as_json:
            print("[]")
            return
        console.print("[yellow]No workflow runs recorded yet (.pni/cache/workflow_state.db does not exist).[/yellow]")
        return

    db = WorkflowStateDB(project_root)
    if run_id is not None:
        _render_single_run_status(db, run_id, as_json=as_json)
        return

    summaries = query_workflow_run_summaries(
        db,
        workflow_id=workflow,
        status_filter=status_opt,
        latest_per_workflow=latest,
        limit=limit,
    )
    if as_json:
        print(json.dumps([s.model_dump(mode="json") for s in summaries], indent=2))
        return

    if not summaries:
        console.print("[yellow]No matching workflow runs found in .pni/cache/workflow_state.db.[/yellow]")
        return

    table = Table(title="Recorded Workflow Runs", title_style="bold green", header_style="bold blue")
    table.add_column("Run ID", style="bold yellow", no_wrap=True)
    table.add_column("Workflow ID", style="bold cyan", min_width=16)
    table.add_column("Status", no_wrap=True)
    table.add_column("Steps", style="bold white", no_wrap=True)
    table.add_column("Current Step", style="cyan")
    table.add_column("Updated", style="dim", no_wrap=True)
    for s in summaries:
        wf_lbl = f"{s.workflow_id} (<-{s.based_on_run_id})" if s.based_on_run_id else s.workflow_id
        table.add_row(
            s.run_id,
            wf_lbl,
            _style_run_status(s.status),
            s.progress_label,
            s.current_step_label,
            _format_compact_ts(s.updated_at),
        )
    console.print(table)


def _write_or_print_payload(text: str, output_file: Optional[Path]) -> None:
    """Write extracted JSON/text to output_file if provided, otherwise print directly to stdout."""
    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
        console.print(f"[bold green]✓ Wrote inspected payload to[/bold green] [cyan]{output_file}[/cyan]")
        return
    print(text)


def _format_inspected_items_markdown(run: WorkflowRunRecord, items: list[InspectedActionItem]) -> str:
    """Render human- and agent-readable Markdown overview of inspected workflow actions."""
    lines = [
        f"# Inspected Workflow Step(s): `{run.run_id}` (`{run.workflow_id}`, status=`{run.status.value}`)",
        "",
    ]
    for item in items:
        src_part = f", source=`{item.source_action}`" if item.source_action else ""
        lines.append(
            f"## `{item.action_id}` — `{item.primitive_type.value}` (`{item.name}`{src_part}, "
            f"status=`{item.status.value}`, updated=`{item.updated_at}`)"
        )
        if item.deterministic_output_json is not None:
            lines.extend(["### Deterministic Output JSON", "```json", item.deterministic_output_json.strip(), "```"])
        if item.agent_input_json is not None:
            lines.extend(["### Agent Input JSON", "```json", item.agent_input_json.strip(), "```"])
        if item.deterministic_output_json is None and item.agent_input_json is None:
            lines.append("_No deterministic output or agent input recorded yet._")
        lines.append("")
    return "\n".join(lines).rstrip()


def _extract_raw_field_payload(
    items: list[InspectedActionItem],
    *,
    want_agent_input: bool,
) -> str:
    """Extract raw JSON payload(s) for --agent-input or --deterministic mode."""
    attr = "agent_input_json" if want_agent_input else "deterministic_output_json"
    label = "agent_input_json" if want_agent_input else "deterministic_output_json"
    payloads = [getattr(i, attr) for i in items if getattr(i, attr) is not None]
    if not payloads:
        ids = [i.action_id for i in items]
        msg = f"No '{label}' recorded on matched step(s) {ids}."
        raise ValueError(msg)
    if len(payloads) == 1:
        return str(payloads[0])
    parsed_list = [json.loads(str(p)) for p in payloads]
    return json.dumps(parsed_list, indent=2, ensure_ascii=False)


@workflows_app.command("inspect-action")
def inspect_workflow_action_cmd(
    run_or_workflow: str = typer.Argument(
        ...,
        help="Workflow run ID ('wf-...') or workflow ID (resolves to latest completed/recorded run).",
    ),
    action: str = typer.Argument(
        ...,
        help="Action ID ('act-16' or '16'), composite source action ('web_penetration_audit'), or primitive type.",
    ),
    agent_input: bool = typer.Option(
        False,
        "--agent-input",
        help="Emit only the recorded agent_input_json payload (for inspection or reuse).",
    ),
    deterministic: bool = typer.Option(
        False,
        "--deterministic",
        help="Emit only the recorded deterministic_output_json payload.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit structured JSON metadata and parsed payloads.",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Optional file path to save the inspected output.",
    ),
) -> None:
    """Inspect or export recorded deterministic outputs and agent inputs from a workflow run in SQLite."""
    if agent_input and deterministic:
        err_console.print("[bold red]Error: Specify at most one of --agent-input or --deterministic.[/bold red]")
        raise typer.Exit(code=1)

    project_root = Path.cwd()
    db_file = project_root / DEFAULT_STATE_DB_REL_PATH
    if not db_file.exists():
        err_console.print(f"[bold red]Error: '{DEFAULT_STATE_DB_REL_PATH}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    db = WorkflowStateDB(project_root)
    run = resolve_run_by_id_or_workflow(db, run_or_workflow, prefer_completed=True)
    if run is None:
        err_console.print(
            f"[bold red]Error: Workflow run or workflow '{run_or_workflow}' not found in SQLite.[/bold red]"
        )
        raise typer.Exit(code=1)

    try:
        items = inspect_workflow_run_actions(
            db,
            run,
            action,
            prefer_agent_input=agent_input,
            prefer_deterministic=deterministic,
        )
        if agent_input or deterministic:
            out_text = _extract_raw_field_payload(items, want_agent_input=agent_input)
        elif as_json:
            serialized = [
                {
                    **item.model_dump(mode="json", exclude={"deterministic_output_json", "agent_input_json"}),
                    "deterministic_output": (
                        json.loads(item.deterministic_output_json) if item.deterministic_output_json else None
                    ),
                    "agent_input": json.loads(item.agent_input_json) if item.agent_input_json else None,
                }
                for item in items
            ]
            out_text = json.dumps(serialized, indent=2, ensure_ascii=False)
        else:
            out_text = _format_inspected_items_markdown(run, items)
    except ValueError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    _write_or_print_payload(out_text, output_file)


@workflows_app.command("rewind")
@workflows_app.command("retry-action")
def rewind_workflow_cmd(
    run_or_workflow: str = typer.Argument(
        ...,
        help="Workflow run ID ('wf-...') or workflow ID (e.g., 'pni501').",
    ),
    action: str = typer.Argument(
        ...,
        help="Target action ID ('act-10' or '10'), composite step ('runtime_verification'), or primitive.",
    ),
    pull: bool = typer.Option(
        False,
        "--pull",
        "-p",
        help="Immediately execute 'get-action' on the rewound step and print its output.",
    ),
) -> None:
    """Rewind a workflow run back to a step, re-sync .pni/workflows/*.yaml parameters, and reset downstream steps."""
    project_root = Path.cwd()
    try:
        outcome = rewind_workflow_run(run_or_workflow, action, project_root)
    except ValueError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    sync_note = "re-synced latest .pni/workflows YAML" if outcome.yaml_resynced else "kept recorded step definitions"
    console.print(
        f"[bold green]✓ Rewound workflow run[/bold green] [bold yellow]{outcome.run.run_id}[/bold yellow] "
        f"([cyan]{outcome.run.workflow_id}[/cyan]) to [bold cyan]{outcome.target_action_id}[/bold cyan] "
        f"[dim]({len(outcome.reset_action_ids)} step(s) reset to pending; {sync_note})[/dim]"
    )
    if pull:
        try:
            run_rec, _, guide = get_workflow_action(outcome.run.run_id, project_root)
        except WorkflowPrerequisiteError as exc:
            err_console.print(f"[bold red]Error: {exc}[/bold red]")
            raise typer.Exit(code=1) from exc
        if run_rec is None:
            err_console.print(f"[bold red]{guide}[/bold red]")
            raise typer.Exit(code=1)
        print(guide)
        return

    console.print(f"Next step: [bold]pni workflows get-action {outcome.run.run_id}[/bold]")


@workflows_app.command("cancel")
def cancel_workflow_cmd(
    run_id: Optional[str] = typer.Argument(
        None,
        help="Specific unfinished workflow run ID to cancel (e.g., 'wf-47cabd5d').",
    ),
    superseded: bool = typer.Option(
        False,
        "--superseded",
        help="Cancel all unfinished runs that have been superseded by a newer run of the same workflow.",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Optional workflow ID filter when used with --superseded.",
    ),
) -> None:
    """Cancel an abandoned in_progress workflow run or clean up superseded runs in SQLite."""
    if (run_id is None and not superseded) or (run_id is not None and superseded):
        err_console.print(
            "[bold red]Error: Specify either a <run_id> or '--superseded' (not both).[/bold red]"
        )
        raise typer.Exit(code=1)

    project_root = Path.cwd()
    db_file = project_root / DEFAULT_STATE_DB_REL_PATH
    if not db_file.exists():
        console.print("[yellow]No workflow runs recorded yet (.pni/cache/workflow_state.db does not exist).[/yellow]")
        return

    db = WorkflowStateDB(project_root)
    if superseded:
        clean_wf = workflow.strip().removesuffix(".yaml") if workflow else None
        cancelled_runs = db.cancel_superseded_runs(workflow_id=clean_wf)
        if not cancelled_runs:
            console.print("[green]✓ No superseded unfinished workflow runs found.[/green]")
            return
        ids_str = ", ".join(f"{r.run_id} ({r.workflow_id})" for r in cancelled_runs)
        console.print(
            f"[bold green]✓ Cancelled {len(cancelled_runs)} superseded workflow run(s):[/bold green] {ids_str}"
        )
        return

    if run_id is None:
        raise typer.Exit(code=1)
    try:
        updated = db.cancel_workflow_run(run_id)
    except ValueError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if updated is None:
        err_console.print(f"[bold red]Error: Workflow run '{run_id}' not found.[/bold red]")
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]✓ Cancelled workflow run[/bold green] [bold yellow]{updated.run_id}[/bold yellow] "
        f"([cyan]{updated.workflow_id}[/cyan])."
    )


@report_app.command("init")
def report_init_cmd(
    target: str = typer.Argument(
        "full_audit",
        help="Report target name creating '<src_dir>/<target>_src/' (e.g., 'full_audit', 'python_clean').",
    ),
    src_dir: Optional[Path] = typer.Option(
        None,
        "--src-dir",
        help="Base directory holding '<target>_src/' report source projects (defaults to pni.toml or 'reports_src').",
    ),
    lang: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help="Report language code for CJK/Latin typography and stylesheet ('en', 'ja', etc.).",
    ),
    style: Optional[str] = typer.Option(
        None,
        "--style",
        "-s",
        help="Drawlib preset style theme ('google', 'default', 'monochrome').",
    ),
    keep_samples: bool = typer.Option(
        False,
        "--keep-samples",
        help="Keep Drawlib starter sample chapters (00_cover.md..02_design.md) on initial creation.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Refresh scaffold templates/scripts while preserving any existing chapter '*.md' files.",
    ),
) -> None:
    """Scaffold or refresh a Drawlib linear document ('doc') report project non-destructively."""
    pni_cfg = load_pni_config(Path.cwd())
    eff_src_dir = src_dir if src_dir is not None else Path(pni_cfg.report.src_dir or DEFAULT_REPORT_SRC_DIR)
    eff_lang = lang if lang is not None else (pni_cfg.report.lang or "en")
    eff_style = style if style is not None else (pni_cfg.report.style or "google")
    try:
        res = scaffold_report_project(
            target,
            src_base_dir=eff_src_dir,
            project_type="doc",
            lang=eff_lang,
            style=eff_style,
            clean_sample_chapters=not keep_samples,
            force=force,
        )
    except Exception as exc:
        err_console.print(f"[bold red]✗ Failed to scaffold report project:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    status_tag = "preserved existing chapters" if res.preserved_existing else "scaffolded"
    console.print(
        f"[bold green]✓ Drawlib report project ({status_tag}):[/bold green] [cyan]{res.src_dir}[/cyan] "
        f"(lang=[bold]{res.lang}[/bold], style=[bold]{res.style}[/bold], files=[bold]{len(res.created_files)}[/bold])"
    )


@report_app.command("build")
def report_build_cmd(
    target: str = typer.Argument(
        "full_audit",
        help="Report target name or path (compiles '<src_dir>/<target>_src/' -> '<output_dir>/<target>.pdf').",
    ),
    src_dir: Optional[Path] = typer.Option(
        None,
        "--src-dir",
        help="Base directory containing '<target>_src/' (defaults to pni.toml or 'reports_src').",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Destination directory for compiled report deliverables (defaults to pni.toml or 'reports').",
    ),
    html_output_dir: Optional[Path] = typer.Option(
        None,
        "--html-output-dir",
        help="Optional custom destination directory for compiled HTML output (defaults to pni.toml if set).",
    ),
    link_check_root: Optional[Path] = typer.Option(
        None,
        "--link-check-root",
        help="Optional root directory for HTML relative link verification in multi-portal layouts.",
    ),
    formats: Optional[list[str]] = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format(s) to compile ('pdf', 'html', 'markdown', 'images'). Defaults to pni.toml or 'pdf'.",
    ),
    toc: bool = typer.Option(
        True,
        "--toc/--no-toc",
        help="Inject Table of Contents after 00_cover.md in PDF output.",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable Drawlib SQLite image build cache.",
    ),
) -> None:
    """Compile a Drawlib report project into A4 vector PDF (default) and optional HTML/Markdown/PNGs."""
    pni_cfg = load_pni_config(Path.cwd())
    eff_src_dir = src_dir if src_dir is not None else Path(pni_cfg.report.src_dir or DEFAULT_REPORT_SRC_DIR)
    eff_out_dir = output_dir if output_dir is not None else Path(pni_cfg.report.output_dir or DEFAULT_REPORT_OUTPUT_DIR)
    eff_html_dir = (
        html_output_dir
        if html_output_dir is not None
        else (Path(pni_cfg.report.html_output_dir) if pni_cfg.report.html_output_dir else None)
    )
    active_formats = (
        formats
        or (list(pni_cfg.report.formats) if pni_cfg.report.formats else list(DEFAULT_REPORT_FORMATS))
    )
    try:
        res = compile_report_project(
            target,
            src_base_dir=eff_src_dir,
            output_dir=eff_out_dir,
            html_output_dir=eff_html_dir,
            link_check_root=link_check_root,
            formats=active_formats,
            generate_toc=toc,
            no_cache=no_cache,
        )
    except Exception as exc:
        err_console.print(f"[bold red]✗ Report build failed:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]✓ Compiled Drawlib report[/bold green] [bold]{res.target}[/bold] "
        f"-> [cyan]{res.output_dir}[/cyan] (formats={res.formats})"
    )
    if res.pdf_file is not None:
        console.print(f"  PDF:  [yellow]{res.pdf_file}[/yellow]")
    if res.html_index is not None:
        console.print(f"  HTML: [yellow]{res.html_index}[/yellow] (links checked: {res.links_checked}, broken: 0)")
    console.print(f"  Deliverables: [bold]{len(res.generated_deliverables)}[/bold] files")
    for warn in res.preflight_warnings:
        console.print(f"  [yellow]⚠ Preflight warning:[/yellow] {warn}")


@app.command("validate-score")
def validate_score_cmd(
    score_path: Path = typer.Argument(
        Path(f"{DEFAULT_REPORT_OUTPUT_DIR}/full_audit_score.json"),
        help="Path to the emitted score JSON file to validate against ScoreResult.",
    ),
) -> None:
    """Validate an emitted score JSON file against the Pydantic ScoreResult schema."""
    if not score_path.exists():
        err_console.print(f"[bold red]Error: Score file '{score_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    try:
        validated = ScoreResult.model_validate_json(score_path.read_text(encoding="utf-8"))
    except Exception as exc:
        err_console.print(f"[bold red]✗ Invalid ScoreResult JSON in '{score_path}':[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]✓ Valid ScoreResult:[/bold green] project=[cyan]{validated.project_name}[/cyan], "
        f"score=[bold yellow]{validated.overall_score}/100 ({validated.grade})[/bold yellow], "
        f"modules=[bold]{len(validated.architecture_overview.modules)}[/bold], "
        f"strengths=[bold]{len(validated.strengths)}[/bold], "
        f"findings=[bold]{len(validated.findings)}[/bold], "
        f"actions=[bold]{len(validated.action_plan)}[/bold]"
    )


@app.command("validate-migration-plan")
def validate_migration_plan_cmd(
    plan_path: Path = typer.Argument(
        Path(f"{DEFAULT_REPORT_OUTPUT_DIR}/migration_plan.json"),
        help="Path to the emitted migration plan JSON file to validate against MigrationPlanResult.",
    ),
) -> None:
    """Validate an emitted migration plan JSON file against the Pydantic MigrationPlanResult schema."""
    if not plan_path.exists():
        err_console.print(f"[bold red]Error: Migration plan file '{plan_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    try:
        validated = MigrationPlanResult.model_validate_json(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        err_console.print(f"[bold red]✗ Invalid MigrationPlanResult JSON in '{plan_path}':[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]✓ Valid MigrationPlanResult:[/bold green] project=[cyan]{validated.project_name}[/cyan], "
        f"mode=[bold yellow]{validated.transformation_mode}[/bold yellow] "
        f"([bold]{validated.migration_strategy}[/bold]), "
        f"axes=[bold]{len(validated.target_axes)}[/bold], "
        f"layers=[bold]{len(validated.target_architecture.target_layers)}[/bold], "
        f"mappings=[bold]{len(validated.target_architecture.component_mappings)}[/bold], "
        f"decisions=[bold]{len(validated.decision_log)}[/bold], "
        f"phases=[bold]{len(validated.phase_gates)}[/bold], "
        f"prs=[bold]{len(validated.pr_wbs)}[/bold]"
    )


@app.command("validate-progress")
def validate_progress_cmd(
    progress_path: Path = typer.Argument(
        Path(f"{DEFAULT_REPORT_OUTPUT_DIR}/project_progress.json"),
        help="Path to the emitted progress JSON file to validate against ProgressResult.",
    ),
) -> None:
    """Validate an emitted progress JSON file against the Pydantic ProgressResult schema."""
    if not progress_path.exists():
        err_console.print(f"[bold red]Error: Progress result file '{progress_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    try:
        validated = ProgressResult.model_validate_json(progress_path.read_text(encoding="utf-8"))
    except Exception as exc:
        err_console.print(f"[bold red]✗ Invalid ProgressResult JSON in '{progress_path}':[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    console.print(
        f"[bold green]✓ Valid ProgressResult:[/bold green] project=[cyan]{validated.project_name}[/cyan], "
        f"status=[bold yellow]{validated.delivery_status}[/bold yellow], "
        f"score=[bold yellow]{validated.overall_health_score}/100[/bold yellow], "
        f"tasks=[bold]{len(validated.task_assessments)}[/bold], "
        f"branches=[bold]{len(validated.branch_assessments)}[/bold], "
        f"actions=[bold]{len(validated.next_actions)}[/bold]"
    )


@progress_app.command("init")
def progress_init_cmd(
    target: str = typer.Argument(
        "project_progress",
        help="Target plan identifier or relative path under .pni/progress/ (e.g., 'project_progress').",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Optional workflow ID in .pni/workflows/ to inherit target ID and source/test paths from.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite an existing .pni/progress/<target>.yaml file.",
    ),
) -> None:
    """Scaffold a starter .pni/progress/<target>.yaml manifest with milestones, tasks, and git_policy."""
    ws_root = Path.cwd().resolve()
    eff_target = target
    src_dir = "src"
    tst_dir = "tests"

    if workflow:
        loaded = load_workflow(workflow, ws_root)
        if loaded is None:
            err_console.print(f"[bold red]Error: Workflow '{workflow}' not found in .pni/workflows/.[/bold red]")
            raise typer.Exit(code=1)
        _, wf_def = loaded
        if target == "project_progress":
            eff_target = wf_def.id
        if wf_def.targets.source:
            src_dir = wf_def.targets.source[0]
        if wf_def.targets.tests:
            tst_dir = wf_def.targets.tests[0]

    try:
        _, rel_str, was_written = scaffold_progress_plan(
            ws_root,
            eff_target,
            source_dir=src_dir,
            test_dir=tst_dir,
            force=force,
        )
    except ValueError as exc:
        err_console.print(f"[bold red]Error: {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    if not was_written:
        console.print(
            f"[yellow]Notice: '{rel_str}' already exists (preserved). Use --force to overwrite.[/yellow]"
        )
        return

    console.print(f"[bold green]✓ Scaffolded progress & Git governance plan:[/bold green] [cyan]{rel_str}[/cyan]")
    console.print(
        f"  Edit milestones, tasks, and git_policy, then run: [bold]pni progress validate {eff_target}[/bold]"
    )


@progress_app.command("validate")
def progress_validate_cmd(
    target_or_path: str = typer.Argument(
        "project_progress",
        help="Progress plan target ID ('project_progress') or relative YAML path ('.pni/progress/foo.yaml').",
    ),
) -> None:
    """Validate .pni/progress/<target>.yaml schema, ISO dates, git_policy, and acyclic depends_on DAG."""
    ws_root = Path.cwd().resolve()
    try:
        plan, rel_str, sha256_hex, hints = load_and_validate_progress_plan(ws_root, target_or_path)
    except Exception as exc:
        err_console.print(f"[bold red]✗ Progress plan validation failed:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    gp = plan.git_policy
    console.print(
        f"[bold green]✓ Valid Progress Plan:[/bold green] [cyan]{rel_str}[/cyan] "
        f"(id=[bold]{plan.id}[/bold], milestones=[bold]{len(plan.milestones)}[/bold], "
        f"tasks=[bold]{len(plan.tasks)}[/bold], methodology=[yellow]{gp.methodology}[/yellow], "
        f"merge_strategy=[yellow]{gp.merge_strategy}[/yellow], sha256=[dim]{sha256_hex[:12]}...[/dim])"
    )
    for hint in hints:
        console.print(f"  [yellow]⚠ Advisory [{hint.code}]:[/yellow] {hint.message}")


def _resolve_cli_source_dirs(target_dir: Path, explicit: Optional[list[str]]) -> list[str]:
    """Resolve source directories for CLI pentest initialization or execution."""
    if explicit:
        return explicit
    if (target_dir / "src" / "main" / "java").is_dir():
        return ["src/main/java"]
    found = [d for d in ("src", "app", "routes") if (target_dir / d).is_dir()]
    return found or ["."]


def _render_pentest_facts_cli(facts: PentestFacts) -> None:
    """Render PentestFacts summary and findings table to the Rich console."""
    summary = facts.probe_summary
    color = "green" if facts.status in {"passed", "skipped"} else "red"
    console.print(
        f"[bold {color}]Web Pentest status={facts.status}[/bold {color}] "
        f"(engine=[cyan]{facts.container_engine or 'none'}[/cyan], "
        f"url=[yellow]{facts.target_base_url or '-'}[/yellow], "
        f"total=[bold]{summary.total_probes}[/bold], passed=[green]{summary.passed_probes}[/green], "
        f"failed=[red]{summary.failed_probes}[/red], skipped=[dim]{summary.skipped_probes}[/dim])"
    )
    if facts.skip_reason:
        console.print(f"  [dim]Skip reason:[/dim] {facts.skip_reason}")
    if facts.boot_failure_reason:
        err_console.print(f"  [bold red]Boot/Execution error:[/bold red] {facts.boot_failure_reason}")
    if facts.pentests_dir:
        console.print(f"  Suite: [cyan]{facts.pentests_dir}[/cyan] | Artifacts: [dim]{facts.artifacts_dir}[/dim]")
    if not facts.findings:
        return

    table = Table(title="Confirmed Dynamic HTTP Penetration Findings")
    table.add_column("Severity", style="bold")
    table.add_column("CWE", style="cyan")
    table.add_column("Endpoint", style="yellow")
    table.add_column("Title")
    for item in facts.findings:
        table.add_row(item.severity.upper(), item.cwe_id or "-", item.endpoint or "/", item.title)
    console.print(table)


def _resolve_pentest_cli_targets(
    ws_root: Path,
    workflow: str | None,
    target_root: str,
    source: list[str] | None,
    default_wf_id: str,
) -> tuple[str, list[str] | None, str]:
    """Resolve target_root, source dirs, and workflow_id from `-w/--workflow` when provided."""
    if not workflow:
        return target_root, source, default_wf_id

    loaded = load_workflow(workflow, ws_root)
    if loaded is None:
        err_console.print(f"[bold red]Error: Workflow '{workflow}' not found in .pni/workflows/.[/bold red]")
        raise typer.Exit(code=1)
    _, wf_def = loaded
    eff_root = wf_def.targets.root if target_root == "." else target_root
    eff_source = source if source is not None else wf_def.targets.source
    return eff_root, eff_source, wf_def.id


@pentests_app.command("init")
def pentests_init_cmd(
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Resolve target_root and source directories directly from .pni/workflows/<workflow>.yaml.",
    ),
    target_root: str = typer.Option(
        ".",
        "--target-root",
        "-t",
        help="Relative target directory inside the workspace (e.g., '.' or 'examples/php/legacy_shop_messy').",
    ),
    source: Optional[list[str]] = typer.Option(
        None,
        "--source",
        "-s",
        help="Relative source directory inside target_root (repeatable; auto-detected when omitted).",
    ),
    lang: Optional[str] = typer.Option(
        None,
        "--lang",
        "-l",
        help="Optional explicit language override ('python', 'java', 'php').",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files in .pni/pentests/<target>/.",
    ),
) -> None:
    """Materialize explicit Python + httpx penetration test files into .pni/pentests/<target>/."""
    ws_root = Path.cwd().resolve()
    eff_root, eff_source, _ = _resolve_pentest_cli_targets(ws_root, workflow, target_root, source, "manual_pentest")
    t_dir = (ws_root / eff_root).resolve()
    if not t_dir.exists():
        err_console.print(f"[bold red]Error: Target root '{eff_root}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    srcs = _resolve_cli_source_dirs(t_dir, eff_source)
    pf = run_project_inspect(t_dir, source_dirs=srcs, lang=lang)
    af = run_ast_analyze(
        t_dir,
        targets=srcs,
        display_root=ws_root,
        lang=pf.language,
        detected_frameworks=pf.detected_frameworks,
        declared_lang_version=pf.language_version_constraint,
    )
    pentests_dir, mat_files = ensure_target_pentests(ws_root, eff_root, ast_facts=af, force_regenerate=force)
    rel_dir = pentests_dir.resolve().relative_to(ws_root).as_posix()
    console.print(
        f"[bold green]✓ Materialized Web penetration test suite[/bold green] in [cyan]{rel_dir}[/cyan] "
        f"(endpoints discovered: [bold]{len(af.api_endpoints)}[/bold])"
    )
    for rel_file in mat_files:
        console.print(f"  - {rel_file}")


@pentests_app.command("run")
def pentests_run_cmd(
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        "-w",
        help="Resolve target_root, source directories, and cache namespace from .pni/workflows/<workflow>.yaml.",
    ),
    target_root: str = typer.Option(
        ".",
        "--target-root",
        "-t",
        help="Relative target directory inside the workspace.",
    ),
    source: Optional[list[str]] = typer.Option(
        None,
        "--source",
        "-s",
        help="Relative source directory inside target_root (repeatable; auto-detected when omitted).",
    ),
    base_url: str = typer.Option(
        "",
        "--base-url",
        help="Optional live loopback base URL (http://127.0.0.1:<port>) to skip container boot.",
    ),
    workflow_id: str = typer.Option(
        "manual_pentest",
        "--workflow-id",
        help="Cache workflow namespace under .pni/cache/<workflow_id>/pentest/.",
    ),
    container_engine: str = typer.Option(
        "auto",
        "--container-engine",
        help="Container runtime preference ('auto', 'docker', 'podman', 'none').",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Regenerate .pni/pentests/<target>/ files before running.",
    ),
) -> None:
    """Execute language-agnostic HTTP penetration tests from .pni/pentests/<target>/."""
    ws_root = Path.cwd().resolve()
    eff_root, eff_source, eff_wf_id = _resolve_pentest_cli_targets(ws_root, workflow, target_root, source, workflow_id)
    t_dir = (ws_root / eff_root).resolve()
    if not t_dir.exists():
        err_console.print(f"[bold red]Error: Target root '{eff_root}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    try:
        opts = PentestOptions.model_validate(
            {
                "base_url": base_url,
                "container_engine": container_engine,
                "force_regenerate_pentests": force,
            }
        )
    except Exception as exc:
        err_console.print(f"[bold red]✗ Invalid pentest options:[/bold red]\n{exc}")
        raise typer.Exit(code=1) from exc

    facts = run_web_pentest(
        ws_root,
        eff_wf_id,
        target_root=eff_root,
        source_targets=eff_source,
        options=opts,
    )
    _render_pentest_facts_cli(facts)
    if facts.status in {"failed", "error", "timeout"}:
        raise typer.Exit(code=1)


@cache_app.command("clean")
def cache_clean_cmd(
    docker: bool = typer.Option(
        False,
        "--docker",
        help="Also remove temporary PNI container images ('pni-*'), dangling images, and builder cache.",
    ),
    container_engine: str = typer.Option(
        "auto",
        "--container-engine",
        help="Container runtime preference ('auto', 'docker', 'podman') when --docker is enabled.",
    ),
) -> None:
    """Clean `.pni/cache/` artifacts and optionally prune PNI Docker/Podman harness images."""
    ws_root = Path.cwd().resolve()
    cache_dir = ws_root / CACHE_REL_DIR
    removed_entries = 0
    if cache_dir.is_dir():
        for child in cache_dir.iterdir():
            if child.name == ".gitignore":
                continue
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
            removed_entries += 1
        ensure_cache_dir(ws_root)
    console.print(
        f"[bold green]✓ Cleaned .pni/cache/[/bold green] (removed {removed_entries} cached entry/entries)"
    )

    if docker:
        engine_name, engine_bin, reason = detect_container_engine(container_engine)
        if engine_name is None or engine_bin is None:
            console.print(f"[yellow]Notice: Skipping container cleanup ({reason}).[/yellow]")
            return
        removed_tags = prune_pni_container_artifacts(engine_bin)
        console.print(
            f"[bold green]✓ Pruned container artifacts via {engine_name}[/bold green] "
            f"(removed {len(removed_tags)} PNI image tag(s))"
        )


@app.command("instructions")
def instructions() -> None:
    """Print the AI agent instruction guide in Markdown format to stdout."""
    project_root = Path.cwd()
    content = get_instructions_content(project_root)
    print(content)


@app.command("instruction", hidden=True)
def instruction_alias() -> None:
    """Alias for 'pni instructions'."""
    instructions()


def _version_callback(value: bool) -> None:
    """Print PNI package name and version when --version / -V is passed."""
    if value:
        console.print(f"{LIB_NAME} {LIB_VERSION}")
        raise typer.Exit(code=0)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    show_version: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Show pni501 version and exit.",
    ),
) -> None:
    """PNI entrypoint callback."""
    _ = show_version
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]Project Nemesis Index (PNI)[/bold cyan]")
        console.print(f"{LIB_NAME} version [bold green]{LIB_VERSION}[/bold green]\n")
        console.print("Evaluate software development project health and generate reports.")
        console.print("Run [bold]pni -h[/bold] or [bold]pni --help[/bold] for available commands.\n")
        console.print(HELP_EPILOG)


def main() -> None:
    """Execute pni CLI."""
    app()


if __name__ == "__main__":
    main()
