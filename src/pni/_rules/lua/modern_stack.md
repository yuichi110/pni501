# Modern Lua (5.4 / LuaJIT) & Ecosystem Idioms (`lua/modern_stack`)

## Core Principles
1. **Modern Module Pattern**: Return a local module table (`local M = {}; ...; return M`) instead of the deprecated Lua 5.1 `module(..., package.seeall)` global pollution pattern (`AstFacts.modernization_hints`).
2. **Efficient String & Table Operations**: Avoid quadratic string concatenation (`s = s .. chunk`) inside loops (accumulate in a local table and call `table.concat(parts)`), and leverage Lua 5.4 `<const>` / `<close>` attributes where targeting 5.4+.
3. **Hardened OpenResty / Network I/O**: Configure explicit timeouts on `ngx.socket.tcp` / `resty.http` / `luasocket` clients (`AstFacts.missing_io_timeouts`) and keep TLS verification enabled (`AstFacts.dangerous_sinks`).
4. **Clean Diagnostics**: Prefer structured logger callbacks (`ngx.log` / `vim.notify` / logger module) over raw `print(...)` inside libraries and services (`AstFacts.unstructured_logging`).
