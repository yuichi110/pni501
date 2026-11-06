"""Repository protocol and in-memory adapter for order persistence."""

from __future__ import annotations

from typing import Protocol

from order_dispatch.domain.models import OrderRecord


class OrderRepository(Protocol):
    """Port interface for storing and retrieving OrderRecord aggregates."""

    def save(self, record: OrderRecord) -> None:
        """Persist an OrderRecord by its order_id.

        Args:
            record: Order aggregate to store.
        """
        ...

    def get(self, order_id: str) -> OrderRecord | None:
        """Retrieve a previously saved OrderRecord or None if absent.

        Args:
            order_id: Unique order identifier.

        Returns:
            OrderRecord | None: Matching order aggregate if found.
        """
        ...


class InMemoryOrderRepository:
    """Thread-local / test-friendly dictionary-backed OrderRepository adapter."""

    def __init__(self) -> None:
        """Initialize an isolated order dictionary."""
        self._records: dict[str, OrderRecord] = {}

    def save(self, record: OrderRecord) -> None:
        """Store or update an OrderRecord in memory.

        Args:
            record: Order aggregate to store.
        """
        self._records[record.order_id] = record

    def get(self, order_id: str) -> OrderRecord | None:
        """Look up an OrderRecord by order_id.

        Args:
            order_id: Unique order identifier.

        Returns:
            OrderRecord | None: Stored order record or None.
        """
        return self._records.get(order_id)
