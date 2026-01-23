"""Filesystem watcher for Obsidian vault changes."""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from ..base_watcher import BaseWatcher
from ..models import Priority, Task, TaskStatus, WatcherEvent


class VaultEventHandler(FileSystemEventHandler):
    """Handle filesystem events in Obsidian vault."""

    def __init__(self, event_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self.event_queue = event_queue
        self.loop = loop

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation."""
        if not event.is_directory and event.src_path.endswith(".md"):
            # Put event in queue for async processing
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("created", event.src_path)),
                self.loop
            )

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification."""
        if not event.is_directory and event.src_path.endswith(".md"):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("modified", event.src_path)),
                self.loop
            )

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file moves."""
        if not event.is_directory and hasattr(event, "dest_path"):
            asyncio.run_coroutine_threadsafe(
                self.event_queue.put(("moved", event.src_path, event.dest_path)),
                self.loop
            )


class FilesystemWatcher(BaseWatcher):
    """
    Watches Obsidian vault filesystem for changes.

    Key responsibilities:
    - Detect when human moves files to /Approved or /Rejected
    - Detect when user creates new task files manually
    - Monitor for manual edits to existing tasks
    """

    def __init__(self) -> None:
        super().__init__(name="filesystem")
        self.observer: Optional[Observer] = None
        self.event_queue: asyncio.Queue = asyncio.Queue()

    async def initialize(self) -> None:
        """Initialize filesystem watcher."""
        self.logger.info("Initializing Filesystem watcher")

        # Create watchdog observer
        self.observer = Observer()

        # Get the current event loop
        loop = asyncio.get_running_loop()

        # Create event handler
        handler = VaultEventHandler(self.event_queue, loop)

        # Watch the entire vault
        self.observer.schedule(
            handler,
            str(self.settings.vault_path),
            recursive=True
        )

        # Start observer
        self.observer.start()

        self.logger.info(f"Filesystem watcher monitoring: {self.settings.vault_path}")

    async def check_for_events(self) -> list[WatcherEvent]:
        """Check for filesystem events."""
        events: list[WatcherEvent] = []

        # Process all queued events (non-blocking)
        while not self.event_queue.empty():
            try:
                event_data = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=0.1
                )

                event = self._create_watcher_event(event_data)
                if event:
                    events.append(event)

            except asyncio.TimeoutError:
                break

        return events

    def _create_watcher_event(self, event_data: tuple) -> Optional[WatcherEvent]:
        """Create WatcherEvent from filesystem event data."""
        event_type = event_data[0]

        if event_type == "created":
            path = Path(event_data[1])
            return WatcherEvent(
                watcher_name=self.name,
                event_type="file_created",
                raw_data={
                    "path": str(path),
                    "filename": path.name,
                    "folder": path.parent.name,
                },
            )

        elif event_type == "modified":
            path = Path(event_data[1])
            return WatcherEvent(
                watcher_name=self.name,
                event_type="file_modified",
                raw_data={
                    "path": str(path),
                    "filename": path.name,
                    "folder": path.parent.name,
                },
            )

        elif event_type == "moved":
            src_path = Path(event_data[1])
            dest_path = Path(event_data[2])

            return WatcherEvent(
                watcher_name=self.name,
                event_type="file_moved",
                raw_data={
                    "src_path": str(src_path),
                    "dest_path": str(dest_path),
                    "filename": dest_path.name,
                    "src_folder": src_path.parent.name,
                    "dest_folder": dest_path.parent.name,
                },
            )

        return None

    async def cleanup(self) -> None:
        """Cleanup filesystem watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        self.logger.info("Filesystem watcher cleaned up")

    def event_to_task(self, event: WatcherEvent) -> Optional[Task]:
        """Convert filesystem event to task."""
        # Only create tasks for specific scenarios
        event_type = event.event_type
        data = event.raw_data

        # Human moved file to Approved folder
        if event_type == "file_moved" and data.get("dest_folder") == "Approved":
            return Task(
                source=self.name,
                title=f"Execute approved action: {data['filename']}",
                description=f"Human approved the action in {data['filename']}. Execute it.",
                context=data,
                status=TaskStatus.APPROVED,
            )

        # Human moved file to Rejected folder
        elif event_type == "file_moved" and data.get("dest_folder") == "Rejected":
            return Task(
                source=self.name,
                title=f"Learn from rejection: {data['filename']}",
                description=f"Human rejected the action in {data['filename']}. Log to Lessons_Learned.md",
                context=data,
                status=TaskStatus.REJECTED,
            )

        # Human created new task manually in Inbox (NOT Needs_Action to avoid cascade)
        # Note: We don't create tasks for files in Needs_Action because other watchers
        # already create tasks there, and this would cause infinite task creation loops.
        elif event_type == "file_created" and data.get("folder") == "Inbox":
            # Try to extract a meaningful title from the file
            file_path = Path(data.get("path", ""))
            title = self._extract_title_from_file(file_path)

            return Task(
                source=self.name,
                title=title,
                description=f"New task from Inbox: {data['filename']}",
                context=data,
                status=TaskStatus.PENDING,
            )

        # Don't create tasks for other events
        return None

    def _extract_title_from_file(self, file_path: Path) -> str:
        """Extract a meaningful title from a file's content."""
        try:
            if not file_path.exists():
                return f"New task: {file_path.stem}"

            content = file_path.read_text(encoding="utf-8")

            # Try to get title from first markdown heading
            import re
            heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1).strip()
                # Clean up common prefixes
                title = re.sub(r'^(Task:|TODO:|Note:)\s*', '', title, flags=re.IGNORECASE)
                if title:
                    return title[:100]  # Limit length

            # Try first non-empty line
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('---')]
            if lines:
                first_line = lines[0].lstrip('#').strip()
                if first_line:
                    return first_line[:100]

            # Fallback to filename (cleaned up)
            name = file_path.stem
            # Convert task_20260123_123456 to more readable format
            if name.startswith('task_'):
                return f"Manual task ({name[-6:]})"

            return f"New task: {name}"

        except Exception:
            return f"New task: {file_path.stem}"

    def calculate_priority(self, event: WatcherEvent) -> Priority:
        """Calculate priority for filesystem events."""
        data = event.raw_data

        # Approved actions are high priority (execute ASAP)
        if data.get("dest_folder") == "Approved":
            return Priority.P0

        # Rejected actions should be logged quickly
        if data.get("dest_folder") == "Rejected":
            return Priority.P1

        # Manual tasks default to P2
        return Priority.P2
