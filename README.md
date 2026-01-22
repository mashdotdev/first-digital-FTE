# Digital FTE - AI-Powered Full-Time Employee

> **"I'm helping!"** - Ralph Wiggum

A local-first, privacy-focused AI business assistant that acts as your digital employee. Built for the Claude Code Digital FTE Hackathon.

## 🎯 What Is This?

Digital FTE is an autonomous AI agent that:
- **Monitors** your Gmail, WhatsApp, and file system for new tasks
- **Proposes** actions based on your Company Handbook and Business Goals
- **Asks permission** before doing anything important (Human-in-the-Loop)
- **Executes** approved actions autonomously
- **Learns** from your corrections
- **Reports** weekly CEO briefings on business health

**Privacy-First:** All processing happens locally. Your data never leaves your machine except for Claude API calls.

---

## 🏆 Features (Gold Tier Target)

### ✅ Implemented

1. **Local Obsidian Vault Integration**
   - All tasks, approvals, and logs stored in markdown
   - Human-readable audit trail
   - Easy to review and modify

2. **Three Watchers**
   - 📧 **Gmail Watcher** - Monitors inbox for new emails
   - 📁 **Filesystem Watcher** - Detects approval/rejection actions
   - 📱 **WhatsApp Watcher** - (Placeholder - coming soon)

3. **Foundational Architecture**
   - `BaseWatcher` - Abstract class for all watchers
   - `Orchestrator` - Central coordinator
   - `AuditLogger` - Comprehensive audit logging
   - `Task/ProposedAction` models with Pydantic

4. **Human-in-the-Loop (HITL) Workflow**
   - AI proposes actions → human approves/rejects
   - Confidence-based auto-approval (configurable threshold)
   - Never auto-approves payments or social posts

5. **Ralph Wiggum Autonomous Loop**
   - Continuously processes `/Needs_Action` folder
   - Reads Company Handbook & Business Goals
   - Proposes actions with Claude
   - Executes or requests approval

6. **Company Context System**
   - `Company_Handbook.md` - Operating rules and decision authority
   - `Business_Goals.md` - Revenue targets, metrics, priorities
   - `Lessons_Learned.md` - AI learns from corrections

### 🚧 Next Steps

7. **MCP Server Integration**
   - Email MCP (send emails via Gmail)
   - Browser MCP (web automation)

8. **CEO Briefing Generation**
   - Monday morning business intelligence reports
   - Revenue tracking, task analysis, recommendations

