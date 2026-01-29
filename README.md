# Digital FTE - Your AI Employee

> **"I'm helping!"** - Ralph Wiggum

An autonomous AI assistant that manages your inbox, messages, and business tasks. It monitors Gmail and WhatsApp, proposes actions based on your rules, and executes approved tasks automatically.

**Status:** Gold Tier Complete | Gmail + WhatsApp Automation Working

---

## What It Does

```
Gmail/WhatsApp → AI analyzes → Proposes action → You approve → AI executes
```

- **Monitors** Gmail and WhatsApp for new messages
- **Analyzes** using Claude (via Claude Code CLI)
- **Proposes** responses based on your Company Handbook
- **Asks permission** for important actions (Human-in-the-Loop)
- **Executes** approved actions automatically
- **Reports** CEO briefings on demand

**Privacy-First:** Runs locally. Your data stays on your machine.

---

## Demo

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     External Sources                         │
│              Gmail API    │    WhatsApp Web                  │
└─────────────┬─────────────┴──────────────┬──────────────────┘
              │                            │
              ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Watchers                                │
│         GmailWatcher      │      WhatsAppWatcher            │
│         (OAuth API)       │      (Playwright)               │
└─────────────┬─────────────┴──────────────┬──────────────────┘
              │                            │
              ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Obsidian Vault                             │
│   /Needs_Action → /Pending_Approval → /Approved → /Done     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Ralph Wiggum Loop (5 min)                    │
│   Reads task + Company_Handbook.md + Business_Goals.md      │
│                          ↓                                   │
│              Claude Code CLI (claude --print)                │
│                          ↓                                   │
│              Proposes action with confidence                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────┐         ┌──────────────────────┐
│   Auto-Approve       │         │   Human Review       │
│   (confidence ≥85%)  │         │   (CEO Dashboard)    │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           └───────────────┬────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Executors                             │
│        EmailMCP (Gmail API)  │  WhatsAppMCP (Playwright)    │
└─────────────────────────────────────────────────────────────┘
```

### CEO Dashboard (Next.js)

The web dashboard at `localhost:3000` shows:
- System status (watchers running, health)
- Task queue with real-time updates
- Pending approvals (approve/reject with one click)
- Activity feed from audit logs
- Social channel connections

---

## Quick Start

### Prerequisites

| Requirement | Installation |
|-------------|--------------|
| Python 3.11+ | [python.org](https://python.org) |
| UV package manager | `pip install uv` |
| Node.js 18+ | [nodejs.org](https://nodejs.org) |
| Bun (for frontend) | `npm install -g bun` |
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |
| Playwright | `playwright install chromium` |

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/digital-fte.git
cd digital-fte

# Backend dependencies
cd backend
uv sync

# Frontend dependencies
cd ../frontend
bun install
```

### 2. Configure Environment

```bash
# Backend config
cd backend
cp .env.example .env
```

Edit `backend/.env`:

```env
# Required
CLAUDE_CODE_PATH=claude
CLAUDE_CODE_MODEL=sonnet
VAULT_PATH=../AI_Employee_Valut

# Gmail (optional - for email automation)
GOOGLE_CREDENTIALS_PATH=credentials.json
GMAIL_ENABLED=true

# WhatsApp (optional - for message automation)
WHATSAPP_ENABLED=true
WHATSAPP_POLL_INTERVAL=120
WHATSAPP_USER_DATA_DIR=.whatsapp_session
```

### 3. Gmail Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `credentials.json` to `backend/`
5. First run will open browser for authorization

### 4. WhatsApp Setup (Optional)

1. Ensure `WHATSAPP_ENABLED=true` in `.env`
2. Run the backend - browser opens WhatsApp Web
3. Scan QR code with your phone
4. Session saved in `.whatsapp_session/` (persistent)

### 5. Run

**Terminal 1 - Backend:**
```bash
cd backend
uv run digital-fte start
```

**Terminal 2 - Frontend:**
```bash
cd frontend
bun dev
```

**Open:** http://localhost:3000

---

## CLI Commands

```bash
cd backend

# Start the orchestrator (main loop)
uv run digital-fte start

# Check system status
uv run digital-fte status

# Generate CEO briefing
uv run digital-fte briefing

# Approve a pending task
uv run digital-fte approve <task-filename>

# Reject a pending task
uv run digital-fte reject <task-filename>

# Show version
uv run digital-fte version
```

---

