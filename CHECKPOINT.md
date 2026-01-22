# Digital FTE - Development Checkpoint

**Date:** 2026-01-22
**Session:** Initial Build Phase
**Status:** Foundation Complete, Ready for Testing & MCP Integration

---

## 📋 Executive Summary

We are building **THE BEST Digital FTE** for the Claude Code hackathon. Strategy: Build **Gold tier first** as a safety net, then upgrade to **Platinum**.

### Strategic Decision: Why Gold → Platinum Approach

1. **Phase 1 (Weeks 1-2):** Build complete Gold tier system
   - This ensures we have a submittable project if time runs out
   - Validates core architecture before adding complexity

2. **Phase 2 (Weeks 3-4):** Add Platinum features
   - Cloud VM deployment (Oracle Free Tier)
   - Vault sync (Git-based)
   - 24/7 operation with offline resilience
   - Odoo ERP integration

3. **Phase 3 (Final Week):** Demo & Polish
   - Killer demo video showing offline resilience scenario
   - Documentation and submission

---

## ✅ Completed Work

### 1. Project Architecture & Setup

**Files Created:**
- `pyproject.toml` - Project configuration with all dependencies
- `.env.example` - Environment variable template
- `.gitignore` - Git ignore patterns
- `README.md` - Comprehensive project documentation

**Dependencies Added:**
- `anthropic` - Claude API client
- `watchdog` - Filesystem monitoring
- `google-api-python-client` - Gmail integration
- `playwright` - WhatsApp automation (future)
- `pydantic` - Data validation
- `typer` + `rich` - CLI interface
- `tenacity` - Retry logic
- Plus dev tools (pytest, ruff, mypy)

### 2. Obsidian Vault Structure

**Created in `AI_Employee_Valut/`:**

```
AI_Employee_Valut/
├── Company_Handbook.md        ✅ Comprehensive operating rules
├── Business_Goals.md           ✅ Revenue targets, KPIs, metrics
├── Dashboard.md                ✅ Real-time status display
│
├── Needs_Action/               ✅ New tasks to process
├── Pending_Approval/           ✅ Awaiting human review
├── Approved/                   ✅ Approved → execute
├── Rejected/                   ✅ Rejected → learn from it
├── In_Progress/                ✅ Currently working
├── Done/                       ✅ Completed
│
├── Logs/
│   └── Lessons_Learned.md      ✅ AI learning journal
│
├── Briefings/                  ✅ CEO reports
├── Accounting/                 ✅ Financial tracking
├── People/                     ✅ Relationship history
├── Metrics/                    ✅ Performance metrics
└── Plans/                      ✅ Project planning
```

**Key Documents:**

1. **Company_Handbook.md**
   - Email response protocols (4hr SLA for clients, 1hr for urgent)
   - Financial decision authority (auto-approve <$20, always ask >$50)
   - Priority tiers (P0/P1/P2/P3)
   - VIP contacts configuration
   - Communication templates
   - Prohibited actions (payments, deletions, etc.)
   - Error handling procedures
   - Success metrics

2. **Business_Goals.md**
   - Q1 2026 revenue targets ($30K quarterly)
   - Key metrics dashboard
   - Active projects tracking
   - Revenue streams
   - Client pipeline
   - Cost management rules
   - Subscription audit criteria
   - Weekly audit focus areas
   - Risk management

3. **Logs/Lessons_Learned.md**
   - Template for AI to document mistakes
   - Learning loop mechanism

### 3. Core Python Architecture

**Created in `src/digital_fte/`:**

#### `models.py` - Data Models
- `Priority` enum (P0, P1, P2, P3)
- `TaskStatus` enum (pending, in_progress, needs_approval, etc.)
- `ActionType` enum (email_reply, payment, file_operation, etc.)
- `Task` - Core task model with metadata
- `ProposedAction` - AI action proposals with confidence scores
- `WatcherEvent` - Events from watchers
- `AuditLog` - Audit trail entries
- `WatcherConfig` - Watcher configuration
- `SystemHealth` - Health monitoring

#### `config.py` - Configuration Management
- `Settings` class with pydantic-settings
- Environment variable loading from `.env`
- All configurable parameters:
  - API keys (Anthropic, Google)
  - Vault paths with helper properties
  - Watcher enable/disable flags
  - Poll intervals
  - HITL confidence threshold (0.85 default)
  - Ralph loop settings
  - CEO briefing schedule
  - Logging configuration
  - Retry logic parameters
- `validate_vault_structure()` method

