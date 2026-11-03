"""
Base de conhecimento da familia ISO 27000.

Mapeia os controles mais relevantes para auditoria de conformidade
em software, cobrindo ISO 27001, 27002, 27005, 27017 e 27018.
"""

from dataclasses import dataclass


@dataclass
class ISOControl:
    """Estrutura de um controle da familia ISO 27000."""
    control_id: str        # Ex: "A.8.10"
    standard: str           # Ex: "ISO 27001:2022"
    family: str             # Ex: "A.8 — Gestao de ativos"
    title: str              # Ex: "Supressao de informacao"
    description: str        # Descricao do controle
    guidance: str           # Orientacao pratica de implementacao
    lgpd_mapping: str       # Artigo LGPD correspondente Ex: "Art. 11"

# Base de conhecimento — controles relevantes para auditoria de software
ISO_KNOWLEDGE_BASE: dict[str, ISOControl] = {
    "A.5.1": ISOControl(
        control_id="A.5.1",
        standard="ISO 27001:2022",
        family="A.5 — Politicas de seguranca da informacao",
        title="Politicas para a seguranca da informacao",
        description="Define politicas de seguranca da informacao aprovadas pela gestao, publicadas e comunicadas.",
        guidance="Verificar se existe politica de seguranca documentada e se os desenvolvedores tem conhecimento.",
        lgpd_mapping="Art. 52",
    ),
    "A.5.2": ISOControl(
        control_id="A.5.2",
        standard="ISO 27001:2022",
        family="A.5 — Politicas de seguranca da informacao",
        title="Funcoes e responsabilidades da seguranca da informacao",
        description="Atribui e comunicam funcoes e responsabilidades de seguranca da informacao.",
        guidance="Verificar se existe DPO ou responsavel designado para protecao de dados.",
        lgpd_mapping="Art. 41",
    ),
    "A.5.19": ISOControl(
        control_id="A.5.19",
        standard="ISO 27001:2022",
        family="A.5 — Politicas de seguranca da informacao",
        title="Seguranca na gestao de fornecedores",
        description="Define processos para tratar riscos de seguranca relacionados a fornecedores.",
        guidance="Verificar contratos com terceiros que processam dados (cloud, APIs) tem clausulas de seguranca.",
        lgpd_mapping="Art. 37",
    ),
    "A.5.24": ISOControl(
        control_id="A.5.24",
        standard="ISO 27001:2022",
        family="A.5 — Politicas de seguranca da informacao",
        title="Gestao de incidentes de seguranca da informacao",
        description="Planeja e prepara a gestao de incidentes de seguranca da informacao.",
        guidance="Todo finding critico deve gerar um protocolo de incidente com data, descricao e plano de remediacao.",
        lgpd_mapping="Art. 25",
    ),
    "A.5.34": ISOControl(
        control_id="A.5.34",
        standard="ISO 27001:2022",
        family="A.5 — Politicas de seguranca da informacao",
        title="Privacidade e protecao de PII",
        description="Identifica e atende aos requisitos de privacidade e protecao de PII.",
        guidance="Todo dado pessoal encontrado deve ter base legal documentada e rastreavel.",
        lgpd_mapping="Art. 7",
    ),
    "A.8.10": ISOControl(
        control_id="A.8.10",
        standard="ISO 27001:2022",
        family="A.8 — Gestao de ativos",
        title="Supressao e descarte de informacao",
        description="Garante que informacao seja suprimida ou descartada quando nao mais necessaria.",
        guidance="Dados pessoais e secrets hardcoded no codigo devem ser removidos e descartados de forma segura.",
        lgpd_mapping="Art. 11",
    ),
    "A.8.12": ISOControl(
        control_id="A.8.12",
        standard="ISO 27002:2022",
        family="A.8 — Gestao de ativos",
        title="Classificacao da informacao",
        description="Classifica a informacao de acordo com requisitos de seguranca e impacto de negocio.",
        guidance="Classificar cada finding como publico, interno, confidencial ou critico para priorizar remediacao.",
        lgpd_mapping="Art. 46",
    ),
    "A.8.15": ISOControl(
        control_id="A.8.15",
        standard="ISO 27002:2022",
        family="A.8 — Gestao de ativos",
        title="Transferencia de informacao",
        description="Garante a seguranca na transferencia de informacao entre sistemas e pessoas.",
        guidance="Logs e mensagens do sistema nao devem expor dados pessoais visiveis a usuarios nao autorizados.",
        lgpd_mapping="Art. 12",
    ),
    "A.8.24": ISOControl(
        control_id="A.8.24",
        standard="ISO 27001:2022",
        family="A.8 — Gestao de ativos",
        title="Uso de critptografia",
        description="Garante uso adequado e eficaz de criptografia para protecao de informacao.",
        guidance="Secrets hardcoded, PII em texto plano e ausencia de criptografia sao violacoes diretas.",
        lgpd_mapping="Art. 46",
    ),
    "A.8.25": ISOControl(
        control_id="A.8.25",
        standard="ISO 27001:2022",
        family="A.8 — Gestao de ativos",
        title="Desenvolvimento seguro",
        description="Estabelece requisitos de seguranca no ciclo de desenvolvimento de software.",
        guidance="Codigo deve ser auditado para secrets e PII antes de subir para producao.",
        lgpd_mapping="Art. 23",
    ),
    "A.8.28": ISOControl(
        control_id="A.8.28",
        standard="ISO 27002:2022",
        family="A.8 — Gestao de ativos",
        title="Codificacao segura",
        description="Define e aplica regras de codificacao segura para reduzir vulnerabilidades.",
        guidance="Implementar gate de qualidade que bloqueia commits com secrets ou PII expostos.",
        lgpd_mapping="Art. 23",
    ),
    # ISO 27005 — Gestao de risco
    "A.5.7": ISOControl(
        control_id="A.5.7",
        standard="ISO 27005:2022",
        family="A.5 — Gestao de risco",
        title="Avaliacao de risco de seguranca",
        description="Identifica, analisa e avalia riscos de seguranca da informacao.",
        guidance="Cada finding deve receber score de likelihood x impact na matriz de riscos.",
        lgpd_mapping="Art. 52",
    ),
    # ISO 27017 — Seguranca em nuvem
    "A.5.23": ISOControl(
        control_id="A.5.23",
        standard="ISO 27017:2015",
        family="A.5 — Seguranca em nuvem",
        title="Segregacao em ambientes de nuvem",
        description="Garante segregacao de dados entre clientes em ambientes de nuvem compartilhados.",
        guidance="Verificar se PII de diferentes clientes esta logicamente segregada em APIs e bancos de dados.",
        lgpd_mapping="Art. 46",
    ),
    # ISO 27018 — Protecao de PII em nuvem
    "A.5.34+": ISOControl(
        control_id="A.5.34+",
        standard="ISO 27018:2019",
        family="A.5 — Protecao de PII em nuvem",
        title="Protecao de PII em processamento em nuvem",
        description="Estabelece diretrizes especificas para protecao de PII em servicos de nuvem publica.",
        guidance="Verificar contratos com provedores cloud incluem clausulas de protecao de PII conforme LGPD.",
        lgpd_mapping="Art. 37",
    ),
}

def get_iso_control(control_id: str) -> ISOControl | None:
    """Busca um controle ISO pelo identificador.

    Args:
        control_id: Identificador do controle, ex: "A.8.10"

    Returns:
        ISOControl se encontrado, None caso contrario.
    """
    return ISO_KNOWLEDGE_BASE.get(control_id)

def list_all_controls() -> list[ISOControl]:
    """Retorna todos os controles da base de conhecimento."""
    return list(ISO_KNOWLEDGE_BASE.values())