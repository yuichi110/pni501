package com.example.inventory;

import com.example.inventory.domain.ReorderPolicy;
import com.example.inventory.domain.StockItem;
import java.time.Instant;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * JUnit 5 unit tests for StockItem and ReorderPolicy domain logic.
 */
class ReorderPolicyTest {

    @Test
    void shouldTriggerRestockWhenAvailableDropsBelowReorderPoint() {
        StockItem healthy = new StockItem("SKU-100", 50, 10, 15, Instant.EPOCH);
        Assertions.assertFalse(ReorderPolicy.requiresRestock(healthy));
        Assertions.assertEquals(0, ReorderPolicy.recommendedOrderQuantity(healthy, 25));

        StockItem depleted = healthy.withAdditionalReservation(30, Instant.EPOCH);
        Assertions.assertEquals(10, depleted.availableUnits());
        Assertions.assertTrue(ReorderPolicy.requiresRestock(depleted));
        Assertions.assertEquals(25, ReorderPolicy.recommendedOrderQuantity(depleted, 25));
    }
}
