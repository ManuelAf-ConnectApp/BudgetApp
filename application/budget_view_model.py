#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import datetime
import re

from PySide6.QtCore import QObject, Signal, Slot

from core.model.budget import Budget
from core.model.company import Company
from core.records import BudgetLineRecord, BudgetRecord
from core.repositories import BudgetRepository
from infrastructure.services.pdf_generator import PDFGenerator
from infrastructure.ui.i18n import normalize_language, t


class BudgetViewModel(QObject):
    changed_client = Signal(str)
    updated_lines = Signal(list)
    changed_total = Signal(str)
    budget_list = Signal(list)
    catalog_loaded = Signal(list)
    budget_saved = Signal(int)
    save_error = Signal(str)
    pdf_export_success = Signal(str)
    pdf_export_error = Signal(str)

    def __init__(self, repository: BudgetRepository, language: str = "es"):
        super().__init__()
        self.db = repository
        self.lang = normalize_language(language)
        self.budget = Budget(client=t("budget.pending_client", self.lang))
        self.selected_history_index: int = -1
        self.product_catalog: list[Budget] = []

    def _budget_to_record(self) -> BudgetRecord:
        return BudgetRecord(
            budget_id=self.budget.budget_id,
            nif_cif=self.budget.nif_cif,
            client=self.budget.client,
            budget_date=self.budget.budget_date,
            total=self.budget.total,
            lines=[
                BudgetLineRecord(
                    description=line.description,
                    product=line.product,
                    unit=line.unit,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    discount_pct=line.discount_pct,
                    tax_pct=line.tax_pct,
                    notes=line.notes,
                )
                for line in self.budget.budget_lines
            ],
        )

    @staticmethod
    def _record_to_budget(record: BudgetRecord) -> Budget:
        budget = Budget(
            budget_id=record.budget_id,
            nif_cif=record.nif_cif,
            client=record.client,
            budget_date=record.budget_date,
        )
        budget.total = record.total
        for line in record.lines:
            budget.add_budget_line(
                description=line.description,
                product=line.product,
                unit=line.unit,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_pct=line.discount_pct,
                tax_pct=line.tax_pct,
                notes=line.notes,
            )
        return budget

    def load_budget_list(self):
        try:
            records = self.db.get_budget_list()
            self.product_catalog = [self._record_to_budget(record) for record in records]
            self.budget_list.emit(self.product_catalog)
        except Exception as e:
            self.save_error.emit(t("vm.load_history_error", self.lang, error=str(e)))

    @Slot(str, str, str, float, float, float, float, str)
    def add_item(
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
        if not description.strip() or not product.strip() or not unit.strip() or quantity <= 0 or unit_price <= 0:
            return

        self.budget.add_budget_line(
            description=description,
            product=product,
            unit=unit,
            quantity=quantity,
            unit_price=unit_price,
            discount_pct=discount_pct,
            tax_pct=tax_pct,
            notes=notes,
        )
        self._notify_changes()

    def set_budget_lines(self, lines: list[BudgetLineRecord]):
        self.budget.budget_lines = []
        for line in lines:
            self.budget.add_budget_line(
                description=line.description,
                product=line.product,
                unit=line.unit,
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_pct=line.discount_pct,
                tax_pct=line.tax_pct,
                notes=line.notes,
            )
        self._notify_changes()

    def _notify_changes(self):
        formatted_lines = [
            f"{l.description} - {l.product} -> ({l.quantity}) - {l.line_total:.2f}€"
            for l in self.budget.budget_lines
        ]
        self.updated_lines.emit(formatted_lines)
        self.changed_total.emit(f"{self.budget.total:.2f}€")

    def interface_refresh(self):
        self.changed_client.emit(self.budget.client)
        catalog_names = [p.client for p in self.product_catalog]
        self.catalog_loaded.emit(catalog_names)
        self._notify_changes()

    @Slot(str, str, datetime.date)
    def save_budget(self, client_name: str, nif_cif: str, budget_date: datetime.date):
        if not self.budget.budget_lines:
            self.save_error.emit(t("vm.save_without_lines", self.lang))
            return

        if not client_name.strip():
            self.save_error.emit(t("vm.save_empty_client", self.lang))
            return

        if nif_cif.strip() and not self.is_valid_dni_nie(nif_cif):
            self.save_error.emit(t("vm.save_invalid_dni", self.lang))
            return

        self.budget.nif_cif = nif_cif.strip()
        self.budget.client = client_name.strip()
        self.budget.budget_date = budget_date

        try:
            new_id = self.db.save_budget(self._budget_to_record())
            self.budget.budget_id = new_id
            self.budget_saved.emit(new_id)
            self.budget = Budget(client=t("budget.pending_client", self.lang))
            self._notify_changes()
            self.load_budget_list()
        except Exception as e:
            self.save_error.emit(t("vm.save_db_error", self.lang, error=str(e)))

    @staticmethod
    def is_valid_dni_nie(document: str) -> bool:
        doc_clean = document.upper().replace("-", "").replace(" ", "")
        regex = r'^[XYZ\d]\d{7}[A-Z]$'
        if not re.match(regex, doc_clean):
            return False

        nie_mapping = {'X': '0', 'Y': '1', 'Z': '2'}
        first_char = doc_clean[0]

        if first_char in nie_mapping:
            numeric_part = nie_mapping[first_char] + doc_clean[1:-1]
        else:
            numeric_part = doc_clean[:-1]

        dni_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        provided_letter = doc_clean[-1]

        try:
            calculated_index = int(numeric_part) % 23
            expected_letter = dni_letters[calculated_index]
            return provided_letter == expected_letter
        except ValueError:
            return False

    @Slot(str)
    def export_current_budget_to_pdf(self, file_path: str):
        if not self.budget.budget_lines:
            self.pdf_export_error.emit(t("vm.pdf_empty", self.lang))
            return

        try:
            company_record = self.db.get_company_profile()
            if company_record is None:
                raise ValueError(t("vm.no_company_profile", self.lang))

            company = Company(
                name=company_record.name,
                cif=company_record.cif,
                address=company_record.address,
                email=company_record.email,
                phone=company_record.phone,
            )

            PDFGenerator.generate_budget_pdf(self.budget, company, file_path)
            self.pdf_export_success.emit(file_path)
        except Exception as e:
            self.pdf_export_error.emit(t("vm.pdf_critical_error", self.lang, error=str(e)))

    @Slot(int)
    def set_selected_budget_index(self, index: int):
        self.selected_history_index = index
