# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Parse-once orchestrator binding language-specific AST and framework checkers."""

from __future__ import annotations

import contextlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ast_grep_py import SgRoot

from pni._actions.ast_analyze.base import (
    BaseDependencyChecker,
    BaseDocChecker,
    BaseFrameworkChecker,
    BaseImportChecker,
    BaseOperationalChecker,
    BaseQualityChecker,
    BaseSecurityChecker,
    BaseTestChecker,
    BaseTypingChecker,
)
from pni._actions.ast_analyze.models import (
    IGNORED_DIR_NAMES,
    AstFacts,
    CodeLocation,
    FrameworkCheckResult,
    OperationalResult,
    ParsedUnit,
    SecurityAstResult,
    SecuritySinkLocation,
    matches_exclude_globs,
)
from pni._actions.ast_analyze.version_compat import check_language_version_compatibility
from pni._actions.project_inspect import run_project_inspect
from pni._config import OptOutEntry, load_pni_config, match_opt_out


def _bug_risk_check_ids(detail: str) -> tuple[str, ...]:
    """Return check ID candidates for a bug_risk_idioms CodeLocation."""
    if "(S307)" in detail:
        return ("CWE-94", "S307", "ast/code_execution", "ast/bug_risk_idioms")
    if "(S602)" in detail:
        return ("CWE-78", "S602", "ast/command_injection", "ast/bug_risk_idioms")
    if "(S301)" in detail or "(S506)" in detail:
        return ("CWE-502", "S301", "S506", "ast/unsafe_deserialization", "ast/bug_risk_idioms")
    return ("ast/bug_risk_idioms",)


def _boundary_check_ids(detail: str) -> tuple[str, ...]:
    """Return check ID candidates for a boundary_violations CodeLocation."""
    lower = detail.lower()
    if "private module" in lower or "private submodule" in lower:
        return ("ast/private_submodule_import", "ast/boundary_violations", "common/architecture")
    return ("ast/boundary_violations", "common/architecture")


def _filter_locations_by_opt_out(
    locations: list[CodeLocation],
    opt_outs: Sequence[OptOutEntry],
    check_ids_fn: Callable[[CodeLocation], Sequence[str]],
    counts: dict[str, int],
    *,
    already_counted_positions: Optional[set[tuple[str, str, int]]] = None,
) -> list[CodeLocation]:
    """Filter CodeLocation items against [[opt_out]] waivers and update counts."""
    if not opt_outs or not locations:
        return locations
    kept: list[CodeLocation] = []
    for loc in locations:
        matched = match_opt_out(opt_outs, check_ids_fn(loc), loc.file)
        if matched is not None:
            pos_key = (matched.id, loc.file, loc.line)
            if already_counted_positions is None or pos_key not in already_counted_positions:
                counts[matched.id] = counts.get(matched.id, 0) + 1
                if already_counted_positions is not None:
                    already_counted_positions.add(pos_key)
        else:
            kept.append(loc)
    return kept


def _filter_sinks_by_opt_out(
    sinks: list[SecuritySinkLocation],
    opt_outs: Sequence[OptOutEntry],
    counts: dict[str, int],
    counted_positions: set[tuple[str, str, int]],
) -> list[SecuritySinkLocation]:
    """Filter SecuritySinkLocation items against [[opt_out]] waivers and record positions."""
    if not opt_outs or not sinks:
        return sinks
    kept: list[SecuritySinkLocation] = []
    for sink in sinks:
        matched = match_opt_out(
            opt_outs,
            (sink.cwe_id, f"ast/{sink.category}", sink.category),
            sink.file,
        )
        if matched is not None:
            counts[matched.id] = counts.get(matched.id, 0) + 1
            counted_positions.add((matched.id, sink.file, sink.line))
        else:
            kept.append(sink)
    return kept


def _is_ignored_path(path: Path, root: Path, exclude_globs: Sequence[str] = ()) -> bool:
    """Return True if path is inside an ignored/hidden directory or matches exclude_globs."""
    rel_parts = path.relative_to(root).parts
    if any(part in IGNORED_DIR_NAMES or part.startswith(".") for part in rel_parts[:-1]):
        return True
    return matches_exclude_globs(path, root, exclude_globs)


