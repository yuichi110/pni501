# Code Quality Standards (Haskell)

## Core Principles
1. **Strict GHC Warnings, HLint & Formatting**: Compile with `-Wall -Wcompat -Wincomplete-record-updates -Wincomplete-uni-patterns -Wredundant-constraints` (plus `-Werror` in CI), lint with `hlint`, and format with `ormolu` / `fourmolu` (`ProjectFacts.tooling_modernization_issues`).
2. **Total Functions & Zero Unsafe Escapes**: Eliminate partial Prelude functions (`head`, `tail`, `init`, `last`, `fromJust`, `read`, `!!`, `error`, `undefined`) in production logic (`AstFacts.bug_risk_idioms`); forbid `unsafePerformIO` / `unsafeCoerce` outside audited low-level FFI wrappers (`AstFacts.dangerous_sinks`, `AstFacts.global_state_usages`).
3. **Explicit Export Lists & Haddock Docs**: Declare explicit module export lists (`module Foo (Bar(..), run) where`) and explicit/qualified imports (`import qualified Data.Text as T`; `AstFacts.wildcard_imports`), and document public modules/types/functions with Haddock (`-- | ...`; `AstFacts.docstring_coverage_pct`).
4. **Pure Core & Bounded Complexity**: Keep pure domain functions separated from `IO` boundaries and decompose sprawling `do` blocks (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero partial functions / `unsafePerformIO` / `unsafeCoerce` in business logic, explicit exports/qualified imports, and `-Wall` cleanliness.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated open imports / HLint hints.
- **`FAIL`**: `docstring_coverage_pct < 60%`, `unsafePerformIO`/`unsafeCoerce` global-state hacks, or pervasive partial functions (`head`/`fromJust`/`error`) risking runtime crashes.
