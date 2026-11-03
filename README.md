# Compliance Audit

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![CI](https://github.com/Berguy/compliance-audit/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-28%20passing-brightgreen)

**Motor de auditoria de conformidade LGPD e ISO 27001 para achados de segurança.**

O Compliance Audit consome os findings gerados pelo pii-guard, calcula risco quantitativo em matriz 5×5, prioriza a remediação e produz um relatório formal em PDF com capa, sumário executivo, matriz de riscos, mapeamento legal e cadeia de evidências.

---

## Por que este projeto existe

Um scanner de segurança entrega uma lista de problemas. Uma auditoria entrega uma decisão.

A diferença está no que acontece depois da detecção. Saber que existe uma chave AWS exposta na linha 12 do arquivo de configuração é útil. Saber que ela é risco crítico, que viola o artigo 46 da LGPD, que corresponde ao controle A.8.24 da ISO 27001 e que precisa ser corrigida antes de qualquer outra coisa — isso é o que permite agir.

O Compliance Audit preenche essa lacuna. Ele não detecta nada: transforma detecção em decisão documentada, com base legal e ordem de prioridade.

## O que já funciona

### Consumo de findings
- Leitura do JSON gerado pelo pii-guard
- Suporte aos dois formatos: com wrapper `{"findings": [...]}` ou lista pura
- Validação da estrutura de entrada

### Cálculo de risco quantitativo
- Matriz 5×5 combinando probabilidade e impacto, conforme ISO 27005
- Pontuação de risco por achado, de 1 a 25
- Classificação em cinco níveis: negligenciável, baixo, médio, alto e crítico
- Priorização automática da fila de remediação

### Mapeamento normativo
- 11 artigos da LGPD mapeados
- 14 controles da ISO 27000 mapeados
- Base legal associada a cada tipo de achado
- Referência normativa complementar (ISO 27017 e 27018 para ambientes de nuvem)

### Plano de remediação
- Ação recomendada por achado
- Ordenação por criticidade
- Estimativa de esforço por prioridade

### Cadeia de evidências
- Registro de data e localização de cada achado
- Rastreabilidade entre detecção e relatório
- Estrutura adequada para uso probatório e auditoria formal

### Relatório PDF formal
- Capa com cliente, escopo, data, auditor, identificação do relatório e contadores
- Resumo executivo com distribuição de riscos, top 3 achados, recomendações e base legal
- Matriz de riscos
- Mapeamento legal detalhado
- Plano de remediação priorizado

### Três formatos de saída
- PDF formal para entrega ao cliente
- JSON estruturado para integração com outros sistemas
- Resumo compacto no terminal para uso rápido

## Ecossistema

O Compliance Audit é o motor de um conjunto de três projetos que se complementam:

| Projeto | Função | Repositório |
|---|---|---|
| pii-guard | Scanner de secrets e PII | [github.com/Berguy/pii-guard](https://github.com/Berguy/pii-guard) |
| compliance-audit | Motor de mapeamento LGPD/ISO | este repositório |
| compliance-suite | Interface web e relatórios | [github.com/Berguy/compliance-suite](https://github.com/Berguy/compliance-suite) |

Cada um funciona de forma independente. Juntos, formam um pipeline completo de auditoria de conformidade.

## Instalação

Requisitos: Python 3.11 ou superior.

```bash
git clone https://github.com/Berguy/compliance-audit.git
cd compliance-audit

python -m venv .venv

# Windows (Git Bash)
source .venv/Scripts/activate
# Linux / macOS
# source .venv/bin/activate

pip install -e .
```

## Uso

### Gerar relatório PDF

```bash
compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --output relatorio_auditoria.pdf \
  --auditor "Berguy Silva"
```

### Gerar saída JSON

```bash
compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --format json
```

### Ver resumo no terminal

```bash
compliance-audit \
  --input findings.json \
  --client "Empresa Exemplo Ltda" \
  --format summary
```

### Opções da CLI

| Opção | Atalho | Descrição | Padrão |
|---|---|---|---|
| `--input` | `-i` | Caminho do JSON de findings do pii-guard | obrigatório |
| `--client` | `-c` | Nome do cliente auditado | obrigatório |
| `--output` | `-o` | Caminho do arquivo de saída | `relatorio_auditoria.pdf` |
| `--format` | `-f` | Formato de saída: `pdf`, `json` ou `summary` | `pdf` |
| `--scope` | `-s` | Escopo da auditoria | `Codigo-fonte` |
| `--auditor` | `-a` | Nome do auditor responsável | `Auditor` |

## Matriz de riscos

O score é calculado como probabilidade (1 a 5) multiplicada pelo impacto (1 a 5), resultando em um valor de 1 a 25.

| Score | Nível | Ação recomendada |
|---|---|---|
| 20 a 25 | Crítico | Remediação imediata — pode ser incidente notificável (Art. 48) |
| 15 a 19 | Alto | Tratar em até 72 horas |
| 10 a 14 | Médio | Incluir no plano de tratamento de risco |
| 5 a 9 | Baixo | Monitorar e programar correção |
| 1 a 4 | Negligenciável | Observação |

A conversão de severidade do pii-guard para probabilidade e impacto é direta: crítico vira 5×5, alto 4×4, médio 3×3, baixo 2×2 e informativo 1×1.

## Pipeline completo

Os dois projetos foram feitos para trabalhar em sequência:

```bash
# 1. Escanear o código com pii-guard
pii-guard src/ --format json --output findings.json

# 2. Gerar o relatório de auditoria
compliance-audit --input findings.json --client "Empresa X" --output relatorio.pdf
```

```text
pii-guard (scanner)          compliance-audit (motor)
┌─────────────────┐          ┌──────────────────────┐
│  Escanear       │          │  Consumir findings   │
│  código-fonte   │──JSON───►│  Calcular riscos     │
│  Detectar PII   │          │  Mapear LGPD/ISO     │
│  Detectar secrets│         │  Gerar PDF formal    │
└─────────────────┘          └──────────────────────┘
```

## Estrutura do projeto

```text
compliance-audit/
├── src/compliance_audit/
│   ├── models.py              # AuditReport, RiskItem, RemediationAction, EvidenceItem
│   ├── engine.py              # Motor principal — consome findings, gera relatório
│   ├── cli.py                 # Interface de linha de comando (Click)
│   ├── generators/
│   │   └── pdf_generator.py   # Geração do relatório PDF (ReportLab)
│   ├── knowledge_base/
│   │   ├── lgpd.py            # 11 artigos da LGPD mapeados
│   │   └── iso27000.py        # 14 controles ISO 27000 mapeados
│   └── risk/
│       └── matrix.py          # Matriz 5×5, scoring e priorização
├── tests/
│   ├── conftest.py            # Fixtures compartilhadas
│   ├── test_matrix.py         # Testes da matriz de riscos
│   ├── test_engine.py         # Testes do motor
│   └── test_models.py         # Testes dos modelos
├── .github/
│   └── workflows/
│       └── ci.yml             # Integração contínua
├── pytest.ini
├── pyproject.toml
├── LICENSE
└── README.md
```

## Testes

O projeto usa pytest. Para executar:

```bash
pip install -e .
pip install pytest
pytest
```

A suíte tem 28 testes cobrindo:

- Cálculo de score e conversão para nível de risco nas cinco faixas
- Criação de itens de risco, incluindo severidade em minúsculas e regra desconhecida
- Priorização de remediação ordenada por score
- Resumo da matriz com e sem itens
- Carregamento de findings nos dois formatos e tratamento de arquivo inválido
- Construção de itens de risco, plano de remediação e cadeia de evidências
- Geração do relatório completo e com zero achados
- Validação dos modelos, incluindo rejeição de valores fora do intervalo
- Recálculo de contadores do relatório

A integração contínua roda em Python 3.11, 3.12 e 3.13, com lint via Ruff.

## Estrutura do relatório PDF

| Seção | Conteúdo |
|---|---|
| Capa | Cliente, escopo, data, auditor, ID do relatório, contadores |
| Resumo executivo | Distribuição de riscos, top 3 achados, recomendações, base legal |
| Matriz de riscos | Probabilidade × impacto, pontuação por achado |
| Mapeamento legal | Artigo da LGPD e controle ISO por achado |
| Plano de remediação | Ações priorizadas por criticidade |
| Cadeia de evidências | Data e localização de cada achado |

## Roadmap

| Etapa | Escopo | Status |
|---|---|---|
| Consumo de findings do pii-guard | Leitura e validação do JSON | Concluída |
| Matriz de risco 5×5 | Cálculo conforme ISO 27005 | Concluída |
| Base de conhecimento LGPD | 11 artigos mapeados | Concluída |
| Base de conhecimento ISO 27000 | 14 controles mapeados | Concluída |
| Geração de relatório PDF | Capa, resumo, matriz e remediação | Concluída |
| CLI com três formatos | pdf, json, summary | Concluída |
| Suíte de testes automatizados | 28 testes com pytest | Concluída |
| Integração contínua | GitHub Actions em Python 3.11, 3.12 e 3.13 | Concluída |
| Exportação para CSV | Formato alternativo de relatório | Planejada |
| Assinatura digital do PDF | Validação de autenticidade do relatório | Planejada |

## Contribuindo

Contribuições são bem-vindas. Para mudanças relevantes, abra uma issue descrevendo o problema ou a proposta antes de enviar um pull request.

```bash
git checkout -b feature/nome-da-feature
pytest          # garanta que os testes passam
git commit -m "feat: descrição da mudança"
```

## Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para os termos completos.

## Autor

**Berguy Silva** — Engenheiro de software, pós-graduado em Computação Forense e Perícia Digital e em Gestão de Projetos.

- LinkedIn: https://www.linkedin.com/in/BerguySilva
- GitHub: https://github.com/Berguy
- Email: contato@berguysilva.com.br

**Versão:** 1.0 · **Data:** novembro de 2026
