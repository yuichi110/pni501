package com.example.billing.model;

/**
 * Simple invoice DTO providing a clean low-risk baseline module for heatmap contrast.
 */
public class InvoiceRecord {

    private final String invoiceId;
    private final long amountCents;

    /**
     * Construct an immutable InvoiceRecord.
     *
     * @param invoiceId unique invoice identifier
     * @param amountCents billed total in integer cents
     */
    public InvoiceRecord(String invoiceId, long amountCents) {
        this.invoiceId = invoiceId;
        this.amountCents = amountCents;
    }

    /**
     * Return unique invoice identifier.
     *
     * @return invoice identifier string
     */
    public String getInvoiceId() {
        return invoiceId;
    }

    /**
     * Return billed total in integer cents.
     *
     * @return amount in cents
     */
    public long getAmountCents() {
        return amountCents;
    }
}
