#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox

from infrastructure.ui.i18n import normalize_language, t
from infrastructure.ui.style import StyleApp


class CompanyConfigDialog(QDialog):
    def __init__(self, parent=None, language: str = "es"):
        super().__init__(parent)
        self.lang = normalize_language(language)
        self.setWindowTitle(t("company.title", self.lang))
        self.setMinimumWidth(400)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(t("company.name", self.lang).replace(" *:", ""))

        self.input_cif = QLineEdit()
        self.input_cif.setPlaceholderText(t("company.cif", self.lang).replace(" *:", ""))

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText(t("company.address", self.lang).replace(":", ""))

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText(t("company.email", self.lang).replace(":", ""))

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText(t("company.phone", self.lang).replace(":", ""))

        form_layout.addRow(t("company.name", self.lang), self.input_name)
        form_layout.addRow(t("company.cif", self.lang), self.input_cif)
        form_layout.addRow(t("company.address", self.lang), self.input_address)
        form_layout.addRow(t("company.email", self.lang), self.input_email)
        form_layout.addRow(t("company.phone", self.lang), self.input_phone)

        self.btn_save = QPushButton(t("company.save", self.lang))
        self.btn_save.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.btn_save)
        self.setLayout(main_layout)

    def _connect_signals(self):
        self.btn_save.clicked.connect(self.on_save_clicked)

    def on_save_clicked(self):
        """Valida que los campos mínimos obligatorios estén rellenos."""
        if not self.input_name.text().strip() or not self.input_cif.text().strip():
            QMessageBox.warning(self, t("company.title", self.lang), t("company.required", self.lang))
            return

        # Si todo es correcto, cerramos el diálogo con éxito
        self.accept()

    def get_data(self) -> dict:
        """Devuelve un diccionario listo para enviar a la base de datos."""
        return {
            "name": self.input_name.text().strip(),
            "cif": self.input_cif.text().strip().upper(),
            "address": self.input_address.text().strip(),
            "email": self.input_email.text().strip(),
            "phone": self.input_phone.text().strip()
        }
