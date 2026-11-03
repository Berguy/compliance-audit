"""Testes do motor de auditoria."""

import json

import pytest

from compliance_audit.engine import (
    build_evidence_chain,
    build_remediation_plan,
    build_risk_items,
    generate_audit_report,
    generate_executive_summary,
    load_findings,
)


def test_load_findings_com_wrapper(findings_file, findings_sample):
    findings = load_findings(findings_file)
    assert len(findings) == 3
    assert findings[0]["rule_id"] == "AWS_ACCESS_KEY"


def test_load_findings_lista_pura(findings_file_lista):
    findings = load_findings(findings_file_lista)
    assert len(findings) == 3


def test_load_findings_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_findings(str(tmp_path / "nao_existe.json"))


def test_load_findings_json_invalido(tmp_path):
    caminho = tmp_path / "invalido.json"
    caminho.write_text('"apenas uma string"', encoding="utf-8")
    assert load_findings(str(caminho)) == []


def test_build_risk_items(findings_sample):
    itens = build_risk_items(findings_sample)
    assert len(itens) == 3
    assert itens[0].rule_id == "AWS_ACCESS_KEY"
    assert itens[0].compliance.lgpd_article == "Art. 46"
    assert itens[0].compliance.iso_control == "A.8.24"


def test_build_risk_items_regra_desconhecida():
    itens = build_risk_items([{"rule_id": "REGRA_NOVA", "severity": "MEDIUM"}])
    assert len(itens) == 1
    assert itens[0].compliance.lgpd_article == "Art. 46"
    assert itens[0].compliance.iso_control == "A.8.24"


def test_build_remediation_plan(findings_sample):
    itens = build_risk_items(findings_sample)
    plano = build_remediation_plan(itens)

    assert len(plano) == 3
    assert plano[0].action_id == "REM-001"
    assert plano[0].priority >= plano[-1].priority
    assert plano[0].status.value == "open"


def test_build_evidence_chain(findings_sample):
    itens = build_risk_items(findings_sample)
    evidencias = build_evidence_chain(itens)

    assert len(evidencias) == 3
    assert evidencias[0].evidence_id == "EV-001"
    assert evidencias[0].evidence_type.value == "code_snippet"
    assert "config.py" in evidencias[0].location


def test_generate_executive_summary(findings_sample):
    itens = build_risk_items(findings_sample)
    resumo = generate_executive_summary(itens, "Empresa Teste")

    assert "Empresa Teste" in resumo
    assert "RESUMO EXECUTIVO" in resumo
    assert "LGPD" in resumo


def test_generate_audit_report_completo(findings_file):
    report = generate_audit_report(
        findings_path=findings_file,
        client_name="Empresa Teste",
        audit_scope="Código-fonte",
        auditor="Berguy Silva",
    )

    assert report.client_name == "Empresa Teste"
    assert report.auditor == "Berguy Silva"
    assert report.report_id.startswith("AUD-")
    assert report.total_findings == 3
    assert report.critical_count == 2
    assert report.low_count == 1
    assert len(report.risk_items) == 3
    assert len(report.remediation_plan) == 3
    assert len(report.evidence_chain) == 3
    assert report.executive_summary != ""


def test_generate_audit_report_sem_findings(tmp_path):
    caminho = tmp_path / "vazio.json"
    caminho.write_text(json.dumps({"findings": []}), encoding="utf-8")

    report = generate_audit_report(
        findings_path=str(caminho),
        client_name="Empresa Sem Achados",
    )

    assert report.total_findings == 0
    assert report.critical_count == 0
    assert report.risk_items == []
