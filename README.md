# 📋 compliance-audit

Motor de auditoria de conformidade **LGPD / ISO 27000** que consome findings do [pii-guard](https://github.com/Berguy/pii-guard) e gera relatórios formais de auditoria com matriz de riscos, plano de remediação e cadeia de evidências.

## 🔎 O que faz

- **Consume** findings do pii-guard (JSON)
- **Enriquece** cada achado com mapeamento jurídico (LGPD) e normativo (ISO 27000)
- **Calcula** risco quantitativo (matriz 5×5 — likelihood × impact, ISO 27005)
- **Gera** plano de remediação priorizado
- **Produz** cadeia de evidências com data e localização
- **Exporta** relatório PDF formal com capa, sumário, matriz e mapeamento legal

## 📦 Instalação

```bash
git clone https://github.com/Berguy/compliance-audit.git
cd compliance-audit
python -m venv .venv
source .venv/Scripts/activate    # Windows
# source .venv/bin/activate       # Linux/macOS
pip install -e .

🚀 Uso
Gerando relatório PDF

compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --output relatorio_auditoria.pdf \
  --auditor "Berguy Silva"

Output JSON (em vez de PDF)

compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --format json

Resumo compacto no terminal

compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --format summary

  📊 Estrutura do relatório PDF

  Seção                                          Conteúdo

  Capa                    Cliente, escopo, data, auditor, ID do relatório, contadores
  Resumo                  ExecutivoDistribuição de riscos, top 3, recomendações, base legal
  Matriz de riscos        Todos os findings com score, nível, LGPD, ISO e recomendação
  Plano de Remediação     Ações priorizadas com esforço estimado e status
  Cadeia de Evidências    Evidências com data de coleta e localização
  Mapeamento Legal        Artigos da LGPD e controles ISO 27000 detalhados

 Base de conhecimento

 LGPD (Lei nº 13.709/2018)
 11 artigos mapeados com texto resumido, implicação prática e controle ISO correspondente:
 Art. 5, Art. 7, Art. 11, Art. 12, Art. 23, Art. 25, Art. 37, Art. 41, Art. 46, Art. 48, Art. 52

 ISO 27000 (família)
 14 controles mapeados cobrindo 5 normas:

    Norma                    Foco                        Controles
 ISO 27001:2022       Requisitos do SGSI         A.5.1, A.5.2, A.5.19, A.5.24, A.5.34, A.8.10, A.8.24, A.8.25
 ISO 27002:2022       Controles e boas práticas  A.8.12, A.8.15, A.8.28
 ISO 27005:2022       Gestão de risco            A.5.7
 ISO 27017:2015       Segurança em nuvem         A.5.23
 ISO 27018:2019       Proteção de PII em nuvem   A.5.34

 🏗️ Arquitetura

 compliance-audit/
├── src/compliance_audit/
│   ├── models.py              # AuditReport, RiskItem, RemediationAction, EvidenceItem
│   ├── engine.py              # Motor principal — consome findings, gera relatório
│   ├── cli.py                 # Interface de linha de comando (click)
│   ├── generators/
│   │   └── pdf_generator.py   # Gera relatório PDF (reportlab)
│   ├── knowledge_base/
│   │   ├── lgpd.py            # 11 artigos da LGPD mapeados
│   │   └── iso27000.py        # 14 controles ISO 27000 mapeados
│   └── risk/
│       └── matrix.py          # Matriz 5×5, scoring, priorização
├── tests/
├── pyproject.toml
└── README.md

🔗 Integração com pii-guard

Fluxo completo de auditoria:

pii-guard (scanner)          compliance-audit (motor)
┌─────────────────┐          ┌──────────────────────┐
│  Escanear       │          │  Consumir findings   │
│  código-fonte   │──JSON──>│  Calcular riscos     │
│  Detectar PII   │          │  Mapear LGPD/ISO     │
│  Detectar secrets│         │  Gerar PDF formal    │
└─────────────────┘          └──────────────────────┘

Pipeline completo

# 1. Escanear código com pii-guard
pii-guard src/ --format json --output findings.json

# 2. Gerar relatório de auditoria
compliance-audit --input findings.json --client "Empresa X" --output relatorio.pdf

⚙️ Opções da CLI

  Opção                          Descrição                                       Padrão

--input, -i            Caminho do JSON de findings do pii-guard               obrigatório
--client, -c           Nome do cliente auditado                               obrigatório
--output, -o           Caminho do PDF de saída                          relatorio_auditoria.pdf
--format, -f           Formato: pdf, json ou summary                              pdf
--scope, -s            Escopo da auditoria                                    Codigo-fonte
--auditor, -a          Nome do auditor                                           Auditor

📐 Matriz de Riscos

Score = likelihood (1-5) × impact (1-5) = 1 a 25

Score            Nível                                    Ação

20-25        🔴 CRÍTICO             Remediação imediata — pode ser incidente notificável (Art. 48)
15-19        🟠 ALTO                Tratar em até 72h
10-14        🟡 MÉDIO               Incluir no plano de tratamento de risco
5-9          🟢 BAIXO               Monitorar e programar correção
1-4          ⚪ NEGLIGENCIÁVEL      Observação
```
