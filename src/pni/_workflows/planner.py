# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Phase 0 Lightweight Recon, safe `when:` DAG evaluator, and validated Mermaid DAG planner."""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Final, Literal, Optional

from pydantic import BaseModel, Field

from pni._actions import (
    PlanApprovalInput,
    PrimitiveStep,
    PrimitiveType,
    ProjectFacts,
    run_project_inspect,
)
from pni._actions.runtime_check.engine_detect import detect_container_engine
from pni._actions.runtime_check.selector import select_harness_tool
from pni._cache import ensure_cache_parent
from pni._config import load_pni_config
from pni._dockerfiles import has_builtin_dockerfile
from pni._languages import LANGUAGE_REGISTRY, get_language_spec
from pni._rules import detect_active_language
from pni._workflows.base_model import WorkflowDefinition
from pni._workflows.mermaid_validator import (
    escape_mermaid_label,
    sanitize_mermaid_id,
    validate_mermaid_static,
)

DETERMINISTIC_PRIMITIVES: Final[frozenset[PrimitiveType]] = frozenset(
    {
        PrimitiveType.PROJECT_INSPECT,
        PrimitiveType.AST_ANALYZE,
        PrimitiveType.RUN_CHECK,
        PrimitiveType.SECURITY_SCAN,
        PrimitiveType.WEB_PENTEST,
        PrimitiveType.MIGRATION_ANALYZE,
        PrimitiveType.PROGRESS_ANALYZE,
    }
)
_IGNORED_SCAN_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        ".pni",
        ".venv",
        "venv",
        "node_modules",
        "vendor",
        "target",
        "build",
        "dist",
        "__pycache__",
        ".drawlib",
        "reports",
        "reports_src",
        "pni_report",
        "pni_report_src",
        "pni_migration",
        "pni_migration_src",
        "pni_progress",
        "pni_progress_src",
    }
)


class DiscoveredComponent(BaseModel):
    """Candidate language component discovered during lightweight repository recon."""

    id: str
    root: str = "."
    language: str
    file_count: int = 0
    approx_loc: int = 0
    has_runtime_harness: bool = False
    recommended_dockerfile: str = ""


class DagPlanNode(BaseModel):
    """Single planned node in the pre-execution Workflow v2 DAG."""

    action_id: str
    step_key: str
    name: str
    primitive_type: PrimitiveType
    source_action: Optional[str] = None
    needs: list[str] = Field(default_factory=list)
    when: Optional[str] = None
    status: Literal["run", "skip", "ask"] = "run"
    badge: Literal["AUTO", "AI", "SKIP", "ASK"] = "AI"
    detail: str = ""
    skip_reason: str = ""


class WorkflowExecutionPlan(BaseModel):
    """Pre-flight execution plan persisted to .pni/cache/<workflow_id>/plan.json."""

    schema_version: str = "2.0"
    workflow_id: str
    category: str = "audit"
    scope: str = "repo"
    target_root: str = "."
    language: str = "python"
    runtime_types: list[str] = Field(default_factory=list)
    detected_frameworks: list[str] = Field(default_factory=list)
    container_engine: Optional[str] = None
    harness_template: str = ""
    components: list[DiscoveredComponent] = Field(default_factory=list)
    companion_languages: list[str] = Field(default_factory=list)
    nodes: list[DagPlanNode] = Field(default_factory=list)
    mermaid_dag: str = ""
    alignment_questions: list[str] = Field(default_factory=list)
    approval: Optional[PlanApprovalInput] = None


def default_plan_rel_path(workflow_id: str) -> str:
    """Return workspace-relative path to `.pni/cache/<workflow_id>/plan.json`."""
    return f".pni/cache/{workflow_id}/plan.json"


def _eval_compare_node(node: ast.Compare, ctx: dict[str, object]) -> bool:
    """Safely evaluate a single comparison AST node (`==`, `!=`, `in`, `not in`)."""
    left = _eval_ast_node(node.left, ctx)
    right = _eval_ast_node(node.comparators[0], ctx)
    op = node.ops[0]
    if isinstance(op, ast.Eq):
        return bool(left == right)
    if isinstance(op, ast.NotEq):
        return bool(left != right)
    if isinstance(op, (ast.In, ast.NotIn)):
        if isinstance(right, str):
            contained = isinstance(left, str) and (left in right)
        elif isinstance(right, (list, tuple, set, frozenset)):
            contained = left in right
        else:
            msg = f"Unsupported right operand for 'in' in workflow 'when' clause: {type(right).__name__}"
            raise ValueError(msg)
        return contained if isinstance(op, ast.In) else not contained
    msg = f"Unsupported comparison operator in workflow 'when' clause: {ast.dump(node)}"
    raise ValueError(msg)


