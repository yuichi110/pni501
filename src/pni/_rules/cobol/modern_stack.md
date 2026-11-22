# Modern COBOL (COBOL-2002 / 2014 / GnuCOBOL) & Migration-Readiness Idioms (`cobol/modern_stack`)

## Core Principles
1. **Modern Structured & Free-Format Hygiene**: Prefer explicit `END-*` terminators, `EVALUATE TRUE` over nested `IF ... ELSE IF`, `INITIALIZE` over uninitialized `WORKING-STORAGE` garbage, and intrinsic functions (`FUNCTION CURRENT-DATE`, `FUNCTION TRIM`, `FUNCTION NUMVAL`) over hand-rolled character loops (`AstFacts.modernization_hints`).
2. **Always Check `FILE STATUS` & `SQLCODE`**: Check `FILE STATUS` after every `OPEN`/`READ`/`WRITE`/`REWRITE`/`CLOSE` and check `SQLCODE` after every `EXEC SQL` statement rather than silently continuing on I/O failure (`AstFacts.bug_risk_idioms`).
3. **Safe Embedded SQL & Subprogram Calls**: Use parameterized host variables (`:WS-USER-ID`) in `EXEC SQL` instead of dynamic string-concatenated `EXEC SQL EXECUTE IMMEDIATE` (CWE-89; `AstFacts.dangerous_sinks`), and prefer static/validated `CALL` targets over untrusted dynamic program names.
4. **Strangler-Fig & API Modernization Readiness**: Isolate pure business calculation paragraphs from terminal/JCL/CICS I/O so core domain logic can be wrapped or migrated incrementally.
