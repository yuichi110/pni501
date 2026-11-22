# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Package cibuildwheel ABI3 wheels into per-language, per-platform GitHub Release ZIPs."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fetch_grammars import UPSTREAM_GRAMMARS  # noqa: E402

ASSET_TO_GRAMMAR_ID: dict[str, str] = {
    "cobol": "cobol",
    "r": "r",
    "vue": "vue",
    "proto": "protobuf",
    "dockerfile": "dockerfile",
}

EXPECTED_PLATFORMS: tuple[str, ...] = (
    "linux_x86_64",
    "linux_aarch64",
    "macos_arm64",
    "macos_x86_64",
    "windows_amd64",
)

DETERMINISTIC_ZIP_DATE: tuple[int, int, int, int, int, int] = (2026, 1, 1, 0, 0, 0)

_PINNED_BEGIN = "# BEGIN PINNED_GRAMMAR_ASSETS"
_PINNED_END = "# END PINNED_GRAMMAR_ASSETS"


def classify_wheel_platform(wheel_name: str) -> str:
    """Map a wheel filename to one of the five canonical PNI platform tags."""
    lower = wheel_name.lower()
    if not lower.endswith(".whl"):
        msg = f"Not a wheel file: {wheel_name}"
        raise ValueError(msg)
    if re.search(r"(manylinux[^.]*_x86_64|linux_x86_64)\.whl$", lower):
        return "linux_x86_64"
    if re.search(r"(manylinux[^.]*_aarch64|linux_aarch64)\.whl$", lower):
        return "linux_aarch64"
    if re.search(r"macosx_[^.]*_arm64\.whl$", lower):
        return "macos_arm64"
    if re.search(r"macosx_[^.]*_x86_64\.whl$", lower):
        return "macos_x86_64"
    if re.search(r"win_amd64\.whl$", lower):
        return "windows_amd64"
    msg = f"Unrecognized wheel platform tag in '{wheel_name}'"
    raise ValueError(msg)


