# Modern Objective-C & Swift Interop Idioms (`objc/modern_stack`)

## Core Principles
1. **Modern Objective-C Literals & Subscripting**: Prefer `@[]`, `@{}`, `@(num)`, `arr[i]`, `@autoreleasepool {}`, and `dispatch_once` over legacy `[NSArray arrayWithObjects:..., nil]` and `@synchronized` singleton boilerplate (`AstFacts.modernization_hints`).
2. **Hardened Networking & Security**: Use `NSURLSession` with explicit `timeoutIntervalForRequest` (`AstFacts.missing_io_timeouts`) instead of removed `NSURLConnection`, enforce App Transport Security (never weaken TLS validation; `AstFacts.dangerous_sinks`), and store credentials in Keychain (`SecItem*`) rather than `NSUserDefaults`.
3. **Structured Logging**: Replace production `NSLog(...)` (slow, unredacted, leaks into system logs) with unified `os_log` (`os_log_t` with `%{private}@` redaction; `AstFacts.unstructured_logging`).
4. **Swift Interoperability Readiness**: Add `NS_SWIFT_NAME`, nullability annotations, and lightweight generics to public headers to support gradual Swift adoption.
