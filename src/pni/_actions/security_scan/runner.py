# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Stage S0-S3 containerized security and supply-chain scanning orchestrator."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

from pni._actions.project_inspect import ProjectFacts, run_project_inspect
from pni._actions.runtime_check.engine_detect import (
    build_container_image,
    detect_container_engine,
    remove_container_images,
)
from pni._actions.runtime_check.selector import (
    compute_harness_build_args,
    select_harness_tool,
)
from pni._actions.security_scan.models import (
    SecurityFacts,
    SecurityScanOptions,
    SecurityScanStatus,
    VulnerabilitySummaryCounts,
    VulnSeverity,
)
from pni._actions.security_scan.parsers import ParsedTrivyBundle, parse_trivy_reports
from pni._actions.security_scan.trivy_runner import (
    is_infra_or_db_unavailable_error,
    run_trivy_fs_scan,
    run_trivy_image_scan,
)
from pni._cache import (
    default_security_facts_rel_path,
    default_security_rel_dir,
    default_trivy_cache_rel_dir,
    ensure_cache_parent,
    normalize_target_subpath,
)
from pni._config import discover_gitignored_paths, load_pni_config
from pni._dockerfiles import ensure_target_dockerfile


def _security_image_slug(target_root_rel: str) -> str:
    """Create a deterministic Docker-safe tag slug from target_root."""
    norm = normalize_target_subpath(target_root_rel) or "root"
    digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()[:8]
    leaf = norm.rsplit("/", maxsplit=1)[-1].lower()
    safe_leaf = "".join(ch if ch.isalnum() else "-" for ch in leaf).strip("-") or "app"
    return f"{safe_leaf}-{digest}"


def _prepare_security_dirs(workspace_root: Path, workflow_id: str) -> tuple[Path, Path]:
    """Initialize `.pni/cache/<workflow_id>/security` and `.pni/cache/trivy-cache`."""
    sec_dir = workspace_root / default_security_rel_dir(workflow_id)
    trivy_cache = workspace_root / default_trivy_cache_rel_dir()
    ensure_cache_parent(workspace_root, sec_dir / "security_facts.json")
    trivy_cache.mkdir(parents=True, exist_ok=True)
    for stale_name in ("trivy_fs.json", "trivy_image.json", "image.tar", "scan.log"):
        (sec_dir / stale_name).unlink(missing_ok=True)
    return sec_dir, trivy_cache


def _persist_security_facts(workspace_root: Path, workflow_id: str, facts: SecurityFacts) -> SecurityFacts:
    """Write SecurityFacts JSON to `.pni/cache/<workflow_id>/security/security_facts.json`."""
    facts_file = workspace_root / default_security_facts_rel_path(workflow_id)
    ensure_cache_parent(workspace_root, facts_file)
    facts_file.write_text(facts.model_dump_json(indent=2), encoding="utf-8")
    return facts


def _append_scan_log(sec_dir: Path, stage_title: str, content: str) -> None:
    """Append stage diagnostic output to `scan.log`."""
    log_path = sec_dir / "scan.log"
    existing = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    block = f"=== {stage_title} ===\n{content.strip()}\n\n"
    log_path.write_text(existing + block, encoding="utf-8")


def _resolve_and_build_scan_image(
    engine_bin: str,
    ws_root: Path,
    target_dir: Path,
    target_root: str,
    pf: ProjectFacts,
    sec_dir: Path,
    build_timeout_sec: float,
    created_tags: list[str],
) -> tuple[Optional[str], str]:
    """Build project Dockerfile if valid, otherwise fall back to .pni/dockerfiles/ harness Dockerfile."""
    slug = _security_image_slug(target_root)
    proj_df = next(
        (target_dir / name for name in ("Dockerfile", "Containerfile") if (target_dir / name).is_file()),
        None,
    )
    if proj_df is not None:
        proj_tag = f"pni-sec-proj-{slug}:scan"
        p_res = build_container_image(engine_bin, proj_tag, proj_df, target_dir, {}, timeout_sec=build_timeout_sec)
        _append_scan_log(sec_dir, "build_project_dockerfile", p_res.combined_output)
        if not p_res.timed_out and p_res.exit_code == 0:
            created_tags.append(proj_tag)
            rel_df = proj_df.resolve().relative_to(ws_root).as_posix()
            return proj_tag, rel_df

    tool = select_harness_tool(pf)
    build_args = compute_harness_build_args(pf)
    harness_df, _ = ensure_target_dockerfile(ws_root, target_root, pf.language, tool)
    harness_tag = f"pni-sec-harness-{slug}:scan"
    h_res = build_container_image(
        engine_bin,
        harness_tag,
        harness_df,
        target_dir,
        build_args,
        timeout_sec=build_timeout_sec,
    )
    _append_scan_log(sec_dir, "build_harness_dockerfile", h_res.combined_output)
    if not h_res.timed_out and h_res.exit_code == 0:
        created_tags.append(harness_tag)
        rel_df = harness_df.resolve().relative_to(ws_root).as_posix()
        return harness_tag, rel_df
    return None, ""


