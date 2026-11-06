package com.example.inventory.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Centralized externalized configuration properties for outbound supplier integration.
 *
 * @param baseUrl supplier partner base URL
 * @param timeoutSeconds bounded HTTP request timeout in seconds
 * @param defaultReorderBatch default restock quantity requested from supplier
 */
@ConfigurationProperties(prefix = "inventory.supplier")
public record SupplierProperties(
        String baseUrl,
        int timeoutSeconds,
        int defaultReorderBatch
) {

    /**
     * Create default supplier properties with safe local timeouts.
     *
     * @return default SupplierProperties instance
     */
    public static SupplierProperties defaults() {
        return new SupplierProperties("https://supplier.internal/api", 5, 50);
    }
}
