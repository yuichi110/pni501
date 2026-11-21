# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Manifest parsers and tooling checks for extended Tier A, Tier B, and Tier C languages."""

from __future__ import annotations

import contextlib
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from pni._languages import get_language_spec

_CSPROJ_TARGET_FW_RE = re.compile(r"<TargetFrameworks?>\s*([^<]+?)\s*</TargetFrameworks?>", re.IGNORECASE)
_CSPROJ_VERSION_RE = re.compile(r"<Version>\s*([^<]+?)\s*</Version>", re.IGNORECASE)
_CSPROJ_PKGREF_RE = re.compile(r"<PackageReference\b([^>]+)>", re.IGNORECASE)
_CSPROJ_ATTR_RE = re.compile(r"""(\w+)\s*=\s*["']([^"']+)["']""")


@dataclass
class ExtendedManifestData:
    """Normalized manifest metadata extracted for any non-core PNI language."""

    project_name: str
    version: str = "0.0.0"
    build_system: str = "unknown"
    language_version_constraint: Optional[str] = None
    manifest_files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    unpinned_dependencies: list[str] = field(default_factory=list)
    dev_dependencies: list[str] = field(default_factory=list)


def _inspect_rust(project_root: Path) -> ExtendedManifestData:
    """Parse Cargo.toml metadata, edition/MSRV, and dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    cargo = project_root / "Cargo.toml"
    if not cargo.is_file():
        return info
    info.manifest_files.append("Cargo.toml")
    info.build_system = "cargo"
    with contextlib.suppress(Exception):
        data = tomllib.loads(cargo.read_text(encoding="utf-8"))
        pkg = data.get("package")
        if isinstance(pkg, dict):
            if isinstance(pkg.get("name"), str):
                info.project_name = pkg["name"]
            if isinstance(pkg.get("version"), str):
                info.version = pkg["version"]
            msrv = pkg.get("rust-version") or pkg.get("edition")
            if isinstance(msrv, str):
                info.language_version_constraint = msrv
        deps = data.get("dependencies")
        if isinstance(deps, dict):
            for name, spec in deps.items():
                info.dependencies.append(name)
                if isinstance(spec, str) and spec.strip() in {"*", ""}:
                    info.unpinned_dependencies.append(name)
        dev_deps = data.get("dev-dependencies")
        if isinstance(dev_deps, dict):
            info.dev_dependencies.extend(dev_deps.keys())
    return info


def _parse_single_csproj(csproj: Path, project_root: Path, info: ExtendedManifestData) -> None:
    """Extract TargetFramework, Version, and PackageReference entries from one .csproj file safely."""
    text = csproj.read_text(encoding="utf-8", errors="ignore")
    if info.project_name == project_root.name:
        info.project_name = csproj.stem
    if not info.language_version_constraint:
        tf_m = _CSPROJ_TARGET_FW_RE.search(text)
        if tf_m:
            info.language_version_constraint = tf_m.group(1).strip()
    if info.version == "0.0.0":
        ver_m = _CSPROJ_VERSION_RE.search(text)
        if ver_m:
            info.version = ver_m.group(1).strip()
    for tag_m in _CSPROJ_PKGREF_RE.finditer(text):
        attrs = {k.lower(): v for k, v in _CSPROJ_ATTR_RE.findall(tag_m.group(1))}
        inc = attrs.get("include")
        if inc and inc not in info.dependencies:
            info.dependencies.append(inc)
            if "*" in attrs.get("version", ""):
                info.unpinned_dependencies.append(inc)


def _inspect_csharp(project_root: Path) -> ExtendedManifestData:
    """Parse .csproj / Directory.Packages.props metadata and NuGet PackageReferences."""
    info = ExtendedManifestData(project_name=project_root.name)
    csproj_files = sorted(project_root.glob("*.csproj")) + sorted(project_root.glob("src/*/*.csproj"))
    if csproj_files:
        info.build_system = "dotnet"
    for csproj in csproj_files[:5]:
        info.manifest_files.append(csproj.relative_to(project_root).as_posix())
        with contextlib.suppress(Exception):
            _parse_single_csproj(csproj, project_root, info)
    for extra in ("Directory.Packages.props", "Directory.Build.props", "global.json"):
        if (project_root / extra).is_file():
            info.manifest_files.append(extra)
            if info.build_system == "unknown":
                info.build_system = "dotnet"
    return info


def _inspect_ruby(project_root: Path) -> ExtendedManifestData:
    """Parse Gemfile and *.gemspec metadata and gem dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    gemfile = project_root / "Gemfile"
    if gemfile.is_file():
        info.manifest_files.append("Gemfile")
        info.build_system = "bundler"
        text = gemfile.read_text(encoding="utf-8", errors="ignore")
        ruby_m = re.search(r"""ruby\s+['"]([^'"]+)['"]""", text)
        if ruby_m:
            info.language_version_constraint = ruby_m.group(1)
        for m in re.finditer(r"""^\s*gem\s+['"]([^'"]+)['"](.*)""", text, re.MULTILINE):
            gem_name = m.group(1)
            if gem_name not in info.dependencies:
                info.dependencies.append(gem_name)
                if not re.search(r"""['"][~><=\d]""", m.group(2)):
                    info.unpinned_dependencies.append(gem_name)
    for gs in sorted(project_root.glob("*.gemspec"))[:2]:
        info.manifest_files.append(gs.name)
        if info.build_system == "unknown":
            info.build_system = "rubygems"
    return info


