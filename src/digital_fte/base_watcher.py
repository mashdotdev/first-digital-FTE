"""Base watcher class for Digital FTE."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from .config import get_settings
from .logger import get_audit_logger
from .models import Priority, Task, WatcherEvent


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers.

    Watchers monitor external systems (Gmail, WhatsApp, filesystem, etc.)
    and create tasks when they detect events that need human/AI attention.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the watcher.

        Args:
            name: Unique identifier for this watcher
        """
        self.name = name
        self.settings = get_settings()
        self.audit = get_audit_logger()
        self.logger = logging.getLogger(f"digital_fte.watcher.{name}")

        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._last_check: Optional[datetime] = None
        self._error_count = 0

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the watcher (setup connections, authenticate, etc.).

        Raises:
            Exception: If initialization fails
        """
        pass

    @abstractmethod
    async def check_for_events(self) -> list[WatcherEvent]:
        """
        Check for new events that need attention.

        Returns:
            List of detected events

        Raises:
            Exception: If check fails
        """
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources (close connections, etc.)."""
        pass

    @abstractmethod
    def event_to_task(self, event: WatcherEvent) -> Optional[Task]:
        """
        Convert a watcher event into a task.

        Args:
            event: The event detected by this watcher

        Returns:
            Task object if the event requires action, None otherwise
        """
        pass

    @abstractmethod
    def calculate_priority(self, event: WatcherEvent) -> Priority:
        """
        Determine the priority of an event.

        Args:
            event: The event to prioritize

        Returns:
            Priority level (P0, P1, P2, P3)
        """
        pass

    async def start(self) -> None:
        """Start the watcher loop."""
        if self._running:
            self.logger.warning(f"Watcher {self.name} is already running")
            return

        self.logger.info(f"Starting watcher: {self.name}")
        self._running = True

        try:
            await self.initialize()
            self.audit.log_watcher_event(
                self.name,
                "started",
                {"status": "initialized successfully"},
            )

            # Create background task
            self._task = asyncio.create_task(self._run_loop())

        except Exception as e:
            self.logger.error(f"Failed to start watcher {self.name}: {e}")
            self.audit.log_error(
                component=f"watcher.{self.name}",
                error=str(e),
                details={"operation": "start"},
            )
            self._running = False
            raise

    async def stop(self) -> None:
        """Stop the watcher loop."""
        if not self._running:
            return

        self.logger.info(f"Stopping watcher: {self.name}")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        await self.cleanup()

        self.audit.log_watcher_event(
            self.name,
            "stopped",
            {"status": "stopped successfully"},
        )

    async def _run_loop(self) -> None:
        """Main watcher loop."""
        poll_interval = self._get_poll_interval()

        while self._running:
            try:
                await self._check_and_process()
                self._error_count = 0  # Reset on success

                # Wait for next interval
                await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                break

            except Exception as e:
                self._error_count += 1
                self.logger.error(
                    f"Error in watcher {self.name} (attempt {self._error_count}): {e}"
                )
                self.audit.log_error(
                    component=f"watcher.{self.name}",
                    error=str(e),
                    details={"error_count": self._error_count},
                )

                # Exponential backoff on errors
                if self._error_count >= self.settings.error_retry_attempts:
                    self.logger.critical(
                        f"Watcher {self.name} failed {self._error_count} times. Stopping."
                    )
                    await self.stop()
                    break

                await asyncio.sleep(min(60 * self._error_count, 300))  # Max 5 min

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
    )
    async def _check_and_process(self) -> None:
        """Check for events and process them (with retry logic)."""
        self.logger.debug(f"Checking for events: {self.name}")

        # Check for events
        events = await self.check_for_events()
        self._last_check = datetime.now()

        if not events:
            return

        self.logger.info(f"Watcher {self.name} found {len(events)} events")

        # Process each event
        for event in events:
            try:
                await self._process_event(event)
            except Exception as e:
                self.logger.error(f"Failed to process event {event.id}: {e}")
                self.audit.log_error(
                    component=f"watcher.{self.name}",
                    error=str(e),
                    details={"event_id": event.id, "event_type": event.event_type},
                )

    async def _process_event(self, event: WatcherEvent) -> None:
        """Process a single event."""
        # Log the event
        self.audit.log_watcher_event(
            self.name,
            event.event_type,
            {"event_id": event.id, "raw_data_keys": list(event.raw_data.keys())},
        )

        # Convert to task
        task = self.event_to_task(event)

        if task is None:
            self.logger.debug(f"Event {event.id} does not require action")
            return

        # Link event and task
        event.task_id = task.id

        # Calculate priority
        task.priority = self.calculate_priority(event)

        # Save task to Obsidian
        await self._save_task_to_vault(task)

        # Log task creation
        self.audit.log_task_created(
            task_id=task.id,
            source=self.name,
            title=task.title,
        )

        self.logger.info(
            f"Created task {task.id} from event {event.id} (priority: {task.priority})"
        )

    async def _save_task_to_vault(self, task: Task) -> None:
        """
        Save task to Obsidian vault as markdown.

        Args:
            task: Task to save
        """
        # Determine folder based on status
        if task.status == "needs_approval":
            folder = self.settings.vault_pending_approval
        elif task.status == "in_progress":
            folder = self.settings.vault_in_progress
        else:
            folder = self.settings.vault_needs_action

        # Create markdown file
        filename = f"{task.id}.md"
        filepath = folder / filename

        # Generate markdown content
        content = self._task_to_markdown(task)

        # Write file
        async with asyncio.Lock():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        self.logger.debug(f"Saved task {task.id} to {filepath}")

    def _task_to_markdown(self, task: Task) -> str:
        """Convert task to markdown format."""
        md = f"""# {task.title}

---
id: {task.id}
created: {task.created_at.isoformat()}
priority: {task.priority.value}
status: {task.status.value}
source: {task.source}
---

## Description

{task.description}

## Context

```json
{task.context}
```

## Proposed Action

{self._format_proposed_action(task)}

## History

- **Created:** {task.created_at:%Y-%m-%d %H:%M:%S}
- **Updated:** {task.updated_at:%Y-%m-%d %H:%M:%S}

---
*Generated by Digital FTE - {self.name} watcher*
"""
        return md

    def _format_proposed_action(self, task: Task) -> str:
        """Format proposed action for markdown."""
        if task.proposed_action is None:
            return "*No action proposed yet*"

        action = task.proposed_action
        return f"""
**Action Type:** {action.action_type.value}

**Reasoning:**
{action.reasoning}

**Confidence:** {action.confidence:.0%}

**Handbook References:**
{chr(10).join(f"- {ref}" for ref in action.handbook_references) if action.handbook_references else "- None"}

**Details:**
```json
{action.action_data}
```

**Requires Approval:** {'Yes' if action.requires_approval else 'No'}
"""

    def _get_poll_interval(self) -> int:
        """Get poll interval for this watcher from config."""
        # Default intervals per watcher type
        defaults = {
            "gmail": 60,
            "whatsapp": 120,
            "filesystem": 30,
        }

        return getattr(
            self.settings,
            f"{self.name}_poll_interval",
            defaults.get(self.name, 60),
        )

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._running

    def get_status(self) -> dict[str, Any]:
        """Get current status of the watcher."""
        return {
            "name": self.name,
            "running": self._running,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "error_count": self._error_count,
        }
