"""Order fulfillment application service coordinating pricing, storage, and webhooks."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Sequence

from order_dispatch.domain.models import CustomerTier, OrderLine, OrderRecord, OrderStatus
from order_dispatch.domain.pricing import compute_order_total_cents
from order_dispatch.infra.repository import OrderRepository
from order_dispatch.infra.webhook_client import AsyncWebhookClient

logger = logging.getLogger(__name__)


class OrderDispatcherService:
    """Stateless application service orchestrating order creation and dispatch."""

    def __init__(
        self,
        repository: OrderRepository,
        webhook_client: AsyncWebhookClient,
        vip_discount_rate: float = 0.10,
    ) -> None:
        """Initialize service with injected repository and webhook ports.

        Args:
            repository: Persistence adapter for OrderRecord objects.
            webhook_client: Async HTTP notifier for partner webhooks.
            vip_discount_rate: Loyalty discount rate applied to VIP customers.
        """
        self._repository: OrderRepository = repository
        self._webhook_client: AsyncWebhookClient = webhook_client
        self._vip_discount_rate: float = vip_discount_rate

    async def place_order(
        self,
        customer_id: str,
        tier: CustomerTier,
        lines: Sequence[OrderLine],
    ) -> OrderRecord:
        """Price, persist, and dispatch an order notification asynchronously.

        Args:
            customer_id: Authenticated or validated customer identifier.
            tier: Customer loyalty tier.
            lines: Validated order line items.

        Returns:
            OrderRecord: Finalized order aggregate with dispatch status.
        """
        subtotal, total = compute_order_total_cents(lines, tier, self._vip_discount_rate)
        order_id = f"ord-{uuid.uuid4().hex[:10]}"
        initial = OrderRecord(
            order_id=order_id,
            customer_id=customer_id,
            tier=tier,
            lines=tuple(lines),
            subtotal_cents=subtotal,
            total_cents=total,
            status=OrderStatus.ACCEPTED,
        )
        delivered = await self._webhook_client.notify_order_accepted(initial)
        final_status = OrderStatus.DISPATCHED if delivered else OrderStatus.WEBHOOK_DEFERRED
        final_record = OrderRecord(
            order_id=order_id,
            customer_id=customer_id,
            tier=tier,
            lines=tuple(lines),
            subtotal_cents=subtotal,
            total_cents=total,
            status=final_status,
        )
        self._repository.save(final_record)
        logger.info("Processed order %s with status=%s", order_id, final_status.value)
        return final_record

    def find_order(self, order_id: str) -> OrderRecord | None:
        """Retrieve an existing order aggregate by ID.

        Args:
            order_id: Unique order identifier.

        Returns:
            OrderRecord | None: Matching order aggregate if present.
        """
        return self._repository.get(order_id)
