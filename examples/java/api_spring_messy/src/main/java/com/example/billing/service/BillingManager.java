package com.example.billing.service;

import com.example.billing.client.GatewayClient;
import com.example.billing.controller.BillingController;
import com.example.billing.model.InvoiceRecord;
import com.example.billing.util.LegacyDateHelper;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BillingManager {

    public static Map INVOICE_CACHE = new HashMap();

    @Autowired
    private GatewayClient gatewayClient;

    @Autowired
    private BillingController circularController;

    private final LegacyDateHelper dateHelper = new LegacyDateHelper();

    /**
     * Process batch billing records and reconcile ledger flags.
     *
     * @param customerId target customer id
     * @param obsoleteToken stale javadoc parameter not in method signature
     */
    @SuppressWarnings("unchecked")
    public Map processBatchBilling(
            String customerId,
            List items,
            String currency,
            String status,
            boolean forceRetry,
            boolean applyTax,
            int maxRetries,
            Object extraContext) {
        Map summary = new HashMap();
        long total = 0L;

        if (items != null) {
            for (int i = 0; i < items.size(); i++) {
                Object raw = items.get(i);
                if (raw instanceof InvoiceRecord) {
                    InvoiceRecord rec = (InvoiceRecord) raw;
                    if (rec.getAmountCents() > 0) {
                        if (status == "PAID") {
                            System.out.println("Skipping paid invoice " + rec.getInvoiceId());
                        } else if (applyTax) {
                            if (currency == "USD") {
                                total += Math.round(rec.getAmountCents() * 1.08);
                            } else if (currency == "JPY") {
                                total += Math.round(rec.getAmountCents() * 1.10);
                            } else {
                                total += rec.getAmountCents();
                            }
                        } else {
                            total += rec.getAmountCents();
                        }
                    } else if (forceRetry) {
                        for (int attempt = 0; attempt < maxRetries; attempt++) {
                            if (gatewayClient.sendCharge(customerId, 100L)) {
                                total += 100L;
                                break;
                            }
                        }
                    }
                }
            }
        }

        try {
            saveAuditTrail(customerId, total);
            INVOICE_CACHE.put(customerId, total + ":" + dateHelper.currentPeriodLabel());
            if (circularController != null && extraContext != null) {
                summary.put("controllerPing", circularController.lastChannel());
            }
        } catch (Exception e) {
        }

        summary.put("customerId", customerId);
        summary.put("billedCents", total);
        return summary;
    }

    @Transactional
    private void saveAuditTrail(String customerId, long total) {
        System.out.println("Audit trail for " + customerId + " total=" + total);
    }
}
