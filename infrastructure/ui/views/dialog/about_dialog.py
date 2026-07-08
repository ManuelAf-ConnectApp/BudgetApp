#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from infrastructure.ui.i18n import normalize_language, t
from infrastructure.ui.style import StyleApp


class AboutDialog(QDialog):
    def __init__(self, parent=None, language: str = "es"):
        super().__init__(parent)
        self.lang = normalize_language(language)
        self.setWindowTitle(t("about.title", self.lang))
        self.setMinimumWidth(360)
        self.setModal(True)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título del Software
        title_label = QLabel(t("about.software", self.lang))
        title_label.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Información de Versión y Datos de Interés
        info_text = (
            f"{t('about.version', self.lang)}"
            f"{t('about.env', self.lang)}"
            f"{t('about.support', self.lang)}"
            f"{t('about.dev', self.lang)}"
            f"{t('about.body', self.lang)}"
        )
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 13px; color: #444444; line-height: 18px;")

        # Copyright
        copyright_label = QLabel(t("about.copy", self.lang))
        copyright_label.setStyleSheet("font-size: 11px; color: #888888;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botón de Cierre
        btn_layout = QHBoxLayout()
        btn_close = QPushButton(t("about.close", self.lang))
        btn_close.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        # Añadir componentes al layout principal
        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addWidget(copyright_label)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
