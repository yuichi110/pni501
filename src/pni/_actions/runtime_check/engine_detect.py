# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Docker / Podman engine discovery and hardened subprocess execution wrappers."""

from __future__ import annotations

import os
import shutil
import subprocess  # noqa: S404
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional

_SUPPORTED_ENGINES: Final[tuple[str, ...]] = ("docker", "podman")
_PREFLIGHT_TIMEOUT_SEC: Final[float] = 5.0


@dataclass(frozen=True)
class CommandExecResult:
    """Captured stdout, stderr, exit code, and timing of a non-shell subprocess call."""

    exit_code: Optional[int]
    timed_out: bool
    duration_sec: float
    stdout: str
    stderr: str

    @property
    def combined_output(self) -> str:
        """Return merged stdout and stderr text."""
        parts = [seg for seg in (self.stdout.strip(), self.stderr.strip()) if seg]
        return "\n".join(parts)

    def tail_lines(self, limit: int = 30) -> list[str]:
        """Return up to the last `limit` non-empty output lines."""
        non_empty = [ln.rstrip() for ln in self.combined_output.splitlines() if ln.strip()]
        return non_empty[-limit:]


def _decode_stream(raw: str | bytes | None) -> str:
    """Normalize subprocess output stream into UTF-8 string."""
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return raw


def run_safe_command(
    args: list[str],
    *,
    timeout_sec: float,
    cwd: Optional[Path] = None,
) -> CommandExecResult:
    """Execute an argument-list command with shell=False and strict timeout enforcement.

    Args:
        args: Executable path and argument list.
        timeout_sec: Maximum allowed runtime in seconds.
        cwd: Optional working directory.

    Returns:
        CommandExecResult: Captured output, exit code, and timeout indicator.
    """
    started = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout_sec,
            check=False,
        )
        elapsed = round(time.monotonic() - started, 2)
        return CommandExecResult(
            exit_code=proc.returncode,
            timed_out=False,
            duration_sec=elapsed,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = round(time.monotonic() - started, 2)
        return CommandExecResult(
            exit_code=None,
            timed_out=True,
            duration_sec=elapsed,
            stdout=_decode_stream(exc.stdout),
            stderr=_decode_stream(exc.stderr),
        )


def detect_container_engine(preference: str = "auto") -> tuple[Optional[str], Optional[str], str]:
    """Detect an active Docker or Podman container runtime on Linux / macOS.

    Args:
        preference: 'auto', 'docker', or 'podman'.

    Returns:
        tuple[Optional[str], Optional[str], str]: (engine_name, binary_path, diagnostic_reason).
    """
    pref = preference.strip().lower() or "auto"
    candidates = _SUPPORTED_ENGINES if pref == "auto" else (pref,)

    reasons: list[str] = []
    for name in candidates:
        if name not in _SUPPORTED_ENGINES:
            reasons.append(f"Unsupported container_engine={name!r}")
            continue
        binary = shutil.which(name)
        if binary is None:
            reasons.append(f"'{name}' CLI not found on PATH")
            continue
        probe = run_safe_command([binary, "info"], timeout_sec=_PREFLIGHT_TIMEOUT_SEC)
        if not probe.timed_out and probe.exit_code == 0:
            return name, binary, "ok"
        detail = "timed out" if probe.timed_out else f"exit={probe.exit_code}"
        reasons.append(f"'{name} info' unavailable ({detail})")

    return None, None, "; ".join(reasons) or "No container runtime detected"


def build_container_image(
    engine_bin: str,
    image_tag: str,
    dockerfile: Path,
    context_dir: Path,
    build_args: dict[str, str],
    *,
    timeout_sec: float = 240.0,
) -> CommandExecResult:
    """Build a container image from an explicit Dockerfile and context directory."""
    cmd: list[str] = [engine_bin, "build", "-t", image_tag, "-f", str(dockerfile)]
    for key in sorted(build_args):
        val = build_args[key]
        if val != "":
            cmd.extend(["--build-arg", f"{key}={val}"])
    cmd.append(str(context_dir))
    return run_safe_command(cmd, timeout_sec=timeout_sec)


def _host_user_flags() -> list[str]:
    """Return non-root host UID:GID mapping and writable HOME=/tmp flags on POSIX hosts."""
    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        uid = os.getuid()
        gid = os.getgid()
        if uid != 0:
            return ["--user", f"{uid}:{gid}", "-e", "HOME=/tmp"]
    return ["-e", "HOME=/tmp"]


def run_container_command(
    engine_name: str,
    engine_bin: str,
    image_tag: str,
    cmd_args: list[str],
    out_dir: Path,
    *,
    allow_network: bool = False,
    timeout_sec: float = 120.0,
    env_vars: Optional[dict[str, str]] = None,
) -> CommandExecResult:
    """Run an ephemeral resource-capped container mounting out_dir at /out."""
    out_dir.mkdir(parents=True, exist_ok=True)
    vol_suffix = "rw,Z" if engine_name == "podman" else "rw"
    cmd: list[str] = [
        engine_bin,
        "run",
        "--rm",
        "--memory=2g",
        "--cpus=2",
        "--pids-limit=256",
        "--security-opt=no-new-privileges",
    ]
    if engine_name == "podman":
        cmd.append("--userns=keep-id")
    cmd.extend(_host_user_flags())
    if not allow_network:
        cmd.append("--network=none")
    for key in sorted(env_vars or {}):
        cmd.extend(["-e", f"{key}={(env_vars or {})[key]}"])
    cmd.extend(["-v", f"{out_dir.resolve()}:/out:{vol_suffix}", image_tag, *cmd_args])
    return run_safe_command(cmd, timeout_sec=timeout_sec)


def remove_container_images(engine_bin: str, image_tags: list[str]) -> None:
    """Remove temporary tagged images while leaving base/layer caches intact."""
    unique_tags = [t for t in dict.fromkeys(image_tags) if t]
    if not unique_tags:
        return
    run_safe_command([engine_bin, "rmi", "-f", *unique_tags], timeout_sec=20.0)
