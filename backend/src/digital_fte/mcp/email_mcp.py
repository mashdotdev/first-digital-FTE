"""Email MCP server for sending emails via Gmail API."""

import logging
from typing import Any, Optional

from ..config import get_settings
from ..models import ProposedAction

logger = logging.getLogger(__name__)


class EmailMCP:
    """MCP server for email operations using Gmail API."""

    def __init__(self, gmail_watcher: Optional[Any] = None):
        """
        Initialize email MCP.

        Args:
            gmail_watcher: GmailWatcher instance for sending emails
        """
        self.settings = get_settings()
        self.logger = logger
        self._gmail_watcher = gmail_watcher

    def set_gmail_watcher(self, gmail_watcher: Any) -> None:
        """Set the Gmail watcher instance."""
        self._gmail_watcher = gmail_watcher
        self.logger.info("Email MCP connected to Gmail watcher")

    async def initialize(self) -> None:
        """Initialize the email MCP server."""
        self.logger.info("Email MCP initialized")

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send an email via Gmail API.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            thread_id: Optional thread ID for replies

        Returns:
            Sent message metadata

        Raises:
            RuntimeError: If Gmail watcher not connected
        """
        if not self._gmail_watcher:
            raise RuntimeError(
                "Gmail watcher not connected to Email MCP. "
                "Call set_gmail_watcher() first."
            )

        self.logger.info(f"Sending email to {to}: {subject}")

        # Use Gmail watcher's send_email method
        result = await self._gmail_watcher.send_email(
            to=to,
            subject=subject,
            body=body,
            thread_id=thread_id,
        )

        self.logger.info(f"Email sent successfully to {to}")
        return result

    async def reply_to_email(
        self,
        original_message_id: str,
        thread_id: str,
        to: str,
        subject: str,
        body: str,
    ) -> dict[str, Any]:
        """
        Reply to an existing email thread.

        Args:
            original_message_id: The message ID being replied to
            thread_id: The thread ID to reply in
            to: Recipient email address
            subject: Email subject (usually "Re: original subject")
            body: Reply body

        Returns:
            Sent message metadata
        """
        if not self._gmail_watcher:
            raise RuntimeError("Gmail watcher not connected to Email MCP.")

        self.logger.info(f"Replying to thread {thread_id}")

        # Send reply in the same thread
        result = await self._gmail_watcher.send_email(
            to=to,
            subject=subject,
            body=body,
            thread_id=thread_id,
        )

        # Mark original as read
        try:
            await self._gmail_watcher.mark_as_read(original_message_id)
        except Exception as e:
            self.logger.warning(f"Failed to mark message as read: {e}")

        return result

    async def execute_action(self, action: ProposedAction, task_context: dict) -> bool:
        """
        Execute an email action.

        Args:
            action: The proposed action to execute
            task_context: Original task context (contains email metadata)

        Returns:
            True if successful, False otherwise
        """
        action_type = action.action_type
        if hasattr(action_type, 'value'):
            action_type = action_type.value

        if action_type not in ["email_reply", "email_send"]:
            self.logger.error(f"Invalid action type for EmailMCP: {action_type}")
            return False

        try:
            action_data = action.action_data

            if action_type == "email_reply":
                # Extract reply details
                to = action_data.get("to") or task_context.get("from", "")

                # Clean up the "to" address (sometimes has name <email> format)
                if "<" in to and ">" in to:
                    # Extract just the email from "Name <email@example.com>"
                    to = to.split("<")[1].split(">")[0]

                original_subject = task_context.get("subject", "")
                subject = action_data.get("subject") or f"Re: {original_subject}"
                body = action_data.get("body", "")
                thread_id = task_context.get("thread_id")
                message_id = task_context.get("message_id")

                if not to or not body:
                    self.logger.error("Missing required fields: to or body")
                    return False

                await self.reply_to_email(
                    original_message_id=message_id,
                    thread_id=thread_id,
                    to=to,
                    subject=subject,
                    body=body,
                )

            elif action_type == "email_send":
                # New email (not a reply)
                to = action_data.get("to", "")
                subject = action_data.get("subject", "")
                body = action_data.get("body", "")

                if not to or not subject or not body:
                    self.logger.error("Missing required fields: to, subject, or body")
                    return False

                await self.send_email(
                    to=to,
                    subject=subject,
                    body=body,
                )

            self.logger.info(f"Successfully executed {action_type}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute email action: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if the email MCP is healthy.

        Returns:
            True if healthy, False otherwise
        """
        return self._gmail_watcher is not None

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Email MCP cleaned up")
