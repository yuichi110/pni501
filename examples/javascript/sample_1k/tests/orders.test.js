import assert from "node:assert/strict";
import { test } from "node:test";
import { OrderService } from "../src/orders.js";

test("computes positive order score", () => {
  const svc = new OrderService(0.1);
  assert.ok(svc.computeOrderScore1({ quantity: 2, unitPrice: 10, tier: 2 }) > 0);
});

test("returns zero for non-positive quantity", () => {
  const svc = new OrderService(0.1);
  assert.equal(svc.computeOrderScore1({ quantity: 0, unitPrice: 10, tier: 1 }), 0);
});
