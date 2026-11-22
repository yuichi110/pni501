# Code Quality & XXE/Security Standards (XML)

## Core Principles
1. **Eliminate External Entities (`<!DOCTYPE>` / `<!ENTITY>`) & XXE Vectors**: Forbid external DTD/entity declarations (`<!ENTITY ... SYSTEM "...">`, parameter entities, and recursive entity expansion / Billion Laughs DoS; CWE-611 / CWE-776; `AstFacts.dangerous_sinks`) in data/config XML documents, and ensure consuming parsers disable DTDs (`disallow-doctype-decl`).
2. **Zero Hardcoded Credentials or Debug Flags in Manifests**: Never commit plaintext passwords, keystore passwords, or tokens inside `settings.xml`, `web.xml`, `applicationContext.xml`, `Web.config`, or `AndroidManifest.xml` (`AstFacts.hardcoded_secrets`), and disable production debug flags (`android:debuggable="false"`, `android:allowBackup="false"`, `android:usesCleartextTraffic="false"`).
3. **Well-Formed UTF-8 Encoding & Explicit Namespaces**: Start documents with `<?xml version="1.0" encoding="UTF-8"?>`, declare explicit `xmlns` and `xsi:schemaLocation` attributes on root elements, and keep consistent 2- or 4-space formatting (`xmllint --format`).
4. **Prevent XSLT / XPath Injection**: When authoring `.xsl`/`.xslt` stylesheets, avoid `disable-output-escaping="yes"` on untrusted values (XSS CWE-79) and external `document()` fetches.

## Evaluation Thresholds
- **`PASS`**: Well-formed UTF-8 XML, zero `<!ENTITY SYSTEM>` / XXE vectors, zero committed secrets or insecure debug flags, and explicit `xmlns` / `schemaLocation`.
- **`WARN`**: Missing `xsi:schemaLocation` or inconsistent formatting/indentation.
- **`FAIL`**: External entity / DTD injection constructs, hardcoded passwords/keys in XML configs, or `android:debuggable="true"` / `usesCleartextTraffic="true"` in release manifests.
