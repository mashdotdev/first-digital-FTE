"""Audit logging for Digital FTE."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .config import get_settings
from .models import AuditLog


class AuditLogger:
    """Handles audit logging to both files and system logs."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logging.getLogger("digital_fte.audit")

        # Ensure logs directory exists
        self.settings.vault_logs.mkdir(parents=True, exist_ok=True)

        self.audit_file = self.settings.vault_logs / f"audit_{datetime.now():%Y%m}.jsonl"

    def log(
        self,
        event_type: str,
        actor: str,
        details: dict[str, Any],
        task_id: Optional[str] = None,
        action_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an audit event.

        Args:
            event_type: Type of event (e.g., "task_created", "action_executed")
            actor: Who triggered this ("ai" or "human")
            details: Additional context
            task_id: Associated task ID
            action_id: Associated action ID
            success: Whether the operation succeeded
            error_message: Error message if failed

        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            event_type=event_type,
            actor=actor,
            task_id=task_id,
            action_id=action_id,
            details=details,
            success=success,
            error_message=error_message,
        )

        # Write to JSONL file
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(audit_log.model_dump_json() + "\n")

        # Also log to system logger
        log_level = logging.INFO if success else logging.ERROR
        self.logger.log(
            log_level,
            f"[{event_type}] {actor} - {details.get('summary', 'No summary')}",
        )

        return audit_log

    def log_task_created(self, task_id: str, source: str, title: str) -> None:
        """Log task creation."""
        self.log(
            event_type="task_created",
            actor="ai",
            task_id=task_id,
            details={
                "summary": f"New task from {source}: {title}",
                "source": source,
                "title": title,
            },
        )

    def log_action_proposed(
        self, action_id: str, task_id: str, action_type: str, confidence: float
    ) -> None:
        """Log action proposal."""
        self.log(
            event_type="action_proposed",
            actor="ai",
            task_id=task_id,
            action_id=action_id,
            details={
                "summary": f"Proposed {action_type} action",
                "action_type": action_type,
                "confidence": confidence,
            },
        )

    def log_human_decision(
        self, action_id: str, task_id: str, approved: bool, notes: Optional[str] = None
    ) -> None:
        """Log human approval/rejection."""
        self.log(
            event_type="human_decision",
            actor="human",
            task_id=task_id,
            action_id=action_id,
            details={
                "summary": f"Action {'approved' if approved else 'rejected'}",
                "approved": approved,
                "notes": notes,
            },
        )

    def log_action_executed(
        self,
        action_id: str,
        task_id: str,
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Log action execution."""
        self.log(
            event_type="action_executed",
            actor="ai",
            task_id=task_id,
            action_id=action_id,
            success=success,
            error_message=error_message,
            details={
                "summary": "Action executed successfully" if success else f"Action failed: {error_message}",
            },
        )

    def log_watcher_event(self, watcher_name: str, event_type: str, details: dict[str, Any]) -> None:
        """Log watcher event."""
        self.log(
            event_type=f"watcher_{event_type}",
            actor="ai",
            details={
                "summary": f"{watcher_name} detected {event_type}",
                "watcher": watcher_name,
                **details,
            },
        )

    def log_error(
        self,
        component: str,
        error: str,
        task_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an error."""
        self.log(
            event_type="error",
            actor="ai",
            task_id=task_id,
            success=False,
            error_message=error,
            details={
                "summary": f"Error in {component}: {error}",
                "component": component,
                **(details or {}),
            },
        )

    def log_health_check(self, health_status: dict[str, Any]) -> None:
        """Log system health check."""
        self.log(
            event_type="health_check",
            actor="ai",
            details={
                "summary": "System health check completed",
                **health_status,
            },
        )

    def create_human_readable_log(self, date: Optional[datetime] = None) -> Path:
        """
        Create a human-readable markdown log for a specific date.

        Args:
            date: Date to generate log for (defaults to today)

        Returns:
            Path to generated markdown file
        """
        if date is None:
            date = datetime.now()

        # Read audit logs for this date
        audit_file_pattern = f"audit_{date:%Y%m}.jsonl"
        audit_file = self.settings.vault_logs / audit_file_pattern

        if not audit_file.exists():
            # No logs for this month
            return self.settings.vault_logs / f"daily_log_{date:%Y%m%d}.md"

        # Parse logs
        daily_logs: list[AuditLog] = []
        with open(audit_file, "r", encoding="utf-8") as f:
            for line in f:
                log_entry = AuditLog.model_validate_json(line)
                if log_entry.timestamp.date() == date.date():
                    daily_logs.append(log_entry)

        # Generate markdown
        md_path = self.settings.vault_logs / f"daily_log_{date:%Y%m%d}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Daily Activity Log - {date:%Y-%m-%d}\n\n")
            f.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")

            if not daily_logs:
                f.write("*No activity recorded for this day*\n")
                return md_path

            # Group by hour
            by_hour: dict[int, list[AuditLog]] = {}
            for log in daily_logs:
                hour = log.timestamp.hour
                if hour not in by_hour:
                    by_hour[hour] = []
                by_hour[hour].append(log)

            for hour in sorted(by_hour.keys()):
                f.write(f"## {hour:02d}:00 - {hour:02d}:59\n\n")
                for log in by_hour[hour]:
                    status = "✅" if log.success else "❌"
                    f.write(f"- **{log.timestamp:%H:%M:%S}** {status} [{log.event_type}] ")
                    f.write(f"{log.details.get('summary', 'No summary')}\n")
                f.write("\n")

        return md_path


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
