# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Stage 0-4 containerized runtime verification orchestrator."""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pni._actions.project_inspect import ProjectFacts, run_project_inspect
from pni._actions.runtime_check.engine_detect import (
    CommandExecResult,
    build_container_image,
    detect_container_engine,
    remove_container_images,
    run_container_command,
)
from pni._actions.runtime_check.models import (
    ContainerBuildResult,
    CoverageResult,
    RuntimeFacts,
    RuntimeStageStatus,
    SmokeCheckResult,
    TestExecutionResult,
)
from pni._actions.runtime_check.parsers import (
    parse_clover_xml,
    parse_go_coverprofile,
    parse_go_test_output,
    parse_istanbul_coverage_summary,
    parse_jacoco_xml,
    parse_junit_xml_files,
    parse_lcov_info,
    parse_node_test_output,
    parse_pytest_coverage_json,
)
from pni._actions.runtime_check.selector import (
    build_test_and_coverage_command,
    compute_harness_build_args,
    select_harness_tool,
)
from pni._actions.runtime_check.smoke import build_smoke_plan, evaluate_smoke_outcome
from pni._cache import (
    default_runtime_facts_rel_path,
    default_runtime_rel_dir,
    ensure_cache_parent,
    normalize_target_subpath,
)
from pni._dockerfiles import ensure_target_dockerfile


@dataclass(frozen=True)
class RuntimeCheckOptions:
    """Configuration options controlling containerized build, test, coverage, and smoke stages."""

    container_engine: str = "auto"
    on_missing_runtime: str = "skip"
    dockerfile: str = ""
    force_regenerate_dockerfile: bool = False
    extra_apt_packages: str = ""
    test_cmd: str = ""
    pytest_extra_args: tuple[str, ...] = ()
    pre_test_cmd: str = ""
    smoke_cmd: str = ""
    smoke_port: int = 18080
    allow_test_network: bool = False
    cleanup_images: bool = True
    build_timeout_sec: float = 240.0
    test_timeout_sec: float = 120.0
    smoke_timeout_sec: float = 30.0


def _target_image_slug(target_root_rel: str) -> str:
    """Create a deterministic Docker-safe tag slug from target_root."""
    norm = normalize_target_subpath(target_root_rel) or "root"
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]
    leaf = norm.rsplit("/", maxsplit=1)[-1].lower()
    safe_leaf = "".join(ch if ch.isalnum() else "-" for ch in leaf).strip("-") or "app"
    return f"{safe_leaf}-{digest}"


def _prepare_runtime_dirs(workspace_root: Path, workflow_id: str) -> tuple[Path, Path]:
    """Initialize .pni/cache/<workflow_id>/runtime and reset its out/ directory."""
    rt_dir = workspace_root / default_runtime_rel_dir(workflow_id)
    out_dir = rt_dir / "out"
    ensure_cache_parent(workspace_root, rt_dir / "runtime_facts.json")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return rt_dir, out_dir


def _to_build_result(dockerfile_display: str, res: CommandExecResult) -> ContainerBuildResult:
    """Convert a container build subprocess result into ContainerBuildResult."""
    if res.timed_out:
        status: RuntimeStageStatus = "timeout"
    elif res.exit_code == 0:
        status = "passed"
    else:
        status = "failed"
    return ContainerBuildResult(
        attempted=True,
        status=status,
        dockerfile_used=dockerfile_display,
        duration_sec=res.duration_sec,
        exit_code=res.exit_code,
        error_tail=[] if status == "passed" else res.tail_lines(30),
    )


def _check_project_dockerfile_if_present(
    engine_bin: str,
    target_dir: Path,
    workspace_root: Path,
    slug: str,
    rt_dir: Path,
    timeout_sec: float,
) -> tuple[Optional[ContainerBuildResult], Optional[str]]:
    """Stage 1A: Build the target repository's own Dockerfile/Containerfile when present."""
    proj_df = next(
        (target_dir / name for name in ("Dockerfile", "Containerfile") if (target_dir / name).is_file()),
        None,
    )
    if proj_df is None:
        return None, None

    tag = f"pni-proj-{slug}:verify"
    res = build_container_image(engine_bin, tag, proj_df, target_dir, {}, timeout_sec=timeout_sec)
    (rt_dir / "project_build.log").write_text(res.combined_output, encoding="utf-8")
    rel_display = proj_df.resolve().relative_to(workspace_root.resolve()).as_posix()
    return _to_build_result(rel_display, res), tag


