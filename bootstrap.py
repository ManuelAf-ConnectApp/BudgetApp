#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import QSettings

from application.budget_view_model import BudgetViewModel
from core.records import CompanyProfileRecord
from infrastructure.database.local_database import LocalDatabase
from infrastructure.database.remote_database import RemoteDatabase
from infrastructure.runtime_paths import local_database_path, resource_path
from infrastructure.ui.i18n import DEFAULT_LANGUAGE, normalize_language
from infrastructure.ui.style import StyleApp
from infrastructure.ui.views.dialog.company_dialog import CompanyConfigDialog
from infrastructure.ui.views.dialog.connection_dialog import ConnectionDialog
from infrastructure.ui.views.main_window import MainWindow
from infrastructure.ui.views.welcome_window import WelcomeWindow


def check_and_route_company_profile(db_instance, language: str):
    profile = db_instance.get_company_profile()

    if not profile:
        company_config_dialog = CompanyConfigDialog(language=language)

        if company_config_dialog.exec() == QDialog.DialogCode.Accepted:
            tax_details = company_config_dialog.get_data()
            db_instance.save_company_profile(CompanyProfileRecord(**tax_details))
        else:
            return False

    return True


class AppController:
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Budget App")
        self.app.setApplicationDisplayName("Budget App")
        self.app.setWindowIcon(QIcon(str(resource_path("assets", "app_icon.png"))))
        self.main_window = None
        self.welcome_window = None

        self.settings = QSettings("Connect App ES", "Budget App")
        if not self.settings.value("ui_language"):
            self.settings.setValue("ui_language", DEFAULT_LANGUAGE)

        if hasattr(StyleApp, "MODERN_STYLE_SHEET"):
            self.app.setStyleSheet(StyleApp.MODERN_STYLE_SHEET)

    def start(self):
        saved_mode = self.settings.value("install_mode")
        saved_language = normalize_language(self.settings.value("ui_language"))

        if saved_mode == "local":
            self.start_local_flow(save_preference=False, language=saved_language)
        elif saved_mode == "remote":
            self.start_remote_flow(save_preference=False, language=saved_language)
        else:
            self._show_welcome_window(language=saved_language)

        sys.exit(self.app.exec())

    def _show_welcome_window(self, language: str):
        if self.welcome_window:
            self.welcome_window.close()
            self.welcome_window = None

        self.welcome_window = WelcomeWindow(
            language=language,
            on_local_clicked=self._on_local_btn_clicked,
            on_remote_clicked=self._on_remote_btn_clicked,
            on_language_changed=self._on_language_changed,
        )
        self.welcome_window.show()

    def _on_local_btn_clicked(self):
        if self.welcome_window:
            self.welcome_window.close()
            self.welcome_window = None
        self.start_local_flow(save_preference=True, language=normalize_language(self.settings.value("ui_language")))

    def _on_remote_btn_clicked(self):
        if self.welcome_window:
            self.welcome_window.close()
            self.welcome_window = None
        self.start_remote_flow(save_preference=True, language=normalize_language(self.settings.value("ui_language")))

    def _on_language_changed(self, language: str):
        language = normalize_language(language)
        self.settings.setValue("ui_language", language)

        if self.main_window:
            self.main_window.close()
            self.main_window = None

        if self.welcome_window:
            self.welcome_window.retranslate(language)

        saved_mode = self.settings.value("install_mode")
        if saved_mode == "local":
            self.start_local_flow(save_preference=False, language=language)
        elif saved_mode == "remote":
            self.start_remote_flow(save_preference=False, language=language)

    def start_local_flow(self, save_preference: bool, language: str):
        if save_preference:
            self.settings.setValue("install_mode", "local")

        local_db = LocalDatabase()

        if not check_and_route_company_profile(local_db, language):
            self.settings.remove("install_mode")
            self._show_welcome_window(language)
            return

        view_model = BudgetViewModel(local_db, language=language)
        self.main_window = MainWindow(view_model, language=language)
        self.main_window.reset_requested.connect(self._handle_live_reset)
        self.main_window.language_changed.connect(self._on_language_changed)
        self.main_window.install_mode_requested.connect(self._on_install_mode_requested)
        self.main_window.remote_connection_requested.connect(self._on_remote_connection_requested)
        self.main_window.show()

    def start_remote_flow(self, save_preference: bool, language: str):
        if save_preference:
            self.settings.setValue("install_mode", "remote")

        host = self.settings.value("remote_host")
        db = self.settings.value("remote_db")
        username = self.settings.value("remote_username")
        password = self.settings.value("remote_password")

        if not host or not db or not username or not password:
            dialog = ConnectionDialog(language=language)

            if dialog.exec() != QDialog.DialogCode.Accepted:
                self.settings.remove("install_mode")
                self._show_welcome_window(language)
                return

            host = self.settings.value("remote_host")
            db = self.settings.value("remote_db")
            username = self.settings.value("remote_username")
            password = self.settings.value("remote_password")

        self._open_main_window_remote(host, db, username, password, language)

    def _on_install_mode_requested(self, mode: str):
        language = normalize_language(self.settings.value("ui_language"))

        if self.main_window:
            self.main_window.close()
            self.main_window = None

        if mode == "local":
            self.start_local_flow(save_preference=True, language=language)
        elif mode == "remote":
            self.start_remote_flow(save_preference=True, language=language)

    def _on_remote_connection_requested(self):
        language = normalize_language(self.settings.value("ui_language"))
        dialog = ConnectionDialog(language=language)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        host = self.settings.value("remote_host")
        db = self.settings.value("remote_db")
        username = self.settings.value("remote_username")
        password = self.settings.value("remote_password")

        if not host or not db or not username or not password:
            return

        self.settings.setValue("install_mode", "remote")
        self._open_main_window_remote(host, db, username, password, language)

    def _open_main_window_remote(self, host: str, db: str, username: str, password: str, language: str):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        db_remote = RemoteDatabase(host=host, database=db, user=username, password=password)
        view_model = BudgetViewModel(db_remote, language=language)

        self.main_window = MainWindow(view_model, language=language)
        self.main_window.reset_requested.connect(self._handle_live_reset)
        self.main_window.language_changed.connect(self._on_language_changed)
        self.main_window.install_mode_requested.connect(self._on_install_mode_requested)
        self.main_window.remote_connection_requested.connect(self._on_remote_connection_requested)
        self.main_window.show()

    def _handle_live_reset(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.settings.remove("install_mode")
        self.settings.remove("remote_host")
        self.settings.remove("remote_db")
        self.settings.remove("remote_username")
        self.settings.remove("remote_password")

        db_path = local_database_path("my_budgets.db")

        if db_path.exists():
            try:
                db_path.unlink()
                print("Base de datos local eliminada con éxito")
            except Exception as e:
                print(f"Aviso: No se puede eliminar base de datos local (puede estar en uso): {str(e)}")

        self._show_welcome_window(normalize_language(self.settings.value("ui_language")))


def run_app():
    controller = AppController()
    controller.start()
