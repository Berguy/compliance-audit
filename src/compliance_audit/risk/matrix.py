"""
Matriz de riscos 5x5 com scoring quantitativo.

Calcula likelihood × impact para cada finding e categoriza
em niveis de risco formais conforme ISO 27005.
"""

from compliance_audit.models import RiskLevel, RiskItem, ComplianceMapping
from compliance_audit.knowledge_base.lgpd import get_lgpd_article
from compliance_audit.knowledge_base.iso27000 import get_iso_control

# Mapeamento de severidade do pii-guard para likelihood e impact
SEVERITY_TO_LIKELIHOOD: dict[str, int] = {
    "CRITICAL": 5,   # Quase certo de ser explorado
    "HIGH": 4,       # Muito provavel
    "MEDIUM": 3,     # Provavel
    "LOW": 2,        # Pouco provavel
    "INFO": 1,       # Raro
}

SEVERITY_TO_IMPACT: dict[str, int] = {
    "CRITICAL": 5,   # Impacto catastrofico — multa LGPD, vazamento massivo
    "HIGH": 4,       # Impacto severo — exposicao de dados sensiveis
    "MEDIUM": 3,     # Impacto moderado — dado pessoal exposto
    "LOW": 2,        # Impacto menor — informacao interna
    "INFO": 1,       # Impacto negligenciavel
}

def calculate_risk_score(likelihood: int, impact: int) -> int:
    """Calcula o score de risco (likelihood × impact).

    Args:
        likelihood: Probabilidade de exploracao (1-5)
        impact: Impacto no negocio (1-5)

    Returns:
        Score de 1 a 25
    """
    return likelihood * impact

def score_to_risk_level(score: int) -> RiskLevel:
    """Converte um score (1-25) em nivel de risco.

    Categorias:
        1-4:   NEGLIGIBLE
        5-9:   LOW
        10-14: MEDIUM
        15-19: HIGH
        20-25: CRITICAL
    """
    if score <= 4:
        return RiskLevel.NEGLIGIBLE
    elif score <= 9:
        return RiskLevel.LOW
    elif score <= 14:
        return RiskLevel.MEDIUM
    elif score <= 19:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL

def build_compliance_mapping(rule_id: str, lgpd_article: str, iso_control: str) -> ComplianceMapping:
    """Constrói o mapeamento de conformidade a partir das bases de conhecimento.

    Args:
        rule_id: Identificador da regra do pii-guard (ex: "BR_CPF")
        lgpd_article: Artigo da LGPD (ex: "Art. 11")
        iso_control: Controle ISO (ex: "A.8.10")

    Returns:
        ComplianceMapping preenchido
    """
    lgpd = get_lgpd_article(lgpd_article)
    iso = get_iso_control(iso_control)

    return ComplianceMapping(
        lgpd_article=lgpd_article,
        lgpd_text=lgpd.summary if lgpd else "Artigo nao mapeado",
        lgpd_implication=lgpd.implication if lgpd else "Implicacao nao mapeada",
        iso_control=iso_control,
        iso_standard=iso.standard if iso else "ISO 27001:2022",
        iso_description=iso.description if iso else "Controle nao mapeado",
        iso_family=iso.family if iso else "A.8 — Gestao de ativos",
    )

def create_risk_item(
    finding_id: str,
    rule_id: str,
    description: str,
    file_path: str,
    line_number: int,
    severity: str,
    lgpd_article: str,
    iso_control: str,
    recommendation: str,
) -> RiskItem:
    """Cria um RiskItem completo a partir de um finding do pii-guard.

    Args:
        finding_id: ID unico do finding
        rule_id: Regra que detectou (ex: "BR_CPF")
        description: Descricao do finding
        file_path: Caminho do arquivo
        line_number: Numero da linha
        severity: Severidade do pii-guard (CRITICAL, HIGH, etc.)
        lgpd_article: Artigo da LGPD violado
        iso_control: Controle ISO violado
        recommendation: Recomendacao de remediacao

    Returns:
        RiskItem com scoring calculado e mapeamento de conformidade
    """
    # CORRECAO: converter severity para maiusculo antes de buscar
    severity_upper = severity.upper()
    likelihood = SEVERITY_TO_LIKELIHOOD.get(severity_upper, 3)
    impact = SEVERITY_TO_IMPACT.get(severity_upper, 3)
    score = calculate_risk_score(likelihood, impact)
    risk_level = score_to_risk_level(score)
    compliance = build_compliance_mapping(rule_id, lgpd_article, iso_control)

    return RiskItem(
        finding_id=finding_id,
        rule_id=rule_id,
        description=description,
        file_path=file_path,
        line_number=line_number,
        likelihood=likelihood,
        impact=impact,
        risk_score=score,
        risk_level=risk_level,
        compliance=compliance,
        recommendation=recommendation,
    )

def generate_remediation_priority(risk_items: list[RiskItem]) -> list[dict]:
    """Gera lista de prioridades de remediacao ordenada por score.

    Returns:
        Lista de dicts com finding_id, score, level e prioridade (1-5)
    """
    sorted_items = sorted(risk_items, key=lambda r: r.risk_score, reverse=True)
    priorities = []

    for item in sorted_items:
        if item.risk_score >= 20:
            priority = 5  # Urgente
        elif item.risk_score >= 15:
            priority = 4  # Alto
        elif item.risk_score >= 10:
            priority = 3  # Medio
        elif item.risk_score >= 5:
            priority = 2  # Baixo
        else:
            priority = 1  # Observacao

        priorities.append({
            "finding_id": item.finding_id,
            "rule_id": item.rule_id,
            "risk_score": item.risk_score,
            "risk_level": item.risk_level.value,
            "priority": priority,
            "file_path": item.file_path,
            "line_number": item.line_number,
            "recommendation": item.recommendation,
        })

    return priorities

def get_risk_matrix_summary(risk_items: list[RiskItem]) -> dict:
    """Gera um resumo da matriz de riscos para o relatorio executivo.

    Returns:
        Dict com contadores por nivel, score medio e top 3 riscos
    """
    if not risk_items:
        return {
            "total": 0,
            "by_level": {},
            "avg_score": 0,
            "top_risks": [],
        }

    by_level: dict[str, int] = {}
    for level in RiskLevel:
        count = sum(1 for r in risk_items if r.risk_level == level)
        if count > 0:
            by_level[level.value] = count

    avg_score = sum(r.risk_score for r in risk_items) / len(risk_items)

    top_risks = sorted(risk_items, key=lambda r: r.risk_score, reverse=True)[:3]
    top_risks_data = [
        {
            "rule_id": r.rule_id,
            "score": r.risk_score,
            "level": r.risk_level.value,
            "file": r.file_path,
            "line": r.line_number,
        }
        for r in top_risks
    ]

    return {
        "total": len(risk_items),
        "by_level": by_level,
        "avg_score": round(avg_score, 1),
        "top_risks": top_risks_data,
    }