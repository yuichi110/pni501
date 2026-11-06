# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Project-level .pni/pni.toml manifest loader, gitignore scope resolver, and design waiver matcher."""

from __future__ import annotations

import contextlib
import fnmatch
import shutil
import subprocess  # noqa: S404
import tomllib
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Final, Optional

from pydantic import BaseModel, Field, field_validator

from pni._actions._repo_governance import RuntimeArchetype, matches_exclude_globs

DEFAULT_PNI_TOML_REL_PATH: Final[str] = ".pni/pni.toml"
MIN_OPT_OUT_REASON_LEN: Final[int] = 10

_CHECK_ID_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    "cwe-94": ("cwe-94", "s307", "ast/code_execution", "code_execution"),
    "s307": ("cwe-94", "s307", "ast/code_execution", "code_execution"),
    "cwe-78": ("cwe-78", "s602", "ast/command_injection", "command_injection"),
    "cwe-502": ("cwe-502", "s301", "s506", "ast/unsafe_deserialization", "unsafe_deserialization"),
    "ds-0026": ("ds-0026", "avd-ds-0026"),
    "avd-ds-0026": ("ds-0026", "avd-ds-0026"),
    "ds-0002": ("ds-0002", "avd-ds-0002"),
    "avd-ds-0002": ("ds-0002", "avd-ds-0002"),
}


class PniProjectConfig(BaseModel):
    """Project identity and optional runtime archetype overrides in .pni/pni.toml."""

    name: Optional[str] = None
    archetypes: Optional[list[RuntimeArchetype]] = None


class PniTargetsConfig(BaseModel):
    """Shared default target directories and exclusion globs in .pni/pni.toml."""

    root: Optional[str] = None
    source: Optional[list[str]] = None
    tests: Optional[list[str]] = None
    docs: Optional[list[str]] = None
    exclude: Optional[list[str]] = None


class PniScanConfig(BaseModel):
    """Filesystem and secret scan scope controls in .pni/pni.toml."""

    respect_gitignore: bool = True
    include_gitignored: list[str] = Field(default_factory=lambda: ["uv.lock"])
    skip_files: list[str] = Field(default_factory=list)
    skip_dirs: list[str] = Field(default_factory=list)


class PniReportConfig(BaseModel):
    """Default Drawlib report scaffolding and compilation settings in .pni/pni.toml."""

    src_dir: Optional[str] = None
    output_dir: Optional[str] = None
    html_output_dir: Optional[str] = None
    formats: Optional[list[str]] = None
    lang: Optional[str] = None
    style: Optional[str] = None


class OptOutEntry(BaseModel):
    """Declarative design waiver ([[opt_out]]) requiring an explicit engineering rationale."""

    id: str
    scope: list[str] = Field(default_factory=list)
    reason: str

    @field_validator("id")
    @classmethod
    def _validate_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            msg = "[[opt_out]] 'id' must not be empty."
            raise ValueError(msg)
        return cleaned

    @field_validator("reason")
    @classmethod
    def _validate_reason(cls, value: str) -> str:
        cleaned = value.strip()
        non_space_len = len("".join(cleaned.split()))
        if non_space_len < MIN_OPT_OUT_REASON_LEN:
            msg = (
                f"[[opt_out]] 'reason' is required and must be at least {MIN_OPT_OUT_REASON_LEN} "
                "non-whitespace characters explaining the design rationale."
            )
            raise ValueError(msg)
        return cleaned


class PniConfig(BaseModel):
    """Complete .pni/pni.toml project configuration manifest."""

    project: PniProjectConfig = Field(default_factory=PniProjectConfig)
    targets: PniTargetsConfig = Field(default_factory=PniTargetsConfig)
    scan: PniScanConfig = Field(default_factory=PniScanConfig)
    report: PniReportConfig = Field(default_factory=PniReportConfig)
    opt_out: list[OptOutEntry] = Field(default_factory=list)


def resolve_pni_toml_path(workspace_root: Path) -> Path:
    """Locate .pni/pni.toml in workspace_root or its nearest ancestor containing .pni/."""
    resolved = workspace_root.resolve()
    direct = resolved / DEFAULT_PNI_TOML_REL_PATH
    if direct.is_file():
        return direct
    for parent in list(resolved.parents)[:4]:
        candidate = parent / DEFAULT_PNI_TOML_REL_PATH
        if candidate.is_file():
            return candidate
    return direct


def load_pni_config(workspace_root: Path) -> PniConfig:
    """Load and validate .pni/pni.toml if present, or return default PniConfig."""
    toml_path = resolve_pni_toml_path(workspace_root)
    if not toml_path.is_file():
        return PniConfig()
    raw = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    return PniConfig.model_validate(raw)


