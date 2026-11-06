# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Tarjan SCC cycle-cut planner and leaf-first 4-wave topological refactoring sorter."""

from __future__ import annotations

from dataclasses import dataclass

from pni._actions.ast_analyze.models import AstFacts
from pni._actions.migration_analyze.models import (
    BoundaryTouchpoint,
    CycleCutSuggestion,
    RefactoringWave,
)


@dataclass
class _TarjanState:
    """Mutable traversal state for Tarjan's strongly connected components algorithm."""

    index: int
    indices: dict[str, int]
    lowlink: dict[str, int]
    stack: list[str]
    on_stack: set[str]
    sccs: list[list[str]]


def _tarjan_visit(node: str, graph: dict[str, list[str]], state: _TarjanState) -> None:
    """Visit one vertex in Tarjan's SCC DFS traversal."""
    state.indices[node] = state.index
    state.lowlink[node] = state.index
    state.index += 1
    state.stack.append(node)
    state.on_stack.add(node)

    for dep in graph.get(node, []):
        if dep not in graph:
            continue
        if dep not in state.indices:
            _tarjan_visit(dep, graph, state)
            state.lowlink[node] = min(state.lowlink[node], state.lowlink[dep])
        elif dep in state.on_stack:
            state.lowlink[node] = min(state.lowlink[node], state.indices[dep])

    if state.lowlink[node] == state.indices[node]:
        comp: list[str] = []
        while True:
            w = state.stack.pop()
            state.on_stack.discard(w)
            comp.append(w)
            if w == node:
                break
        state.sccs.append(sorted(comp))


def _compute_sccs(graph: dict[str, list[str]]) -> list[list[str]]:
    """Compute deterministically ordered strongly connected components via Tarjan's algorithm."""
    state = _TarjanState(index=0, indices={}, lowlink={}, stack=[], on_stack=set(), sccs=[])
    for node in sorted(graph):
        if node not in state.indices:
            _tarjan_visit(node, graph, state)
    return state.sccs


def _layer_rank_for_cut(module_path: str) -> int:
    """Assign architectural upward rank (lower = deeper layer; higher = outer/entrypoint layer)."""
    low = module_path.lower()
    if any(tok in low for tok in ("util", "helper", "model", "entity", "dto", "domain")):
        return 1
    if any(tok in low for tok in ("db", "repo", "client", "gateway", "dao", "adapter")):
        return 2
    if any(tok in low for tok in ("service", "manager", "usecase")):
        return 3
    if any(tok in low for tok in ("controller", "route", "handler", "index.php", "login.php", "app")):
        return 4
    return 2


def _suggest_cut_for_scc(comp: list[str], graph: dict[str, list[str]]) -> CycleCutSuggestion:
    """Choose the architectural back-edge (lower-rank module importing higher-rank module) to cut."""
    comp_set = set(comp)
    candidate_edges: list[tuple[int, str, str]] = []
    for src in comp:
        for dst in graph.get(src, []):
            if dst in comp_set and dst != src:
                upward_penalty = _layer_rank_for_cut(dst) - _layer_rank_for_cut(src)
                candidate_edges.append((upward_penalty, src, dst))

    if not candidate_edges:
        return CycleCutSuggestion(
            cycle_modules=comp,
            recommended_cut_from=comp[0],
            recommended_cut_to=comp[-1],
            rationale="Decouple mutual dependency via shared Domain/Port interface.",
        )

    candidate_edges.sort(key=lambda item: (-item[0], item[1], item[2]))
    _, cut_from, cut_to = candidate_edges[0]
    return CycleCutSuggestion(
        cycle_modules=comp,
        recommended_cut_from=cut_from,
        recommended_cut_to=cut_to,
        rationale=(
            f"Break upward/cyclic back-reference `{cut_from} -> {cut_to}` by passing required scalar/DTO "
            "inputs explicitly or inverting dependency via a Port interface."
        ),
    )


def _strip_source_ext(file_path: str) -> str:
    """Strip common source extensions and Python __init__ suffix for FQN suffix matching."""
    low = file_path.replace("\\", "/").strip("/")
    for ext in (".java", ".py", ".php", ".phtml", ".inc"):
        if low.lower().endswith(ext):
            low = low[: -len(ext)]
            break
    if low.endswith("/__init__"):
        low = low[: -len("/__init__")]
    return low.lower()


