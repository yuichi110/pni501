"""Unit tests for schemas, settings, main app factory, and route handlers."""

from __future__ import annotations

from order_dispatch.api.routes import router
from order_dispatch.api.schemas import CreateOrderRequest, OrderLineInput, to_domain_lines
from order_dispatch.main import create_app
from order_dispatch.settings import ServiceSettings, load_settings


def test_schemas_and_app_factory_wiring() -> None:
    """Verify SKU normalization, settings loader, and FastAPI route registration."""
    req = CreateOrderRequest(
        customer_id="cust-100",
        lines=[OrderLineInput(sku="  item-abc ", quantity=3, unit_price_cents=400)],
    )
    domain_lines = to_domain_lines(req.lines)
    assert domain_lines[0].sku == "ITEM-ABC"
    assert domain_lines[0].quantity == 3

    cfg = load_settings()
    assert isinstance(cfg, ServiceSettings)
    app = create_app(cfg)
    route_paths = {getattr(r, "path", "") for r in router.routes}
    assert "/healthz" in route_paths
    assert "/v1/orders" in route_paths
    assert app.title == "order-dispatch"
