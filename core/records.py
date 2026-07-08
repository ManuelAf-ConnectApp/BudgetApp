#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from dataclasses import dataclass, field
import datetime


@dataclass(slots=True)
class CompanyProfileRecord:
    name: str
    cif: str
    address: str = ""
    email: str = ""
    phone: str = ""


@dataclass(slots=True)
class BudgetLineRecord:
    description: str
    product: str
    unit: str
    quantity: float
    unit_price: float
    discount_pct: float = 0.0
    tax_pct: float = 21.0
    notes: str = ""


@dataclass(slots=True)
class BudgetRecord:
    budget_id: int = 0
    nif_cif: str = ""
    client: str = ""
    budget_date: datetime.date = field(default_factory=datetime.date.today)
    total: float = 0.0
    lines: list[BudgetLineRecord] = field(default_factory=list)
