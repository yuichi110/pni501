"""Shared currency and tax constants used across order_app modules."""

from __future__ import annotations

from typing import Final

SUPPORTED_CURRENCIES: Final[tuple[str, ...]] = ("USD", "JPY", "EUR")
DEFAULT_TAX_RATE: Final[float] = 0.10
MAX_BATCH_ITEMS: Final[int] = 250


def is_supported_currency(code: str) -> bool:
    """Return True if a 3-letter ISO currency code is supported.

    Args:
        code: Uppercase or lowercase currency code.

    Returns:
        bool: True when currency is in SUPPORTED_CURRENCIES.
    """
    return code.strip().upper() in SUPPORTED_CURRENCIES
