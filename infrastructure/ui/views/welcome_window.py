#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from PySide6.QtCore import Qt, QSettings
from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox

from infrastructure.ui.i18n import normalize_language, t


class WelcomeWindow(QWidget):
    def __init__(self, language: str, on_local_clicked, on_remote_clicked, on_language_changed):
        super().__init__()
        self.settings = QSettings("Connect App ES", "Budget App")
        self.lang = normalize_language(language)

        self._on_local_clicked = on_local_clicked
        self._on_remote_clicked = on_remote_clicked
        self._on_language_changed = on_language_changed

        self.setFixedSize(600, 500)

        self.language_label = QLabel()
        self.language_combo = QComboBox()
        self.language_combo.currentIndexChanged.connect(self._handle_language_change)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 20px;")

        self.local_button = QPushButton()
        self.local_button.setStyleSheet("font-size: 14px; font-weight: bold; padding: 15px;")

        self.remote_button = QPushButton()
        self.remote_button.setStyleSheet("font-size: 14px; font-weight: bold; padding: 15px;")

        language_layout = QHBoxLayout()
        language_layout.addStretch(1)
        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(language_layout)
        layout.addWidget(self.title_label)
        layout.addWidget(self.local_button)
        layout.addWidget(self.remote_button)

        self.setLayout(layout)

        self.retranslate(self.lang)

        self.local_button.clicked.connect(self._handle_local)
        self.remote_button.clicked.connect(self._handle_remote)

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
        self.setWindowTitle(t("app.start", self.lang))
        self.title_label.setText(t("welcome.title", self.lang))
        self.local_button.setText(t("welcome.local", self.lang))
        self.remote_button.setText(t("welcome.remote", self.lang))
        self.language_label.setText(f"{t('welcome.language', self.lang)}:")
        self._populate_language_combo()

    def _handle_language_change(self):
        language = normalize_language(self.language_combo.currentData())
        self.settings.setValue("ui_language", language)
        self.retranslate(language)
        self._on_language_changed(language)

    def _handle_local(self):
        self.close()
        self._on_local_clicked()

    def _handle_remote(self):
        self.close()
        self._on_remote_clicked()
