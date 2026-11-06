package com.example.inventory.service;

import com.example.inventory.client.SupplierRestClient;
import com.example.inventory.config.SupplierProperties;
import com.example.inventory.domain.ReorderPolicy;
import com.example.inventory.domain.StockItem;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Application service coordinating stock reservations and supplier restock triggers.
 */
@Service
public class InventoryService {

    private static final Logger LOGGER = LoggerFactory.getLogger(InventoryService.class);

    private final Map<String, StockItem> inventoryStore = new ConcurrentHashMap<>();
    private final SupplierRestClient supplierClient;
    private final SupplierProperties properties;

    /**
     * Construct InventoryService using explicit constructor dependency injection.
     *
     * @param supplierClient outbound HTTP client for supplier restock orders
     * @param properties validated supplier configuration properties
     */
    public InventoryService(SupplierRestClient supplierClient, SupplierProperties properties) {
        this.supplierClient = supplierClient;
        this.properties = properties;
    }

    /**
     * Register or replace a StockItem snapshot in the warehouse store.
     *
     * @param item stock item snapshot to store
     */
    public void upsertItem(StockItem item) {
        inventoryStore.put(item.sku(), item);
    }

    /**
     * Look up a StockItem by SKU identifier.
     *
     * @param sku warehouse stock-keeping unit code
     * @return Optional containing the StockItem when present
     */
    public Optional<StockItem> findBySku(String sku) {
        return Optional.ofNullable(inventoryStore.get(sku));
    }

    /**
     * Reserve units for a SKU and trigger supplier replenishment if stock drops below threshold.
     *
     * @param sku warehouse stock-keeping unit code
     * @param quantity positive number of units to reserve
     * @return updated StockItem snapshot after reservation
     */
    public StockItem reserveStock(String sku, int quantity) {
        StockItem existing = inventoryStore.get(sku);
        if (existing == null) {
            throw new IllegalArgumentException("Unknown SKU: " + sku);
        }
        StockItem updated = existing.withAdditionalReservation(quantity, Instant.now());
        inventoryStore.put(sku, updated);

        int restockQty = ReorderPolicy.recommendedOrderQuantity(updated, properties.defaultReorderBatch());
        if (restockQty > 0) {
            boolean notified = supplierClient.requestRestock(sku, restockQty);
            LOGGER.info("Triggered restock for sku={}, qty={}, accepted={}", sku, restockQty, notified);
        }
        return updated;
    }
}
