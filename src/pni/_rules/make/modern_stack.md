# Modern Make & Task-Runner Idioms (`make/modern_stack`)

## Core Principles
1. **Modern GNU Make Safety Header**: Start modern GNU Makefiles with `SHELL := bash`, `.SHELLFLAGS := -eu -o pipefail -c`, `.DELETE_ON_ERROR:`, and `MAKEFLAGS += --no-builtin-rules` (eliminates slow, surprising implicit rules; `AstFacts.modernization_hints`).
2. **Order-Only Directory Prerequisites & Target-Specific Vars**: Use `$(OUT_DIR)/app: $(OBJS) | $(OUT_DIR)` instead of phony directory dependencies that trigger needless rebuilds.
3. **Modular `*.mk` Includes**: Split large multi-hundred-line Makefiles into focused `mk/*.mk` includes (or migrate complex task orchestration to `justfile` / language CLI tools when scripting complexity outgrows Make).
4. **Zero Silent Failure Prefixes**: Avoid `-` ignore-error prefixes on test/build commands unless explicitly justified (e.g., optional cleanup).
