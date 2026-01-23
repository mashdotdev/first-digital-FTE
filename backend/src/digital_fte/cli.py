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
            "Your AI-powered business assistant",
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

        console.print("[green][OK][/green] Orchestrator initialized")

        await orchestrator.start()

        console.print("[green][OK][/green] All systems running\n")
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
    config_table.add_row("Gmail Watcher", "[X] Enabled" if settings.gmail_enabled else "[ ] Disabled")
    config_table.add_row("WhatsApp Watcher", "[X] Enabled" if settings.whatsapp_enabled else "[ ] Disabled")
    config_table.add_row("Filesystem Watcher", "[X] Enabled" if settings.filesystem_enabled else "[ ] Disabled")
    config_table.add_row("Ralph Loop", "[X] Enabled" if settings.ralph_enabled else "[ ] Disabled")
    config_table.add_row("CEO Briefing", "[X] Enabled" if settings.briefing_enabled else "[ ] Disabled")

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
        "Inbox",
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
        console.print(f"  [green][OK][/green] Created {folder}/")

    # Create template files
    console.print("\n[cyan]Creating template files...[/cyan]")

    # Company Handbook
    handbook_path = vault_path / "Company_Handbook.md"
    if not handbook_path.exists():
        handbook_path.write_text("# Company Handbook\n\nAdd your operating rules here.\n")
        console.print(f"  [green][OK][/green] Created Company_Handbook.md")

    # Business Goals
    goals_path = vault_path / "Business_Goals.md"
    if not goals_path.exists():
        goals_path.write_text("# Business Goals\n\nAdd your business objectives here.\n")
        console.print(f"  [green][OK][/green] Created Business_Goals.md")

    # Dashboard
    dashboard_path = vault_path / "Dashboard.md"
    if not dashboard_path.exists():
        dashboard_path.write_text("# AI Employee Dashboard\n\n*Status: Initializing*\n")
        console.print(f"  [green][OK][/green] Created Dashboard.md")

    # Create .env template
    console.print("\n[cyan]Creating .env template...[/cyan]")

    env_example = """# Google Gemini API
GEMINI_API_KEY=your_api_key_here

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
    console.print(f"  [green][OK][/green] Created .env.example")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("  1. Copy .env.example to .env")
    console.print("  2. Add your GEMINI_API_KEY to .env (get free key from: https://aistudio.google.com/apikey)")
    console.print("  3. Customize Company_Handbook.md and Business_Goals.md")
    console.print("  4. Run: [cyan]digital-fte start[/cyan]")


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    console.print(f"[bold]Digital FTE[/bold] version [cyan]{__version__}[/cyan]")


@app.command()
def briefing(
    days: int = typer.Option(7, help="Number of days to analyze"),
) -> None:
    """Generate a CEO briefing report."""
    setup_logging("WARNING")

    from .briefing_generator import CEOBriefingGenerator

    settings = get_settings()

    console.print(Panel.fit("[bold]Generating CEO Briefing[/bold]", border_style="cyan"))

    try:
        generator = CEOBriefingGenerator(str(settings.vault_path))
        filepath = generator.generate_briefing(period_days=days)

        console.print(f"\n[green][OK][/green] CEO briefing generated!")
        console.print(f"[cyan]Location:[/cyan] {filepath}")
        console.print(f"\n[dim]Open in Obsidian to view the full report.[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error generating briefing:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def approve(
    task_name: str = typer.Argument(..., help="Name of task to approve"),
) -> None:
    """Approve a pending task (move from Pending_Approval to Approved)."""
    setup_logging("WARNING")

    settings = get_settings()
    pending_path = settings.vault_pending_approval
    approved_path = settings.vault_approved

    # Find the task file
    task_file = None
    for f in pending_path.glob("*.md"):
        if task_name.lower() in f.stem.lower():
            task_file = f
            break

    if task_file is None:
        console.print(f"[red]Task not found:[/red] {task_name}")
        console.print(f"[dim]Check files in: {pending_path}[/dim]")
        raise typer.Exit(code=1)

    # Move to approved
    new_path = approved_path / task_file.name
    task_file.rename(new_path)

    console.print(f"[green][OK][/green] Approved: {task_file.name}")
    console.print(f"[dim]Moved to: {new_path}[/dim]")


@app.command()
def reject(
    task_name: str = typer.Argument(..., help="Name of task to reject"),
    reason: Optional[str] = typer.Option(None, help="Reason for rejection"),
) -> None:
    """Reject a pending task (move from Pending_Approval to Rejected)."""
    setup_logging("WARNING")

    settings = get_settings()
    pending_path = settings.vault_pending_approval
    rejected_path = settings.vault_rejected

    # Find the task file
    task_file = None
    for f in pending_path.glob("*.md"):
        if task_name.lower() in f.stem.lower():
            task_file = f
            break

    if task_file is None:
        console.print(f"[red]Task not found:[/red] {task_name}")
        console.print(f"[dim]Check files in: {pending_path}[/dim]")
        raise typer.Exit(code=1)

    # Add rejection reason if provided
    if reason:
        content = task_file.read_text(encoding="utf-8")
        content += f"\n\n---\n**Rejected:** {reason}\n"
        task_file.write_text(content, encoding="utf-8")

    # Move to rejected
    new_path = rejected_path / task_file.name
    task_file.rename(new_path)

    console.print(f"[yellow][REJECTED][/yellow] {task_file.name}")
    if reason:
        console.print(f"[dim]Reason: {reason}[/dim]")
    console.print(f"[dim]Moved to: {new_path}[/dim]")


if __name__ == "__main__":
    app()
