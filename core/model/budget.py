#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from dataclasses import dataclass
import datetime
from decimal import Decimal
from typing import List

from core.money import money, to_decimal


@dataclass
class BudgetLine:
    description: str
    product: str
    unit: str
    quantity: Decimal | float
    unit_price: Decimal | float
    discount_pct: Decimal | float = 0.0
    tax_pct: Decimal | float = 21.0
    notes: str = ""

    @property
    def gross_amount(self) -> Decimal:
        return money(to_decimal(self.quantity) * to_decimal(self.unit_price))

    @property
    def discount_amount(self) -> Decimal:
        return money(self.gross_amount * to_decimal(self.discount_pct) / Decimal("100"))

    @property
    def taxable_amount(self) -> Decimal:
        return money(self.gross_amount - self.discount_amount)

    @property
    def tax_amount(self) -> Decimal:
        return money(self.taxable_amount * to_decimal(self.tax_pct) / Decimal("100"))

    @property
    def subtotal(self) -> Decimal:
        return self.taxable_amount

    @property
    def line_total(self) -> Decimal:
        return money(self.taxable_amount + self.tax_amount)


class Budget:
    def __init__(self, budget_id: int = 0, nif_cif: str = "", client: str = "", budget_date: datetime.date | None = None, status: str = "draft"):
        self.budget_id = budget_id
        self.nif_cif = nif_cif
        self.client = client
        self.budget_date = budget_date or datetime.date.today()
        self.status = status
        self.budget_lines: List[BudgetLine] = []
        self._total = None


    def add_budget_line(
        self,
        description: str,
        product: str,
        unit: str,
        quantity: float,
        unit_price: float,
        discount_pct: float = 0.0,
        tax_pct: float = 21.0,
        notes: str = "",
    ):
        new_line = BudgetLine(
            description=description,
            product=product,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            discount_pct=discount_pct,
            tax_pct=tax_pct,
            notes=notes,
        )
        self.budget_lines.append(new_line)

    @property
    def total(self) -> Decimal:
        if not self.budget_lines and self._total is not None:
            return money(self._total)
        return sum((line.line_total for line in self.budget_lines), Decimal("0.00"))

    @total.setter
    def total(self, value: Decimal | float):
        self._total = money(value)
