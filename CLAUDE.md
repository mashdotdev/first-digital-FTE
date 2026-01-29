# Digital FTE - Claude Context File

## Project Overview

Digital FTE (Full-Time Equivalent) is an autonomous AI employee system that manages personal and business affairs. It uses:
- **Claude Code CLI** as the reasoning engine (uses Claude Pro subscription)
- **Obsidian Vault** as the management dashboard and task storage
- **Next.js Dashboard** for real-time monitoring and approvals

## Current Status (2026-01-29)

**Tier:** Gold (100% complete)

### Working Features
- Gmail automation (read, analyze, reply) - FULLY TESTED
- **WhatsApp message READING** - WORKING! (detects unread, creates tasks)
- **WhatsApp message SENDING** - IMPLEMENTED (test scripts ready)
- **Invoice PDF Generation** - NEW! (generates PDF invoices in /Invoices)
- **Twitter/X Integration** - NEW! (post tweets, threads via Tweepy)
- Claude Code CLI integration (replaced OpenAI Agents SDK)
- Ralph Wiggum autonomous loop (5-min cycle)
- HITL approval workflow
- CEO Briefing generation
- Next.js CEO Dashboard with real-time updates
- Filesystem watcher
- Audit logging (JSONL + Markdown)

### Example Workflow (from details.md lines 899-984)
The full invoice flow is now implemented and tested:
1. WhatsApp Watcher detects "invoice" keyword -> creates P1 task
2. Claude proposes `invoice_generate` action
3. Human approves via dashboard
4. InvoiceMCP generates PDF in /Invoices folder
5. EmailMCP sends invoice to client
6. Task moved to /Done, action logged

### Test Scripts
- `backend/test_invoice_flow.py` - Tests invoice generation end-to-end
- `backend/test_whatsapp_send.py` - Tests WhatsApp send functionality
- `backend/test_twitter.py` - Tests Twitter posting functionality

### Not Yet Implemented
- Odoo connection (MCP ready, needs Odoo instance)

## Architecture

```
External Sources (Gmail, WhatsApp, etc.)
         ↓ Watchers detect events
Obsidian Vault (/Needs_Action, /Pending_Approval, etc.)
         ↓ Ralph loop processes
Claude Code CLI (analyzes, proposes actions)
         ↓ Auto-approve or human review
MCP Servers execute actions (EmailMCP, WhatsAppMCP, etc.)
         ↓ Results logged
Audit Trail + Dashboard updates
```

## Key Directories

```
A:\Desktop\first-digital-FTE\
├── AI_Employee_Valut/          # Obsidian vault
│   ├── Needs_Action/           # Tasks to process
│   ├── Pending_Approval/       # Awaiting human review
│   ├── Approved/               # Ready to execute
│   ├── Rejected/               # Learn from these
│   ├── Done/                   # Completed
│   ├── Company_Handbook.md     # Operating rules
│   └── Business_Goals.md       # Strategic priorities
├── backend/                    # Python backend
│   └── src/digital_fte/
│       ├── orchestrator.py     # Main brain
│       ├── config.py           # Settings
│       ├── watchers/           # Gmail, Filesystem, WhatsApp
│       └── mcp/                # Email, Browser, Odoo MCPs
├── frontend/                   # Next.js dashboard
│   └── src/
│       ├── app/                # Pages and API routes
│       └── components/         # Dashboard components
├── .claude/skills/             # Agent skill definitions
├── CHECKPOINT.md               # Development progress
└── CLAUDE.md                   # This file
```

## Session 8 Fixes (2026-01-25)
- Fixed QR code detection (wait for canvas to render with size > 50x50)
- Fixed login page detection (check for "Steps to log in" text)
- Fixed navigation timeout (increased to 60s, handle already-loaded page)
- Added multiple fallback selectors for chat items and unread badges
- Added debug screenshots on failure (saved to `.whatsapp_session/`)
- Added detailed INFO-level logging for message detection

## WhatsApp Implementation Files (COMPLETE)

