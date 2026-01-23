# Twitter (X) Manager Skill

## Description
Manage Twitter/X presence - create tweets, threads, engage with audience, and track analytics.

## Instructions

### 1. Content Types

**Single Tweet**
```
[Concise, punchy message under 280 chars]

[Optional link]
```

**Thread Format**
```
1/ [Hook - the most compelling part]

2/ [Context or background]

3/ [Key point 1]

4/ [Key point 2]

5/ [Key point 3]

6/ [Conclusion + CTA]

[Like + RT if this was helpful!]
```

**Quote Tweet**
```
[Your take on the original tweet]

[Add value, don't just agree]
```

**Reply Strategy**
- Add value to conversations
- Be helpful, not promotional
- Build relationships with industry peers

### 2. Tweet Templates

**Insight Tweet**
```
[Counterintuitive observation]

Most people think [common belief].

But actually [your insight].

Here's why:
```

**Tip Tweet**
```
Quick tip for [audience]:

[Actionable advice]

Bookmark this.
```

**Story Tweet**
```
[Year] ago, I [situation].

Today, [outcome].

What changed:
[Lesson learned]
```

**Engagement Tweet**
```
Unpopular opinion:

[Your take]

Agree or disagree?
```

### 3. Posting Schedule

- Frequency: 3-5 tweets/day
- Best times: 8-10 AM, 12-1 PM, 5-6 PM
- Threads: 1-2 per week (weekday mornings)
- Weekend: Lighter posting, more casual

### 4. Workflow

1. **Content Creation**
   - Monitor trending topics
   - Draft tweet following templates
   - Check character count (280 max)
   - Schedule for optimal time

2. **Approval Request**
   ```markdown
   ---
   type: approval_request
   action: social_post
   platform: twitter
   tweet_type: single|thread|reply
   scheduled_time: 2026-01-24T09:00:00Z
   ---

   # Twitter Post Approval

   ## Content
   [Tweet text]

   ## Thread (if applicable)
   1/ [First tweet]
   2/ [Second tweet]
   ...

   ## Replying To
   [Original tweet URL if reply]

   ## Media
   [Image/video if any]

   ## Character Count
   [X/280]
   ```

3. **Post (After Approval)**
   - Post via Twitter API v2
   - Log tweet ID
   - Schedule engagement check

4. **Engagement**
   - Monitor replies
   - Flag important mentions
   - Track retweets from notable accounts

### 5. Twitter API v2 Integration

**Authentication:**
- OAuth 2.0 with PKCE
- Required scopes: tweet.read, tweet.write, users.read

**Endpoints:**
- POST /2/tweets - Create tweet
- GET /2/tweets/:id - Get tweet
- GET /2/users/:id/tweets - User timeline
- GET /2/tweets/:id/metrics - Engagement metrics

**Rate Limits:**
- 200 tweets/15 min (app level)
- 50 tweets/24h (user level for free tier)

### 6. Thread Posting Logic

```python
# Pseudocode for thread posting
def post_thread(tweets: list[str]):
    reply_to = None
    for tweet in tweets:
        response = post_tweet(tweet, reply_to=reply_to)
        reply_to = response.tweet_id
    return first_tweet_url
```

### 7. Engagement Summary Format

```markdown
## Twitter Weekly Summary

**Period:** Jan 13-19, 2026

### Tweet Performance

| Date | Type | Impressions | Engagements | Clicks |
|------|------|-------------|-------------|--------|
| Jan 14 | Thread | 5,678 | 234 | 89 |
| Jan 15 | Single | 1,234 | 45 | 12 |

### Engagement Rate
- Average: 4.2%
- Best performer: 6.8%

### Follower Growth
- New followers: +67
- Unfollows: -23
- Net: +44

### Top Tweet
"[Tweet content]"
- 234 likes, 45 retweets, 12 replies

### Notable Mentions
- @[influential_account] retweeted your thread
- @[potential_client] replied asking about services

### Hashtag Performance
| Hashtag | Uses | Avg Impressions |
|---------|------|-----------------|
| #hashtag1 | 5 | 2,345 |

### Recommendations
- Threads outperform single tweets 3x
- [Other insights]
```

### 8. Safety Rules

- ALWAYS require approval for tweets
- No political commentary
- No engagement with trolls
- Don't tweet while emotional/reactive
- Avoid controversy and hot takes on sensitive issues
- Never delete tweets without documenting reason
- Be careful with quote tweets (can seem aggressive)

### 9. Best Practices

**Do:**
- Be authentic and conversational
- Share genuine insights
- Engage with replies
- Use visuals when relevant
- Build in public

**Don't:**
- Over-promote
- Use too many hashtags (0-2 max)
- Tweet controversial takes
- Engage with negativity
- Buy followers or engagement

## Example Usage

```
Create a Twitter thread about the 5 key lessons from completing Project Alpha
```

## Tools Used
- Read (for content ideas)
- Write (for drafts)
- Bash (for API calls via MCP)
