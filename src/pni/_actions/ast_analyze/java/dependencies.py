# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Java internal FQN import and same-package type dependency checker."""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pni._actions.ast_analyze.base import BaseDependencyChecker
from pni._actions.ast_analyze.java._helpers import unit_fqn
from pni._actions.ast_analyze.models import CodeLocation, ParsedUnit
from pni._actions.project_inspect import run_project_inspect

_REQUIRED_JAVA_MODULE_MARKERS: Final[tuple[tuple[str, tuple[str, ...], str], ...]] = (
    (
        "org.springframework.transaction.",
        ("spring-tx", "starter-jdbc", "starter-data-", "starter-jooq", "starter-batch", "spring-orm"),
        "Spring transaction API imported without 'spring-tx' or data/jdbc starter in manifest",
    ),
    (
        "org.springframework.security.",
        ("spring-security", "starter-security"),
        "Spring Security API imported without 'spring-boot-starter-security' or 'spring-security' in manifest",
    ),
    (
        "jakarta.validation.",
        ("validation", "hibernate-validator"),
        "Jakarta Bean Validation API imported without validation dependency in manifest",
    ),
    (
        "javax.validation.",
        ("validation", "hibernate-validator"),
        "Bean Validation API imported without validation dependency in manifest",
    ),
    (
        "jakarta.persistence.",
        ("persistence", "starter-data-jpa", "hibernate-core"),
        "Jakarta Persistence API imported without JPA/persistence dependency in manifest",
    ),
    (
        "javax.persistence.",
        ("persistence", "starter-data-jpa", "hibernate-core"),
        "JPA API imported without JPA/persistence dependency in manifest",
    ),
)
_JAVA_TEST_IMPORT_PREFIXES: Final[tuple[str, ...]] = (
    "org.junit.",
    "junit.framework.",
    "org.mockito.",
    "org.assertj.",
)


def _resolve_import_targets(
    imp_text: str,
    current_fqn: str,
    known_fqns: set[str],
    pkg_to_fqns: dict[str, list[str]],
    used_simple_names: set[str],
) -> set[str]:
    """Resolve a single Java import declaration into matching internal FQNs."""
    raw = imp_text.removeprefix("import").strip().removesuffix(";").strip()
    is_static = raw.startswith("static ")
    target = raw.removeprefix("static ").strip()

    if target.endswith(".*"):
        wildcard_pkg = target[:-2]
        return {
            cand
            for cand in pkg_to_fqns.get(wildcard_pkg, [])
            if cand != current_fqn and cand.rsplit(".", maxsplit=1)[-1] in used_simple_names
        }
    if target in known_fqns and target != current_fqn:
        return {target}
    if is_static and "." in target:
        owner_fqn = target.rsplit(".", maxsplit=1)[0]
        if owner_fqn in known_fqns and owner_fqn != current_fqn:
            return {owner_fqn}
    return set()


def _extract_unit_dependencies(
    unit: ParsedUnit,
    pkg_name: str,
    current_fqn: str,
    known_fqns: set[str],
    pkg_to_fqns: dict[str, list[str]],
) -> list[str]:
    """Extract sorted internal FQN dependencies from explicit imports and same-package usages."""
    deps: set[str] = set()
    used_simple_names = {
        n.text() for n in [*unit.root.find_all(kind="type_identifier"), *unit.root.find_all(kind="identifier")]
    }

    for imp in unit.root.find_all(kind="import_declaration"):
        deps.update(_resolve_import_targets(imp.text(), current_fqn, known_fqns, pkg_to_fqns, used_simple_names))

    for sibling_fqn in pkg_to_fqns.get(pkg_name, []):
        if sibling_fqn != current_fqn and sibling_fqn.rsplit(".", maxsplit=1)[-1] in used_simple_names:
            deps.add(sibling_fqn)

    return sorted(deps)


class JavaDependencyChecker(BaseDependencyChecker):
    """Build 2-pass internal Java FQN dependency graph and audit Maven/Gradle manifest imports."""

    def build_import_graph(self, units: list[ParsedUnit], project_root: Path) -> dict[str, list[str]]:
        """Index package/FQN symbols (Pass 1) and extract internal dependencies (Pass 2)."""
        _ = project_root
        indexed = [(unit, *unit_fqn(unit)) for unit in units]
        known_fqns = {fqn for _, _, fqn in indexed}
        pkg_to_fqns: dict[str, list[str]] = {}
        for _, pkg_name, fqn in indexed:
            pkg_to_fqns.setdefault(pkg_name, []).append(fqn)

        graph: dict[str, list[str]] = {}
        for unit, pkg_name, fqn in indexed:
            graph[fqn] = _extract_unit_dependencies(unit, pkg_name, fqn, known_fqns, pkg_to_fqns)
        return graph

    def check_manifest_dependencies(
        self,
        units: list[ParsedUnit],
        project_root: Path,
    ) -> tuple[list[str], list[CodeLocation]]:
        """Cross-check production Java imports against declared Maven/Gradle runtime dependencies."""
        pf = run_project_inspect(project_root, lang="java")
        if not pf.manifest_files:
            return [], []

        declared_runtime = [d.lower() for d in pf.dependencies]
        undeclared: list[CodeLocation] = []
        seen: set[tuple[str, str]] = set()

        for unit in units:
            for imp in unit.root.find_all(kind="import_declaration"):
                raw = imp.text().removeprefix("import").strip().removesuffix(";").strip()
                target = raw.removeprefix("static ").strip()
                lineno = imp.range().start.line + 1

                for prefix, markers, detail in _REQUIRED_JAVA_MODULE_MARKERS:
                    if target.startswith(prefix) and not any(
                        m in dep for dep in declared_runtime for m in markers
                    ):
                        if (unit.rel_path, prefix) not in seen:
                            seen.add((unit.rel_path, prefix))
                            undeclared.append(
                                CodeLocation(file=unit.rel_path, line=lineno, symbol=target, detail=detail)
                            )

                for test_prefix in _JAVA_TEST_IMPORT_PREFIXES:
                    if target.startswith(test_prefix) and not any(
                        "junit" in dep or "mockito" in dep or "assertj" in dep for dep in declared_runtime
                    ):
                        if (unit.rel_path, test_prefix) not in seen:
                            seen.add((unit.rel_path, test_prefix))
                            undeclared.append(
                                CodeLocation(
                                    file=unit.rel_path,
                                    line=lineno,
                                    symbol=target,
                                    detail=f"Test-scoped dependency '{target}' imported in production source",
                                )
                            )

        return [], undeclared
