"""
Gerador de relatório PDF formal de auditoria de conformidade LGPD / ISO 27000.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from compliance_audit.models import AuditReport, RiskLevel

# ===== PALETA DE CORES =====
COR_PRIMARIA = HexColor("#1a365d")
COR_SECUNDARIA = HexColor("#2c5282")
COR_DESTAQUE = HexColor("#2f855a")
COR_CRITICO = HexColor("#c53030")
COR_ALTO = HexColor("#dd6b20")
COR_MEDIO = HexColor("#d69e2e")
COR_BAIXO = HexColor("#38a169")
COR_NEGLIG = HexColor("#718096")
COR_FUNDO_CLARO = HexColor("#f7fafc")
COR_LINHA_ALT = HexColor("#edf2f7")
COR_DIVISORIA = HexColor("#e2e8f0")
COR_TEXTO = HexColor("#2d3748")
COR_TEXTO_CLARO = HexColor("#718096")
COR_CONFIDENCIAL = HexColor("#c53030")

# ===== CLASSES AUXILIARES =====

class CabecalhoSecao(Flowable):
    """Cabeçalho de seção com banda colorida e número."""

    def __init__(self, largura, numero, titulo, cor=COR_PRIMARIA):
        Flowable.__init__(self)
        self.largura = largura
        self.numero = numero
        self.titulo = titulo
        self.cor = cor
        self.height = 0.85 * cm

    def draw(self):
        self.canv.setFillColor(self.cor)
        self.canv.roundRect(0, 0, self.largura, self.height, 3, fill=1, stroke=0)
        self.canv.setFillColor(white)
        self.canv.circle(0.65 * cm, self.height / 2, 0.25 * cm, fill=1, stroke=0)
        self.canv.setFillColor(self.cor)
        self.canv.setFont("Helvetica-Bold", 10)
        self.canv.drawCentredString(0.65 * cm, self.height / 2 - 3, str(self.numero))
        self.canv.setFillColor(white)
        self.canv.setFont("Helvetica-Bold", 11)
        self.canv.drawString(1.2 * cm, self.height / 2 - 3.5, self.titulo)

# ===== FUNÇÕES UTILITÁRIAS =====

def _cor_risco(level: RiskLevel) -> HexColor:
    cores = {
        RiskLevel.CRITICAL: COR_CRITICO,
        RiskLevel.HIGH: COR_ALTO,
        RiskLevel.MEDIUM: COR_MEDIO,
        RiskLevel.LOW: COR_BAIXO,
        RiskLevel.NEGLIGIBLE: COR_NEGLIG,
    }
    return cores.get(level, COR_NEGLIG)

def _rotulo_risco(level: RiskLevel) -> str:
    rotulos = {
        RiskLevel.CRITICAL: "Crítico",
        RiskLevel.HIGH: "Alto",
        RiskLevel.MEDIUM: "Médio",
        RiskLevel.LOW: "Baixo",
        RiskLevel.NEGLIGIBLE: "Negligenciável",
    }
    return rotulos.get(level, "N/D")

def _estilos() -> dict:
    base = getSampleStyleSheet()

    return {
        "titulo": ParagraphStyle(
            "Titulo", parent=base["Title"],
            fontSize=20, textColor=white, spaceAfter=4,
            alignment=TA_CENTER, fontName="Helvetica-Bold",
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Normal"],
            fontSize=11, textColor=HexColor("#a0aec0"), spaceAfter=4,
            alignment=TA_CENTER,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"],
            fontSize=14, textColor=COR_PRIMARIA, spaceAfter=10, spaceBefore=14,
            fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"],
            fontSize=11, textColor=COR_SECUNDARIA, spaceAfter=6, spaceBefore=10,
            fontName="Helvetica-Bold",
        ),
        "corpo": ParagraphStyle(
            "Corpo", parent=base["Normal"],
            fontSize=10, alignment=TA_JUSTIFY, spaceAfter=6, leading=14,
            textColor=COR_TEXTO,
        ),
        "corpo_pequeno": ParagraphStyle(
            "CorpoPequeno", parent=base["Normal"],
            fontSize=9, alignment=TA_JUSTIFY, spaceAfter=4, leading=12,
            textColor=COR_TEXTO,
        ),
        "celula": ParagraphStyle(
            "Celula", parent=base["Normal"],
            fontSize=7.5, leading=10, textColor=COR_TEXTO,
            alignment=TA_LEFT,
        ),
        "celula_centro": ParagraphStyle(
            "CelulaCentro", parent=base["Normal"],
            fontSize=7.5, leading=10, textColor=COR_TEXTO,
            alignment=TA_CENTER,
        ),
        "celula_negrito": ParagraphStyle(
            "CelulaNegrito", parent=base["Normal"],
            fontSize=7.5, leading=10, fontName="Helvetica-Bold", textColor=COR_TEXTO,
            alignment=TA_LEFT,
        ),
        "celula_negrito_centro": ParagraphStyle(
            "CelulaNegritoCentro", parent=base["Normal"],
            fontSize=7.5, leading=10, fontName="Helvetica-Bold", textColor=COR_TEXTO,
            alignment=TA_CENTER,
        ),
        "celula_branco": ParagraphStyle(
            "CelulaBranco", parent=base["Normal"],
            fontSize=7, leading=9, fontName="Helvetica-Bold", textColor=white,
            alignment=TA_CENTER,
            splitLongWords=0,
        ),
        "rotulo_capa": ParagraphStyle(
            "RotuloCapa", parent=base["Normal"],
            fontSize=9, textColor=HexColor("#a0aec0"), fontName="Helvetica",
        ),
        "valor_capa": ParagraphStyle(
            "ValorCapa", parent=base["Normal"],
            fontSize=10, textColor=white, fontName="Helvetica-Bold",
        ),
        "kpi_valor": ParagraphStyle(
            "KPIValor", parent=base["Normal"],
            fontSize=18, textColor=white, fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ),
        "kpi_rotulo": ParagraphStyle(
            "KPIRotulo", parent=base["Normal"],
            fontSize=7.5, textColor=HexColor("#a0aec0"), alignment=TA_CENTER,
        ),
        "rodape": ParagraphStyle(
            "Rodape", parent=base["Normal"],
            fontSize=7, textColor=COR_TEXTO_CLARO, alignment=TA_CENTER,
        ),
        "confidencial": ParagraphStyle(
            "Confidencial", parent=base["Normal"],
            fontSize=7.5, textColor=COR_CONFIDENCIAL, alignment=TA_CENTER,
            fontName="Helvetica-Bold",
        ),
        "resumo_texto": ParagraphStyle(
            "ResumoTexto", parent=base["Normal"],
            fontSize=9.5, alignment=TA_JUSTIFY, leading=14, textColor=COR_TEXTO,
            spaceAfter=6,
        ),
        "resumo_destaque": ParagraphStyle(
            "ResumoDestaque", parent=base["Normal"],
            fontSize=9, fontName="Helvetica-Bold", textColor=COR_CRITICO,
            spaceAfter=4,
        ),
    }

# ===== ESTILO BASE PARA TODAS AS TABELAS =====

def _estilo_tabela_base(num_linhas: int, cor_header: HexColor = COR_PRIMARIA) -> list:
    """Retorna comandos de estilo base para todas as tabelas."""
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("VALIGN", (0, 1), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, 0), 1, cor_header),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, COR_DIVISORIA),
        ("BOX", (0, 0), (-1, -1), 0.5, COR_DIVISORIA),
    ]
    for i in range(1, num_linhas):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), COR_LINHA_ALT))
    return cmds

# ===== SEÇÕES DO RELATÓRIO =====

def _construir_capa(report: AuditReport, estilos: dict, largura: float) -> list:
    elementos = []
    elementos.append(Spacer(1, 2.5 * cm))

    banda = Table([[
        Paragraph("Relatório de Auditoria", estilos["titulo"]),
    ]], colWidths=[largura])
    banda.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_PRIMARIA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 25),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
    ]))
    elementos.append(banda)

    sub = Table([[
        Paragraph("Conformidade LGPD / ISO 27000", estilos["subtitulo"]),
    ]], colWidths=[largura])
    sub.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_SECUNDARIA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(sub)

    elementos.append(Spacer(1, 1.5 * cm))

    kpi_largura = (largura - 0.6 * cm) / 4
    kpi_dados = [[
        Table([[Paragraph(str(report.total_findings), estilos["kpi_valor"])]],
              colWidths=[kpi_largura], rowHeights=[1.1 * cm]),
        Table([[Paragraph(str(report.critical_count), estilos["kpi_valor"])]],
              colWidths=[kpi_largura], rowHeights=[1.1 * cm]),
        Table([[Paragraph(str(report.high_count), estilos["kpi_valor"])]],
              colWidths=[kpi_largura], rowHeights=[1.1 * cm]),
        Table([[Paragraph(str(report.medium_count + report.low_count), estilos["kpi_valor"])]],
              colWidths=[kpi_largura], rowHeights=[1.1 * cm]),
    ]]

    kpi_tabela = Table(kpi_dados, colWidths=[kpi_largura + 0.2 * cm] * 4)
    kpi_tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), COR_SECUNDARIA),
        ("BACKGROUND", (1, 0), (1, 0), COR_CRITICO),
        ("BACKGROUND", (2, 0), (2, 0), COR_ALTO),
        ("BACKGROUND", (3, 0), (3, 0), COR_MEDIO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    elementos.append(kpi_tabela)

    rotulos = [[
        Paragraph("Total de achados", estilos["kpi_rotulo"]),
        Paragraph("Críticos", estilos["kpi_rotulo"]),
        Paragraph("Altos", estilos["kpi_rotulo"]),
        Paragraph("Médios e baixos", estilos["kpi_rotulo"]),
    ]]
    rotulo_tabela = Table(rotulos, colWidths=[kpi_largura + 0.2 * cm] * 4)
    rotulo_tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_PRIMARIA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elementos.append(rotulo_tabela)

    elementos.append(Spacer(1, 2 * cm))

    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
    }
    data_extenso = report.audit_date.strftime(f"%d de {meses[report.audit_date.month]} de %Y")

    dados_cliente = [
        [Paragraph("Cliente", estilos["rotulo_capa"]), Paragraph(report.client_name, estilos["valor_capa"])],
        [Paragraph("Escopo", estilos["rotulo_capa"]), Paragraph(report.audit_scope, estilos["valor_capa"])],
        [Paragraph("Auditor", estilos["rotulo_capa"]), Paragraph(report.auditor, estilos["valor_capa"])],
        [Paragraph("Data", estilos["rotulo_capa"]), Paragraph(data_extenso, estilos["valor_capa"])],
        [Paragraph("Identificação", estilos["rotulo_capa"]), Paragraph(report.report_id, estilos["valor_capa"])],
    ]

    tabela_cliente = Table(dados_cliente, colWidths=[3.5 * cm, largura - 3.5 * cm])
    tabela_cliente.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_PRIMARIA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, HexColor("#2a4a6b")),
    ]))
    elementos.append(tabela_cliente)

    elementos.append(Spacer(1, 2 * cm))

    aviso = Table([[
        Paragraph("Documento confidencial — uso restrito ao destinatário", estilos["confidencial"]),
    ]], colWidths=[largura])
    aviso.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#fff5f5")),
        ("BOX", (0, 0), (-1, -1), 1, COR_CONFIDENCIAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(aviso)

    elementos.append(PageBreak())
    return elementos

def _construir_resumo(report: AuditReport, estilos: dict, largura: float) -> list:
    """Resumo executivo sem menção à automação."""
    elementos = []
    elementos.append(CabecalhoSecao(largura, 1, "Resumo executivo"))
    elementos.append(Spacer(1, 0.5 * cm))

    col_largura = largura / 5
    stats = [[
        Paragraph(f"<b>{report.total_findings}</b><br/><font size=7>total</font>",
                  ParagraphStyle("s1", parent=estilos["kpi_valor"], fontSize=14, textColor=COR_PRIMARIA)),
        Paragraph(f"<b>{report.critical_count}</b><br/><font size=7>críticos</font>",
                  ParagraphStyle("s2", parent=estilos["kpi_valor"], fontSize=14, textColor=COR_CRITICO)),
        Paragraph(f"<b>{report.high_count}</b><br/><font size=7>altos</font>",
                  ParagraphStyle("s3", parent=estilos["kpi_valor"], fontSize=14, textColor=COR_ALTO)),
        Paragraph(f"<b>{report.medium_count}</b><br/><font size=7>médios</font>",
                  ParagraphStyle("s4", parent=estilos["kpi_valor"], fontSize=14, textColor=COR_MEDIO)),
        Paragraph(f"<b>{report.low_count}</b><br/><font size=7>baixos</font>",
                  ParagraphStyle("s5", parent=estilos["kpi_valor"], fontSize=14, textColor=COR_BAIXO)),
    ]]

    stats_tabela = Table(stats, colWidths=[col_largura] * 5)
    stats_tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COR_FUNDO_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 0.5, COR_DIVISORIA),
    ]))
    elementos.append(stats_tabela)
    elementos.append(Spacer(1, 0.6 * cm))

    total = report.total_findings
    criticos = report.critical_count
    altos = report.high_count
    medios = report.medium_count
    baixos = report.low_count

    if report.risk_items:
        score_medio = sum(r.risk_score for r in report.risk_items) / len(report.risk_items)
        score_str = f"{score_medio:.1f}".replace(".", ",")
    else:
        score_str = "0,0"

    if criticos > 0:
        nivel_geral = "elevado"
        cor_nivel = COR_CRITICO
        acao = (
            "Recomenda-se tratamento imediato dos achados críticos, com priorização "
            "máxima de correção. A exposição de credenciais e dados pessoais sensíveis "
            "no código-fonte configura risco potencial de incidente de segurança "
            "notificável conforme o Art. 48 da LGPD."
        )
    elif altos > 0:
        nivel_geral = "moderado a alto"
        cor_nivel = COR_ALTO
        acao = (
            "Recomenda-se tratamento dos achados em até 72 horas, com inclusão "
            "no plano de tratamento de riscos da organização."
        )
    else:
        nivel_geral = "baixo"
        cor_nivel = COR_BAIXO
        acao = (
            "Os achados identificados são de baixo impacto. Recomenda-se "
            "monitoramento e programação de correções de forma planejada."
        )

    top3 = sorted(report.risk_items, key=lambda r: r.risk_score, reverse=True)[:3]
    top3_nomes = [item.rule_id for item in top3] if top3 else []

    # Texto do resumo — SEM menção à auditoria automática
    elementos.append(Paragraph(
        f"A análise do código-fonte do cliente <b>{report.client_name}</b> "
        f"identificou <b>{total} achados</b> de não conformidade relacionados à "
        f"exposição de dados sensíveis, credenciais e informações pessoais, "
        f"distribuídos em diferentes níveis de risco.",
        estilos["resumo_texto"]
    ))

    elementos.append(Paragraph(
        f"Nível de risco geral: <font color='{cor_nivel.hexval()}'><b>{nivel_geral.upper()}</b></font>",
        estilos["resumo_destaque"]
    ))

    elementos.append(Paragraph(
        f"Distribuição por severidade: {criticos} crítico(s), {altos} alto(s), "
        f"{medios} médio(s) e {baixos} baixo(s). A pontuação média de risco "
        f"calculada foi <b>{score_str}/25</b>, utilizando matriz 5×5 "
        f"(probabilidade × impacto) conforme metodologia ISO 27005.",
        estilos["resumo_texto"]
    ))

    if top3_nomes:
        elementos.append(Paragraph(
            f"Principais categorias de risco detectadas: "
            f"<b>{', '.join(top3_nomes)}</b>.",
            estilos["resumo_texto"]
        ))

    elementos.append(Paragraph(acao, estilos["resumo_texto"]))

    elementos.append(Paragraph(
        "O relatório completo inclui a matriz de riscos detalhada, o plano de correção "
        "priorizado, a cadeia de evidências e o mapeamento para os artigos da LGPD "
        "(Lei nº 13.709/2018) e controles da família ISO/IEC 27000.",
        estilos["resumo_texto"]
    ))

    elementos.append(Spacer(1, 0.8 * cm))
    elementos.append(PageBreak())
    return elementos

def _construir_matriz(report: AuditReport, estilos: dict, largura: float) -> list:
    elementos = []
    elementos.append(CabecalhoSecao(largura, 2, "Matriz de riscos", COR_CRITICO))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        "Os achados estão ordenados por pontuação de risco (probabilidade × impacto), "
        "conforme metodologia ISO 27005. A pontuação máxima é 25 (5×5).",
        estilos["corpo_pequeno"]
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    if not report.risk_items:
        elementos.append(Paragraph("Nenhum achado de não conformidade identificado.", estilos["corpo"]))
        return elementos

    cabecalho = [
        Paragraph("ID", estilos["celula_branco"]),
        Paragraph("Regra", estilos["celula_branco"]),
        Paragraph("Arquivo:linha", estilos["celula_branco"]),
        Paragraph("Pontuação", estilos["celula_branco"]),
        Paragraph("Nível", estilos["celula_branco"]),
        Paragraph("LGPD", estilos["celula_branco"]),
        Paragraph("ISO", estilos["celula_branco"]),
        Paragraph("Recomendação", estilos["celula_branco"]),
    ]

    dados = [cabecalho]
    for item in sorted(report.risk_items, key=lambda r: r.risk_score, reverse=True):
        dados.append([
            Paragraph(item.finding_id, estilos["celula_centro"]),
            Paragraph(item.rule_id, estilos["celula_negrito_centro"]),
            Paragraph(f"{Path(item.file_path).name}:{item.line_number}", estilos["celula_centro"]),
            Paragraph(f"{item.risk_score}/25", estilos["celula_negrito_centro"]),
            Paragraph(_rotulo_risco(item.risk_level), estilos["celula_negrito_centro"]),
            Paragraph(item.compliance.lgpd_article, estilos["celula_centro"]),
            Paragraph(item.compliance.iso_control, estilos["celula_centro"]),
            Paragraph(item.recommendation, estilos["celula"]),
        ])

    # Larguras: 1.2+1.6+2.0+1.8+1.4+1.2+1.2+6.6 = 17.0
    # "Pontuação" agora tem 1.8cm (antes 1.3cm) — cabe sem quebra
    col_larguras = [1.2*cm, 1.6*cm, 2.0*cm, 1.8*cm, 1.4*cm, 1.2*cm, 1.2*cm, 6.6*cm]
    tabela = Table(dados, colWidths=col_larguras, repeatRows=1)

    cmds = _estilo_tabela_base(len(dados), COR_CRITICO)

    for i, item in enumerate(sorted(report.risk_items, key=lambda r: r.risk_score, reverse=True)):
        linha = i + 1
        cmds.append(("TEXTCOLOR", (4, linha), (4, linha), _cor_risco(item.risk_level)))

    tabela.setStyle(TableStyle(cmds))
    elementos.append(tabela)
    elementos.append(Spacer(1, 0.8 * cm))
    elementos.append(PageBreak())
    return elementos

def _construir_remediacao(report: AuditReport, estilos: dict, largura: float) -> list:
    elementos = []
    elementos.append(CabecalhoSecao(largura, 3, "Plano de correção", COR_ALTO))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        "Ações priorizadas por pontuação de risco. Prioridade 5 exige ação imediata; "
        "prioridade 1 pode ser programada.",
        estilos["corpo_pequeno"]
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    if not report.remediation_plan:
        elementos.append(Paragraph("Nenhuma ação de correção necessária.", estilos["corpo"]))
        return elementos

    cabecalho = [
        Paragraph("Ação", estilos["celula_branco"]),
        Paragraph("Achado", estilos["celula_branco"]),
        Paragraph("Título", estilos["celula_branco"]),
        Paragraph("Prioridade", estilos["celula_branco"]),
        Paragraph("Esforço", estilos["celula_branco"]),
        Paragraph("Status", estilos["celula_branco"]),
        Paragraph("Descrição", estilos["celula_branco"]),
    ]

    dados = [cabecalho]
    for action in report.remediation_plan:
        dados.append([
            Paragraph(action.action_id, estilos["celula_negrito_centro"]),
            Paragraph(action.finding_id, estilos["celula_centro"]),
            Paragraph(action.title, estilos["celula"]),
            Paragraph(f"P{action.priority}", estilos["celula_negrito_centro"]),
            Paragraph(action.estimated_effort, estilos["celula_centro"]),
            Paragraph(action.status.value, estilos["celula_centro"]),
            Paragraph(action.description, estilos["celula"]),
        ])

    # Larguras: 1.2+1.2+2.6+1.8+1.4+1.2+7.6 = 17.0
    # "Prioridade" agora tem 1.8cm (antes 1.3cm) — cabe sem quebra
    col_larguras = [1.2*cm, 1.2*cm, 2.6*cm, 1.8*cm, 1.4*cm, 1.2*cm, 7.6*cm]
    tabela = Table(dados, colWidths=col_larguras, repeatRows=1)

    cmds = _estilo_tabela_base(len(dados), COR_ALTO)

    tabela.setStyle(TableStyle(cmds))
    elementos.append(tabela)
    elementos.append(Spacer(1, 0.8 * cm))
    elementos.append(PageBreak())
    return elementos

def _construir_evidencias(report: AuditReport, estilos: dict, largura: float) -> list:
    elementos = []
    elementos.append(CabecalhoSecao(largura, 4, "Cadeia de evidências", COR_SECUNDARIA))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        "Evidências coletadas durante a auditoria. "
        "Podem ser utilizadas em auditorias externas ou processos de comprovação.",
        estilos["corpo_pequeno"]
    ))
    elementos.append(Spacer(1, 0.4 * cm))

    if not report.evidence_chain:
        elementos.append(Paragraph("Nenhuma evidência coletada.", estilos["corpo"]))
        return elementos

    cabecalho = [
        Paragraph("ID", estilos["celula_branco"]),
        Paragraph("Achado", estilos["celula_branco"]),
        Paragraph("Tipo", estilos["celula_branco"]),
        Paragraph("Coletado em", estilos["celula_branco"]),
        Paragraph("Localização", estilos["celula_branco"]),
    ]

    dados = [cabecalho]
    for ev in report.evidence_chain:
        dados.append([
            Paragraph(ev.evidence_id, estilos["celula_negrito_centro"]),
            Paragraph(ev.finding_id, estilos["celula_centro"]),
            Paragraph(ev.evidence_type.value, estilos["celula_centro"]),
            Paragraph(ev.collected_at.strftime("%d/%m/%Y %H:%M"), estilos["celula_centro"]),
            Paragraph(ev.location, estilos["celula"]),
        ])

    # Larguras: 1.5+1.5+2.5+2.5+9.0 = 17.0
    col_larguras = [1.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 9.0*cm]
    tabela = Table(dados, colWidths=col_larguras, repeatRows=1)

    cmds = _estilo_tabela_base(len(dados), COR_SECUNDARIA)

    tabela.setStyle(TableStyle(cmds))
    elementos.append(tabela)
    elementos.append(PageBreak())
    return elementos

def _construir_mapeamento(report: AuditReport, estilos: dict, largura: float) -> list:
    elementos = []
    elementos.append(CabecalhoSecao(largura, 5, "Mapeamento legal e normativo", COR_DESTAQUE))
    elementos.append(Spacer(1, 0.3 * cm))
    elementos.append(Paragraph(
        "Embasamento jurídico (LGPD) e normativo (ISO 27000) aplicável aos achados.",
        estilos["corpo_pequeno"]
    ))
    elementos.append(Spacer(1, 0.5 * cm))

    artigos_vistos = set()
    controles_vistos = set()

    # LGPD
    elementos.append(Paragraph("Lei nº 13.709/2018 — LGPD", estilos["h2"]))

    dados_lgpd = [[
        Paragraph("Artigo", estilos["celula_branco"]),
        Paragraph("Resumo", estilos["celula_branco"]),
        Paragraph("Implicação prática", estilos["celula_branco"]),
    ]]

    for item in report.risk_items:
        art = item.compliance.lgpd_article
        if art not in artigos_vistos:
            artigos_vistos.add(art)
            dados_lgpd.append([
                Paragraph(art, estilos["celula_negrito_centro"]),
                Paragraph(item.compliance.lgpd_text, estilos["celula"]),
                Paragraph(item.compliance.lgpd_implication, estilos["celula"]),
            ])

    # Larguras: 1.8+5.5+9.7 = 17.0
    tab_lgpd = Table(dados_lgpd, colWidths=[1.8*cm, 5.5*cm, 9.7*cm], repeatRows=1)
    tab_lgpd.setStyle(TableStyle(_estilo_tabela_base(len(dados_lgpd), COR_PRIMARIA)))
    elementos.append(tab_lgpd)
    elementos.append(Spacer(1, 0.6 * cm))

    # ISO
    elementos.append(Paragraph("Família ISO/IEC 27000", estilos["h2"]))

    dados_iso = [[
        Paragraph("Controle", estilos["celula_branco"]),
        Paragraph("Norma", estilos["celula_branco"]),
        Paragraph("Família", estilos["celula_branco"]),
        Paragraph("Descrição", estilos["celula_branco"]),
    ]]

    for item in report.risk_items:
        ctrl = item.compliance.iso_control
        if ctrl not in controles_vistos:
            controles_vistos.add(ctrl)
            dados_iso.append([
                Paragraph(ctrl, estilos["celula_negrito_centro"]),
                Paragraph(item.compliance.iso_standard, estilos["celula_centro"]),
                Paragraph(item.compliance.iso_family, estilos["celula"]),
                Paragraph(item.compliance.iso_description, estilos["celula"]),
            ])

    # Larguras: 1.8+2.5+3.0+9.7 = 17.0
    tab_iso = Table(dados_iso, colWidths=[1.8*cm, 2.5*cm, 3.0*cm, 9.7*cm], repeatRows=1)
    tab_iso.setStyle(TableStyle(_estilo_tabela_base(len(dados_iso), COR_DESTAQUE)))
    elementos.append(tab_iso)

    return elementos

# ===== RODAPÉ =====

def _rodape(canvas_obj, doc):
    canvas_obj.saveState()

    canvas_obj.setStrokeColor(COR_DIVISORIA)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(1.5 * cm, 1.5 * cm, A4[0] - 1.5 * cm, 1.5 * cm)

    canvas_obj.setFont("Helvetica", 7)
    canvas_obj.setFillColor(COR_TEXTO_CLARO)
    canvas_obj.drawString(1.5 * cm, 1.1 * cm, "Relatório de auditoria")
    canvas_obj.drawCentredString(A4[0] / 2, 1.1 * cm, f"Página {doc.page}")
    canvas_obj.drawRightString(A4[0] - 1.5 * cm, 1.1 * cm, datetime.now().strftime("%d/%m/%Y"))

    canvas_obj.setFont("Helvetica-Bold", 6)
    canvas_obj.setFillColor(COR_CONFIDENCIAL)
    canvas_obj.drawCentredString(A4[0] / 2, 0.6 * cm, "Documento confidencial — distribuição restrita")

    canvas_obj.restoreState()

# ===== FUNÇÃO PRINCIPAL =====

def generate_pdf(report: AuditReport, output_path: str) -> str:
    """Gera o relatório PDF completo a partir de um AuditReport."""
    estilos = _estilos()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=2.2 * cm,
    )

    largura = A4[0] - 3 * cm  # 17.0 cm

    elementos = []
    elementos.extend(_construir_capa(report, estilos, largura))
    elementos.extend(_construir_resumo(report, estilos, largura))
    elementos.extend(_construir_matriz(report, estilos, largura))
    elementos.extend(_construir_remediacao(report, estilos, largura))
    elementos.extend(_construir_evidencias(report, estilos, largura))
    elementos.extend(_construir_mapeamento(report, estilos, largura))

    doc.build(elementos, onFirstPage=_rodape, onLaterPages=_rodape)

    return output_path