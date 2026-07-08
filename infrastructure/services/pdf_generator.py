#
# Author: Manuel Maria Alconchel Fernandez
# E-mail: incidencias@connectapp.es
# Date: 30/06/2026
#
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.model.budget import Budget
from core.model.company import Company
from infrastructure.runtime_paths import resource_path


def format_budget_reference(value) -> str:
    try:
        budget_id = int(value)
    except (TypeError, ValueError):
        return "N/D"
    return str(budget_id) if budget_id > 0 else "N/D"


class PDFGenerator:
    BRAND_COLOR = colors.HexColor("#1A365D")
    ACCENT_COLOR = colors.HexColor("#2B6CB0")
    SOFT_BG = colors.HexColor("#F7FAFC")
    GRID_COLOR = colors.HexColor("#D9E2EC")
    TEXT_COLOR = colors.HexColor("#1F2937")
    MUTED_TEXT = colors.HexColor("#5B677A")

    @staticmethod
    def generate_budget_pdf(budget: Budget, company: Company, file_path: str):
        """Genera un archivo PDF profesional a partir de un objeto Budget."""

        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=34 * mm,
            bottomMargin=20 * mm,
        )
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=PDFGenerator.BRAND_COLOR,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "SubtitleStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=PDFGenerator.MUTED_TEXT,
        )
        meta_style = ParagraphStyle(
            "MetaStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=PDFGenerator.TEXT_COLOR,
        )
        small_style = ParagraphStyle(
            "SmallStyle",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=PDFGenerator.MUTED_TEXT,
        )

        def money(value: float) -> str:
            return f"{value:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")

        def fmt_date(value) -> str:
            if hasattr(value, "strftime"):
                return value.strftime("%d/%m/%Y")
            return str(value)

        def canvas_text(value: str) -> str:
            return str(value or "-")

        def rich_text(value: str) -> str:
            return escape(canvas_text(value)).replace("\n", "<br/>")

        def draw_header_footer(canvas, doc_obj):
            canvas.saveState()

            width, height = A4
            left = doc.leftMargin
            right = width - doc.rightMargin

            canvas.setFillColor(PDFGenerator.BRAND_COLOR)
            canvas.rect(0, height - 22 * mm, width, 22 * mm, stroke=0, fill=1)

            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 16)
            canvas.drawString(left, height - 11 * mm, canvas_text(company.name))
            canvas.setFont("Helvetica", 8.5)
            canvas.drawRightString(right, height - 11 * mm, f"Presupuesto #{format_budget_reference(budget.budget_id)}")

            canvas.setFillColor(PDFGenerator.TEXT_COLOR)
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(left, height - 27 * mm, "PRESUPUESTO")
            canvas.setFont("Helvetica", 8.5)
            canvas.drawRightString(right, height - 27 * mm, f"Fecha: {fmt_date(budget.budget_date)}")

            canvas.setStrokeColor(PDFGenerator.GRID_COLOR)
            canvas.setLineWidth(0.7)
            canvas.line(left, doc.bottomMargin - 6, right, doc.bottomMargin - 6)

            canvas.setFillColor(PDFGenerator.MUTED_TEXT)
            canvas.setFont("Helvetica", 8)
            footer_left = f"{canvas_text(company.address)}"
            footer_center = f"{canvas_text(company.email)}"
            footer_right = f"{canvas_text(company.phone)} | Página {doc_obj.page}"
            canvas.drawString(left, 12 * mm, footer_left[:80])
            canvas.drawCentredString(width / 2, 12 * mm, footer_center[:80])
            canvas.drawRightString(right, 12 * mm, footer_right[:80])

            canvas.restoreState()

        def section_block(title: str, body: str) -> Table:
            block = Table(
                [[Paragraph(f"<b>{title}</b>", meta_style)], [Paragraph(body, meta_style)]],
                colWidths=[86 * mm],
            )
            block.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PDFGenerator.SOFT_BG),
                        ("TEXTCOLOR", (0, 0), (-1, -1), PDFGenerator.TEXT_COLOR),
                        ("BOX", (0, 0), (-1, -1), 0.7, PDFGenerator.GRID_COLOR),
                        ("INNERPADDING", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            return block

        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"Presupuesto #{format_budget_reference(budget.budget_id)}", title_style))
        story.append(Paragraph(f"Documento comercial generado para {rich_text(budget.client)}", subtitle_style))
        story.append(Spacer(1, 4 * mm))

        date_str = fmt_date(budget.budget_date)
        info_table = Table(
            [[
                section_block(
                    "Empresa emisora",
                    f"{rich_text(company.name)}<br/>"
                    f"CIF: {rich_text(company.cif)}<br/>"
                    f"{rich_text(company.address)}<br/>"
                    f"{rich_text(company.email)}<br/>"
                    f"{rich_text(company.phone)}",
                ),
                section_block(
                    "Cliente",
                    f"{rich_text(budget.client)}<br/>"
                    f"NIF/CIF: {rich_text(budget.nif_cif)}<br/>"
                    f"Fecha: {date_str}",
                ),
            ]],
            colWidths=[86 * mm, 86 * mm],
        )
        info_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        story.append(info_table)
        story.append(Spacer(1, 6 * mm))

        table_data = [[
            Paragraph("<b>Descripción</b>", meta_style),
            Paragraph("<b>Producto</b>", meta_style),
            Paragraph("<b>Unidad</b>", meta_style),
            Paragraph("<b>Cant.</b>", meta_style),
            Paragraph("<b>P. Unit.</b>", meta_style),
            Paragraph("<b>Dto.</b>", meta_style),
            Paragraph("<b>IVA</b>", meta_style),
            Paragraph("<b>Total</b>", meta_style),
            Paragraph("<b>Obs.</b>", meta_style),
        ]]

        for line in budget.budget_lines:
            prod_name = line.product.name if hasattr(line.product, "name") else str(line.product)
            table_data.append([
                Paragraph(rich_text(line.description), meta_style),
                Paragraph(rich_text(prod_name), meta_style),
                Paragraph(rich_text(line.unit or "-"), meta_style),
                Paragraph(f"{line.quantity:.2f}", meta_style),
                Paragraph(money(line.unit_price), meta_style),
                Paragraph(f"{line.discount_pct:.2f}%", meta_style),
                Paragraph(f"{line.tax_pct:.2f}%", meta_style),
                Paragraph(money(line.line_total), meta_style),
                Paragraph(rich_text(line.notes or "-"), meta_style),
            ])

        subtotal = sum(line.gross_amount for line in budget.budget_lines)
        discount_total = sum(line.discount_amount for line in budget.budget_lines)
        taxable_total = sum(line.taxable_amount for line in budget.budget_lines)
        tax_total = sum(line.tax_amount for line in budget.budget_lines)
        grand_total = budget.total

        summary_table = Table(
            [
                ["Subtotal", money(subtotal)],
                ["Descuento total", money(discount_total)],
                ["Base imponible", money(taxable_total)],
                ["IVA", money(tax_total)],
                ["Total", money(grand_total)],
            ],
            colWidths=[55 * mm, 35 * mm],
            hAlign="RIGHT",
        )
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -2), colors.white),
                    ("BACKGROUND", (0, -1), (-1, -1), PDFGenerator.SOFT_BG),
                    ("TEXTCOLOR", (0, 0), (-1, -1), PDFGenerator.TEXT_COLOR),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("BOX", (0, 0), (-1, -1), 0.8, PDFGenerator.GRID_COLOR),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, PDFGenerator.GRID_COLOR),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        item_table = Table(
            table_data,
            colWidths=[42 * mm, 28 * mm, 10 * mm, 12 * mm, 18 * mm, 12 * mm, 12 * mm, 20 * mm, 20 * mm],
            repeatRows=1,
            splitByRow=1,
        )
        item_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PDFGenerator.BRAND_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9.2),
                    ("ALIGN", (2, 1), (7, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDFGenerator.SOFT_BG]),
                    ("GRID", (0, 0), (-1, -1), 0.4, PDFGenerator.GRID_COLOR),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        story.append(item_table)
        story.append(Spacer(1, 6 * mm))
        story.append(summary_table)
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("Documento generado electrónicamente por Budget App.", small_style))

        doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)

    @staticmethod
    def generate_application_manual_pdf(file_path: str, language: str = "es"):
        """Genera un manual visual de la aplicación con diagramas e iconografía."""

        lang = "en" if language == "en" else "es"
        text = {
            "es": {
                "title": "Budget App - Guía visual de uso",
                "subtitle": "Manual práctico para entender el flujo completo de la aplicación.",
                "intro": (
                    "Budget App es una aplicación de escritorio para crear, editar, guardar y exportar "
                    "presupuestos comerciales. El flujo está pensado para trabajar en modo local o remoto "
                    "sin que el usuario tenga que conocer la estructura interna de la base de datos."
                ),
                "section1": "1. Qué hace la aplicación",
                "section1_body": (
                    "La aplicación organiza el trabajo en cuatro bloques: arranque, configuración, "
                    "edición de presupuestos y exportación. El usuario selecciona el idioma, el modo de "
                    "uso y, a partir de ahí, trabaja en la pantalla principal."
                ),
                "section2": "2. Flujo de uso",
                "section2_body": (
                    "El diagrama muestra el recorrido normal: inicio, elección de entorno, validación de "
                    "conexión o datos locales, acceso a la ventana principal y gestión del presupuesto."
                ),
                "section3": "3. Pantalla principal",
                "section3_body": (
                    "La vista principal se divide en un editor de presupuesto a la izquierda y un historial "
                    "de presupuestos a la derecha. Desde la barra de menús se accede a guardar, exportar, "
                    "copias de seguridad, datos de empresa y cambio de modo."
                ),
                "section4": "4. Módulos principales",
                "section4_body": (
                    "El gráfico resume las áreas funcionales más importantes. No es una métrica técnica; "
                    "es un mapa visual para que el usuario entienda dónde vive cada función."
                ),
                "section5": "5. Qué debe saber el usuario",
                "section5_body": (
                    "En modo remoto la aplicación necesita host, base de datos, usuario y contraseña. "
                    "En modo local usa un fichero SQLite. Los cambios se guardan desde la propia interfaz "
                    "y los presupuestos pueden exportarse a PDF."
                ),
                "flow_steps": [
                    "Abrir la app",
                    "Elegir idioma",
                    "Elegir modo",
                    "Configurar acceso",
                    "Entrar en la ventana principal",
                    "Editar y exportar",
                ],
                "main_labels": [
                    "Menú superior",
                    "Editor de presupuesto",
                    "Historial",
                    "Acciones rápidas",
                ],
                "chart_title": "Mapa visual de módulos",
                "chart_labels": [
                    "Arranque",
                    "Configuración",
                    "Edición",
                    "Historial",
                    "Exportación PDF",
                    "Datos / copias",
                ],
                "chart_values": [18, 16, 24, 14, 16, 12],
                "chart_descriptions": [
                    "Selección de idioma y modo.",
                    "Datos de empresa o conexión remota.",
                    "Alta y edición de partidas.",
                    "Consulta de presupuestos anteriores.",
                    "Salida a PDF para entrega.",
                    "Persistencia, backup y restauración.",
                ],
                "closing": "Documento generado automáticamente por Budget App.",
            },
            "en": {
                "title": "Budget App - Visual User Guide",
                "subtitle": "A practical manual to understand the full application flow.",
                "intro": (
                    "Budget App is a desktop application for creating, editing, saving and exporting "
                    "commercial budgets. The flow is designed for local or remote usage without exposing "
                    "the internal database structure to the user."
                ),
                "section1": "1. What the application does",
                "section1_body": (
                    "The application is organized into four blocks: startup, setup, budget editing and "
                    "export. The user chooses a language, a usage mode and then works in the main window."
                ),
                "section2": "2. Usage flow",
                "section2_body": (
                    "The diagram shows the normal path: launch, choose environment, validate the connection "
                    "or local data, open the main window and manage budgets."
                ),
                "section3": "3. Main screen",
                "section3_body": (
                    "The main view is split into a budget editor on the left and a history panel on the right. "
                    "The menu bar provides save, export, backups, company data and mode switching."
                ),
                "section4": "4. Main modules",
                "section4_body": (
                    "The chart summarizes the most important functional areas. It is not a technical metric; "
                    "it is a visual map that helps the user understand where each feature lives."
                ),
                "section5": "5. What the user should know",
                "section5_body": (
                    "In remote mode the app needs host, database, user and password. In local mode it uses a "
                    "SQLite file. Changes are saved from the interface and budgets can be exported to PDF."
                ),
                "flow_steps": [
                    "Open the app",
                    "Choose language",
                    "Choose mode",
                    "Set up access",
                    "Enter the main window",
                    "Edit and export",
                ],
                "main_labels": [
                    "Top menu",
                    "Budget editor",
                    "History",
                    "Quick actions",
                ],
                "chart_title": "Visual module map",
                "chart_labels": [
                    "Startup",
                    "Setup",
                    "Editing",
                    "History",
                    "PDF export",
                    "Data / backups",
                ],
                "chart_values": [18, 16, 24, 14, 16, 12],
                "chart_descriptions": [
                    "Language and mode selection.",
                    "Company data or remote connection.",
                    "Create and edit line items.",
                    "Review previous budgets.",
                    "PDF output for delivery.",
                    "Persistence, backup and restore.",
                ],
                "closing": "Automatically generated by Budget App.",
            },
        }[lang]

        cover_image_candidates = [
            resource_path("assets", "connectapp_logo.jpg"),
            resource_path("assets", "connectapp_logo.png"),
            resource_path("assets", "app_icon.png"),
        ]
        cover_image_path = next((path for path in cover_image_candidates if path.exists()), None)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "ManualTitle",
            parent=styles["Heading1"],
            fontSize=24,
            leading=28,
            textColor=PDFGenerator.BRAND_COLOR,
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "ManualSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=PDFGenerator.MUTED_TEXT,
            spaceAfter=8,
        )
        heading_style = ParagraphStyle(
            "ManualHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=17,
            textColor=PDFGenerator.BRAND_COLOR,
            spaceBefore=6,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "ManualBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=PDFGenerator.TEXT_COLOR,
            spaceAfter=6,
        )
        note_style = ParagraphStyle(
            "ManualNote",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=PDFGenerator.MUTED_TEXT,
        )
        panel_style = ParagraphStyle(
            "ManualPanel",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=PDFGenerator.TEXT_COLOR,
        )

        def rich(value: str) -> str:
            return escape(str(value or "")).replace("\n", "<br/>")

        def page_decor(canvas, doc_obj):
            canvas.saveState()
            width, height = A4
            left = doc.leftMargin
            right = width - doc.rightMargin
            canvas.setStrokeColor(PDFGenerator.GRID_COLOR)
            canvas.setLineWidth(0.6)
            canvas.line(left, height - 12 * mm, right, height - 12 * mm)
            canvas.line(left, 16 * mm, right, 16 * mm)
            canvas.setFillColor(PDFGenerator.MUTED_TEXT)
            canvas.setFont("Helvetica", 8)
            canvas.drawString(left, 10 * mm, "Budget App")
            canvas.drawRightString(right, 10 * mm, f"{text['title']}  |  {doc_obj.page}")
            canvas.restoreState()

        def boxed_paragraph(title: str, body: str, width_mm: float = 85.0):
            table = Table(
                [[Paragraph(f"<b>{rich(title)}</b>", panel_style)], [Paragraph(rich(body), panel_style)]],
                colWidths=[width_mm * mm],
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PDFGenerator.SOFT_BG),
                        ("TEXTCOLOR", (0, 0), (-1, -1), PDFGenerator.TEXT_COLOR),
                        ("BOX", (0, 0), (-1, -1), 0.8, PDFGenerator.GRID_COLOR),
                        ("INNERPADDING", (0, 0), (-1, -1), 6),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            return table

        def build_flow_diagram() -> Drawing:
            width = 520
            height = 250
            drawing = Drawing(width, height)
            x = 28
            y = height - 40
            box_w = 150
            box_h = 26
            gap = 15

            for idx, step in enumerate(text["flow_steps"]):
                current_y = y - idx * (box_h + gap)
                fill = PDFGenerator.BRAND_COLOR if idx in (0, len(text["flow_steps"]) - 1) else PDFGenerator.SOFT_BG
                stroke = PDFGenerator.BRAND_COLOR if idx in (0, len(text["flow_steps"]) - 1) else PDFGenerator.GRID_COLOR
                label_color = colors.white if idx in (0, len(text["flow_steps"]) - 1) else PDFGenerator.TEXT_COLOR
                drawing.add(Rect(x, current_y, box_w, box_h, rx=4, ry=4, fillColor=fill, strokeColor=stroke, strokeWidth=1))
                drawing.add(String(x + 8, current_y + 9, f"{idx + 1}. {step}", fontName="Helvetica-Bold", fontSize=9.5, fillColor=label_color))
                if idx < len(text["flow_steps"]) - 1:
                    line_y1 = current_y - 2
                    line_y2 = current_y - gap + 2
                    drawing.add(Line(x + box_w / 2, line_y1, x + box_w / 2, line_y2, strokeColor=PDFGenerator.ACCENT_COLOR, strokeWidth=1.2))

            right_x = 230
            drawing.add(Rect(right_x, height - 210, 255, 175, rx=8, ry=8, fillColor=colors.white, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=1))
            drawing.add(String(right_x + 14, height - 32, "Ruta resumida", fontName="Helvetica-Bold", fontSize=11, fillColor=PDFGenerator.BRAND_COLOR))
            summary_lines = [
                "1. El usuario abre la aplicación.",
                "2. Selecciona idioma y modo.",
                "3. Si es remoto, valida conexión.",
                "4. Se abre la pantalla principal.",
                "5. Se editan líneas y totales.",
                "6. Se exporta el resultado a PDF.",
            ]
            for idx, line in enumerate(summary_lines):
                drawing.add(String(right_x + 14, height - 55 - idx * 22, line, fontName="Helvetica", fontSize=9.5, fillColor=PDFGenerator.TEXT_COLOR))

            return drawing

        def build_main_window_mockup() -> Drawing:
            width = 520
            height = 280
            drawing = Drawing(width, height)
            drawing.add(Rect(10, 10, 500, 250, rx=8, ry=8, fillColor=colors.white, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=1.2))
            drawing.add(Rect(10, 230, 500, 30, rx=8, ry=8, fillColor=PDFGenerator.BRAND_COLOR, strokeColor=PDFGenerator.BRAND_COLOR, strokeWidth=1.0))
            drawing.add(String(24, 240, "Budget App", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.white))
            menu_items = ["Archivo", "Editar", "Ver", "Presupuesto", "Configuración", "Ayuda"]
            cursor = 96
            for item in menu_items:
                drawing.add(String(cursor, 240, item, fontName="Helvetica", fontSize=8, fillColor=colors.white))
                cursor += 54

            drawing.add(Rect(24, 40, 295, 175, rx=4, ry=4, fillColor=PDFGenerator.SOFT_BG, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=1))
            drawing.add(Rect(332, 40, 156, 175, rx=4, ry=4, fillColor=PDFGenerator.SOFT_BG, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=1))
            drawing.add(Rect(24, 220, 464, 30, rx=4, ry=4, fillColor=colors.white, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=0.8))

            for i in range(6):
                y = 186 - i * 23
                drawing.add(Line(24, y, 319, y, strokeColor=PDFGenerator.GRID_COLOR, strokeWidth=0.5))
            drawing.add(String(34, 197, "Editor de presupuesto", fontName="Helvetica-Bold", fontSize=10, fillColor=PDFGenerator.BRAND_COLOR))
            drawing.add(String(344, 197, "Historial", fontName="Helvetica-Bold", fontSize=10, fillColor=PDFGenerator.BRAND_COLOR))
            drawing.add(String(34, 172, "Cliente, partidas, importes y exportación.", fontName="Helvetica", fontSize=8.6, fillColor=PDFGenerator.TEXT_COLOR))
            drawing.add(String(344, 172, "Lista de trabajos guardados.", fontName="Helvetica", fontSize=8.6, fillColor=PDFGenerator.TEXT_COLOR))
            drawing.add(String(34, 228, "Barra de acciones rápidas: guardar, deshacer, PDF, copia.", fontName="Helvetica", fontSize=8.6, fillColor=PDFGenerator.TEXT_COLOR))
            drawing.add(String(34, 26, "Estado y mensajes de la aplicación", fontName="Helvetica", fontSize=8.6, fillColor=PDFGenerator.MUTED_TEXT))
            return drawing

        def build_module_chart() -> Drawing:
            drawing = Drawing(520, 220)
            chart = HorizontalBarChart()
            chart.x = 140
            chart.y = 24
            chart.height = 155
            chart.width = 330
            chart.data = [text["chart_values"]]
            chart.categoryAxis.categoryNames = text["chart_labels"]
            chart.categoryAxis.labels.boxAnchor = "e"
            chart.categoryAxis.labels.dx = -6
            chart.categoryAxis.labels.dy = 0
            chart.categoryAxis.labels.fontName = "Helvetica"
            chart.categoryAxis.labels.fontSize = 8.2
            chart.categoryAxis.strokeColor = colors.transparent
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 30
            chart.valueAxis.valueStep = 5
            chart.valueAxis.labels.fontName = "Helvetica"
            chart.valueAxis.labels.fontSize = 8
            chart.valueAxis.strokeColor = PDFGenerator.GRID_COLOR
            chart.bars[0].fillColor = PDFGenerator.ACCENT_COLOR
            chart.bars[0].strokeColor = PDFGenerator.BRAND_COLOR
            chart.barWidth = 11
            chart.groupSpacing = 4
            chart.categoryAxis.style = "parallel"
            drawing.add(chart)
            drawing.add(String(12, 194, text["chart_title"], fontName="Helvetica-Bold", fontSize=11, fillColor=PDFGenerator.BRAND_COLOR))
            drawing.add(String(12, 180, "Mapa visual de módulos y áreas funcionales", fontName="Helvetica", fontSize=8.5, fillColor=PDFGenerator.MUTED_TEXT))
            return drawing

        story.append(Spacer(1, 2 * mm))
        if cover_image_path:
            cover_image = Image(str(cover_image_path), width=62 * mm, height=62 * mm)
            cover_image.hAlign = "CENTER"
            story.append(cover_image)
            story.append(Spacer(1, 3 * mm))

        story.append(Paragraph(text["title"], title_style))
        story.append(Paragraph(text["subtitle"], subtitle_style))
        story.append(Paragraph(text["intro"], body_style))

        cover_table = Table(
            [
                [
                    boxed_paragraph("Ámbitos", "Local y remoto, con persistencia en SQLite o MySQL."),
                    boxed_paragraph("Salida", "Presupuestos en pantalla y exportación a PDF."),
                ],
                [
                    boxed_paragraph("Idioma", "Interfaz disponible en español e inglés."),
                    boxed_paragraph("Seguridad", "Validación básica de conexión y datos obligatorios."),
                ],
            ],
            colWidths=[84 * mm, 84 * mm],
        )
        cover_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(Spacer(1, 4 * mm))
        story.append(cover_table)
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph("Este PDF se ha diseñado para que un usuario nuevo entienda el recorrido completo sin leer código.", note_style))
        story.append(PageBreak())

        story.append(Paragraph(text["section1"], heading_style))
        story.append(Paragraph(text["section1_body"], body_style))
        story.append(Paragraph(text["section2"], heading_style))
        story.append(Paragraph(text["section2_body"], body_style))
        story.append(build_flow_diagram())
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("La parte remota pide credenciales del servidor. La parte local utiliza un archivo SQLite generado por la propia app.", note_style))
        story.append(PageBreak())

        story.append(Paragraph(text["section3"], heading_style))
        story.append(Paragraph(text["section3_body"], body_style))
        story.append(build_main_window_mockup())
        story.append(Spacer(1, 4 * mm))
        story.append(Table(
            [[Paragraph(f"<b>{rich(label)}</b>", panel_style), Paragraph(rich(desc), panel_style)] for label, desc in zip(text["main_labels"], [
                "Lanzas acciones globales como guardar, exportar y ayuda.",
                "Zona de edición de datos del presupuesto.",
                "Lista de presupuestos guardados previamente.",
                "Botones y menús de acceso rápido.",
            ])],
            colWidths=[45 * mm, 130 * mm],
        ))
        story[-1].setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PDFGenerator.SOFT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, PDFGenerator.GRID_COLOR),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph("La ventana principal es el lugar donde ocurre el trabajo real. El resto del flujo solo prepara el contexto.", note_style))
        story.append(PageBreak())

        story.append(Paragraph(text["section4"], heading_style))
        story.append(Paragraph(text["section4_body"], body_style))
        story.append(build_module_chart())
        story.append(Spacer(1, 3 * mm))
        legend_table = Table(
            [[Paragraph(f"<b>{rich(label)}</b>", panel_style), Paragraph(rich(desc), panel_style)] for label, desc in zip(text["chart_labels"], text["chart_descriptions"])],
            colWidths=[50 * mm, 125 * mm],
        )
        legend_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, PDFGenerator.SOFT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, PDFGenerator.GRID_COLOR),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("INNERPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(legend_table)
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph(text["section5"], heading_style))
        story.append(Paragraph(text["section5_body"], body_style))
        story.append(Paragraph(text["closing"], note_style))

        doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
