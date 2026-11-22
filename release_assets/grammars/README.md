# PNI Extra Tree-sitter Grammar Release Assets

Internal build recipe that compiles five MIT-licensed Tree-sitter grammars lacking full 3-OS wheels on PyPI into cross-platform Python `cp310-abi3` native extensions and packages them as per-language, per-platform deterministic ZIP archives distributed via GitHub Releases:

- **COBOL** (`nolanlwin/tree-sitter-cobol`, MIT)
- **R** (`r-lib/tree-sitter-r`, MIT)
- **Vue** (`tree-sitter-grammars/tree-sitter-vue`, MIT)
- **Protocol Buffers** (`coder3101/tree-sitter-proto`, MIT)
- **Dockerfile** (`TheAuditorTool/tree-sitter-dockerfile`, MIT)

## Distribution Model

Following the same runtime asset caching architecture as `drawlib`, `pni501` itself remains a lightweight pure-Python (`py3-none-any`) wheel on PyPI. At runtime, `pni._languages._grammar_assets` downloads only the exact `<lang> × <platform>` ZIP archive on first use, verifies its pinned SHA-256 digest, and caches the extracted `_<lang>.abi3.so` / `_<lang>.pyd` binary locally.

Supported platform targets (Python 3.10+ `abi3`):

- `linux_x86_64` (`manylinux2014`)
- `linux_aarch64` (`manylinux2014`)
- `macos_arm64`
- `macos_x86_64`
- `windows_amd64`

## Triggering a Grammar Asset Release

Push a `grammars-v*` tag (e.g. `grammars-v0.2.0`) or dispatch `.github/workflows/build-grammar-assets.yml` from GitHub Actions. After the release is published, sync the pinned SHA-256 manifest into `src/pni/_languages/_grammar_assets.py`:

```bash
python release_assets/grammars/scripts/package_release_assets.py \
  --sync-manifest-url https://github.com/yuichi110/pni501/releases/download/grammars-v0.2.0/manifest.json \
  --target-py src/pni/_languages/_grammar_assets.py
```
