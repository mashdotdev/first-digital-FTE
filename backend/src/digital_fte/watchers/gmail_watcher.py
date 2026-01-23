"""Gmail watcher using Google API."""

import base64
import os
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ..base_watcher import BaseWatcher
from ..models import Priority, Task, TaskStatus, WatcherEvent

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for new messages."""

    def __init__(self) -> None:
        super().__init__(name="gmail")
        self.service: Optional[Any] = None
        self.last_checked_time: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize Gmail API connection."""
        self.logger.info("Initializing Gmail watcher")

        creds = None

        # Token file to store the user's access and refresh tokens
        token_path = self.settings.google_token_path

        if token_path and token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired Google credentials")
                creds.refresh(Request())
            else:
                if not self.settings.google_credentials_path:
                    raise RuntimeError(
                        "Gmail watcher enabled but google_credentials_path not set. "
                        "Please download OAuth credentials from Google Cloud Console."
                    )

                if not self.settings.google_credentials_path.exists():
                    raise FileNotFoundError(
                        f"Google credentials file not found: {self.settings.google_credentials_path}"
                    )

                self.logger.info("Starting OAuth flow for Gmail access")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.settings.google_credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            if token_path:
                with open(token_path, "wb") as token:
                    pickle.dump(creds, token)
                self.logger.info(f"Saved Google credentials to {token_path}")

        # Build Gmail service
        self.service = build("gmail", "v1", credentials=creds)

        self.logger.info("Gmail watcher initialized successfully")

    async def check_for_events(self) -> list[WatcherEvent]:
        """Check for new emails."""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        events: list[WatcherEvent] = []

        try:
            # Build query for unread messages
            # If this is first check, only get messages from last hour
            if self.last_checked_time is None:
                self.last_checked_time = datetime.now() - timedelta(hours=1)

            query = "is:unread"

            # Get messages
            results = self.service.users().messages().list(
                userId="me",
                q=query,
                maxResults=10
            ).execute()

            messages = results.get("messages", [])

            self.logger.debug(f"Found {len(messages)} unread emails")

            for message in messages:
                # Get full message details
                msg = self.service.users().messages().get(
                    userId="me",
                    id=message["id"],
                    format="full"
                ).execute()

                # Extract metadata
                headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

                # Create event
                event = WatcherEvent(
                    watcher_name=self.name,
                    event_type="new_email",
                    raw_data={
                        "message_id": msg["id"],
                        "thread_id": msg["threadId"],
                        "subject": headers.get("Subject", ""),
                        "from": headers.get("From", ""),
                        "to": headers.get("To", ""),
                        "date": headers.get("Date", ""),
                        "snippet": msg.get("snippet", ""),
                        "labels": msg.get("labelIds", []),
                    },
                )

                events.append(event)

            # Update last checked time
            self.last_checked_time = datetime.now()

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            raise

        return events

    async def cleanup(self) -> None:
        """Cleanup Gmail connection."""
        self.service = None
        self.logger.info("Gmail watcher cleaned up")

    def event_to_task(self, event: WatcherEvent) -> Optional[Task]:
        """Convert email event to task."""
        data = event.raw_data

        # Create task
        task = Task(
            source=self.name,
            title=f"Email: {data['subject'][:50]}",
            description=f"""
New email received from {data['from']}

**Subject:** {data['subject']}

**Snippet:**
{data['snippet']}

**Received:** {data['date']}
""".strip(),
            context=data,
            status=TaskStatus.PENDING,
        )

        return task

    def calculate_priority(self, event: WatcherEvent) -> Priority:
        """Calculate email priority."""
        data = event.raw_data

        # Check for urgent keywords
        subject = data.get("subject", "").lower()
        snippet = data.get("snippet", "").lower()

        urgent_keywords = ["urgent", "asap", "emergency", "important", "critical"]

        if any(keyword in subject or keyword in snippet for keyword in urgent_keywords):
            return Priority.P0

        # Check for IMPORTANT label
        if "IMPORTANT" in data.get("labels", []):
            return Priority.P1

        # Default: P1 for client emails (you can customize this)
        return Priority.P1

    async def send_email(
        self, to: str, subject: str, body: str, thread_id: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Send an email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            thread_id: Optional thread ID to reply to

        Returns:
            Sent message metadata
        """
        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        message_body = {"raw": raw_message}
        if thread_id:
            message_body["threadId"] = thread_id

        sent_message = self.service.users().messages().send(
            userId="me",
            body=message_body
        ).execute()

        self.logger.info(f"Sent email to {to}: {subject}")

        return sent_message

    async def mark_as_read(self, message_id: str) -> None:
        """Mark an email as read."""
        if not self.service:
            raise RuntimeError("Gmail service not initialized")

        self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

        self.logger.debug(f"Marked message {message_id} as read")