def _inspect_swift(project_root: Path) -> ExtendedManifestData:
    """Parse Package.swift metadata and SwiftPM package dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    pkg = project_root / "Package.swift"
    if not pkg.is_file():
        return info
    info.manifest_files.append("Package.swift")
    info.build_system = "swiftpm"
    text = pkg.read_text(encoding="utf-8", errors="ignore")
    tools_m = re.search(r"swift-tools-version:\s*([0-9.]+)", text)
    if tools_m:
        info.language_version_constraint = f"swift-tools-{tools_m.group(1)}"
    name_m = re.search(r"""name\s*:\s*"([^"]+)""", text)
    if name_m:
        info.project_name = name_m.group(1)
    for m in re.finditer(r"""\.package\s*\([^)]*url\s*:\s*"([^"]+)""", text):
        dep = m.group(1).rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        if dep and dep not in info.dependencies:
            info.dependencies.append(dep)
    return info


def _inspect_scala(project_root: Path) -> ExtendedManifestData:
    """Parse build.sbt metadata, scalaVersion, and libraryDependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    sbt = project_root / "build.sbt"
    if not sbt.is_file():
        return info
    info.manifest_files.append("build.sbt")
    info.build_system = "sbt"
    text = sbt.read_text(encoding="utf-8", errors="ignore")
    name_m = re.search(r"""name\s*:=\s*"([^"]+)""", text)
    if name_m:
        info.project_name = name_m.group(1)
    ver_m = re.search(r"""version\s*:=\s*"([^"]+)""", text)
    if ver_m:
        info.version = ver_m.group(1)
    scala_m = re.search(r"""scalaVersion\s*:=\s*"([^"]+)""", text)
    if scala_m:
        info.language_version_constraint = scala_m.group(1)
    for m in re.finditer(r""""([^"]+)"\s*%%?\s*"([^"]+)""", text):
        dep = f"{m.group(1)}:{m.group(2)}"
        if dep not in info.dependencies:
            info.dependencies.append(dep)
    return info


def _inspect_dart(project_root: Path) -> ExtendedManifestData:
    """Parse pubspec.yaml metadata, SDK constraint, and dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    pub = project_root / "pubspec.yaml"
    if not pub.is_file():
        return info
    info.manifest_files.append("pubspec.yaml")
    info.build_system = "pub"
    with contextlib.suppress(Exception):
        data = yaml.safe_load(pub.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            if isinstance(data.get("name"), str):
                info.project_name = data["name"]
            if isinstance(data.get("version"), str):
                info.version = data["version"]
            env = data.get("environment")
            if isinstance(env, dict) and isinstance(env.get("sdk"), str):
                info.language_version_constraint = env["sdk"]
            deps = data.get("dependencies")
            if isinstance(deps, dict):
                for k, v in deps.items():
                    info.dependencies.append(str(k))
                    if v is None or str(v).strip() == "any":
                        info.unpinned_dependencies.append(str(k))
            dev_deps = data.get("dev_dependencies")
            if isinstance(dev_deps, dict):
                info.dev_dependencies.extend(str(k) for k in dev_deps)
    return info


def _inspect_elixir(project_root: Path) -> ExtendedManifestData:
    """Parse mix.exs metadata, Elixir version constraint, and Hex dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    mix = project_root / "mix.exs"
    if not mix.is_file():
        return info
    info.manifest_files.append("mix.exs")
    info.build_system = "mix"
    text = mix.read_text(encoding="utf-8", errors="ignore")
    app_m = re.search(r"app:\s*:([a-zA-Z0-9_]+)", text)
    if app_m:
        info.project_name = app_m.group(1)
    ver_m = re.search(r"""version:\s*"([^"]+)""", text)
    if ver_m:
        info.version = ver_m.group(1)
    ex_m = re.search(r"""elixir:\s*"([^"]+)""", text)
    if ex_m:
        info.language_version_constraint = ex_m.group(1)
    for m in re.finditer(r"""\{\s*:([a-zA-Z0-9_]+)\s*,\s*"([^"]+)""", text):
        dep = m.group(1)
        if dep not in info.dependencies:
            info.dependencies.append(dep)
    return info


def _inspect_perl(project_root: Path) -> ExtendedManifestData:
    """Parse cpanfile / Makefile.PL / Build.PL metadata and Perl module dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    for mf, bs in (("cpanfile", "cpanm"), ("Makefile.PL", "ExtUtils::MakeMaker"), ("Build.PL", "Module::Build")):
        p = project_root / mf
        if p.is_file():
            info.manifest_files.append(mf)
            if info.build_system == "unknown":
                info.build_system = bs
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"""requires\s+['"]([A-Za-z0-9_:]+)['"]""", text):
                dep = m.group(1)
                if dep == "perl":
                    continue
                if dep not in info.dependencies:
                    info.dependencies.append(dep)
    return info


