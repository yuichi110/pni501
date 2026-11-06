# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Abstract base checker for internal dependency graphs, cycles, manifest hygiene, and boundaries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar, Final

from pni._actions.ast_analyze.models import CodeLocation, DependencyResult, ParsedUnit

_DEFAULT_MAX_CYCLES_PER_SCC: Final[int] = 5
_DEFAULT_MAX_TOTAL_CYCLES: Final[int] = 50
_DEFAULT_MAX_STEPS_PER_SCC: Final[int] = 2000


def _tarjan_nontrivial_sccs(graph: dict[str, list[str]]) -> list[list[str]]:
    """Compute non-trivial strongly connected components in O(V + E) using an explicit DFS stack."""
    index_counter = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    tarjan_stack: list[str] = []
    sccs: list[list[str]] = []

    for root in sorted(graph):
        if root in indices:
            continue
        indices[root] = index_counter
        lowlink[root] = index_counter
        index_counter += 1
        tarjan_stack.append(root)
        on_stack.add(root)
        neighbors_root = [n for n in graph.get(root, []) if n in graph]
        call_stack: list[tuple[str, list[str], int]] = [(root, neighbors_root, 0)]

        while call_stack:
            node, neighbors, idx = call_stack[-1]
            if idx < len(neighbors):
                call_stack[-1] = (node, neighbors, idx + 1)
                succ = neighbors[idx]
                if succ not in indices:
                    indices[succ] = index_counter
                    lowlink[succ] = index_counter
                    index_counter += 1
                    tarjan_stack.append(succ)
                    on_stack.add(succ)
                    succ_neighbors = [n for n in graph.get(succ, []) if n in graph]
                    call_stack.append((succ, succ_neighbors, 0))
                elif succ in on_stack:
                    lowlink[node] = min(lowlink[node], indices[succ])
                continue

            call_stack.pop()
            if call_stack:
                parent = call_stack[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])

            if lowlink[node] == indices[node]:
                comp = _pop_scc_component(tarjan_stack, on_stack, node)
                if len(comp) > 1 or node in graph.get(node, []):
                    sccs.append(sorted(comp))

    return sorted(sccs, key=lambda c: c[0])


def _pop_scc_component(tarjan_stack: list[str], on_stack: set[str], head: str) -> list[str]:
    """Pop nodes from Tarjan's stack up to head inclusive."""
    comp: list[str] = []
    while tarjan_stack:
        member = tarjan_stack.pop()
        on_stack.discard(member)
        comp.append(member)
        if member == head:
            break
    return comp


def _canonicalize_cycle(path: list[str]) -> tuple[str, ...]:
    """Rotate a closed simple path (without trailing repeat) so its smallest node is first."""
    min_idx = min(range(len(path)), key=lambda i: path[i])
    rotated = [*path[min_idx:], *path[:min_idx]]
    return (*rotated, rotated[0])


def _search_cycles_from_start(
    start: str,
    scc_set: set[str],
    graph: dict[str, list[str]],
    seen: set[tuple[str, ...]],
    found: list[list[str]],
    *,
    max_cycles: int,
    remaining_steps: int,
) -> int:
    """Run bounded iterative DFS from start inside scc_set and return steps consumed."""
    dfs_stack: list[tuple[str, list[str], set[str]]] = [(start, [start], {start})]
    steps = 0
    while dfs_stack and len(found) < max_cycles and steps < remaining_steps:
        curr, path, visited = dfs_stack.pop()
        steps += 1
        for neighbor in reversed(graph.get(curr, [])):
            if neighbor not in scc_set or neighbor < start:
                continue
            if neighbor == start and len(path) > 1:
                canon = _canonicalize_cycle(path)
                if canon not in seen:
                    seen.add(canon)
                    found.append(list(canon))
            elif neighbor not in visited:
                dfs_stack.append((neighbor, [*path, neighbor], {*visited, neighbor}))
    return steps


def _extract_scc_cycles(
    scc_nodes: list[str],
    graph: dict[str, list[str]],
    *,
    max_cycles: int,
    max_steps: int,
) -> list[list[str]]:
    """Extract bounded canonical elementary cycles within a single non-trivial SCC subgraph."""
    if len(scc_nodes) == 1:
        only = scc_nodes[0]
        return [[only, only]] if only in graph.get(only, []) else []

    scc_set = set(scc_nodes)
    seen: set[tuple[str, ...]] = set()
    found: list[list[str]] = []
    steps = 0

    for start in scc_nodes:
        if len(found) >= max_cycles or steps >= max_steps:
            break
        steps += _search_cycles_from_start(
            start,
            scc_set,
            graph,
            seen,
            found,
            max_cycles=max_cycles,
            remaining_steps=max_steps - steps,
        )
    return found[:max_cycles]


class BaseDependencyChecker(ABC):
    """Template-method base class for internal graph, cycle, manifest, and boundary checks."""

    cycles_applicable: ClassVar[bool] = True

    def check(self, units: list[ParsedUnit], project_root: Path) -> DependencyResult:
        """Build internal dependency graph, detect cycles, and inspect manifest/boundary hygiene.

        Args:
            units: Parsed compilation units in the target project.
            project_root: Target project root directory.

        Returns:
            DependencyResult: Adjacency graph, cycles, manifest mismatches, and boundary violations.
        """
        graph = self.build_import_graph(units, project_root)
        cycles = self.detect_cycles(graph) if self.cycles_applicable else []
        tc_cycles = self.detect_type_checking_cycles(units, project_root, cycles) if self.cycles_applicable else []
        unused, undeclared = self.check_manifest_dependencies(units, project_root)
        boundaries = self.check_boundary_violations(units, project_root)
        return DependencyResult(
            internal_import_graph=graph,
            circular_dependencies=cycles,
            type_checking_cycles=tc_cycles,
            unused_dependencies=unused,
            undeclared_dependencies=undeclared,
            boundary_violations=boundaries,
        )

    @staticmethod
    def detect_cycles(
        graph: dict[str, list[str]],
        *,
        max_cycles_per_scc: int = _DEFAULT_MAX_CYCLES_PER_SCC,
        max_total_cycles: int = _DEFAULT_MAX_TOTAL_CYCLES,
        max_steps_per_scc: int = _DEFAULT_MAX_STEPS_PER_SCC,
    ) -> list[list[str]]:
        """Detect canonical elementary cycles via O(V + E) Tarjan SCC decomposition and bounded search."""
        cycles: list[list[str]] = []
        for scc in _tarjan_nontrivial_sccs(graph):
            remaining = max_total_cycles - len(cycles)
            if remaining <= 0:
                break
            scc_cycles = _extract_scc_cycles(
                scc,
                graph,
                max_cycles=min(max_cycles_per_scc, remaining),
                max_steps=max_steps_per_scc,
            )
            cycles.extend(scc_cycles)
        return cycles

    def detect_type_checking_cycles(
        self,
        units: list[ParsedUnit],
        project_root: Path,
        runtime_cycles: list[list[str]],
    ) -> list[list[str]]:
        """Detect cycles introduced exclusively by static type-checking guards (e.g., if TYPE_CHECKING)."""
        _ = (units, project_root, runtime_cycles)
        return []

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check declared manifest packages against actual third-party imports."""
        _ = (units, project_root)
        return [], []

    def check_boundary_violations(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> list[CodeLocation]:
        """Detect cross-package imports referencing private/internal modules."""
        _ = (units, project_root)
        return []

    @abstractmethod
    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Build sorted internal dependency adjacency lists keyed by module or type identifier."""
