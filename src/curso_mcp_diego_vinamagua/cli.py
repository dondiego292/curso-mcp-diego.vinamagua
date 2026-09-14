"""Interfaz de línea de comandos enriquecida (CLI) para validación de contraseñas, correos y lotes de usuarios."""

import getpass
import json
import sys
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

from .password_validator import PasswordValidator, ValidationResult, validate_password
from .email_validator import EmailValidator, EmailValidationResult, validate_email
from .user_validator import (
    UserData,
    UserValidationResult,
    BatchValidationReport,
    UserValidator,
    validate_user,
    validate_users,
)

console = Console()

SAMPLE_USERS: List[Dict[str, str]] = [
    {
        "username": "diego_v",
        "email": "diego.vinamagua@gmail.com",
        "password": "Password#2026Secure!",
    },
    {
        "username": "ana_dev",
        "email": "ana.lopez@empresa.com",
        "password": "AnaDev2026!",  # Contraseña contiene el usuario
    },
    {
        "username": "carlos_fake",
        "email": "carlos@mailinator.com",  # Dominio desechable
        "password": "K9#mQ8$zL2!wX5@v",
    },
    {
        "username": "maria_typo",
        "email": "maria@gmial.com",  # Typo sugerido
        "password": "Password123",  # Contraseña común
    },
    {
        "username": "diego_v",  # Username duplicado
        "email": "diego.otro@gmail.com",
        "password": "SuperSecurePass#99!",
    },
]


def format_strength_badge(strength: str, score: int) -> Text:
    """Devuelve un texto estilizado con el nivel de fortaleza."""
    color_map = {
        "Muy Débil": "bold red",
        "Débil": "bold dark_orange",
        "Media": "bold yellow",
        "Fuerte": "bold green",
        "Muy Fuerte": "bold bright_green",
    }
    style = color_map.get(strength, "white")
    return Text(f"{strength} ({score}/100)", style=style)


def display_password_result(result: ValidationResult) -> None:
    """Muestra un reporte visual completo de contraseña usando Rich."""
    console.print()
    if result.is_valid:
        status_text = Text("✔ CONTRASEÑA VÁLIDA", style="bold green")
    else:
        status_text = Text("✖ CONTRASEÑA INVÁLIDA", style="bold red")

    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_column("Key", style="cyan bold")
    summary_table.add_column("Value")

    summary_table.add_row("Estado:", status_text)
    summary_table.add_row("Fortaleza:", format_strength_badge(result.strength_label, result.score))
    summary_table.add_row("Entropía estimada:", f"[bold cyan]{result.entropy_bits}[/bold cyan] bits")

    console.print(
        Panel(
            summary_table,
            title="[bold blue]Resumen de Seguridad - Contraseña[/bold blue]",
            border_style="blue" if result.is_valid else "red",
        )
    )

    table = Table(title="Desglose de Criterios", show_header=True, header_style="bold magenta")
    table.add_column("Criterio", style="bold")
    table.add_column("Descripción")
    table.add_column("Tipo", justify="center")
    table.add_column("Estado", justify="center")

    for rule in result.rules:
        status = "[green]✔ Cumple[/green]" if rule.passed else "[red]✖ No cumple[/red]"
        imp_badge = (
            "[bold red]Obligatorio[/bold red]"
            if rule.importance == "required"
            else "[yellow]Recomendado[/yellow]"
        )
        table.add_row(rule.name, rule.description, imp_badge, status)

    console.print(table)

    if result.errors:
        err_text = "\n".join(f"• [red]{err}[/red]" for err in result.errors)
        console.print(Panel(err_text, title="[bold red]Requisitos no cumplidos[/bold red]", border_style="red"))

    if result.recommendations:
        rec_text = "\n".join(f"• [yellow]{rec}[/yellow]" for rec in result.recommendations)
        console.print(Panel(rec_text, title="[bold yellow]Sugerencias de mejora[/bold yellow]", border_style="yellow"))
    console.print()


