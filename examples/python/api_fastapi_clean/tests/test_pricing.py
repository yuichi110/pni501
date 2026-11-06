"""Unit tests for order_dispatch.domain.models and order_dispatch.domain.pricing."""

from __future__ import annotations

import pytest

from order_dispatch.domain.models import CustomerTier, OrderLine
from order_dispatch.domain.pricing import PricingError, calculate_subtotal_cents, compute_order_total_cents


def test_pricing_standard_and_vip_discounts() -> None:
    """Verify integer-cents subtotal and VIP discount calculation."""
    lines = [
        OrderLine(sku="BOOK-01", quantity=2, unit_price_cents=1500),
        OrderLine(sku="PEN-02", quantity=1, unit_price_cents=500),
    ]
    assert calculate_subtotal_cents(lines) == 3500
    assert compute_order_total_cents(lines, CustomerTier.STANDARD) == (3500, 3500)
    assert compute_order_total_cents(lines, CustomerTier.VIP, vip_discount_rate=0.10) == (3500, 3150)


def test_pricing_rejects_empty_or_invalid_inputs() -> None:
    """Verify domain PricingError guards on empty lines or out-of-range discounts."""
    with pytest.raises(PricingError):
        calculate_subtotal_cents([])

    with pytest.raises(PricingError):
        compute_order_total_cents(
            [OrderLine(sku="BAD", quantity=0, unit_price_cents=100)],
            CustomerTier.STANDARD,
        )
