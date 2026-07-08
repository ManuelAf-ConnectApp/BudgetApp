#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from core.model.budget import Budget
from infrastructure.ui.i18n import normalize_language, t
from infrastructure.ui.style import StyleApp


class BudgetListViewWidget(QWidget):
    def __init__(self, vm, language: str = "es"):
        super().__init__()
        self._vm = vm
        self.lang = normalize_language(language)

        self._setup_ui()
        self._connect_signals()

        # Carga inicial
        self._vm.load_budget_list()

    def _setup_ui(self):
        """Inicializa y organiza la estructura visual del listado en formato tabla."""
        main_layout = QVBoxLayout()

        list_components = self._create_list_components()
        action_components = self._create_action_components()

        main_layout.addLayout(list_components)
        main_layout.addLayout(action_components)

        self.setLayout(main_layout)

    def _create_list_components(self) -> QVBoxLayout:
        """Construye el título y la tabla estilo Excel."""
        layout = QVBoxLayout()

        budget_list_title = QLabel(t("budget.history_title", self.lang))
        budget_list_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")

        # 💥 COMPONENTE CLAVE: Cambiamos a QTableWidget
        self.budget_list_widget = QTableWidget()
        self.budget_list_widget.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)

        # 1. Definimos las 5 columnas de nuestro Excel
        self.budget_list_widget.setColumnCount(4)
        self.budget_list_widget.setHorizontalHeaderLabels([
            t("budget.col_client", self.lang),
            t("budget.col_nif", self.lang),
            t("budget.col_date", self.lang),
            t("budget.col_total", self.lang),
        ])

        # 2. Comportamiento profesional de selección
        self.budget_list_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)  # Selecciona la fila entera
        self.budget_list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)  # Solo una fila a la vez
        self.budget_list_widget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)  # No editable al hacer doble clic

        # 3. Ajustes estéticos de las columnas
        self.budget_list_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)  # Se estiran solas
        self.budget_list_widget.verticalHeader().setVisible(False)  # Ocultamos el número de fila de la izquierda

        layout.addWidget(budget_list_title)
        layout.addWidget(self.budget_list_widget)
        return layout

    def _create_action_components(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        self.btn_export_pdf = QPushButton(t("budget.export_pdf", self.lang))
        self.btn_export_pdf.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        layout.addWidget(self.btn_export_pdf)
        return layout

    def _connect_signals(self):
        self.btn_export_pdf.clicked.connect(self.on_export_pdf_clicked)

        # 💥 Al pinchar en cualquier celda, capturamos la fila entera
        self.budget_list_widget.cellClicked.connect(self.on_row_selected)

        # Escuchamos la lista de objetos del ViewModel
        self._vm.budget_list.connect(self.update_visual_list)
        self._vm.pdf_export_success.connect(self.show_pdf_success)
        self._vm.pdf_export_error.connect(self.show_pdf_error)

    # --- COMPORTAMIENTOS Y SLOTS ---

    def on_row_selected(self, row: int, column: int):
        """Avisa al ViewModel de qué número de fila ha pinchado el usuario."""
        self._vm.set_selected_budget_index(row)

    def update_visual_list(self, budgets: list[Budget]):
        """Puebla la tabla desglosando cada objeto Budget en sus columnas correspondientes."""
        self.budget_list_widget.setRowCount(0)  # Limpieza higiénica de la tabla

        for row_idx, b in enumerate(budgets):
            self.budget_list_widget.insertRow(row_idx)

            # 1. Creamos las celdas de texto plano (QTableWidgetItem)
            item_id = QTableWidgetItem(f"#{b.budget_id}")
            item_client = QTableWidgetItem(str(b.client))
            item_nif = QTableWidgetItem(str(b.nif_cif or "-"))

            # Formateamos la fecha si viene como objeto date
            fecha_str = b.budget_date.strftime("%d/%m/%Y") if hasattr(b.budget_date, "strftime") else str(b.budget_date)
            item_date = QTableWidgetItem(fecha_str)

            item_total = QTableWidgetItem(f"{b.total:.2f}€")

            # 2. 🎨 Alineaciones estéticas estilo Excel (Números al centro/derecha, texto a la izquierda)
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_nif.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # 3. Inyectamos las celdas en sus respectivas columnas (0 a 4)
            self.budget_list_widget.setItem(row_idx, 0, item_client)
            self.budget_list_widget.setItem(row_idx, 1, item_nif)
            self.budget_list_widget.setItem(row_idx, 2, item_date)
            self.budget_list_widget.setItem(row_idx, 3, item_total)

    def on_export_pdf_clicked(self):
        try:
            if self._vm.selected_history_index < 0:
                self.show_pdf_error(t("budget.export_select", self.lang))
                return

            selected_budget: Budget = self._vm.product_catalog[self._vm.selected_history_index]
            nombre_limpio = selected_budget.client.replace(" ", "_")
            suggested_name = t("budget.export_name", self.lang, name=nombre_limpio)

            file_path, _ = QFileDialog.getSaveFileName(
                self, t("budget.export_title", self.lang), suggested_name, t("budget.pdf_filter", self.lang)
            )

            if not file_path:
                return

            self._vm.budget.client = selected_budget.client
            self._vm.budget.nif_cif = selected_budget.nif_cif
            self._vm.budget.budget_date = selected_budget.budget_date
            self._vm.budget.budget_lines = selected_budget.budget_lines

            self._vm.export_current_budget_to_pdf(file_path)

        except Exception as e:
            self.show_pdf_error(t("budget.export_error", self.lang, error=str(e)))

    def show_pdf_error(self, error_msg: str):
        QMessageBox.warning(self, t("budget.export_error_title", self.lang), error_msg)

    def show_pdf_success(self, path: str):
        QMessageBox.information(self, t("budget.export_success_title", self.lang), t("budget.export_success", self.lang, path=path))
