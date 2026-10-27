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
                SELECT b.id,
                       b.nif_cif,
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
                       COALESCE(bl.notes, '') AS notes,
                       b.status
                FROM budgets b
                         LEFT JOIN budget_lines bl ON b.id = bl.budget_id
                ORDER BY b.id DESC
                """
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        budget_map: dict[int, BudgetRecord] = {}
        for row in rows:
            budget_id = row[0]
            if budget_id not in budget_map:
                budget_map[budget_id] = BudgetRecord(
                    budget_id=budget_id,
                    nif_cif=row[1],
                    client=row[2],
                    budget_date=_coerce_budget_date(row[3]),
                    total=float(row[4]) if row[4] is not None else 0.0,
                    status=row[13] or "draft",
                )
            if any(row[5:13]):
                budget_map[budget_id].lines.append(BudgetLineRecord(
                    description=row[5],
                    product=row[6],
                    unit=row[7],
                    quantity=float(row[8]),
                    unit_price=float(row[9]),
                    discount_pct=float(row[10] or 0),
                    tax_pct=float(row[11] or 21),
                    notes=row[12] or "",
                ))

        return list(budget_map.values())

    def save_budget(self, budget: BudgetRecord) -> int:
        conn = self.create_database.connect()
        cursor = conn.cursor()

        try:
            conn.start_transaction()
            if budget.budget_id:
                cursor.execute(
                    """UPDATE budgets SET nif_cif = %s, client_name = %s, budget_date = %s, total = %s, status = %s
                       WHERE id = %s""",
                    (budget.nif_cif, budget.client, budget.budget_date.isoformat(), budget.total, budget.status, budget.budget_id),
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Budget {budget.budget_id} does not exist")
                cursor.execute("DELETE FROM budget_lines WHERE budget_id = %s", (budget.budget_id,))
                budget_id = budget.budget_id
            else:
                cursor.execute(
                    """INSERT INTO budgets (nif_cif, client_name, budget_date, total, status)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (budget.nif_cif, budget.client, budget.budget_date.isoformat(), budget.total, budget.status),
                )
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

            conn.commit()
            return budget_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_budget(self, budget_id: int) -> None:
        conn = self.create_database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM budgets WHERE id = %s", (budget_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_budget_status(self, budget_id: int, status: str) -> None:
        conn = self.create_database.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE budgets SET status = %s WHERE id = %s", (status, budget_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
