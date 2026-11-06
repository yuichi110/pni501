# order-fulfillment-api

Strict PHP 8.3 order fulfillment API microservice structured around immutable `readonly` DTOs, constructor dependency injection, parameterized PDO persistence, and constant-time HMAC webhook verification.

## Architecture Overview

- **`public/index.php` & `routes/api.php`**: Minimal HTTP front controller and Sanctum-guarded API route definitions (`/up`, `/healthz`, `GET /api/orders`, `POST /api/orders`).
- **`app/DTO/OrderPayload.php`**: Immutable `final readonly` input schema enforcing SKU format and positive quantity bounds.
- **`app/Models/OrderRecord.php`**: Domain entity with explicit `$fillable` allow-listing.
- **`app/Repositories/OrderRepository.php`**: Parameterized PDO SQLite repository (`PDO::ERRMODE_EXCEPTION`, `prepare()` + `execute()`).
- **`app/Services/OrderFulfillmentService.php`**: Domain service calculating totals and validating webhook signatures via `hash_equals()`.
- **`app/Http/Controllers/OrderController.php`**: Thin HTTP controller delegating to `OrderFulfillmentService`.

## Running Tests & Quality Checks

```bash
composer install
vendor/bin/phpunit --coverage-clover build/clover.xml
```