## Project Structure

```
digital-fte/
├── backend/                    # Python backend
│   ├── src/digital_fte/
│   │   ├── orchestrator.py     # Main brain (Ralph loop)
│   │   ├── config.py           # Settings
│   │   ├── models.py           # Pydantic models
│   │   ├── cli.py              # CLI interface
│   │   ├── watchers/
│   │   │   ├── gmail_watcher.py      # Gmail API integration
│   │   │   ├── whatsapp_watcher.py   # Playwright automation
│   │   │   └── filesystem_watcher.py # Vault monitoring
│   │   └── mcp/
│   │       ├── email_mcp.py    # Send emails
│   │       └── whatsapp_mcp.py # Send WhatsApp messages
│   └── .env                    # Configuration
│
├── frontend/                   # Next.js dashboard
│   └── src/
│       ├── app/                # Pages + API routes
│       └── components/         # Dashboard UI
│
├── AI_Employee_Valut/          # Obsidian vault (task storage)
│   ├── Needs_Action/           # New tasks
│   ├── Pending_Approval/       # Awaiting human review
│   ├── Approved/               # Ready to execute
│   ├── Done/                   # Completed
│   ├── Rejected/               # Declined tasks
│   ├── Company_Handbook.md     # Your operating rules
│   ├── Business_Goals.md       # KPIs and priorities
│   └── Logs/                   # Audit trail
│
├── .claude/skills/             # Claude Code skill definitions
├── CLAUDE.md                   # Project context for Claude
└── CHECKPOINT.md               # Development progress
```

---

## How the AI Decides

The AI reads two files before every decision:

### Company_Handbook.md

```markdown
## Email Response Protocol
- Client emails: respond within 4 hours
- Urgent (P0): respond within 1 hour

## Financial Authority
- Auto-approve: subscriptions < $20/month
- Always ask: anything > $50

## VIP Contacts
- Jane (CEO client) - always priority P0
```

### Business_Goals.md

```markdown
## Q1 2026 Targets
- Monthly revenue: $10,000
- Response time: < 4 hours
- Client satisfaction: 95%+
```

**Edit these files to customize AI behavior.**

---

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Gmail Read | ✅ Working | Detects new emails, creates tasks |
| Gmail Reply | ✅ Working | Sends replies via Gmail API |
| WhatsApp Read | ✅ Working | Detects unread messages |
| WhatsApp Reply | ✅ Implemented | Sends via Playwright (needs testing) |
| HITL Workflow | ✅ Working | Approve/reject via dashboard or CLI |
| CEO Briefing | ✅ Working | Weekly business reports |
| CEO Dashboard | ✅ Working | Real-time web UI at localhost:3000 |
| Audit Logging | ✅ Working | JSONL + Markdown logs |
| Auto-Approve | ✅ Working | High-confidence actions skip review |

---

## Customization

### Add VIP Contacts

Edit `AI_Employee_Valut/Company_Handbook.md`:

```markdown
## VIP Contacts (Always Priority P0)
- Alice Chen - key client
- Bob Smith - investor
```

### Change Auto-Approval Threshold

Edit `backend/.env`:

```env
HITL_CONFIDENCE_THRESHOLD=0.90  # Higher = more human review
```

### Disable a Watcher

```env
GMAIL_ENABLED=false
WHATSAPP_ENABLED=false
```

---

## Troubleshooting

### WhatsApp QR Code Not Showing

```bash
# Delete old session and restart
rm -rf backend/.whatsapp_session
uv run digital-fte start
```

### Gmail Auth Error

```bash
# Delete token and re-authorize
rm backend/token.pickle
uv run digital-fte start
```

### Dashboard Not Loading

```bash
# Check frontend is running
cd frontend
bun dev

# Check API routes work
curl http://localhost:3000/api/status
```

---

## Tech Stack

- **Backend:** Python 3.11, UV, Pydantic, Playwright
- **Frontend:** Next.js 14, React, Tailwind CSS, shadcn/ui
- **AI:** Claude Code CLI (Claude Pro subscription)
- **Storage:** Obsidian Vault (Markdown files)
- **APIs:** Gmail API, WhatsApp Web (Playwright)

---

## License

MIT License

---

## Acknowledgments

- Built for the Claude Code Digital FTE Hackathon
- Powered by Anthropic Claude
- Ralph Wiggum mascot inspired by The Simpsons

---

**Built with Claude Code**
