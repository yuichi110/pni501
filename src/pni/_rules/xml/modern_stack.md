# Modern XML, Safe Parsing & Interop Idioms (`xml/modern_stack`)

## Core Principles
1. **Safe Parser Guidance (`defusedxml` / `FEATURE_SECURE_PROCESSING`)**: Ensure services consuming XML files use XXE-hardened parsers (`defusedxml` in Python, `XMLConstants.FEATURE_SECURE_PROCESSING` + `disallow-doctype-decl` in Java, `XmlReaderSettings { DtdProcessing = Prohibit }` in .NET; `AstFacts.dangerous_sinks`).
2. **Prefer Structured Modern Formats for New Configs**: Keep XML where standards require it (Maven, MSBuild, Android, SVG, SAML, SOAP, DocBook, JUnit/Cobertura/JaCoCo reports), and prefer JSON/TOML/YAML/Protobuf for net-new greenfield internal configuration (`AstFacts.modernization_hints`).
3. **Hardened SVG Security**: Treat untrusted `.svg` XML assets as active content (strip `<script>`, `onload`, and external `<use href>` handlers before inline rendering).
4. **UTF-8 & Canonical Formatting**: Standardize on UTF-8 without BOM and consistent indentation for clean `git diff` history.
