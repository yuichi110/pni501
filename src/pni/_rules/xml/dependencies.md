# Schema Catalog & XML Manifest Dependency Standards (XML)

## Core Principles
1. **Local XML Catalogs Over Live Remote Schema Fetches**: Resolve external XSD/DTD references through local vendored schemas or OASIS XML Catalogs (`catalog.xml`) so validation runs deterministically offline without live HTTP/HTTPS schema fetches (`ProjectFacts.unpinned_dependencies`).
2. **HTTPS-Only Namespace & Schema Locations**: Never fetch live schemas over plaintext `http://` at runtime (MITM tampering risk); pin immutable versioned schema files locally.
3. **Zero-Lockfile Exemption**: Standalone XML/XSD schema repositories do **not** use npm-style lockfiles (when XML is a Maven `pom.xml` or `.csproj`, follow `java/dependencies` or `csharp/dependencies`).
4. **Build & Manifest Auditing**: Audit XML-based manifests (`pom.xml`, `*.csproj`, `AndroidManifest.xml`, `phpunit.xml`) with Trivy and secret scanners in CI.

## Evaluation Thresholds
- **`PASS`**: Offline-resolvable local/catalog schemas, zero plaintext runtime schema downloads, and clean manifest security hygiene.
- **`WARN`**: Remote HTTPS `schemaLocation` URLs without local catalog fallback.
- **`FAIL`**: Live `http://` DTD/XSD network fetches during parsing or committed Maven/NuGet credential files (`settings.xml` passwords).
