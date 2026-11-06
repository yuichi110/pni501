package com.example.inventory.domain;

/**
 * Pure domain policy determining when warehouse stock requires supplier replenishment.
 */
public final class ReorderPolicy {

    private ReorderPolicy() {
    }

    /**
     * Determine whether an item's available stock has reached or fallen below its reorder point.
     *
     * @param item stock item snapshot to evaluate
     * @return true when supplier restock should be requested
     */
    public static boolean requiresRestock(StockItem item) {
        return item.availableUnits() <= item.reorderPoint();
    }

    /**
     * Calculate recommended replenishment quantity to restore healthy buffer stock.
     *
     * @param item stock item snapshot to evaluate
     * @param minimumBatch minimum supplier order batch size
     * @return positive restock unit quantity, or zero when restock is unnecessary
     */
    public static int recommendedOrderQuantity(StockItem item, int minimumBatch) {
        if (!requiresRestock(item)) {
            return 0;
        }
        int deficit = (item.reorderPoint() * 2) - item.availableUnits();
        return Math.max(Math.max(1, minimumBatch), deficit);
    }
}
