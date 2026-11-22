package com.sample.orders

class OrderServiceSpec extends munit.FunSuite {
  test("computes positive order score") {
    val svc = new OrderService(0.1)
    assert(svc.computeOrderScore1(2, 10.0, 2) > 0.0)
  }

  test("returns zero for non-positive quantity") {
    val svc = new OrderService(0.1)
    assertEquals(svc.computeOrderScore1(0, 10.0, 1), 0.0)
  }
}
