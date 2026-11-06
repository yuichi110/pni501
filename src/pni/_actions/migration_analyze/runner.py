# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Orchestrator for deterministic migration_analyze fact extraction and caching."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final, Optional

from pni._actions._repo_governance import matches_exclude_globs
from pni._actions.ast_analyze import AstFacts, run_ast_analyze
from pni._actions.ast_analyze.models import IGNORED_DIR_NAMES
from pni._actions.migration_analyze.ambiguities import extract_spec_vs_bug_candidates
from pni._actions.migration_analyze.codemods import (
    check_migration_preflight_hints,
    classify_transformation_mode,
    collect_migration_blockers,
    match_codemod_recipes,
    resolve_effective_strategy,
)
from pni._actions.migration_analyze.contracts import extract_implicit_and_env_contracts
from pni._actions.migration_analyze.graph_waves import compute_refactoring_waves
from pni._actions.migration_analyze.models import MigrationFacts, MigrationOptions
from pni._actions.migration_analyze.touchpoints import extract_boundary_touchpoints
from pni._actions.project_inspect import ProjectFacts, run_project_inspect
from pni._actions.runtime_check.models import RuntimeFacts
from pni._cache import (
    default_facts_rel_path,
    default_migration_facts_rel_path,
    ensure_cache_parent,
)

_SOURCE_EXTENSIONS: Final[frozenset[str]] = frozenset({".py", ".java", ".php", ".phtml"})


def resolve_migration_brief(workspace_root: Path, options: MigrationOptions) -> str:
    """Resolve and combine inline `brief` text and workspace-relative `brief_file` Markdown.

    Args:
        workspace_root: Workspace root directory.
        options: Migration step options.

    Returns:
        str: Combined stripped migration brief text.

    Raises:
        ValueError: If `brief_file` escapes `workspace_root` or does not exist.
    """
    parts: list[str] = []
    if options.brief_file and options.brief_file.strip():
        resolved_root = workspace_root.resolve()
        candidate = (workspace_root / options.brief_file.strip()).resolve()
        if not candidate.is_relative_to(resolved_root):
            msg = f"brief_file must stay within workspace root: {options.brief_file!r}"
            raise ValueError(msg)
        if not candidate.is_file():
            msg = f"brief_file does not exist: {options.brief_file!r}"
            raise ValueError(msg)
        parts.append(candidate.read_text(encoding="utf-8").strip())
    if options.brief.strip():
        parts.append(options.brief.strip())
    return "\n\n".join(p for p in parts if p)


