"""Command-line interface for Digital FTE."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from .config import get_settings
from .orchestrator import Orchestrator

app = typer.Typer(
    name="digital-fte",
    help="Digital Full-Time Employee - AI-powered business automation",
    add_completion=False,
)

console = Console()


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with rich handler."""
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def start(
    log_level: str = typer.Option("INFO", help="Logging level"),
    daemon: bool = typer.Option(False, help="Run as background daemon"),
) -> None:
    """Start the Digital FTE orchestrator."""
    setup_logging(log_level)

    console.print(
        Panel.fit(
            "[bold cyan]Digital FTE Starting...[/bold cyan]\n"
            "🤖 Your AI-powered business assistant",
            border_style="cyan",
        )
    )

    try:
        # Create and run orchestrator
        orchestrator = Orchestrator()

        if daemon:
            console.print("[yellow]Daemon mode not yet implemented. Running in foreground.[/yellow]")

        # Run async orchestrator
        asyncio.run(run_orchestrator(orchestrator))

    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down gracefully...[/yellow]")
        sys.exit(0)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}", style="red")
        sys.exit(1)


async def run_orchestrator(orchestrator: Orchestrator) -> None:
    """Run the orchestrator."""
    try:
        await orchestrator.initialize()

        console.print("[green]✓[/green] Orchestrator initialized")

        await orchestrator.start()

        console.print("[green]✓[/green] All systems running\n")
        console.print("[dim]Press Ctrl+C to stop[/dim]\n")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping orchestrator...[/yellow]")
        await orchestrator.stop()

    except Exception as e:
        console.print(f"[bold red]Fatal error:[/bold red] {e}")
        raise


@app.command()
def status() -> None:
    """Show system status."""
    setup_logging("WARNING")

    settings = get_settings()

    console.print(Panel.fit("[bold]Digital FTE Status[/bold]", border_style="cyan"))

    # Vault status
    vault_table = Table(title="Obsidian Vault")
    vault_table.add_column("Folder", style="cyan")
    vault_table.add_column("Tasks", justify="right", style="yellow")

    folders = [
        ("Needs Action", settings.vault_needs_action),
        ("Pending Approval", settings.vault_pending_approval),
        ("Approved", settings.vault_approved),
        ("Rejected", settings.vault_rejected),
        ("In Progress", settings.vault_in_progress),
        ("Done", settings.vault_done),
    ]

    for name, path in folders:
        count = len(list(path.glob("*.md"))) if path.exists() else 0
        vault_table.add_row(name, str(count))

    console.print(vault_table)

    # Configuration
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="yellow")

    config_table.add_row("Vault Path", str(settings.vault_path))
    config_table.add_row("Gmail Watcher", "✓ Enabled" if settings.gmail_enabled else "✗ Disabled")
    config_table.add_row("WhatsApp Watcher", "✓ Enabled" if settings.whatsapp_enabled else "✗ Disabled")
    config_table.add_row("Filesystem Watcher", "✓ Enabled" if settings.filesystem_enabled else "✗ Disabled")
    config_table.add_row("Ralph Loop", "✓ Enabled" if settings.ralph_enabled else "✗ Disabled")
    config_table.add_row("CEO Briefing", "✓ Enabled" if settings.briefing_enabled else "✗ Disabled")

    console.print(config_table)


@app.command()
def init(
    vault_path: Optional[Path] = typer.Option(None, help="Path to Obsidian vault"),
) -> None:
    """Initialize a new Digital FTE installation."""
    console.print(Panel.fit("[bold]Digital FTE Setup[/bold]", border_style="cyan"))

    if vault_path is None:
        vault_path = Path("AI_Employee_Vault")

    console.print(f"[cyan]Creating vault structure at:[/cyan] {vault_path}")

    # Create vault directories
    folders = [
        "Needs_Action",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "In_Progress",
        "Done",
        "Logs",
        "Briefings",
        "Accounting",
        "People",
        "Metrics",
        "Plans",
    ]

    for folder in folders:
        folder_path = vault_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] Created {folder}/")

    # Create template files
    console.print("\n[cyan]Creating template files...[/cyan]")

    # Company Handbook
    handbook_path = vault_path / "Company_Handbook.md"
    if not handbook_path.exists():
        handbook_path.write_text("# Company Handbook\n\nAdd your operating rules here.\n")
        console.print(f"  [green]✓[/green] Created Company_Handbook.md")

    # Business Goals
    goals_path = vault_path / "Business_Goals.md"
    if not goals_path.exists():
        goals_path.write_text("# Business Goals\n\nAdd your business objectives here.\n")
        console.print(f"  [green]✓[/green] Created Business_Goals.md")

    # Dashboard
    dashboard_path = vault_path / "Dashboard.md"
    if not dashboard_path.exists():
        dashboard_path.write_text("# AI Employee Dashboard\n\n*Status: Initializing*\n")
        console.print(f"  [green]✓[/green] Created Dashboard.md")

    # Create .env template
    console.print("\n[cyan]Creating .env template...[/cyan]")

    env_example = """# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here

# Obsidian Vault
VAULT_PATH=AI_Employee_Vault

# Watchers
GMAIL_ENABLED=true
WHATSAPP_ENABLED=false
FILESYSTEM_ENABLED=true

# Google API (for Gmail)
# Download from: https://console.cloud.google.com/
GOOGLE_CREDENTIALS_PATH=credentials.json

# Ralph Wiggum Loop
RALPH_ENABLED=true
RALPH_INTERVAL_SECONDS=300

# CEO Briefing
BRIEFING_ENABLED=true
"""

    env_path = Path(".env.example")
    env_path.write_text(env_example)
    console.print(f"  [green]✓[/green] Created .env.example")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("  1. Copy .env.example to .env")
    console.print("  2. Add your ANTHROPIC_API_KEY to .env")
    console.print("  3. Customize Company_Handbook.md and Business_Goals.md")
    console.print("  4. Run: [cyan]digital-fte start[/cyan]")


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"[bold]Digital FTE[/bold] version [cyan]{__version__}[/cyan]")


if __name__ == "__main__":
    app()
