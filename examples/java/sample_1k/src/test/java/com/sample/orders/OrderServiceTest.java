package com.sample.orders;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.Test;

public class OrderServiceTest {
    @Test
    public void testComputeScore() {
        OrderService svc = new OrderService(0.1);
        assertTrue(svc.computeOrderScore1(2, 10.0, 1) > 0.0);
    }

    @Test
    public void testZeroQuantityReturnsZero() {
        OrderService svc = new OrderService(0.1);
        assertEquals(0.0, svc.computeOrderScore1(0, 10.0, 1));
    }
}
