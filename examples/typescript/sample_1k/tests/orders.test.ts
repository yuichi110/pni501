import { expect, test } from "vitest";
import { OrderService } from "../src/orders";

test("computes positive order score", () => {
  const svc = new OrderService(0.1);
  expect(svc.computeOrderScore1({ id: "1", quantity: 2, unitPrice: 10, tier: 2 })).toBeGreaterThan(0);
});

test("returns zero for non-positive quantity", () => {
  const svc = new OrderService(0.1);
  expect(svc.computeOrderScore1({ id: "2", quantity: 0, unitPrice: 10, tier: 1 })).toBe(0);
});
