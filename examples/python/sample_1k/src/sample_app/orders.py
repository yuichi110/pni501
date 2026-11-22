"""Order domain service module."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class OrderRecord:

    """Immutable order record."""

    item_id: str
    quantity: int
    unit_price: float
    tier: int = 1

class OrderService:

    """Service handling order calculations and validation."""

    def __init__(self, tax_rate: float = 0.1) -> None:

        """Initialize service."""

        self._tax_rate = tax_rate

    def compute_order_score_1(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 1."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 0.5
        return round(total, 2)

    def compute_order_score_2(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 2."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 1.0
        return round(total, 2)

    def compute_order_score_3(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 3."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 1.5
        return round(total, 2)

    def compute_order_score_4(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 4."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 2.0
        return round(total, 2)

    def compute_order_score_5(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 5."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 2.5
        return round(total, 2)

    def compute_order_score_6(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 6."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 3.0
        return round(total, 2)

    def compute_order_score_7(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 7."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 3.5
        return round(total, 2)

    def compute_order_score_8(self, rec: OrderRecord, bonus: float = 0.0) -> float:
        """Compute weighted order score variant 8."""
        base = rec.quantity * rec.unit_price
        if rec.quantity <= 0:
            return 0.0
        if rec.tier >= 3:
            base *= 0.92
        elif rec.tier == 2:
            base *= 0.96
        total = base * (1.0 + self._tax_rate) + bonus + 4.0
        return round(total, 2)

