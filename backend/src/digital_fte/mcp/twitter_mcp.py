"""Twitter MCP server for posting tweets via Twitter API v2."""

import logging
from typing import Any, Optional

import tweepy

from ..config import get_settings
from ..models import ProposedAction

logger = logging.getLogger(__name__)


class TwitterMCP:
    """MCP server for Twitter/X operations using Tweepy."""

    def __init__(self):
        """Initialize Twitter MCP."""
        self.settings = get_settings()
        self.logger = logger
        self._client: Optional[tweepy.Client] = None
        self._api: Optional[tweepy.API] = None

    async def initialize(self) -> bool:
        """
        Initialize the Twitter API client.

        Returns:
            True if initialization successful, False otherwise
        """
        if not self.settings.twitter_enabled:
            self.logger.info("Twitter integration disabled")
            return False

        if not all([
            self.settings.twitter_api_key,
            self.settings.twitter_api_secret,
            self.settings.twitter_access_token,
            self.settings.twitter_access_token_secret,
        ]):
            self.logger.warning("Twitter API credentials not configured")
            return False

        try:
            # Initialize Twitter API v2 Client (for posting)
            self._client = tweepy.Client(
                consumer_key=self.settings.twitter_api_key,
                consumer_secret=self.settings.twitter_api_secret,
                access_token=self.settings.twitter_access_token,
                access_token_secret=self.settings.twitter_access_token_secret,
            )

            # Also initialize v1.1 API for media uploads
            auth = tweepy.OAuth1UserHandler(
                self.settings.twitter_api_key,
                self.settings.twitter_api_secret,
                self.settings.twitter_access_token,
                self.settings.twitter_access_token_secret,
            )
            self._api = tweepy.API(auth)

            # Verify credentials
            self._client.get_me()
            self.logger.info("Twitter MCP initialized successfully")
            return True

        except tweepy.TweepyException as e:
            self.logger.error(f"Failed to initialize Twitter API: {e}")
            return False

    async def post_tweet(
        self,
        text: str,
        reply_to_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Post a tweet.

        Args:
            text: Tweet text (max 280 characters)
            reply_to_id: Optional tweet ID to reply to

        Returns:
            Tweet metadata including id and text

        Raises:
            RuntimeError: If Twitter client not initialized
            ValueError: If tweet exceeds character limit
        """
        if not self._client:
            raise RuntimeError("Twitter client not initialized. Call initialize() first.")

        # Validate tweet length
        if len(text) > 280:
            raise ValueError(f"Tweet exceeds 280 characters ({len(text)} chars)")

        try:
            response = self._client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id,
            )

            tweet_data = response.data
            self.logger.info(f"Tweet posted successfully: {tweet_data['id']}")

            return {
                "id": tweet_data["id"],
                "text": tweet_data["text"],
                "url": f"https://twitter.com/i/web/status/{tweet_data['id']}",
            }

        except tweepy.TweepyException as e:
            self.logger.error(f"Failed to post tweet: {e}")
            raise RuntimeError(f"Failed to post tweet: {e}")

    async def post_thread(self, tweets: list[str]) -> list[dict[str, Any]]:
        """
        Post a thread (multiple connected tweets).

        Args:
            tweets: List of tweet texts in order

        Returns:
            List of tweet metadata for each tweet in thread
        """
        if not self._client:
            raise RuntimeError("Twitter client not initialized")

        results = []
        reply_to_id = None

        for i, text in enumerate(tweets):
            if len(text) > 280:
                raise ValueError(f"Tweet {i+1} exceeds 280 characters ({len(text)} chars)")

            try:
                response = self._client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=reply_to_id,
                )

                tweet_data = response.data
                results.append({
                    "id": tweet_data["id"],
                    "text": tweet_data["text"],
                    "position": i + 1,
                })

                # Next tweet replies to this one
                reply_to_id = tweet_data["id"]

            except tweepy.TweepyException as e:
                self.logger.error(f"Failed to post tweet {i+1} in thread: {e}")
                raise RuntimeError(f"Failed to post tweet {i+1}: {e}")

        self.logger.info(f"Thread posted successfully ({len(results)} tweets)")
        return results

    async def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet.

        Args:
            tweet_id: ID of the tweet to delete

        Returns:
            True if deleted successfully
        """
        if not self._client:
            raise RuntimeError("Twitter client not initialized")

        try:
            self._client.delete_tweet(tweet_id)
            self.logger.info(f"Tweet deleted: {tweet_id}")
            return True

        except tweepy.TweepyException as e:
            self.logger.error(f"Failed to delete tweet: {e}")
            return False

    async def execute_action(self, action: ProposedAction, task_context: dict) -> bool:
        """
        Execute a Twitter action.

        Args:
            action: The proposed action to execute
            task_context: Original task context

        Returns:
            True if successful, False otherwise
        """
        action_type = action.action_type
        if hasattr(action_type, "value"):
            action_type = action_type.value

        # Handle both "twitter_post" and "social_post" with platform=twitter
        if action_type == "social_post":
            platform = action.action_data.get("platform", "").lower()
            if platform != "twitter":
                self.logger.error(f"TwitterMCP received non-twitter social_post: {platform}")
                return False
        elif action_type != "twitter_post":
            self.logger.error(f"Invalid action type for TwitterMCP: {action_type}")
            return False

        # Initialize if needed
        if not self._client:
            success = await self.initialize()
            if not success:
                self.logger.error("Failed to initialize Twitter client")
                return False

        try:
            action_data = action.action_data
            content = action_data.get("content", action_data.get("text", ""))

            if not content:
                self.logger.error("Missing tweet content")
                return False

            # Check if it's a thread (multiple tweets)
            if isinstance(content, list):
                await self.post_thread(content)
            else:
                # Single tweet
                reply_to = action_data.get("reply_to_id")
                await self.post_tweet(text=content, reply_to_id=reply_to)

            self.logger.info("Successfully executed twitter_post action")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute Twitter action: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if the Twitter MCP is healthy.

        Returns:
            True if healthy and authenticated, False otherwise
        """
        if not self._client:
            return False

        try:
            self._client.get_me()
            return True
        except tweepy.TweepyException:
            return False

    async def cleanup(self) -> None:
        """Clean up resources."""
        self._client = None
        self._api = None
        self.logger.info("Twitter MCP cleaned up")