### Created:
- `backend/src/digital_fte/watchers/whatsapp_watcher.py` - Playwright-based watcher
- `backend/src/digital_fte/mcp/whatsapp_mcp.py` - WhatsApp action executor

### Modified:
- `backend/src/digital_fte/orchestrator.py` - Registers WhatsApp watcher + MCP
- `backend/src/digital_fte/config.py` - Added `whatsapp_user_data_dir` setting
- `backend/src/digital_fte/watchers/__init__.py` - Exports WhatsAppWatcher
- `backend/src/digital_fte/mcp/__init__.py` - Exports WhatsAppMCP

### Reference:
- `.claude/skills/whatsapp-handler.md` - Skill definition with priority keywords

## Invoice MCP (NEW - 2026-01-29)

### Files:
- `backend/src/digital_fte/mcp/invoice_mcp.py` - PDF invoice generator

### Features:
- Generates professional PDF invoices
- Supports multiple line items
- Calculates totals automatically
- Saves to `/Invoices` folder in vault

### Action Type: `invoice_generate`
```json
{
  "action_type": "invoice_generate",
  "action_data": {
    "client_name": "Client A",
    "client_email": "client@example.com",
    "amount": 1500.00,
    "description": "Services rendered",
    "items": [{"description": "...", "quantity": 1, "unit_price": 100}],
    "notes": "Optional notes"
  }
}
```

## Twitter MCP (NEW - 2026-01-29)

### Files:
- `backend/src/digital_fte/mcp/twitter_mcp.py` - Twitter/X API integration

### Features:
- Post single tweets
- Post threads (multiple connected tweets)
- Delete tweets
- Reply to tweets

### Action Type: `twitter_post` or `social_post` with platform=twitter
```json
{
  "action_type": "twitter_post",
  "action_data": {
    "content": "Tweet text (max 280 chars)",
    "reply_to_id": "optional_tweet_id"
  }
}
```

### Environment Variables:
```bash
TWITTER_ENABLED=true
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

## Commands

```bash
# Backend (from backend/ folder)
cd backend
uv run digital-fte start           # Start orchestrator
uv run digital-fte status          # Show system status
uv run digital-fte briefing        # Generate CEO briefing

# Frontend (from frontend/ folder)
cd frontend
bun dev                            # Dashboard at localhost:3000

# Playwright (for WhatsApp)
playwright install chromium        # Install browser
```

## Environment Variables

```bash
# backend/.env
CLAUDE_CODE_PATH=claude
CLAUDE_CODE_MODEL=sonnet
VAULT_PATH=../AI_Employee_Valut
GOOGLE_CREDENTIALS_PATH=credentials.json

# WhatsApp (now implemented!)
WHATSAPP_ENABLED=true                    # Set to true to enable
WHATSAPP_POLL_INTERVAL=120               # Check every 2 minutes
WHATSAPP_USER_DATA_DIR=.whatsapp_session # Persistent browser session
```

## WhatsApp Automation Design

### How it works:
1. **First run:** Opens WhatsApp Web, user scans QR code
2. **Persistent session:** Browser profile saved in `.whatsapp_session/`
3. **Watcher loop:** Check for unread messages every 2 minutes
4. **Task creation:** Unread messages become tasks in /Needs_Action
5. **Claude analysis:** Proposes reply based on handbook/goals
6. **Approval:** Human approves via dashboard or auto-approve if confident
7. **Send:** WhatsAppMCP sends message via Playwright

### Key selectors (WhatsApp Web):
- Unread indicator: `[data-icon="unread-count"]` or `.unread-count`
- Chat list: `[data-testid="chat-list"]`
- Message input: `[data-testid="conversation-compose-box-input"]`
- Send button: `[data-testid="send"]`

## Session Resume Prompt

```
"Continue Digital FTE WhatsApp. Read CLAUDE.md for context.
DONE: WhatsApp reading messages works! Creates tasks from unread messages.
NEXT: Test WhatsApp REPLY - approve a task and verify send_message() works.
Files: whatsapp_watcher.py (send_message at line 511), whatsapp_mcp.py
The send selectors may need updating - check debug screenshots if send fails."
```