def _load_cached_base_facts(
    workspace_root: Path,
    base_workflow_id: str,
) -> tuple[ProjectFacts | None, AstFacts | None, RuntimeFacts | None]:
    """Load cached ProjectFacts, AstFacts, and RuntimeFacts from a prior audit workflow if present."""
    clean_wf = base_workflow_id.strip()
    if not clean_wf:
        return None, None, None
    facts_file = workspace_root / default_facts_rel_path(clean_wf)
    if not facts_file.is_file():
        return None, None, None
    try:
        raw = json.loads(facts_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None, None
    if not isinstance(raw, dict):
        return None, None, None

    pf = ProjectFacts.model_validate(raw["project_facts"]) if raw.get("project_facts") else None
    af = AstFacts.model_validate(raw["ast_facts"]) if raw.get("ast_facts") else None
    rf = RuntimeFacts.model_validate(raw["runtime_facts"]) if raw.get("runtime_facts") else None
    return pf, af, rf


def _collect_source_files(
    workspace_root: Path,
    target_root_dir: Path,
    source_targets: list[str],
    exclude_globs: Optional[list[str]] = None,
) -> dict[str, str]:
    """Read target source files into a deterministic workspace-relative path -> content map."""
    resolved_ws = workspace_root.resolve()
    globs = exclude_globs or []
    files: dict[str, str] = {}
    search_roots = [target_root_dir / rel for rel in (source_targets or ["."])]
    for root in search_roots:
        if root.is_file() and root.suffix.lower() in _SOURCE_EXTENSIONS:
            if matches_exclude_globs(root, target_root_dir, globs):
                continue
            rel_key = root.resolve().relative_to(resolved_ws).as_posix()
            files[rel_key] = root.read_text(encoding="utf-8", errors="replace")
        elif root.is_dir():
            for child in sorted(root.rglob("*")):
                if not child.is_file() or child.suffix.lower() not in _SOURCE_EXTENSIONS:
                    continue
                rel_to_target = child.relative_to(target_root_dir)
                if any(part in IGNORED_DIR_NAMES for part in rel_to_target.parts):
                    continue
                if matches_exclude_globs(child, target_root_dir, globs):
                    continue
                rel_key = child.resolve().relative_to(resolved_ws).as_posix()
                files[rel_key] = child.read_text(encoding="utf-8", errors="replace")
    return files


def run_migration_analyze(
    workspace_root: Path,
    workflow_id: str,
    *,
    target_root: str = ".",
    source_targets: Optional[list[str]] = None,
    test_targets: Optional[list[str]] = None,
    doc_targets: Optional[list[str]] = None,
    exclude_globs: Optional[list[str]] = None,
    lang: Optional[str] = None,
    project_facts: Optional[ProjectFacts] = None,
    ast_facts: Optional[AstFacts] = None,
    runtime_facts: Optional[RuntimeFacts] = None,
    options: Optional[MigrationOptions] = None,
) -> MigrationFacts:
    """Execute deterministic As-Is migration analysis and persist migration_facts.json.

    Args:
        workspace_root: Workspace root directory.
        workflow_id: Active workflow identifier.
        target_root: Target project directory relative to workspace_root.
        source_targets: Relative source directories/files inside target_root.
        test_targets: Relative test directories inside target_root.
        doc_targets: Relative documentation files inside target_root.
        exclude_globs: Optional glob patterns excluded from source/test analysis.
        lang: Optional explicit language override ('python', 'java', 'php').
        project_facts: Optional pre-loaded ProjectFacts.
        ast_facts: Optional pre-loaded AstFacts.
        runtime_facts: Optional pre-loaded RuntimeFacts.
        options: Optional MigrationOptions configuration.

    Returns:
        MigrationFacts: Complete deterministic As-Is migration facts bundle.
    """
    active_opts = options or MigrationOptions()
    resolved_brief = resolve_migration_brief(workspace_root, active_opts)

    if active_opts.base_audit_workflow and (project_facts is None or ast_facts is None):
        cached_pf, cached_af, cached_rf = _load_cached_base_facts(
            workspace_root,
            active_opts.base_audit_workflow,
        )
        project_facts = project_facts or cached_pf
        ast_facts = ast_facts or cached_af
        runtime_facts = runtime_facts or cached_rf

    target_dir = (workspace_root / target_root).resolve()
    eff_sources = source_targets or ["."]
    eff_tests = test_targets or []
    eff_docs = doc_targets or ["README.md"]

    if project_facts is None:
        project_facts = run_project_inspect(
            target_dir,
            source_dirs=eff_sources,
            test_dirs=eff_tests,
            doc_files=eff_docs,
            lang=lang,
            exclude_globs=exclude_globs,
        )

    if ast_facts is None:
        ast_facts = run_ast_analyze(
            target_dir,
            targets=eff_sources,
            display_root=workspace_root.resolve(),
            lang=lang or project_facts.language,
            test_targets=eff_tests,
            exclude_globs=exclude_globs,
            detected_frameworks=project_facts.detected_frameworks,
            declared_lang_version=project_facts.language_version_constraint,
        )

    active_lang = (lang or ast_facts.language or project_facts.language).lower()
    source_files = _collect_source_files(workspace_root, target_dir, eff_sources, exclude_globs=exclude_globs)

    preflight_hints = check_migration_preflight_hints(active_opts, resolved_brief)
    touchpoints = extract_boundary_touchpoints(source_files, active_lang, ast_facts)
    waves, cycle_cuts = compute_refactoring_waves(ast_facts, source_files, touchpoints)
    implicit_contracts, env_contracts = extract_implicit_and_env_contracts(
        source_files,
        active_lang,
        ast_facts,
    )
    mode = classify_transformation_mode(active_lang, resolved_brief, project_facts, touchpoints)
    eff_strategy = resolve_effective_strategy(active_opts, mode)
    codemods = match_codemod_recipes(active_lang, active_opts, resolved_brief, ast_facts)
    blockers = collect_migration_blockers(project_facts, ast_facts, runtime_facts)
    candidates = extract_spec_vs_bug_candidates(ast_facts, source_files)

    mig_facts = MigrationFacts(
        project_name=project_facts.project_name,
        source_language=active_lang,
        base_audit_workflow=active_opts.base_audit_workflow,
        resolved_brief=resolved_brief,
        effective_options=active_opts,
        transformation_mode=mode,
        resolved_strategy=eff_strategy,
        preflight_hints=preflight_hints,
        refactoring_waves=waves,
        cycle_cuts=cycle_cuts,
        implicit_contracts=implicit_contracts,
        env_contracts=env_contracts,
        boundary_touchpoints=touchpoints,
        mechanical_codemods=codemods,
        manual_blockers=blockers,
        spec_vs_bug_candidates=candidates,
    )

    out_file = workspace_root / default_migration_facts_rel_path(workflow_id)
    ensure_cache_parent(workspace_root, out_file)
    out_file.write_text(mig_facts.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return mig_facts
