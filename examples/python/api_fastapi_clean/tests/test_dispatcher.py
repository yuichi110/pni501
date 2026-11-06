"""Unit tests for repository, webhook_client, and OrderDispatcherService."""

from __future__ import annotations

import asyncio

from order_dispatch.domain.models import CustomerTier, OrderLine, OrderRecord, OrderStatus
from order_dispatch.infra.repository import InMemoryOrderRepository
from order_dispatch.infra.webhook_client import AsyncWebhookClient
from order_dispatch.services.dispatcher import OrderDispatcherService


class _StubWebhookClient(AsyncWebhookClient):
    """Deterministic stub avoiding real network calls during unit tests."""

    def __init__(self, succeed: bool) -> None:
        super().__init__(endpoint_url="https://stub.internal/hook", timeout_sec=1.0)
        self._succeed = succeed

    async def notify_order_accepted(self, record: OrderRecord) -> bool:
        _ = record
        return self._succeed


def test_dispatcher_persists_dispatched_and_deferred_orders() -> None:
    """Verify OrderDispatcherService persists status transitions accurately."""
    repo = InMemoryOrderRepository()
    service_ok = OrderDispatcherService(repository=repo, webhook_client=_StubWebhookClient(succeed=True))
    placed = asyncio.run(
        service_ok.place_order(
            customer_id="cust-1",
            tier=CustomerTier.VIP,
            lines=[OrderLine(sku="SKU-1", quantity=1, unit_price_cents=2000)],
        )
    )
    assert placed.status == OrderStatus.DISPATCHED
    assert placed.total_cents == 1800
    assert service_ok.find_order(placed.order_id) == placed

    service_defer = OrderDispatcherService(repository=repo, webhook_client=_StubWebhookClient(succeed=False))
    deferred = asyncio.run(
        service_defer.place_order(
            customer_id="cust-2",
            tier=CustomerTier.STANDARD,
            lines=[OrderLine(sku="SKU-2", quantity=2, unit_price_cents=500)],
        )
    )
    assert deferred.status == OrderStatus.WEBHOOK_DEFERRED