9. **End-to-End Testing**
   - Real-world testing for 2+ weeks
   - Edge case handling
   - Production hardening

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [UV package manager](https://docs.astral.sh/uv/)
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Google Cloud project with Gmail API enabled (optional, for email)

### Installation

```bash
# Install dependencies
uv sync

# Initialize vault structure (if not already done)
uv run digital-fte init

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Gmail Setup (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to project root
6. Run the app - it will prompt for OAuth authorization on first run

### Run

```bash
# Start the Digital FTE
uv run digital-fte start

# Check status
uv run digital-fte status

# View help
uv run digital-fte --help
```

---

## 📁 Vault Structure

The Obsidian vault is organized as follows:

```
AI_Employee_Valut/
├── Company_Handbook.md      # Operating rules & decision authority
├── Business_Goals.md         # Revenue targets & KPIs
├── Dashboard.md              # Real-time system status
│
├── Needs_Action/             # New tasks to process
├── Pending_Approval/         # Awaiting human review
├── Approved/                 # Human approved → execute
├── Rejected/                 # Human rejected → learn from it
├── In_Progress/              # Currently being worked on
├── Done/                     # Completed tasks
│
├── Logs/                     # Audit logs
│   ├── audit_202601.jsonl    # Machine-readable audit trail
│   ├── daily_log_20260122.md # Human-readable daily summary
│   └── Lessons_Learned.md    # AI's learning journal
│
├── Briefings/                # CEO briefings
├── Accounting/               # Financial tracking
├── People/                   # Contact relationship history
└── Metrics/                  # Performance metrics
```

---

## 🧠 How It Works

### 1. Watchers Detect Events

- **Gmail Watcher** checks inbox every 60s for unread emails
- **Filesystem Watcher** monitors vault for file moves (approval workflow)
- Events → Tasks saved to `/Needs_Action`

### 2. Ralph Loop Processes Tasks

Every 5 minutes, Ralph:
1. Scans `/Needs_Action` for new tasks
2. Loads `Company_Handbook.md` + `Business_Goals.md`
3. Calls Claude with full context
4. Claude proposes an action with confidence score

### 3. Decision: Auto-Approve or HITL?

**Auto-approve if:**
- Confidence ≥ 0.85
- Handbook allows it
- No financial impact
- Not on "always ask" list (payments, social media)

**Otherwise:**
- Save proposed action to task file
- Move to `/Pending_Approval`
- Wait for human to move to `/Approved` or `/Rejected`

### 4. Execution

- If approved → Execute via MCP servers
- Log results to audit trail
- Move task to `/Done`
- Update Dashboard

### 5. Learning Loop

- Human corrections → Logged to `Lessons_Learned.md`
- AI proposes new handbook rules
- System improves over time

---

## 🔧 Configuration

Edit `.env` to customize behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | **Required** - Your Claude API key |
| `VAULT_PATH` | `AI_Employee_Valut` | Path to Obsidian vault |
| `GMAIL_ENABLED` | `true` | Enable Gmail monitoring |
| `RALPH_ENABLED` | `true` | Enable autonomous task processing |
| `HITL_CONFIDENCE_THRESHOLD` | `0.85` | Min confidence for auto-approval |
| `MAX_CONCURRENT_TASKS` | `3` | Parallel task limit |

See `.env.example` for all options.

---

## 📊 Monitoring

### Dashboard

Open `AI_Employee_Valut/Dashboard.md` in Obsidian to see:
- System health (which watchers are running)
- Task counts by status
- Recent activity

### Audit Logs

**Machine-readable:** `Logs/audit_YYYYMM.jsonl` (JSONL format)

**Human-readable:** `Logs/daily_log_YYYYMMDD.md` (generated automatically)

### CLI Status

```bash
uv run digital-fte status
```

Shows:
- Task counts per folder
- Enabled watchers
- Configuration summary

---

## 🎓 Customization

### Define Your Operating Rules

Edit `AI_Employee_Valut/Company_Handbook.md`:

```markdown
## Email Response Protocol
- Under 4 hours: All client emails
- Under 1 hour: P0/Urgent emails

## Financial Decision Authority
- Auto-approve: < $20/month subscriptions
- Always ask: Anything > $50

## VIP Contacts
- Alice (CEO) - Priority: P0
- Bob (Co-founder) - Priority: P0
```

The AI reads this **before every decision**.

### Set Business Goals

Edit `AI_Employee_Valut/Business_Goals.md`:

```markdown
## Q1 2026 Objectives
- Monthly revenue: $10,000
- Client response time: < 4 hours
- Active projects: 3-5
```

Claude uses this for **CEO Briefings** and **strategic decisions**.

---

## 🧪 Development

### Project Structure

```
digital-fte/
├── src/digital_fte/
│   ├── __init__.py
│   ├── config.py              # Settings management
│   ├── models.py              # Pydantic data models
│   ├── logger.py              # Audit logging
│   ├── base_watcher.py        # Base watcher class
│   ├── orchestrator.py        # Main coordinator
│   ├── cli.py                 # CLI interface
│   │
│   ├── watchers/
│   │   ├── gmail_watcher.py
│   │   ├── filesystem_watcher.py
│   │   └── whatsapp_watcher.py (TODO)
│   │
│   └── mcp/
│       ├── email_mcp.py       (TODO)
│       └── browser_mcp.py     (TODO)
│
├── AI_Employee_Valut/         # Obsidian vault
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy src/
```

---

## 🛣️ Roadmap

### Phase 1: Gold Tier (Current)
- ✅ Local Obsidian integration
- ✅ 3 watchers (Gmail, WhatsApp placeholder, Filesystem)
- ✅ HITL approval workflow
- ✅ Ralph Wiggum autonomous loop
- ✅ Company context system
- 🚧 2 MCP servers (Email, Browser)
- 🚧 CEO Briefing generation
- 📅 2+ weeks real-world testing

### Phase 2: Platinum (Future)
- ☁️ Cloud agent on Oracle Free Tier
- 🔄 Vault sync (Git-based)
- 🌐 24/7 operation (offline resilience)
- 📊 Odoo ERP integration
- 🔐 Enhanced security audit

### Phase 3: Polish
- 🎥 Demo video
- 📖 Comprehensive documentation
- 🎨 Obsidian theme/templates
- 📊 Metrics dashboard

---

## 📜 License

MIT License

---

## 🙏 Acknowledgments

- Built for the Claude Code Digital FTE Hackathon
- Powered by Anthropic Claude
- Inspired by the need for local-first, privacy-respecting AI automation

---

**Built with ❤️ and Claude Sonnet 4.5**
