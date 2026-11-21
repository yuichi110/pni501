# Generic Testing & Verification Standards

## Evaluation Criteria (`AstFacts` & `RuntimeFacts`)
- **Hermetic Tests**: Automated tests must run deterministically without external network or production database dependencies.
- **Real Assertions**: Every test case must contain explicit assertions (`assertion_free_tests == 0`).
- **Module Coverage**: Critical domain modules should have corresponding automated unit/integration test coverage (`module_test_coverage_pct >= 70%` for production services/libraries).