def display_email_result(result: EmailValidationResult) -> None:
    """Muestra un reporte visual completo de correo electrónico usando Rich."""
    console.print()
    if result.is_valid:
        status_text = Text("✔ FORMATO DE EMAIL VÁLIDO", style="bold green")
    else:
        status_text = Text("✖ FORMATO DE EMAIL INVÁLIDO", style="bold red")

    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_column("Key", style="cyan bold")
    summary_table.add_column("Value")

    summary_table.add_row("Estado:", status_text)
    summary_table.add_row("Email ingresado:", f"[bold white]{result.email}[/bold white]")
    if result.normalized_email:
        summary_table.add_row("Email normalizado:", f"[bold cyan]{result.normalized_email}[/bold cyan]")
    if result.domain:
        summary_table.add_row("Dominio:", f"[yellow]{result.domain}[/yellow]")
    if result.is_disposable:
        summary_table.add_row("Desechable/Temporal:", "[bold red]Sí (Dominio de riesgo)[/bold red]")

    console.print(
        Panel(
            summary_table,
            title="[bold blue]Resumen de Validación - Correo Electrónico[/bold blue]",
            border_style="green" if result.is_valid else "red",
        )
    )

    table = Table(title="Comprobaciones de Formato y Dominio", show_header=True, header_style="bold magenta")
    table.add_column("Comprobación", style="bold")
    table.add_column("Descripción")
    table.add_column("Tipo", justify="center")
    table.add_column("Estado", justify="center")

    for rule in result.rules:
        status = "[green]✔ Correcto[/green]" if rule.passed else "[red]✖ Falló[/red]"
        imp_badge = (
            "[bold red]Obligatorio[/bold red]"
            if rule.importance == "required"
            else "[yellow]Advertencia[/yellow]"
        )
        table.add_row(rule.name, rule.description, imp_badge, status)

    console.print(table)

    if result.errors:
        err_text = "\n".join(f"• [red]{err}[/red]" for err in result.errors)
        console.print(Panel(err_text, title="[bold red]Errores de formato encontrados[/bold red]", border_style="red"))

    if result.warnings:
        warn_text = "\n".join(f"• [yellow]{w}[/yellow]" for w in result.warnings)
        console.print(Panel(warn_text, title="[bold yellow]Sugerencias / Advertencias[/bold yellow]", border_style="yellow"))
    console.print()


def display_batch_report(report: BatchValidationReport) -> None:
    """Muestra un reporte gráfico detallado para un lote de usuarios."""
    console.print()

    # Métricas generales
    summary_table = Table.grid(padding=(0, 2))
    summary_table.add_column("Key", style="cyan bold")
    summary_table.add_column("Value")

    overall_status = (
        Text("✔ TODOS LOS USUARIOS VÁLIDOS", style="bold green")
        if report.all_valid
        else Text(f"✖ HAY {report.invalid_count} USUARIO(S) CON ERRORES", style="bold red")
    )
    summary_table.add_row("Estado Global:", overall_status)
    summary_table.add_row("Total de usuarios:", str(report.total_users))
    summary_table.add_row("Usuarios válidos:", f"[bold green]{report.valid_count}[/bold green]")
    summary_table.add_row("Usuarios inválidos:", f"[bold red]{report.invalid_count}[/bold red]")
    summary_table.add_row("Tasa de éxito:", f"[bold cyan]{report.success_rate}%[/bold cyan]")

    if report.duplicate_emails:
        summary_table.add_row("Emails duplicados:", f"[bold red]{', '.join(report.duplicate_emails)}[/bold red]")
    if report.duplicate_usernames:
        summary_table.add_row("Usuarios duplicados:", f"[bold red]{', '.join(report.duplicate_usernames)}[/bold red]")

    console.print(
        Panel(
            summary_table,
            title="[bold blue]👥 Reporte de Validación de Usuarios (Lote)[/bold blue]",
            border_style="green" if report.all_valid else "red",
        )
    )

    # Tabla resumen por cada usuario
    table = Table(title="Detalle por Usuario", show_header=True, header_style="bold magenta")
    table.add_column("#", justify="center", style="dim")
    table.add_column("Usuario", style="bold")
    table.add_column("Email")
    table.add_column("Fortaleza Clave", justify="center")
    table.add_column("Estado Global", justify="center")
    table.add_column("Detalles / Errores")

    for idx, u_res in enumerate(report.results, 1):
        status_badge = "[green]✔ Válido[/green]" if u_res.is_valid else "[red]✖ Inválido[/red]"
        pwd_badge = format_strength_badge(u_res.password_result.strength_label, u_res.password_result.score)
        
        # Email status
        email_str = u_res.user.email
        if not u_res.email_result.is_valid:
            email_str = f"[red]{email_str} ✖[/red]"
        elif u_res.email_result.warnings:
            email_str = f"[yellow]{email_str} ⚠[/yellow]"
        else:
            email_str = f"[green]{email_str} ✔[/green]"

        # Detalles
        details = []
        if u_res.all_errors:
            details.append("[red]" + " | ".join(u_res.all_errors) + "[/red]")
        if u_res.custom_warnings:
            details.append("[yellow]" + " | ".join(u_res.custom_warnings) + "[/yellow]")
        if u_res.email_result.warnings:
            details.append("[yellow]" + " | ".join(u_res.email_result.warnings) + "[/yellow]")
        if not details:
            details.append("[green]Sin observaciones[/green]")

        table.add_row(
            str(idx),
            u_res.user.username or "[dim](vacío)[/dim]",
            email_str,
            pwd_badge,
            status_badge,
            "\n".join(details),
        )

    console.print(table)
    console.print()


