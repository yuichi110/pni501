package com.example.inventory.api;

import com.example.inventory.domain.StockItem;
import com.example.inventory.service.InventoryService;
import jakarta.validation.constraints.Min;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing typed warehouse inventory lookup and reservation endpoints.
 */
@RestController
@RequestMapping("/api/v1/items")
public class InventoryController {

    private final InventoryService inventoryService;

    /**
     * Construct InventoryController with constructor-injected InventoryService.
     *
     * @param inventoryService application service managing stock reservations
     */
    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    /**
     * Retrieve current stock levels for a single SKU.
     *
     * @param sku stock-keeping unit path variable
     * @return 200 OK with StockItem or 404 Not Found
     */
    @GetMapping("/{sku}")
    public ResponseEntity<StockItem> getItem(@PathVariable String sku) {
        return inventoryService.findBySku(sku)
                .map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    /**
     * Reserve units for a SKU.
     *
     * @param sku stock-keeping unit path variable
     * @param quantity positive reservation unit count
     * @return 200 OK with updated StockItem
     */
    @PostMapping("/{sku}/reserve")
    public ResponseEntity<StockItem> reserveItem(
            @PathVariable String sku,
            @RequestParam @Min(1) int quantity
    ) {
        // TODO(security): Require OAuth2 JWT resource-server scope check before external ingress exposure.
        StockItem updated = inventoryService.reserveStock(sku, quantity);
        return ResponseEntity.ok(updated);
    }
}
