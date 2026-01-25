"""WhatsApp watcher using Playwright for WhatsApp Web automation."""

import asyncio
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..base_watcher import BaseWatcher
from ..config import get_settings
from ..models import Priority, Task, TaskStatus, WatcherEvent

# Playwright is imported lazily to avoid issues if not installed
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Browser = Any
    BrowserContext = Any
    Page = Any


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for new messages using Playwright."""

    # Priority keywords from skill spec
    P0_KEYWORDS = ["emergency", "urgent", "asap"]
    P1_KEYWORDS = ["invoice", "payment", "deadline", "money"]
    P2_KEYWORDS = ["help", "question", "issue", "problem"]

    # WhatsApp Web selectors (2026) - multiple fallbacks for reliability
    SELECTORS = {
        # Chat list selectors
        "chat_list": "#pane-side",
        "chat_item": "[data-testid='cell-frame-container'], [data-testid='list-item-chat']",
        "unread_badge": "[data-testid='icon-unread-count'], .unread-count, span[data-icon='unread-count'], ._ahlk",

        # Conversation selectors
        "conversation_header": "[data-testid='conversation-info-header-chat-title']",
        "message_input": "[data-testid='conversation-compose-box-input'], footer [contenteditable='true'], div[contenteditable='true'][data-tab='10']",
        "send_button": "[data-testid='send'], [data-icon='send'], button[aria-label='Send']",

        # Message content
        "message_in": ".message-in, [data-testid='msg-container']",
        "message_text": ".selectable-text.copyable-text, [data-testid='conversation-text-body']",

        # Login state - multiple fallbacks
        "qr_code": "canvas[aria-label='Scan this QR code to link a device!'], canvas[aria-label='Scan me!'], div[data-ref] canvas",
        "logged_in_indicator": "#pane-side, [data-testid='chat-list'], div[aria-label='Chat list']",

        # Landing/loading page elements - detect the login instructions page
        "login_page": "div:has-text('Steps to log in'), div:has-text('Log in with phone number')",
        "qr_loading": "div[data-ref]",  # QR container (even while loading)
    }

    def __init__(self) -> None:
        super().__init__(name="whatsapp")
        self.playwright: Optional[Any] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._processed_message_ids: set[str] = set()
        self._last_check: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize Playwright browser with persistent session."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright not installed. Install with: pip install playwright && playwright install chromium"
            )

        self.logger.info("Initializing WhatsApp watcher with Playwright")

        # Get user data directory for persistent session
        user_data_dir = self.settings.whatsapp_user_data_dir
        if not user_data_dir.exists():
            user_data_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created WhatsApp session directory: {user_data_dir}")

        # Start Playwright
        self.playwright = await async_playwright().start()

        # Launch browser with persistent context (saves QR login)
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,  # Must be visible for QR scanning
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
            ],
            viewport={"width": 1280, "height": 800},
        )

        # Get or create page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        # Navigate to WhatsApp Web (with extended timeout for slow connections)
        try:
            current_url = self.page.url
            if "web.whatsapp.com" in current_url:
                self.logger.info("WhatsApp Web already loaded, refreshing...")
                await self.page.reload(timeout=60000)
            else:
                self.logger.info("Navigating to WhatsApp Web...")
                await self.page.goto("https://web.whatsapp.com", wait_until="domcontentloaded", timeout=60000)
            self.logger.info("WhatsApp Web page loaded")
        except Exception as e:
            self.logger.warning(f"Navigation timeout, checking if page loaded anyway: {e}")
            # Check if we're on WhatsApp despite the timeout
            await asyncio.sleep(5)
            if "web.whatsapp.com" not in self.page.url:
                raise RuntimeError(f"Failed to load WhatsApp Web: {e}")

        # Wait for login (QR code or already logged in)
        await self._wait_for_login()

        self.logger.info("WhatsApp watcher initialized successfully")

    async def _wait_for_login(self, timeout: int = 120000) -> None:
        """Wait for user to scan QR code or for existing session to load."""
        self.logger.info("Waiting for WhatsApp Web to load...")

        try:
            # First, wait for the page to fully load (give it time for JS to execute)
            await asyncio.sleep(3)

            # Check if we're already logged in by looking for chat list
            logged_in = await self._check_logged_in()
            if logged_in:
                self.logger.info("Already logged in (session restored)")
                await asyncio.sleep(2)
                return

            # Wait for login page to appear (with QR code area)
            self.logger.info("Waiting for login page to load...")
            await self._wait_for_login_page()

            # Now wait for the actual QR code canvas to render
            self.logger.info("Waiting for QR code to render...")
            qr_ready = await self._wait_for_qr_code()

            if qr_ready:
                self.logger.info("=" * 50)
                self.logger.info("QR CODE READY - Please scan with your phone!")
                self.logger.info("1. Open WhatsApp on your phone")
                self.logger.info("2. Tap Menu (Android) or Settings (iPhone)")
                self.logger.info("3. Tap 'Linked devices' > 'Link a device'")
                self.logger.info("4. Point your phone at the QR code")
                self.logger.info("=" * 50)

                # Wait for user to scan QR code (check every 2 seconds)
                start_time = asyncio.get_event_loop().time()
                while (asyncio.get_event_loop().time() - start_time) < (timeout / 1000):
                    await asyncio.sleep(2)
                    if await self._check_logged_in():
                        self.logger.info("QR code scanned successfully! Logged in.")
                        await asyncio.sleep(3)  # Wait for chats to load
                        return

                raise RuntimeError("Timeout waiting for QR code scan")

            # Last resort: take a screenshot for debugging
            screenshot_path = self.settings.whatsapp_user_data_dir / "debug_screenshot.png"
            await self.page.screenshot(path=str(screenshot_path))
            self.logger.warning(f"Debug screenshot saved to: {screenshot_path}")

            raise RuntimeError("Could not detect WhatsApp login state. Check debug_screenshot.png")

        except Exception as e:
            self.logger.error(f"Failed to complete WhatsApp login: {e}")
            raise RuntimeError(f"WhatsApp login failed: {e}")

    async def _wait_for_login_page(self, timeout: int = 30) -> bool:
        """Wait for the WhatsApp login page to appear."""
        for _ in range(timeout):
            try:
                # Check for login page elements
                page_text = await self.page.content()
                if "Steps to log in" in page_text or "Link a device" in page_text or "Scan" in page_text:
                    return True
                # Check for QR container
                qr_container = self.page.locator("div[data-ref]")
                if await qr_container.count() > 0:
                    return True
            except Exception:
                pass
            await asyncio.sleep(1)
        return False

    async def _wait_for_qr_code(self, timeout: int = 30) -> bool:
        """Wait for the QR code canvas to actually render."""
        for _ in range(timeout):
            try:
                # Look for the canvas element inside the QR container
                canvas = self.page.locator("canvas")
                if await canvas.count() > 0:
                    # Check if canvas has actual size (rendered)
                    first_canvas = canvas.first
                    box = await first_canvas.bounding_box()
                    if box and box['width'] > 50 and box['height'] > 50:
                        return True
            except Exception:
                pass
            await asyncio.sleep(1)
        return False

    async def _check_logged_in(self) -> bool:
        """Check if we're logged into WhatsApp Web."""
        try:
            # Try multiple selectors for logged-in state
            selectors = self.SELECTORS['logged_in_indicator'].split(', ')
            for selector in selectors:
                try:
                    element = self.page.locator(selector)
                    if await element.count() > 0 and await element.first.is_visible():
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

    async def _check_qr_visible(self) -> bool:
        """Check if QR code is visible for scanning."""
        try:
            # Try multiple selectors for QR code
            selectors = self.SELECTORS['qr_code'].split(', ')
            for selector in selectors:
                try:
                    element = self.page.locator(selector)
                    if await element.count() > 0 and await element.first.is_visible():
                        return True
                except Exception:
                    continue

            # Also check for the landing page with QR instructions
            landing_selectors = self.SELECTORS.get('landing_page', '').split(', ')
            for selector in landing_selectors:
                if selector:
                    try:
                        element = self.page.locator(selector)
                        if await element.count() > 0:
                            return True
                    except Exception:
                        continue

            return False
        except Exception:
            return False

    async def check_for_events(self) -> list[WatcherEvent]:
        """Check for new unread messages in WhatsApp."""
        if not self.page:
            raise RuntimeError("WhatsApp page not initialized")

        events: list[WatcherEvent] = []

        try:
            self.logger.info("Checking WhatsApp for new messages...")

            # Wait for chat list to be visible
            try:
                await self.page.wait_for_selector(
                    self.SELECTORS['chat_list'],
                    timeout=10000
                )
            except Exception as e:
                self.logger.warning(f"Chat list not found with primary selector, trying fallback...")
                # Take debug screenshot
                screenshot_path = self.settings.whatsapp_user_data_dir / "debug_check.png"
                await self.page.screenshot(path=str(screenshot_path))
                self.logger.info(f"Debug screenshot saved to: {screenshot_path}")
                return events

            # Find all chat items - try multiple selector strategies
            chat_items = []

            # Strategy 1: data-testid selectors
            for selector in self.SELECTORS['chat_item'].split(', '):
                items = await self.page.locator(selector).all()
                if items:
                    chat_items = items
                    self.logger.info(f"Found {len(chat_items)} chats using selector: {selector}")
                    break

            # Strategy 2: If no items found, try aria-label approach
            if not chat_items:
                items = await self.page.locator("div[role='listitem'], div[role='row']").all()
                if items:
                    chat_items = items
                    self.logger.info(f"Found {len(chat_items)} chats using role selector")

            # Strategy 3: Try getting all direct children of chat list
            if not chat_items:
                items = await self.page.locator("#pane-side > div > div > div").all()
                if items:
                    chat_items = items
                    self.logger.info(f"Found {len(chat_items)} chats using pane-side children")

            if not chat_items:
                self.logger.warning("No chat items found! Taking debug screenshot...")
                screenshot_path = self.settings.whatsapp_user_data_dir / "debug_no_chats.png"
                await self.page.screenshot(path=str(screenshot_path))
                return events

            self.logger.info(f"Scanning {len(chat_items)} chats for unread messages...")

            unread_found = 0
            for idx, chat_item in enumerate(chat_items[:20]):  # Check first 20 chats
                try:
                    # Check if this chat has unread messages - try multiple selectors
                    has_unread = False
                    unread_count = 0

                    # Try to find unread badge with various selectors
                    unread_selectors = [
                        "span[data-testid='icon-unread-count']",
                        "span.unread-count",
                        "span[aria-label*='unread']",
                        "div[aria-label*='unread']",
                        "span._ahlk",  # WhatsApp internal class
                    ]

                    for unread_sel in unread_selectors:
                        badge = chat_item.locator(unread_sel)
                        count = await badge.count()
                        if count > 0:
                            has_unread = True
                            try:
                                unread_text = await badge.first.text_content()
                                unread_count = int(unread_text) if unread_text and unread_text.isdigit() else 1
                            except Exception:
                                unread_count = 1
                            break

                    if not has_unread:
                        continue

                    unread_found += 1

                    # Get contact name
                    contact_name = await self._get_contact_name(chat_item)

                    if not contact_name:
                        continue

                    # Generate a unique ID for this message batch
                    message_id = f"whatsapp_{contact_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"

                    # Skip if we've already processed this
                    if message_id in self._processed_message_ids:
                        continue

                    # Click on chat to get message content
                    await chat_item.click()
                    await asyncio.sleep(1)  # Wait for chat to load

                    # Get the latest messages
                    messages = await self._get_latest_messages()

                    if messages:
                        # Create event
                        event = WatcherEvent(
                            watcher_name=self.name,
                            event_type="new_message",
                            raw_data={
                                "message_id": message_id,
                                "contact_name": contact_name,
                                "unread_count": unread_count,
                                "messages": messages,
                                "latest_message": messages[-1] if messages else "",
                                "received_at": datetime.now().isoformat(),
                            },
                        )
                        events.append(event)
                        self._processed_message_ids.add(message_id)

                        self.logger.info(f"New WhatsApp message from {contact_name}")

                except Exception as e:
                    self.logger.warning(f"Error processing chat item {idx}: {e}")
                    continue

            self._last_check = datetime.now()

            # Summary logging
            if unread_found > 0:
                self.logger.info(f"Found {unread_found} chats with unread messages, created {len(events)} new tasks")
            else:
                self.logger.info("No unread messages found")

            # Clean up old message IDs (keep last 100)
            if len(self._processed_message_ids) > 100:
                self._processed_message_ids = set(list(self._processed_message_ids)[-100:])

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            # Take debug screenshot on error
            try:
                screenshot_path = self.settings.whatsapp_user_data_dir / "debug_error.png"
                await self.page.screenshot(path=str(screenshot_path))
                self.logger.info(f"Error debug screenshot saved to: {screenshot_path}")
            except Exception:
                pass
            raise

        return events

    async def _get_contact_name(self, chat_item: Any) -> Optional[str]:
        """Extract contact name from a chat item."""
        try:
            # Try to get the title/name element
            title_element = chat_item.locator("span[title]").first
            if await title_element.count() > 0:
                return await title_element.get_attribute("title")
            return None
        except Exception:
            return None

    async def _get_latest_messages(self, count: int = 5) -> list[str]:
        """Get the latest incoming messages from the current conversation."""
        messages = []
        try:
            # Get incoming messages
            message_elements = await self.page.locator(
                f"{self.SELECTORS['message_in']} {self.SELECTORS['message_text']}"
            ).all()

            # Get the last N messages
            for element in message_elements[-count:]:
                text = await element.text_content()
                if text:
                    messages.append(text.strip())

        except Exception as e:
            self.logger.debug(f"Error getting messages: {e}")

        return messages

    async def cleanup(self) -> None:
        """Cleanup browser resources."""
        self.logger.info("Cleaning up WhatsApp watcher")

        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

        self.logger.info("WhatsApp watcher cleaned up")

    def event_to_task(self, event: WatcherEvent) -> Optional[Task]:
        """Convert WhatsApp message event to task."""
        data = event.raw_data
        contact_name = data.get("contact_name", "Unknown")
        latest_message = data.get("latest_message", "")

        # Get all messages for context
        all_messages = data.get("messages", [])
        messages_text = "\n".join(f"- {msg}" for msg in all_messages)

        task = Task(
            source=self.name,
            title=f"WhatsApp: {contact_name}",
            description=f"""
New WhatsApp message from **{contact_name}**

**Message:**
{messages_text}

**Received:** {data.get('received_at', 'Unknown')}
**Unread Count:** {data.get('unread_count', 1)}
""".strip(),
            context=data,
            status=TaskStatus.PENDING,
        )

        return task

    def calculate_priority(self, event: WatcherEvent) -> Priority:
        """Calculate message priority based on keywords."""
        data = event.raw_data
        latest_message = data.get("latest_message", "").lower()
        all_messages = " ".join(data.get("messages", [])).lower()

        combined_text = f"{latest_message} {all_messages}"

        # Check P0 keywords
        if any(keyword in combined_text for keyword in self.P0_KEYWORDS):
            return Priority.P0

        # Check P1 keywords
        if any(keyword in combined_text for keyword in self.P1_KEYWORDS):
            return Priority.P1

        # Check P2 keywords
        if any(keyword in combined_text for keyword in self.P2_KEYWORDS):
            return Priority.P2

        # Default to P3
        return Priority.P3

    async def send_message(self, contact_name: str, message: str) -> bool:
        """
        Send a WhatsApp message to a contact.

        Args:
            contact_name: Name of the contact to message
            message: Message text to send

        Returns:
            True if successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("WhatsApp page not initialized")

        try:
            # Search for the contact
            search_box = self.page.locator('[data-testid="chat-list-search"]')
            if await search_box.count() > 0:
                await search_box.click()
                await search_box.fill(contact_name)
                await asyncio.sleep(1)  # Wait for search results

            # Click on the contact in search results
            contact = self.page.locator(f"span[title='{contact_name}']").first
            if await contact.count() > 0:
                await contact.click()
                await asyncio.sleep(1)
            else:
                self.logger.error(f"Contact not found: {contact_name}")
                return False

            # Type the message
            input_box = self.page.locator(self.SELECTORS['message_input']).first
            await input_box.click()
            await input_box.fill(message)
            await asyncio.sleep(0.5)

            # Click send button
            send_button = self.page.locator(self.SELECTORS['send_button']).first
            await send_button.click()

            self.logger.info(f"Sent WhatsApp message to {contact_name}")

            # Wait a moment for message to send
            await asyncio.sleep(1)

            return True

        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp message: {e}")
            return False

    async def open_chat(self, contact_name: str) -> bool:
        """
        Open a chat with a specific contact.

        Args:
            contact_name: Name of the contact

        Returns:
            True if chat opened successfully
        """
        if not self.page:
            raise RuntimeError("WhatsApp page not initialized")

        try:
            # Look for the contact in the chat list
            chat_items = await self.page.locator(self.SELECTORS['chat_item']).all()

            for chat_item in chat_items:
                name = await self._get_contact_name(chat_item)
                if name and contact_name.lower() in name.lower():
                    await chat_item.click()
                    await asyncio.sleep(1)
                    return True

            self.logger.warning(f"Chat not found for: {contact_name}")
            return False

        except Exception as e:
            self.logger.error(f"Error opening chat: {e}")
            return False

    def is_logged_in(self) -> bool:
        """Check if WhatsApp session is active."""
        return self.page is not None and self.context is not None
