# Spring Boot Best Practices (`java/frameworks/spring_boot`)

## 1. Constructor Injection Over Field Injection
- Always use constructor injection (`private final OrderRepository repo;`) rather than `@Autowired` / `@Inject` field injection so components remain immutable and unit-testable without starting a Spring container.

## 2. Explicit Web Layer & DTO Separation
- Prefer explicit HTTP verb annotations (`@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`) over generic method-level `@RequestMapping`.
- Return dedicated immutable Java `record` DTOs from `@RestController` endpoints rather than exposing JPA `@Entity` classes directly.

## 3. Modern JDK & Configuration Hygiene
- Bind external configuration via `@ConfigurationProperties` records with Bean Validation (`@Validated`) rather than scattered `@Value` fields.
- Use `java.time` (`Instant`, `LocalDate`, `DateTimeFormatter`) instead of legacy `Date`, `Calendar`, or `SimpleDateFormat`.

## 4. Concurrency Precision: Shared Singleton State vs. Local Legacy APIs
- Strictly separate **active cross-request race conditions** (mutable instance fields on singleton `@RestController`/`@Service`/`@Component` beans or unsynchronized `static` collections like `static Map` mutated across requests) from **legacy API modernization debt** (method-local `new SimpleDateFormat(...)`, `new Vector()`, or unreferenced helper utilities). Never claim a method-local or uninvoked `SimpleDateFormat`/`Vector` causes an active concurrent race condition unless the instance itself is shared across threads.