def _collect_dir_files(
    directory: Path,
    project_root: Path,
    extensions: tuple[str, ...],
    exclude_globs: Sequence[str] = (),
) -> list[Path]:
    """Return sorted non-ignored files under directory matching any extension."""
    collected: list[Path] = []
    for ext in extensions:
        for match in sorted(directory.rglob(f"*{ext}")):
            if not _is_ignored_path(match, project_root, exclude_globs) and match not in collected:
                collected.append(match)
    return collected


def discover_source_files(
    project_root: Path,
    targets: list[str],
    extensions: tuple[str, ...],
    *,
    fallback_dirs: tuple[str, ...] = (),
    allow_root_glob: bool = True,
    exclude_globs: Sequence[str] = (),
) -> list[Path]:
    """Discover non-ignored source files matching extensions across relative target paths."""
    found: list[Path] = []
    for tdir in targets:
        candidate = project_root / tdir
        if candidate.is_dir():
            found.extend(
                f for f in _collect_dir_files(candidate, project_root, extensions, exclude_globs) if f not in found
            )
        elif (
            candidate.is_file()
            and candidate.suffix in extensions
            and not matches_exclude_globs(candidate, project_root, exclude_globs)
            and candidate not in found
        ):
            found.append(candidate)

    for fb in fallback_dirs:
        if found:
            break
        fb_dir = project_root / fb
        if fb_dir.is_dir():
            found.extend(_collect_dir_files(fb_dir, project_root, extensions, exclude_globs))

    if not found and allow_root_glob:
        for ext in extensions:
            found.extend(
                p
                for p in sorted(project_root.glob(f"*{ext}"))
                if not matches_exclude_globs(p, project_root, exclude_globs) and p not in found
            )

    return found