def _execute_test_and_coverage_stage(
    engine_name: str,
    engine_bin: str,
    harness_tag: str,
    pf: ProjectFacts,
    tool: str,
    source_targets: list[str],
    test_targets: list[str],
    out_dir: Path,
    rt_dir: Path,
    options: RuntimeCheckOptions,
) -> tuple[TestExecutionResult, CoverageResult]:
    """Stage 2: Run offline unit tests inside harness image and parse JUnit + coverage reports."""
    cmd_args = build_test_and_coverage_command(
        pf,
        tool,
        source_targets,
        test_targets,
        override_cmd=options.test_cmd,
        pytest_extra_args=options.pytest_extra_args,
        pre_test_cmd=options.pre_test_cmd,
    )
    res = run_container_command(
        engine_name,
        engine_bin,
        harness_tag,
        cmd_args,
        out_dir,
        allow_network=options.allow_test_network,
        timeout_sec=options.test_timeout_sec,
    )
    (rt_dir / "test.log").write_text(res.combined_output, encoding="utf-8")

    xml_files: list[Path] = []
    if (out_dir / "junit.xml").is_file():
        xml_files.append(out_dir / "junit.xml")
    if (out_dir / "surefire").is_dir():
        xml_files.extend(sorted((out_dir / "surefire").glob("*.xml")))

    total, passed, failed, errors, skipped, failures = parse_junit_xml_files(xml_files)
    if total == 0 and pf.language == "go":
        total, passed, failed, errors, skipped, failures = parse_go_test_output(out_dir / "go_test.txt")
    elif total == 0 and pf.language in {"typescript", "javascript"}:
        total, passed, failed, errors, skipped, failures = parse_node_test_output(out_dir / "node_test.txt")

    if res.timed_out:
        t_status: RuntimeStageStatus = "timeout"
    elif res.exit_code == 0 and failed == 0 and errors == 0:
        t_status = "passed"
    else:
        t_status = "failed"

    test_res = TestExecutionResult(
        attempted=True,
        status=t_status,
        command=" ".join(cmd_args[:4]) if len(cmd_args) > 4 else " ".join(cmd_args),
        duration_sec=res.duration_sec,
        exit_code=res.exit_code,
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        error_tests=errors,
        skipped_tests=skipped,
        failures=failures,
        log_tail=[] if t_status == "passed" else res.tail_lines(25),
    )

    cov_res = _parse_stage_coverage(pf.language, source_targets, out_dir)
    return test_res, cov_res


def _parse_node_stage_coverage(out_dir: Path) -> CoverageResult:
    """Parse Istanbul coverage-summary.json, LCOV lcov.info, or Clover XML from out_dir."""
    cov_res = parse_istanbul_coverage_summary(out_dir / "coverage-summary.json")
    if not cov_res.measured and (out_dir / "lcov.info").is_file():
        return parse_lcov_info(out_dir / "lcov.info")
    if not cov_res.measured and (out_dir / "clover.xml").is_file():
        return parse_clover_xml(out_dir / "clover.xml")
    return cov_res


def _parse_stage_coverage(language: str, source_targets: list[str], out_dir: Path) -> CoverageResult:
    """Parse language-specific coverage artifact from out_dir into a canonical CoverageResult."""
    if language == "java":
        src_prefix = source_targets[0] if source_targets else "src/main/java"
        return parse_jacoco_xml(out_dir / "jacoco.xml", source_root_prefix=src_prefix)
    if language == "php":
        return parse_clover_xml(out_dir / "clover.xml")
    if language == "go":
        return parse_go_coverprofile(out_dir / "coverage.out")
    if language in {"typescript", "javascript"}:
        return _parse_node_stage_coverage(out_dir)
    return parse_pytest_coverage_json(out_dir / "coverage.json")