def _counts_trigger_failure(counts: VulnerabilitySummaryCounts, fail_set: set[VulnSeverity]) -> bool:
    """Return True if any non-zero count matches `fail_set` severities."""
    return (
        ("CRITICAL" in fail_set and counts.critical > 0)
        or ("HIGH" in fail_set and counts.high > 0)
        or ("MEDIUM" in fail_set and counts.medium > 0)
        or ("LOW" in fail_set and counts.low > 0)
    )


def _derive_security_status(bundle: ParsedTrivyBundle, fail_severities: list[VulnSeverity]) -> SecurityScanStatus:
    """Derive `passed` or `failed` from deduplicated vulnerabilities, misconfigs, and secrets."""
    fail_set = set(fail_severities)
    if _counts_trigger_failure(bundle.app_vuln_counts, fail_set):
        return "failed"
    if any(m.severity in fail_set for m in bundle.misconfigurations):
        return "failed"
    if any(s.severity in fail_set for s in bundle.secrets):
        return "failed"
    return "passed"


def _handle_missing_engine(
    ws_root: Path,
    workflow_id: str,
    opts: SecurityScanOptions,
    sec_rel: str,
    reason: str,
) -> SecurityFacts:
    """Persist skipped SecurityFacts or raise RuntimeError according to `on_missing_runtime`."""
    if opts.on_missing_runtime == "fail":
        msg = f"Container runtime unavailable ({reason}) and on_missing_runtime='fail'"
        raise RuntimeError(msg)
    skipped = SecurityFacts(
        status="skipped",
        container_engine="none",
        engine_available=False,
        skip_reason=reason,
        trivy_image=opts.trivy_image,
        artifacts_dir=sec_rel,
    )
    return _persist_security_facts(ws_root, workflow_id, skipped)


def _execute_image_scan_stage(
    engine_name: str,
    engine_bin: str,
    ws_root: Path,
    target_dir: Path,
    target_root: str,
    pf: ProjectFacts,
    trivy_cache: Path,
    sec_dir: Path,
    opts: SecurityScanOptions,
    created_tags: list[str],
) -> tuple[bool, str]:
    """Build resolved container image and scan its installed packages with `trivy image`."""
    scan_tag, resolved_source = _resolve_and_build_scan_image(
        engine_bin,
        ws_root,
        target_dir,
        target_root,
        pf,
        sec_dir,
        float(opts.build_timeout_sec),
        created_tags,
    )
    if scan_tag is None:
        return False, ""
    img_res = run_trivy_image_scan(
        engine_name,
        engine_bin,
        opts.trivy_image,
        scan_tag,
        trivy_cache,
        sec_dir,
        timeout_sec=float(opts.scan_timeout_sec),
    )
    _append_scan_log(sec_dir, "trivy_image", img_res.combined_output)
    scanned_ok = not img_res.timed_out and (sec_dir / "trivy_image.json").is_file()
    return scanned_ok, (resolved_source if scanned_ok else "")


