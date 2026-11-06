# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Socketless Docker / Podman execution helpers for Trivy filesystem and image scanning."""

from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pni._actions.runtime_check.engine_detect import CommandExecResult, run_safe_command

_SKIP_FS_DIRS: Final[str] = ".pni,.git,.venv,venv,node_modules,__pycache__,.mypy_cache,.ruff_cache"


def _format_skip_dirs_arg(skip_dirs: Sequence[str]) -> str:
    """Combine built-in skipped directories with project-configured/gitignored skip_dirs."""
    items: list[str] = list(_SKIP_FS_DIRS.split(","))
    for raw in skip_dirs:
        cleaned = raw.strip().strip("/")
        if cleaned and cleaned not in items:
            items.append(cleaned)
    return ",".join(items)


def _format_skip_files_arg(skip_files: Sequence[str]) -> str:
    """Format skip_files patterns for Trivy container mount (/target/...)."""
    items: list[str] = []
    for raw in skip_files:
        cleaned = raw.strip()
        if not cleaned:
            continue
        container_rel = cleaned if cleaned.startswith("/") else f"/target/{cleaned.lstrip('/')}"
        for candidate in (cleaned, container_rel):
            if candidate not in items:
                items.append(candidate)
    return ",".join(items)


def _user_and_security_flags(engine_name: str) -> list[str]:
    """Return hardened resource, privilege, and host-UID mapping flags for Trivy containers."""
    flags: list[str] = [
        "--rm",
        "--memory=2g",
        "--cpus=2",
        "--pids-limit=256",
        "--security-opt=no-new-privileges",
    ]
    if engine_name == "podman":
        flags.append("--userns=keep-id")
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        uid = os.getuid()
        gid = os.getgid()
        if uid != 0:
            flags.extend(["--user", f"{uid}:{gid}"])
    flags.extend(["-e", "HOME=/tmp"])
    return flags


def has_cached_trivy_db(trivy_cache_dir: Path) -> bool:
    """Return True if a previously downloaded Trivy vulnerability DB exists on disk."""
    return (trivy_cache_dir / "db" / "metadata.json").is_file()


def is_infra_or_db_unavailable_error(output: str) -> bool:
    """Return True if failure output indicates image pull or offline DB bootstrap failure."""
    lowered = output.lower()
    markers = (
        "unable to find image",
        "pull access denied",
        "failed to download vulnerability db",
        "failed to download artifact",
        "dial tcp",
        "temporary failure in name resolution",
        "network is unreachable",
        "i/o timeout",
        "connection refused",
        "toomanyrequests",
    )
    return any(m in lowered for m in markers)


def _build_trivy_container_cmd(
    engine_name: str,
    engine_bin: str,
    trivy_image: str,
    mounts: list[tuple[Path, str, bool]],
    trivy_args: list[str],
    *,
    offline: bool = False,
) -> list[str]:
    """Construct `docker/podman run` invocation for Trivy without mounting any Docker socket."""
    cmd: list[str] = [engine_bin, "run", *_user_and_security_flags(engine_name)]
    if offline:
        cmd.append("--network=none")
    for host_path, container_path, read_only in mounts:
        mode = "ro" if read_only else "rw"
        if engine_name == "podman":
            mode = f"{mode},Z"
        cmd.extend(["-v", f"{host_path.resolve()}:{container_path}:{mode}"])
    cmd.extend([trivy_image, *trivy_args])
    return cmd


def run_trivy_fs_scan(
    engine_name: str,
    engine_bin: str,
    trivy_image: str,
    target_dir: Path,
    trivy_cache_dir: Path,
    sec_dir: Path,
    *,
    timeout_sec: float = 240.0,
    skip_files: Sequence[str] = (),
    skip_dirs: Sequence[str] = (),
) -> CommandExecResult:
    """Run `trivy fs` (vuln, misconfig, secret) with shared DB cache and offline retry."""
    trivy_cache_dir.mkdir(parents=True, exist_ok=True)
    sec_dir.mkdir(parents=True, exist_ok=True)
    mounts = [
        (target_dir, "/target", True),
        (trivy_cache_dir, "/trivy-cache", False),
        (sec_dir, "/out", False),
    ]
    base_args = [
        "fs",
        "--cache-dir",
        "/trivy-cache",
        "--cache-backend",
        "memory",
        "--scanners",
        "vuln,misconfig,secret",
        "--skip-dirs",
        _format_skip_dirs_arg(skip_dirs),
    ]
    skip_files_str = _format_skip_files_arg(skip_files)
    if skip_files_str:
        base_args.extend(["--skip-files", skip_files_str])
    base_args.extend(
        [
            "--quiet",
            "--format",
            "json",
            "--output",
            "/out/trivy_fs.json",
        ]
    )
    cmd = _build_trivy_container_cmd(
        engine_name,
        engine_bin,
        trivy_image,
        mounts,
        [*base_args, "/target"],
    )
    res = run_safe_command(cmd, timeout_sec=timeout_sec)
    if res.exit_code == 0 or res.timed_out or not has_cached_trivy_db(trivy_cache_dir):
        return res

    offline_args = [
        *base_args,
        "--skip-db-update",
        "--skip-java-db-update",
        "--offline-scan",
        "/target",
    ]
    retry_cmd = _build_trivy_container_cmd(
        engine_name,
        engine_bin,
        trivy_image,
        mounts,
        offline_args,
        offline=True,
    )
    return run_safe_command(retry_cmd, timeout_sec=timeout_sec)


def run_trivy_image_scan(
    engine_name: str,
    engine_bin: str,
    trivy_image: str,
    target_image_tag: str,
    trivy_cache_dir: Path,
    sec_dir: Path,
    *,
    timeout_sec: float = 240.0,
) -> CommandExecResult:
    """Export target_image_tag to a temporary tar archive and scan via `trivy image --input`."""
    trivy_cache_dir.mkdir(parents=True, exist_ok=True)
    sec_dir.mkdir(parents=True, exist_ok=True)
    image_tar = sec_dir / "image.tar"

    try:
        save_res = run_safe_command(
            [engine_bin, "save", "-o", str(image_tar), target_image_tag],
            timeout_sec=min(timeout_sec, 120.0),
        )
        if save_res.timed_out or save_res.exit_code != 0:
            return save_res

        mounts = [
            (trivy_cache_dir, "/trivy-cache", False),
            (sec_dir, "/out", False),
        ]
        base_args = [
            "image",
            "--cache-dir",
            "/trivy-cache",
            "--cache-backend",
            "memory",
            "--scanners",
            "vuln",
            "--quiet",
            "--input",
            "/out/image.tar",
            "--format",
            "json",
            "--output",
            "/out/trivy_image.json",
        ]
        cmd = _build_trivy_container_cmd(engine_name, engine_bin, trivy_image, mounts, base_args)
        res = run_safe_command(cmd, timeout_sec=timeout_sec)
        if res.exit_code == 0 or res.timed_out or not has_cached_trivy_db(trivy_cache_dir):
            return res

        offline_args = [*base_args, "--skip-db-update", "--skip-java-db-update", "--offline-scan"]
        retry_cmd = _build_trivy_container_cmd(
            engine_name,
            engine_bin,
            trivy_image,
            mounts,
            offline_args,
            offline=True,
        )
        return run_safe_command(retry_cmd, timeout_sec=timeout_sec)
    finally:
        image_tar.unlink(missing_ok=True)
