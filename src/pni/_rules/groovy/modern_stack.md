# Modern Groovy 4 & JVM Stack Idioms (`groovy/modern_stack`)

## Core Principles
1. **Groovy 4 Modernization**: Migrate `org.codehaus.groovy` to `org.apache.groovy`, use `record` classes, `sealed` hierarchies, and switch expressions (`AstFacts.modernization_hints`).
2. **Safe XML / JSON Parsing**: Configure `XmlSlurper` / `XmlParser` with `disallow-doctype-decl` to block XXE (CWE-611; `AstFacts.dangerous_sinks`), and prefer `JsonSlurper` over Java serialization (`ObjectInputStream`).
3. **Hardened Network & Timeouts**: Never call `new URL(url).text` without explicit connect/read timeouts (`connectTimeout`, `readTimeout`; `AstFacts.missing_io_timeouts`).
4. **Structured Logging**: Use `@Slf4j` AST transformation instead of `println(...)` in production classes (`AstFacts.unstructured_logging`).
