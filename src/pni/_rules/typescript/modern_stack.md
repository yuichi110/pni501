# Modern TypeScript & Node/Frontend Ecosystem Standards (`typescript/modern_stack`)

## Core Principles
1. **Standard ES Modules (ESM)**: Prefer native ES Modules (`"type": "module"`, `import`/`export`) over legacy CommonJS `require()` / `module.exports` (`AstFacts.modernization_hints`).
2. **Explicit HTTP & CORS Security (Express / Fastify / Hono / NestJS)**: Never deploy unrestricted `cors()` allowing all origins (`AstFacts.framework_issues`); configure an explicit origin allowlist, schema validation (`zod`/`valibot`), and explicit `AbortSignal.timeout(...)` on outbound `fetch`/HTTP requests (`AstFacts.missing_io_timeouts`).
3. **React & Next.js Boundary Hygiene**: Use stable entity identifiers rather than array indices (`key={index}`) for React list rendering, and never reference server-only `process.env.<SECRET>` variables (anything other than `NODE_ENV` or `NEXT_PUBLIC_*`) inside `'use client'` modules (`AstFacts.framework_issues`).
4. **Structured Logging & Modern Node LTS**: Target Node 20/22+ LTS and emit structured logs (`pino`/`winston`) rather than raw `console.log()` in production services (`AstFacts.unstructured_logging`).
