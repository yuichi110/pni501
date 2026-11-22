# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Unit tests for on-demand GitHub Releases Tree-sitter grammar downloader and cache."""

from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from pni._languages import _grammar_assets as ga
from pni.cli import app

runner = CliRunner()


def _make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_detect_platform_tag_matrix() -> None:
    assert ga.detect_platform_tag(sys_platform="linux", machine="x86_64") == "linux_x86_64"
    assert ga.detect_platform_tag(sys_platform="linux", machine="aarch64") == "linux_aarch64"
    assert ga.detect_platform_tag(sys_platform="darwin", machine="arm64") == "macos_arm64"
    assert ga.detect_platform_tag(sys_platform="darwin", machine="x86_64") == "macos_x86_64"
    assert ga.detect_platform_tag(sys_platform="win32", machine="AMD64") == "windows_amd64"
    with pytest.raises(RuntimeError, match="Unsupported platform"):
        ga.detect_platform_tag(sys_platform="freebsd14", machine="riscv64")


def test_normalize_asset_id_aliases() -> None:
    assert ga.normalize_asset_id("protobuf") == "proto"
    assert ga.normalize_asset_id("proto") == "proto"
    assert ga.normalize_asset_id("docker") == "dockerfile"
    assert ga.normalize_asset_id("cbl") == "cobol"
    assert ga.normalize_asset_id("rlang") == "r"
    assert ga.normalize_asset_id("vuejs") == "vue"
    with pytest.raises(ValueError, match="Unknown extra Tree-sitter grammar"):
        ga.normalize_asset_id("python")


def test_ensure_grammar_binary_downloads_verifies_and_caches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = b"\x7fELF-mock-abi3-binary"
    archive_bytes = _make_zip(
        {
            "_dockerfile.abi3.so": payload,
            "THIRD_PARTY_LICENSES.txt": b"MIT License\n",
        }
    )
    digest = hashlib.sha256(archive_bytes).hexdigest()
    asset = ga.GrammarReleaseAsset(
        asset_id="dockerfile",
        grammar_id="dockerfile",
        platform_tag="linux_x86_64",
        archive_name="pni_grammar_dockerfile_linux_x86_64.zip",
        binary_filename="_dockerfile.abi3.so",
        sha256=digest,
        size=len(archive_bytes),
    )

    monkeypatch.setitem(ga.PINNED_GRAMMAR_ASSETS, ("dockerfile", "linux_x86_64"), asset)
    calls: list[str] = []

    def fake_get(url: str, *, timeout: int = 120) -> bytes:
        _ = timeout
        calls.append(url)
        return archive_bytes

    monkeypatch.setattr(ga, "_http_get_bytes", fake_get)

    path1 = ga.ensure_grammar_binary(
        "dockerfile",
        platform_tag="linux_x86_64",
        release_tag=ga.DEFAULT_GRAMMAR_RELEASE_TAG,
        cache_dir=tmp_path,
    )
    assert path1.is_file()
    assert path1.read_bytes() == payload
    assert (path1.parent / "THIRD_PARTY_LICENSES.txt").is_file()
    assert len(calls) == 1

    # Second call hits cache with zero network requests
    path2 = ga.ensure_grammar_binary(
        "dockerfile",
        platform_tag="linux_x86_64",
        release_tag=ga.DEFAULT_GRAMMAR_RELEASE_TAG,
        cache_dir=tmp_path,
    )
    assert path2 == path1
    assert len(calls) == 1


def test_ensure_grammar_binary_rejects_sha256_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    archive_bytes = _make_zip({"_vue.abi3.so": b"tampered"})
    asset = ga.GrammarReleaseAsset(
        asset_id="vue",
        grammar_id="vue",
        platform_tag="linux_x86_64",
        archive_name="pni_grammar_vue_linux_x86_64.zip",
        binary_filename="_vue.abi3.so",
        sha256="0" * 64,
        size=len(archive_bytes),
    )
    monkeypatch.setitem(ga.PINNED_GRAMMAR_ASSETS, ("vue", "linux_x86_64"), asset)
    monkeypatch.setattr(ga, "_http_get_bytes", lambda url, *, timeout=120: archive_bytes)

    with pytest.raises(RuntimeError, match="SHA-256 checksum mismatch"):
        ga.ensure_grammar_binary(
            "vue",
            platform_tag="linux_x86_64",
            release_tag=ga.DEFAULT_GRAMMAR_RELEASE_TAG,
            cache_dir=tmp_path,
        )


def test_extract_archive_blocks_zip_slip(tmp_path: Path) -> None:
    evil_zip = _make_zip({"../../escape.so": b"evil"})
    with pytest.raises(ValueError, match="Unsafe archive member path"):
        ga._extract_archive_atomically(evil_zip, tmp_path / "dest", "evil.zip")


def test_cli_grammars_status_and_clear(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PNI_GRAMMAR_CACHE_DIR", str(tmp_path))
    status_res = runner.invoke(app, ["grammars", "status"])
    assert status_res.exit_code == 0
    assert "dockerfile" in status_res.stdout
    assert "cobol" in status_res.stdout

    # Populate dummy folder and verify clear removes it
    dummy = tmp_path / ga.DEFAULT_GRAMMAR_RELEASE_TAG / "linux_x86_64" / "dockerfile"
    dummy.mkdir(parents=True)
    (dummy / "_dockerfile.abi3.so").write_bytes(b"dummy")

    clear_res = runner.invoke(app, ["grammars", "clear"])
    assert clear_res.exit_code == 0
    assert not (tmp_path / ga.DEFAULT_GRAMMAR_RELEASE_TAG).exists()
