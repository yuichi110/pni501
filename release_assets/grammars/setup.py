"""Setuptools build script compiling 5 independent ABI3 Tree-sitter extensions."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_ext import build_ext

ROOT = Path(__file__).resolve().parent
VENDOR_DIR = ROOT / "vendor"
LANGUAGES = ("cobol", "r", "vue", "proto", "dockerfile")


def _ensure_vendored_sources() -> None:
    """Fetch pinned grammar sources if vendor/ is missing."""
    missing = [lang for lang in LANGUAGES if not (VENDOR_DIR / lang / "src" / "parser.c").is_file()]
    if not missing:
        return
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import fetch_grammars

        fetch_grammars.fetch_all()
    finally:
        sys.path.pop(0)


class _Abi3BdistWheel(bdist_wheel):
    """Tag built wheels as Python 3.10+ abi3 limited-API binaries."""

    def get_tag(self) -> tuple[str, str, str]:
        python_tag, abi_tag, plat_tag = super().get_tag()
        if python_tag.startswith("cp"):
            return "cp310", "abi3", plat_tag
        return python_tag, abi_tag, plat_tag


class _GrammarBuildExt(build_ext):
    """Apply platform-specific C11 / C++14 optimization flags per source file."""

    def build_extension(self, ext: Extension) -> None:
        is_msvc = self.compiler.compiler_type == "msvc"
        orig_compile = self.compiler._compile if hasattr(self.compiler, "_compile") else None

        if is_msvc:
            ext.extra_compile_args = ["/O2", "/utf-8", "/wd4244", "/wd4267", "/wd4018"]
        else:
            ext.extra_compile_args = ["-O2", "-fvisibility=hidden", "-Wno-unused-value", "-Wno-unused-but-set-variable"]
            # Apply -std=c11 only to C files when mixed with C++ scanner files
            has_cpp = any(src.endswith((".cc", ".cpp")) for src in ext.sources)
            if not has_cpp:
                ext.extra_compile_args.append("-std=c11")
            elif orig_compile is not None:
                def _mixed_compile(obj, src, ext_name, cc_args, extra_postargs, pp_opts):
                    per_file = list(extra_postargs or [])
                    if src.endswith((".cc", ".cpp")):
                        per_file.append("-std=c++14")
                    else:
                        per_file.append("-std=c11")
                    return orig_compile(obj, src, ext_name, cc_args, per_file, pp_opts)

                self.compiler._compile = _mixed_compile  # type: ignore[method-assign]

        try:
            super().build_extension(ext)
        finally:
            if orig_compile is not None:
                self.compiler._compile = orig_compile  # type: ignore[method-assign]


def _build_extensions() -> list[Extension]:
    """Construct one independent abi3 Extension per bundled grammar."""
    _ensure_vendored_sources()
    extensions: list[Extension] = []
    for lang in LANGUAGES:
        src_dir = VENDOR_DIR / lang / "src"
        sources = [
            f"csrc/mod_{lang}.c",
            f"vendor/{lang}/src/parser.c",
        ]
        language_mode = "c"
        for scanner_name in ("scanner.c", "scanner.cc", "scanner.cpp"):
            scanner_path = src_dir / scanner_name
            if scanner_path.is_file():
                sources.append(f"vendor/{lang}/src/{scanner_name}")
                if scanner_name.endswith((".cc", ".cpp")):
                    language_mode = "c++"
                break

        extensions.append(
            Extension(
                name=f"pni501_extra_grammars._{lang}",
                sources=sources,
                include_dirs=["csrc", f"vendor/{lang}/src"],
                define_macros=[("PY_SSIZE_T_CLEAN", None), ("TREE_SITTER_HIDE_SYMBOLS", None)],
                py_limited_api=True,
                language=language_mode,
            )
        )
    return extensions


setup(
    ext_modules=_build_extensions(),
    cmdclass={"build_ext": _GrammarBuildExt, "bdist_wheel": _Abi3BdistWheel},
    options={"bdist_wheel": {"py_limited_api": "cp310"}},
)
