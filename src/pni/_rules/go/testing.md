# Testing Standards (Go)

## Core Principles
1. **Table-Driven Standard `testing`**: Write table-driven unit tests (`func TestXxx(t *testing.T)`) using `t.Run(...)` subtests co-located in `*_test.go` files alongside the package under test.
2. **Coverage Target**: Maintain statement coverage of 80% or higher (`go test -coverprofile=coverage.out ./...`) across core packages.
3. **Deterministic & Race-Free**: Isolate external network/database dependencies via narrow interfaces, mark helper functions with `t.Helper()`, and ensure tests pass under `-race`.
4. **Meaningful Assertions**: Verify both happy-path outputs and error branches (`t.Fatalf`, `t.Errorf`, `errors.Is`, `errors.As`, or `testify/require`).
