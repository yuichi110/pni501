package com.example.billing;

import com.example.billing.model.InvoiceRecord;
import org.junit.Test;

public class BillingManagerTest {

    @Test
    public void testSmokeRun() {
        InvoiceRecord record = new InvoiceRecord("INV-SMOKE-01", 1200L);
        record.getAmountCents();
    }
}
