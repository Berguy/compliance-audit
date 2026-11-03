"""
Modelos de dados do compliance-audit.

Define as estruturas que representam um relatório de auditoria
formal, com matriz de riscos, plano de remediação e evidências.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Níveis de risco da matriz 5x5."""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RemediationStatus(str, Enum):
    """Status de remediação de um finding."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"  # Risco aceito formalmente

class EvidenceType(str, Enum):
    """Tipos de evidência documental."""
    SCREENSHOT = "screenshot"
    LOG = "log"
    CODE_SNIPPET = "code_snippet"
    CONFIG_FILE = "config_file"
    POLICY_DOC = "policy_doc"
    INTERVIEW = "interview"

class ComplianceMapping(BaseModel):
    """Mapeamento de um finding para LGPD e ISO 27000."""
    lgpd_article: str = Field(description="Artigo da LGPD ex: 'Art. 11'")
    lgpd_text: str = Field(description="Texto resumido do artigo")
    lgpd_implication: str = Field(description="Implicação jurídica prática")
    iso_control: str = Field(description="Controle ISO ex: 'A.8.10'")
    iso_standard: str = Field(description="Norma ex: 'ISO 27001:2022'")
    iso_description: str = Field(description="Descrição do controle")
    iso_family: str = Field(description="Família ex: 'A.8 — Gestão de ativos'")

class RiskItem(BaseModel):
    """Item individual na matriz de riscos."""
    finding_id: str
    rule_id: str
    description: str
    file_path: str
    line_number: int
    likelihood: int = Field(ge=1, le=5, description="Probabilidade 1-5")
    impact: int = Field(ge=1, le=5, description="Impacto 1-5")
    risk_score: int = Field(description="likelihood × impact")
    risk_level: RiskLevel
    compliance: ComplianceMapping
    recommendation: str

class RemediationAction(BaseModel):
    """Ação de remediação para um finding."""
    action_id: str
    finding_id: str
    title: str
    description: str
    priority: int = Field(ge=1, le=5, description="Prioridade 1-5")
    estimated_effort: str = Field(description="Ex: '2h', '1dia', '1semana'")
    status: RemediationStatus = RemediationStatus.OPEN
    assigned_to: str = Field(default="", description="Responsável")
    due_date: str = Field(default="", description="Prazo ISO 8601")

class EvidenceItem(BaseModel):
    """Evidência documental com cadeia de custódia."""
    evidence_id: str
    finding_id: str
    evidence_type: EvidenceType
    description: str
    collected_at: datetime = Field(default_factory=datetime.now)
    collected_by: str = Field(default="auditor")
    file_hash: str = Field(default="", description="SHA-256 do arquivo evidencial")
    location: str = Field(description="Onde a evidência está armazenada")

class AuditReport(BaseModel):
    """Relatório formal de auditoria de conformidade."""
    report_id: str
    client_name: str
    audit_scope: str = Field(description="Escopo da auditoria")
    audit_date: datetime = Field(default_factory=datetime.now)
    auditor: str = Field(default="")
    # Estatísticas
    total_findings: int = 0
    files_scanned: int = 0
    # Riscos
    risk_items: list[RiskItem] = Field(default_factory=list)
    # Plano de remediação
    remediation_plan: list[RemediationAction] = Field(default_factory=list)
    # Evidências
    evidence_chain: list[EvidenceItem] = Field(default_factory=list)
    # Resumo executivo
    executive_summary: str = ""
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    negligible_count: int = 0

    def compute_summary(self) -> None:
        """Recalcula contadores a partir dos risk_items."""
        self.total_findings = len(self.risk_items)
        self.critical_count = sum(1 for r in self.risk_items if r.risk_level == RiskLevel.CRITICAL)
        self.high_count = sum(1 for r in self.risk_items if r.risk_level == RiskLevel.HIGH)
        self.medium_count = sum(1 for r in self.risk_items if r.risk_level == RiskLevel.MEDIUM)
        self.low_count = sum(1 for r in self.risk_items if r.risk_level == RiskLevel.LOW)
        self.negligible_count = sum(1 for r in self.risk_items if r.risk_level == RiskLevel.NEGLIGIBLE)