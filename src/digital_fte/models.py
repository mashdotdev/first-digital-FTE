"""Core data models for Digital FTE."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Task priority levels."""
    P0 = "P0"  # Urgent - immediate action
    P1 = "P1"  # High - within 4 hours
    P2 = "P2"  # Normal - within 24 hours
    P3 = "P3"  # Low - when capacity available


class TaskStatus(str, Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    NEEDS_APPROVAL = "needs_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class ActionType(str, Enum):
    """Types of actions the AI can take."""
    EMAIL_REPLY = "email_reply"
    EMAIL_SEND = "email_send"
    WHATSAPP_REPLY = "whatsapp_reply"
    FILE_OPERATION = "file_operation"
    CALENDAR_EVENT = "calendar_event"
    PAYMENT = "payment"
    SOCIAL_POST = "social_post"
    CUSTOM = "custom"


class Task(BaseModel):
    """Represents a task detected by watchers."""

    id: str = Field(default_factory=lambda: f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    source: str  # Which watcher detected this (e.g., "gmail", "whatsapp")
    priority: Priority = Priority.P2
    status: TaskStatus = TaskStatus.PENDING

    title: str
    description: str
    context: dict[str, Any] = Field(default_factory=dict)  # Raw data from watcher

    proposed_action: Optional["ProposedAction"] = None
    human_decision: Optional[str] = None
    human_decision_at: Optional[datetime] = None

    error_count: int = 0
    last_error: Optional[str] = None

    completed_at: Optional[datetime] = None


class ProposedAction(BaseModel):
    """An action proposed by the AI for human approval."""

    id: str = Field(default_factory=lambda: f"action_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = Field(default_factory=datetime.now)

    action_type: ActionType
    requires_approval: bool = True

    title: str
    reasoning: str  # Why is the AI proposing this action?

    # The actual action details
    action_data: dict[str, Any]

    # AI confidence (0.0 - 1.0)
    confidence: float = Field(ge=0.0, le=1.0)

    # References to handbook rules that justify this action
    handbook_references: list[str] = Field(default_factory=list)

    approved: Optional[bool] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None


class WatcherEvent(BaseModel):
    """Event detected by a watcher."""

    id: str = Field(default_factory=lambda: f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    timestamp: datetime = Field(default_factory=datetime.now)

    watcher_name: str
    event_type: str  # e.g., "new_email", "file_created", "message_received"

    raw_data: dict[str, Any]

    # Did this event generate a task?
    task_id: Optional[str] = None


class AuditLog(BaseModel):
    """Audit trail for all AI actions."""

    id: str = Field(default_factory=lambda: f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    timestamp: datetime = Field(default_factory=datetime.now)

    event_type: str  # e.g., "task_created", "action_proposed", "action_executed"
    actor: str  # "ai" or "human"

    task_id: Optional[str] = None
    action_id: Optional[str] = None

    details: dict[str, Any]

    success: bool = True
    error_message: Optional[str] = None


class WatcherConfig(BaseModel):
    """Configuration for a watcher."""

    name: str
    enabled: bool = True
    poll_interval_seconds: int = 60

    config: dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Health status of the Digital FTE system."""

    timestamp: datetime = Field(default_factory=datetime.now)

    watchers_running: dict[str, bool]
    mcp_servers_healthy: dict[str, bool]

    tasks_pending: int
    tasks_needs_approval: int
    tasks_failed: int

    last_successful_run: Optional[datetime] = None
    errors_last_hour: int = 0

    vault_path_accessible: bool
    disk_space_mb: Optional[float] = None
