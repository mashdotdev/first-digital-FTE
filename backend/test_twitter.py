"""Quick test script for Twitter integration."""

import asyncio
import sys
sys.path.insert(0, "src")

from digital_fte.mcp.twitter_mcp import TwitterMCP


async def test_twitter(post_tweet: bool = False, tweet_text: str = None):
    """Test Twitter MCP initialization and optionally post a tweet."""
    print("Testing Twitter MCP...")

    mcp = TwitterMCP()

    # Initialize
    print("Initializing Twitter client...")
    success = await mcp.initialize()

    if not success:
        print("FAILED: Could not initialize Twitter MCP")
        print("Check your .env file has valid Twitter credentials")
        return False

    print("SUCCESS: Twitter MCP initialized!")

    # Health check
    healthy = await mcp.health_check()
    print(f"Health check: {'PASSED' if healthy else 'FAILED'}")

    if not healthy:
        return False

    # Post a test tweet if requested
    if post_tweet:
        text = tweet_text or "Testing my Digital FTE AI Employee Twitter integration!"
        print(f"\nPosting tweet: {text}")
        print(f"Character count: {len(text)}/280")

        try:
            result = await mcp.post_tweet(text)
            print(f"\nTweet posted successfully!")
            print(f"Tweet ID: {result['id']}")
            print(f"URL: {result['url']}")
        except Exception as e:
            print(f"Failed to post tweet: {e}")
            return False

    await mcp.cleanup()
    return True


if __name__ == "__main__":
    # Parse command line args
    post = "--post" in sys.argv
    tweet = None

    for i, arg in enumerate(sys.argv):
        if arg == "--text" and i + 1 < len(sys.argv):
            tweet = sys.argv[i + 1]

    if post and not tweet:
        print("Usage: python test_twitter.py --post --text 'Your tweet text'")
        print("\nRunning without --post to just test connection...")
        post = False

    result = asyncio.run(test_twitter(post_tweet=post, tweet_text=tweet))
    print("\n" + "="*50)
    print(f"Test {'PASSED' if result else 'FAILED'}")
