# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""On-demand GitHub Releases downloader and cache for extra Tree-sitter ABI3 grammars.

Follows the Drawlib release-asset caching architecture so ``pni501`` stays a pure-Python
(``py3-none-any``) wheel while still providing full cross-platform Tree-sitter AST parsing
for MIT-licensed grammars that lack 3-OS PyPI wheels (COBOL, R, Vue, Protocol Buffers,
and Dockerfile).
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import platform
import shutil
import sys
import tempfile
import threading
import urllib.request
import zipfile
from collections.abc import Generator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None  # type: ignore[assignment]

DEFAULT_GRAMMAR_REPO_OWNER: Final[str] = "yuichi110"
DEFAULT_GRAMMAR_REPO_NAME: Final[str] = "pni501"
DEFAULT_GRAMMAR_RELEASE_TAG: Final[str] = "grammars-v0.2.0"

EXTRA_GRAMMAR_ASSET_IDS: Final[tuple[str, ...]] = ("cobol", "dockerfile", "proto", "r", "vue")

ASSET_ID_TO_GRAMMAR_ID: Final[dict[str, str]] = {
    "cobol": "cobol",
    "dockerfile": "dockerfile",
    "proto": "protobuf",
    "r": "r",
    "vue": "vue",
}

GRAMMAR_ALIAS_TO_ASSET_ID: Final[dict[str, str]] = {
    "cobol": "cobol",
    "cob": "cobol",
    "cbl": "cobol",
    "dockerfile": "dockerfile",
    "docker": "dockerfile",
    "containerfile": "dockerfile",
    "proto": "proto",
    "protobuf": "proto",
    "r": "r",
    "rlang": "r",
    "vue": "vue",
    "vuejs": "vue",
}

SUPPORTED_PLATFORMS: Final[tuple[str, ...]] = (
    "linux_x86_64",
    "linux_aarch64",
    "macos_arm64",
    "macos_x86_64",
    "windows_amd64",
)

_THREAD_LOCKS_GUARD = threading.Lock()
_THREAD_LOCKS: dict[str, threading.Lock] = {}


@dataclass(frozen=True)
class GrammarReleaseAsset:
    """Metadata describing one downloadable per-language, per-platform ABI3 grammar archive."""

    asset_id: str
    grammar_id: str
    platform_tag: str
    archive_name: str
    binary_filename: str
    sha256: str
    size: int = 0

    def get_download_url(
        self,
        *,
        release_tag: str | None = None,
        base_url: str | None = None,
        repo_owner: str = DEFAULT_GRAMMAR_REPO_OWNER,
        repo_name: str = DEFAULT_GRAMMAR_REPO_NAME,
    ) -> str:
        """Return the HTTPS download URL for this grammar archive."""
        resolved_base = (base_url or os.environ.get("PNI_GRAMMAR_BASE_URL", "")).strip().rstrip("/")
        if resolved_base:
            return f"{resolved_base}/{self.archive_name}"
        tag = (release_tag or resolve_release_tag()).strip()
        return f"https://github.com/{repo_owner}/{repo_name}/releases/download/{tag}/{self.archive_name}"


@dataclass(frozen=True)
class GrammarCacheStatus:
    """Runtime status snapshot for one release-managed Tree-sitter grammar."""

    asset_id: str
    grammar_id: str
    platform_tag: str
    release_tag: str
    archive_name: str
    binary_path: Path
    cached: bool
    pinned_sha256: str
    size_bytes: int


# BEGIN PINNED_GRAMMAR_ASSETS
PINNED_GRAMMAR_ASSETS: Final[dict[tuple[str, str], GrammarReleaseAsset]] = {}
# END PINNED_GRAMMAR_ASSETS


def normalize_asset_id(name: str) -> str:
    """Resolve a language name or alias (e.g. 'protobuf') to its canonical asset_id ('proto')."""
    key = name.strip().lower()
    asset_id = GRAMMAR_ALIAS_TO_ASSET_ID.get(key)
    if asset_id is None:
        supported = ", ".join(EXTRA_GRAMMAR_ASSET_IDS)
        msg = f"Unknown extra Tree-sitter grammar '{name}'. Supported assets: {supported}."
        raise ValueError(msg)
    return asset_id


