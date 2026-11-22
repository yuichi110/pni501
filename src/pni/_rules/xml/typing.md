# XSD / RELAX NG Schema & Namespace Contract Standards (XML)

## Core Principles
1. **Formal XSD (`*.xsd`) or RELAX NG (`*.rng`) Contracts**: Pair structured XML interchange/configuration documents with versioned XSD 1.1 / XSD 1.0 or RELAX NG schemas enforcing element order, cardinality (`minOccurs`/`maxOccurs`), numeric ranges, and string enumerations (`AstFacts.type_safety_coverage_pct`).
2. **Versioned Target Namespaces**: Declare explicit versioned `targetNamespace` URIs (e.g., `urn:acme:invoice:v1`) and `elementFormDefault="qualified"` in authored `.xsd` schemas to prevent element name collisions.
3. **Avoid `xs:any` / Unbounded Wildcards**: Minimize `<xs:any processContents="skip"/>` wildcards in core interchange schemas (`AstFacts.weak_type_usages`), and enforce explicit `maxLength` / `maxOccurs` bounds to mitigate payload DoS.
4. **DSL Exemption**: XML is a markup/schema format — evaluate contract rigor via XSD/RELAX NG definitions and namespace discipline rather than programming-language type rules.

## Evaluation Thresholds
- **`PASS`**: Versioned `xmlns`/`targetNamespace`, strict XSD/RNG bounds (`minOccurs`/`maxOccurs`), and minimal `xs:any` wildcards.
- **`WARN`**: Missing `xsi:schemaLocation` hints or loose unbounded string lengths.
- **`FAIL`**: Unvalidated XML interchange formats lacking schema contracts or conflicting namespace bindings.