def _eval_ast_node(node: ast.AST, ctx: dict[str, object]) -> object:
    """Safely evaluate a whitelisted boolean/comparison AST node without eval()."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return ctx.get(node.id, False)
    if isinstance(node, (ast.List, ast.Tuple)) and all(isinstance(el, ast.Constant) for el in node.elts):
        return [el.value for el in node.elts if isinstance(el, ast.Constant)]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not bool(_eval_ast_node(node.operand, ctx))
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        fn = all if isinstance(node.op, ast.And) else any
        return fn(bool(_eval_ast_node(v, ctx)) for v in node.values)
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
        return _eval_compare_node(node, ctx)
    msg = f"Unsupported expression syntax in workflow 'when' clause: {ast.dump(node)}"
    raise ValueError(msg)


def evaluate_when_expr(expr: str | None, ctx: dict[str, object]) -> tuple[bool, str]:
    """Evaluate a safe workflow `when:` predicate against recon context.

    Returns:
        tuple[bool, str]: (should_run, diagnostic_reason_if_skipped)
    """
    if not expr or not expr.strip():
        return True, ""
    parsed = ast.parse(expr.strip(), mode="eval")
    result = bool(_eval_ast_node(parsed.body, ctx))
    if result:
        return True, ""
    return False, f"Condition '{expr.strip()}' evaluated to false"


def _build_extension_maps() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Build extension and filename lookup maps for app languages and companion DSLs."""
    ext_to_app: dict[str, str] = {}
    ext_to_comp: dict[str, str] = {}
    fname_to_comp: dict[str, str] = {}
    for lid, spec in LANGUAGE_REGISTRY.items():
        if spec.tier == "companion_dsl":
            for ext in spec.file_extensions:
                ext_to_comp.setdefault(ext.lower(), lid)
            for fn in spec.filenames:
                fname_to_comp.setdefault(fn, lid)
        else:
            for ext in spec.file_extensions:
                ext_to_app.setdefault(ext.lower(), lid)
    return ext_to_app, ext_to_comp, fname_to_comp


