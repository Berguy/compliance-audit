"""
Gerador de relatorio PDF formal de auditoria de conformidade.

Produz um documento profissional com:
- Capa
- Resumo executivo
- Matriz de riscos detalhada
- Plano de remediacao
- Cadeia de evidencias
- Mapeamento LGPD/ISO 27000
"""

from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfgen import canvas

from compliance_audit.models import AuditReport, RiskLevel

# Cores corporativas
COLOR_PRIMARY = HexColor("#1a365d")
COLOR_CRITICAL = HexColor("#c0392b")
COLOR_HIGH = HexColor("#e67e22")
COLOR_MEDIUM = HexColor("#f1c40f")
COLOR_LOW = HexColor("#27ae60")
COLOR_NEGLIGIBLE = HexColor("#95a5a6")
COLOR_LIGHT_BG = HexColor("#f8f9fa")
COLOR_TABLE_HEADER = HexColor("#2c3e50")

def _risk_color(level: RiskLevel) -> HexColor:
    """Retorna a cor correspondente ao nivel de risco."""
    colors = {
        RiskLevel.CRITICAL: COLOR_CRITICAL,
        RiskLevel.HIGH: COLOR_HIGH,
        RiskLevel.MEDIUM: COLOR_MEDIUM,
        RiskLevel.LOW: COLOR_LOW,
        RiskLevel.NEGLIGIBLE: COLOR_NEGLIGIBLE,
    }
    return colors.get(level, COLOR_NEGLIGIBLE)

def _risk_label(level: RiskLevel) -> str:
    """Retorna o label em portugues para o nivel de risco."""
    labels = {
        RiskLevel.CRITICAL: "CRITICO",
        RiskLevel.HIGH: "ALTO",
        RiskLevel.MEDIUM: "MEDIO",
        RiskLevel.LOW: "BAIXO",
        RiskLevel.NEGLIGIBLE: "NEGLIGENCAVEL",
    }
    return labels.get(level, "DESCONHECIDO")

def _build_styles() -> dict:
    """Cria os estilos de paragrafo do documento."""
    styles = getSampleStyleSheet()

    custom = {
        "title": ParagraphStyle(
            "CustomTitle", parent=styles["Title"],
            fontSize=24, textColor=COLOR_PRIMARY, spaceAfter=30,
            alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "CustomSubtitle", parent=styles["Normal"],
            fontSize=14, textColor=COLOR_PRIMARY, spaceAfter=12,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "CustomH1", parent=styles["Heading1"],
            fontSize=16, textColor=COLOR_PRIMARY, spaceAfter=12, spaceBefore=20,
        ),
        "h2": ParagraphStyle(
            "CustomH2", parent=styles["Heading2"],
            fontSize=13, textColor=COLOR_TABLE_HEADER, spaceAfter=8, spaceBefore=12,
        ),
        "body": ParagraphStyle(
            "CustomBody", parent=styles["Normal"],
            fontSize=10, alignment=TA_JUSTIFY, spaceAfter=8, leading=14,
        ),
        "cell": ParagraphStyle(
            "CustomCell", parent=styles["Normal"],
            fontSize=8, leading=10,
        ),
        "cell_bold": ParagraphStyle(
            "CustomCellBold", parent=styles["Normal"],
            fontSize=8, leading=10, fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "CustomFooter", parent=styles["Normal"],
            fontSize=8, textColor=COLOR_NEGLIGIBLE, alignment=TA_CENTER,
        ),
    }
    return custom

def _build_cover(report: AuditReport, styles: dict) -> list:
    """Constroi a capa do relatorio."""
    elements = []
    elements.append(Spacer(1, 4 * cm))
    elements.append(Paragraph("RELATORIO DE AUDITORIA", styles["title"]))
    elements.append(Paragraph("CONFORMIDADE LGPD / ISO 27000", styles["subtitle"]))
    elements.append(Spacer(1, 2 * cm))

    cover_data = [
        ["Cliente:", report.client_name],
        ["Escopo:", report.audit_scope],
        ["Data:", report.audit_date.strftime("%d/%m/%Y")],
        ["Auditor:", report.auditor],
        ["ID do Relatorio:", report.report_id],
        ["Total de Achados:", str(report.total_findings)],
        ["Criticos:", str(report.critical_count)],
        ["Altos:", str(report.high_count)],
        ["Medios:", str(report.medium_count)],
        ["Baixos:", str(report.low_count)],
    ]

    cover_table = Table(cover_data, colWidths=[5 * cm, 10 * cm])
    cover_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (0, -1), COLOR_PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), black),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, COLOR_LIGHT_BG),
    ]))
    elements.append(cover_table)
    elements.append(PageBreak())
    return elements

def _build_executive_summary(report: AuditReport, styles: dict) -> list:
    """Constroi o resumo executivo."""
    elements = []
    elements.append(Paragraph("1. RESUMO EXECUTIVO", styles["h1"]))

    summary_lines = report.executive_summary.split("\n")
    for line in summary_lines:
        line = line.strip()
        if line:
            elements.append(Paragraph(line, styles["body"]))

    elements.append(Spacer(1, 1 * cm))
    elements.append(PageBreak())
    return elements