def resolve_release_tag(release_tag: str | None = None) -> str:
    """Return the active GitHub Release tag for extra grammar downloads."""
    if release_tag and release_tag.strip():
        return release_tag.strip()
    env_tag = os.environ.get("PNI_GRAMMAR_RELEASE_TAG", "").strip()
    return env_tag or DEFAULT_GRAMMAR_RELEASE_TAG


def detect_platform_tag(*, sys_platform: str | None = None, machine: str | None = None) -> str:
    """Detect the canonical PNI release platform tag for the current OS and CPU architecture."""
    plat = (sys_platform or sys.platform).lower()
    arch = (machine or platform.machine()).lower()

    if plat.startswith("linux"):
        if arch in {"x86_64", "amd64"}:
            return "linux_x86_64"
        if arch in {"aarch64", "arm64"}:
            return "linux_aarch64"
    elif plat == "darwin":
        if arch in {"arm64", "aarch64"}:
            return "macos_arm64"
        if arch in {"x86_64", "amd64"}:
            return "macos_x86_64"
    elif plat in {"win32", "cygwin"}:
        if arch in {"amd64", "x86_64"}:
            return "windows_amd64"

    supported = ", ".join(SUPPORTED_PLATFORMS)
    msg = (
        f"Unsupported platform for prebuilt PNI extra Tree-sitter grammars: "
        f"sys.platform={plat!r}, machine={arch!r}. Supported: {supported}."
    )
    raise RuntimeError(msg)


def default_binary_filename(asset_id: str, platform_tag: str) -> str:
    """Return the expected compiled extension filename for asset_id on platform_tag."""
    if platform_tag.startswith("windows_"):
        return f"_{asset_id}.pyd"
    return f"_{asset_id}.abi3.so"