def _scan_dir_language_counts(base_dir: Path, *, max_depth: int = 4) -> tuple[dict[str, tuple[int, int]], set[str]]:
    """Count (files, approx_loc) per app/static language and discover companion DSLs quickly."""
    ext_to_app, ext_to_comp, fname_to_comp = _build_extension_maps()
    counts: dict[str, list[int]] = {}
    companions: set[str] = set()
    root_depth = len(base_dir.parts)

    for dirpath, dirnames, filenames in os.walk(base_dir):
        curr = Path(dirpath)
        depth = len(curr.parts) - root_depth
        dirnames[:] = [d for d in sorted(dirnames) if d not in _IGNORED_SCAN_DIRS and not d.startswith(".")]
        if depth > max_depth:
            dirnames.clear()
            continue
        for fname in filenames:
            if fname in fname_to_comp:
                companions.add(fname_to_comp[fname])
                continue
            ext = Path(fname).suffix.lower()
            if ext in ext_to_comp:
                companions.add(ext_to_comp[ext])
                continue
            lid = ext_to_app.get(ext)
            if lid is None:
                continue
            try:
                loc = max(1, (curr / fname).stat().st_size // 36)
            except OSError:
                loc = 1
            entry = counts.setdefault(lid, [0, 0])
            entry[0] += 1
            entry[1] += loc

    return {k: (v[0], v[1]) for k, v in counts.items()}, companions


def _has_language_manifest(directory: Path) -> bool:
    """Return True if *directory* directly contains any app/static language manifest."""
    for spec in LANGUAGE_REGISTRY.values():
        if spec.tier == "companion_dsl":
            continue
        if any((directory / mf).is_file() for mf in (*spec.primary_manifests, *spec.secondary_manifests)):
            return True
        if any(next(directory.glob(pat), None) is not None for pat in spec.manifest_globs):
            return True
    return False


def _collect_top_level_companions(project_root: Path) -> set[str]:
    """Detect companion DSL files directly at repository root (e.g. Dockerfile, Makefile, *.tf)."""
    _, ext_to_comp, fname_to_comp = _build_extension_maps()
    companions: set[str] = set()
    for entry in project_root.iterdir():
        if not entry.is_file():
            continue
        if entry.name in fname_to_comp:
            companions.add(fname_to_comp[entry.name])
        elif entry.suffix.lower() in ext_to_comp:
            companions.add(ext_to_comp[entry.suffix.lower()])
    return companions


def discover_repo_components(project_root: Path) -> tuple[list[DiscoveredComponent], list[str]]:
    """Fast (<1s) discovery of candidate multi-language components and companion DSLs."""
    components: list[DiscoveredComponent] = []
    all_companions: set[str] = _collect_top_level_companions(project_root)

    # Check top-level subprojects containing language manifests (e.g. backend/, frontend/, services/*)
    for child in sorted(project_root.iterdir()):
        if not child.is_dir() or child.name in _IGNORED_SCAN_DIRS or child.name.startswith("."):
            continue
        sub_counts, sub_comps = _scan_dir_language_counts(child, max_depth=3)
        all_companions.update(sub_comps)
        if not sub_counts or not _has_language_manifest(child):
            continue
        top_lang, (fcnt, aloc) = max(sub_counts.items(), key=lambda kv: (kv[1][1], kv[1][0]))
        spec = get_language_spec(top_lang)
        has_h = has_builtin_dockerfile(top_lang)
        components.append(
            DiscoveredComponent(
                id=sanitize_mermaid_id(child.name),
                root=child.relative_to(project_root).as_posix(),
                language=top_lang,
                file_count=fcnt,
                approx_loc=aloc,
                has_runtime_harness=has_h,
                recommended_dockerfile=f"{top_lang}/..." if has_h and spec else "",
            )
        )

    if not components:
        root_counts, root_comps = _scan_dir_language_counts(project_root, max_depth=4)
        all_companions.update(root_comps)
        ranked = sorted(root_counts.items(), key=lambda kv: (kv[1][1], kv[1][0]), reverse=True)
        for lid, (fcnt, aloc) in ranked[:4]:
            if fcnt < 1:
                continue
            has_h = has_builtin_dockerfile(lid)
            components.append(
                DiscoveredComponent(
                    id=sanitize_mermaid_id(lid),
                    root=".",
                    language=lid,
                    file_count=fcnt,
                    approx_loc=aloc,
                    has_runtime_harness=has_h,
                    recommended_dockerfile=f"{lid}/..." if has_h else "",
                )
            )

    return components, sorted(all_companions)


def build_recon_context(
    workflow_def: WorkflowDefinition,
    pf: ProjectFacts,
    *,
    container_engine: Optional[str],
) -> dict[str, object]:
    """Build deterministic boolean/scalar context dictionary for safe `when:` evaluation."""
    rtypes = [str(rt) for rt in pf.runtime_types]
    return {
        "lang": pf.language,
        "language": pf.language,
        "scope": workflow_def.scope,
        "is_repo_scope": workflow_def.scope == "repo",
        "is_component_scope": workflow_def.scope == "component",
        "has_runtime_harness": has_builtin_dockerfile(pf.language),
        "docker_available": container_engine is not None,
        "has_tests": pf.test_files_count > 0,
        "has_web_api": "web_api" in rtypes,
        "has_cli": "cli" in rtypes,
        "runtime_types": rtypes,
        "detected_frameworks": list(pf.detected_frameworks),
    }


def render_plan_mermaid(nodes: list[DagPlanNode]) -> str:
    """Deterministically generate and validate a Mermaid `flowchart TD` DAG from planned nodes."""
    lines = ["flowchart TD"]
    id_map: dict[str, str] = {}
    key_to_ids: dict[str, list[str]] = {}

    for node in nodes:
        mid = sanitize_mermaid_id(node.action_id)
        id_map[node.action_id] = mid
        key_to_ids.setdefault(node.step_key, []).append(mid)
        if node.source_action:
            key_to_ids.setdefault(node.source_action, []).append(mid)

        extra = f"\n{node.skip_reason}" if node.status == "skip" and node.skip_reason else ""
        raw_label = f"[{node.badge}] {node.action_id}: {node.name}{extra}"
        safe_label = escape_mermaid_label(raw_label)
        lines.append(f'    {mid}["{safe_label}"]')

    prev_mid: Optional[str] = None
    for node in nodes:
        mid = id_map[node.action_id]
        edges_added = False
        for dep in node.needs:
            dep_ids = [id_map[dep]] if dep in id_map else key_to_ids.get(dep, [])
            if dep_ids:
                dmid = dep_ids[-1]
                if dmid != mid:
                    lines.append(f"    {dmid} --> {mid}")
                    edges_added = True
        if not edges_added and prev_mid is not None and not node.needs:
            lines.append(f"    {prev_mid} --> {mid}")
        prev_mid = mid

    lines.extend(
        [
            "    classDef auto fill:#e8f0fe,stroke:#1a73e8,color:#174ea6",
            "    classDef ai fill:#fef7e0,stroke:#f9ab00,color:#b06000",
            "    classDef skip fill:#f1f3f4,stroke:#9aa0a6,color:#5f6368",
            "    classDef ask fill:#e6f4ea,stroke:#1e8e3e,color:#137333",
        ]
    )
    badge_class = {"AUTO": "auto", "AI": "ai", "SKIP": "skip", "ASK": "ask"}
    for node in nodes:
        lines.append(f"    class {id_map[node.action_id]} {badge_class[node.badge]}")

    code = "\n".join(lines)
    validation = validate_mermaid_static(code)
    if not validation.valid:
        msg = f"Internal Mermaid DAG generation failed validation: {validation.issues}"
        raise RuntimeError(msg)
    return code


def _build_alignment_questions(
    workflow_def: WorkflowDefinition,
    pf: ProjectFacts,
    components: list[DiscoveredComponent],
    container_engine: Optional[str],
    nodes: list[DagPlanNode],
    *,
    configured_opt_outs: int = 0,
) -> list[str]:
    """Generate 2-4 concrete human alignment questions grounded in Recon findings."""
    questions: list[str] = [
        (
            f"Target scope check: `root={workflow_def.targets.root}`, `source={workflow_def.targets.source}`, "
            f"`tests={workflow_def.targets.tests}` ({pf.source_files_count} source / {pf.test_files_count} test files "
            f"detected for `{pf.language}`). Any directories to add or exclude?"
        ),
    ]
    if len(components) >= 2 and workflow_def.category == "audit":
        comp_desc = ", ".join(f"`{c.id}` ({c.language}, {c.root})" for c in components)
        questions.append(
            f"Multi-language repository detected ({comp_desc}). Proceed with single-language audit or switch to "
            "a Multi-Audit Rollup workflow (`category: rollup`)?"
        )
    has_runtime_node = any(n.primitive_type == PrimitiveType.RUN_CHECK and n.status == "run" for n in nodes)
    if has_runtime_node:
        eng_note = f"engine=`{container_engine}`" if container_engine else "no container engine detected (will skip)"
        questions.append(
            f"Containerized runtime tests & security scan are planned ({eng_note}). "
            "Should all active stages run or should any optional stage be disabled?"
        )
    waiver_note = f" ({configured_opt_outs} waiver(s) already active in `.pni/pni.toml`)" if configured_opt_outs else ""
    questions.append(
        f"Any focus areas (e.g. security, refactoring, test coverage), design waivers (`opt_out`){waiver_note}, "
        "or preferred report language/format (`en`/`ja`, `pdf`/`html`)?"
    )
    return questions[:4]


def build_workflow_plan(
    workflow_def: WorkflowDefinition,
    primitives: list[PrimitiveStep],
    project_root: Path,
    *,
    probe_container_engine: bool = True,
) -> WorkflowExecutionPlan:
    """Execute Phase 0 Lightweight Recon and build a validated WorkflowExecutionPlan + Mermaid DAG."""
    target_dir = (project_root / workflow_def.targets.root).resolve()
    detected_lang = detect_active_language(target_dir) if target_dir.is_dir() else "python"
    pf = run_project_inspect(
        target_dir if target_dir.is_dir() else project_root,
        source_dirs=workflow_def.targets.source,
        test_dirs=workflow_def.targets.tests,
        doc_files=workflow_def.targets.docs,
        lang=detected_lang,
        exclude_globs=workflow_def.targets.exclude,
    )
    eng_name: Optional[str] = None
    if probe_container_engine:
        eng_name, _, _ = detect_container_engine("auto")

    tool = select_harness_tool(pf)
    harness_tpl = f"{pf.language}/{tool}.dockerfile" if has_builtin_dockerfile(pf.language) else ""
    ctx = build_recon_context(workflow_def, pf, container_engine=eng_name)
    components, companions = discover_repo_components(project_root)

    nodes: list[DagPlanNode] = []
    for idx, step in enumerate(primitives, start=1):
        action_id = f"act-{idx:02d}"
        should_run, skip_reason = evaluate_when_expr(step.when, ctx)
        if not should_run:
            status: Literal["run", "skip", "ask"] = "skip"
            badge: Literal["AUTO", "AI", "SKIP", "ASK"] = "SKIP"
        elif step.type == PrimitiveType.CONFIRM_PLAN:
            status = "ask"
            badge = "ASK"
        elif step.type in DETERMINISTIC_PRIMITIVES:
            status = "run"
            badge = "AUTO"
        else:
            status = "run"
            badge = "AI"

        detail = ""
        if step.type == PrimitiveType.RUN_CHECK and harness_tpl:
            detail = f"harness={harness_tpl}, engine={eng_name or 'unavailable'}"
        elif step.rules:
            detail = f"rules={', '.join(step.rules[:4])}"

        nodes.append(
            DagPlanNode(
                action_id=action_id,
                step_key=step.step_key or step.id,
                name=step.name,
                primitive_type=step.type,
                source_action=step.source_action,
                needs=list(step.needs),
                when=step.when,
                status=status,
                badge=badge,
                detail=detail,
                skip_reason=skip_reason,
            )
        )

    pni_cfg = load_pni_config(project_root)
    mermaid_dag = render_plan_mermaid(nodes)
    questions = _build_alignment_questions(
        workflow_def,
        pf,
        components,
        eng_name,
        nodes,
        configured_opt_outs=len(pni_cfg.opt_out),
    )

    return WorkflowExecutionPlan(
        workflow_id=workflow_def.id,
        category=workflow_def.category.value,
        scope=workflow_def.scope,
        target_root=workflow_def.targets.root,
        language=pf.language,
        runtime_types=[str(rt) for rt in pf.runtime_types],
        detected_frameworks=list(pf.detected_frameworks),
        container_engine=eng_name,
        harness_template=harness_tpl,
        components=components,
        companion_languages=companions,
        nodes=nodes,
        mermaid_dag=mermaid_dag,
        alignment_questions=questions,
    )


def persist_workflow_plan(project_root: Path, plan: WorkflowExecutionPlan) -> Path:
    """Save WorkflowExecutionPlan JSON to `.pni/cache/<workflow_id>/plan.json`."""
    plan_file = project_root / default_plan_rel_path(plan.workflow_id)
    ensure_cache_parent(project_root, plan_file)
    plan_file.write_text(plan.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return plan_file


def render_plan_markdown(plan: WorkflowExecutionPlan) -> str:
    """Render a complete human-readable execution plan with validated Mermaid DAG and alignment questions."""
    pni_note = f"engine=`{plan.container_engine or 'unavailable'}`, harness=`{plan.harness_template or 'none'}`"
    lines = [
        f"# PNI Workflow Execution Plan (`{plan.workflow_id}`)",
        f"- **Category / Scope**: `{plan.category}` / `{plan.scope}` | **Target Root**: `{plan.target_root}`",
        (
            f"- **Detected Language**: `{plan.language}` | **Archetypes**: `{plan.runtime_types}` | "
            f"**Frameworks**: `{plan.detected_frameworks or ['none']}`"
        ),
        f"- **Container Runtime**: {pni_note}",
    ]
    if plan.components:
        comp_str = ", ".join(f"`{c.id}` ({c.language}, `{c.root}`, ~{c.approx_loc} LOC)" for c in plan.components)
        lines.append(f"- **Discovered Components**: {comp_str}")
    if plan.companion_languages:
        lines.append(f"- **Companion DSLs**: `{plan.companion_languages}`")

    lines.extend(["\n## Planned Execution DAG", "```mermaid", plan.mermaid_dag, "```", "\n## Planned Steps"])
    lines.append("| Action | Step Key | Mode | Type | Status | Detail / Skip Reason |")
    lines.append("| :--- | :--- | :---: | :--- | :---: | :--- |")
    for n in plan.nodes:
        note = n.skip_reason if n.status == "skip" else n.detail
        row = f"| `{n.action_id}` | `{n.step_key}` | `{n.badge}` | `{n.primitive_type.value}` | `{n.status}` | {note} |"
        lines.append(row)

    if plan.alignment_questions:
        lines.append("\n## Alignment Questions Before Execution")
        for i, q in enumerate(plan.alignment_questions, start=1):
            lines.append(f"{i}. {q}")

    return "\n".join(lines) + "\n"
