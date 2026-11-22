# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""GitHub Releases and Actions REST API client for PNI grammar release assets."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Final

from pni._languages._grammar_assets import (
    DEFAULT_GRAMMAR_REPO_NAME,
    DEFAULT_GRAMMAR_REPO_OWNER,
)
from tools.pcli.common import PROJECT_ROOT

DEFAULT_HTTP_TIMEOUT: Final[float] = 30.0
WORKFLOW_FILENAME: Final[str] = "build-grammar-assets.yml"
_PINNED_BEGIN: Final[str] = "# BEGIN PINNED_GRAMMAR_ASSETS"
_PINNED_END: Final[str] = "# END PINNED_GRAMMAR_ASSETS"


def resolve_github_token(explicit_token: str | None = None) -> str | None:
    """Resolve GitHub token from flag, environment, workspace .env, or git credential helper."""
    if explicit_token:
        return explicit_token

    for env_key in ("GITHUB_TOKEN", "GH_TOKEN"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val

    env_file = PROJECT_ROOT / ".env"
    if env_file.is_file():
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            if key.strip() in {"GITHUB_TOKEN", "GH_TOKEN"}:
                cleaned = val.strip().strip("\"'")
                if cleaned:
                    return cleaned

    return _resolve_token_from_git()


def _resolve_token_from_git() -> str | None:
    """Retrieve GitHub token from system git credential helper if configured."""
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception:
        return None
    return None


class GitHubGrammarAssetsClient:
    """Minimal GitHub REST API client for inspecting grammar Releases and Actions runs."""

    def __init__(
        self,
        owner: str = DEFAULT_GRAMMAR_REPO_OWNER,
        repo: str = DEFAULT_GRAMMAR_REPO_NAME,
        token: str | None = None,
        timeout: float = DEFAULT_HTTP_TIMEOUT,
    ) -> None:
        """Initialize client for owner/repo."""
        self.owner = owner
        self.repo = repo
        self.token = token
        self.timeout = timeout
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"

    def _headers(
        self,
        content_type: str | None = None,
        accept: str = "application/vnd.github+json",
    ) -> dict[str, str]:
        """Build standard GitHub REST API headers."""
        headers = {
            "Accept": accept,
            "User-Agent": "pni501-pcli",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def get_release_by_tag(self, tag: str) -> dict[str, Any] | None:
        """Fetch GitHub Release JSON by tag name, returning None on 404."""
        url = f"{self.api_base}/releases/tags/{urllib.parse.quote(tag, safe='')}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
                return data
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise

    def fetch_remote_manifest(self, tag: str) -> dict[str, Any]:
        """Download and parse manifest.json from the GitHub Release for tag."""
        url = f"https://github.com/{self.owner}/{self.repo}/releases/download/{tag}/manifest.json"
        req = urllib.request.Request(url, headers={"User-Agent": "pni501-pcli"}, method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
            return data

    def list_workflow_runs(self, per_page: int = 10) -> list[dict[str, Any]]:
        """List recent GitHub Actions runs for build-grammar-assets.yml."""
        query = urllib.parse.urlencode({"per_page": per_page})
        url = f"{self.api_base}/actions/workflows/{WORKFLOW_FILENAME}/runs?{query}"
        req = urllib.request.Request(url, headers=self._headers(), method="GET")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            payload: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
            runs = payload.get("workflow_runs", [])
            return runs if isinstance(runs, list) else []

    def trigger_workflow(self, release_tag: str, *, ref: str = "main", publish_release: bool = True) -> None:
        """Dispatch build-grammar-assets.yml on GitHub Actions."""
        if not self.token:
            msg = "GitHub token required to dispatch workflow. Set GITHUB_TOKEN or pass --token."
            raise RuntimeError(msg)
        url = f"{self.api_base}/actions/workflows/{WORKFLOW_FILENAME}/dispatches"
        payload = {
            "ref": ref,
            "inputs": {
                "release_tag": release_tag,
                "publish_release": "true" if publish_release else "false",
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(content_type="application/json"),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout):
            return


def render_pinned_assets_block(manifest: dict[str, Any]) -> str:
    """Render the PINNED_GRAMMAR_ASSETS Python dictionary block from manifest.json."""
    raw_assets = manifest.get("assets", [])
    if not isinstance(raw_assets, list):
        msg = "Invalid manifest.json: 'assets' must be a list."
        raise ValueError(msg)

    lines: list[str] = [
        _PINNED_BEGIN,
        "PINNED_GRAMMAR_ASSETS: Final[dict[tuple[str, str], GrammarReleaseAsset]] = {",
    ]
    for item in sorted(raw_assets, key=lambda x: (str(x["asset_id"]), str(x["platform"]))):
        lines.append(f'    ("{item["asset_id"]}", "{item["platform"]}"): GrammarReleaseAsset(')
        lines.append(f'        asset_id="{item["asset_id"]}",')
        lines.append(f'        grammar_id="{item["grammar_id"]}",')
        lines.append(f'        platform_tag="{item["platform"]}",')
        lines.append(f'        archive_name="{item["archive_name"]}",')
        lines.append(f'        binary_filename="{item["binary_filename"]}",')
        lines.append(f'        sha256="{item["sha256"]}",')
        lines.append(f'        size={int(item["size"])},')
        lines.append("    ),")
    lines.append("}")
    lines.append(_PINNED_END)
    return "\n".join(lines)


def sync_manifest_into_source(
    manifest: dict[str, Any],
    target_py: Path,
    *,
    check_only: bool = False,
) -> bool:
    """Sync manifest.json into src/pni/_languages/_grammar_assets.py; returns True if already in sync."""
    original = target_py.read_text(encoding="utf-8")
    start_idx = original.find(_PINNED_BEGIN)
    end_idx = original.find(_PINNED_END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        msg = f"Expected sync markers '{_PINNED_BEGIN}' / '{_PINNED_END}' in {target_py}"
        raise RuntimeError(msg)
    end_idx += len(_PINNED_END)

    updated = original[:start_idx] + render_pinned_assets_block(manifest) + original[end_idx:]
    release_tag = str(manifest.get("release_tag", "")).strip()
    if release_tag:
        updated = re.sub(
            r'DEFAULT_GRAMMAR_RELEASE_TAG:\s*Final\[str\]\s*=\s*"[^"]*"',
            f'DEFAULT_GRAMMAR_RELEASE_TAG: Final[str] = "{release_tag}"',
            updated,
            count=1,
        )

    if check_only:
        return updated == original
    target_py.write_text(updated, encoding="utf-8")
    return True
