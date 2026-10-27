from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


MONEY_PLACES = Decimal("0.01")


def to_decimal(value: Decimal | int | float | str) -> Decimal:
    """Convert user and database values without inheriting binary float errors."""
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money(value: Decimal | int | float | str) -> Decimal:
    return to_decimal(value).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