#### `logger.py` - Audit Logging
- `AuditLogger` class
- JSONL format for machine readability (`audit_YYYYMM.jsonl`)
- Markdown format for humans (`daily_log_YYYYMMDD.md`)
- Methods for all event types:
  - `log_task_created()`
  - `log_action_proposed()`
  - `log_human_decision()`
  - `log_action_executed()`
  - `log_watcher_event()`
  - `log_error()`
  - `log_health_check()`
- `create_human_readable_log()` - Daily summaries

#### `base_watcher.py` - Abstract Watcher Base Class
- Async architecture
- Lifecycle management (initialize, start, stop, cleanup)
- `check_for_events()` abstract method
- `event_to_task()` abstract method
- `calculate_priority()` abstract method
- Built-in error handling with retry logic (tenacity)
- Exponential backoff on failures
- Auto-stop after max retry attempts
- Task-to-markdown conversion
- Vault integration (saves tasks to folders)

#### `orchestrator.py` - Central Coordinator
**Key Responsibilities:**
1. **Watcher Management**
   - Register and start/stop watchers
   - Monitor health

2. **Ralph Wiggum Loop** (Autonomous Processing)
   - Every 5 minutes (configurable)
   - Scans `/Needs_Action` folder
   - Loads Company Handbook + Business Goals
   - Calls Claude with full context
   - Parses JSON response into `ProposedAction`
   - Decides: auto-approve or HITL?
   - Executes or moves to `/Pending_Approval`

3. **HITL Decision Logic**
   - Auto-approve IF:
     - `requires_approval: false` in Claude response
     - Confidence >= 0.85 threshold
     - Not in "never auto" list (payment, social_post)
   - Otherwise: Require human approval

4. **Health Monitoring**
   - Periodic health checks
   - Updates Dashboard.md
   - Tracks task counts
   - Monitors watcher status

5. **System Prompt Builder**
   - Injects Company Handbook
   - Injects Business Goals
   - Provides JSON response format
   - Defines decision rules for Claude

#### `cli.py` - Command-Line Interface
Commands:
- `digital-fte start` - Start orchestrator
- `digital-fte status` - Show system status
- `digital-fte init` - Initialize new installation
- `digital-fte version` - Show version

Features:
- Rich console output with colors/tables
- Logging configuration
- Async orchestrator runner

### 4. Watcher Implementations

#### `watchers/gmail_watcher.py` - Gmail Integration
- Google OAuth 2.0 authentication
- Token persistence (`.google_token.json`)
- Polls for unread emails (60s default)
- Extracts email metadata (subject, from, snippet)
- Priority detection (urgent keywords → P0)
- Methods:
  - `send_email()` - Send via Gmail API
  - `mark_as_read()` - Mark processed emails
- Creates tasks in `/Needs_Action`

#### `watchers/filesystem_watcher.py` - Vault Monitoring
- Uses `watchdog` library
- Monitors entire vault for file changes
- Detects:
  - File creation in `/Needs_Action` (manual tasks)
  - File moves to `/Approved` (execute action)
  - File moves to `/Rejected` (learn from it)
- Async event queue for thread-safe processing
- Only creates tasks for relevant events

---

## 🚧 Current Status

### What Works Right Now

1. ✅ **Complete vault structure** with all folders
2. ✅ **Comprehensive context documents** (Handbook, Goals)
3. ✅ **Full data model** with Pydantic validation
4. ✅ **Configuration system** with environment variables
5. ✅ **Audit logging** (JSONL + markdown)
6. ✅ **Base watcher architecture** with error handling
7. ✅ **Two working watchers** (Gmail, Filesystem)
8. ✅ **Orchestrator** with Ralph loop and HITL
9. ✅ **CLI interface** with status/init commands

### What Needs Testing

- Dependencies not yet installed (`uv sync` needs to run)
- No end-to-end test yet
- Gmail OAuth flow not tested
- Claude API integration not tested
- File system events not tested in practice

---

## 📝 Next Steps (Prioritized)

### Immediate (This Session)

1. **Install Dependencies**
   ```bash
   cd A:\Desktop\first-digital-FTE
   uv sync
   ```

2. **Create .env File**
   ```bash
   cp .env.example .env
   # Add ANTHROPIC_API_KEY
   ```

3. **Test CLI**
   ```bash
   uv run digital-fte --help
   uv run digital-fte status
   ```

4. **First Run Test**
   ```bash
   uv run digital-fte start
   # Should start orchestrator (will fail on Gmail auth, that's OK)
   ```

