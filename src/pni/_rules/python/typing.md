# Typing Standards (Python)

## Core Principles
1. **Mandatory Type Annotations**: All public functions and methods must have complete parameter and return type hints (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
2. **Modern PEP 585/604 Syntax**: Use `from __future__ import annotations`, built-in generic collections (`list[str]`, `dict[str, int]`, `tuple[int, ...]`), and PEP 604 union syntax (`X | Y`, `X | None`) rather than legacy `typing.List`, `typing.Union`, or `typing.Optional`.
3. **Minimize `Any` & Escape Hatches**: Avoid `Any` (`AstFacts.weak_type_usages`) and bare `# type: ignore` comments (`AstFacts.unscoped_type_ignores`); model contracts with `Protocol`, `TypeVar`, TypedDict, or Pydantic models, and scope any unavoidable ignore with a specific error code.
4. **Static Type Checking**: Pass static type verification (e.g., Ty, Pyright, or mypy) with zero errors and ship `py.typed` for libraries (`ProjectFacts.has_type_marker`).

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 90%`, `unscoped_type_ignores == 0`, and minimal/justified `weak_type_usages`.
- **`WARN`**: `type_safety_coverage_pct` between `70%` and `89.9%`, or isolated `Any` / bare `# type: ignore` occurrences.
- **`FAIL`**: `type_safety_coverage_pct < 70%` or widespread untyped public APIs / blanket type-ignore suppressions.
