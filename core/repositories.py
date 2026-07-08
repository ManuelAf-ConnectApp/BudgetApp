#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from typing import Protocol

from core.records import BudgetRecord, CompanyProfileRecord


class BudgetRepository(Protocol):
    def get_company_profile(self) -> CompanyProfileRecord | None: ...

    def save_company_profile(self, data: CompanyProfileRecord) -> None: ...

    def get_budget_list(self) -> list[BudgetRecord]: ...

    def save_budget(self, budget: BudgetRecord) -> int: ...