def _build_risk_matrix(report: AuditReport, styles: dict) -> list:
    """Constroi a tabela detalhada da matriz de riscos."""
    elements = []
    elements.append(Paragraph("2. MATRIZ DE RISCOS", styles["h1"]))
    elements.append(Paragraph(
        "A seguinte matriz apresenta todos os achados de nao conformidade "
        "identificados durante a auditoria, ordenados por score de risco "
        "(likelihood x impact, metodologia ISO 27005).",
        styles["body"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    if not report.risk_items:
        elements.append(Paragraph(
            "Nenhum achado de nao conformidade foi identificado.",
            styles["body"]
        ))
        return elements

    header = [
        Paragraph("ID", styles["cell_bold"]),
        Paragraph("Regra", styles["cell_bold"]),
        Paragraph("Arquivo:Linha", styles["cell_bold"]),
        Paragraph("Score", styles["cell_bold"]),
        Paragraph("Nivel", styles["cell_bold"]),
        Paragraph("LGPD", styles["cell_bold"]),
        Paragraph("ISO 27000", styles["cell_bold"]),
        Paragraph("Recomendacao", styles["cell_bold"]),
    ]

    data = [header]
    row_colors = []

    for item in sorted(report.risk_items, key=lambda r: r.risk_score, reverse=True):
        row = [
            Paragraph(item.finding_id, styles["cell"]),
            Paragraph(item.rule_id, styles["cell"]),
            Paragraph(f"{Path(item.file_path).name}:{item.line_number}", styles["cell"]),
            Paragraph(f"{item.risk_score}/25", styles["cell"]),
            Paragraph(_risk_label(item.risk_level), styles["cell"]),
            Paragraph(item.compliance.lgpd_article, styles["cell"]),
            Paragraph(item.compliance.iso_control, styles["cell"]),
            Paragraph(item.recommendation, styles["cell"]),
        ]
        data.append(row)
        row_colors.append(_risk_color(item.risk_level))

    col_widths = [1.5*cm, 2*cm, 2.5*cm, 1.2*cm, 1.5*cm, 1.2*cm, 1.2*cm, 4*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_NEGLIGIBLE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]

    for i, color in enumerate(row_colors):
        row_idx = i + 1
        style_cmds.append(("TEXTCOLOR", (4, row_idx), (4, row_idx), color))
        style_cmds.append(("FONTNAME", (4, row_idx), (4, row_idx), "Helvetica-Bold"))

    table.setStyle(TableStyle(style_cmds))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))
    elements.append(PageBreak())
    return elements

def _build_remediation_plan(report: AuditReport, styles: dict) -> list:
    """Constroi o plano de remediacao."""
    elements = []
    elements.append(Paragraph("3. PLANO DE REMEDIACAO", styles["h1"]))
    elements.append(Paragraph(
        "O seguinte plano de remediacao prioriza as acoes conforme o score de risco. "
        "Acoes de prioridade 5 (urgente) devem ser executadas imediatamente.",
        styles["body"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    if not report.remediation_plan:
        elements.append(Paragraph(
            "Nenhuma acao de remediacao necessaria.",
            styles["body"]
        ))
        return elements

    header = [
        Paragraph("ID Acao", styles["cell_bold"]),
        Paragraph("Finding", styles["cell_bold"]),
        Paragraph("Titulo", styles["cell_bold"]),
        Paragraph("Prioridade", styles["cell_bold"]),
        Paragraph("Esforco Est.", styles["cell_bold"]),
        Paragraph("Status", styles["cell_bold"]),
        Paragraph("Descricao", styles["cell_bold"]),
    ]

    data = [header]
    for action in report.remediation_plan:
        row = [
            Paragraph(action.action_id, styles["cell"]),
            Paragraph(action.finding_id, styles["cell"]),
            Paragraph(action.title, styles["cell"]),
            Paragraph(f"P{action.priority}", styles["cell"]),
            Paragraph(action.estimated_effort, styles["cell"]),
            Paragraph(action.status.value, styles["cell"]),
            Paragraph(action.description, styles["cell"]),
        ]
        data.append(row)

    col_widths = [1.5*cm, 1.5*cm, 3*cm, 1.2*cm, 1.5*cm, 1.5*cm, 4.5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_NEGLIGIBLE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 1 * cm))
    elements.append(PageBreak())
    return elements

def _build_evidence_chain(report: AuditReport, styles: dict) -> list:
    """Constroi a cadeia de evidencias."""
    elements = []
    elements.append(Paragraph("4. CADEIA DE EVIDENCIAS", styles["h1"]))
    elements.append(Paragraph(
        "As evidencias abaixo foram coletadas automaticamente durante a auditoria "
        "e podem ser usadas para fins de comprovacao em auditorias externas.",
        styles["body"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    if not report.evidence_chain:
        elements.append(Paragraph(
            "Nenhuma evidencia coletada.",
            styles["body"]
        ))
        return elements

    header = [
        Paragraph("ID Evid.", styles["cell_bold"]),
        Paragraph("Finding", styles["cell_bold"]),
        Paragraph("Tipo", styles["cell_bold"]),
        Paragraph("Coletado em", styles["cell_bold"]),
        Paragraph("Local", styles["cell_bold"]),
    ]

    data = [header]
    for ev in report.evidence_chain:
        row = [
            Paragraph(ev.evidence_id, styles["cell"]),
            Paragraph(ev.finding_id, styles["cell"]),
            Paragraph(ev.evidence_type.value, styles["cell"]),
            Paragraph(ev.collected_at.strftime("%d/%m/%Y %H:%M"), styles["cell"]),
            Paragraph(ev.location, styles["cell"]),
        ]
        data.append(row)

    col_widths = [1.5*cm, 1.5*cm, 2*cm, 2.5*cm, 5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_NEGLIGIBLE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(table)
    elements.append(PageBreak())
    return elements

def _build_legal_mapping(report: AuditReport, styles: dict) -> list:
    """Constroi a secao de mapeamento legal e normativo."""
    elements = []
    elements.append(Paragraph("5. MAPEAMENTO LEGAL E NORMATIVO", styles["h1"]))
    elements.append(Paragraph(
        "Esta secao detalha o embasamento juridico (LGPD) e normativo (ISO 27000) "
        "para cada achado identificado.",
        styles["body"]
    ))
    elements.append(Spacer(1, 0.5 * cm))

    seen_articles = set()
    seen_controls = set()

    elements.append(Paragraph("5.1 Artigos da LGPD", styles["h2"]))

    lgpd_data = [[
        Paragraph("Artigo", styles["cell_bold"]),
        Paragraph("Texto", styles["cell_bold"]),
        Paragraph("Implicacao", styles["cell_bold"]),
    ]]

    for item in report.risk_items:
        art = item.compliance.lgpd_article
        if art not in seen_articles:
            seen_articles.add(art)
            lgpd_data.append([
                Paragraph(art, styles["cell"]),
                Paragraph(item.compliance.lgpd_text, styles["cell"]),
                Paragraph(item.compliance.lgpd_implication, styles["cell"]),
            ])

    lgpd_table = Table(lgpd_data, colWidths=[2*cm, 5*cm, 6*cm], repeatRows=1)
    lgpd_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_NEGLIGIBLE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(lgpd_table)
    elements.append(Spacer(1, 0.8 * cm))

    elements.append(Paragraph("5.2 Controles ISO 27000", styles["h2"]))

    iso_data = [[
        Paragraph("Controle", styles["cell_bold"]),
        Paragraph("Norma", styles["cell_bold"]),
        Paragraph("Familia", styles["cell_bold"]),
        Paragraph("Descricao", styles["cell_bold"]),
    ]]

    for item in report.risk_items:
        ctrl = item.compliance.iso_control
        if ctrl not in seen_controls:
            seen_controls.add(ctrl)
            iso_data.append([
                Paragraph(ctrl, styles["cell"]),
                Paragraph(item.compliance.iso_standard, styles["cell"]),
                Paragraph(item.compliance.iso_family, styles["cell"]),
                Paragraph(item.compliance.iso_description, styles["cell"]),
            ])

    iso_table = Table(iso_data, colWidths=[1.5*cm, 2.5*cm, 3*cm, 6*cm], repeatRows=1)
    iso_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_NEGLIGIBLE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(iso_table)
    return elements

def _footer(canvas_obj: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    """Adiciona rodape numerado em cada pagina."""
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(COLOR_NEGLIGIBLE)
    page_text = f"Relatorio de Auditoria — Pagina {doc.page}"
    canvas_obj.drawCentredString(A4[0] / 2, 1 * cm, page_text)
    canvas_obj.drawRightString(
        A4[0] - 1.5 * cm, 1 * cm,
        datetime.now().strftime("%d/%m/%Y")
    )
    canvas_obj.restoreState()

def generate_pdf(report: AuditReport, output_path: str) -> str:
    """Gera o relatorio PDF completo a partir de um AuditReport.

    Args:
        report: Objeto AuditReport com todos os dados
        output_path: Caminho onde o PDF sera salvo

    Returns:
        Caminho do arquivo PDF gerado
    """
    styles = _build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2 * cm,
    )

    elements = []

    # Capa
    elements.extend(_build_cover(report, styles))

    # Resumo executivo
    elements.extend(_build_executive_summary(report, styles))

    # Matriz de riscos
    elements.extend(_build_risk_matrix(report, styles))

    # Plano de remediacao
    elements.extend(_build_remediation_plan(report, styles))

    # Cadeia de evidencias
    elements.extend(_build_evidence_chain(report, styles))

    # Mapeamento legal e normativo
    elements.extend(_build_legal_mapping(report, styles))

    # Construir PDF
    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)

    return output_path