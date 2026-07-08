#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

class StyleApp:
    MODERN_STYLE_SHEET = """
            /* Fondo general de la aplicación */
            QMainWindow, QWidget {
                background-color: #F8FAFC;  /* Un blanco roto/grisáceo muy limpio */
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #1E293B;  /* Azul oscuro casi negro para los textos */
            }

            /* Cajas de texto (Inputs) */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 10px;
                background-color: #FFFFFF;
            }
            
            #remoteBanner {
                background-color: #e3f2fd;       /* Azul claro de información */
                color: #0d47a1;                  /* Texto azul oscuro de alto contraste */
                border: 1px solid #bbdefb;       /* Borde suave a juego */
                border-radius: 6px;              /* Esquinas redondeadas estilo ERP moderno */
                padding: 12px 16px;              /* Margen interno para que respire el texto */
                font-size: 13px;                 /* Tamaño de letra legible pero estilizado */
            }

            /* Efecto cuando el usuario hace clic en una caja de texto */
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3B82F6;  /* Borde azul brillante */
            }

            /* Las cajas grupales (Información de cliente, líneas, etc.) */
            QGroupBox {
                width: 100%;
                font-weight: bold;
                font-size: 14px;
                color: #0F172A;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 16px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 4px;
            }

            /* Listado de Presupuestos (QListWidget) */
            QListWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background-color: #FFFFFF;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:hover {
                background-color: #F1F5F9;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
                border-radius: 4px;
            }

            /* Botón Secundario (Limpiar, Volver...) */
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                color: #475569;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }

            /* Botón Principal (Guardar, Agregar...) - Estilo "Accent" */
            QPushButton#btn_principal {
                background-color: #0F172A;  /* Slate oscuro muy elegante */
                color: #FFFFFF;
                border: none;
            }
            QPushButton#btn_principal:hover {
                background-color: #1E293B;
            }
            QPushButton#btn_principal:pressed {
                background-color: #334155;
            }
            
            /* --- BARRA DE MENÚ SUPERIOR --- */
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                color: #333333;
            }
            
            /* 💥 SOLUCIÓN: Efecto hover para el menú horizontal superior */
            QMenuBar::item:selected {
                background-color: #f5f5f5;
                border-radius: 4px;
                color: #000000;
            }
            
            /* --- MENÚS DESPLEGABLES --- */
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 6px 24px 6px 12px;
                color: #333333;
            }
            
            /* 💥 SOLUCIÓN: Efecto hover para las opciones desplegables */
            QMenu::item:selected {
                background-color: #0d47a1;  /* El azul corporativo de tu app */
                color: #ffffff;             /* Texto blanco para alto contraste */
                border-radius: 4px;
            }
            
        """
