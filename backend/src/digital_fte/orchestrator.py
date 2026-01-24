"""Main orchestrator for Digital FTE - coordinates all watchers and Claude Code CLI."""

import asyncio
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .config import get_settings
from .logger import get_audit_logger
from .mcp.email_mcp import EmailMCP
from .models import Priority, ProposedAction, SystemHealth, Task, TaskStatus


class Orchestrator:
    """
    Central coordinator for the Digital FTE system.

    Responsibilities:
    - Start/stop watchers
    - Process tasks with Claude Code CLI (uses Claude Pro subscription)
    - Handle human-in-the-loop approvals
    - Execute Ralph Wiggum autonomous loop
    - Generate CEO briefings
    - Monitor system health
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.audit = get_audit_logger()
        self.logger = logging.getLogger("digital_fte.orchestrator")

        # Watcher registry
        self.watchers: dict[str, Any] = {}

        # MCP servers
        self.email_mcp = EmailMCP()

        # System state
        self._running = False
        self._ralph_task: Optional[asyncio.Task[None]] = None
        self._health_task: Optional[asyncio.Task[None]] = None

        # Load context documents
        self._company_handbook: Optional[str] = None
        self._business_goals: Optional[str] = None

    async def initialize(self) -> None:
        """Initialize the orchestrator and validate setup."""
        self.logger.info("Initializing Digital FTE Orchestrator")

        # Validate vault structure
        if not self.settings.validate_vault_structure():
            raise RuntimeError("Obsidian vault structure invalid")

        # Verify Claude Code CLI is available
        await self._verify_claude_code()

        # Load context documents
        await self._load_context_documents()

        self.logger.info("Using Claude Code CLI as the reasoning engine")

        # Register watchers
        await self._register_watchers()

        self.logger.info("Orchestrator initialized successfully")

    async def _verify_claude_code(self) -> None:
        """Verify that Claude Code CLI is installed and accessible."""
        try:
            result = subprocess.run(
                [self.settings.claude_code_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Claude Code CLI found: {version}")
            else:
                raise RuntimeError(f"Claude Code CLI error: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"Claude Code CLI not found at '{self.settings.claude_code_path}'. "
                "Please install it: npm install -g @anthropic-ai/claude-code"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code CLI timed out during version check")

    async def _load_context_documents(self) -> None:
        """Load Company Handbook and Business Goals."""
        try:
            with open(self.settings.company_handbook_path, "r", encoding="utf-8") as f:
                self._company_handbook = f.read()

            with open(self.settings.business_goals_path, "r", encoding="utf-8") as f:
                self._business_goals = f.read()

            self.logger.info("Loaded context documents (handbook, goals)")

        except Exception as e:
            self.logger.error(f"Failed to load context documents: {e}")
            raise

    async def _register_watchers(self) -> None:
        """Register all enabled watchers."""
        # Import watchers here to avoid circular imports
        from .watchers.gmail_watcher import GmailWatcher
        from .watchers.filesystem_watcher import FilesystemWatcher

        if self.settings.gmail_enabled:
            self.watchers["gmail"] = GmailWatcher()
            # Connect EmailMCP to Gmail watcher for sending
            self.email_mcp.set_gmail_watcher(self.watchers["gmail"])
            self.logger.info("Registered Gmail watcher + Email MCP")

        if self.settings.filesystem_enabled:
            self.watchers["filesystem"] = FilesystemWatcher()
            self.logger.info("Registered Filesystem watcher")

        # WhatsApp watcher will be added later
        # if self.settings.whatsapp_enabled:
        #     self.watchers["whatsapp"] = WhatsAppWatcher()

    async def start(self) -> None:
        """Start the orchestrator and all watchers."""
        if self._running:
            self.logger.warning("Orchestrator already running")
            return

        self.logger.info("Starting Digital FTE Orchestrator")
        self._running = True

        try:
            # Start all watchers
            for name, watcher in self.watchers.items():
                try:
                    await watcher.start()
                    self.logger.info(f"Started watcher: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to start watcher {name}: {e}")

            # Start Ralph Wiggum loop
            if self.settings.ralph_enabled:
                self._ralph_task = asyncio.create_task(self._ralph_loop())
                self.logger.info("Started Ralph Wiggum autonomous loop")

            # Start health monitoring
            self._health_task = asyncio.create_task(self._health_monitor_loop())
            self.logger.info("Started health monitoring")

            self.audit.log(
                event_type="orchestrator_started",
                actor="ai",
                details={"watchers": list(self.watchers.keys())},
            )

        except Exception as e:
            self.logger.error(f"Failed to start orchestrator: {e}")
            await self.stop()
            raise

    async def stop(self) -> None:
        """Stop the orchestrator and all watchers."""
        if not self._running:
            return

        self.logger.info("Stopping Digital FTE Orchestrator")
        self._running = False

        # Stop Ralph loop
        if self._ralph_task:
            self._ralph_task.cancel()

        # Stop health monitor
        if self._health_task:
            self._health_task.cancel()

        # Stop all watchers
        for name, watcher in self.watchers.items():
            try:
                await watcher.stop()
                self.logger.info(f"Stopped watcher: {name}")
            except Exception as e:
                self.logger.error(f"Error stopping watcher {name}: {e}")

        self.audit.log(
            event_type="orchestrator_stopped",
            actor="ai",
            details={},
        )

    async def _ralph_loop(self) -> None:
        """
        Ralph Wiggum autonomous loop.

        "I'm helping!" - Ralph Wiggum

        Continuously processes tasks from Needs_Action folder:
        1. Read task
        2. Load handbook + business goals
        3. Ask Claude Code for proposed action
        4. If confidence high enough and handbook allows → execute
        5. Otherwise → move to Pending_Approval
        """
        interval = self.settings.ralph_interval_seconds

        while self._running:
            try:
                await self._ralph_iteration()

                # Wait for next iteration
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break

            except Exception as e:
                self.logger.error(f"Error in Ralph loop: {e}")
                self.audit.log_error(
                    component="ralph_loop",
                    error=str(e),
                )
                await asyncio.sleep(60)  # Back off on error

    async def _ralph_iteration(self) -> None:
        """Single iteration of Ralph loop."""
        # Get tasks from Needs_Action
        tasks = await self._load_tasks_from_folder(self.settings.vault_needs_action)

        if not tasks:
            return

        self.logger.info(f"Ralph found {len(tasks)} tasks to process")

        # Process each task
        for task_path in tasks[:self.settings.max_concurrent_tasks]:
            try:
                await self._process_task(task_path)
            except Exception as e:
                self.logger.error(f"Failed to process task {task_path.name}: {e}")

    async def _load_tasks_from_folder(self, folder: Path) -> list[Path]:
        """Load all task markdown files from a folder."""
        if not folder.exists():
            return []

        return [f for f in folder.glob("*.md") if f.is_file()]

    async def _process_task(self, task_path: Path) -> None:
        """
        Process a single task with Claude Code CLI.

        Args:
            task_path: Path to task markdown file
        """
        self.logger.info(f"Processing task: {task_path.name}")

        # Read task file
        with open(task_path, "r", encoding="utf-8") as f:
            task_content = f.read()

        # Build prompt for Claude Code
        prompt = self._build_task_prompt(task_content)

        # Run Claude Code CLI
        try:
            response_text = await self._call_claude_code(prompt)

            proposed_action = await self._parse_agent_response(response_text)

            if proposed_action is None:
                self.logger.warning(f"Claude didn't propose an action for {task_path.name}")
                return

            # Decide: auto-approve or require human review?
            if await self._should_auto_approve(proposed_action):
                self.logger.info(f"Auto-approving action {proposed_action.id}")

                # Execute action
                await self._execute_action(proposed_action, task_path)

                # Move to Done
                await self._move_task(task_path, self.settings.vault_done)

            else:
                self.logger.info(f"Action {proposed_action.id} requires human approval")

                # Save proposed action to task file
                await self._update_task_with_action(task_path, proposed_action)

                # Move to Pending_Approval
                await self._move_task(task_path, self.settings.vault_pending_approval)

        except Exception as e:
            self.logger.error(f"Error processing task {task_path.name}: {e}")
            self.audit.log_error(
                component="ralph_task_processing",
                error=str(e),
                details={"task": task_path.name},
            )

    async def _call_claude_code(self, prompt: str) -> str:
        """
        Call Claude Code CLI with a prompt and return the response.

        Uses the user's Claude Pro subscription via the CLI.
        """
        # Write prompt to a temp file to avoid shell escaping issues
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(prompt)
            prompt_file = f.name

        try:
            # Build Claude Code command
            cmd = [
                self.settings.claude_code_path,
                "--print",  # Print response and exit (non-interactive)
                "--model", self.settings.claude_code_model,
            ]

            # Run Claude Code with the prompt via stdin
            # Use cwd parameter to set working directory to the vault
            vault_path = str(self.settings.vault_path.resolve())
            self.logger.debug(f"Running Claude Code in {vault_path}: {' '.join(cmd)}")

            # Use asyncio to run subprocess without blocking
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=vault_path,  # Set working directory to vault
            )

            # Send prompt and get response
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=prompt.encode('utf-8')),
                timeout=self.settings.claude_code_timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise RuntimeError(f"Claude Code failed: {error_msg}")

            response = stdout.decode('utf-8').strip()
            self.logger.debug(f"Claude Code response length: {len(response)} chars")

            return response

        except asyncio.TimeoutError:
            raise RuntimeError(
                f"Claude Code timed out after {self.settings.claude_code_timeout}s"
            )
        finally:
            # Clean up temp file
            Path(prompt_file).unlink(missing_ok=True)

    def _build_system_prompt(self) -> str:
        """Build system prompt (instructions) for the AI agent."""
        return f"""You are a Digital Full-Time Employee (FTE) - an AI assistant that helps with business operations.

