#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

import os
import shutil
import sys

from PySide6.QtCore import QSettings, Signal
from PySide6.QtGui import QAction, QActionGroup, QIcon
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                               QMessageBox, QFileDialog, QDialog)

from infrastructure.ui.i18n import normalize_language, t
from infrastructure.ui.style import StyleApp
from application.budget_view_model import BudgetViewModel
from core.records import CompanyProfileRecord
from infrastructure.runtime_paths import local_database_path, resource_path
from infrastructure.ui.views.dialog.about_dialog import AboutDialog
from infrastructure.ui.views.dialog.company_dialog import CompanyConfigDialog
from infrastructure.ui.views.widgets.budget_list_view import BudgetListViewWidget
from infrastructure.ui.views.widgets.budget_view import BudgetViewWidget


class MainWindow(QMainWindow):

    reset_requested = Signal()
    language_changed = Signal(str)
    install_mode_requested = Signal(str)
    remote_connection_requested = Signal()

    def __init__(self, view_model: BudgetViewModel, language: str = "es"):
        super().__init__()
        self._vm = view_model
        self.lang = normalize_language(language)
        self._history_visible = True
        self._summary_visible = True
        self.setWindowTitle(t("app.name", self.lang))
        self.setWindowIcon(QIcon(str(resource_path("assets", "app_icon.png"))))
        self.style = StyleApp
        self.resize(1280, 1080)

        main_layout = QHBoxLayout()

        self.budget_view = BudgetViewWidget(self._vm, language=self.lang)
        self.budget_list_view = BudgetListViewWidget(self._vm, language=self.lang)

        main_layout.addWidget(self.budget_view)
        main_layout.addWidget(self.budget_list_view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self._create_menu_bar()
        self._vm.interface_refresh()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        file_menu = menu_bar.addMenu(t("main.file", self.lang))
        edit_menu = menu_bar.addMenu(t("main.edit", self.lang))
        view_menu = menu_bar.addMenu(t("main.view", self.lang))
        budget_menu = menu_bar.addMenu(t("main.budget", self.lang))
        settings_menu = menu_bar.addMenu(t("main.settings", self.lang))
        help_menu = menu_bar.addMenu(t("main.help", self.lang))

        file_menu.addAction(self._make_action(t("main.new_budget", self.lang), self._new_budget, "Ctrl+N"))
        file_menu.addAction(self._make_action(t("main.open_history", self.lang), self._open_history_panel, "Ctrl+H"))
        file_menu.addAction(self._make_action(t("main.save", self.lang), self._save_budget, "Ctrl+S"))
        file_menu.addAction(self._make_action(t("main.save_as", self.lang), self._save_budget_as, "Ctrl+Shift+S"))
        file_menu.addAction(self._make_action(t("main.export_pdf", self.lang), self._export_current_budget_pdf, "Ctrl+P"))
        file_menu.addAction(self._make_action(t("main.print", self.lang), self._print_current_budget, "Ctrl+Alt+P"))
        file_menu.addSeparator()
        file_menu.addAction(self._make_action(t("main.reset", self.lang), self._on_reset_mode_clicked))
        file_menu.addAction(self._make_action(t("main.exit", self.lang), self._on_exit_clicked, "Alt+F4"))

        edit_menu.addAction(self._make_action(t("main.undo", self.lang), self.budget_view.undo_last_change, "Ctrl+Z"))
        edit_menu.addAction(self._make_action(t("main.redo", self.lang), self.budget_view.redo_last_change, "Ctrl+Y"))
        edit_menu.addSeparator()
        edit_menu.addAction(self._make_action(t("main.new_line", self.lang), self._add_line, "Ctrl+L"))
        edit_menu.addAction(self._make_action(t("main.duplicate_line", self.lang), self.budget_view.duplicate_selected_line, "Ctrl+D"))
        edit_menu.addAction(self._make_action(t("main.delete_line", self.lang), self.budget_view.delete_selected_line, "Delete"))
        edit_menu.addAction(self._make_action(t("main.clear_budget", self.lang), self._clear_budget, "Ctrl+Shift+Delete"))

        view_menu.addAction(self._make_checkable_action(t("main.show_history", self.lang), self._toggle_history_panel, True))
        view_menu.addAction(self._make_checkable_action(t("main.show_summary", self.lang), self._toggle_summary_panel, True))
        view_menu.addSeparator()
        view_menu.addAction(self._make_action(t("main.zoom_in", self.lang), lambda: self._zoom_table(1), "Ctrl++"))
        view_menu.addAction(self._make_action(t("main.zoom_out", self.lang), lambda: self._zoom_table(-1), "Ctrl+-"))
        view_menu.addAction(self._make_action(t("main.zoom_reset", self.lang), self._reset_zoom, "Ctrl+0"))

        budget_menu.addAction(self._make_action(t("main.duplicate_budget", self.lang), self._duplicate_selected_budget))
        budget_menu.addAction(self._make_action(t("main.recalculate", self.lang), self._recalculate_budget))

        settings_mode_menu = settings_menu.addMenu(t("main.install_mode", self.lang))
        settings_mode_menu.addAction(self._make_action(t("main.install_local", self.lang), lambda: self._set_install_mode("local")))
        settings_mode_menu.addAction(self._make_action(t("main.install_remote", self.lang), lambda: self._set_install_mode("remote")))
        settings_menu.addSeparator()
        settings_menu.addAction(self._make_action(t("main.company_data", self.lang), self._open_company_dialog))
        settings_menu.addAction(self._make_action(t("main.remote_connection", self.lang), self._request_remote_connection))
        settings_menu.addAction(self._make_action(t("main.backup_db", self.lang), self._backup_local_database))
        settings_menu.addAction(self._make_action(t("main.restore_db", self.lang), self._restore_local_database))
        settings_menu.addSeparator()

        language_menu = settings_menu.addMenu(t("welcome.language", self.lang))
        language_group = QActionGroup(self)
        language_group.setExclusive(True)
        action_es = QAction(t("language.spanish", self.lang), self, checkable=True)
        action_en = QAction(t("language.english", self.lang), self, checkable=True)
        action_es.setChecked(self.lang == "es")
        action_en.setChecked(self.lang == "en")
        action_es.triggered.connect(lambda _checked=False: self._switch_language("es"))
        action_en.triggered.connect(lambda _checked=False: self._switch_language("en"))
        language_group.addAction(action_es)
        language_group.addAction(action_en)
        language_menu.addAction(action_es)
        language_menu.addAction(action_en)

        help_menu.addAction(self._make_action(t("main.about", self.lang), self._show_about_dialog, "Ctrl+A"))
        help_menu.addAction(self._make_action(t("main.manual", self.lang), self._show_quick_manual))
        help_menu.addAction(self._make_action(t("main.shortcuts", self.lang), self._show_shortcuts))
        help_menu.addAction(self._make_action(t("main.version", self.lang), self._show_version_status))
        help_menu.addAction(self._make_action(t("main.support", self.lang), self._show_support_info))

    def _make_action(self, text: str, callback, shortcut: str | None = None, checkable: bool = False):
        action = QAction(text, self)
        action.setCheckable(checkable)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.triggered.connect(callback)
        else:
            action.triggered.connect(lambda _checked=False, cb=callback: cb())
        return action

    def _make_checkable_action(self, text: str, callback, checked: bool):
        action = QAction(text, self)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(callback)
        return action

    def _show_about_dialog(self):
        dialog = AboutDialog(self, language=self.lang)
        dialog.exec()

    def _show_quick_manual(self):
        QMessageBox.information(
            self,
            t("main.manual_title", self.lang),
            t("main.manual_body", self.lang),
        )

    def _show_shortcuts(self):
        QMessageBox.information(
            self,
            t("main.shortcuts_title", self.lang),
            t("main.shortcuts_body", self.lang),
        )

    def _show_version_status(self):
        QMessageBox.information(
            self,
            t("main.version_title", self.lang),
            t("main.version_body", self.lang),
        )

    def _show_support_info(self):
        QMessageBox.information(
            self,
            t("main.support_title", self.lang),
            t("main.support_body", self.lang),
        )

    def _new_budget(self):
        self.budget_view.new_budget()

    def _save_budget(self):
        self.budget_view.on_save_clicked()

    def _save_budget_as(self):
        self.budget_view.save_budget_as()

    def _export_current_budget_pdf(self):
        self.budget_view.export_current_budget_pdf()

    def _print_current_budget(self):
        self.budget_view.print_current_budget()

    def _open_history_panel(self):
        self._history_visible = True
        self.budget_list_view.setVisible(True)
        self.budget_list_view.setFocus()

    def _toggle_history_panel(self, checked: bool):
        self._history_visible = checked
        self.budget_list_view.setVisible(checked)

    def _toggle_summary_panel(self, checked: bool):
        self._summary_visible = checked
        self.budget_view.set_summary_visible(checked)

    def _add_line(self):
        self.budget_view._insert_blank_line()

    def _clear_budget(self):
        self.budget_view.clear_editor_and_model()

    def _duplicate_selected_budget(self):
        index = self._vm.selected_history_index
        if index < 0 or index >= len(self._vm.product_catalog):
            QMessageBox.information(self, t("budget.history_title", self.lang), t("budget.select_history", self.lang))
            return
        self.budget_view.load_budget_into_editor(self._vm.product_catalog[index])

    def _recalculate_budget(self):
        self.budget_view._recalculate_all_rows()
        self.budget_view._sync_view_model_from_table()

    def _zoom_table(self, delta: int):
        header = self.budget_view.lines_table.verticalHeader()
        size = max(24, header.defaultSectionSize() + (delta * 2))
        header.setDefaultSectionSize(size)

    def _reset_zoom(self):
        self.budget_view.lines_table.verticalHeader().setDefaultSectionSize(28)

    def _open_company_dialog(self):
        dialog = CompanyConfigDialog(self, language=self.lang)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._vm.db.save_company_profile(CompanyProfileRecord(**dialog.get_data()))
            QMessageBox.information(self, t("company.title", self.lang), t("company.saved", self.lang))

    def _request_remote_connection(self):
        self.remote_connection_requested.emit()

    def _set_install_mode(self, mode: str):
        self.install_mode_requested.emit(mode)

    def _backup_local_database(self):
        if not self._is_local_database():
            QMessageBox.information(self, t("main.backup_title", self.lang), t("main.backup_only_local", self.lang))
            return

        source_path = self._local_db_path()
        if not os.path.exists(source_path):
            QMessageBox.warning(self, t("main.backup_title", self.lang), t("main.backup_missing", self.lang))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("main.backup_title", self.lang),
            t("main.backup_default_name", self.lang),
            t("main.sqlite_filter", self.lang),
        )
        if not file_path:
            return

        shutil.copy2(source_path, file_path)
        QMessageBox.information(self, t("main.backup_title", self.lang), t("main.backup_ok", self.lang, path=file_path))

    def _restore_local_database(self):
        if not self._is_local_database():
            QMessageBox.information(self, t("main.restore_title", self.lang), t("main.backup_only_local", self.lang))
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("main.restore_title", self.lang),
            "",
            t("main.sqlite_filter", self.lang),
        )
        if not file_path:
            return

        target_path = self._local_db_path()
        shutil.copy2(file_path, target_path)
        QMessageBox.information(self, t("main.restore_title", self.lang), t("main.restore_ok", self.lang))

    def _is_local_database(self) -> bool:
        return hasattr(self._vm.db, "create_database") and getattr(self._vm.db.create_database, "is_local", False)

    def _local_db_path(self) -> str:
        return str(local_database_path("my_budgets.db"))

    def _on_reset_mode_clicked(self):
        print(t("main.reset_step1", self.lang))
        reply = QMessageBox.question(
            self,
            t("main.reset_title", self.lang),
            t("main.reset_question", self.lang),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            settings = QSettings("Connect App ES", "Budget App")

            settings.remove("install_mode")
            print(t("main.reset_step2", self.lang))
            self.reset_requested.emit()

    def _switch_language(self, language: str):
        language = normalize_language(language)
        self.lang = language
        settings = QSettings("Connect App ES", "Budget App")
        settings.setValue("ui_language", language)
        self.language_changed.emit(language)

    def _on_exit_clicked(self):
        self.close()
        sys.exit(0)
