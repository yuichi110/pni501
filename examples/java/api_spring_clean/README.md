# inventory-service

`inventory-service` is a Spring Boot 3.3 + Java 21 microservice managing warehouse stock reservations and supplier restock notifications.

## Quickstart Tutorial

```bash
./mvnw test
./mvnw spring-boot:run
```

## Operations How-To Guide

### Configure Supplier Endpoint (`@ConfigurationProperties`)
Bind `inventory.supplier.base-url` and `inventory.supplier.timeout-seconds` via environment variables (`INVENTORY_SUPPLIER_BASE_URL`, `INVENTORY_SUPPLIER_TIMEOUT_SECONDS`).

## REST API Reference

- `GET /api/v1/items/{sku}`: Inspect current on-hand and reserved quantities.
- `POST /api/v1/items/{sku}/reserve`: Reserve units and trigger supplier restock when stock falls below threshold.

## Layered Architecture Explanation

`api` (`InventoryController`) -> `service` (`InventoryService`) -> `domain` (`StockItem`, `ReorderPolicy`) + `client` (`SupplierRestClient`) + `config` (`SupplierProperties`).
All Spring components use constructor dependency injection, immutable Java `record` DTOs, SLF4J structured logging, and explicit `java.net.http.HttpClient` timeouts.
