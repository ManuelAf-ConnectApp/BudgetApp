#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import datetime
from html import escape

from PySide6.QtCore import QDate, Qt, QTimer
from PySide6.QtGui import QTextDocument
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSizePolicy,
    QLineEdit, QDateEdit, QListWidget, QLabel, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFileDialog, QDialog
)
from PySide6.QtPrintSupport import QPrinter, QPrintDialog

from application.budget_view_model import BudgetViewModel
from core.model.budget import Budget
from core.records import BudgetLineRecord
from infrastructure.ui.i18n import normalize_language, t
from infrastructure.ui.style import StyleApp


class BudgetViewWidget(QWidget):
    LINE_COLUMNS = 9

    def __init__(self, vm: BudgetViewModel, language: str = "es"):
        super().__init__()
        self._vm = vm
        self.lang = normalize_language(language)
        self.style = StyleApp
        self._syncing_table = False
        self._restoring_history = False
        self._pending_history_state = None
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []
        self._pending_preserve_state = None
        self._preserve_editor_after_save = False

        self._setup_ui()
        self._connect_signals()
        self._insert_blank_line(record_history=False)
        self._sync_view_model_from_table()

    def _setup_ui(self):
        main_layout = QVBoxLayout()

        client_section = self._create_client_section()
        lines_section = self._create_lines_section()
        list_section = self._create_list_section()
        bottom_actions = self._create_bottom_actions()

        main_layout.addWidget(client_section)
        main_layout.addWidget(lines_section)
        main_layout.addLayout(list_section)
        main_layout.addLayout(bottom_actions)

        self.setLayout(main_layout)

    def _create_client_section(self) -> QGroupBox:
        group_client = QGroupBox(t("budget.client_section", self.lang))
        group_client.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        group_client.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)

        self.input_client_company = QLineEdit()
        self.input_client_company.setPlaceholderText(t("budget.company_ph", self.lang))
        self.input_client_company.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.input_client_name = QLineEdit()
        self.input_client_name.setPlaceholderText(t("budget.name_ph", self.lang))
        self.input_client_name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.input_surname = QLineEdit()
        self.input_surname.setPlaceholderText(t("budget.surname_ph", self.lang))
        self.input_surname.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.input_nif_client = QLineEdit()
        self.input_nif_client.setPlaceholderText(t("budget.nif_ph", self.lang))
        self.input_nif_client.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.input_date = QDateEdit()
        self.input_date.setCalendarPopup(True)
        self.input_date.setDate(QDate.currentDate())
        self.input_date.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        form_layout.addRow(t("budget.company", self.lang), self.input_client_company)
        form_layout.addRow(t("budget.name", self.lang), self.input_client_name)
        form_layout.addRow(t("budget.surname", self.lang), self.input_surname)
        form_layout.addRow(t("budget.nif", self.lang), self.input_nif_client)
        form_layout.addRow(t("budget.date", self.lang), self.input_date)

        group_client.setLayout(form_layout)
        return group_client

    def _create_lines_section(self) -> QGroupBox:
        group_lines = QGroupBox(t("budget.lines_section", self.lang))
        group_lines.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        group_lines.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        wrapper = QVBoxLayout()
        toolbar = QHBoxLayout()

        self.btn_add_line = QPushButton(t("budget.add", self.lang))
        self.btn_remove_line = QPushButton(t("budget.remove", self.lang))
        self.btn_clear_lines = QPushButton(t("budget.clear_lines", self.lang))

        toolbar.addWidget(self.btn_add_line)
        toolbar.addWidget(self.btn_remove_line)
        toolbar.addWidget(self.btn_clear_lines)
        toolbar.addStretch()

        self.lines_table = QTableWidget(0, self.LINE_COLUMNS)
        self.lines_table.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        self.lines_table.setHorizontalHeaderLabels([
            t("budget.description", self.lang),
            t("budget.product", self.lang),
            t("budget.unit", self.lang),
            t("budget.quantity", self.lang),
            t("budget.unit_price", self.lang),
            t("budget.discount", self.lang),
            t("budget.tax", self.lang),
            t("budget.total_line", self.lang),
            t("budget.notes", self.lang),
        ])
        header = self.lines_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)
        header.setMinimumSectionSize(70)
        self.lines_table.verticalHeader().setVisible(False)
        self.lines_table.verticalHeader().setDefaultSectionSize(28)
        self.lines_table.setAlternatingRowColors(True)
        self.lines_table.setWordWrap(False)
        self.lines_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.lines_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.lines_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.SelectedClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
        )

        wrapper.addLayout(toolbar)
        wrapper.addWidget(self.lines_table)
        group_lines.setLayout(wrapper)
        return group_lines

    def _create_list_section(self) -> QVBoxLayout:
        layout = QVBoxLayout()

        self.items_list = QListWidget()
        self.lbl_total = QLabel(t("budget.total_label", self.lang, amount=t("budget.zero_amount", self.lang)))
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")

        layout.addWidget(self.items_list)
        layout.addWidget(self.lbl_total)
        return layout

    def _create_bottom_actions(self) -> QHBoxLayout:
        layout_bottom = QHBoxLayout()

        self.clear_button = QPushButton(t("budget.clear", self.lang))
        self.clear_button.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)

        self.btn_save_budget = QPushButton(t("budget.save", self.lang))
        self.btn_save_budget.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)

        layout_bottom.addWidget(self.clear_button)
        layout_bottom.addWidget(self.btn_save_budget)
        return layout_bottom

    def _connect_signals(self):
        self.btn_add_line.clicked.connect(self._insert_blank_line)
        self.btn_remove_line.clicked.connect(self._remove_selected_line)
        self.btn_clear_lines.clicked.connect(self._clear_lines_table)
        self.clear_button.clicked.connect(self._clear_budget)
        self.btn_save_budget.clicked.connect(self.on_save_clicked)

        self.lines_table.cellPressed.connect(self._capture_pending_history_state)
        self.lines_table.cellChanged.connect(self._on_line_cell_changed)

        self._vm.changed_total.connect(self._update_total_label)
        self._vm.updated_lines.connect(self.visual_list_update)
        self._vm.budget_saved.connect(self.show_success_message)
        self._vm.save_error.connect(self.show_error_message)
        self._vm.pdf_export_error.connect(self.show_error_message)
        self._vm.load_budget_list()

    def _capture_state(self) -> dict:
        return {
            "budget_id": self._vm.budget.budget_id,
            "company": self.input_client_company.text(),
            "name": self.input_client_name.text(),
            "surname": self.input_surname.text(),
            "nif": self.input_nif_client.text(),
            "date": self.input_date.date().toPython(),
            "rows": [
                [self._item_text(row, column) for column in range(self.LINE_COLUMNS)]
                for row in range(self.lines_table.rowCount())
            ],
        }

    def _restore_state(self, state: dict, sync_vm: bool = True):
        self._restoring_history = True
        self.lines_table.blockSignals(True)
        try:
            self.input_client_company.setText(state.get("company", ""))
            self.input_client_name.setText(state.get("name", ""))
            self.input_surname.setText(state.get("surname", ""))
            self.input_nif_client.setText(state.get("nif", ""))
            date_value = state.get("date")
            if isinstance(date_value, datetime.date):
                self.input_date.setDate(QDate(date_value.year, date_value.month, date_value.day))
            else:
                self.input_date.setDate(QDate.currentDate())

            self.lines_table.setRowCount(0)
            for row_values in state.get("rows", []):
                row = self.lines_table.rowCount()
                self.lines_table.insertRow(row)
                for column, value in enumerate(row_values):
                    editable = column != 7
                    alignment = {
                        0: Qt.AlignmentFlag.AlignLeft,
                        1: Qt.AlignmentFlag.AlignLeft,
                        2: Qt.AlignmentFlag.AlignCenter,
                        3: Qt.AlignmentFlag.AlignRight,
                        4: Qt.AlignmentFlag.AlignRight,
                        5: Qt.AlignmentFlag.AlignRight,
                        6: Qt.AlignmentFlag.AlignRight,
                        7: Qt.AlignmentFlag.AlignRight,
                        8: Qt.AlignmentFlag.AlignLeft,
                    }[column]
                    self.lines_table.setItem(
                        row,
                        column,
                        self._create_text_item(value, editable=editable, alignment=alignment),
                    )
                self._recalculate_row_total(row)
        finally:
            self.lines_table.blockSignals(False)
            self._restoring_history = False
            self._pending_history_state = None

        if sync_vm:
            self._vm.budget = Budget(
                budget_id=state.get("budget_id", 0),
                nif_cif=state.get("nif", ""),
                client=state.get("name", ""),
                budget_date=state.get("date") or QDate.currentDate().toPython(),
            )
            self._sync_view_model_from_table()

    def _push_undo_state(self, state: dict | None):
        if state is None:
            return
        self._undo_stack.append(state)
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def _capture_pending_history_state(self, row: int, column: int):
        if self._restoring_history:
            return
        self._pending_history_state = self._capture_state()

    def _begin_history_action(self):
        if not self._restoring_history:
            self._pending_history_state = self._capture_state()

    def _commit_history_action(self):
        if self._restoring_history:
            return
        if self._pending_history_state is None:
            return
        current_state = self._capture_state()
        if current_state != self._pending_history_state:
            self._push_undo_state(self._pending_history_state)
        self._pending_history_state = None

    def undo_last_change(self):
        if not self._undo_stack:
            return
        current_state = self._capture_state()
        state = self._undo_stack.pop()
        self._redo_stack.append(current_state)
        self._restore_state(state)

    def redo_last_change(self):
        if not self._redo_stack:
            return
        current_state = self._capture_state()
        state = self._redo_stack.pop()
        self._undo_stack.append(current_state)
        self._restore_state(state)

    def _recalculate_all_rows(self):
        for row in range(self.lines_table.rowCount()):
            self._recalculate_row_total(row)

    def set_summary_visible(self, visible: bool):
        self.items_list.setVisible(visible)
        self.lbl_total.setVisible(visible)

    def new_budget(self):
        self._clear_budget()

    def delete_selected_line(self):
        self._remove_selected_line()

    def duplicate_selected_line(self):
        row = self.lines_table.currentRow()
        if row < 0:
            return

        self._begin_history_action()
        source_values = [self._item_text(row, column) for column in range(self.LINE_COLUMNS)]
        insert_row = row + 1
        self.lines_table.blockSignals(True)
        self.lines_table.insertRow(insert_row)
        try:
            for column, value in enumerate(source_values):
                editable = column != 7
                alignment = {
                    0: Qt.AlignmentFlag.AlignLeft,
                    1: Qt.AlignmentFlag.AlignLeft,
                    2: Qt.AlignmentFlag.AlignCenter,
                    3: Qt.AlignmentFlag.AlignRight,
                    4: Qt.AlignmentFlag.AlignRight,
                    5: Qt.AlignmentFlag.AlignRight,
                    6: Qt.AlignmentFlag.AlignRight,
                    7: Qt.AlignmentFlag.AlignRight,
                    8: Qt.AlignmentFlag.AlignLeft,
                }[column]
                self.lines_table.setItem(
                    insert_row,
                    column,
                    self._create_text_item(value, editable=editable, alignment=alignment),
                )
        finally:
            self.lines_table.blockSignals(False)

        self._recalculate_row_total(insert_row)
        self.lines_table.selectRow(insert_row)
        self._sync_view_model_from_table()
        self._commit_history_action()

    def load_budget_into_editor(self, budget: Budget):
        self._begin_history_action()
        self._vm.budget = Budget(
            budget_id=budget.budget_id,
            nif_cif=budget.nif_cif,
            client=budget.client,
            budget_date=budget.budget_date,
        )
        self.input_client_company.setText("")
        self.input_client_name.setText(budget.client)
        self.input_surname.clear()
        self.input_nif_client.setText(budget.nif_cif)
        if hasattr(budget.budget_date, "year"):
            self.input_date.setDate(QDate(budget.budget_date.year, budget.budget_date.month, budget.budget_date.day))
        else:
            self.input_date.setDate(QDate.currentDate())

        self.lines_table.setRowCount(0)
        for line in budget.budget_lines:
            row = self.lines_table.rowCount()
            self.lines_table.insertRow(row)
            values = [
                line.description,
                line.product if isinstance(line.product, str) else str(line.product),
                line.unit,
                f"{line.quantity}",
                f"{line.unit_price:.2f}",
                f"{line.discount_pct:.2f}",
                f"{line.tax_pct:.2f}",
                f"{line.line_total:.2f}€",
                line.notes,
            ]
            for column, value in enumerate(values):
                editable = column != 7
                alignment = {
                    0: Qt.AlignmentFlag.AlignLeft,
                    1: Qt.AlignmentFlag.AlignLeft,
                    2: Qt.AlignmentFlag.AlignCenter,
                    3: Qt.AlignmentFlag.AlignRight,
                    4: Qt.AlignmentFlag.AlignRight,
                    5: Qt.AlignmentFlag.AlignRight,
                    6: Qt.AlignmentFlag.AlignRight,
                    7: Qt.AlignmentFlag.AlignRight,
                    8: Qt.AlignmentFlag.AlignLeft,
                }[column]
                self.lines_table.setItem(row, column, self._create_text_item(value, editable=editable, alignment=alignment))
            self._recalculate_row_total(row)

        self._sync_budget_header_to_vm()
        self._sync_view_model_from_table()
        self._commit_history_action()

    def export_current_budget_pdf(self):
        lines, errors = self._collect_lines_from_table(strict=True)
        if errors:
            self.show_error_message("\n".join(errors))
            return

        self._vm.set_budget_lines(lines)
        self._sync_budget_header_to_vm()

        fallback_name = t("budget.pending_client", self.lang).replace(" ", "_").lower()
        default_name = t(
            "budget.export_name",
            self.lang,
            name=self._vm.budget.client.replace(" ", "_") or fallback_name,
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("budget.export_title", self.lang),
            default_name,
            t("budget.pdf_filter", self.lang),
        )
        if not file_path:
            return

        self._vm.export_current_budget_to_pdf(file_path)

    def print_current_budget(self):
        lines, errors = self._collect_lines_from_table(strict=True)
        if errors:
            self.show_error_message("\n".join(errors))
            return

        self._vm.set_budget_lines(lines)
        self._sync_budget_header_to_vm()

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        doc = QTextDocument()
        html = self._build_printable_html()
        doc.setHtml(html)
        doc.print(printer)

    def _build_printable_html(self) -> str:
        client = escape(self.input_client_name.text().strip() or "-")
        nif = escape(self.input_nif_client.text().strip() or "-")
        date_value = self.input_date.date().toPython()
        date_str = date_value.strftime("%d/%m/%Y") if hasattr(date_value, "strftime") else str(date_value)

        rows = []
        for row in range(self.lines_table.rowCount()):
            rows.append(
                "<tr>"
                + "".join(
                    f"<td>{escape(self._item_text(row, column)) if self._item_text(row, column) else '&nbsp;'}</td>"
                    for column in range(self.LINE_COLUMNS)
                )
                + "</tr>"
            )

        return f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Helvetica, Arial, sans-serif; color: #1f2937; }}
                    h1 {{ color: #1a365d; font-size: 22px; margin-bottom: 4px; }}
                    h2 {{ color: #1a365d; font-size: 14px; margin-top: 18px; }}
                    table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
                    th {{ background: #1a365d; color: white; padding: 6px; text-align: left; }}
                    td {{ border: 1px solid #d9e2ec; padding: 5px; vertical-align: top; }}
                    .meta {{ margin-bottom: 12px; font-size: 10px; }}
                    .summary {{ width: 40%; margin-left: auto; }}
                    .summary td {{ font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>{t("budget.print_title", self.lang)}</h1>
                <div class="meta">
                    <div><b>{t("budget.print.client", self.lang)}:</b> {client}</div>
                    <div><b>{t("budget.print.nif", self.lang)}:</b> {nif}</div>
                    <div><b>{t("budget.print.date", self.lang)}:</b> {date_str}</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>{t("budget.print.description", self.lang)}</th><th>{t("budget.print.product", self.lang)}</th><th>{t("budget.print.unit", self.lang)}</th><th>{t("budget.print.quantity", self.lang)}</th><th>{t("budget.print.unit_price", self.lang)}</th><th>{t("budget.print.discount", self.lang)}</th><th>{t("budget.print.tax", self.lang)}</th><th>{t("budget.print.total", self.lang)}</th><th>{t("budget.print.notes", self.lang)}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(rows)}
                    </tbody>
                </table>
            </body>
        </html>
        """

    def save_budget_as(self):
        self._pending_preserve_state = self._capture_state()
        self._preserve_editor_after_save = True
        self.on_save_clicked()

    def clear_editor_and_model(self):
        self._clear_budget()

    def _sync_budget_header_to_vm(self):
        self._vm.budget.client = self.input_client_name.text().strip()
        self._vm.budget.nif_cif = self.input_nif_client.text().strip()
        self._vm.budget.budget_date = self.input_date.date().toPython()

    def _create_text_item(self, text: str, editable: bool = True, alignment=Qt.AlignmentFlag.AlignLeft) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def _insert_blank_line(self, record_history: bool = True):
        if record_history and not self._restoring_history:
            self._begin_history_action()
        row = self.lines_table.rowCount()
        self.lines_table.blockSignals(True)
        self.lines_table.insertRow(row)

        defaults = [
            ("", True, Qt.AlignmentFlag.AlignLeft),
            ("", True, Qt.AlignmentFlag.AlignLeft),
            (t("budget.unit_default", self.lang), True, Qt.AlignmentFlag.AlignCenter),
            ("1", True, Qt.AlignmentFlag.AlignRight),
            ("0.00", True, Qt.AlignmentFlag.AlignRight),
            ("0.00", True, Qt.AlignmentFlag.AlignRight),
            ("21.00", True, Qt.AlignmentFlag.AlignRight),
            (t("budget.zero_amount", self.lang), False, Qt.AlignmentFlag.AlignRight),
            ("", True, Qt.AlignmentFlag.AlignLeft),
        ]

        for column, (text, editable, alignment) in enumerate(defaults):
            self.lines_table.setItem(row, column, self._create_text_item(text, editable=editable, alignment=alignment))

        self.lines_table.blockSignals(False)
        self._recalculate_row_total(row)
        self._sync_view_model_from_table()
        if record_history:
            self._commit_history_action()

    def _remove_selected_line(self):
        row = self.lines_table.currentRow()
        if row >= 0:
            self._begin_history_action()
            self.lines_table.removeRow(row)
            if self.lines_table.rowCount() == 0:
                self._insert_blank_line(record_history=False)
            self._sync_view_model_from_table()
            self._commit_history_action()

    def _clear_lines_table(self):
        self._begin_history_action()
        self.lines_table.setRowCount(0)
        self._insert_blank_line(record_history=False)
        self._commit_history_action()

    def _clear_budget(self):
        self._begin_history_action()
        self.lines_table.setRowCount(0)
        self._insert_blank_line(record_history=False)
        self._vm.budget = Budget(client=t("budget.pending_client", self.lang))
        self._vm.set_budget_lines([])
        self.items_list.clear()
        self.input_client_company.clear()
        self.input_client_name.clear()
        self.input_surname.clear()
        self.input_nif_client.clear()
        self.input_date.setDate(QDate.currentDate())
        self._commit_history_action()

    def _on_line_cell_changed(self, row: int, column: int):
        if self._syncing_table:
            return
        self._recalculate_row_total(row)
        self._sync_view_model_from_table()
        self._commit_history_action()

    def _recalculate_row_total(self, row: int):
        try:
            quantity = self._parse_float(row, 3, default=0.0)
            unit_price = self._parse_float(row, 4, default=0.0)
            discount_pct = self._parse_float(row, 5, default=0.0)
            tax_pct = self._parse_float(row, 6, default=21.0)
            gross = quantity * unit_price
            net = gross - (gross * discount_pct / 100.0)
            total = net + (net * tax_pct / 100.0)
            total_item = self._create_text_item(f"{total:.2f}€", editable=False, alignment=Qt.AlignmentFlag.AlignRight)
            self._set_item_safely(row, 7, total_item)
        except Exception:
            self._set_item_safely(
                row,
                7,
                self._create_text_item(t("budget.zero_amount", self.lang), editable=False, alignment=Qt.AlignmentFlag.AlignRight),
            )

    def _parse_float(self, row: int, column: int, default: float = 0.0) -> float:
        item = self.lines_table.item(row, column)
        if item is None:
            return default
        text = item.text().strip().replace("%", "").replace("€", "")
        if not text:
            return default
        return float(text.replace(",", "."))

    def _set_item_safely(self, row: int, column: int, item: QTableWidgetItem):
        self.lines_table.blockSignals(True)
        self.lines_table.setItem(row, column, item)
        self.lines_table.blockSignals(False)

    def _collect_lines_from_table(self, strict: bool = False) -> tuple[list[BudgetLineRecord], list[str]]:
        lines: list[BudgetLineRecord] = []
        errors: list[str] = []

        for row in range(self.lines_table.rowCount()):
            description = self._item_text(row, 0)
            product = self._item_text(row, 1)
            unit = self._item_text(row, 2) or t("budget.unit_default", self.lang)
            notes = self._item_text(row, 8)

            if not any([description, product, notes, self._item_text(row, 3), self._item_text(row, 4)]):
                continue

            try:
                quantity = self._parse_float(row, 3, default=0.0)
                unit_price = self._parse_float(row, 4, default=0.0)
                discount_pct = self._parse_float(row, 5, default=0.0)
                tax_pct = self._parse_float(row, 6, default=21.0)
            except ValueError:
                errors.append(t("budget.row_invalid_numbers", self.lang, row=row + 1))
                continue

            if not description.strip():
                errors.append(t("budget.row_missing_description", self.lang, row=row + 1))
                continue
            if not product.strip():
                errors.append(t("budget.row_missing_product", self.lang, row=row + 1))
                continue
            if quantity <= 0:
                errors.append(t("budget.row_quantity_gt_zero", self.lang, row=row + 1))
                continue
            if unit_price <= 0:
                errors.append(t("budget.row_unit_price_gt_zero", self.lang, row=row + 1))
                continue

            lines.append(BudgetLineRecord(
                description=description.strip(),
                product=product.strip(),
                unit=unit.strip(),
                quantity=quantity,
                unit_price=unit_price,
                discount_pct=discount_pct,
                tax_pct=tax_pct,
                notes=notes.strip(),
            ))

        if strict and not lines:
            errors.append(t("budget.row_min_one", self.lang))

        return lines, errors

    def _validate_client_fields(self) -> tuple[str | None, QLineEdit | None]:
        required_fields: list[tuple[str, QLineEdit]] = [
            (t("budget.name", self.lang).rstrip(":"), self.input_client_name),
            (t("budget.nif", self.lang).rstrip(":"), self.input_nif_client),
        ]

        for field_label, field_widget in required_fields:
            if not field_widget.text().strip():
                return t("budget.field_required", self.lang, field=field_label), field_widget

        return None, None

    def _item_text(self, row: int, column: int) -> str:
        item = self.lines_table.item(row, column)
        return item.text().strip() if item else ""

    def _update_total_label(self, text: str):
        self.lbl_total.setText(t("budget.total_label", self.lang, amount=text))

    def _sync_view_model_from_table(self):
        self._sync_budget_header_to_vm()
        lines, _ = self._collect_lines_from_table(strict=False)
        self._vm.set_budget_lines(lines)

    def on_save_clicked(self):
        client_error, field_widget = self._validate_client_fields()
        if client_error:
            if field_widget is not None:
                field_widget.setFocus(Qt.FocusReason.OtherFocusReason)
                field_widget.selectAll()
            self.show_error_message(client_error)
            self._pending_preserve_state = None
            self._preserve_editor_after_save = False
            return

        lines, errors = self._collect_lines_from_table(strict=True)
        if errors:
            self.show_error_message("\n".join(errors))
            self._pending_preserve_state = None
            self._preserve_editor_after_save = False
            return

        self._vm.set_budget_lines(lines)
        self._sync_budget_header_to_vm()
        self._vm.save_budget(self._vm.budget.client, self._vm.budget.nif_cif, self._vm.budget.budget_date)

    def visual_list_update(self, text_items):
        self.items_list.clear()
        self.items_list.addItems(text_items)

    def show_success_message(self, budget_id: int):
        QMessageBox.information(
            self, t("budget.save_title", self.lang), t("budget.save_ok", self.lang, budget_id=budget_id)
        )
        if self._preserve_editor_after_save and self._pending_preserve_state is not None:
            state = self._pending_preserve_state
            state["budget_id"] = budget_id
            self._pending_preserve_state = None
            self._preserve_editor_after_save = False
            QTimer.singleShot(0, lambda: self._restore_state(state))
            return

        self.input_client_company.clear()
        self.input_client_name.clear()
        self.input_surname.clear()
        self.input_nif_client.clear()
        self.input_date.setDate(QDate.currentDate())
        self._clear_lines_table()

    def show_error_message(self, error_msg: str):
        QMessageBox.warning(self, t("budget.save_title", self.lang), error_msg)
        self._pending_preserve_state = None
        self._preserve_editor_after_save = False
