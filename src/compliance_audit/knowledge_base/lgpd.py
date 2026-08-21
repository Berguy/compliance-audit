"""
Base de conhecimento da LGPD (Lei nº 13.709/2018).

Mapeia os artigos mais relevantes para auditoria de conformidade
em software, com texto resumido, implicação prática e controle
correspondente da família ISO 27000.
"""

from dataclasses import dataclass

@dataclass
class LGPDArticle:
    """Estrutura de um artigo da LGPD."""
    article: str           # Ex: "Art. 5"
    title: str             # Ex: "Direitos do titular"
    summary: str           # Texto resumido do artigo
    implication: str       # Implicação prática para auditoria
    iso_mapping: str       # Controle ISO correspondente Ex: "A.8.10"

# Base de conhecimento — artigos relevantes para auditoria de software
LGPD_KNOWLEDGE_BASE: dict[str, LGPDArticle] = {
    "Art. 5": LGPDArticle(
        article="Art. 5",
        title="Direitos do titular de dados pessoais",
        summary="O titular tem direito ao acesso, retificação, eliminação, portabilidade e informação sobre o uso de seus dados.",
        implication="O sistema deve permitir rastrear onde dados pessoais estão armazenados para atender a solicitações do titular.",
        iso_mapping="A.8.10",
    ),
    "Art. 7": LGPDArticle(
        article="Art. 7",
        title="Bases legais para tratamento de dados",
        summary="O tratamento de dados pessoais somente pode ocorrer com base legal (consentimento, obrigação legal, execução de contrato, etc.).",
        implication="Todo dado pessoal encontrado no código deve ter base legal documentada e rastreável.",
        iso_mapping="A.5.34",
    ),
    "Art. 11": LGPDArticle(
        article="Art. 11",
        title="Dados sensíveis",
        summary="Dados sensíveis (origem racial, convicção religiosa, saúde, biometria, etc.) exigem proteção reforçada e consentimento específico.",
        implication="Dados sensíveis hardcoded no código são violação crítica — exigem criptografia e acesso restrito imediatamente.",
        iso_mapping="A.8.10",
    ),
    "Art. 12": LGPDArticle(
        article="Art. 12",
        title="Comunicação ao titular",
        summary="O controlador deve comunicar de forma clara e adequada sobre o tratamento de dados.",
        implication="Logs e mensagens do sistema não devem expor dados pessoais visíveis a usuários não autorizados.",
        iso_mapping="A.8.15",
    ),
    "Art. 23": LGPDArticle(
        article="Art. 23",
        title="Segurança e boa-fé",
        summary="O controlador deve adotar medidas de segurança técnicas e organizacionais para proteger dados pessoais.",
        implication="A ausência de criptografia, controle de acesso ou monitoramento de logs é violação direta deste artigo.",
        iso_mapping="A.8.24",
    ),
    "Art. 25": LGPDArticle(
        article="Art. 25",
        title="Notificação de incidentes",
        summary="O controlador deve comunicar incidentes de segurança que possam acarretar risco aos titulares à ANPD e aos afetados.",
        implication="Toda exposição de dados encontrada deve ser classificada como incidente potencial e notificada.",
        iso_mapping="A.5.24",
    ),
    "Art. 37": LGPDArticle(
        article="Art. 37",
        title="Responsabilidade do operador",
        summary="O operador deve seguir as instruções do controlador e aplicar medidas de segurança.",
        implication="Terceiros que processam dados (APIs, serviços cloud) devem ter contrato com cláusulas de segurança.",
        iso_mapping="A.5.19",
    ),
    "Art. 41": LGPDArticle(
        article="Art. 41",
        title="Encarregado de dados (DPO)",
        summary="O controlador deve designar um encarregado de tratamento de dados pessoais (DPO).",
        implication="O relatório de auditoria deve ser endereçado ao DPO como responsável pela governança.",
        iso_mapping="A.5.2",
    ),
    "Art. 46": LGPDArticle(
        article="Art. 46",
        title="Medidas de segurança",
        summary="O tratamento de dados pessoais deve ocorrer com adoção de medidas de segurança capazes de proteger os dados de acessos não autorizados e situações de destruição, perda, alteração ou comunicação indevida.",
        implication="Secrets hardcoded, PII em texto plano e ausência de controle de acesso são violações diretas deste artigo.",
        iso_mapping="A.8.24",
    ),
    "Art. 48": LGPDArticle(
        article="Art. 48",
        title="Comunicação de incidentes à ANPD",
        summary="A comunicação de incidente deve ser feita em prazo razoável, especificando a natureza dos dados, descrição do incidente e medidas adotadas.",
        implication="Todo finding crítico deve gerar um protocolo de incidente com data, descrição e plano de remediação.",
        iso_mapping="A.5.24",
    ),
    "Art. 52": LGPDArticle(
        article="Art. 52",
        title="Sanções administrativas",
        summary="A ANPD pode aplicar sanções: advertência, multa de até 2% do faturamento, bloqueio ou eliminação de dados.",
        implication="A matriz de riscos deve quantificar o impacto financeiro potencial de cada finding para priorização executiva.",
        iso_mapping="A.5.1",
    ),
}

def get_lgpd_article(article: str) -> LGPDArticle | None:
    """Busca um artigo da LGPD pelo identificador.

    Args:
        article: Identificador do artigo, ex: "Art. 11"

    Returns:
        LGPDArticle se encontrado, None caso contrário.
    """
    return LGPD_KNOWLEDGE_BASE.get(article)

def list_all_articles() -> list[LGPDArticle]:
    """Retorna todos os artigos da base de conhecimento."""
    return list(LGPD_KNOWLEDGE_BASE.values())