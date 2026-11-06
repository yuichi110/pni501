"""Async outbound webhook client enforcing explicit SRE timeouts."""

from __future__ import annotations

import logging

import httpx

from order_dispatch.domain.models import OrderRecord

logger = logging.getLogger(__name__)


class AsyncWebhookClient:
    """Non-blocking HTTP webhook notifier backed by httpx.AsyncClient."""

    def __init__(self, endpoint_url: str, timeout_sec: float = 5.0) -> None:
        """Initialize webhook client with bounded request timeout.

        Args:
            endpoint_url: Target partner webhook URL.
            timeout_sec: Maximum request duration in seconds.
        """
        self._endpoint_url: str = endpoint_url
        self._timeout_sec: float = timeout_sec

    async def notify_order_accepted(self, record: OrderRecord) -> bool:
        """Deliver order acceptance event asynchronously with explicit timeout.

        Args:
            record: Accepted order aggregate to publish.

        Returns:
            bool: True when partner endpoint responds with a 2xx status code.
        """
        payload: dict[str, str | int] = {
            "order_id": record.order_id,
            "customer_id": record.customer_id,
            "total_cents": record.total_cents,
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout_sec) as client:
                response = await client.post(self._endpoint_url, json=payload, timeout=self._timeout_sec)
                return 200 <= response.status_code < 300
        except httpx.HTTPError as exc:
            logger.warning("Webhook delivery failed for order %s: %s", record.order_id, exc)
            return False
