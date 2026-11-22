# Data Representation, `PIC` Precision & `REDEFINES` Standards (COBOL)

## Core Principles
1. **Explicit Signed Fixed-Point Precision (`PIC` / `COMP-3`)**: Use explicit signed packed decimal (`PIC S9(n)V99 COMP-3` / `USAGE PACKED-DECIMAL`) for monetary and accounting values rather than binary floating-point (`COMP-1`/`COMP-2`) or unsigned `PIC 9` fields when negative balances are possible, and guard arithmetic with `ON SIZE ERROR` / `ROUNDED` (`AstFacts.bug_risk_idioms`).
2. **Level-88 Condition Names & Symbolic Constants**: Define `88`-level condition names (`88 STATUS-ACTIVE VALUE 'A'.`) instead of scattering magic string/numeric literals throughout `PROCEDURE DIVISION`.
3. **Safe `REDEFINES` & Table Bounds (`OCCURS`)**: Minimize overlapping `REDEFINES` unions (and validate discriminating tags before reading redefined layouts); always guard `OCCURS` table subscripts/indexes against out-of-bounds access (CWE-125/CWE-787) and prefer `INDEXED BY` + `SEARCH`/`SEARCH ALL`.
4. **Validated `LINKAGE SECTION` & `COPY` Contracts**: Share record layouts across `CALL` boundaries via canonical `.cpy` copybooks so caller and callee `PIC` definitions never drift (`AstFacts.type_safety_issues`).

## Evaluation Thresholds
- **`PASS`**: Clean `.cpy` shared record layouts, signed `COMP-3` financial precision with `ON SIZE ERROR`, `88`-level domain flags, and bounds-checked `OCCURS` access.
- **`WARN`**: Isolated magic literals or missing `ON SIZE ERROR` guards on non-critical counters.
- **`FAIL`**: Unchecked `OCCURS` buffer overruns, floating-point money calculations, mismatched `CALL` / `LINKAGE SECTION` `PIC` sizes, or unsafe untagged `REDEFINES`.
