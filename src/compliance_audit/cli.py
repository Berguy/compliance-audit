"""
Interface de linha de comando do compliance-audit.

Uso:
    compliance-audit --input findings.json --client "Empresa X" --output relatorio.pdf
    compliance-audit --input findings.json --client "Empresa X" --format json
    compliance-audit --input findings.json --client "Empresa X" --format summary
"""

import json
import sys

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from compliance_audit.engine import generate_audit_report
from compliance_audit.generators.pdf_generator import generate_pdf
from compliance_audit.risk.matrix import get_risk_matrix_summary

console = Console()

@click.command()
@click.option(
    "--input", "-i", "input_path",
    required=True,
    help="Caminho para o arquivo JSON de findings do pii-guard",
)
@click.option(
    "--client", "-c", "client_name",
    required=True,
    help="Nome do cliente auditado",
)
@click.option(
    "--output", "-o", "output_path",
    default="relatorio_auditoria.pdf",
    help="Caminho do PDF de saida (padrao: relatorio_auditoria.pdf)",
)
@click.option(
    "--format", "-f", "output_format",
    type=click.Choice(["pdf", "json", "summary"]),
    default="pdf",
    help="Formato de saida: pdf, json ou summary",
)
@click.option(
    "--scope", "-s", "audit_scope",
    default="Codigo-fonte",
    help="Escopo da auditoria",
)
@click.option(
    "--auditor", "-a", "auditor_name",
    default="Auditor",
    help="Nome do auditor",
)
def main(
    input_path: str,
    client_name: str,
    output_path: str,
    output_format: str,
    audit_scope: str,
    auditor_name: str,
):
    """Gera relatorio de auditoria de conformidade LGPD/ISO 27000."""

    console.print()
    console.print(Panel.fit(
        f"[bold blue]COMPLIANCE-AUDIT[/bold blue]\n"
        f"Motor de Auditoria LGPD / ISO 27000\n"
        f"Cliente: [bold]{client_name}[/bold]",
        border_style="blue",
    ))
    console.print()

    # 1. Gerar relatorio
    console.print("[dim]Gerando relatorio de auditoria...[/dim]")
    try:
        report = generate_audit_report(
            findings_path=input_path,
            client_name=client_name,
            audit_scope=audit_scope,
            auditor=auditor_name,
        )
    except FileNotFoundError as e:
        console.print(f"[red]Erro: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro inesperado: {e}[/red]")
        sys.exit(1)

    # 2. Mostrar resumo no terminal
    _print_summary(report)

    # 3. Gerar saida no formato solicitado
    if output_format == "pdf":
        console.print(f"\n[dim]Gerando PDF em {output_path}...[/dim]")
        generate_pdf(report, output_path)
        console.print(f"[green]Relatorio PDF gerado: {output_path}[/green]")

    elif output_format == "json":
        report_dict = report.model_dump()
        # Converter datetime para string
        _serialize_datetimes(report_dict)
        if output_path.endswith(".json"):
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_dict, f, ensure_ascii=False, indent=2)
            console.print(f"[green]Relatorio JSON salvo: {output_path}[/green]")
        else:
            console.print_json(json.dumps(report_dict, ensure_ascii=False, indent=2))

    elif output_format == "summary":
        summary = get_risk_matrix_summary(report.risk_items)
        _print_risk_summary(summary, client_name)

