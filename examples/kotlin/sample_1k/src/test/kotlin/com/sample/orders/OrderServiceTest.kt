package com.sample.orders

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class OrderServiceTest {
    @Test
    fun testOrderScore() {
        val svc = OrderService(0.1)
        assertTrue(svc.computeOrderScore1(2, 10.0, 2) > 0.0)
    }

    @Test
    fun testZeroQuantityScore() {
        val svc = OrderService(0.1)
        assertEquals(0.0, svc.computeOrderScore1(0, 10.0, 1))
    }
}
