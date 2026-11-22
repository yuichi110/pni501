# Typing, LuaCATS Annotations & Table Contract Standards (Lua)

## Core Principles
1. **Dynamic Typing Exemption & LuaLS / Teal Contracts**: Lua is dynamically typed — do **NOT** penalize Lua code for lacking native static type syntax. Evaluate contract clarity via LuaLS (`---@class`, `---@param`, `---@return`, `---@alias`) annotations or Teal (`.tl`) definitions alongside runtime argument checks (`assert(type(x) == "string", ...)`).
2. **Avoid `any` & Unstructured Table Bags**: Define named `---@class` table schemas for domain records instead of passing undocumented nested tables, and minimize `---@type any` or `---@diagnostic disable` overrides (`AstFacts.weak_type_usages`, `AstFacts.unscoped_type_ignores`).
3. **1-Based Sequence & Hole-Free Table Discipline**: Never insert `nil` into sequence arrays (breaks `#t` and `ipairs`), and distinguish sequence iteration (`ipairs` / numeric `for i = 1, #t`) from hash-map iteration (`pairs`).
4. **Explicit Metatable Contracts**: Keep metatables (`__index`, `__newindex`) shallow and documented to avoid hidden property resolution surprises.

## Evaluation Thresholds
- **`PASS`**: Clear LuaCATS `@class`/`@param`/`@return` contracts on public module APIs, safe `ipairs`/`pairs` usage, and minimal diagnostic disables.
- **`WARN`**: Partial LuaCATS coverage or isolated untyped table option bags.
- **`FAIL`**: Undocumented public tables combined with `nil`-hole sequence bugs or blanket `---@diagnostic disable` files.
