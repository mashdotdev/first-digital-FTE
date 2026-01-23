# Instagram Manager Skill

## Description
Manage Instagram business account - create posts, stories, reels concepts, and generate engagement analytics.

## Instructions

### 1. Content Types

**Feed Post (Image)**
```
[Compelling caption that tells a story]

[Key message in 2-3 short paragraphs]

[Call to action]

.
.
.

#hashtag1 #hashtag2 #hashtag3 #hashtag4 #hashtag5
[Up to 30 hashtags, separated from main content]
```

**Carousel Post**
```
Slide 1: Hook - [Attention-grabbing statement]
Slide 2-9: Value - [Educational content]
Slide 10: CTA - [What to do next]

Caption: [Summary + engagement prompt]
```

**Story Content**
- Behind-the-scenes moments
- Quick tips (text overlay)
- Polls and questions
- Countdowns to events
- Product teasers

**Reels Concept**
```
Hook (0-3 sec): [Attention grabber]
Content (3-25 sec): [Main value]
CTA (25-30 sec): [Follow, like, save]
Audio: [Trending sound suggestion]
```

### 2. Posting Schedule

- Feed posts: 3-5 per week
- Stories: Daily when possible
- Reels: 2-3 per week
- Best times: 11 AM-1 PM, 7-9 PM
- Best days: Tuesday, Wednesday, Friday

### 3. Visual Guidelines

**Image Specs:**
- Square: 1080x1080 (feed)
- Portrait: 1080x1350 (feed, better engagement)
- Story/Reel: 1080x1920

**Aesthetic:**
- Consistent color palette
- Cohesive feed appearance
- High-quality images only
- Brand elements visible

### 4. Hashtag Strategy

**Hashtag Categories:**
1. Branded (1-2): Your unique hashtags
2. Industry (5-10): Relevant to your field
3. Community (5-10): Your target audience uses
4. Trending (3-5): Currently popular
5. Location (1-2): If relevant

**Hashtag Sets (Rotate):**
```
Set A: #business #entrepreneur #startup #growth...
Set B: #smallbusiness #businesstips #success...
Set C: #motivation #hustle #goals #mindset...
```

### 5. Workflow

1. **Content Planning**
   - Check content calendar
   - Review recent performance
   - Identify trending topics/sounds
   - Plan visual content needs

2. **Create Approval Request**
   ```markdown
   ---
   type: approval_request
   action: social_post
   platform: instagram
   content_type: feed|story|reel
   scheduled_time: 2026-01-24T11:00:00Z
   ---

   # Instagram Post Approval

   ## Visual
   [Image/video description or file path]

   ## Caption
   [Full caption text]

   ## Hashtags
   [List of hashtags]

   ## First Comment
   [Additional hashtags or content]
   ```

3. **Post (After Approval)**
   - Upload via Instagram Graph API or Browser MCP
   - Add to first comment if needed
   - Log post details

4. **Engagement Monitoring**
   - Check performance after 1h, 24h, 48h
   - Respond to comments (flag for approval)
   - Save insights for weekly summary

### 6. Instagram Graph API Integration

**Required:**
- Facebook Page linked to Instagram Business Account
- Access token with instagram_basic, instagram_content_publish

**Endpoints:**
- POST /{ig-user-id}/media - Create media container
- POST /{ig-user-id}/media_publish - Publish
- GET /{media-id}/insights - Get metrics

### 7. Engagement Summary Format

```markdown
## Instagram Weekly Summary

**Period:** Jan 13-19, 2026

### Feed Performance

| Date | Type | Reach | Likes | Comments | Saves |
|------|------|-------|-------|----------|-------|
| Jan 14 | Carousel | 3,456 | 234 | 45 | 89 |
| Jan 16 | Single | 2,123 | 156 | 23 | 34 |

### Stories
- Posted: 12
- Avg. views: 567
- Replies: 8
- Link clicks: 23

### Reels
- Posted: 2
- Total plays: 12,345
- Avg. watch time: 8.5s

### Growth
- New followers: +45
- Unfollows: -12
- Net: +33

### Top Content
[Best performing post] - 234 likes, 89 saves

### Insights
- Carousel posts outperform single images
- [Other observations]
```

### 8. Safety Rules

- ALWAYS require approval for all posts
- Never post without proper image rights
- Avoid controversial hashtags
- Don't buy followers or engagement
- Maintain authentic brand voice
- Flag negative comments for human review

## Example Usage

```
Create an Instagram carousel post with 5 tips from our recent project learnings
```

## Tools Used
- Read (for content ideas)
- Write (for drafts)
- Bash (for API calls via MCP)