def _resolve_graph_node(raw_node: str, canonical_files: list[str], stem_index: dict[str, str]) -> str:
    """Resolve an FQN or module identifier (e.g. 'com.acme.billing.BillingManager') to its canonical file path."""
    if raw_node in stem_index:
        return stem_index[raw_node]
    norm = raw_node.replace("\\", "/").replace(".", "/").strip("/").lower()
    for fpath in canonical_files:
        fstem = _strip_source_ext(fpath)
        if fstem == norm or fstem.endswith(f"/{norm}"):
            stem_index[raw_node] = fpath
            return fpath
    return raw_node


def _normalize_graph(ast_facts: AstFacts | None, source_files: dict[str, str]) -> dict[str, list[str]]:
    """Build a canonical file-path adjacency map including isolated leaf files with 0 imports."""
    file_set: set[str] = set(source_files.keys())
    if ast_facts is not None:
        file_set.update(m.file for m in ast_facts.module_inventory)
    canonical_files = sorted(file_set)
    stem_index: dict[str, str] = {f: f for f in canonical_files}

    adj: dict[str, set[str]] = {f: set() for f in canonical_files}
    if ast_facts is not None:
        for raw_src, raw_deps in ast_facts.internal_import_graph.items():
            src = _resolve_graph_node(raw_src, canonical_files, stem_index)
            adj.setdefault(src, set())
            for raw_dep in raw_deps:
                dep = _resolve_graph_node(raw_dep, canonical_files, stem_index)
                adj.setdefault(dep, set())
                if dep != src:
                    adj[src].add(dep)

    return {node: sorted(deps) for node, deps in sorted(adj.items())}


def compute_refactoring_waves(
    ast_facts: AstFacts | None,
    source_files: dict[str, str],
    touchpoints: list[BoundaryTouchpoint],
) -> tuple[list[RefactoringWave], list[CycleCutSuggestion]]:
    """Compute 4-stage leaf-first refactoring waves and cycle-cut suggestions.

    Args:
        ast_facts: Deterministic AST facts containing internal_import_graph and module_inventory.
        source_files: Workspace-relative source file map.
        touchpoints: Extracted boundary touchpoints used to identify outbound I/O modules.

    Returns:
        tuple[list[RefactoringWave], list[CycleCutSuggestion]]: Waves 1..4 and cycle cut plans.
    """
    graph = _normalize_graph(ast_facts, source_files)
    if not graph:
        return [], []

    sccs = _compute_sccs(graph)
    cycle_nodes: set[str] = set()
    cycle_cuts: list[CycleCutSuggestion] = []

    for comp in sccs:
        if len(comp) >= 2:
            cycle_nodes.update(comp)
            cycle_cuts.append(_suggest_cut_for_scc(comp, graph))

    io_files = {
        tp.file
        for tp in touchpoints
        if tp.kind in {"persistence_db", "external_http_rpc"}
    }
    endpoint_files = {ep.file for ep in ast_facts.api_endpoints} if ast_facts is not None else set()

    wave1: list[str] = []
    wave2: list[str] = []
    wave3 = sorted(cycle_nodes)
    wave4: list[str] = []

    non_cycle = [n for n in sorted(graph) if n not in cycle_nodes]
    for node in non_cycle:
        deps = graph[node]
        is_entry = node in endpoint_files or node.lower().endswith(("app.java", "main.py", "index.php"))
        if not deps and not is_entry and node not in io_files:
            wave1.append(node)

    wave1_set = set(wave1)
    for node in non_cycle:
        if node in wave1_set:
            continue
        deps = graph[node]
        is_entry = node in endpoint_files or node.lower().endswith(("app.java", "main.py", "index.php"))
        if not is_entry and all(d in wave1_set for d in deps):
            wave2.append(node)
        else:
            wave4.append(node)

    waves = [
        RefactoringWave(
            wave=1,
            label="Wave 1: Leaf Models, Value Objects & Pure Utilities",
            modules=wave1,
            rationale="Zero internal dependencies and zero external I/O; safe to migrate/type first as Domain core.",
        ),
        RefactoringWave(
            wave=2,
            label="Wave 2: Outbound Infrastructure & Gateway/DB Clients",
            modules=wave2,
            rationale="Depends only on Wave 1 leaves; prime candidates for Outbound Port & Adapter extraction.",
        ),
        RefactoringWave(
            wave=3,
            label="Wave 3: Strongly Connected Components (Cycle Cut Targets)",
            modules=wave3,
            rationale="Bidirectional circular dependencies that must be severed before layered/Clean Arch isolation.",
        ),
        RefactoringWave(
            wave=4,
            label="Wave 4: Application Orchestrators, Controllers & Entrypoints",
            modules=wave4,
            rationale="Top-level inbound adapters and boot entrypoints wired after Domain, Ports, and Adapters exist.",
        ),
    ]
    return [w for w in waves if w.modules], cycle_cuts