def run_security_scan(
    workspace_root: Path,
    workflow_id: str,
    *,
    target_root: str = ".",
    source_targets: Optional[list[str]] = None,
    test_targets: Optional[list[str]] = None,
    lang: Optional[str] = None,
    project_facts: Optional[ProjectFacts] = None,
    options: Optional[SecurityScanOptions] = None,
) -> SecurityFacts:
    """Execute Stage S0-S3 containerized Trivy vulnerability, IaC, and secret scanning."""
    opts = options or SecurityScanOptions()
    ws_root = workspace_root.resolve()
    target_dir = (ws_root / target_root).resolve()
    pni_cfg = load_pni_config(ws_root)
    sec_dir, trivy_cache = _prepare_security_dirs(ws_root, workflow_id)
    sec_rel = default_security_rel_dir(workflow_id)

    engine_name, engine_bin, reason = detect_container_engine(opts.container_engine)
    if engine_name is None or engine_bin is None:
        return _handle_missing_engine(ws_root, workflow_id, opts, sec_rel, reason)

    pf = project_facts or run_project_inspect(
        target_dir,
        source_dirs=source_targets if source_targets is not None else ["src"],
        test_dirs=test_targets if test_targets is not None else ["tests"],
        lang=lang,
    )

    ignored_files, ignored_dirs = (
        discover_gitignored_paths(target_dir, include_gitignored=pni_cfg.scan.include_gitignored)
        if pni_cfg.scan.respect_gitignore
        else ([], [])
    )
    eff_skip_files = [*ignored_files, *pni_cfg.scan.skip_files]
    eff_skip_dirs = [*ignored_dirs, *pni_cfg.scan.skip_dirs]

    scanned_fs = False
    scanned_img = False
    resolved_img_src = ""
    created_tags: list[str] = []

    try:
        if opts.scan_filesystem:
            extra_skip_kwargs: dict[str, list[str]] = {}
            if eff_skip_files:
                extra_skip_kwargs["skip_files"] = eff_skip_files
            if eff_skip_dirs:
                extra_skip_kwargs["skip_dirs"] = eff_skip_dirs
            fs_res = run_trivy_fs_scan(
                engine_name,
                engine_bin,
                opts.trivy_image,
                target_dir,
                trivy_cache,
                sec_dir,
                timeout_sec=float(opts.scan_timeout_sec),
                **extra_skip_kwargs,
            )
            _append_scan_log(sec_dir, "trivy_fs", fs_res.combined_output)
            if fs_res.timed_out:
                return _persist_security_facts(
                    ws_root,
                    workflow_id,
                    SecurityFacts(
                        status="timeout",
                        container_engine=engine_name,
                        engine_available=True,
                        skip_reason="trivy fs timed out",
                        trivy_image=opts.trivy_image,
                        artifacts_dir=sec_rel,
                    ),
                )
            if (sec_dir / "trivy_fs.json").is_file():
                scanned_fs = True
            elif is_infra_or_db_unavailable_error(fs_res.combined_output) and opts.on_missing_runtime != "fail":
                return _persist_security_facts(
                    ws_root,
                    workflow_id,
                    SecurityFacts(
                        status="skipped",
                        container_engine=engine_name,
                        engine_available=True,
                        skip_reason="Trivy image or vulnerability DB unavailable offline",
                        trivy_image=opts.trivy_image,
                        artifacts_dir=sec_rel,
                    ),
                )
            else:
                return _persist_security_facts(
                    ws_root,
                    workflow_id,
                    SecurityFacts(
                        status="error",
                        container_engine=engine_name,
                        engine_available=True,
                        skip_reason=f"trivy fs exited with code {fs_res.exit_code}",
                        trivy_image=opts.trivy_image,
                        artifacts_dir=sec_rel,
                    ),
                )

        if opts.scan_resolved_image:
            scanned_img, resolved_img_src = _execute_image_scan_stage(
                engine_name,
                engine_bin,
                ws_root,
                target_dir,
                target_root,
                pf,
                trivy_cache,
                sec_dir,
                opts,
                created_tags,
            )

        bundle = parse_trivy_reports(
            fs_json_path=sec_dir / "trivy_fs.json" if scanned_fs else None,
            image_json_path=sec_dir / "trivy_image.json" if scanned_img else None,
            opt_outs=pni_cfg.opt_out,
            skip_files=eff_skip_files,
            skip_dirs=eff_skip_dirs,
        )
        status = _derive_security_status(bundle, opts.fail_on_severities)
        completed = SecurityFacts(
            status=status,
            container_engine=engine_name,
            engine_available=True,
            trivy_image=opts.trivy_image,
            scanned_filesystem=scanned_fs,
            scanned_resolved_image=scanned_img,
            resolved_image_source=resolved_img_src,
            artifacts_dir=sec_rel,
            vuln_counts=bundle.vuln_counts,
            app_vuln_counts=bundle.app_vuln_counts,
            os_vuln_counts=bundle.os_vuln_counts,
            vulnerabilities=bundle.vulnerabilities,
            misconfigurations=bundle.misconfigurations,
            secrets=bundle.secrets,
            opt_out_counts=bundle.opt_out_counts,
        )
        return _persist_security_facts(ws_root, workflow_id, completed)
    finally:
        if created_tags:
            remove_container_images(engine_bin, created_tags)
