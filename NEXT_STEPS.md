# Next Steps - Quick Reference

**Last Updated:** 2026-01-22
**Current Status:** Foundation complete, ready for testing

---

## 🚀 Immediate Actions (Do This Now)

### 1. Install Dependencies (5 minutes)
```bash
cd A:\Desktop\first-digital-FTE
uv sync
```

### 2. Configure Environment (2 minutes)
```bash
# Copy example file
cp .env.example .env

# Edit .env and add:
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

Get your API key: https://console.anthropic.com/

### 3. Test CLI (1 minute)
```bash
# Check if everything installed correctly
uv run digital-fte --help
uv run digital-fte status
```

Expected: Should show vault status and configuration

### 4. First Run (Debug Session)
```bash
uv run digital-fte start
```

**Expected behavior:**
- Orchestrator initializes ✓
- Loads Company_Handbook.md ✓
- Loads Business_Goals.md ✓
- Filesystem watcher starts ✓
- Gmail watcher starts (will fail without OAuth - that's OK for now)
- Ralph loop begins running

**If you see errors:** That's normal! We'll fix them together.

---

## 🔧 Troubleshooting Common Issues

### ImportError: No module named 'digital_fte'
```bash
# Make sure you're in the project directory
cd A:\Desktop\first-digital-FTE

# Reinstall
uv sync
```

### Gmail Watcher Fails
**Expected!** Gmail needs OAuth setup:

1. Go to https://console.cloud.google.com/
2. Create new project: "Digital-FTE"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as `credentials.json`
6. Put in project root: `A:\Desktop\first-digital-FTE\credentials.json`
7. Restart the app - browser will open for authorization

### Anthropic API Error
```bash
# Check your .env file
cat .env

# Should see:
# ANTHROPIC_API_KEY=sk-ant-api...
```

### Vault Path Not Found
The vault should already exist at `A:\Desktop\first-digital-FTE\AI_Employee_Valut`

If missing:
```bash
uv run digital-fte init
```

---

## ✅ Success Criteria for First Run

You know it's working when:

1. **CLI responds without errors**
   ```bash
   uv run digital-fte status
   # Shows task counts, watcher status
   ```

2. **Dashboard updates**
   - Open `AI_Employee_Valut/Dashboard.md`
   - Should show current timestamp
   - Watcher status (green for running)

3. **Logs are created**
   - Check `AI_Employee_Valut/Logs/audit_202601.jsonl`
   - Should contain startup events

4. **Ralph loop is running**
   - Check terminal output
   - Should see: "Ralph found 0 tasks to process" (if no tasks yet)

---

## 🧪 Manual Testing Flow

### Test 1: Manual Task Creation

1. Create a file in `AI_Employee_Valut/Needs_Action/test_task.md`:

```markdown
# Test Email Reply

---
id: test_001
priority: P2
source: manual
---

## Description

Received email from client asking about pricing.

## Context

From: client@example.com
Subject: Pricing inquiry
```

2. Wait 5 minutes (or restart the app)
3. Ralph should process it
4. Check `AI_Employee_Valut/Pending_Approval/` for Claude's proposed action

### Test 2: Approval Workflow

1. After test 1, you should have a file in `/Pending_Approval`
2. Read Claude's proposed action
3. Move the file to `/Approved` (if you agree) or `/Rejected` (if not)
4. Filesystem watcher detects the move
5. Check logs for execution attempt

### Test 3: Gmail Detection (After OAuth)

1. Send yourself an email
2. Wait 60 seconds (Gmail poll interval)
3. Check `Needs_Action/` for new task
4. Verify email details captured correctly

---

## 📋 Phase 1 Checklist (Gold Tier)

Copy this to track your progress:

### Core System
- [x] Dependencies installed
- [x] .env configured
- [ ] CLI working
- [ ] Orchestrator starts successfully
- [ ] Vault structure validated

### Watchers
- [ ] Filesystem watcher running
- [ ] Gmail OAuth completed
- [ ] Gmail watcher running
- [ ] Manual task test passed
- [ ] Email detection test passed

### AI Processing
- [ ] Ralph loop processing tasks
- [ ] Claude API calls working
- [ ] Proposed actions generated
- [ ] HITL workflow tested
- [ ] Action execution attempted

### Monitoring
- [ ] Dashboard updating
- [ ] Audit logs being written
- [ ] No critical errors in logs
- [ ] Health checks passing

### Documentation
- [x] Company_Handbook.md customized for your use case
- [x] Business_Goals.md filled with your goals
- [ ] Test results documented

---

## 🎯 This Week's Goals

By end of this week, you should have:

1. ✅ **Fully working Gold tier core**
   - All 3 watchers functional
   - Ralph processing real tasks
   - Claude providing good suggestions
   - Approval workflow smooth

2. ✅ **MCP Servers Integrated**
   - Email MCP can send emails
   - Browser MCP can open/read pages

3. ✅ **Real Data Testing**
   - Processing actual emails
   - Making real decisions
   - Improving prompts based on results

4. ✅ **CEO Briefing v1**
   - Basic weekly report
   - Task summary
   - Time saved estimate

---

## 🆘 When You Need Help

**If stuck on technical issues:**
1. Check `AI_Employee_Valut/Logs/` for error details
2. Read CHECKPOINT.md for architecture context
3. Check README.md for setup instructions

**Common questions:**
- "What should Company_Handbook.md contain?" → Your actual business rules
- "How do I test without real emails?" → Use manual tasks in /Needs_Action
- "Is it normal for Gmail to fail at first?" → Yes! OAuth setup needed
- "How long should I run it before submitting?" → 2+ weeks minimum

---

## 📞 Quick Commands Reference

```bash
# Start the system
uv run digital-fte start

# Check status
uv run digital-fte status

# View logs
cat AI_Employee_Valut/Logs/audit_202601.jsonl

# Watch Ralph in action
tail -f AI_Employee_Valut/Logs/audit_202601.jsonl

# Stop (Ctrl+C in terminal)
```

---

## 🎬 Ready? Let's Go!

**Your next command:**
```bash
cd A:\Desktop\first-digital-FTE
uv sync
```

Then come back and tell me what you see!

---

**Remember:** You committed to dedicating your life to this. That mindset will build the BEST Digital FTE. Let's make it happen! 🚀