# Your Operating Context

## Company Handbook (Your Rules)
{self._company_handbook}

## Business Goals (Your Mission)
{self._business_goals}

# Your Job

You receive tasks detected by watchers (email, messages, file changes). For each task:

1. **Understand the context** - What happened? What needs to be done?
2. **Check the handbook** - What are the rules? Is this allowed?
3. **Check business goals** - Does this align with objectives?
4. **Propose an action** - What should we do?
5. **Rate your confidence** - How sure are you? (0.0 - 1.0)

# Response Format

Respond with a JSON object:

```json
{{
  "action_type": "<one of the valid types below>",
  "title": "Brief title of proposed action",
  "reasoning": "Explain WHY this action based on handbook/goals",
  "action_data": {{
    // Specific details needed to execute the action
  }},
  "confidence": 0.85,
  "handbook_references": ["Section 2.1: Email Protocol"],
  "requires_approval": true
}}
```

## VALID ACTION TYPES (you MUST use exactly one of these):

### email_reply - Reply to an email
action_data must contain:
- "body": "The reply message text"
- "to": (optional) recipient email, defaults to sender

### email_send - Send a new email
action_data must contain:
- "to": "recipient@email.com"
- "subject": "Email subject"
- "body": "Email body text"

### whatsapp_reply - Reply to a WhatsApp message
action_data must contain:
- "body": "The reply message"