@dataclass(frozen=True)
class LanguageAnalyzerSuite:
    """Cohesive language suite executing specialized AST and framework checkers over once-parsed CSTs."""

    language: str
    ast_grep_lang: str
    file_extensions: tuple[str, ...]
    default_target_dirs: tuple[str, ...]
    fallback_dirs: tuple[str, ...]
    import_checker: BaseImportChecker
    quality_checker: BaseQualityChecker
    typing_checker: BaseTypingChecker
    doc_checker: BaseDocChecker
    dependency_checker: BaseDependencyChecker
    test_checker: BaseTestChecker
    operational_checker: Optional[BaseOperationalChecker] = None
    security_checker: Optional[BaseSecurityChecker] = None
    default_test_dirs: tuple[str, ...] = ()
    framework_checkers: tuple[BaseFrameworkChecker, ...] = ()
    source_preprocessor: Optional[Callable[[str], str]] = None

    def _parse_units(self, files: list[Path], display_root: Path) -> list[ParsedUnit]:
        """Parse discovered source files once into immutable ParsedUnit instances."""
        units: list[ParsedUnit] = []
        for src_file in files:
            source = ""
            with contextlib.suppress(Exception):
                source = src_file.read_text(encoding="utf-8")
            if not source and not src_file.exists():
                continue
            cst_source = self.source_preprocessor(source) if self.source_preprocessor is not None else source
            root = SgRoot(cst_source, self.ast_grep_lang).root()
            if root.has(kind="ERROR"):
                continue
            rel_str = (
                src_file.relative_to(display_root).as_posix()
                if src_file.is_relative_to(display_root)
                else src_file.name
            )
            units.append(
                ParsedUnit(
                    file_path=src_file,
                    rel_path=rel_str,
                    source=source,
                    root=root,
                )
            )
        return units

    def _run_framework_checkers(
        self,
        units: list[ParsedUnit],
        project_root: Path,
        detected_frameworks: Optional[list[str]],
    ) -> FrameworkCheckResult:
        """Execute applicable framework checkers for the active project."""
        if not self.framework_checkers:
            return FrameworkCheckResult()
        fw_set = (
            set(detected_frameworks)
            if detected_frameworks is not None
            else set(run_project_inspect(project_root, lang=self.language).detected_frameworks)
        )
        issues: list[CodeLocation] = []
        hints: list[CodeLocation] = []
        for checker in self.framework_checkers:
            if checker.applies_to(fw_set, units):
                res = checker.check(units)
                issues.extend(res.framework_issues)
                hints.extend(res.modernization_hints)
        return FrameworkCheckResult(framework_issues=issues, modernization_hints=hints)

    def analyze(
        self,
        project_root: Path,
        targets: Optional[list[str]] = None,
        display_root: Optional[Path] = None,
        test_targets: Optional[list[str]] = None,
        detected_frameworks: Optional[list[str]] = None,
        declared_lang_version: Optional[str] = None,
        exclude_globs: Optional[list[str]] = None,
    ) -> AstFacts:
        """Discover source and test files, parse CSTs once, run all checkers, and compose AstFacts.

        Args:
            project_root: Target project root directory.
            targets: Optional relative source directory or file paths inside project_root.
            display_root: Optional workspace root used to format CodeLocation file paths.
            test_targets: Optional relative test directory paths inside project_root.
            detected_frameworks: Optional pre-detected framework identifiers.
            declared_lang_version: Optional declared language version constraint from ProjectFacts.
            exclude_globs: Optional glob patterns relative to project_root to exclude from discovery.

        Returns:
            AstFacts: Language-agnostic deterministic AST metrics and pinpointed locations.
        """
        base_display = display_root or project_root
        pni_cfg = load_pni_config(base_display)
        eff_targets = (
            targets
            if targets is not None
            else (list(pni_cfg.targets.source) if pni_cfg.targets.source else list(self.default_target_dirs))
        )
        eff_test_dirs = (
            test_targets
            if test_targets is not None
            else (list(pni_cfg.targets.tests) if pni_cfg.targets.tests else list(self.default_test_dirs))
        )
        eff_excludes = (
            exclude_globs
            if exclude_globs is not None
            else (list(pni_cfg.targets.exclude) if pni_cfg.targets.exclude else [])
        )
        raw_test_files = discover_source_files(
            project_root,
            eff_test_dirs,
            self.file_extensions,
            allow_root_glob=False,
            exclude_globs=eff_excludes,
        )
        files = discover_source_files(
            project_root,
            eff_targets,
            self.file_extensions,
            fallback_dirs=self.fallback_dirs,
            exclude_globs=eff_excludes,
        )
        if "." in eff_targets and raw_test_files:
            raw_test_set = set(raw_test_files)
            files = [f for f in files if f not in raw_test_set]
            test_files = raw_test_files
        else:
            src_set = set(files)
            test_files = [tf for tf in raw_test_files if tf not in src_set]

        units = self._parse_units(files, base_display)
        test_units = self._parse_units(test_files, base_display)

        if detected_frameworks is None or declared_lang_version is None:
            inspected = run_project_inspect(project_root, lang=self.language, exclude_globs=eff_excludes)
            eff_frameworks = (
                detected_frameworks if detected_frameworks is not None else inspected.detected_frameworks
            )
            eff_version = (
                declared_lang_version
                if declared_lang_version is not None
                else inspected.language_version_constraint
            )
        else:
            eff_frameworks = detected_frameworks
            eff_version = declared_lang_version

        import_res = self.import_checker.check(units, project_root)
        quality_res = self.quality_checker.check(units)
        typing_res = self.typing_checker.check(units)
        doc_res = self.doc_checker.check(units)
        dep_res = self.dependency_checker.check(units, project_root)
        test_res = self.test_checker.check(test_units, units, project_root)
        op_res = self.operational_checker.check(units) if self.operational_checker is not None else OperationalResult()
        sec_res = self.security_checker.check(units) if self.security_checker is not None else SecurityAstResult()
        fw_res = self._run_framework_checkers(units, project_root, eff_frameworks)
        ver_mismatches = check_language_version_compatibility(self.language, eff_version, units)

        opt_outs = pni_cfg.opt_out
        opt_out_counts: dict[str, int] = {}
        counted_positions: set[tuple[str, str, int]] = set()
        filtered_sinks = _filter_sinks_by_opt_out(
            sec_res.dangerous_sinks, opt_outs, opt_out_counts, counted_positions
        )
        filtered_bug_risk = _filter_locations_by_opt_out(
            quality_res.bug_risk_idioms,
            opt_outs,
            lambda loc: _bug_risk_check_ids(loc.detail),
            opt_out_counts,
            already_counted_positions=counted_positions,
        )
        filtered_boundary = _filter_locations_by_opt_out(
            dep_res.boundary_violations,
            opt_outs,
            lambda loc: _boundary_check_ids(loc.detail),
            opt_out_counts,
        )
        filtered_excessive_params = _filter_locations_by_opt_out(
            quality_res.excessive_parameters,
            opt_outs,
            lambda _loc: ("ast/excessive_parameters", "common/code_quality"),
            opt_out_counts,
        )
        filtered_complex_fns = _filter_locations_by_opt_out(
            quality_res.complex_functions,
            opt_outs,
            lambda _loc: ("ast/complex_functions", "common/code_quality"),
            opt_out_counts,
        )
        filtered_global_state = _filter_locations_by_opt_out(
            quality_res.global_state_usages,
            opt_outs,
            lambda _loc: ("ast/global_state", "ast/global_state_usages", "common/code_quality"),
            opt_out_counts,
        )
        filtered_hardcoded_secrets = _filter_locations_by_opt_out(
            op_res.hardcoded_secrets,
            opt_outs,
            lambda _loc: ("ast/hardcoded_secrets", "common/security"),
            opt_out_counts,
        )

        return AstFacts(
            language=self.language,
            total_files=len(files),
            total_loc=quality_res.total_loc,
            total_classes=quality_res.total_classes,
            total_functions=quality_res.total_functions,
            module_inventory=quality_res.module_inventory,
            import_hygiene_coverage_pct=import_res.import_hygiene_coverage_pct,
            unsorted_imports=import_res.unsorted_imports,
            wildcard_imports=import_res.wildcard_imports,
            late_imports=import_res.late_imports,
            type_safety_coverage_pct=typing_res.type_safety_coverage_pct,
            type_safety_issues=typing_res.type_safety_issues,
            weak_type_usages=typing_res.weak_type_usages,
            unscoped_type_ignores=typing_res.unscoped_type_ignores,
            docstring_coverage_pct=doc_res.docstring_coverage_pct,
            missing_docstrings=doc_res.missing_docstrings,
            empty_docstrings=doc_res.empty_docstrings,
            doc_signature_mismatches=doc_res.doc_signature_mismatches,
            complex_functions=filtered_complex_fns,
            excessive_parameters=filtered_excessive_params,
            global_state_usages=filtered_global_state,
            bug_risk_idioms=filtered_bug_risk,
            internal_import_graph=dep_res.internal_import_graph,
            circular_dependencies=dep_res.circular_dependencies,
            type_checking_cycles=dep_res.type_checking_cycles,
            unused_dependencies=dep_res.unused_dependencies,
            undeclared_dependencies=dep_res.undeclared_dependencies,
            boundary_violations=filtered_boundary,
            test_functions_count=test_res.test_functions_count,
            module_test_coverage_pct=test_res.module_test_coverage_pct,
            assertion_free_tests=test_res.assertion_free_tests,
            test_harness_notes=test_res.test_harness_notes,
            framework_issues=fw_res.framework_issues,
            modernization_hints=fw_res.modernization_hints,
            language_version_mismatches=ver_mismatches,
            missing_io_timeouts=op_res.missing_io_timeouts,
            scattered_env_access=op_res.scattered_env_access,
            unstructured_logging=op_res.unstructured_logging,
            hardcoded_secrets=filtered_hardcoded_secrets,
            dangerous_sinks=filtered_sinks,
            api_endpoints=sec_res.api_endpoints,
            opt_out_counts=opt_out_counts,
        )
