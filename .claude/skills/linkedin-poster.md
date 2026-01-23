# LinkedIn Poster Skill

## Description
Automatically create and post business content on LinkedIn to generate leads and establish thought leadership. Posts are drafted and queued for approval before publishing.

## Instructions

### 1. Content Strategy

Generate posts based on:
- Business achievements from `/Done/` folder
- Industry insights related to `Business_Goals.md`
- Tips and value-add content for target audience
- Company updates and milestones

### 2. Post Types

**Thought Leadership**
```
[Insight or observation about industry]

Here's what I've learned:

1. [Key point 1]
2. [Key point 2]
3. [Key point 3]

What's your experience with [topic]?

#relevanthashtag #industry
```

**Achievement Post**
```
Excited to share [achievement]!

[Brief story of how it happened]

Key takeaway: [lesson learned]

#milestone #growth
```

**Value-Add Post**
```
[Problem statement that audience faces]

Here's a simple framework I use:

Step 1: [Action]
Step 2: [Action]
Step 3: [Action]

Save this for later!

#tips #productivity
```

### 3. Posting Schedule

- Optimal times: Tuesday-Thursday, 8-10 AM or 5-6 PM
- Frequency: 2-3 posts per week
- Never post on weekends (lower engagement)

### 4. Workflow

1. **Generate Content**
   - Analyze recent accomplishments
   - Check Business_Goals.md for themes
   - Draft post following templates

2. **Create Approval Request**
   ```markdown
   ---
   type: approval_request
   action: social_post
   platform: linkedin
   scheduled_time: 2026-01-24T09:00:00Z
   ---

   # LinkedIn Post Approval

   ## Draft Content
   [Post content here]

   ## Hashtags
   #tag1 #tag2

   ## Reasoning
   [Why this content now]

   ## To Approve
   Move to /Approved/
   ```

3. **Execute (After Approval)**
   - Post via LinkedIn API/MCP
   - Log post details
   - Track engagement metrics later

### 5. LinkedIn API Integration

Uses Browser MCP or LinkedIn MCP for:
- Authentication (OAuth 2.0)
- Post creation
- Engagement tracking

### 6. Safety Rules

- ALWAYS require human approval before posting
- Never post controversial or political content
- Maintain professional tone
- No competitor mentions
- No confidential business information

## Example Usage

```
Generate a LinkedIn post about completing the Q1 project milestone
```

## Tools Used
- Read (for context from vault)
- Write (for drafts and approvals)
- Bash (for API calls via MCP)
