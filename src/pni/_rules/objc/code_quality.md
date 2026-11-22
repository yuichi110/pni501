# Code Quality Standards (Objective-C)

## Core Principles
1. **ARC Memory Safety & Retain-Cycle Prevention**: Use Automatic Reference Counting (ARC) everywhere (flag legacy MRC `retain`/`release`/`autorelease` as modernization debt), declare delegate properties `weak` (never `strong` or `assign` for objects), use `copy` on `NSString`/block/collection properties, and capture `__weak typeof(self) weakSelf = self;` inside escaping blocks (`AstFacts.bug_risk_idioms`).
2. **Eliminate Format-String, C-Buffer & Unsafe Deserialization Sinks**: Never pass non-literal strings directly as format arguments (`NSLog(userStr)`, `[NSString stringWithFormat:userStr]`; CWE-134), ban unsafe C functions (`strcpy`/`sprintf`/`gets`), and replace deprecated `NSKeyedUnarchiver` without `NSSecureCoding` (`requiresSecureCoding = YES`; CWE-502; `AstFacts.dangerous_sinks`).
3. **Header Hygiene, Class Prefixes & Documentation**: Prefix public Objective-C classes/categories (`XYZMyClass` / `xyz_methodName`) to avoid flat-namespace collisions, use `#import` and `@class` forward declarations in `.h` headers, and document public APIs with HeaderDoc/Doxygen comments (`/** ... */`; `AstFacts.docstring_coverage_pct`).
4. **Error Propagation & Bounded Complexity**: Propagate recoverable failures via `NSError **` out-parameters (guard `if (error != NULL)` before dereferencing) rather than `@throw` exceptions, avoid mutable global singletons (`AstFacts.global_state_usages`), and keep methods concise (`AstFacts.complex_functions`).

## Evaluation Thresholds
- **`PASS`**: ARC-clean ownership (`weak` delegates, `copy` strings/blocks), zero format-string/insecure-archiver CWE sinks, HeaderDoc coverage `>= 80%`, and `NSError **` discipline.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, missing `copy` on minor `NSString` properties, or isolated method complexity.
- **`FAIL`**: Format-string vulnerabilities, insecure `NSKeyedUnarchiver` deserialization, strong delegate retain cycles, or unchecked C buffer sinks.
