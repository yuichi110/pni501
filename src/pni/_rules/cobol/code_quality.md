# Code Quality Standards (COBOL)

## Core Principles
1. **Structured Control Flow (Zero `GO TO` / `ALTER`)**: Replace unstructured `GO TO` jumps, `ALTER` self-modifying jumps, and fall-through `PERFORM ... THRU` spaghetti with structured `PERFORM <paragraph>`, `PERFORM UNTIL ... END-PERFORM`, and `EVALUATE ... END-EVALUATE` (`AstFacts.bug_risk_idioms`).
2. **Explicit Scope Terminators**: Always close compound statements explicitly with `END-IF`, `END-EVALUATE`, `END-PERFORM`, `END-READ`, `END-CALL`, and `END-COMPUTE` instead of relying on ambiguous period (`.`) termination.
3. **Cohesive Paragraphs, Sections & Header Comments**: Document every `PROGRAM-ID`, copybook (`.cpy`), and business-logic `SECTION`/`PARAGRAPH` with concise `*>` / `*` header comments explaining inputs, outputs, and file/DB side effects (`AstFacts.docstring_coverage_pct`), and keep paragraphs modular (`AstFacts.complex_functions`).
4. **Controlled `WORKING-STORAGE` & `LOCAL-STORAGE` Scope**: Avoid sprawling global `WORKING-STORAGE` flags mutated across unrelated paragraphs (`AstFacts.global_state_usages`); use `LOCAL-STORAGE` for reentrant subprograms and pass explicit `LINKAGE SECTION` structures between `CALL`ed subprograms. Do **NOT** penalize COBOL programs for lacking OOP classes or modern exception syntax.

## Evaluation Thresholds
- **`PASS`**: Zero `ALTER` / spaghetti `GO TO` jumps, consistent explicit `END-*` scope terminators, clear `PROGRAM-ID`/copybook comments, and cohesive `PERFORM` paragraphs.
- **`WARN`**: Isolated legacy `GO TO EXIT-PARA` patterns or oversized monolithic paragraphs without `LOCAL-STORAGE` isolation.
- **`FAIL`**: `ALTER` statements, pervasive `GO TO` spaghetti, period-terminated nested `IF` chains, or undocumented monolithic `PROCEDURE DIVISION`s.