def looks_like_email(text: str) -> bool:
    """Verifica heurísticamente si el texto parece una dirección de email."""
    return "@" in text and not text.startswith("@") and not text.endswith("@")


def interactive_cli() -> None:
    """Ejecuta el menú interactivo para validaciones."""
    console.print(
        Panel.fit(
            "[bold cyan]🛡️ Validador de Seguridad y Gestión de Usuarios[/bold cyan]\n"
            "[dim]Valida contraseñas, correos electrónicos y listas de usuarios.[/dim]",
            border_style="cyan",
        )
    )

    pwd_validator = PasswordValidator()
    email_validator = EmailValidator()

    while True:
        choice = Prompt.ask(
            "Selecciona una opción:\n"
            " [bold]1[/bold] - Validar Contraseña\n"
            " [bold]2[/bold] - Validar Correo Electrónico\n"
            " [bold]3[/bold] - Validar Lista de Usuarios de Ejemplo (Batch Demo)\n"
            " [bold]4[/bold] - Validar Lote de Usuarios desde archivo JSON\n"
            " [bold]q[/bold] - Salir\n"
            "Opción",
            choices=["1", "2", "3", "4", "q"],
            default="3",
        )

        if choice == "q":
            console.print("[dim]¡Hasta luego![/dim]")
            break

        if choice == "1":
            mode = Prompt.ask("¿Ingresar contraseña en [bold](v)[/bold]isible o [bold](o)[/bold]culta?", choices=["v", "o"], default="v")
            pwd = getpass.getpass("Ingresa la contraseña (oculta): ") if mode == "o" else Prompt.ask("Ingresa la contraseña")
            if pwd:
                display_password_result(pwd_validator.validate(pwd))

        elif choice == "2":
            email = Prompt.ask("Ingresa el correo electrónico a validar")
            if email:
                display_email_result(email_validator.validate(email))

        elif choice == "3":
            console.print("\n[bold cyan]Ejecutando validación en lote de 5 usuarios de prueba...[/bold cyan]")
            report = validate_users(SAMPLE_USERS)
            display_batch_report(report)

        elif choice == "4":
            filepath = Prompt.ask("Ruta del archivo JSON con lista de usuarios")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        report = validate_users(data)
                        display_batch_report(report)
                    else:
                        console.print("[red]El archivo JSON debe contener una lista de objetos de usuario.[/red]\n")
            except Exception as e:
                console.print(f"[red]Error al leer archivo:[/red] {e}\n")


def main() -> None:
    """Punto de entrada principal CLI."""
    if len(sys.argv) > 1:
        args = sys.argv[1:]

        # Comando explícito: users / batch
        if args[0].lower() in ["users", "batch", "--users", "-u"]:
            if len(args) > 1:
                try:
                    with open(args[1], "r", encoding="utf-8") as f:
                        data = json.load(f)
                        report = validate_users(data)
                        display_batch_report(report)
                        return
                except Exception as e:
                    console.print(f"[red]Error leyendo {args[1]}: {e}[/red]")
                    return
            else:
                # Demo batch
                report = validate_users(SAMPLE_USERS)
                display_batch_report(report)
                return

        # Comandos explícitos: email / password
        if args[0].lower() in ["--email", "-e", "email"] and len(args) > 1:
            display_email_result(validate_email(args[1]))
            return

        if args[0].lower() in ["--password", "-p", "password", "pwd"] and len(args) > 1:
            display_password_result(validate_password(args[1]))
            return

        # Auto-detección
        val = args[0]
        if looks_like_email(val):
            display_email_result(validate_email(val))
        else:
            display_password_result(validate_password(val))
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
