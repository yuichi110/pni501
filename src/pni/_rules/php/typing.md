# Type Safety & Static Analysis Standards (PHP)

## Core Principles
1. **Mandatory `declare(strict_types=1);`**: Declare `declare(strict_types=1);` at the top of every PHP source file to prevent silent scalar type coercion bugs.
2. **Complete Parameter, Return & Property Types**: Provide explicit native PHP 8.2+ type declarations on all function/method parameters, return types (`void`, `never`, union/nullable types), and class properties.
3. **Value Objects, Enums & Readonly DTOs**: Prefer `readonly class` DTOs and native Backed `enum` types over untyped associative arrays (`array<string, mixed>`) and `mixed` parameters.
4. **Static Type Verification (PHPStan / Psalm)**: Enforce PHPStan (level 6–9) or Psalm in CI without unscoped `@phpstan-ignore-next-line` or `@psalm-suppress` directives.
