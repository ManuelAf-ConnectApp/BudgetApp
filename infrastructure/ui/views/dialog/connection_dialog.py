#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import mysql.connector
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox,
    QHBoxLayout, QLabel, QComboBox
)

from infrastructure.ui.style import StyleApp
from infrastructure.ui.i18n import normalize_language, t


class ConnectionDialog(QDialog):
    def __init__(self, language: str = "es"):
        super().__init__()
        self.lang = normalize_language(language)
        self.setWindowTitle(t("connection.title", self.lang))
        self.resize(500, 400)

        self.settings = QSettings("Connect App ES", "Budget App")

        # --- Form ---

        layout = QVBoxLayout()
        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.currentIndexChanged.connect(lambda _index=0: self._handle_language_change())

        top_bar = QHBoxLayout()
        top_bar.addStretch(1)
        top_bar.addWidget(self.language_label, 0, Qt.AlignmentFlag.AlignRight)
        top_bar.addWidget(self.language_combo, 0, Qt.AlignmentFlag.AlignRight)

        self.note_label = QLabel(t("connection.note", self.lang))
        self.note_label.setWordWrap(True)
        self.note_label.setObjectName("remoteBanner")

        form_layout = QFormLayout()

        layout.addLayout(top_bar)
        layout.addWidget(self.note_label)

        self.input_host = QLineEdit()
        self.input_host.setPlaceholderText(t("connection.host_placeholder", self.lang))

        self.input_db = QLineEdit()
        self.input_db.setPlaceholderText(t("connection.db_placeholder", self.lang))

        self.input_user = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Preload data if it already exists
        self.input_host.setText(self.settings.value("remote_host", ""))
        self.input_db.setText(self.settings.value("remote_db", ""))
        self.input_user.setText(self.settings.value("remote_username", ""))

        form_layout.addRow(t("connection.host", self.lang), self.input_host)
        form_layout.addRow(t("connection.db", self.lang), self.input_db)
        form_layout.addRow(t("connection.user", self.lang), self.input_user)
        form_layout.addRow(t("connection.password", self.lang), self.input_password)

        self.btn_save = QPushButton(t("connection.save", self.lang))
        self.btn_save.clicked.connect(self._handle_save)

        self.btn_back = QPushButton(t("connection.back", self.lang))
        self.btn_back.clicked.connect(self.reject)

        layout_btn = QHBoxLayout()

        layout_btn.addWidget(self.btn_save)
        layout_btn.addWidget(self.btn_back)

        layout.addLayout(form_layout)
        layout.addLayout(layout_btn)
        self.setLayout(layout)
        self.retranslate(self.lang)

    def _populate_language_combo(self):
        current_language = self.language_combo.currentData()
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        self.language_combo.addItem(t("language.spanish", self.lang), "es")
        self.language_combo.addItem(t("language.english", self.lang), "en")
        index = self.language_combo.findData(current_language if current_language else self.lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
        self.language_combo.blockSignals(False)

    def retranslate(self, language: str):
        self.lang = normalize_language(language)
        self.setWindowTitle(t("connection.title", self.lang))
        self.language_label.setText(f"{t('welcome.language', self.lang)}:")
        self.note_label.setText(t("connection.note", self.lang))
        self.input_host.setPlaceholderText(t("connection.host_placeholder", self.lang))
        self.input_db.setPlaceholderText(t("connection.db_placeholder", self.lang))
        self.btn_save.setText(t("connection.save", self.lang))
        self.btn_back.setText(t("connection.back", self.lang))
        self._populate_language_combo()

    def _handle_language_change(self):
        language = normalize_language(self.language_combo.currentData())
        self.settings.setValue("ui_language", language)
        self.retranslate(language)

    def _handle_save(self):
        host = self.input_host.text().strip()
        db = self.input_db.text().strip()
        user = self.input_user.text().strip()
        password = self.input_password.text()

        if not host or not db or not user or not password:
            QMessageBox.information(self, t("connection.title", self.lang), t("connection.empty", self.lang))
            return

        try:
            conn = mysql.connector.connect(host=host, database=db, user=user, password=password)
            conn.close()
            QMessageBox.information(self, t("connection.success_title", self.lang), t("connection.success", self.lang))

        except Exception as e:
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setWindowTitle(t("connection.error_title", self.lang))
            error_box.setText(t("connection.error", self.lang))
            error_box.setInformativeText(str(e))
            error_box.exec()
            return

        self.settings.setValue("remote_host", host)
        self.settings.setValue("remote_db", db)
        self.settings.setValue("remote_username", user)
        self.settings.setValue("remote_password", password)
        self.accept()
