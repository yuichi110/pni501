# Code Quality Standards (Java)

## Core Principles
1. **Google Java Style & Static Analysis**: Adhere to Google Java Style Guide and enforce Checkstyle / SpotBugs / ErrorProne checks.
2. **Javadoc Documentation**: Provide clear Javadoc (`/** ... */`) for all public classes, interfaces, records, enums, and public non-`@Override` methods.
3. **Naming Conventions**: Use `PascalCase` for types, `camelCase` for methods and fields, `UPPER_SNAKE_CASE` for `static final` constants, and lowercase reverse-domain names for packages.
4. **Immutability & Cohesion**: Prefer `final` fields, Java `record` value types, concise methods (<= 50 lines), and zero mutable `static` state.