def _is_dir_writable(path: Path) -> bool:
    """Return True if path can be created and written to by the current process."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / f".write_probe_{os.getpid()}_{threading.get_ident()}"
        probe.write_bytes(b"")
        probe.unlink(missing_ok=True)
    except OSError:
        return False
    return True


def _os_user_cache_dir() -> Path:
    """Return the standard OS user cache directory for pni501 grammar binaries."""
    if sys.platform == "win32":
        local_app = os.environ.get("LOCALAPPDATA")
        base = Path(local_app) if local_app else Path.home() / "AppData" / "Local"
        return base / "pni501" / "grammars"
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "pni501" / "grammars"


def resolve_grammar_cache_dir() -> Path:
    """Resolve a writable cache root for runtime-downloaded Tree-sitter grammar binaries.

    Precedence:
        1. ``PNI_GRAMMAR_CACHE_DIR`` environment variable (if set).
        2. Package-local ``pni/_cached_grammars`` directory (matching Drawlib) when writable.
        3. OS user cache directory (``~/.cache/pni501/grammars`` or ``%LOCALAPPDATA%``).
        4. System temp fallback (``<tmp>/pni501_grammars``).
    """
    env_override = os.environ.get("PNI_GRAMMAR_CACHE_DIR", "").strip()
    if env_override:
        override_path = Path(env_override).expanduser().resolve()
        override_path.mkdir(parents=True, exist_ok=True)
        return override_path

    pkg_cache = Path(__file__).resolve().parent.parent / "_cached_grammars"
    if _is_dir_writable(pkg_cache):
        return pkg_cache

    user_cache = _os_user_cache_dir()
    if _is_dir_writable(user_cache):
        return user_cache

    tmp_cache = Path(tempfile.gettempdir()) / "pni501_grammars"
    tmp_cache.mkdir(parents=True, exist_ok=True)
    return tmp_cache


def _get_thread_lock(lock_key: str) -> threading.Lock:
    """Return a per-key re-usable threading.Lock."""
    with _THREAD_LOCKS_GUARD:
        lock = _THREAD_LOCKS.get(lock_key)
        if lock is None:
            lock = threading.Lock()
            _THREAD_LOCKS[lock_key] = lock
        return lock


@contextlib.contextmanager
def _grammar_lock(cache_root: Path, lock_key: str) -> Generator[None]:
    """Acquire both an in-process thread lock and a cross-process advisory file lock."""
    thread_lock = _get_thread_lock(lock_key)
    locks_dir = cache_root / ".locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_file = locks_dir / f"{lock_key}.lock"

    with thread_lock:
        if fcntl is None:  # pragma: no cover - Windows
            yield
            return
        with lock_file.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _validate_download_url(url: str) -> None:
    """Restrict runtime downloads to HTTPS (or explicit HTTP mirror override)."""
    lower = url.lower()
    if lower.startswith("https://"):
        return
    if lower.startswith("http://") and os.environ.get("PNI_GRAMMAR_BASE_URL", "").strip():
        return
    msg = f"Refusing unsafe grammar download URL scheme: '{url}' (only https:// is permitted)."
    raise ValueError(msg)


def _http_get_bytes(url: str, *, timeout: int = 120) -> bytes:
    """Download raw bytes from a validated URL."""
    _validate_download_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "pni501-grammar-downloader/0.2"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return bytes(resp.read())


def _fetch_remote_manifest_asset(
    asset_id: str,
    platform_tag: str,
    *,
    release_tag: str,
    base_url: str | None = None,
) -> GrammarReleaseAsset:
    """Fallback lookup against remote manifest.json when a custom release tag is unpinned."""
    resolved_base = (base_url or os.environ.get("PNI_GRAMMAR_BASE_URL", "")).strip().rstrip("/")
    if resolved_base:
        manifest_url = f"{resolved_base}/manifest.json"
    else:
        manifest_url = (
            f"https://github.com/{DEFAULT_GRAMMAR_REPO_OWNER}/{DEFAULT_GRAMMAR_REPO_NAME}"
            f"/releases/download/{release_tag}/manifest.json"
        )
    raw = _http_get_bytes(manifest_url, timeout=60)
    payload = json.loads(raw.decode("utf-8"))
    for entry in payload.get("assets", []):
        if entry.get("asset_id") == asset_id and entry.get("platform") == platform_tag:
            return GrammarReleaseAsset(
                asset_id=asset_id,
                grammar_id=str(entry.get("grammar_id", ASSET_ID_TO_GRAMMAR_ID[asset_id])),
                platform_tag=platform_tag,
                archive_name=str(entry["archive_name"]),
                binary_filename=str(entry["binary_filename"]),
                sha256=str(entry.get("sha256", "")),
                size=int(entry.get("size", 0)),
            )
    msg = f"Grammar '{asset_id}' for platform '{platform_tag}' not listed in {manifest_url}."
    raise RuntimeError(msg)


def get_release_asset(
    asset_id: str,
    *,
    platform_tag: str | None = None,
    release_tag: str | None = None,
    base_url: str | None = None,
    allow_remote_manifest: bool = True,
) -> GrammarReleaseAsset:
    """Resolve the GrammarReleaseAsset descriptor for (asset_id, platform_tag)."""
    canonical = normalize_asset_id(asset_id)
    plat = platform_tag or detect_platform_tag()
    tag = resolve_release_tag(release_tag)

    if tag == DEFAULT_GRAMMAR_RELEASE_TAG:
        pinned = PINNED_GRAMMAR_ASSETS.get((canonical, plat))
        if pinned is not None:
            return pinned

    if allow_remote_manifest:
        try:
            return _fetch_remote_manifest_asset(canonical, plat, release_tag=tag, base_url=base_url)
        except Exception:
            if not PINNED_GRAMMAR_ASSETS:
                raise

    return GrammarReleaseAsset(
        asset_id=canonical,
        grammar_id=ASSET_ID_TO_GRAMMAR_ID[canonical],
        platform_tag=plat,
        archive_name=f"pni_grammar_{canonical}_{plat}.zip",
        binary_filename=default_binary_filename(canonical, plat),
        sha256="",
        size=0,
    )


def _extract_archive_atomically(archive_bytes: bytes, dest_dir: Path, archive_name: str) -> None:
    """Safely validate and atomically extract all files from a grammar ZIP archive."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_resolved = dest_dir.resolve()
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
        for member in zf.infolist():
            member_dest = (dest_resolved / member.filename).resolve()
            if not member_dest.is_relative_to(dest_resolved):
                msg = f"Unsafe archive member path '{member.filename}' in '{archive_name}'."
                raise ValueError(msg)
            if member.is_dir():
                member_dest.mkdir(parents=True, exist_ok=True)
                continue
            member_dest.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = member_dest.parent / f".tmp_{os.getpid()}_{threading.get_ident()}_{member_dest.name}"
            try:
                tmp_path.write_bytes(zf.read(member))
                if member_dest.suffix in {".so", ".dylib"}:
                    os.chmod(tmp_path, 0o700)
                os.replace(tmp_path, member_dest)
            except BaseException:
                tmp_path.unlink(missing_ok=True)
                raise