def _inspect_r(project_root: Path) -> ExtendedManifestData:
    """Parse R DESCRIPTION package metadata and Imports/Suggests dependencies."""
    info = ExtendedManifestData(project_name=project_root.name)
    desc = project_root / "DESCRIPTION"
    if desc.is_file():
        info.manifest_files.append("DESCRIPTION")
        info.build_system = "r-package"
        text = desc.read_text(encoding="utf-8", errors="ignore")
        pkg_m = re.search(r"^Package:\s*(.+)$", text, re.MULTILINE)
        if pkg_m:
            info.project_name = pkg_m.group(1).strip()
        ver_m = re.search(r"^Version:\s*(.+)$", text, re.MULTILINE)
        if ver_m:
            info.version = ver_m.group(1).strip()
        imp_m = re.search(r"^Imports:\s*(.+(?:\n[ \t]+.+)*)", text, re.MULTILINE)
        if imp_m:
            for item in re.split(r"[\n,]+", imp_m.group(1)):
                dep = item.strip().split(" ", 1)[0].split("(", 1)[0].strip()
                if dep and dep not in info.dependencies:
                    info.dependencies.append(dep)
    if (project_root / "renv.lock").is_file():
        info.manifest_files.append("renv.lock")
        if info.build_system == "unknown":
            info.build_system = "renv"
    return info


def _inspect_c_cpp(project_root: Path) -> ExtendedManifestData:
    """Parse CMakeLists.txt, meson.build, vcpkg.json, or conanfile manifests for C/C++."""
    info = ExtendedManifestData(project_name=project_root.name)
    for mf, bs in (
        ("CMakeLists.txt", "cmake"),
        ("meson.build", "meson"),
        ("vcpkg.json", "vcpkg"),
        ("conanfile.txt", "conan"),
        ("conanfile.py", "conan"),
        ("Makefile", "make"),
    ):
        p = project_root / mf
        if p.is_file():
            info.manifest_files.append(mf)
            if info.build_system == "unknown":
                info.build_system = bs
            if mf == "CMakeLists.txt":
                text = p.read_text(encoding="utf-8", errors="ignore")
                proj_m = re.search(r"project\s*\(\s*([A-Za-z0-9_.-]+)", text, re.IGNORECASE)
                if proj_m:
                    info.project_name = proj_m.group(1)
                ver_m = re.search(r"VERSION\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", text)
                if ver_m:
                    info.version = ver_m.group(1)
    return info


def inspect_extended_manifests(project_root: Path, active_lang: str) -> ExtendedManifestData:
    """Inspect build manifests for any non-core language registered in LANGUAGE_REGISTRY."""
    dispatch = {
        "rust": _inspect_rust,
        "csharp": _inspect_csharp,
        "ruby": _inspect_ruby,
        "swift": _inspect_swift,
        "scala": _inspect_scala,
        "dart": _inspect_dart,
        "elixir": _inspect_elixir,
        "perl": _inspect_perl,
        "r": _inspect_r,
        "c": _inspect_c_cpp,
        "cpp": _inspect_c_cpp,
        "cuda": _inspect_c_cpp,
    }
    handler = dispatch.get(active_lang)
    if handler is not None:
        return handler(project_root)

    spec = get_language_spec(active_lang)
    info = ExtendedManifestData(project_name=project_root.name, build_system=active_lang)
    if spec is not None:
        for mf in (*spec.primary_manifests, *spec.secondary_manifests):
            if (project_root / mf).is_file() and mf not in info.manifest_files:
                info.manifest_files.append(mf)
        for pat in spec.manifest_globs:
            for matched in sorted(project_root.glob(pat))[:3]:
                if matched.name not in info.manifest_files:
                    info.manifest_files.append(matched.name)
    return info


def detect_extended_tooling_issues(
    active_lang: str,
    manifest_info: ExtendedManifestData,
    lockfiles: list[str],
) -> list[str]:
    """Check lockfile presence and unpinned dependencies for non-core Tier A/B/C languages."""
    issues: list[str] = []
    spec = get_language_spec(active_lang)
    if spec is None or spec.tier == "companion_dsl":
        return issues
    if spec.lockfiles and (manifest_info.dependencies or manifest_info.dev_dependencies):
        if not (set(lockfiles) & set(spec.lockfiles)):
            expected = " / ".join(spec.lockfiles)
            issues.append(f"Missing lockfile ({expected}) for reproducible {spec.display_name} builds")
    if manifest_info.unpinned_dependencies:
        sample = ", ".join(manifest_info.unpinned_dependencies[:5])
        issues.append(f"Unpinned dependencies declared in {spec.display_name} manifest: {sample}")
    return issues
