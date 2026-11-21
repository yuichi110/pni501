"""Reproducibly fetch pinned MIT Tree-sitter grammar C sources for pni501-extra-grammars."""

from __future__ import annotations

import io
import shutil
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UpstreamGrammar:
    """Pinned upstream MIT Tree-sitter grammar repository descriptor."""

    lang_id: str
    repo: str
    rev: str
    license_name: str = "MIT"


UPSTREAM_GRAMMARS: tuple[UpstreamGrammar, ...] = (
    UpstreamGrammar("cobol", "nolanlwin/tree-sitter-cobol", "6f1a60ad52b52ccb5e794985454c6743531f17d7"),
    UpstreamGrammar("r", "r-lib/tree-sitter-r", "58a22794466c0fc15b0d3b40531db751593721e8"),
    UpstreamGrammar("vue", "tree-sitter-grammars/tree-sitter-vue", "ce8011a414fdf8091f4e4071752efc376f4afb08"),
    UpstreamGrammar("proto", "coder3101/tree-sitter-proto", "18366491f37d43d6d5d02cbb1e79b650b5728145"),
    UpstreamGrammar("dockerfile", "TheAuditorTool/tree-sitter-dockerfile", "33df056e1e6652b1f3e9b7636f40da0d3b1b0949"),
)

PKG_ROOT = Path(__file__).resolve().parent.parent
VENDOR_DIR = PKG_ROOT / "vendor"
LICENSES_OUT = PKG_ROOT / "pni501_extra_grammars" / "THIRD_PARTY_LICENSES.txt"


def _is_wanted_member(rel_path: str) -> bool:
    """Return True if archive relative path belongs to C sources/headers or LICENSE."""
    lower = rel_path.lower()
    if lower in {"license", "license.txt", "license.md"}:
        return True
    if rel_path.startswith("src/"):
        return lower.endswith((".c", ".cc", ".cpp", ".h", ".hpp"))
    return False


def fetch_grammar(item: UpstreamGrammar, *, force: bool = False) -> Path:
    """Download and extract pinned C grammar sources for one upstream language."""
    dest = VENDOR_DIR / item.lang_id
    parser_c = dest / "src" / "parser.c"
    if parser_c.is_file() and not force:
        return dest

    url = f"https://github.com/{item.repo}/archive/{item.rev}.tar.gz"
    req = urllib.request.Request(url, headers={"User-Agent": "pni501-extra-grammars-fetch/0.1"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        archive_bytes = resp.read()

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    dest_resolved = dest.resolve()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            parts = Path(member.name).parts
            if len(parts) < 2:
                continue
            rel = Path(*parts[1:]).as_posix()
            if not _is_wanted_member(rel):
                continue
            out_path = (dest / rel).resolve()
            if not out_path.is_relative_to(dest_resolved):
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            extracted = tf.extractfile(member)
            if extracted is not None:
                out_path.write_bytes(extracted.read())

    if not parser_c.is_file():
        msg = f"Failed to locate src/parser.c for {item.lang_id} from {url}"
        raise RuntimeError(msg)
    return dest


def write_third_party_licenses() -> None:
    """Assemble combined THIRD_PARTY_LICENSES.txt from vendored MIT LICENSE files."""
    sections: list[str] = [
        "Third-Party Tree-sitter Grammar Licenses (pni501-extra-grammars)\n",
        "=" * 68 + "\n",
    ]
    for item in UPSTREAM_GRAMMARS:
        dest = VENDOR_DIR / item.lang_id
        lic_file = next(
            (p for name in ("LICENSE", "LICENSE.txt", "LICENSE.md") if (p := dest / name).is_file()),
            None,
        )
        sections.append(f"\n--- {item.lang_id} ({item.repo} @ {item.rev}, {item.license_name}) ---\n")
        if lic_file is not None:
            sections.append(lic_file.read_text(encoding="utf-8", errors="replace").strip() + "\n")
        else:
            sections.append(f"Licensed under {item.license_name}.\n")
    LICENSES_OUT.parent.mkdir(parents=True, exist_ok=True)
    LICENSES_OUT.write_text("".join(sections), encoding="utf-8")


def fetch_all(*, force: bool = False) -> None:
    """Ensure all 5 upstream MIT grammars are fetched into vendor/."""
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    for item in UPSTREAM_GRAMMARS:
        dest = fetch_grammar(item, force=force)
        src_files = sorted(p.name for p in (dest / "src").iterdir() if p.is_file())
        print(f"  ready {item.lang_id:12s} ({item.repo}@{item.rev[:8]}): {src_files}")
    write_third_party_licenses()


if __name__ == "__main__":
    fetch_all()