### Short Term (Next 1-2 Days)

5. **Gmail OAuth Setup**
   - Create Google Cloud project
   - Enable Gmail API
   - Download credentials.json
   - Complete OAuth flow
   - Test email detection

6. **Create Test Tasks Manually**
   - Add test task to `/Needs_Action`
   - Watch Ralph process it
   - Verify Claude API call works
   - Test approval workflow

7. **Fix Import Issues**
   - The orchestrator imports watchers - may need `__init__.py` files
   - Test actual imports

8. **Add Missing MCP Integration Stubs**
   - Create `src/digital_fte/mcp/` folder
   - Create `email_mcp.py` stub
   - Orchestrator calls these when executing actions

### Medium Term (Week 1-2)

9. **MCP Server Implementation**
   - Email MCP (send emails via Gmail watcher)
   - Browser MCP (Playwright automation)

10. **CEO Briefing Generator**
    - Create `briefing_generator.py`
    - Cron-like scheduler (Monday 6 AM)
    - Analyze logs, tasks, Business Goals
    - Generate markdown report in `/Briefings`

11. **WhatsApp Watcher**
    - Playwright automation for WhatsApp Web
    - Session persistence
    - Message detection
    - Reply drafting

12. **Robust Error Handling**
    - Test failure scenarios
    - Improve retry logic
    - Better error messages in vault

13. **Real-World Testing**
    - Run for 2+ weeks continuously
    - Handle real emails
    - Fix edge cases
    - Improve prompts based on actual behavior

### Long Term (Week 3-4 - Platinum)

14. **Cloud VM Setup**
    - Oracle Free Tier account
    - Ubuntu server setup
    - Install dependencies
    - Configure systemd service

15. **Vault Sync**
    - Git-based sync (Local ↔ Cloud)
    - Conflict resolution
    - Auto-commit/push/pull

16. **Cloud Agent**
    - Read-only vault access
    - Draft-only mode (no execution)
    - Writes to `/Pending_Approval`
    - Local agent executes when online

17. **Odoo Integration**
    - MCP for Odoo API
    - Financial tracking
    - Invoice generation
    - Customer relationship data

### Polish (Final Week)

18. **Demo Video**
    - Scenario: Email arrives while offline
    - Cloud drafts reply
    - User approves when back online
    - Local executes

19. **Documentation**
    - Architecture diagrams
    - Setup guide with screenshots
    - Troubleshooting guide

20. **Metrics Dashboard**
    - Obsidian Dataview plugin
    - Live metrics in vault
    - Time saved calculator

---

## 🎯 Success Criteria for Gold Tier

- [ ] 3 watchers running (Gmail ✅, WhatsApp 🚧, Filesystem ✅)
- [ ] 2 MCP servers (Email 🚧, Browser 🚧)
- [ ] HITL workflow functional ✅ (built, not tested)
- [ ] Ralph loop processes tasks ✅ (built, not tested)
- [ ] CEO Briefing generates 🚧
- [ ] 2+ weeks real-world testing 📅
- [ ] Comprehensive docs ✅
- [ ] Demo video 📅

**Current Progress: ~60% complete**

---

## 🔑 Key Design Decisions Made

### 1. Local-First Architecture
- All sensitive data stays on user's machine
- Only Claude API calls leave localhost
- Obsidian vault is single source of truth

### 2. Human-in-the-Loop Safety
- Never auto-approve payments, social posts
- Confidence threshold: 0.85
- Explicit approval via file moves (intuitive for non-coders)

### 3. Markdown-Based Task System
- Human-readable audit trail
- Easy debugging
- Works with any text editor (not just Obsidian)
- Version control friendly

### 4. Context-Driven AI
- Company Handbook defines operating rules
- Business Goals provide strategic direction
- Claude reads these BEFORE every decision
- Learning loop improves over time

### 5. Ralph Wiggum Philosophy
- "I'm helping!" - Well-intentioned but needs supervision
- Proposes actions, doesn't assume
- When uncertain, asks for help
- Gets smarter from corrections

### 6. Async Architecture
- All watchers run concurrently
- Non-blocking I/O
- Scales to many watchers

### 7. Pydantic for Everything
- Type safety
- Validation at runtime
- Auto-generated JSON schemas
- Environment variable parsing

---

## 🐛 Known Issues / Technical Debt

1. **Import Paths**
   - Need to verify `from .watchers.gmail_watcher import GmailWatcher` works
   - May need `__init__.py` adjustments