def _default_source_and_tests_for_lang(project_root: Path, lang: str) -> tuple[list[str], list[str]]:
    """Return sensible default source and test directory lists for initial pni.toml scaffolding."""
    if lang == "java":
        src = ["src/main/java"] if (project_root / "src" / "main" / "java").is_dir() else ["src"]
        tst = ["src/test/java"] if (project_root / "src" / "test" / "java").is_dir() else ["tests"]
        return src, tst
    if lang == "php":
        src = [d for d in ("app", "src", "routes", "public") if (project_root / d).is_dir()] or ["src"]
        return src, ["tests"]
    return ["src"], ["tests"]


def render_default_pni_toml(project_root: Path, *, lang: str = "python") -> str:
    """Render a commented starter .pni/pni.toml template tailored to project_root."""
    proj_name = project_root.resolve().name or "project"
    src_dirs, test_dirs = _default_source_and_tests_for_lang(project_root, lang)
    src_literal = ", ".join(f'"{s}"' for s in src_dirs)
    tst_literal = ", ".join(f'"{t}"' for t in test_dirs)
    return (
        "# PNI Project Configuration Manifest (.pni/pni.toml)\n"
        "# Precedence: CLI / Workflow step `with:` > Workflow YAML > .pni/pni.toml > Built-in defaults\n\n"
        "[project]\n"
        f'name = "{proj_name}"\n'
        '# archetypes = ["library", "cli"]\n\n'
        "[targets]\n"
        'root = "."\n'
        f"source = [{src_literal}]\n"
        f"tests = [{tst_literal}]\n"
        'docs = ["README.md"]\n'
        'exclude = ["reports/**", "reports_src/**"]\n\n'
        "[scan]\n"
        "# Exclude untracked files matched by .gitignore (e.g. local developer .env) from filesystem/secret scans\n"
        "respect_gitignore = true\n"
        'include_gitignored = ["uv.lock"]\n'
        'skip_files = [".env", ".env.*", "**/.env"]\n'
        'skip_dirs = ["reports", "reports_src"]\n\n'
        "[report]\n"
        'src_dir = "reports_src"\n'
        'output_dir = "reports"\n'
        '# html_output_dir = "docs/reports/pni-full-audit"\n'
        'formats = ["pdf"]\n'
        'lang = "en"\n'
        'style = "google"\n\n'
        "# Declarative design waivers (each entry requires `id` and `reason` >= 10 non-whitespace chars):\n"
        "# [[opt_out]]\n"
        '# id = "DS-0026"\n'
        '# scope = ["Dockerfile*"]\n'
        '# reason = "Batch CLI container exits upon completion; daemon HEALTHCHECK is not applicable."\n'
    )


def scaffold_pni_config(
    project_root: Path,
    *,
    lang: str = "python",
    force: bool = False,
) -> list[Path]:
    """Create .pni/pni.toml if missing (or overwrite when force=True)."""
    toml_path = project_root / DEFAULT_PNI_TOML_REL_PATH
    if toml_path.exists() and not force:
        return []
    toml_path.parent.mkdir(parents=True, exist_ok=True)
    toml_path.write_text(render_default_pni_toml(project_root, lang=lang), encoding="utf-8")
    return [toml_path]


def normalize_check_id_aliases(raw_id: str) -> set[str]:
    """Expand a check/rule/CWE/Trivy identifier into lowercase canonical aliases."""
    low = raw_id.strip().lower()
    if not low:
        return set()
    aliases = {low}
    if low in _CHECK_ID_ALIASES:
        aliases.update(_CHECK_ID_ALIASES[low])
    if low.startswith("avd-ds-"):
        aliases.add(low.removeprefix("avd-"))
    elif low.startswith("ds-"):
        aliases.add(f"avd-{low}")
    return aliases


def _single_glob_matches_path(norm_path: str, pure_path: PurePosixPath, basename: str, pat: str) -> bool:
    """Return True if a single glob pattern matches norm_path, pure_path, or basename."""
    clean_pat = pat.lstrip("./").replace("\\", "/")
    if clean_pat.endswith("/**"):
        prefix = clean_pat[:-3].rstrip("/")
        if prefix and (norm_path == prefix or norm_path.startswith(f"{prefix}/")):
            return True
    if fnmatch.fnmatchcase(norm_path, clean_pat) or pure_path.match(clean_pat):
        return True
    if "/" not in clean_pat and fnmatch.fnmatchcase(basename, clean_pat):
        return True
    return bool(
        clean_pat.startswith("**/")
        and (fnmatch.fnmatchcase(norm_path, clean_pat[3:]) or fnmatch.fnmatchcase(basename, clean_pat[3:]))
    )


def matches_opt_out_scope(file_path: str | None, scope_globs: Sequence[str]) -> bool:
    """Return True if file_path matches any glob in scope_globs (or if scope_globs is empty)."""
    active_globs = [g.strip() for g in scope_globs if g.strip()]
    if not active_globs:
        return True
    if not file_path or not file_path.strip():
        return False

    norm_path = file_path.strip().lstrip("./").replace("\\", "/")
    pure_path = PurePosixPath(norm_path)
    basename = pure_path.name
    return any(_single_glob_matches_path(norm_path, pure_path, basename, pat) for pat in active_globs)


