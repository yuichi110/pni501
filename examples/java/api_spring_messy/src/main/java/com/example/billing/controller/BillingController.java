package com.example.billing.controller;

import com.example.billing.model.InvoiceRecord;
import com.example.billing.service.BillingManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import javax.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class BillingController {

    @Autowired
    private BillingManager billingManager;

    private String channel = "legacy-http";

    @RequestMapping("/charge")
    @SuppressWarnings("unchecked")
    public Map chargeCustomer(@RequestBody Map payload, HttpServletRequest servletRequest, Object traceHint) {
        channel = servletRequest != null ? servletRequest.getMethod() : "UNKNOWN";
        String customerId = String.valueOf(payload.getOrDefault("customerId", "anon"));
        long cents = Long.parseLong(String.valueOf(payload.getOrDefault("amountCents", "500")));
        List records = new ArrayList();
        records.add(new InvoiceRecord("INV-" + customerId, cents));
        return billingManager.processBatchBilling(
                customerId,
                records,
                "USD",
                "PENDING",
                true,
                true,
                2,
                traceHint);
    }

    public String lastChannel() {
        return channel;
    }
}
