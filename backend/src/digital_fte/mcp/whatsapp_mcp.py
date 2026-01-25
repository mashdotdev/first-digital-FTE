"""WhatsApp MCP server for sending messages via WhatsApp Web automation."""

import logging
from typing import Any, Optional

from ..config import get_settings
from ..models import ProposedAction

logger = logging.getLogger(__name__)


class WhatsAppMCP:
    """MCP server for WhatsApp operations using Playwright automation."""

    def __init__(self, whatsapp_watcher: Optional[Any] = None):
        """
        Initialize WhatsApp MCP.

        Args:
            whatsapp_watcher: WhatsAppWatcher instance for sending messages
        """
        self.settings = get_settings()
        self.logger = logger
        self._whatsapp_watcher = whatsapp_watcher

    def set_whatsapp_watcher(self, whatsapp_watcher: Any) -> None:
        """Set the WhatsApp watcher instance."""
        self._whatsapp_watcher = whatsapp_watcher
        self.logger.info("WhatsApp MCP connected to WhatsApp watcher")

    async def initialize(self) -> None:
        """Initialize the WhatsApp MCP server."""
        self.logger.info("WhatsApp MCP initialized")

    async def send_message(
        self,
        contact_name: str,
        message: str,
    ) -> bool:
        """
        Send a WhatsApp message via the watcher.

        Args:
            contact_name: Name of the contact to message
            message: Message text to send

        Returns:
            True if successful, False otherwise

        Raises:
            RuntimeError: If WhatsApp watcher not connected
        """
        if not self._whatsapp_watcher:
            raise RuntimeError(
                "WhatsApp watcher not connected to WhatsApp MCP. "
                "Call set_whatsapp_watcher() first."
            )

        self.logger.info(f"Sending WhatsApp message to {contact_name}")

        # Use WhatsApp watcher's send_message method
        result = await self._whatsapp_watcher.send_message(
            contact_name=contact_name,
            message=message,
        )

        if result:
            self.logger.info(f"WhatsApp message sent successfully to {contact_name}")
        else:
            self.logger.error(f"Failed to send WhatsApp message to {contact_name}")

        return result

    async def reply_to_message(
        self,
        contact_name: str,
        message: str,
    ) -> bool:
        """
        Reply to a WhatsApp message.

        This is essentially the same as send_message since WhatsApp
        doesn't have explicit reply-to-thread like email.

        Args:
            contact_name: Name of the contact to reply to
            message: Reply message text

        Returns:
            True if successful, False otherwise
        """
        if not self._whatsapp_watcher:
            raise RuntimeError("WhatsApp watcher not connected to WhatsApp MCP.")

        self.logger.info(f"Replying to WhatsApp message from {contact_name}")

        # Open the chat first to ensure we're replying in context
        chat_opened = await self._whatsapp_watcher.open_chat(contact_name)
        if not chat_opened:
            self.logger.warning(f"Could not open chat for {contact_name}, trying direct send")

        # Send the reply
        result = await self._whatsapp_watcher.send_message(
            contact_name=contact_name,
            message=message,
        )

        return result

    async def execute_action(self, action: ProposedAction, task_context: dict) -> bool:
        """
        Execute a WhatsApp action.

        Args:
            action: The proposed action to execute
            task_context: Original task context (contains message metadata)

        Returns:
            True if successful, False otherwise
        """
        action_type = action.action_type
        if hasattr(action_type, 'value'):
            action_type = action_type.value

        if action_type != "whatsapp_reply":
            self.logger.error(f"Invalid action type for WhatsAppMCP: {action_type}")
            return False

        try:
            action_data = action.action_data

            # Get contact name from task context or action data
            contact_name = action_data.get("to") or task_context.get("contact_name", "")
            message = action_data.get("body", "")

            if not contact_name or not message:
                self.logger.error("Missing required fields: contact_name or body")
                return False

            # Send the reply
            result = await self.reply_to_message(
                contact_name=contact_name,
                message=message,
            )

            if result:
                self.logger.info(f"Successfully executed whatsapp_reply to {contact_name}")
            else:
                self.logger.error(f"Failed to execute whatsapp_reply to {contact_name}")

            return result

        except Exception as e:
            self.logger.error(f"Failed to execute WhatsApp action: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if the WhatsApp MCP is healthy.

        Returns:
            True if healthy and logged in, False otherwise
        """
        if not self._whatsapp_watcher:
            return False

        return self._whatsapp_watcher.is_logged_in()

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("WhatsApp MCP cleaned up")