2. **MCP Integration**
   - Orchestrator references MCP servers that don't exist yet
   - `_execute_action()` is a stub

3. **CEO Briefing**
   - Not implemented yet
   - Needs cron-like scheduler

4. **WhatsApp Watcher**
   - Placeholder only
   - Playwright implementation needed

5. **Error Recovery**
   - No recovery from partial failures
   - Task status not persisted if crash occurs

6. **Testing**
   - No unit tests yet
   - No integration tests
   - No CI/CD

---

## 💡 Competitive Advantages (Why We'll Win)

### 1. Production-Grade Reliability
Most hackathon projects demo well but break in real use. We're building for continuous operation with:
- Comprehensive error handling
- Retry logic with exponential backoff
- Health monitoring
- Graceful degradation

### 2. Obsessive Audit Trail
Every action logged in both:
- Machine format (JSONL for analysis)
- Human format (Markdown for review)
- Makes debugging and trust-building easy

### 3. Learning Loop
`Lessons_Learned.md` grows over time:
- AI documents its mistakes
- Human provides corrections
- System proposes new handbook rules
- Shows improvement over time (key demo point)

### 4. Business Intelligence
CEO Briefing isn't just reporting - it's strategic insights:
- Which clients are high-value but high-maintenance?
- Where is time being wasted?
- Cash flow predictions
- Proactive risk identification

### 5. Platinum's Killer Feature (If We Get There)
The offline resilience scenario is **compelling**:
- Cloud agent works 24/7
- Local agent has full execution power
- User approves from anywhere
- Demonstrates true "employee" behavior

---

## 📞 How to Resume This Session

### Quick Context Refresh

**What we're building:** Digital FTE for Claude Code hackathon

**Current phase:** Gold tier foundation (60% complete)

**Strategy:** Build Gold first (safety net), then Platinum

**Next immediate steps:**
1. Run `uv sync` to install dependencies
2. Create `.env` with ANTHROPIC_API_KEY
3. Test CLI: `uv run digital-fte status`
4. First run: `uv run digital-fte start`
5. Fix any import errors
6. Set up Gmail OAuth
7. Create test task and watch Ralph process it

**Key files to know:**
- `src/digital_fte/orchestrator.py` - The brain
- `src/digital_fte/base_watcher.py` - Watcher template
- `AI_Employee_Valut/Company_Handbook.md` - AI's rulebook
- `AI_Employee_Valut/Business_Goals.md` - Strategic context

**Architecture:** Watchers → Tasks → Ralph → Claude → HITL → Execute → Audit

**User's mindset:** "Dedicated my whole life to this" - high commitment, go deep

---

## 🎬 Demo Scenario (For Final Submission)

### Gold Tier Demo

**Title:** "Your AI Employee That Never Sleeps (Locally)"

**Scenario:**
1. Show inbox with client email: "Need proposal by EOD"
2. Gmail watcher detects it → Creates task
3. Ralph loop picks it up
4. Claude reads handbook, proposes draft reply
5. Task moves to `/Pending_Approval`
6. Human reviews in Obsidian, approves
7. Email sends automatically
8. Audit log shows entire trail
9. Dashboard updates

**Highlight:** Show `Lessons_Learned.md` with previous corrections

### Platinum Demo (If We Get There)

**Title:** "The Offline Business Owner"

**Scenario:**
1. Client emails at 2 AM (user sleeping, laptop closed)
2. Cloud agent detects, drafts reply
3. Syncs to vault's `/Pending_Approval`
4. User wakes at 8 AM, opens laptop
5. Dashboard shows pending task
6. User reviews, moves to `/Approved`
7. Local agent sends email via Gmail
8. Cloud logs completion

**Highlight:** System worked while user was offline - true FTE behavior

---

## 📚 Resources & Links

- **Claude API:** https://docs.anthropic.com/claude/reference
- **Gmail API:** https://developers.google.com/gmail/api
- **Google Cloud Console:** https://console.cloud.google.com/
- **Playwright:** https://playwright.dev/python/
- **Obsidian:** https://obsidian.md/
- **UV Package Manager:** https://docs.astral.sh/uv/
- **Hackathon Details:** See `details.md`

---

## 🔄 Version History

- **2026-01-22:** Initial foundation complete
  - Architecture designed
  - Core components built
  - Vault structure created
  - Documentation written
  - Ready for testing phase

---

**Resume Command for Claude:**

"Continue building Digital FTE from CHECKPOINT.md. We're at 60% Gold tier completion. Next: install dependencies and run first tests."

