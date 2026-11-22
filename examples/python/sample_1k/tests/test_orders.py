"""Unit tests for orders."""
from sample_app.orders import OrderRecord, OrderService

def test_order_score() -> None:
    svc = OrderService()
    rec = OrderRecord('ord-1', 2, 50.0, 2)
    assert svc.compute_order_score_1(rec) > 0