def _create_deterministic_zip(entries: dict[str, bytes]) -> bytes:
    """Create a reproducible ZIP archive with fixed timestamps and permissions."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for arcname in sorted(entries):
            info = zipfile.ZipInfo(filename=arcname, date_time=DETERMINISTIC_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            # Preserve executable permission bit on Unix shared libraries
            mode = 0o755 if arcname.endswith((".so", ".dylib", ".pyd")) else 0o644
            info.external_attr = (mode & 0xFFFF) << 16
            zf.writestr(info, entries[arcname])
    return buf.getvalue()


def _find_extension_in_wheel(zf: zipfile.ZipFile, asset_id: str) -> tuple[str, bytes]:
    """Locate and read the compiled ABI3 binary for asset_id inside a wheel."""
    prefix = f"pni501_extra_grammars/_{asset_id}."
    candidates = [
        name for name in zf.namelist() if name.startswith(prefix) and name.endswith((".so", ".pyd", ".dylib"))
    ]
    if len(candidates) != 1:
        msg = f"Expected exactly 1 compiled binary for '{asset_id}' in wheel, found: {candidates}"
        raise RuntimeError(msg)
    member_name = candidates[0]
    binary_filename = Path(member_name).name
    return binary_filename, zf.read(member_name)


def package_wheelhouse(
    wheelhouse_dir: Path,
    output_dir: Path,
    release_tag: str,
    *,
    require_all_platforms: bool = False,
) -> dict[str, object]:
    """Unpack wheels in wheelhouse_dir into deterministic per-language-per-platform ZIPs."""
    wheels = sorted(wheelhouse_dir.rglob("*.whl"))
    if not wheels:
        msg = f"No .whl files found under {wheelhouse_dir}"
        raise RuntimeError(msg)

    by_platform: dict[str, Path] = {}
    for whl in wheels:
        plat = classify_wheel_platform(whl.name)
        if plat in by_platform:
            msg = f"Duplicate wheel for platform '{plat}': {by_platform[plat]} and {whl}"
            raise RuntimeError(msg)
        by_platform[plat] = whl

    if require_all_platforms:
        missing = [p for p in EXPECTED_PLATFORMS if p not in by_platform]
        if missing:
            msg = f"Missing expected platform wheel(s): {missing} (found: {sorted(by_platform)})"
            raise RuntimeError(msg)

    upstream_map = {item.lang_id: item for item in UPSTREAM_GRAMMARS}
    output_dir.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, object]] = []
    sha_lines: list[str] = []

    for plat in sorted(by_platform):
        whl_path = by_platform[plat]
        with zipfile.ZipFile(whl_path, "r") as zf:
            license_member = "pni501_extra_grammars/THIRD_PARTY_LICENSES.txt"
            if license_member not in zf.namelist():
                msg = f"Missing {license_member} in {whl_path}"
                raise RuntimeError(msg)
            license_bytes = zf.read(license_member)

            for asset_id in sorted(ASSET_TO_GRAMMAR_ID):
                binary_filename, binary_bytes = _find_extension_in_wheel(zf, asset_id)
                archive_name = f"pni_grammar_{asset_id}_{plat}.zip"
                zip_bytes = _create_deterministic_zip(
                    {
                        binary_filename: binary_bytes,
                        "THIRD_PARTY_LICENSES.txt": license_bytes,
                    }
                )
                out_zip = output_dir / archive_name
                out_zip.write_bytes(zip_bytes)

                digest = hashlib.sha256(zip_bytes).hexdigest()
                upstream = upstream_map[asset_id]
                assets.append(
                    {
                        "asset_id": asset_id,
                        "grammar_id": ASSET_TO_GRAMMAR_ID[asset_id],
                        "platform": plat,
                        "archive_name": archive_name,
                        "binary_filename": binary_filename,
                        "sha256": digest,
                        "size": len(zip_bytes),
                        "upstream_repo": upstream.repo,
                        "upstream_rev": upstream.rev,
                        "license": upstream.license_name,
                    }
                )
                sha_lines.append(f"{digest}  {archive_name}\n")

    assets.sort(key=lambda item: (str(item["asset_id"]), str(item["platform"])))
    manifest: dict[str, object] = {
        "schema_version": 1,
        "release_tag": release_tag,
        "abi": "cp310-abi3",
        "platforms": sorted(by_platform),
        "assets": assets,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (output_dir / "SHA256SUMS.txt").write_text("".join(sorted(sha_lines)), encoding="utf-8")
    return manifest


def render_pinned_python_block(manifest: dict[str, object]) -> str:
    """Render the PINNED_GRAMMAR_ASSETS Python dictionary block from a manifest dict."""
    raw_assets = manifest.get("assets", [])
    if not isinstance(raw_assets, list):
        msg = "Invalid manifest: 'assets' must be a list"
        raise ValueError(msg)

    lines: list[str] = [
        _PINNED_BEGIN,
        "PINNED_GRAMMAR_ASSETS: Final[dict[tuple[str, str], GrammarReleaseAsset]] = {",
    ]
    for item in sorted(raw_assets, key=lambda x: (str(x["asset_id"]), str(x["platform"]))):
        asset_id = str(item["asset_id"])
        grammar_id = str(item["grammar_id"])
        plat = str(item["platform"])
        archive_name = str(item["archive_name"])
        binary_filename = str(item["binary_filename"])
        sha256 = str(item["sha256"])
        size = int(item["size"])
        lines.append(f'    ("{asset_id}", "{plat}"): GrammarReleaseAsset(')
        lines.append(f'        asset_id="{asset_id}",')
        lines.append(f'        grammar_id="{grammar_id}",')
        lines.append(f'        platform_tag="{plat}",')
        lines.append(f'        archive_name="{archive_name}",')
        lines.append(f'        binary_filename="{binary_filename}",')
        lines.append(f'        sha256="{sha256}",')
        lines.append(f"        size={size},")
        lines.append("    ),")
    lines.append("}")
    lines.append(_PINNED_END)
    return "\n".join(lines)


def sync_manifest_to_python(manifest: dict[str, object], target_py: Path) -> None:
    """Inject the pinned manifest block and DEFAULT_GRAMMAR_RELEASE_TAG into _grammar_assets.py."""
    content = target_py.read_text(encoding="utf-8")
    start_idx = content.find(_PINNED_BEGIN)
    end_idx = content.find(_PINNED_END)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        msg = f"Markers '{_PINNED_BEGIN}' / '{_PINNED_END}' not found in {target_py}"
        raise RuntimeError(msg)
    end_idx += len(_PINNED_END)

    release_tag = str(manifest.get("release_tag", "")).strip()
    new_block = render_pinned_python_block(manifest)
    updated = content[:start_idx] + new_block + content[end_idx:]
    if release_tag:
        updated = re.sub(
            r'DEFAULT_GRAMMAR_RELEASE_TAG:\s*Final\[str\]\s*=\s*"[^"]*"',
            f'DEFAULT_GRAMMAR_RELEASE_TAG: Final[str] = "{release_tag}"',
            updated,
            count=1,
        )
    target_py.write_text(updated, encoding="utf-8")


def main() -> None:
    """CLI entrypoint for packaging wheels or syncing a published manifest."""
    parser = argparse.ArgumentParser(description="Package or sync PNI extra Tree-sitter grammar release assets.")
    parser.add_argument("--wheelhouse", type=Path, help="Directory containing cibuildwheel .whl outputs.")
    parser.add_argument("--output-dir", type=Path, help="Destination directory for ZIP archives and manifest.json.")
    parser.add_argument("--tag", type=str, default="grammars-v0.2.0", help="GitHub Release tag name.")
    parser.add_argument(
        "--require-all-platforms",
        action="store_true",
        help="Fail unless all 5 target platforms are present in --wheelhouse.",
    )
    parser.add_argument("--sync-manifest", type=Path, help="Local manifest.json path to sync into Python SoT.")
    parser.add_argument("--sync-manifest-url", type=str, help="Remote manifest.json URL to sync into Python SoT.")
    parser.add_argument(
        "--target-py",
        type=Path,
        default=Path("src/pni/_languages/_grammar_assets.py"),
        help="Python SoT file to update when syncing manifest.",
    )
    args = parser.parse_args()

    if args.sync_manifest is not None:
        manifest = json.loads(args.sync_manifest.read_text(encoding="utf-8"))
        sync_manifest_to_python(manifest, args.target_py)
        print(f"Synced {len(manifest.get('assets', []))} pinned assets from {args.sync_manifest} -> {args.target_py}")
        return

    if args.sync_manifest_url:
        req = urllib.request.Request(args.sync_manifest_url, headers={"User-Agent": "pni501-grammar-sync"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            manifest = json.loads(resp.read().decode("utf-8"))
        sync_manifest_to_python(manifest, args.target_py)
        print(f"Synced {len(manifest.get('assets', []))} pinned assets from {args.sync_manifest_url} -> {args.target_py}")
        return

    if args.wheelhouse is None or args.output_dir is None:
        parser.error("Provide --wheelhouse and --output-dir (or --sync-manifest / --sync-manifest-url).")

    manifest = package_wheelhouse(
        args.wheelhouse,
        args.output_dir,
        args.tag,
        require_all_platforms=args.require_all_platforms,
    )
    assets_list = manifest["assets"]
    assert isinstance(assets_list, list)
    print(f"Packaged {len(assets_list)} grammar archives into {args.output_dir} (tag={args.tag})")


if __name__ == "__main__":
    main()
