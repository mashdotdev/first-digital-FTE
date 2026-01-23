"""
Social Media Watcher for Digital FTE

Monitors multiple social media platforms for scheduled posting times
and engagement tracking. Supports Facebook, Instagram, and Twitter/X.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from ..base_watcher import BaseWatcher
from ..models import WatcherEvent, Priority, Task, TaskStatus

logger = logging.getLogger(__name__)


class SocialPlatform(str, Enum):
    """Supported social media platforms."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"


class SocialMediaWatcher(BaseWatcher):
    """
    Social Media Watcher that:
    1. Monitors scheduled posting times for each platform
    2. Creates content creation tasks
    3. Tracks engagement metrics (future)
    """

    def __init__(
        self,
        vault_path: str,
        enabled_platforms: Optional[list[SocialPlatform]] = None,
        check_interval: int = 1800,  # Check every 30 minutes
    ):
        super().__init__(
            name="social_media",
            vault_path=vault_path,
            check_interval=check_interval,
        )

        # Default to all platforms
        self.enabled_platforms = enabled_platforms or [
            SocialPlatform.FACEBOOK,
            SocialPlatform.INSTAGRAM,
            SocialPlatform.TWITTER,
        ]

        # Posting schedules (day_of_week: list of hours)
        self.schedules = {
            SocialPlatform.FACEBOOK: {
                0: [14],      # Monday 2 PM
                2: [14],      # Wednesday 2 PM
                4: [14],      # Friday 2 PM
            },
            SocialPlatform.INSTAGRAM: {
                1: [11, 19],  # Tuesday 11 AM, 7 PM
                3: [11, 19],  # Thursday 11 AM, 7 PM
                5: [11],      # Saturday 11 AM
            },
            SocialPlatform.TWITTER: {
                0: [9, 17],   # Monday 9 AM, 5 PM
                1: [9, 17],   # Tuesday 9 AM, 5 PM
                2: [9, 17],   # Wednesday 9 AM, 5 PM
                3: [9, 17],   # Thursday 9 AM, 5 PM
                4: [9, 17],   # Friday 9 AM, 5 PM
            },
        }

        # Track last check for each platform
        self.last_checks: dict[SocialPlatform, datetime] = {}

    async def initialize(self) -> None:
        """Initialize the social media watcher."""
        logger.info(f"Social media watcher initialized")
        logger.info(f"Enabled platforms: {[p.value for p in self.enabled_platforms]}")

    async def check_for_events(self) -> list[WatcherEvent]:
        """Check if it's time to create posting tasks for any platform."""
        events = []
        now = datetime.now()
        day_of_week = now.weekday()
        current_hour = now.hour

        for platform in self.enabled_platforms:
            schedule = self.schedules.get(platform, {})

            if day_of_week in schedule:
                scheduled_hours = schedule[day_of_week]

                if current_hour in scheduled_hours:
                    # Check if we already created a task for this slot
                    last_check = self.last_checks.get(platform)
                    if last_check is None or (
                        last_check.date() != now.date() or
                        last_check.hour != current_hour
                    ):
                        self.last_checks[platform] = now

                        event = WatcherEvent(
                            source=f"social_{platform.value}",
                            event_type="scheduled_post",
                            content=f"Time to create {platform.value.title()} post",
                            metadata={
                                "platform": platform.value,
                                "scheduled_time": now.isoformat(),
                                "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][day_of_week],
                                "optimal_time": True,
                            },
                            timestamp=now,
                        )
                        events.append(event)
                        logger.info(
                            f"Created {platform.value} posting task for "
                            f"{now.strftime('%A %H:%M')}"
                        )

        return events

    def event_to_task(self, event: WatcherEvent) -> Task:
        """Convert a social media event to a Task."""
        platform = event.metadata.get("platform", "social")
        platform_title = platform.title()

        # Platform-specific instructions
        instructions = {
            "facebook": """
### Facebook Post Guidelines
- Optimal length: 40-80 characters for highest engagement
- Include an image (1200x630 px recommended)
- Ask a question to encourage comments
- Use 1-3 relevant hashtags
""",
            "instagram": """
### Instagram Post Guidelines
- High-quality visual is essential
- Caption can be longer (up to 2200 chars)
- Use 20-30 hashtags (in first comment or caption)
- Include a clear call-to-action
- Consider carousel for educational content
""",
            "twitter": """
### Twitter Post Guidelines
- Keep under 280 characters
- Consider a thread for longer content
- Use 0-2 hashtags maximum
- Include a hook in the first line
- Visuals increase engagement 150%
""",
        }

        return Task(
            id=f"{platform.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=f"Create {platform_title} Post",
            description=f"""
## {platform_title} Posting Task

**Scheduled Time:** {event.metadata.get('scheduled_time', 'N/A')}
**Day:** {event.metadata.get('day', 'N/A')}

### Instructions

1. Review recent business achievements in `/Done/` folder
2. Check `Business_Goals.md` for current messaging priorities
3. Draft content following the {platform}-manager skill guidelines
4. Create approval request in `/Pending_Approval/`
5. After approval, post via MCP server

{instructions.get(platform, '')}

### Content Ideas
- Share a recent accomplishment or milestone
- Provide value with tips or insights
- Behind-the-scenes content
- Engage with a question or poll
- Celebrate team or customer wins

### Remember
- All social posts require human approval
- Maintain brand voice consistency
- No controversial or political content
- Include appropriate call-to-action
""",
            source="social_media_watcher",
            priority=self.calculate_priority(event),
            status=TaskStatus.PENDING,
            created_at=event.timestamp,
            metadata=event.metadata,
        )

    def calculate_priority(self, event: WatcherEvent) -> Priority:
        """Social media posts are P2 priority (important but not urgent)."""
        return Priority.P2

    async def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Social media watcher cleaned up")


# Factory function
def create_social_media_watcher(
    vault_path: str,
    platforms: Optional[list[str]] = None,
) -> SocialMediaWatcher:
    """Create a social media watcher instance."""
    enabled = None
    if platforms:
        enabled = [SocialPlatform(p) for p in platforms if p in [e.value for e in SocialPlatform]]

    return SocialMediaWatcher(
        vault_path=vault_path,
        enabled_platforms=enabled,
    )
