from __future__ import annotations

import os
import sys
import tempfile
import types
import unittest
from contextlib import contextmanager
from datetime import date
from pathlib import Path


def _install_mysql_stub() -> None:
    if "mysql" not in sys.modules:
        mysql_module = types.ModuleType("mysql")
        mysql_module.__path__ = []  # type: ignore[attr-defined]
        sys.modules["mysql"] = mysql_module
    else:
        mysql_module = sys.modules["mysql"]

    if "mysql.connector" not in sys.modules:
        connector_module = types.ModuleType("mysql.connector")

        def _unexpected_mysql_connect():
            raise AssertionError("MySQL connection should not be used in these tests")

        connector_module.connect = _unexpected_mysql_connect  # type: ignore[attr-defined]
        connector_module.__package__ = "mysql"
        sys.modules["mysql.connector"] = connector_module
        setattr(mysql_module, "connector", connector_module)


_install_mysql_stub()


def _install_reportlab_stub() -> None:
    if "reportlab" not in sys.modules:
        reportlab_module = types.ModuleType("reportlab")
        reportlab_module.__path__ = []  # type: ignore[attr-defined]
        sys.modules["reportlab"] = reportlab_module

    def _ensure_module(name: str) -> types.ModuleType:
        module = sys.modules.get(name)
        if module is None:
            module = types.ModuleType(name)
            sys.modules[name] = module
        return module

    colors_module = _ensure_module("reportlab.lib.colors")
    colors_module.HexColor = lambda value: value  # type: ignore[attr-defined]
    colors_module.white = "white"  # type: ignore[attr-defined]

    pagesizes_module = _ensure_module("reportlab.lib.pagesizes")
    pagesizes_module.A4 = (595.27, 841.89)  # type: ignore[attr-defined]

    styles_module = _ensure_module("reportlab.lib.styles")
    styles_module.ParagraphStyle = object  # type: ignore[attr-defined]
    styles_module.getSampleStyleSheet = lambda: {"Heading1": object(), "Normal": object()}  # type: ignore[attr-defined]

    units_module = _ensure_module("reportlab.lib.units")
    units_module.mm = 1  # type: ignore[attr-defined]

    charts_module = _ensure_module("reportlab.graphics.charts.barcharts")
    charts_module.HorizontalBarChart = object  # type: ignore[attr-defined]

    shapes_module = _ensure_module("reportlab.graphics.shapes")
    shapes_module.Drawing = object  # type: ignore[attr-defined]
    shapes_module.Line = object  # type: ignore[attr-defined]
    shapes_module.Rect = object  # type: ignore[attr-defined]
    shapes_module.String = object  # type: ignore[attr-defined]

    platypus_module = _ensure_module("reportlab.platypus")
    for name in ["Image", "PageBreak", "Paragraph", "SimpleDocTemplate", "Spacer", "Table", "TableStyle"]:
        setattr(platypus_module, name, object)

    _ensure_module("reportlab.lib")
    _ensure_module("reportlab.graphics")
    _ensure_module("reportlab.graphics.charts")


from core.model.budget import Budget, BudgetLine
from core.records import BudgetLineRecord, BudgetRecord, CompanyProfileRecord
from infrastructure.database.local_database import LocalDatabase

try:
    from infrastructure.services.pdf_generator import format_budget_reference
except ModuleNotFoundError as exc:
    if not exc.name or not exc.name.startswith("reportlab"):
        raise
    _install_reportlab_stub()
    from infrastructure.services.pdf_generator import format_budget_reference


@contextmanager
def temporary_home():
    old_home = os.environ.get("HOME")
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["HOME"] = tmpdir
        try:
            yield Path(tmpdir)
        finally:
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home


class TestBudgetCalculations(unittest.TestCase):
    def test_budget_line_amounts(self):
        line = BudgetLine(
            description="Servicio",
            product="Producto",
            unit="ud",
            quantity=2,
            unit_price=100,
            discount_pct=10,
            tax_pct=21,
        )

        self.assertEqual(line.gross_amount, 200)
        self.assertEqual(line.discount_amount, 20)
        self.assertEqual(line.taxable_amount, 180)
        self.assertAlmostEqual(line.tax_amount, 37.8)
        self.assertAlmostEqual(line.line_total, 217.8)

    def test_budget_total_is_recomputed_from_lines(self):
        budget = Budget(budget_id=1, nif_cif="A12345678", client="Cliente", budget_date=date(2026, 6, 30))
        budget.add_budget_line(
            description="Linea 1",
            product="Prod 1",
            unit="ud",
            quantity=1,
            unit_price=100,
            discount_pct=0,
            tax_pct=21,
        )
        budget.add_budget_line(
            description="Linea 2",
            product="Prod 2",
            unit="ud",
            quantity=2,
            unit_price=50,
            discount_pct=10,
            tax_pct=21,
        )

        self.assertEqual(len(budget.budget_lines), 2)
        self.assertAlmostEqual(budget.total, 229.9)

    def test_budget_total_can_be_set_when_there_are_no_lines(self):
        budget = Budget()
        budget.total = 123.45

        self.assertEqual(budget.total, 123.45)


class TestLocalDatabaseIntegration(unittest.TestCase):
    def test_company_profile_round_trip(self):
        with temporary_home():
            db = LocalDatabase()
            self.assertIsNone(db.get_company_profile())

            profile = CompanyProfileRecord(
                name="Connect App ES",
                cif="B12345678",
                address="Calle Principal 1",
                email="info@example.com",
                phone="123456789",
            )
            db.save_company_profile(profile)

            loaded = db.get_company_profile()

            self.assertEqual(loaded, profile)

    def test_budget_round_trip(self):
        with temporary_home():
            db = LocalDatabase()
            budget = BudgetRecord(
                nif_cif="A12345678",
                client="Cliente Demo",
                budget_date=date(2026, 6, 30),
                total=217.8,
                lines=[
                    BudgetLineRecord(
                        description="Servicio principal",
                        product="Consultoria",
                        unit="h",
                        quantity=2,
                        unit_price=100,
                        discount_pct=10,
                        tax_pct=21,
                        notes="Trabajo inicial",
                    ),
                ],
            )

            budget_id = db.save_budget(budget)
            budgets = db.get_budget_list()

            self.assertEqual(budget_id, 1)
            self.assertEqual(len(budgets), 1)
            loaded = budgets[0]
            self.assertEqual(loaded.budget_id, 1)
            self.assertEqual(loaded.nif_cif, "A12345678")
            self.assertEqual(loaded.client, "Cliente Demo")
            self.assertEqual(loaded.budget_date, date(2026, 6, 30))
            self.assertAlmostEqual(loaded.total, 217.8)
            self.assertEqual(len(loaded.lines), 1)

            line = loaded.lines[0]
            self.assertEqual(line.description, "Servicio principal")
            self.assertEqual(line.product, "Consultoria")
            self.assertEqual(line.unit, "h")
            self.assertEqual(line.quantity, 2)
            self.assertEqual(line.unit_price, 100)
            self.assertEqual(line.discount_pct, 10)
            self.assertEqual(line.tax_pct, 21)
            self.assertEqual(line.notes, "Trabajo inicial")


class TestPdfReferenceFormatting(unittest.TestCase):
    def test_budget_reference_formats_only_positive_ids(self):
        self.assertEqual(format_budget_reference(1), "1")
        self.assertEqual(format_budget_reference("7"), "7")
        self.assertEqual(format_budget_reference(0), "N/D")
        self.assertEqual(format_budget_reference(None), "N/D")
        self.assertEqual(format_budget_reference(""), "N/D")


if __name__ == "__main__":
    unittest.main()