def _print_summary(report) -> None:
    """Imprime resumo do relatorio no terminal."""
    console.print()
    table = Table(title="Resumo da Auditoria", show_header=True, header_style="bold blue")
    table.add_column("Metrica", style="bold")
    table.add_column("Valor", justify="right")

    table.add_row("Total de Findings", str(report.total_findings))
    table.add_row("Criticos", f"[red]{report.critical_count}[/red]")
    table.add_row("Altos", f"[orange]{report.high_count}[/orange]")
    table.add_row("Medios", f"[yellow]{report.medium_count}[/yellow]")
    table.add_row("Baixos", f"[green]{report.low_count}[/green]")
    table.add_row("ID Relatorio", report.report_id)
    table.add_row("Cliente", report.client_name)
    table.add_row("Auditor", report.auditor)

    console.print(table)
    console.print()

    # Top 5 riscos
    if report.risk_items:
        risk_table = Table(title="Top 5 Riscos", show_header=True, header_style="bold red")
        risk_table.add_column("ID", style="dim")
        risk_table.add_column("Regra")
        risk_table.add_column("Score", justify="center")
        risk_table.add_column("Nivel")
        risk_table.add_column("Arquivo:Linha")
        risk_table.add_column("LGPD")
        risk_table.add_column("ISO")

        sorted_items = sorted(report.risk_items, key=lambda r: r.risk_score, reverse=True)
        for item in sorted_items[:5]:
            level_str = item.risk_level.value.upper()
            if item.risk_level.value == "critical":
                level_str = f"[red]{level_str}[/red]"
            elif item.risk_level.value == "high":
                level_str = f"[orange]{level_str}[/orange]"
            elif item.risk_level.value == "medium":
                level_str = f"[yellow]{level_str}[/yellow]"
            else:
                level_str = f"[green]{level_str}[/green]"

            risk_table.add_row(
                item.finding_id,
                item.rule_id,
                f"{item.risk_score}/25",
                level_str,
                f"{item.file_path.split('/')[-1]}:{item.line_number}",
                item.compliance.lgpd_article,
                item.compliance.iso_control,
            )

        console.print(risk_table)
        console.print()

        # Plano de remediacao
        if report.remediation_plan:
            rem_table = Table(title="Plano de Remediacao (Top 5)", show_header=True, header_style="bold yellow")
            rem_table.add_column("ID Acao", style="dim")
            rem_table.add_column("Finding")
            rem_table.add_column("Prioridade", justify="center")
            rem_table.add_column("Esforco")
            rem_table.add_column("Titulo")

            for action in report.remediation_plan[:5]:
                prio_str = f"P{action.priority}"
                if action.priority >= 5:
                    prio_str = f"[red]{prio_str}[/red]"
                elif action.priority >= 4:
                    prio_str = f"[orange]{prio_str}[/orange]"
                elif action.priority >= 3:
                    prio_str = f"[yellow]{prio_str}[/yellow]"

                rem_table.add_row(
                    action.action_id,
                    action.finding_id,
                    prio_str,
                    action.estimated_effort,
                    action.title,
                )

            console.print(rem_table)
            console.print()

def _print_risk_summary(summary: dict, client_name: str) -> None:
    """Imprime resumo compacto da matriz de riscos."""
    console.print()
    console.print(Panel.fit(
        f"[bold]Matriz de Riscos — {client_name}[/bold]",
        border_style="blue",
    ))
    console.print()

    by_level = summary.get("by_level", {})
    console.print(f"  Total de riscos: [bold]{summary['total']}[/bold]")
    console.print(f"  Score medio: [bold]{summary['avg_score']}/25[/bold]")
    console.print()
    console.print(f"  Criticos: [red]{by_level.get('critical', 0)}[/red]")
    console.print(f"  Altos: [orange]{by_level.get('high', 0)}[/orange]")
    console.print(f"  Medios: [yellow]{by_level.get('medium', 0)}[/yellow]")
    console.print(f"  Baixos: [green]{by_level.get('low', 0)}[/green]")
    console.print(f"  Negligenciaveis: [dim]{by_level.get('negligible', 0)}[/dim]")
    console.print()

    top_risks = summary.get("top_risks", [])
    if top_risks:
        console.print("[bold]Top 3 Riscos:[/bold]")
        for i, risk in enumerate(top_risks):
            console.print(
                f"  {i+1}. {risk['rule_id']} — "
                f"Score: {risk['score']}/25 ({risk['level']}) — "
                f"{risk['file']}:{risk['line']}"
            )

def _serialize_datetimes(obj):
    """Converte objetos datetime para string recursivamente."""
    from datetime import datetime
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, datetime):
                obj[k] = v.isoformat()
            else:
                _serialize_datetimes(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, datetime):
                obj[i] = v.isoformat()
            else:
                _serialize_datetimes(v)

if __name__ == "__main__":
    main()