#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import datetime
import sqlite3

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


class LocalDatabase:
    def __init__(self):
        self.create_database = CreateDatabase(is_local=True, database="my_budgets.db")

    def get_company_profile(self) -> CompanyProfileRecord | None:
        conn = self.create_database.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT name, cif, address, email, phone FROM company_profile where id = 1")

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
        conn = self.create_database.connect()
        cursor = conn.cursor()

        query = """
            INSERT INTO company_profile (id, name, cif, address, email, phone)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                cif = excluded.cif,
                address = excluded.address,
                email = excluded.email,
                phone = excluded.phone
        """

        cursor.execute(query, (
            data.name,
            data.cif,
            data.address,
            data.email,
            data.phone
        ))

        conn.commit()
        cursor.close()
        conn.close()

    def get_budget_list(self) -> list[BudgetRecord]:
        conn = self.create_database.connect()
        cursor = conn.cursor()

        # 1. Una sola consulta combinando Presupuestos y Líneas
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

        # Cerramos el cursor y la conexión de inmediato, ya tenemos los datos en memoria
        cursor.close()
        conn.close()

        budgets_dict = {}

        for row in rows:
            budget_id = row[0]

            # 2. Si es la primera vez que vemos este presupuesto, creamos su objeto
            if budget_id not in budgets_dict:
                budget = BudgetRecord(
                    budget_id=budget_id,
                    nif_cif=row[1],
                    client=row[2],
                    budget_date=_coerce_budget_date(row[3]),
                    total=float(row[4]) if row[4] is not None else 0.0,
                    status=row[13] or "draft",
                )

                budgets_dict[budget_id] = budget

            # 3. Si la fila actual contiene una línea de presupuesto (el concepto no es NULL)
            if any(row[5:13]):
                line_obj = BudgetLineRecord(
                    description=row[5],
                    product=row[6],
                    unit=row[7],
                    quantity=float(row[8]),
                    unit_price=float(row[9]),
                    discount_pct=float(row[10] or 0),
                    tax_pct=float(row[11] or 21),
                    notes=row[12] or "",
                )
                budgets_dict[budget_id].lines.append(line_obj)

        # 4. Devolvemos la lista de los objetos Budget que se han agrupado
        return list(budgets_dict.values())

    def save_budget(self, budget: BudgetRecord) -> int:

        conn = self.create_database.connect()
        cursor = conn.cursor()

        try:
            if budget.budget_id:
                cursor.execute(
                    """UPDATE budgets SET nif_cif = ?, client_name = ?, budget_date = ?, total = ?, status = ?
                       WHERE id = ?""",
                    (budget.nif_cif, budget.client, budget.budget_date.isoformat(), str(budget.total), budget.status, budget.budget_id),
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Budget {budget.budget_id} does not exist")
                cursor.execute("DELETE FROM budget_lines WHERE budget_id = ?", (budget.budget_id,))
                budget_id = budget.budget_id
            else:
                cursor.execute(
                    """INSERT INTO budgets (nif_cif, client_name, budget_date, total, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (budget.nif_cif, budget.client, budget.budget_date.isoformat(), str(budget.total), budget.status),
                )
                budget_id = cursor.lastrowid

            lines_data = []
            for line in budget.lines:
                lines_data.append((
                    budget_id,
                    line.description,
                    line.product,
                    line.unit,
                    str(line.quantity),
                    str(line.unit_price),
                    str(line.discount_pct),
                    str(line.tax_pct),
                    line.notes,
                ))

            if lines_data:
                cursor.executemany('''
                                   INSERT INTO budget_lines (
                                       budget_id, description, product, unit, quantity, unit_price, discount_pct, tax_pct, notes
                                   )
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', lines_data)

            conn.commit()
            return budget_id

        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_budget(self, budget_id: int) -> None:
        conn = self.create_database.connect()
        try:
            conn.execute("DELETE FROM budget_lines WHERE budget_id = ?", (budget_id,))
            conn.execute("DELETE FROM budgets WHERE id = ?", (budget_id,))
            conn.commit()
        finally:
            conn.close()

    def update_budget_status(self, budget_id: int, status: str) -> None:
        conn = self.create_database.connect()
        try:
            conn.execute("UPDATE budgets SET status = ? WHERE id = ?", (status, budget_id))
            conn.commit()
        finally:
            conn.close()

    def backup_to(self, destination: str) -> None:
        """Use SQLite's online backup API so an active database stays consistent."""
        destination_conn = sqlite3.connect(destination)
        source_conn = self.create_database.connect()
        try:
            source_conn.backup(destination_conn)
        finally:
            destination_conn.close()
            source_conn.close()
