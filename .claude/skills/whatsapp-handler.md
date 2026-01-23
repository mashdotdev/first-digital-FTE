# WhatsApp Handler Skill

## Description
Monitor WhatsApp Web for incoming messages, detect urgent keywords, and draft appropriate responses for approval.

## Instructions

### 1. Message Detection

Monitor for keywords indicating urgency:
- "urgent", "asap", "emergency"
- "invoice", "payment", "money"
- "help", "problem", "issue"
- "deadline", "today", "now"
- VIP contact names from Company_Handbook.md

### 2. Priority Classification

| Keywords | Priority | Response Time |
|----------|----------|---------------|
| emergency, urgent, asap | P0 | < 30 min |
| invoice, payment, deadline | P1 | < 2 hours |
| help, question, issue | P2 | < 4 hours |
| general inquiry | P3 | < 24 hours |

### 3. Response Templates

**Acknowledgment (Immediate)**
```
Hi [Name]! Got your message. Looking into this now and will get back to you shortly.
```

**Invoice Request**
```
Hi [Name]! I'll prepare that invoice for you right away. You should receive it via email within [timeframe].
```

**Meeting Request**
```
Hi [Name]! Let me check my calendar and get back to you with available slots. Preferred time: morning or afternoon?
```

**General Response**
```
Hi [Name]! Thanks for reaching out. [Response to their query]. Let me know if you need anything else!
```

### 4. Workflow

1. **Detection** (via Watcher)
   - Playwright monitors WhatsApp Web
   - Detects unread messages matching keywords
   - Creates task in `/Needs_Action/WHATSAPP_[contact]_[date].md`

2. **Processing**
   - Read message context
   - Check if sender is known contact
   - Classify priority
   - Draft response

3. **Approval**
   - All WhatsApp responses require approval
   - Create approval file with draft message
   - Wait for human to approve/modify

4. **Send**
   - After approval, send via WhatsApp Web automation
   - Log the interaction
   - Move to /Done

### 5. Task File Format

```markdown
---
type: whatsapp
from: Contact Name
phone: +1234567890
priority: P1
keywords_detected: [invoice, urgent]
received: 2026-01-23T10:30:00Z
status: pending
---

## Message Content

[Original message text]

## Suggested Response

[AI-drafted response]

## Context

- Known contact: Yes/No
- Previous interactions: [count]
- Last topic: [topic]
```

### 6. Safety Rules

- ALWAYS require approval for WhatsApp messages
- Never send messages to unknown numbers without approval
- Be aware of WhatsApp's Terms of Service
- Limit automated interactions to avoid account restrictions
- Keep session data secure (never sync to cloud)

## Example Usage

```
Process the WhatsApp message from John asking about the project deadline
```

## Tools Used
- Read (for message content)
- Write (for drafts)
- Bash (for Playwright automation via MCP)
