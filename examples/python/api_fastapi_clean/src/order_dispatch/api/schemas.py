"""Pydantic v2 request and response DTOs for the order_dispatch HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from order_dispatch.domain.models import CustomerTier, OrderLine, OrderRecord, OrderStatus


class OrderLineInput(BaseModel):
    """Validated line-item payload within CreateOrderRequest."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0, le=1000)
    unit_price_cents: int = Field(ge=0, le=10_000_000)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        """Strip surrounding whitespace and uppercase SKU codes.

        Args:
            value: Raw SKU string.

        Returns:
            str: Trimmed uppercase SKU identifier.
        """
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("sku must not be blank.")
        return cleaned


class CreateOrderRequest(BaseModel):
    """Inbound payload for creating and dispatching a new order."""

    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=64)
    tier: CustomerTier = CustomerTier.STANDARD
    lines: list[OrderLineInput] = Field(min_length=1, max_length=100)


class OrderResponse(BaseModel):
    """Outbound HTTP representation of an OrderRecord."""

    model_config = ConfigDict(frozen=True)

    order_id: str
    customer_id: str
    tier: CustomerTier
    subtotal_cents: int
    total_cents: int
    status: OrderStatus


class HealthResponse(BaseModel):
    """Readiness probe payload for SRE health monitoring."""

    model_config = ConfigDict(frozen=True)

    service: str
    environment: str
    status: str


def to_domain_lines(items: list[OrderLineInput]) -> list[OrderLine]:
    """Convert validated API line inputs into pure domain OrderLine objects.

    Args:
        items: Validated API line-item DTOs.

    Returns:
        list[OrderLine]: Domain value objects.
    """
    return [OrderLine(sku=i.sku, quantity=i.quantity, unit_price_cents=i.unit_price_cents) for i in items]


def to_order_response(record: OrderRecord) -> OrderResponse:
    """Project a domain OrderRecord onto an HTTP OrderResponse DTO.

    Args:
        record: Domain order aggregate.

    Returns:
        OrderResponse: Serialized API response model.
    """
    return OrderResponse(
        order_id=record.order_id,
        customer_id=record.customer_id,
        tier=record.tier,
        subtotal_cents=record.subtotal_cents,
        total_cents=record.total_cents,
        status=record.status,
    )