def _execute_smoke_stage(
    engine_name: str,
    engine_bin: str,
    harness_tag: str,
    target_dir: Path,
    pf: ProjectFacts,
    source_targets: list[str],
    out_dir: Path,
    rt_dir: Path,
    options: RuntimeCheckOptions,
) -> SmokeCheckResult:
    """Stage 3: Execute archetype-specific startup / import / CLI help verification."""
    archetype, smoke_cmd = build_smoke_plan(
        target_dir,
        pf,
        source_targets,
        override_cmd=options.smoke_cmd,
        smoke_port=options.smoke_port,
    )
    if smoke_cmd is None:
        return SmokeCheckResult(
            attempted=False,
            archetype=archetype,
            status="skipped",
            detail="No discoverable package or entrypoint for smoke probe",
        )

    res = run_container_command(
        engine_name,
        engine_bin,
        harness_tag,
        smoke_cmd,
        out_dir,
        allow_network=options.allow_test_network,
        timeout_sec=options.smoke_timeout_sec,
    )
    (rt_dir / "smoke.log").write_text(res.combined_output, encoding="utf-8")
    return evaluate_smoke_outcome(archetype, smoke_cmd, res, out_dir)


def _derive_overall_status(
    proj_build: Optional[ContainerBuildResult],
    harness_build: ContainerBuildResult,
    test_res: TestExecutionResult,
    smoke_res: SmokeCheckResult,
) -> RuntimeStageStatus:
    """Derive top-level RuntimeFacts.status across executed stages."""
    statuses = [harness_build.status, test_res.status, smoke_res.status]
    if proj_build is not None:
        statuses.append(proj_build.status)
    if "timeout" in statuses:
        return "timeout"
    if "failed" in statuses or "error" in statuses:
        return "failed"
    return "passed"


def _persist_runtime_facts(workspace_root: Path, workflow_id: str, facts: RuntimeFacts) -> RuntimeFacts:
    """Write RuntimeFacts JSON to .pni/cache/<workflow_id>/runtime/runtime_facts.json."""
    facts_file = workspace_root / default_runtime_facts_rel_path(workflow_id)
    ensure_cache_parent(workspace_root, facts_file)
    facts_file.write_text(facts.model_dump_json(indent=2), encoding="utf-8")
    return facts


