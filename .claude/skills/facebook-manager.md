# Facebook Manager Skill

## Description
Manage Facebook business page - create posts, schedule content, and generate engagement summaries.

## Instructions

### 1. Content Types

**Business Update**
```
[Exciting news/update]

[2-3 sentences explaining the update]

[Call to action - like, comment, share, or link]

#hashtag1 #hashtag2
```

**Behind the Scenes**
```
[Peek behind the curtain]

[Story or insight about how things work]

What would you like to see more of? Let us know in the comments!
```

**Educational Content**
```
Did you know? [Interesting fact]

Here's why this matters for [audience]:

[Explanation]

Save this post for later!
```

**Promotional**
```
[Product/Service highlight]

[Key benefits - bullet points work well]

[Limited time offer if applicable]

[Clear CTA with link]
```

### 2. Posting Schedule

- Optimal times: 1-4 PM on weekdays
- Best days: Wednesday, Thursday, Friday
- Frequency: 3-5 posts per week
- Mix: 80% value content, 20% promotional

### 3. Workflow

1. **Content Creation**
   - Review recent activities and achievements
   - Check content calendar in `/Plans/`
   - Draft post following templates
   - Select or suggest image/media

2. **Approval Request**
   ```markdown
   ---
   type: approval_request
   action: social_post
   platform: facebook
   scheduled_time: 2026-01-24T14:00:00Z
   ---

   # Facebook Post Approval

   ## Draft Content
   [Post text]

   ## Media
   [Image description or path]

   ## Target Audience
   [Who this is for]

   ## Goal
   [Engagement/traffic/awareness]
   ```

3. **Posting (After Approval)**
   - Post via Facebook Graph API or Browser MCP
   - Log post details and ID
   - Schedule engagement check for 24h later

4. **Engagement Summary**
   - Track: Likes, comments, shares, reach
   - Compare to previous posts
   - Include in CEO Briefing

### 4. Facebook-Specific Guidelines

- Images: 1200x630 pixels optimal
- Video: Under 2 minutes performs best
- Links: Use UTM parameters for tracking
- Hashtags: 1-3 maximum (less is more on FB)
- Tagging: Only tag relevant pages/people

### 5. Integration with Graph API

**Authentication:**
- Page Access Token required
- Permissions: pages_manage_posts, pages_read_engagement

**Endpoints Used:**
- POST /{page-id}/feed - Create post
- GET /{post-id}/insights - Get metrics
- GET /{page-id}/posts - List posts

### 6. Engagement Summary Format

```markdown
## Facebook Weekly Summary

**Period:** Jan 13-19, 2026

### Post Performance

| Date | Content | Reach | Engagement | Link Clicks |
|------|---------|-------|------------|-------------|
| Jan 15 | Product update | 1,234 | 89 | 45 |
| Jan 17 | Tips post | 2,567 | 156 | 23 |

### Totals
- Posts: 3
- Total Reach: 5,234
- Total Engagement: 312
- Engagement Rate: 5.9%

### Top Performing Post
[Post content excerpt] - 156 engagements

### Recommendations
- [Insight based on data]
```

### 7. Safety Rules

- ALWAYS require approval before posting
- No political or controversial content
- Respond to negative comments with care (flag for human)
- Never delete user comments without approval
- Maintain brand voice consistency

## Example Usage

```
Create a Facebook post announcing the completion of Project Alpha
```

## Tools Used
- Read (for context)
- Write (for drafts)
- Bash (for Graph API calls via MCP)
