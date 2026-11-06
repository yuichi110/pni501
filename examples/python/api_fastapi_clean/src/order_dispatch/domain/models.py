"""Pure domain entities and value objects for order fulfillment."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CustomerTier(StrEnum):
    """Supported customer loyalty tiers."""

    STANDARD = "standard"
    VIP = "vip"


class OrderStatus(StrEnum):
    """Lifecycle states of a customer order."""

    ACCEPTED = "accepted"
    DISPATCHED = "dispatched"
    WEBHOOK_DEFERRED = "webhook_deferred"


@dataclass(frozen=True)
class OrderLine:
    """Immutable line item inside a customer order."""

    sku: str
    quantity: int
    unit_price_cents: int


@dataclass(frozen=True)
class OrderRecord:
    """Persisted domain aggregate representing a priced and dispatched order."""

    order_id: str
    customer_id: str
    tier: CustomerTier
    lines: tuple[OrderLine, ...]
    subtotal_cents: int
    total_cents: int
    status: OrderStatus
