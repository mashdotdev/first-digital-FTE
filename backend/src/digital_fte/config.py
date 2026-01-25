"""Configuration management for Digital FTE."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Claude Code CLI Configuration
    claude_code_path: str = Field(
        default="claude",
        description="Path to Claude Code CLI executable"
    )
    claude_code_timeout: int = Field(
        default=300,
        description="Timeout for Claude Code CLI calls (seconds)"
    )
    claude_code_model: str = Field(
        default="sonnet",
        description="Claude model to use (sonnet, opus, haiku)"
    )

    # Obsidian Vault
    vault_path: Path = Field(
        default=Path("AI_Employee_Valut"),
        description="Path to Obsidian vault"
    )

    # Watcher Configuration
    gmail_enabled: bool = Field(default=True, description="Enable Gmail watcher")
    gmail_poll_interval: int = Field(default=60, description="Gmail check interval (seconds)")

    whatsapp_enabled: bool = Field(default=False, description="Enable WhatsApp watcher")
    whatsapp_poll_interval: int = Field(default=120, description="WhatsApp check interval")
    whatsapp_user_data_dir: Path = Field(
        default=Path(".whatsapp_session"),
        description="Playwright user data directory for WhatsApp session persistence"
    )

    filesystem_enabled: bool = Field(default=True, description="Enable filesystem watcher")

    # MCP Servers
    mcp_email_enabled: bool = Field(default=True, description="Enable email MCP")
    mcp_browser_enabled: bool = Field(default=False, description="Enable browser MCP")

    # Human-in-the-Loop
    hitl_auto_approve_known_contacts: bool = Field(
        default=False,
        description="Auto-approve emails to known contacts"
    )
    hitl_confidence_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for auto-approval"
    )

    # Ralph Wiggum Loop
    ralph_enabled: bool = Field(default=True, description="Enable autonomous task completion")
    ralph_max_iterations: int = Field(default=5, description="Max iterations per task")
    ralph_interval_seconds: int = Field(default=300, description="Check interval (seconds)")

    # CEO Briefing
    briefing_enabled: bool = Field(default=True, description="Enable Monday morning briefing")
    briefing_day: int = Field(default=0, ge=0, le=6, description="Day of week (0=Monday)")
    briefing_time: str = Field(default="06:00", description="Time to generate briefing")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    audit_log_retention_days: int = Field(default=90, description="Audit log retention")

    # System
    max_concurrent_tasks: int = Field(default=3, description="Max concurrent tasks")
    error_retry_attempts: int = Field(default=3, description="Retry attempts on error")
    error_retry_delay_seconds: int = Field(default=60, description="Delay between retries")

    health_check_interval: int = Field(default=300, description="Health check interval (seconds)")

    # Google API (Gmail)
    google_credentials_path: Optional[Path] = Field(
        default=None,
        description="Path to Google OAuth credentials"
    )
    google_token_path: Optional[Path] = Field(
        default=Path(".google_token.json"),
        description="Path to store Google OAuth token"
    )

    @property
    def vault_needs_action(self) -> Path:
        """Path to Needs_Action folder."""
        return self.vault_path / "Needs_Action"

    @property
    def vault_pending_approval(self) -> Path:
        """Path to Pending_Approval folder."""
        return self.vault_path / "Pending_Approval"

    @property
    def vault_approved(self) -> Path:
        """Path to Approved folder."""
        return self.vault_path / "Approved"

    @property
    def vault_rejected(self) -> Path:
        """Path to Rejected folder."""
        return self.vault_path / "Rejected"

    @property
    def vault_in_progress(self) -> Path:
        """Path to In_Progress folder."""
        return self.vault_path / "In_Progress"

    @property
    def vault_done(self) -> Path:
        """Path to Done folder."""
        return self.vault_path / "Done"

    @property
    def vault_logs(self) -> Path:
        """Path to Logs folder."""
        return self.vault_path / "Logs"

    @property
    def vault_briefings(self) -> Path:
        """Path to Briefings folder."""
        return self.vault_path / "Briefings"

    @property
    def company_handbook_path(self) -> Path:
        """Path to Company Handbook."""
        return self.vault_path / "Company_Handbook.md"

    @property
    def business_goals_path(self) -> Path:
        """Path to Business Goals."""
        return self.vault_path / "Business_Goals.md"

    def validate_vault_structure(self) -> bool:
        """Verify that vault directory structure exists."""
        required_folders = [
            self.vault_needs_action,
            self.vault_pending_approval,
            self.vault_approved,
            self.vault_rejected,
            self.vault_in_progress,
            self.vault_done,
            self.vault_logs,
            self.vault_briefings,
        ]

        for folder in required_folders:
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)

        return all(folder.exists() for folder in required_folders)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
