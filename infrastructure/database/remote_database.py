#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import datetime

from core.records import BudgetLineRecord, BudgetRecord, CompanyProfileRecord
from infrastructure.database.create_database import CreateDatabase


def _coerce_budget_date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return value
    return value


class RemoteDatabase:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.create_database = CreateDatabase(self.host, self.database, self.user, self.password)

    def get_company_profile(self) -> CompanyProfileRecord | None:
        """Recupera los datos fiscales de la empresa si existen en MySQL (Fila 1)."""
        conn = self.create_database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT name, cif, address, email, phone FROM company_profile WHERE id = 1")
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return CompanyProfileRecord(
            name=row[0],
            cif=row[1],
            address=row[2],
            email=row[3],
            phone=row[4]
        )

    def save_company_profile(self, data: CompanyProfileRecord) -> None:
        """Guarda o actualiza los datos fiscales en MySQL usando ON DUPLICATE KEY."""
        conn = self.create_database.connect()
        cursor = conn.cursor()

        # Sintaxis estándar de MySQL para actualizar si la clave primaria (id=1) ya existe
        query = """
                INSERT INTO company_profile (id, name, cif, address, email, phone)
                VALUES (1, %s, %s, %s, %s, %s) ON DUPLICATE KEY \
                UPDATE \
                    name = \
                VALUES (name), cif = \
                VALUES (cif), address = \
                VALUES (address), email = \
                VALUES (email), phone = \
                VALUES (phone) \
                """
        cursor.execute(query, (
            data.name,
            data.cif,
            data.address,
            data.email,
            data.phone
        ))

        cursor.close()
        conn.close()

    def get_budget_list(self) -> list[BudgetRecord]:
        conn = self.create_database.connect()

        cursor = conn.cursor()

        query = """
                SELECT b.nif_cif,
                       b.client_name,
                       b.budget_date,
                       b.total,
                       COALESCE(bl.description, bl.concept, '') AS description,
                       COALESCE(bl.product, bl.product_id, '') AS product,
                       COALESCE(bl.unit, '') AS unit,
                       COALESCE(bl.quantity, 0) AS quantity,
                       COALESCE(bl.unit_price, bl.price, 0) AS unit_price,
                       COALESCE(bl.discount_pct, 0) AS discount_pct,
                       COALESCE(bl.tax_pct, 21) AS tax_pct,
                       COALESCE(bl.notes, '') AS notes
                FROM budgets b
                         LEFT JOIN budget_lines bl ON b.id = bl.budget_id
                ORDER BY b.id DESC
                """
        cursor.execute(query)
        rows = cursor.fetchall()

        conn.close()

        budget_map: dict[tuple, BudgetRecord] = {}
        for row in rows:
            key = (row[0], row[1], row[2], row[3])
            if key not in budget_map:
                budget_map[key] = BudgetRecord(
                    nif_cif=row[0],
                    client=row[1],
                    budget_date=_coerce_budget_date(row[2]),
                    total=float(row[3]) if row[3] is not None else 0.0,
                )
            if any(row[4:12]):
                budget_map[key].lines.append(BudgetLineRecord(
                    description=row[4],
                    product=row[5],
                    unit=row[6],
                    quantity=float(row[7]),
                    unit_price=float(row[8]),
                    discount_pct=float(row[9] or 0),
                    tax_pct=float(row[10] or 21),
                    notes=row[11] or "",
                ))

        return list(budget_map.values())

    def save_budget(self, budget: BudgetRecord) -> int:
        conn = self.create_database.connect()
        cursor = conn.cursor()

        try:
            query_budget = """
                           INSERT INTO budgets (nif_cif, client_name, budget_date, total)
                           VALUES (%s, %s, %s, %s)
                           """

            values_budget = (budget.nif_cif, budget.client, budget.budget_date.isoformat(), budget.total)
            cursor.execute(query_budget, values_budget)

            budget_id = cursor.lastrowid

            lines_data = []
            for line in budget.lines:
                lines_data.append((
                    budget_id,
                    line.description,
                    line.product,
                    line.unit,
                    line.quantity,
                    line.unit_price,
                    line.discount_pct,
                    line.tax_pct,
                    line.notes,
                ))

            if lines_data:
                cursor.executemany(
                    """
                    INSERT INTO budget_lines (
                        budget_id, description, product, unit, quantity, unit_price, discount_pct, tax_pct, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    lines_data
                )

            return budget_id
        finally:
            cursor.close()
            conn.close()