def match_opt_out(
    opt_outs: Sequence[OptOutEntry],
    check_ids: str | Sequence[str],
    file_path: str | None = None,
) -> OptOutEntry | None:
    """Return the first OptOutEntry matching any of `check_ids` and `file_path` scope."""
    if not opt_outs:
        return None
    raw_list = [check_ids] if isinstance(check_ids, str) else list(check_ids)
    target_aliases: set[str] = set()
    for cid in raw_list:
        target_aliases.update(normalize_check_id_aliases(cid))
    if not target_aliases:
        return None

    for entry in opt_outs:
        entry_aliases = normalize_check_id_aliases(entry.id)
        if (entry_aliases & target_aliases) and matches_opt_out_scope(file_path, entry.scope):
            return entry
    return None


def _is_included_gitignored(rel_posix: str, include_globs: Sequence[str]) -> bool:
    """Return True if rel_posix matches any pattern in `include_gitignored`."""
    return matches_opt_out_scope(rel_posix, include_globs)


def _git_ignored_entries(target_dir: Path) -> list[str]:
    """Query `git status --ignored --porcelain -z` for ignored paths under target_dir."""
    git_bin = shutil.which("git")
    if git_bin is None:
        return []
    entries: list[str] = []
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        proc = subprocess.run(  # noqa: S603
            [git_bin, "-c", "core.quotepath=false", "-C", str(target_dir), "status", "--ignored", "--porcelain", "-z"],
            capture_output=True,
            text=True,
            timeout=5.0,
            check=False,
        )
        if proc.returncode != 0 or not proc.stdout:
            return []
        for token in proc.stdout.split("\0"):
            if token.startswith("!! "):
                rel = token[3:].strip().replace("\\", "/")
                if rel:
                    entries.append(rel)
    return entries


def _parse_gitignore_patterns(target_dir: Path) -> list[str]:
    """Read basic non-comment, non-negated patterns from target_dir/.gitignore."""
    gitignore_file = target_dir / ".gitignore"
    if not gitignore_file.is_file():
        return []
    patterns: list[str] = []
    with contextlib.suppress(OSError):
        for raw_line in gitignore_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith(("#", "!")):
                continue
            patterns.append(line.lstrip("/"))
    return patterns


def _apply_gitignore_patterns(
    resolved_root: Path,
    patterns: Sequence[str],
    include_gitignored: Sequence[str],
    ignored_files: set[str],
    ignored_dirs: set[str],
) -> None:
    """Walk resolved_root and match files/directories against .gitignore patterns."""
    dir_globs = [p.rstrip("/") for p in patterns if p.endswith("/")]
    file_globs = [f"**/{p}" if "/" not in p else p for p in patterns if not p.endswith("/")]
    for candidate in resolved_root.rglob("*"):
        rel_posix = ""
        with contextlib.suppress(ValueError):
            rel_posix = candidate.relative_to(resolved_root).as_posix()
        if not rel_posix or rel_posix == ".git" or rel_posix.startswith(".git/"):
            continue
        if _is_included_gitignored(rel_posix, include_gitignored):
            continue
        if candidate.is_dir():
            if matches_opt_out_scope(rel_posix, dir_globs) or matches_opt_out_scope(rel_posix, file_globs):
                ignored_dirs.add(rel_posix)
        elif candidate.is_file() and (
            matches_exclude_globs(candidate, resolved_root, file_globs)
            or matches_opt_out_scope(rel_posix, patterns)
        ):
            ignored_files.add(rel_posix)


def discover_gitignored_paths(
    target_dir: Path,
    *,
    include_gitignored: Sequence[str] = ("uv.lock",),
) -> tuple[list[str], list[str]]:
    """Return (ignored_files, ignored_dirs) relative to target_dir excluding `include_gitignored`.

    Args:
        target_dir: Target directory being scanned.
        include_gitignored: Relative paths or globs that should remain scannable even if gitignored.

    Returns:
        tuple[list[str], list[str]]: Sorted relative file paths and relative directory paths to skip.
    """
    resolved_root = target_dir.resolve()
    if not resolved_root.is_dir():
        return [], []

    ignored_files: set[str] = set()
    ignored_dirs: set[str] = set()

    for rel in _git_ignored_entries(resolved_root):
        clean_rel = rel.rstrip("/")
        if not clean_rel or _is_included_gitignored(clean_rel, include_gitignored):
            continue
        candidate = resolved_root / clean_rel
        if rel.endswith("/") or candidate.is_dir():
            ignored_dirs.add(clean_rel)
        elif candidate.is_file():
            ignored_files.add(clean_rel)

    patterns = _parse_gitignore_patterns(resolved_root)
    if patterns:
        _apply_gitignore_patterns(resolved_root, patterns, include_gitignored, ignored_files, ignored_dirs)

    return sorted(ignored_files), sorted(ignored_dirs)
