# Testing Standards (Java)

## Core Principles
1. **JUnit 5 Framework**: Use JUnit Jupiter (`@Test`, `@ParameterizedTest`, `Assertions.assertThrows`) for unit and integration testing.
2. **Coverage Target**: Maintain line and branch coverage of 80% or higher (verified via JaCoCo) across core packages.
3. **Deterministic & Isolated**: Isolate external I/O and collaborators using interfaces, fakes, or Mockito without live network or shared static state dependencies.
4. **Standard Package Mirror Layout**: Place unit tests under `src/test/java/` mirroring the `src/main/java/` package hierarchy (`*Test.java` / `*Tests.java`).
