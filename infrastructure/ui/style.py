class StyleApp:
    """Shared visual language for the desktop workspace."""

    MODERN_STYLE_SHEET = """
        QMainWindow, QWidget { background: #F6F8FC; color: #172033; font-family: "Segoe UI", "Inter", Arial, sans-serif; font-size: 13px; }
        QMainWindow::separator { background: #E2E8F0; width: 1px; height: 1px; }
        QMenuBar { background: #FFFFFF; border-bottom: 1px solid #E2E8F0; padding: 2px 8px; }
        QMenuBar::item { padding: 7px 10px; border-radius: 5px; }
        QMenuBar::item:selected, QMenu::item:selected { background: #EAF2FF; color: #1D4ED8; }
        QMenu { background: #FFFFFF; border: 1px solid #D9E2EF; padding: 5px; }
        QMenu::item { padding: 7px 28px 7px 10px; border-radius: 4px; }
        QToolBar { background: #FFFFFF; border: none; border-bottom: 1px solid #E2E8F0; padding: 9px 16px; spacing: 8px; }
        QToolButton { padding: 7px 10px; border-radius: 6px; }
        QToolButton:hover { background: #F1F5F9; }
        QLineEdit, QComboBox, QDateEdit { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 7px; padding: 7px 10px; min-height: 18px; }
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border: 2px solid #2563EB; padding: 6px 9px; }
        QGroupBox, QFrame#workspaceCard, QFrame#summaryPanel, QFrame#historyPanel { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; }
        QGroupBox { font-weight: 700; font-size: 14px; margin-top: 12px; padding: 18px 14px 14px; }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
        QLabel#workspaceTitle { font-size: 20px; font-weight: 700; color: #0F172A; }
        QLabel#sectionTitle { font-size: 15px; font-weight: 700; color: #172033; }
        QLabel#mutedText { color: #64748B; }
        QLabel#totalCaption { color: #64748B; font-weight: 600; }
        QLabel#totalAmount { color: #0F172A; font-size: 25px; font-weight: 750; }
        QLabel#summaryValue { font-weight: 600; color: #334155; }
        QLabel#statusPill, QComboBox#statusPill { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; border-radius: 12px; padding: 4px 9px; font-weight: 700; }
        QPushButton { background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 7px; color: #334155; font-weight: 600; padding: 8px 13px; min-height: 18px; }
        QPushButton:hover { background: #F8FAFC; border-color: #94A3B8; }
        QPushButton#primaryButton { background: #2563EB; color: #FFFFFF; border: 1px solid #2563EB; }
        QPushButton#primaryButton:hover { background: #1D4ED8; border-color: #1D4ED8; }
        QPushButton#quietButton { border-color: transparent; background: transparent; color: #475569; }
        QPushButton#quietButton:hover { background: #F1F5F9; }
        QTableWidget { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; gridline-color: #EEF2F7; }
        QTableWidget::item { padding: 7px 8px; border-bottom: 1px solid #EEF2F7; }
        QTableWidget::item:selected { background: #EAF2FF; color: #172033; }
        QHeaderView::section { background: #F8FAFC; color: #475569; border: none; border-bottom: 1px solid #E2E8F0; padding: 8px; font-weight: 700; }
        QScrollBar:vertical { background: transparent; width: 10px; margin: 4px; }
        QScrollBar::handle:vertical { background: #CBD5E1; border-radius: 5px; min-height: 25px; }
        QSplitter::handle { background: #E2E8F0; width: 1px; }
    """
