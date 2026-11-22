# Well-Formedness, XSD Validation & XSLT Testing Standards (XML)

## Core Principles
1. **Automated `xmllint` Well-Formedness & Schema CI Gate**: Run `xmllint --noout --nonet --schema <schema.xsd> <doc.xml>` (note `--nonet` guarantees zero unintended external network fetches!) in CI for all tracked XML/XSD documents.
2. **Valid & Invalid Schema Test Fixtures**: When authoring `.xsd`/`.rng` schemas or `.xsl` transforms, maintain positive fixtures (must pass) and negative/malformed/XXE fixtures (must be rejected cleanly; `AstFacts.test_functions_count`).
3. **XSLT Unit Testing (`XSpec`)**: Verify non-trivial XSLT stylesheets with `XSpec` or golden XML output comparisons (`diff` / XML-canonical comparison).
4. **DSL Exemption**: Evaluate XML verification via `xmllint --noout --nonet`, schema validation fixtures, and XSLT tests rather than code line-coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated `xmllint --noout --nonet` + XSD/RNG schema validation (and positive/negative fixtures for authored schemas).
- **`WARN`**: Well-formedness checked without XSD/RNG schema validation.
- **`FAIL`**: Zero automated XML validation allowing malformed XML or broken manifests into `main`.
