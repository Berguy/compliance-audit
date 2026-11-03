"""
Motor principal do compliance-audit.

Consome findings do pii-guard (JSON), enriquece com dados juridicos
(LGPD) e tecnicos (ISO 27000), calcula riscos e monta o relatorio
de auditoria formal.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from compliance_audit.models import (
    AuditReport,
    EvidenceItem,
    EvidenceType,
    RemediationAction,
    RemediationStatus,
    RiskItem,
)
from compliance_audit.risk.matrix import (
    create_risk_item,
    generate_remediation_priority,
    get_risk_matrix_summary,
)

# Mapeamento de regras do pii-guard para LGPD e ISO 27000
RULE_MAPPING: dict[str, dict] = {
    "AWS_ACCESS_KEY": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover a chave do codigo imediatamente. Usar variaveis de ambiente ou AWS IAM Roles. Revogar a chave comprometida no console AWS.",
    },
    "AWS_SECRET_KEY": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover a secret key do codigo. Rotacionar a credencial comprometida e usar AWS Secrets Manager.",
    },
    "GITHUB_TOKEN": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Revogar o token imediatamente no GitHub. Usar GitHub Actions Secrets ou variaveis de ambiente.",
    },
    "GOOGLE_API_KEY": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover a chave do Google do codigo. Revogar e recriar via Google Cloud Secret Manager.",
    },
    "GENERIC_PASSWORD": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover senha hardcoded. Usar variaveis de ambiente ou cofre de segredos (HashiCorp Vault, AWS Secrets Manager).",
    },
    "PRIVATE_KEY": {
        "lgpd": "Art. 11",
        "iso": "A.8.24",
        "recommendation": "Remover a chave privada do codigo. e considerada dado sensivel. Armazenar em cofre e rotacionar imediatamente.",
    },
    "JWT_TOKEN": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover o token JWT do codigo. Revogar a sessao associada e usar fluxo OAuth2 para obter tokens em runtime.",
    },
    "CONNECTION_STRING": {
        "lgpd": "Art. 46",
        "iso": "A.8.24",
        "recommendation": "Remover a string de conexao com credenciais. Usar variaveis de ambiente separadas para host, user e password.",
    },
    "BR_CPF": {
        "lgpd": "Art. 11",
        "iso": "A.8.10",
        "recommendation": "Remover CPF do codigo. e considerado dado sensivel. Se necessario para testes, usar dados anonimizados ou mocks.",
    },
    "BR_CNPJ": {
        "lgpd": "Art. 7",
        "iso": "A.8.10",
        "recommendation": "Remover CNPJ do codigo. Usar variaveis de configuracao ou banco de dados com controle de acesso.",
    },
    "EMAIL_ADDRESS": {
        "lgpd": "Art. 5",
        "iso": "A.8.10",
        "recommendation": "Remover e-mail pessoal do codigo. Usar variaveis de ambiente ou dados ficticios para testes.",
    },
    "BR_PHONE": {
        "lgpd": "Art. 5",
        "iso": "A.8.10",
        "recommendation": "Remover telefone do codigo. e dado pessoal. Usar mocks ou dados anonimizados em testes.",
    },
    "BR_RG": {
        "lgpd": "Art. 11",
        "iso": "A.8.10",
        "recommendation": "Remover RG do codigo. e considerado dado sensivel. Usar dados ficticios para testes.",
    },
    "BR_CEP": {
        "lgpd": "Art. 5",
        "iso": "A.8.10",
        "recommendation": "Remover CEP do codigo. e dado pessoal de localizacao. Usar variaveis de configuracao.",
    },
    "CREDIT_CARD": {
        "lgpd": "Art. 11",
        "iso": "A.8.24",
        "recommendation": "Remover numero de cartao do codigo. e dado financeiro sensivel. Nunca armazenar cartoes em texto plano — usar tokenizacao PCI-DSS.",
    },
    "FULL_NAME_HINT": {
        "lgpd": "Art. 5",
        "iso": "A.8.10",
        "recommendation": "Revisar se o nome em variavel e dado real de cliente. Se sim, remover e usar dados anonimizados.",
    },
}

def load_findings(findings_path: str) -> list[dict]:
    """Carrega findings do pii-guard a partir de um arquivo JSON.

    Args:
        findings_path: Caminho para o arquivo JSON gerado pelo pii-guard

    Returns:
        Lista de findings (dicts)
    """
    path = Path(findings_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de findings nao encontrado: {findings_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # O pii-guard pode retornar {"findings": [...]} ou [...]
    if isinstance(data, dict):
        return data.get("findings", [])
    elif isinstance(data, list):
        return data
    else:
        return []

def build_risk_items(findings: list[dict]) -> list[RiskItem]:
    """Converte findings do pii-guard em RiskItems com scoring e mapeamento.

    Args:
        findings: Lista de findings do pii-guard

    Returns:
        Lista de RiskItems enriquecidos
    """
    risk_items = []

    for i, finding in enumerate(findings):
        rule_id = finding.get("rule_id", "UNKNOWN")
        mapping = RULE_MAPPING.get(rule_id, {
            "lgpd": "Art. 46",
            "iso": "A.8.24",
            "recommendation": "Revisar e remover dado sensivel do codigo.",
        })

        risk_item = create_risk_item(
            finding_id=finding.get("id", f"Finding-{i+1:03d}"),
            rule_id=rule_id,
            description=finding.get("description", "Finding sem descricao"),
            file_path=finding.get("file_path", "unknown"),
            line_number=finding.get("line_number", 0),
            severity=finding.get("severity", "MEDIUM"),
            lgpd_article=mapping["lgpd"],
            iso_control=mapping["iso"],
            recommendation=mapping["recommendation"],
        )
        risk_items.append(risk_item)

    return risk_items

def build_remediation_plan(risk_items: list[RiskItem]) -> list[RemediationAction]:
    """Gera plano de remediacao a partir dos risk items priorizados.

    Args:
        risk_items: Lista de RiskItems

    Returns:
        Lista de RemediationActions ordenadas por prioridade
    """
    priorities = generate_remediation_priority(risk_items)
    plan = []

    for i, p in enumerate(priorities):
        action = RemediationAction(
            action_id=f"REM-{i+1:03d}",
            finding_id=p["finding_id"],
            title=f"Remediar {p['rule_id']} em {Path(p['file_path']).name}:{p['line_number']}",
            description=p["recommendation"],
            priority=p["priority"],
            estimated_effort="2h" if p["priority"] >= 4 else "1dia" if p["priority"] >= 3 else "1semana",
            status=RemediationStatus.OPEN,
        )
        plan.append(action)

    return plan

def build_evidence_chain(risk_items: list[RiskItem]) -> list[EvidenceItem]:
    """Gera cadeia de evidencias para cada finding encontrado.

    Args:
        risk_items: Lista de RiskItems

    Returns:
        Lista de EvidenceItems
    """
    evidence_chain = []

    for i, item in enumerate(risk_items):
        evidence = EvidenceItem(
            evidence_id=f"EV-{i+1:03d}",
            finding_id=item.finding_id,
            evidence_type=EvidenceType.CODE_SNIPPET,
            description=f"Codigo fonte em {item.file_path}:{item.line_number} contendo {item.rule_id}",
            collected_at=datetime.now(),
            collected_by="compliance-audit-engine",
            location=f"{item.file_path}:{item.line_number}",
        )
        evidence_chain.append(evidence)

    return evidence_chain

def generate_executive_summary(risk_items: list[RiskItem], client_name: str) -> str:
    """Gera resumo executivo do relatorio de auditoria.

    Args:
        risk_items: Lista de RiskItems
        client_name: Nome do cliente auditado

    Returns:
        Texto do resumo executivo
    """
    summary_data = get_risk_matrix_summary(risk_items)

    total = summary_data["total"]
    by_level = summary_data["by_level"]
    avg_score = summary_data["avg_score"]
    top_risks = summary_data["top_risks"]

    critical = by_level.get("critical", 0)
    high = by_level.get("high", 0)
    medium = by_level.get("medium", 0)
    low = by_level.get("low", 0)

    summary = f"""RELATORIO DE AUDITORIA DE CONFORMIDADE LGPD/ISO 27000

