package com.example.inventory;

import com.example.inventory.api.InventoryController;
import com.example.inventory.client.SupplierRestClient;
import com.example.inventory.config.SupplierProperties;
import com.example.inventory.domain.StockItem;
import com.example.inventory.service.InventoryService;
import java.time.Instant;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;

/**
 * JUnit 5 unit tests for InventoryService, InventoryController, SupplierProperties, and application wiring.
 */
class InventoryServiceTest {

    private static final class StubSupplierClient extends SupplierRestClient {

        private int restockCalls;

        StubSupplierClient(SupplierProperties properties) {
            super(properties);
        }

        @Override
        public boolean requestRestock(String sku, int quantity) {
            this.restockCalls += 1;
            return quantity > 0 && !sku.isEmpty();
        }
    }

    @Test
    void shouldReserveUnitsAndInvokeSupplierWhenLow() {
        SupplierProperties props = SupplierProperties.defaults();
        StubSupplierClient stubClient = new StubSupplierClient(props);
        InventoryService service = new InventoryService(stubClient, props);
        InventoryController controller = new InventoryController(service);
        InventoryApplication app = new InventoryApplication();
        Assertions.assertNotNull(app);

        service.upsertItem(new StockItem("SKU-200", 20, 0, 10, Instant.EPOCH));
        ResponseEntity<StockItem> response = controller.reserveItem("SKU-200", 12);
        StockItem body = response.getBody();
        Assertions.assertNotNull(body);
        Assertions.assertEquals(8, body.availableUnits());
        Assertions.assertEquals(1, stubClient.restockCalls);
    }
}