def run_runtime_check(
    workspace_root: Path,
    workflow_id: str,
    *,
    target_root: str = ".",
    source_targets: Optional[list[str]] = None,
    test_targets: Optional[list[str]] = None,
    lang: Optional[str] = None,
    project_facts: Optional[ProjectFacts] = None,
    options: Optional[RuntimeCheckOptions] = None,
) -> RuntimeFacts:
    """Execute Stage 0-4 containerized dynamic verification and persist artifacts under .pni/cache/.

    Args:
        workspace_root: Workspace root directory containing .pni/.
        workflow_id: Active workflow identifier.
        target_root: Relative path to target project root (e.g. '.' or 'examples/python/lib_clean').
        source_targets: Relative source directories inside target_root.
        test_targets: Relative test directories inside target_root.
        lang: Optional explicit language override ('python', 'java').
        project_facts: Optional pre-computed ProjectFacts for target_root.
        options: Optional RuntimeCheckOptions configuration.

    Returns:
        RuntimeFacts: Deterministic build, test, coverage, and startup verification facts.

    Raises:
        RuntimeError: When container runtime is unavailable and options.on_missing_runtime == 'fail'.
    """
    opts = options or RuntimeCheckOptions()
    ws_root = workspace_root.resolve()
    target_dir = (ws_root / target_root).resolve()
    eff_sources = source_targets if source_targets is not None else ["src"]
    eff_tests = test_targets if test_targets is not None else ["tests"]

    pf = project_facts or run_project_inspect(
        target_dir,
        source_dirs=eff_sources,
        test_dirs=eff_tests,
        lang=lang,
    )
    tool = select_harness_tool(pf)
    rt_dir, out_dir = _prepare_runtime_dirs(ws_root, workflow_id)

    harness_df, template_id = ensure_target_dockerfile(
        ws_root,
        target_root,
        pf.language,
        tool,
        explicit_dockerfile=opts.dockerfile,
        force_regenerate=opts.force_regenerate_dockerfile,
    )
    build_args = compute_harness_build_args(
        pf,
        extra_apt_packages=opts.extra_apt_packages,
        harness_dockerfile=harness_df,
    )
    harness_df_rel = harness_df.resolve().relative_to(ws_root).as_posix()
    rt_rel = default_runtime_rel_dir(workflow_id)

    engine_name, engine_bin, reason = detect_container_engine(opts.container_engine)
    if engine_name is None or engine_bin is None:
        if opts.on_missing_runtime.strip().lower() == "fail":
            msg = f"Container runtime unavailable ({reason}) and on_missing_runtime='fail'"
            raise RuntimeError(msg)
        skipped = RuntimeFacts(
            status="skipped",
            container_engine=None,
            engine_available=False,
            skip_reason=reason,
            language=pf.language,
            selected_dockerfile_template=template_id,
            harness_dockerfile_path=harness_df_rel,
            build_args=build_args,
            artifacts_dir=rt_rel,
        )
        return _persist_runtime_facts(ws_root, workflow_id, skipped)

    slug = _target_image_slug(target_root)
    harness_tag = f"pni-harness-{slug}:verify"
    created_tags: list[str] = []

    try:
        proj_build, proj_tag = _check_project_dockerfile_if_present(
            engine_bin,
            target_dir,
            ws_root,
            slug,
            rt_dir,
            opts.build_timeout_sec,
        )
        if proj_tag:
            created_tags.append(proj_tag)

        h_exec = build_container_image(
            engine_bin,
            harness_tag,
            harness_df,
            target_dir,
            build_args,
            timeout_sec=opts.build_timeout_sec,
        )
        (rt_dir / "build.log").write_text(h_exec.combined_output, encoding="utf-8")
        created_tags.append(harness_tag)
        harness_res = _to_build_result(harness_df_rel, h_exec)

        if harness_res.status != "passed":
            blocked = RuntimeFacts(
                status=harness_res.status,
                container_engine=engine_name,
                engine_available=True,
                language=pf.language,
                selected_dockerfile_template=template_id,
                harness_dockerfile_path=harness_df_rel,
                build_args=build_args,
                artifacts_dir=rt_rel,
                project_dockerfile_build=proj_build,
                harness_build=harness_res,
                test_execution=TestExecutionResult(attempted=False, status="blocked"),
                smoke_check=SmokeCheckResult(
                    attempted=False,
                    archetype="+".join(pf.runtime_types or ["library"]),
                    status="blocked",
                    detail="Blocked by harness build failure",
                ),
            )
            return _persist_runtime_facts(ws_root, workflow_id, blocked)

        test_res, cov_res = _execute_test_and_coverage_stage(
            engine_name,
            engine_bin,
            harness_tag,
            pf,
            tool,
            eff_sources,
            eff_tests,
            out_dir,
            rt_dir,
            opts,
        )
        smoke_res = _execute_smoke_stage(
            engine_name,
            engine_bin,
            harness_tag,
            target_dir,
            pf,
            eff_sources,
            out_dir,
            rt_dir,
            opts,
        )
        overall = _derive_overall_status(proj_build, harness_res, test_res, smoke_res)
        completed = RuntimeFacts(
            status=overall,
            container_engine=engine_name,
            engine_available=True,
            language=pf.language,
            selected_dockerfile_template=template_id,
            harness_dockerfile_path=harness_df_rel,
            build_args=build_args,
            artifacts_dir=rt_rel,
            project_dockerfile_build=proj_build,
            harness_build=harness_res,
            test_execution=test_res,
            coverage=cov_res,
            smoke_check=smoke_res,
        )
        return _persist_runtime_facts(ws_root, workflow_id, completed)
    finally:
        if opts.cleanup_images and created_tags:
            remove_container_images(engine_bin, created_tags)
