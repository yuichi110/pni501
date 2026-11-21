# pni501-extra-grammars

Companion cross-platform `abi3` Tree-sitter grammar bundle for [pni501](https://github.com/yuichi110/pni501), bundling five MIT-licensed grammars that lack full 3-OS wheels on PyPI:

- **COBOL** (`nolanlwin/tree-sitter-cobol`, MIT)
- **R** (`r-lib/tree-sitter-r`, MIT)
- **Vue** (`tree-sitter-grammars/tree-sitter-vue`, MIT)
- **Protocol Buffers** (`coder3101/tree-sitter-proto`, MIT)
- **Dockerfile** (`TheAuditorTool/tree-sitter-dockerfile`, MIT)

Each grammar is compiled as an independent Python `abi3` extension module (`_cobol`, `_r`, `_vue`, `_proto`, `_dockerfile`) and loaded lazily on first use.

## Local Build

```bash
python scripts/fetch_grammars.py
pip install --no-build-isolation .
```
