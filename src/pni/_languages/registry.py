# Copyright (c) 2026 Yuichi Ito (yuichi@yuichi.com)
#
# This software is licensed under the Apache License, Version 2.0.
# For more information, please visit: https://github.com/yuichi110/pni501
#
# This software is provided "as is", without warranty of any kind,
# express or implied, including but not limited to the warranties of
# merchantability, fitness for a particular purpose and noninfringement.

"""Declarative single-source-of-truth registry for all 55 supported languages and Tree-sitter grammars."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

LanguageTier = Literal["full_audit", "static_audit", "companion_dsl"]
LanguageCategory = Literal[
    "app_language",
    "systems_hdl",
    "legacy_enterprise",
    "frontend_sfc",
    "iac_schema_config",
]
GrammarSource = Literal["package", "language_pack", "extra_wheel"]


@dataclass(frozen=True)
class GrammarProviderSpec:
    """Tree-sitter grammar loader binding for a single grammar identifier."""

    grammar_id: str
    module_name: str
    callable_name: str = "language"
    source: GrammarSource = "package"


@dataclass(frozen=True)
class LanguageSpec:
    """Canonical metadata describing one PNI-supported language."""

    language_id: str
    display_name: str
    tier: LanguageTier
    category: LanguageCategory
    default_grammar: str
    file_extensions: tuple[str, ...] = ()
    filenames: tuple[str, ...] = ()
    ext_grammars: tuple[tuple[str, str], ...] = ()
    primary_manifests: tuple[str, ...] = ()
    secondary_manifests: tuple[str, ...] = ()
    manifest_globs: tuple[str, ...] = ()
    lockfiles: tuple[str, ...] = ()
    default_source_dirs: tuple[str, ...] = ("src",)
    default_test_dirs: tuple[str, ...] = ("tests",)
    test_file_patterns: tuple[str, ...] = ()
    excluded_source_suffixes: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    has_runtime_harness: bool = False


GRAMMAR_PROVIDERS: dict[str, GrammarProviderSpec] = {
    # Core & Tier A (20 languages -> 22 grammars incl. php_only, tsx)
    "python": GrammarProviderSpec("python", "tree_sitter_python", "language"),
    "java": GrammarProviderSpec("java", "tree_sitter_java", "language"),
    "php": GrammarProviderSpec("php", "tree_sitter_php", "language_php"),
    "php_only": GrammarProviderSpec("php_only", "tree_sitter_php", "language_php_only"),
    "go": GrammarProviderSpec("go", "tree_sitter_go", "language"),
    "typescript": GrammarProviderSpec("typescript", "tree_sitter_typescript", "language_typescript"),
    "tsx": GrammarProviderSpec("tsx", "tree_sitter_typescript", "language_tsx"),
    "javascript": GrammarProviderSpec("javascript", "tree_sitter_javascript", "language"),
    "csharp": GrammarProviderSpec("csharp", "tree_sitter_c_sharp", "language"),
    "rust": GrammarProviderSpec("rust", "tree_sitter_rust", "language"),
    "ruby": GrammarProviderSpec("ruby", "tree_sitter_ruby", "language"),
    "kotlin": GrammarProviderSpec("kotlin", "tree_sitter_kotlin", "language"),
    "swift": GrammarProviderSpec("swift", "tree_sitter_swift", "language"),
    "c": GrammarProviderSpec("c", "tree_sitter_c", "language"),
    "cpp": GrammarProviderSpec("cpp", "tree_sitter_cpp", "language"),
    "scala": GrammarProviderSpec("scala", "tree_sitter_scala", "language"),
    "dart": GrammarProviderSpec("dart", "tree_sitter_dart", "language"),
    "elixir": GrammarProviderSpec("elixir", "tree_sitter_elixir", "language"),
    "vue": GrammarProviderSpec("vue", "pni501_extra_grammars", "language_vue", source="extra_wheel"),
    "perl": GrammarProviderSpec("perl", "tree_sitter_perl", "language"),
    "cobol": GrammarProviderSpec("cobol", "pni501_extra_grammars", "language_cobol", source="extra_wheel"),
    "r": GrammarProviderSpec("r", "pni501_extra_grammars", "language_r", source="extra_wheel"),
    # Tier B (20 static-audit languages)
    "bash": GrammarProviderSpec("bash", "tree_sitter_bash", "language"),
    "powershell": GrammarProviderSpec("powershell", "tree_sitter_powershell", "language"),
    "groovy": GrammarProviderSpec("groovy", "tree_sitter_groovy", "language"),
    "objc": GrammarProviderSpec("objc", "tree_sitter_objc", "language"),
    "lua": GrammarProviderSpec("lua", "tree_sitter_lua", "language"),
    "haskell": GrammarProviderSpec("haskell", "tree_sitter_haskell", "language"),
    "fsharp": GrammarProviderSpec("fsharp", "tree_sitter_fsharp", "language"),
    "ocaml": GrammarProviderSpec("ocaml", "tree_sitter_ocaml", "language_ocaml"),
    "zig": GrammarProviderSpec("zig", "tree_sitter_zig", "language"),
    "julia": GrammarProviderSpec("julia", "tree_sitter_julia", "language"),
    "fortran": GrammarProviderSpec("fortran", "tree_sitter_fortran", "language"),
    "matlab": GrammarProviderSpec("matlab", "tree_sitter_matlab", "language"),
    "svelte": GrammarProviderSpec("svelte", "tree_sitter_svelte", "language"),
    "solidity": GrammarProviderSpec("solidity", "tree_sitter_solidity", "language"),
    "cuda": GrammarProviderSpec("cuda", "tree_sitter_cuda", "language"),
    "verilog": GrammarProviderSpec("verilog", "tree_sitter_verilog", "language"),
    "vhdl": GrammarProviderSpec("vhdl", "tree_sitter_vhdl", "language"),
    "ada": GrammarProviderSpec("ada", "tree_sitter_ada", "language"),
    "odin": GrammarProviderSpec("odin", "tree_sitter_odin", "language"),
    "commonlisp": GrammarProviderSpec("commonlisp", "tree_sitter_commonlisp", "language"),
    # Tier C (15 companion IaC / schema / build / config languages)
    "dockerfile": GrammarProviderSpec(
        "dockerfile", "pni501_extra_grammars", "language_dockerfile", source="extra_wheel"
    ),
    "hcl": GrammarProviderSpec("hcl", "tree_sitter_hcl", "language"),
    "bicep": GrammarProviderSpec("bicep", "tree_sitter_bicep", "language"),
    "nix": GrammarProviderSpec("nix", "tree_sitter_nix", "language"),
    "make": GrammarProviderSpec("make", "tree_sitter_make", "language"),
    "starlark": GrammarProviderSpec("starlark", "tree_sitter_starlark", "language"),
    "protobuf": GrammarProviderSpec("protobuf", "pni501_extra_grammars", "language_proto", source="extra_wheel"),
    "sql": GrammarProviderSpec("sql", "tree_sitter_sql", "language"),
    "html": GrammarProviderSpec("html", "tree_sitter_html", "language"),
    "css": GrammarProviderSpec("css", "tree_sitter_css", "language"),
    "scss": GrammarProviderSpec("scss", "tree_sitter_scss", "language"),
    "yaml": GrammarProviderSpec("yaml", "tree_sitter_yaml", "language"),
    "json": GrammarProviderSpec("json", "tree_sitter_json", "language"),
    "toml": GrammarProviderSpec("toml", "tree_sitter_toml", "language"),
    "xml": GrammarProviderSpec("xml", "tree_sitter_xml", "language_xml"),
}

LANGUAGE_REGISTRY: dict[str, LanguageSpec] = {
    # =========================================================================
    # Tier A: Full Engineering Audit (20 languages)
    # =========================================================================
    "python": LanguageSpec(
        language_id="python",
        display_name="Python",
        tier="full_audit",
        category="app_language",
        default_grammar="python",
        file_extensions=(".py",),
        primary_manifests=("pyproject.toml", "setup.py", "setup.cfg", "Pipfile"),
        secondary_manifests=("requirements.txt",),
        lockfiles=("uv.lock", "poetry.lock", "Pipfile.lock"),
        default_source_dirs=("src",),
        default_test_dirs=("tests",),
        test_file_patterns=("test_*.py", "*_test.py"),
        aliases=("py", "python3"),
        has_runtime_harness=True,
    ),
    "java": LanguageSpec(
        language_id="java",
        display_name="Java",
        tier="full_audit",
        category="app_language",
        default_grammar="java",
        file_extensions=(".java",),
        primary_manifests=("pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
        lockfiles=("gradle.lockfile",),
        default_source_dirs=("src/main/java",),
        default_test_dirs=("src/test/java",),
        test_file_patterns=("*Test.java", "*Tests.java", "Test*.java", "*IT.java"),
        has_runtime_harness=True,
    ),
    "php": LanguageSpec(
        language_id="php",
        display_name="PHP",
        tier="full_audit",
        category="app_language",
        default_grammar="php",
        file_extensions=(".php", ".phtml"),
        primary_manifests=(
            "composer.json",
            "wp-config.php",
            "wp-config-sample.php",
            "artisan",
            "phpunit.xml",
            "phpunit.xml.dist",
        ),
        lockfiles=("composer.lock",),
        default_source_dirs=("app", "src", "routes"),
        default_test_dirs=("tests",),
        test_file_patterns=("*Test.php", "Test*.php", "*_test.php"),
        has_runtime_harness=True,
    ),
    "go": LanguageSpec(
        language_id="go",
        display_name="Go",
        tier="full_audit",
        category="app_language",
        default_grammar="go",
        file_extensions=(".go",),
        primary_manifests=("go.mod", "go.work"),
        lockfiles=("go.sum",),
        default_source_dirs=(".",),
        default_test_dirs=(".",),
        test_file_patterns=("*_test.go",),
        aliases=("golang",),
        has_runtime_harness=True,
    ),
    "typescript": LanguageSpec(
        language_id="typescript",
        display_name="TypeScript",
        tier="full_audit",
        category="app_language",
        default_grammar="typescript",
        file_extensions=(".ts", ".tsx"),
        ext_grammars=((".ts", "typescript"), (".tsx", "tsx")),
        primary_manifests=("tsconfig.json", "tsconfig.base.json"),
        secondary_manifests=("package.json",),
        lockfiles=("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"),
        default_source_dirs=("src",),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*.test.ts", "*.spec.ts", "*.test.tsx", "*.spec.tsx"),
        excluded_source_suffixes=(".d.ts",),
        aliases=("ts", "tsx"),
        has_runtime_harness=True,
    ),
    "javascript": LanguageSpec(
        language_id="javascript",
        display_name="JavaScript",
        tier="full_audit",
        category="app_language",
        default_grammar="tsx",
        file_extensions=(".js", ".jsx", ".mjs", ".cjs"),
        ext_grammars=((".js", "tsx"), (".jsx", "tsx"), (".mjs", "tsx"), (".cjs", "tsx")),
        primary_manifests=("jsconfig.json",),
        secondary_manifests=("package.json",),
        lockfiles=("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"),
        default_source_dirs=("src",),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*.test.js", "*.spec.js", "*.test.jsx", "*.spec.jsx", "*.test.mjs", "*.spec.mjs"),
        aliases=("js", "jsx", "node", "nodejs"),
        has_runtime_harness=True,
    ),
    "csharp": LanguageSpec(
        language_id="csharp",
        display_name="C#",
        tier="full_audit",
        category="app_language",
        default_grammar="csharp",
        file_extensions=(".cs",),
        primary_manifests=("Directory.Build.props", "Directory.Packages.props", "global.json"),
        manifest_globs=("*.csproj", "*.sln"),
        lockfiles=("packages.lock.json",),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("*Tests.cs", "*Test.cs", "*Spec.cs"),
        excluded_source_suffixes=(".designer.cs", ".g.cs"),
        aliases=("c#", "cs", "c-sharp", "dotnet"),
        has_runtime_harness=True,
    ),
    "rust": LanguageSpec(
        language_id="rust",
        display_name="Rust",
        tier="full_audit",
        category="app_language",
        default_grammar="rust",
        file_extensions=(".rs",),
        primary_manifests=("Cargo.toml",),
        lockfiles=("Cargo.lock",),
        default_source_dirs=("src",),
        default_test_dirs=("tests",),
        test_file_patterns=("*_test.rs", "test_*.rs"),
        aliases=("rs",),
        has_runtime_harness=True,
    ),
    "ruby": LanguageSpec(
        language_id="ruby",
        display_name="Ruby",
        tier="full_audit",
        category="app_language",
        default_grammar="ruby",
        file_extensions=(".rb", ".rake"),
        primary_manifests=("Gemfile", "Rakefile"),
        manifest_globs=("*.gemspec",),
        lockfiles=("Gemfile.lock",),
        default_source_dirs=("lib", "app", "src"),
        default_test_dirs=("spec", "test"),
        test_file_patterns=("*_spec.rb", "*_test.rb", "test_*.rb"),
        aliases=("rb", "rails"),
        has_runtime_harness=True,
    ),
    "kotlin": LanguageSpec(
        language_id="kotlin",
        display_name="Kotlin",
        tier="full_audit",
        category="app_language",
        default_grammar="kotlin",
        file_extensions=(".kt", ".kts"),
        secondary_manifests=("build.gradle.kts", "settings.gradle.kts", "pom.xml"),
        lockfiles=("gradle.lockfile",),
        default_source_dirs=("src/main/kotlin", "src"),
        default_test_dirs=("src/test/kotlin", "tests"),
        test_file_patterns=("*Test.kt", "*Tests.kt", "*Spec.kt"),
        aliases=("kt", "kts"),
        has_runtime_harness=True,
    ),
    "swift": LanguageSpec(
        language_id="swift",
        display_name="Swift",
        tier="full_audit",
        category="app_language",
        default_grammar="swift",
        file_extensions=(".swift",),
        primary_manifests=("Package.swift",),
        lockfiles=("Package.resolved",),
        default_source_dirs=("Sources", "src"),
        default_test_dirs=("Tests", "tests"),
        test_file_patterns=("*Tests.swift", "*Test.swift"),
        has_runtime_harness=True,
    ),
    "c": LanguageSpec(
        language_id="c",
        display_name="C",
        tier="full_audit",
        category="systems_hdl",
        default_grammar="c",
        file_extensions=(".c", ".h"),
        secondary_manifests=("CMakeLists.txt", "meson.build", "Makefile"),
        default_source_dirs=("src", "include", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("test_*.c", "*_test.c"),
        has_runtime_harness=True,
    ),
    "cpp": LanguageSpec(
        language_id="cpp",
        display_name="C++",
        tier="full_audit",
        category="systems_hdl",
        default_grammar="cpp",
        file_extensions=(".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"),
        primary_manifests=("conanfile.txt", "conanfile.py", "vcpkg.json"),
        secondary_manifests=("CMakeLists.txt", "meson.build", "Makefile"),
        default_source_dirs=("src", "include", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("test_*.cpp", "*_test.cpp", "*_test.cc", "*Test.cpp"),
        aliases=("c++", "cxx", "cc"),
        has_runtime_harness=True,
    ),
    "scala": LanguageSpec(
        language_id="scala",
        display_name="Scala",
        tier="full_audit",
        category="app_language",
        default_grammar="scala",
        file_extensions=(".scala", ".sc"),
        primary_manifests=("build.sbt",),
        default_source_dirs=("src/main/scala", "src"),
        default_test_dirs=("src/test/scala", "tests"),
        test_file_patterns=("*Spec.scala", "*Suite.scala", "*Test.scala"),
        has_runtime_harness=True,
    ),
    "dart": LanguageSpec(
        language_id="dart",
        display_name="Dart",
        tier="full_audit",
        category="app_language",
        default_grammar="dart",
        file_extensions=(".dart",),
        primary_manifests=("pubspec.yaml",),
        lockfiles=("pubspec.lock",),
        default_source_dirs=("lib", "bin", "src"),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("*_test.dart",),
        aliases=("flutter",),
        has_runtime_harness=True,
    ),
    "elixir": LanguageSpec(
        language_id="elixir",
        display_name="Elixir",
        tier="full_audit",
        category="app_language",
        default_grammar="elixir",
        file_extensions=(".ex", ".exs"),
        primary_manifests=("mix.exs",),
        lockfiles=("mix.lock",),
        default_source_dirs=("lib", "src"),
        default_test_dirs=("test",),
        test_file_patterns=("*_test.exs",),
        aliases=("ex", "exs"),
        has_runtime_harness=True,
    ),
    "vue": LanguageSpec(
        language_id="vue",
        display_name="Vue",
        tier="full_audit",
        category="frontend_sfc",
        default_grammar="vue",
        file_extensions=(".vue",),
        primary_manifests=("nuxt.config.ts", "nuxt.config.js", "vue.config.js"),
        secondary_manifests=("package.json",),
        lockfiles=("package-lock.json", "pnpm-lock.yaml", "yarn.lock"),
        default_source_dirs=("src", "components", "pages"),
        default_test_dirs=("tests", "test", "__tests__"),
        test_file_patterns=("*.test.ts", "*.spec.ts", "*.test.js", "*.spec.js"),
        aliases=("vuejs",),
        has_runtime_harness=True,
    ),
    "perl": LanguageSpec(
        language_id="perl",
        display_name="Perl",
        tier="full_audit",
        category="legacy_enterprise",
        default_grammar="perl",
        file_extensions=(".pl", ".pm", ".t"),
        primary_manifests=("cpanfile", "Makefile.PL", "Build.PL", "dist.ini"),
        lockfiles=("cpanfile.snapshot",),
        default_source_dirs=("lib", "bin", "src", "."),
        default_test_dirs=("t", "tests"),
        test_file_patterns=("*.t",),
        aliases=("pl", "pm"),
        has_runtime_harness=True,
    ),
    "cobol": LanguageSpec(
        language_id="cobol",
        display_name="COBOL",
        tier="full_audit",
        category="legacy_enterprise",
        default_grammar="cobol",
        file_extensions=(".cob", ".cbl", ".cpy"),
        default_source_dirs=("src", "cobol", "cbl", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("test_*.cob", "test_*.cbl", "*_test.cbl"),
        aliases=("cob", "cbl"),
        has_runtime_harness=False,
    ),
    "r": LanguageSpec(
        language_id="r",
        display_name="R",
        tier="full_audit",
        category="legacy_enterprise",
        default_grammar="r",
        file_extensions=(".r",),
        primary_manifests=("DESCRIPTION", "NAMESPACE"),
        manifest_globs=("*.Rproj",),
        lockfiles=("renv.lock",),
        default_source_dirs=("R", "src", "."),
        default_test_dirs=("tests", "tests/testthat"),
        test_file_patterns=("test-*.r", "test_*.r", "*_test.r"),
        aliases=("rlang",),
        has_runtime_harness=True,
    ),
    # =========================================================================
    # Tier B: Declarative Static AST Audit (20 languages)
    # =========================================================================
    "bash": LanguageSpec(
        language_id="bash",
        display_name="Bash / Shell",
        tier="static_audit",
        category="app_language",
        default_grammar="bash",
        file_extensions=(".sh", ".bash", ".zsh"),
        default_source_dirs=("scripts", "bin", "src", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("*_test.sh", "test_*.sh", "*.bats"),
        aliases=("sh", "shell", "zsh"),
    ),
    "powershell": LanguageSpec(
        language_id="powershell",
        display_name="PowerShell",
        tier="static_audit",
        category="app_language",
        default_grammar="powershell",
        file_extensions=(".ps1", ".psm1", ".psd1"),
        default_source_dirs=("src", "scripts", "."),
        default_test_dirs=("tests", "Tests"),
        test_file_patterns=("*.Tests.ps1", "*.tests.ps1"),
        aliases=("ps1", "pwsh"),
    ),
    "groovy": LanguageSpec(
        language_id="groovy",
        display_name="Groovy",
        tier="static_audit",
        category="app_language",
        default_grammar="groovy",
        file_extensions=(".groovy", ".gradle"),
        default_source_dirs=("src/main/groovy", "src", "vars", "."),
        default_test_dirs=("src/test/groovy", "test", "tests"),
        test_file_patterns=("*Spec.groovy", "*Test.groovy"),
    ),
    "objc": LanguageSpec(
        language_id="objc",
        display_name="Objective-C",
        tier="static_audit",
        category="app_language",
        default_grammar="objc",
        file_extensions=(".m", ".mm"),
        primary_manifests=("Podfile",),
        lockfiles=("Podfile.lock",),
        default_source_dirs=("Sources", "Classes", "src", "."),
        default_test_dirs=("Tests", "tests"),
        test_file_patterns=("*Tests.m", "*Test.m"),
        aliases=("objective-c", "objectivec"),
    ),
    "lua": LanguageSpec(
        language_id="lua",
        display_name="Lua",
        tier="static_audit",
        category="app_language",
        default_grammar="lua",
        file_extensions=(".lua",),
        manifest_globs=("*.rockspec",),
        default_source_dirs=("lua", "src", "lib", "."),
        default_test_dirs=("spec", "tests", "test"),
        test_file_patterns=("*_spec.lua", "*_test.lua", "test_*.lua"),
    ),
    "haskell": LanguageSpec(
        language_id="haskell",
        display_name="Haskell",
        tier="static_audit",
        category="app_language",
        default_grammar="haskell",
        file_extensions=(".hs", ".lhs"),
        primary_manifests=("stack.yaml", "cabal.project", "package.yaml"),
        manifest_globs=("*.cabal",),
        default_source_dirs=("src", "app"),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("*Spec.hs", "*Test.hs"),
        aliases=("hs",),
    ),
    "fsharp": LanguageSpec(
        language_id="fsharp",
        display_name="F#",
        tier="static_audit",
        category="app_language",
        default_grammar="fsharp",
        file_extensions=(".fs", ".fsi", ".fsx"),
        manifest_globs=("*.fsproj",),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("*Tests.fs", "*Test.fs"),
        aliases=("f#", "fs", "f-sharp"),
    ),
    "ocaml": LanguageSpec(
        language_id="ocaml",
        display_name="OCaml",
        tier="static_audit",
        category="app_language",
        default_grammar="ocaml",
        file_extensions=(".ml", ".mli"),
        primary_manifests=("dune-project", "dune"),
        manifest_globs=("*.opam",),
        default_source_dirs=("lib", "bin", "src"),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("test_*.ml", "*_test.ml"),
        aliases=("ml",),
    ),
    "zig": LanguageSpec(
        language_id="zig",
        display_name="Zig",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="zig",
        file_extensions=(".zig",),
        primary_manifests=("build.zig", "build.zig.zon"),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*_test.zig", "test_*.zig"),
    ),
    "julia": LanguageSpec(
        language_id="julia",
        display_name="Julia",
        tier="static_audit",
        category="app_language",
        default_grammar="julia",
        file_extensions=(".jl",),
        primary_manifests=("Project.toml",),
        lockfiles=("Manifest.toml",),
        default_source_dirs=("src", "."),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("runtests.jl", "test_*.jl", "*_test.jl"),
        aliases=("jl",),
    ),
    "fortran": LanguageSpec(
        language_id="fortran",
        display_name="Fortran",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="fortran",
        file_extensions=(".f90", ".f95", ".f03", ".f08", ".f", ".for"),
        primary_manifests=("fpm.toml",),
        default_source_dirs=("src", "app", "."),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("test_*.f90", "*_test.f90"),
        aliases=("f90",),
    ),
    "matlab": LanguageSpec(
        language_id="matlab",
        display_name="MATLAB",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="matlab",
        file_extensions=(".m",),
        default_source_dirs=("src", "matlab", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("test_*.m", "*Test.m"),
    ),
    "svelte": LanguageSpec(
        language_id="svelte",
        display_name="Svelte",
        tier="static_audit",
        category="frontend_sfc",
        default_grammar="svelte",
        file_extensions=(".svelte",),
        primary_manifests=("svelte.config.js", "svelte.config.ts"),
        secondary_manifests=("package.json",),
        default_source_dirs=("src",),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*.test.ts", "*.spec.ts", "*.test.js"),
    ),
    "solidity": LanguageSpec(
        language_id="solidity",
        display_name="Solidity",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="solidity",
        file_extensions=(".sol",),
        primary_manifests=("foundry.toml", "hardhat.config.ts", "hardhat.config.js", "truffle-config.js"),
        default_source_dirs=("contracts", "src"),
        default_test_dirs=("test", "tests"),
        test_file_patterns=("*.t.sol", "*Test.sol"),
        aliases=("sol",),
    ),
    "cuda": LanguageSpec(
        language_id="cuda",
        display_name="CUDA",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="cuda",
        file_extensions=(".cu", ".cuh"),
        default_source_dirs=("src", "kernels", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("test_*.cu", "*_test.cu"),
    ),
    "verilog": LanguageSpec(
        language_id="verilog",
        display_name="Verilog / SystemVerilog",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="verilog",
        file_extensions=(".v", ".sv", ".svh", ".vh"),
        default_source_dirs=("rtl", "src", "hdl", "."),
        default_test_dirs=("tb", "sim", "tests"),
        test_file_patterns=("tb_*.sv", "tb_*.v", "*_tb.sv", "*_tb.v"),
        aliases=("sv", "systemverilog"),
    ),
    "vhdl": LanguageSpec(
        language_id="vhdl",
        display_name="VHDL",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="vhdl",
        file_extensions=(".vhd", ".vhdl"),
        default_source_dirs=("rtl", "src", "hdl", "."),
        default_test_dirs=("tb", "sim", "tests"),
        test_file_patterns=("tb_*.vhd", "*_tb.vhd", "*_tb.vhdl"),
    ),
    "ada": LanguageSpec(
        language_id="ada",
        display_name="Ada",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="ada",
        file_extensions=(".adb", ".ads"),
        primary_manifests=("alire.toml",),
        manifest_globs=("*.gpr",),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "test"),
        test_file_patterns=("*_test.adb", "test_*.adb"),
    ),
    "odin": LanguageSpec(
        language_id="odin",
        display_name="Odin",
        tier="static_audit",
        category="systems_hdl",
        default_grammar="odin",
        file_extensions=(".odin",),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "src"),
        test_file_patterns=("*_test.odin", "test_*.odin"),
    ),
    "commonlisp": LanguageSpec(
        language_id="commonlisp",
        display_name="Common Lisp",
        tier="static_audit",
        category="app_language",
        default_grammar="commonlisp",
        file_extensions=(".lisp", ".lsp", ".cl", ".asd"),
        manifest_globs=("*.asd",),
        default_source_dirs=("src", "."),
        default_test_dirs=("tests", "t"),
        test_file_patterns=("*-test.lisp", "test-*.lisp"),
        aliases=("lisp", "cl"),
    ),
    # =========================================================================
    # Tier C: Polyglot Companion / IaC / Schema / Config (15 languages)
    # =========================================================================
    "dockerfile": LanguageSpec(
        language_id="dockerfile",
        display_name="Dockerfile",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="dockerfile",
        file_extensions=(".dockerfile",),
        filenames=("Dockerfile", "Containerfile"),
        default_source_dirs=(".",),
        default_test_dirs=(),
        aliases=("docker", "containerfile"),
    ),
    "hcl": LanguageSpec(
        language_id="hcl",
        display_name="HCL / Terraform",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="hcl",
        file_extensions=(".tf", ".tfvars", ".hcl"),
        default_source_dirs=(".", "infra", "terraform"),
        default_test_dirs=(),
        aliases=("terraform", "tf"),
    ),
    "bicep": LanguageSpec(
        language_id="bicep",
        display_name="Bicep",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="bicep",
        file_extensions=(".bicep",),
        default_source_dirs=(".", "infra", "bicep"),
        default_test_dirs=(),
    ),
    "nix": LanguageSpec(
        language_id="nix",
        display_name="Nix",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="nix",
        file_extensions=(".nix",),
        primary_manifests=("flake.nix",),
        lockfiles=("flake.lock",),
        default_source_dirs=(".",),
        default_test_dirs=(),
    ),
    "make": LanguageSpec(
        language_id="make",
        display_name="Makefile",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="make",
        file_extensions=(".mk", ".mak"),
        filenames=("Makefile", "GNUmakefile", "makefile"),
        default_source_dirs=(".",),
        default_test_dirs=(),
        aliases=("makefile",),
    ),
    "starlark": LanguageSpec(
        language_id="starlark",
        display_name="Starlark / Bazel",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="starlark",
        file_extensions=(".bzl", ".star"),
        filenames=("BUILD", "BUILD.bazel", "WORKSPACE", "WORKSPACE.bazel", "MODULE.bazel"),
        default_source_dirs=(".",),
        default_test_dirs=(),
        aliases=("bazel", "bzl"),
    ),
    "protobuf": LanguageSpec(
        language_id="protobuf",
        display_name="Protocol Buffers",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="protobuf",
        file_extensions=(".proto",),
        primary_manifests=("buf.yaml",),
        lockfiles=("buf.lock",),
        default_source_dirs=("proto", "protos", "api", "."),
        default_test_dirs=(),
        aliases=("proto",),
    ),
    "sql": LanguageSpec(
        language_id="sql",
        display_name="SQL",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="sql",
        file_extensions=(".sql",),
        default_source_dirs=("migrations", "sql", "db", "."),
        default_test_dirs=(),
    ),
    "html": LanguageSpec(
        language_id="html",
        display_name="HTML",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="html",
        file_extensions=(".html", ".htm"),
        default_source_dirs=("templates", "public", "src", "."),
        default_test_dirs=(),
    ),
    "css": LanguageSpec(
        language_id="css",
        display_name="CSS",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="css",
        file_extensions=(".css",),
        default_source_dirs=("styles", "src", "public", "."),
        default_test_dirs=(),
    ),
    "scss": LanguageSpec(
        language_id="scss",
        display_name="SCSS",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="scss",
        file_extensions=(".scss",),
        default_source_dirs=("styles", "src", "."),
        default_test_dirs=(),
        aliases=("sass",),
    ),
    "yaml": LanguageSpec(
        language_id="yaml",
        display_name="YAML",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="yaml",
        file_extensions=(".yaml", ".yml"),
        default_source_dirs=(".", ".github/workflows"),
        default_test_dirs=(),
        aliases=("yml",),
    ),
    "json": LanguageSpec(
        language_id="json",
        display_name="JSON",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="json",
        file_extensions=(".json",),
        default_source_dirs=(".",),
        default_test_dirs=(),
    ),
    "toml": LanguageSpec(
        language_id="toml",
        display_name="TOML",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="toml",
        file_extensions=(".toml",),
        default_source_dirs=(".",),
        default_test_dirs=(),
    ),
    "xml": LanguageSpec(
        language_id="xml",
        display_name="XML",
        tier="companion_dsl",
        category="iac_schema_config",
        default_grammar="xml",
        file_extensions=(".xml", ".xsd", ".xsl"),
        default_source_dirs=(".",),
        default_test_dirs=(),
    ),
}

_LANGUAGE_ALIAS_MAP: dict[str, str] = {}
for _lang_id, _spec in LANGUAGE_REGISTRY.items():
    _LANGUAGE_ALIAS_MAP[_lang_id] = _lang_id
    for _alias in _spec.aliases:
        _LANGUAGE_ALIAS_MAP[_alias.lower()] = _lang_id


def resolve_language_id(language_id: str) -> str:
    """Resolve a language name or alias into its canonical lowercase language_id."""
    key = language_id.strip().lower()
    return _LANGUAGE_ALIAS_MAP.get(key, key)


def register_grammar_provider(spec: GrammarProviderSpec) -> None:
    """Register or override a Tree-sitter grammar provider entry."""
    GRAMMAR_PROVIDERS[spec.grammar_id.lower()] = spec


def get_grammar_provider(grammar_id: str) -> GrammarProviderSpec | None:
    """Look up a registered Tree-sitter grammar provider by grammar_id."""
    key = grammar_id.strip().lower()
    direct = GRAMMAR_PROVIDERS.get(key)
    if direct is not None:
        return direct
    resolved = resolve_language_id(key)
    return GRAMMAR_PROVIDERS.get(resolved)


def register_language_spec(spec: LanguageSpec) -> None:
    """Register or override a language specification in the central registry."""
    lid = spec.language_id.lower()
    LANGUAGE_REGISTRY[lid] = spec
    _LANGUAGE_ALIAS_MAP[lid] = lid
    for alias in spec.aliases:
        _LANGUAGE_ALIAS_MAP[alias.lower()] = lid


def get_language_spec(language_id: str) -> LanguageSpec | None:
    """Return the LanguageSpec for a normalized language_id or alias, or None if unregistered."""
    return LANGUAGE_REGISTRY.get(resolve_language_id(language_id))


def iter_language_specs(*, tier: LanguageTier | None = None) -> tuple[LanguageSpec, ...]:
    """Return registered LanguageSpec entries, optionally filtered by support tier."""
    if tier is None:
        return tuple(LANGUAGE_REGISTRY.values())
    return tuple(spec for spec in LANGUAGE_REGISTRY.values() if spec.tier == tier)


def list_supported_languages(*, tier: LanguageTier | None = None) -> tuple[str, ...]:
    """Return registered language IDs in deterministic registration order."""
    return tuple(spec.language_id for spec in iter_language_specs(tier=tier))


def resolve_grammar_for_path(spec: LanguageSpec, file_path: Path) -> str:
    """Resolve the Tree-sitter grammar ID for file_path using spec.ext_grammars or default_grammar."""
    suffix = file_path.suffix.lower()
    for ext, grammar_id in spec.ext_grammars:
        if suffix == ext:
            return grammar_id
    return spec.default_grammar


def get_language_by_path(file_path: Path) -> LanguageSpec | None:
    """Resolve the matching LanguageSpec for a single file path by filename or extension."""
    name = file_path.name
    name_low = name.lower()
    for spec in LANGUAGE_REGISTRY.values():
        if name in spec.filenames or name_low in {fn.lower() for fn in spec.filenames}:
            return spec
        if name_low.startswith("dockerfile.") and spec.language_id == "dockerfile":
            return spec

    suffix = file_path.suffix.lower()
    if not suffix:
        return None
    for spec in LANGUAGE_REGISTRY.values():
        if suffix in spec.file_extensions:
            if spec.excluded_source_suffixes and any(name_low.endswith(ex) for ex in spec.excluded_source_suffixes):
                continue
            return spec
    return None
