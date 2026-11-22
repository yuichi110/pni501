# Modern Bazel 7/8 & Starlark Idioms (`starlark/modern_stack`)

## Core Principles
1. **Bazel 7/8 Bzlmod & Symbolic Macros**: Migrate `WORKSPACE` to `MODULE.bazel`, adopt symbolic `macro(...)` (enforcing visibility & laziness), `ctx.actions.args().add_all(depset)` (deferred expansion), and `platforms`/`toolchains` over legacy `--crosstool_top` flags (`AstFacts.modernization_hints`).
2. **No Deprecated Native Rules in `BUILD` Files**: Load language rules explicitly from their dedicated rulesets (`load("@rules_cc//cc:defs.bzl", "cc_library")`, `@rules_python`, `@rules_java`, `@rules_shell`) rather than calling removed built-in `native.*` rules.
3. **Remote-Cache & Build-Without-the-Bytes Readiness**: Keep actions purely functional (no timestamps/randomness/host paths embedded in outputs) so remote caching achieves high hit rates.
4. **Clean `select()` Config Conditions**: Use `config_setting` + `select()` cleanly rather than hardcoding OS/arch assumptions in `.bzl` rules.