Cliente: {client_name}
Data: {datetime.now().strftime('%d/%m/%Y')}

1. RESUMO EXECUTIVO

Foram identificados {total} achados de nao conformidade durante a auditoria
automatizada do codigo-fonte. A distribuicao por nivel de risco e:

  - Critico: {critical}
  - Alto: {high}
  - Medio: {medium}
  - Baixo: {low}

O score medio de risco calculado foi {avg_score}/25 (matriz 5x5 — likelihood x impact),
conforme metodologia ISO 27005.

2. PRINCIPAIS RISCOS
"""

    for i, risk in enumerate(top_risks):
        summary += f"\n  {i+1}. {risk['rule_id']} — Score: {risk['score']}/25 ({risk['level']})\n"
        summary += f"     Local: {risk['file']}:{risk['line']}\n"

    summary += f"""
3. RECOMENDACOES

Os achados criticos ({critical}) exigem remediacao imediata, podendo caracterizar
incidente de seguranca notificavel conforme Art. 48 da LGPD.

Os achados altos ({high}) devem ser tratados em no maximo 72 horas.

Os achados medios ({medium}) e baixos ({low}) devem ser incluidos no plano
de tratamento de risco com prazo definido pelo DPO.

4. BASE LEGAL E NORMATIVA

Esta auditoria fundamenta-se na Lei nº 13.709/2018 (LGPD) e na familia
ISO/IEC 27000, incluindo ISO 27001:2022 (requisitos), ISO 27002:2022 (controles),
ISO 27005:2022 (gestao de risco), ISO 27017:2015 (nuvem) e ISO 27018:2019 (PII em nuvem).
"""

    return summary

def generate_audit_report(
    findings_path: str,
    client_name: str,
    audit_scope: str = "Codigo-fonte",
    auditor: str = "Auditor",
) -> AuditReport:
    """Funcao principal — gera relatorio de auditoria completo.

    Args:
        findings_path: Caminho para o JSON de findings do pii-guard
        client_name: Nome do cliente auditado
        audit_scope: Escopo da auditoria
        auditor: Nome do auditor

    Returns:
        AuditReport completo com riscos, remediacao, evidencias e resumo
    """
    # 1. Carregar findings do pii-guard
    findings = load_findings(findings_path)

    # 2. Converter em RiskItems com scoring e mapeamento
    risk_items = build_risk_items(findings)

    # 3. Gerar plano de remediacao
    remediation_plan = build_remediation_plan(risk_items)

    # 4. Gerar cadeia de evidencias
    evidence_chain = build_evidence_chain(risk_items)

    # 5. Gerar resumo executivo
    executive_summary = generate_executive_summary(risk_items, client_name)

    # 6. Montar relatorio
    report = AuditReport(
        report_id=f"AUD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
        client_name=client_name,
        audit_scope=audit_scope,
        auditor=auditor,
        risk_items=risk_items,
        remediation_plan=remediation_plan,
        evidence_chain=evidence_chain,
        executive_summary=executive_summary,
    )

    # 7. Recalcular estatisticas
    report.compute_summary()

    return report