### file_operation - Create, update, or move files
action_data must contain:
- "operation": "create" | "update" | "move"
- "path": "file path"
- "content": "file content" (for create/update)

### calendar_event - Schedule calendar events
action_data must contain:
- "title": "Event title"
- "datetime": "ISO datetime"

### payment - Process payments (always requires approval)
action_data must contain:
- "amount": dollar amount
- "recipient": "who to pay"

### social_post - Post to social media
action_data must contain:
- "platform": "linkedin" | "twitter" | "facebook"
- "content": "post content"

### custom - Any other action

# Decision Rules

**Auto-approve (requires_approval: false) when:**
- Handbook explicitly allows this type of action
- Your confidence is >= 0.85
- No financial impact
- Low risk

**Require approval (requires_approval: true) when:**
- Handbook is unclear
- Confidence < 0.85
- Financial decision
- First time seeing this scenario
- Anything that could hurt the business

**When in doubt, ask for approval.** The human wants you to be helpful but safe.
"""

    def _build_task_prompt(self, task_content: str) -> str:
        """Build complete prompt for Claude Code to analyze a task."""
        system_context = self._build_system_prompt()

        return f"""{system_context}

---

# CURRENT TASK

{task_content}

---

Based on the Company Handbook and Business Goals above, propose an action to handle this task.

