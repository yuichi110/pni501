# Testing & Coverage Standards (PHP)

## Core Principles
1. **Automated PHPUnit / Pest Suite**: Maintain deterministic automated unit and feature tests under `tests/` configured via `phpunit.xml` or `phpunit.xml.dist` (PHPUnit 10/11+ or Pest).
2. **Meaningful Assertions & Edge-Case Coverage**: Every test method (`test*` or `#[Test]`) must execute explicit assertions (`$this->assertSame(...)`, `$this->expectException(...)`, or Pest `expect(...)`) covering nominal paths, validation failures, and security boundaries.
3. **Offline Heretic Execution & PCOV Coverage**: Tests must run offline without live external databases or HTTP APIs (use in-memory `pdo_sqlite`, fakes, or mocks) and target >= 80% statement/branch coverage measured with `pcov`.
