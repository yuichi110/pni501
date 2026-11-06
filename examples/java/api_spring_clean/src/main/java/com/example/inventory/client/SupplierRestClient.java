package com.example.inventory.client;

import com.example.inventory.config.SupplierProperties;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Outbound HTTP adapter notifying upstream suppliers with explicit connection and request timeouts.
 */
@Component
public class SupplierRestClient {

    private static final Logger LOGGER = LoggerFactory.getLogger(SupplierRestClient.class);

    private final HttpClient httpClient;
    private final SupplierProperties properties;

    /**
     * Construct a SupplierRestClient with bounded connectTimeout from SupplierProperties.
     *
     * @param properties externalized supplier endpoint and timeout settings
     */
    public SupplierRestClient(SupplierProperties properties) {
        this.properties = properties;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(Math.max(1, properties.timeoutSeconds())))
                .build();
    }

    /**
     * Send a JSON restock request to the configured supplier endpoint.
     *
     * @param sku stock-keeping unit identifier to replenish
     * @param quantity number of units requested
     * @return true if the supplier accepted the restock request with 2xx status
     */
    public boolean requestRestock(String sku, int quantity) {
        String body = "{\"sku\":\"" + sku + "\",\"quantity\":" + quantity + "}";
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(properties.baseUrl() + "/v1/restock"))
                .timeout(Duration.ofSeconds(Math.max(1, properties.timeoutSeconds())))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(body))
                .build();
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() >= 200 && response.statusCode() < 300;
        } catch (IOException exc) {
            LOGGER.warn("Supplier restock call failed for sku={}: {}", sku, exc.getMessage());
            return false;
        } catch (InterruptedException exc) {
            Thread.currentThread().interrupt();
            LOGGER.warn("Supplier restock interrupted for sku={}", sku);
            return false;
        }
    }
}
