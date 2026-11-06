package com.example.inventory.domain;

import java.time.Instant;

/**
 * Immutable warehouse stock item snapshot using Java 21 record semantics.
 *
 * @param sku unique warehouse stock-keeping unit code
 * @param onHand total physical units on warehouse shelves
 * @param reserved units currently allocated to open orders
 * @param reorderPoint minimum available threshold triggering restock
 * @param updatedAt UTC timestamp of most recent stock mutation
 */
public record StockItem(
        String sku,
        int onHand,
        int reserved,
        int reorderPoint,
        Instant updatedAt
) {

    /**
     * Compute unallocated stock currently available for new reservations.
     *
     * @return non-negative available unit count
     */
    public int availableUnits() {
        return Math.max(0, onHand - reserved);
    }

    /**
     * Return an updated StockItem reflecting an additional reservation.
     *
     * @param quantity positive number of units to reserve
     * @param now current UTC timestamp
     * @return new StockItem instance with incremented reserved count
     */
    public StockItem withAdditionalReservation(int quantity, Instant now) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Reservation quantity must be positive.");
        }
        if (quantity > availableUnits()) {
            throw new IllegalStateException("Insufficient available stock for SKU: " + sku);
        }
        return new StockItem(sku, onHand, reserved + quantity, reorderPoint, now);
    }
}