Respond ONLY with the JSON object as specified. No other text.
"""

    async def _parse_agent_response(self, response: str) -> Optional[ProposedAction]:
        """Parse agent's JSON response into ProposedAction."""
        try:
            # Extract JSON from response (in case agent added extra text)
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                return None

            json_str = response[start:end]
            data = json.loads(json_str)

            return ProposedAction(
                action_type=data["action_type"],
                title=data["title"],
                reasoning=data["reasoning"],
                action_data=data.get("action_data", {}),
                confidence=data["confidence"],
                handbook_references=data.get("handbook_references", []),
                requires_approval=data.get("requires_approval", True),
            )

        except Exception as e:
            self.logger.error(f"Failed to parse agent response: {e}")
            self.logger.debug(f"Response was: {response}")
            return None

    async def _should_auto_approve(self, action: ProposedAction) -> bool:
        """Determine if an action can be auto-approved."""
        # Never auto-approve if explicitly requires approval
        if action.requires_approval:
            return False

        # Check confidence threshold
        if action.confidence < self.settings.hitl_confidence_threshold:
            return False

        # Never auto-approve certain action types
        never_auto = ["payment", "social_post"]
        if action.action_type in never_auto:
            return False

        return True

    async def _execute_action(self, action: ProposedAction, task_path: Path) -> None:
        """Execute an approved action via appropriate MCP server."""
        action_type = action.action_type
        if hasattr(action_type, 'value'):
            action_type = action_type.value

        self.logger.info(f"Executing action: {action_type}")

        success = False

        try:
            # Read task file to get context
            with open(task_path, "r", encoding="utf-8") as f:
                task_content = f.read()

            # Extract context from task (email metadata, etc.)
            task_context = self._extract_task_context(task_content)

            # Route to appropriate MCP server
            if action_type in ["email_reply", "email_send"]:
                success = await self.email_mcp.execute_action(action, task_context)

            elif action_type == "social_post":
                # TODO: Implement social media MCP
                self.logger.warning(f"Social post MCP not yet implemented")
                success = False

            elif action_type == "file_operation":
                # File operations are handled directly
                self.logger.info("File operation - no external action needed")
                success = True

            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                success = False

        except Exception as e:
            self.logger.error(f"Failed to execute action: {e}")
            success = False

        self.audit.log_action_executed(
            action_id=action.id,
            task_id=task_path.stem,
            success=success,
        )

        if not success:
            raise RuntimeError(f"Failed to execute action: {action_type}")

    def _extract_task_context(self, task_content: str) -> dict:
        """Extract context/metadata from task markdown file."""
        import ast
        import re

        context = {}

        # Try to extract from the JSON/dict context block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", task_content, re.DOTALL)
        if json_match:
            raw_context = json_match.group(1).strip()
            try:
                # Try JSON first (new format)
                context = json.loads(raw_context)
            except json.JSONDecodeError:
                try:
                    # Fall back to Python literal (old format with single quotes)
                    context = ast.literal_eval(raw_context)
                except (ValueError, SyntaxError):
                    pass

        # Also extract from markdown patterns as backup
        patterns = {
            "subject": r"\*\*Subject:\*\*\s*(.+)",
            "from": r"New email received from\s+(.+)",
        }

        for key, pattern in patterns.items():
            if key not in context:
                match = re.search(pattern, task_content)
                if match:
                    context[key] = match.group(1).strip()

        return context

    async def _update_task_with_action(self, task_path: Path, action: ProposedAction) -> None:
        """Update task file with proposed action."""
        # Read current content
        with open(task_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Append proposed action
        action_md = f"""
---

## Proposed Action (Requires Approval)

**Action ID:** {action.id}
**Type:** {action.action_type}
**Confidence:** {action.confidence:.0%}

### Reasoning
{action.reasoning}

### Proposed Details
```json
{json.dumps(action.action_data, indent=2)}
```

### Handbook References
{chr(10).join(f"- {ref}" for ref in action.handbook_references)}

---

**To approve:** Move this file to `/Approved`
**To reject:** Move this file to `/Rejected`
"""

        # Write updated content
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(content + action_md)

    async def _move_task(self, task_path: Path, destination: Path) -> None:
        """Move task file to another folder."""
        new_path = destination / task_path.name
        task_path.rename(new_path)
        self.logger.debug(f"Moved {task_path.name} to {destination.name}/")

    async def _health_monitor_loop(self) -> None:
        """Monitor system health and log status."""
        interval = self.settings.health_check_interval

        while self._running:
            try:
                health = await self._check_health()

                self.audit.log_health_check(health.model_dump())

                # Update dashboard
                await self._update_dashboard(health)

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break

            except Exception as e:
                self.logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(60)

    async def _check_health(self) -> SystemHealth:
        """Check system health."""
        # Check watchers
        watchers_status = {
            name: watcher.is_running()
            for name, watcher in self.watchers.items()
        }

        # Count tasks in each folder
        tasks_pending = len(list(self.settings.vault_needs_action.glob("*.md")))
        tasks_approval = len(list(self.settings.vault_pending_approval.glob("*.md")))
        tasks_failed = 0  # TODO: Track failed tasks

        return SystemHealth(
            watchers_running=watchers_status,
            mcp_servers_healthy={},  # TODO: Check MCP servers
            tasks_pending=tasks_pending,
            tasks_needs_approval=tasks_approval,
            tasks_failed=tasks_failed,
            vault_path_accessible=self.settings.vault_path.exists(),
        )

    async def _update_dashboard(self, health: SystemHealth) -> None:
        """Update Obsidian dashboard with current status."""
        dashboard_path = self.settings.vault_path / "Dashboard.md"

        # Build status indicators
        watcher_status = "\n".join([
            f"| {name} | {'🟢 Running' if status else '🔴 Stopped'} | {datetime.now():%Y-%m-%d %H:%M} |"
            for name, status in health.watchers_running.items()
        ])

        content = f"""# AI Employee Dashboard

---
last_updated: {datetime.now().isoformat()}
status: {"operational" if all(health.watchers_running.values()) else "degraded"}
---

## System Status

| Component | Status | Last Check |
|-----------|--------|------------|
{watcher_status}

## Pending Work

- **Needs Action:** {health.tasks_pending} tasks
- **Awaiting Approval:** {health.tasks_needs_approval} tasks
- **Failed:** {health.tasks_failed} tasks

## Quick Links

- [[Company_Handbook]] - Operating rules
- [[Business_Goals]] - Business objectives
- [[Needs_Action/]] - Tasks to process
- [[Pending_Approval/]] - Awaiting your review

---
*Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}*
"""

        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(content)
