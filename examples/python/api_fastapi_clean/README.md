# order-dispatch

`order-dispatch` is a layered FastAPI + Pydantic v2 microservice that prices multi-line orders, persists fulfillment state via repository ports, and delivers non-blocking outbound webhooks with bounded timeouts.

## Quickstart Tutorial

```bash
uv sync
uv run uvicorn order_dispatch.main:create_app --factory --host 127.0.0.1 --port 8080
```

## Operations How-To Guide

### Configure Environment Variables (12-Factor III)
All runtime settings are validated at startup in `order_dispatch/settings.py`:
- `ORDER_DISPATCH_ENV`: Deployment tier (`dev`, `staging`, `prod`).
- `ORDER_DISPATCH_WEBHOOK_URL`: Partner fulfillment endpoint.
- `ORDER_DISPATCH_HTTP_TIMEOUT_SEC`: Outbound `httpx` timeout (default `5.0` seconds).

## HTTP API Reference

- `GET /healthz` -> `HealthResponse` readiness probe.
- `POST /v1/orders` -> `OrderResponse` validated order creation and dispatch receipt.
- `GET /v1/orders/{order_id}` -> `OrderResponse` lookup by identifier.

## Layered Architecture Explanation

```text
api (routes, schemas) -> services (dispatcher) -> domain (models, pricing)
                                               -> infra (repository, webhook_client)
```

Domain logic in `order_dispatch/domain/` has zero framework or network imports, ensuring pure deterministic unit testing.
