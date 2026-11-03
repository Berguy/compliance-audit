"""Testes da matriz de riscos 5x5."""

from compliance_audit.models import RiskLevel
from compliance_audit.risk.matrix import (
    calculate_risk_score,
    create_risk_item,
    generate_remediation_priority,
    get_risk_matrix_summary,
    score_to_risk_level,
)


def test_calculate_risk_score():
    assert calculate_risk_score(5, 5) == 25
    assert calculate_risk_score(1, 1) == 1
    assert calculate_risk_score(3, 4) == 12


def test_score_to_risk_level_negligible():
    assert score_to_risk_level(1) == RiskLevel.NEGLIGIBLE
    assert score_to_risk_level(4) == RiskLevel.NEGLIGIBLE


def test_score_to_risk_level_low():
    assert score_to_risk_level(5) == RiskLevel.LOW
    assert score_to_risk_level(9) == RiskLevel.LOW


def test_score_to_risk_level_medium():
    assert score_to_risk_level(10) == RiskLevel.MEDIUM
    assert score_to_risk_level(14) == RiskLevel.MEDIUM


def test_score_to_risk_level_high():
    assert score_to_risk_level(15) == RiskLevel.HIGH
    assert score_to_risk_level(19) == RiskLevel.HIGH


def test_score_to_risk_level_critical():
    assert score_to_risk_level(20) == RiskLevel.CRITICAL
    assert score_to_risk_level(25) == RiskLevel.CRITICAL


def test_create_risk_item_critical():
    item = create_risk_item(
        finding_id="F-1",
        rule_id="AWS_ACCESS_KEY",
        description="Chave exposta",
        file_path="config.py",
        line_number=12,
        severity="CRITICAL",
        lgpd_article="Art. 46",
        iso_control="A.8.24",
        recommendation="Remover a chave",
    )
    assert item.likelihood == 5
    assert item.impact == 5
    assert item.risk_score == 25
    assert item.risk_level == RiskLevel.CRITICAL


def test_create_risk_item_low():
    item = create_risk_item(
        finding_id="F-2",
        rule_id="BR_CEP",
        description="CEP exposto",
        file_path="enderecos.py",
        line_number=8,
        severity="LOW",
        lgpd_article="Art. 7",
        iso_control="A.8.10",
        recommendation="Usar variável de configuração",
    )
    assert item.likelihood == 2
    assert item.impact == 2
    assert item.risk_score == 4
    assert item.risk_level == RiskLevel.NEGLIGIBLE


def test_create_risk_item_severidade_minuscula():
    item = create_risk_item(
        finding_id="F-3",
        rule_id="GITHUB_TOKEN",
        description="Token exposto",
        file_path="app.py",
        line_number=3,
        severity="critical",
        lgpd_article="Art. 46",
        iso_control="A.8.5",
        recommendation="Revogar o token",
    )
    assert item.risk_score == 25


def test_create_risk_item_severidade_desconhecida_usa_padrao():
    item = create_risk_item(
        finding_id="F-4",
        rule_id="DESCONHECIDA",
        description="Regra sem mapeamento",
        file_path="x.py",
        line_number=1,
        severity="DESCONHECIDA",
        lgpd_article="Art. 46",
        iso_control="A.8.24",
        recommendation="Revisar",
    )
    assert item.likelihood == 3
    assert item.impact == 3
    assert item.risk_score == 9


def test_generate_remediation_priority_ordena_por_score(findings_sample):
    itens = [
        create_risk_item(
            finding_id=f["id"],
            rule_id=f["rule_id"],
            description=f["description"],
            file_path=f["file_path"],
            line_number=f["line_number"],
            severity=f["severity"],
            lgpd_article="Art. 46",
            iso_control="A.8.24",
            recommendation="Remediar",
        )
        for f in findings_sample
    ]
    prioridades = generate_remediation_priority(itens)

    assert len(prioridades) == 3
    assert prioridades[0]["risk_score"] >= prioridades[-1]["risk_score"]
    assert prioridades[0]["priority"] == 5


def test_get_risk_matrix_summary_vazio():
    resumo = get_risk_matrix_summary([])
    assert resumo["total"] == 0
    assert resumo["avg_score"] == 0
    assert resumo["top_risks"] == []


def test_get_risk_matrix_summary_com_itens(findings_sample):
    itens = [
        create_risk_item(
            finding_id=f["id"],
            rule_id=f["rule_id"],
            description=f["description"],
            file_path=f["file_path"],
            line_number=f["line_number"],
            severity=f["severity"],
            lgpd_article="Art. 46",
            iso_control="A.8.24",
            recommendation="Remediar",
        )
        for f in findings_sample
    ]
    resumo = get_risk_matrix_summary(itens)

    assert resumo["total"] == 3
    assert resumo["avg_score"] > 0
    assert len(resumo["top_risks"]) == 3
    assert resumo["top_risks"][0]["score"] >= resumo["top_risks"][-1]["score"]
