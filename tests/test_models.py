"""Testes dos modelos de dados."""

import pytest
from pydantic import ValidationError

from compliance_audit.models import (
    AuditReport,
    ComplianceMapping,
    EvidenceItem,
    EvidenceType,
    RemediationAction,
    RemediationStatus,
    RiskItem,
    RiskLevel,
)


def _compliance():
    return ComplianceMapping(
        lgpd_article="Art. 46",
        lgpd_text="Medidas de segurança",
        lgpd_implication="Exige controles técnicos",
        iso_control="A.8.24",
        iso_standard="ISO 27001:2022",
        iso_description="Criptografia",
        iso_family="A.8 — Gestão de ativos",
    )


def _risk_item(score=25, level=RiskLevel.CRITICAL):
    return RiskItem(
        finding_id="F-1",
        rule_id="AWS_ACCESS_KEY",
        description="Chave exposta",
        file_path="config.py",
        line_number=12,
        likelihood=5,
        impact=5,
        risk_score=score,
        risk_level=level,
        compliance=_compliance(),
        recommendation="Remover",
    )


def test_risk_item_valido():
    item = _risk_item()
    assert item.risk_score == 25
    assert item.risk_level == RiskLevel.CRITICAL


def test_risk_item_likelihood_fora_do_intervalo():
    with pytest.raises(ValidationError):
        RiskItem(
            finding_id="F-1",
            rule_id="X",
            description="d",
            file_path="f.py",
            line_number=1,
            likelihood=6,
            impact=5,
            risk_score=30,
            risk_level=RiskLevel.CRITICAL,
            compliance=_compliance(),
            recommendation="r",
        )


def test_remediation_action_status_padrao():
    acao = RemediationAction(
        action_id="REM-001",
        finding_id="F-1",
        title="Remediar",
        description="Descrição",
        priority=5,
        estimated_effort="2h",
    )
    assert acao.status == RemediationStatus.OPEN
    assert acao.assigned_to == ""


def test_remediation_action_prioridade_invalida():
    with pytest.raises(ValidationError):
        RemediationAction(
            action_id="REM-001",
            finding_id="F-1",
            title="Remediar",
            description="Descrição",
            priority=6,
            estimated_effort="2h",
        )


def test_evidence_item_valido():
    evidencia = EvidenceItem(
        evidence_id="EV-001",
        finding_id="F-1",
        evidence_type=EvidenceType.CODE_SNIPPET,
        description="Trecho de código",
        location="config.py:12",
    )
    assert evidencia.collected_by == "auditor"
    assert evidencia.file_hash == ""


def test_audit_report_compute_summary():
    report = AuditReport(
        report_id="AUD-1",
        client_name="Empresa",
        audit_scope="Código-fonte",
        risk_items=[
            _risk_item(25, RiskLevel.CRITICAL),
            _risk_item(16, RiskLevel.HIGH),
            _risk_item(12, RiskLevel.MEDIUM),
            _risk_item(6, RiskLevel.LOW),
            _risk_item(2, RiskLevel.NEGLIGIBLE),
        ],
    )
    report.compute_summary()

    assert report.total_findings == 5
    assert report.critical_count == 1
    assert report.high_count == 1
    assert report.medium_count == 1
    assert report.low_count == 1
    assert report.negligible_count == 1


def test_audit_report_vazio():
    report = AuditReport(
        report_id="AUD-2",
        client_name="Empresa",
        audit_scope="Código-fonte",
    )
    report.compute_summary()
    assert report.total_findings == 0
