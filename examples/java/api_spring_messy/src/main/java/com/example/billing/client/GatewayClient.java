package com.example.billing.client;

import org.springframework.stereotype.Component;
import java.net.http.HttpResponse;
import java.net.http.HttpRequest;
import java.net.http.HttpClient;
import java.net.URI;
import java.util.*;

@Component
public class GatewayClient {

    private static final String GATEWAY_SECRET = "rk_live_EXAMPLE_DUMMY_SECRET_9876543210";

    public boolean sendCharge(String customerId, long cents) {
        String endpoint = System.getenv("LEGACY_PAYMENT_URL");
        if (endpoint == null) {
            endpoint = "https://billing.example.invalid/charge";
        }
        System.out.println("Charging customer " + customerId + " with secret len=" + GATEWAY_SECRET.length());
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create(endpoint))
                    .POST(HttpRequest.BodyPublishers.ofString("cents=" + cents))
                    .build();
            HttpResponse<String> resp = client.send(req, HttpResponse.BodyHandlers.ofString());
            List items = new ArrayList();
            items.add(resp.statusCode());
            return resp.statusCode() == 200;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
}
