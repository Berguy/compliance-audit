"""Configuração compartilhada dos testes do compliance-audit."""

import json

import pytest


@pytest.fixture()
def findings_sample():
    """Findings de exemplo no formato produzido pelo pii-guard."""
    return [
        {
            "id": "Finding-001",
            "rule_id": "AWS_ACCESS_KEY",
            "description": "AWS Access Key ID exposta no código",
            "file_path": "src/config.py",
            "line_number": 12,
            "severity": "CRITICAL",
        },
        {
            "id": "Finding-002",
            "rule_id": "BR_CPF",
            "description": "CPF exposto no código",
            "file_path": "src/clientes.py",
            "line_number": 47,
            "severity": "CRITICAL",
        },
        {
            "id": "Finding-003",
            "rule_id": "BR_CEP",
            "description": "CEP exposto no código",
            "file_path": "src/enderecos.py",
            "line_number": 8,
            "severity": "LOW",
        },
    ]


@pytest.fixture()
def findings_file(tmp_path, findings_sample):
    """Grava os findings de exemplo em um arquivo JSON temporário."""
    caminho = tmp_path / "findings.json"
    caminho.write_text(
        json.dumps({"findings": findings_sample}, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(caminho)


@pytest.fixture()
def findings_file_lista(tmp_path, findings_sample):
    """Grava os findings como lista pura, sem o wrapper 'findings'."""
    caminho = tmp_path / "findings_lista.json"
    caminho.write_text(json.dumps(findings_sample, ensure_ascii=False), encoding="utf-8")
    return str(caminho)
