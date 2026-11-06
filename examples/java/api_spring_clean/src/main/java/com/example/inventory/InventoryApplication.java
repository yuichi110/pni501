package com.example.inventory;

import com.example.inventory.config.SupplierProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

/**
 * Spring Boot entry point for the warehouse inventory reservation microservice.
 */
@SpringBootApplication
@EnableConfigurationProperties(SupplierProperties.class)
public class InventoryApplication {

    /**
     * Launch the Spring Boot application context.
     *
     * @param args command-line startup arguments
     */
    public static void main(String[] args) {
        SpringApplication.run(InventoryApplication.class, args);
    }
}