def get_cached_binary_path(
    asset_id: str,
    *,
    platform_tag: str | None = None,
    release_tag: str | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Return the deterministic cached binary path for (asset_id, platform_tag, release_tag)."""
    canonical = normalize_asset_id(asset_id)
    plat = platform_tag or detect_platform_tag()
    tag = resolve_release_tag(release_tag)
    root = cache_dir or resolve_grammar_cache_dir()
    pinned = PINNED_GRAMMAR_ASSETS.get((canonical, plat)) if tag == DEFAULT_GRAMMAR_RELEASE_TAG else None
    bin_name = pinned.binary_filename if pinned is not None else default_binary_filename(canonical, plat)
    return root / tag / plat / canonical / bin_name


def ensure_grammar_binary(
    asset_id: str,
    *,
    force: bool = False,
    release_tag: str | None = None,
    platform_tag: str | None = None,
    base_url: str | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Ensure the compiled ABI3 binary for asset_id is cached locally, downloading on demand."""
    canonical = normalize_asset_id(asset_id)
    plat = platform_tag or detect_platform_tag()
    tag = resolve_release_tag(release_tag)
    root = cache_dir or resolve_grammar_cache_dir()

    fast_path = get_cached_binary_path(canonical, platform_tag=plat, release_tag=tag, cache_dir=root)
    if not force and fast_path.is_file():
        return fast_path

    lock_key = f"{tag}_{plat}_{canonical}".replace("/", "_")
    with _grammar_lock(root, lock_key):
        if not force and fast_path.is_file():
            return fast_path

        asset = get_release_asset(
            canonical,
            platform_tag=plat,
            release_tag=tag,
            base_url=base_url,
        )
        dest_dir = root / tag / plat / canonical
        binary_path = dest_dir / asset.binary_filename
        if not force and binary_path.is_file():
            return binary_path

        url = asset.get_download_url(release_tag=tag, base_url=base_url)
        try:
            archive_bytes = _http_get_bytes(url, timeout=120)
        except Exception as exc:
            msg = (
                f"Failed to download Tree-sitter grammar '{canonical}' ({plat}) from '{url}': {exc}. "
                f"Check internet access or pre-cache via 'pni grammars prefetch {canonical}'."
            )
            raise RuntimeError(msg) from exc

        if asset.sha256:
            actual_sha = hashlib.sha256(archive_bytes).hexdigest().lower()
            if actual_sha != asset.sha256.lower():
                msg = (
                    f"SHA-256 checksum mismatch for '{asset.archive_name}': "
                    f"expected {asset.sha256}, got {actual_sha}."
                )
                raise RuntimeError(msg)

        _extract_archive_atomically(archive_bytes, dest_dir, asset.archive_name)
        if not binary_path.is_file():
            msg = f"Archive '{asset.archive_name}' did not contain expected binary '{asset.binary_filename}'."
            raise RuntimeError(msg)
        return binary_path


def load_grammar_capsule(asset_id: str) -> object:
    """Lazily download (if needed), dynamically import, and return the Language PyCapsule."""
    canonical = normalize_asset_id(asset_id)
    mod_name = f"pni._cached_grammars._{canonical}"
    existing = sys.modules.get(mod_name)
    if existing is not None:
        return existing.language()

    binary_path = ensure_grammar_binary(canonical)
    spec = importlib.util.spec_from_file_location(mod_name, binary_path)
    if spec is None or spec.loader is None:
        msg = f"Unable to create import spec for Tree-sitter binary '{binary_path}'."
        raise RuntimeError(msg)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        sys.modules.pop(mod_name, None)
        raise
    return mod.language()


def get_grammar_cache_statuses(
    *,
    release_tag: str | None = None,
    platform_tag: str | None = None,
    cache_dir: Path | None = None,
) -> list[GrammarCacheStatus]:
    """Return cache status entries for all five release-managed extra grammars."""
    plat = platform_tag or detect_platform_tag()
    tag = resolve_release_tag(release_tag)
    root = cache_dir or resolve_grammar_cache_dir()

    statuses: list[GrammarCacheStatus] = []
    for asset_id in EXTRA_GRAMMAR_ASSET_IDS:
        pinned = PINNED_GRAMMAR_ASSETS.get((asset_id, plat)) if tag == DEFAULT_GRAMMAR_RELEASE_TAG else None
        bin_name = pinned.binary_filename if pinned is not None else default_binary_filename(asset_id, plat)
        archive_name = pinned.archive_name if pinned is not None else f"pni_grammar_{asset_id}_{plat}.zip"
        bin_path = root / tag / plat / asset_id / bin_name
        cached = bin_path.is_file()
        size = bin_path.stat().st_size if cached else (pinned.size if pinned is not None else 0)
        statuses.append(
            GrammarCacheStatus(
                asset_id=asset_id,
                grammar_id=ASSET_ID_TO_GRAMMAR_ID[asset_id],
                platform_tag=plat,
                release_tag=tag,
                archive_name=archive_name,
                binary_path=bin_path,
                cached=cached,
                pinned_sha256=pinned.sha256 if pinned is not None else "",
                size_bytes=size,
            )
        )
    return statuses


def prefetch_grammars(
    targets: Sequence[str] | None = None,
    *,
    force: bool = False,
    release_tag: str | None = None,
    platform_tag: str | None = None,
    base_url: str | None = None,
    cache_dir: Path | None = None,
) -> list[Path]:
    """Download and cache one or more (or all) release-managed extra grammars upfront."""
    selected = tuple(normalize_asset_id(name) for name in targets) if targets else EXTRA_GRAMMAR_ASSET_IDS
    paths: list[Path] = []
    for asset_id in selected:
        paths.append(
            ensure_grammar_binary(
                asset_id,
                force=force,
                release_tag=release_tag,
                platform_tag=platform_tag,
                base_url=base_url,
                cache_dir=cache_dir,
            )
        )
    return paths


def clear_grammar_cache(
    *,
    release_tag: str | None = None,
    cache_dir: Path | None = None,
) -> int:
    """Remove cached grammar binary directories and return count of removed release folders."""
    root = cache_dir or resolve_grammar_cache_dir()
    if not root.is_dir():
        return 0
    if release_tag is not None:
        target = root / release_tag
        if target.is_dir():
            shutil.rmtree(target)
            return 1
        return 0

    removed = 0
    for child in root.iterdir():
        if child.name in {"__init__.py", ".gitignore", "__pycache__", ".locks"}:
            continue
        if child.is_dir():
            shutil.rmtree(child)
            removed += 1
        else:
            child.unlink(missing_ok=True)
            removed += 1
    return removed


def language_cobol() -> object:
    """Return the Tree-sitter Language PyCapsule for COBOL."""
    return load_grammar_capsule("cobol")


def language_r() -> object:
    """Return the Tree-sitter Language PyCapsule for R."""
    return load_grammar_capsule("r")


def language_vue() -> object:
    """Return the Tree-sitter Language PyCapsule for Vue SFC."""
    return load_grammar_capsule("vue")


def language_proto() -> object:
    """Return the Tree-sitter Language PyCapsule for Protocol Buffers."""
    return load_grammar_capsule("proto")


def language_dockerfile() -> object:
    """Return the Tree-sitter Language PyCapsule for Dockerfile."""
    return load_grammar_capsule("dockerfile")


__all__ = [
    "ASSET_ID_TO_GRAMMAR_ID",
    "DEFAULT_GRAMMAR_RELEASE_TAG",
    "DEFAULT_GRAMMAR_REPO_NAME",
    "DEFAULT_GRAMMAR_REPO_OWNER",
    "EXTRA_GRAMMAR_ASSET_IDS",
    "PINNED_GRAMMAR_ASSETS",
    "SUPPORTED_PLATFORMS",
    "GrammarCacheStatus",
    "GrammarReleaseAsset",
    "clear_grammar_cache",
    "detect_platform_tag",
    "ensure_grammar_binary",
    "get_cached_binary_path",
    "get_grammar_cache_statuses",
    "get_release_asset",
    "language_cobol",
    "language_dockerfile",
    "language_proto",
    "language_r",
    "language_vue",
    "load_grammar_capsule",
    "normalize_asset_id",
    "prefetch_grammars",
    "resolve_grammar_cache_dir",
    "resolve_release_tag",
]
