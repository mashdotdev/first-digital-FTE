# Digital FTE - Claude Code Agent Skills

## Overview

This Digital FTE (Full-Time Equivalent) is an autonomous AI employee that manages personal and business affairs using Claude Code as the executor and Obsidian as the management dashboard.

**Hackathon Tier:** Gold (with all Bronze and Silver features included)

## Available Skills

### Core Skills (Bronze Tier)

| Skill | File | Description |
|-------|------|-------------|
| task-processor | `skills/task-processor.md` | Process tasks from vault, analyze with context, propose actions |
| email-handler | `skills/email-handler.md` | Handle email reading, drafting, and sending |
| vault-manager | `skills/vault-manager.md` | Manage Obsidian vault structure and file organization |
| audit-logger | `skills/audit-logger.md` | Log all actions for accountability and learning |
| hitl-workflow | `skills/hitl-workflow.md` | Manage human-in-the-loop approval workflow |

### Communication Skills (Silver Tier)

| Skill | File | Description |
|-------|------|-------------|
| linkedin-poster | `skills/linkedin-poster.md` | Auto-post business content on LinkedIn for lead generation |
| whatsapp-handler | `skills/whatsapp-handler.md` | Monitor and respond to WhatsApp messages |
| plan-creator | `skills/plan-creator.md` | Create detailed Plan.md files for complex tasks |

### Social Media Skills (Gold Tier)

| Skill | File | Description |
|-------|------|-------------|
| facebook-manager | `skills/facebook-manager.md` | Post to Facebook and generate engagement summaries |
| instagram-manager | `skills/instagram-manager.md` | Post to Instagram and generate engagement summaries |
| twitter-manager | `skills/twitter-manager.md` | Post to Twitter/X and generate engagement summaries |

### Business Intelligence Skills (Gold Tier)

| Skill | File | Description |
|-------|------|-------------|
| ceo-briefing | `skills/ceo-briefing.md` | Generate weekly CEO briefings with business audit |
| odoo-integration | `skills/odoo-integration.md` | Manage accounting through Odoo ERP |

## Quick Start

To use a skill, invoke it by name:

```bash
# Core operations
/task-processor     # Process pending tasks
/email-handler      # Handle email tasks
/vault-manager      # Manage vault files

# Communication
/linkedin-poster    # Create LinkedIn content
/whatsapp-handler   # Process WhatsApp messages

# Social media
/facebook-manager   # Manage Facebook posts
/instagram-manager  # Manage Instagram posts
/twitter-manager    # Manage Twitter/X posts

# Business intelligence
/ceo-briefing       # Generate weekly business report
/odoo-integration   # Interact with Odoo ERP
```

## Architecture

```
External Sources
├── Gmail API
├── WhatsApp Web (Playwright)
├── LinkedIn API
├── Facebook Graph API
├── Instagram Graph API
├── Twitter API v2
└── Odoo JSON-RPC API

        ↓ Watchers detect events

Obsidian Vault (AI_Employee_Valut/)
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Tasks to process
├── In_Progress/        # Currently working
├── Pending_Approval/   # Human review needed
├── Approved/           # Ready to execute
├── Rejected/           # Learn from these
├── Done/               # Completed
├── Plans/              # Project plans
├── Briefings/          # CEO reports
├── Accounting/         # Financial data
├── Logs/               # Audit trail
├── Dashboard.md        # Real-time status
├── Company_Handbook.md # Operating rules
└── Business_Goals.md   # Strategic priorities

        ↓ Claude Code processes tasks

Skills Layer
├── task-processor      # Analyze & propose
├── email-handler       # Email operations
├── linkedin-poster     # LinkedIn posts
├── facebook-manager    # Facebook posts
├── instagram-manager   # Instagram posts
├── twitter-manager     # Twitter posts
├── ceo-briefing        # Weekly reports
└── odoo-integration    # ERP operations

        ↓ Actions require approval

HITL Workflow
├── Confidence > 85% → Auto-approve (if allowed)
├── Sensitive actions → Always require approval
└── Rejected → Log lesson learned

        ↓ Approved actions execute

MCP Servers
├── email_mcp       # Gmail API
├── browser_mcp     # Playwright automation
└── odoo_mcp        # Odoo JSON-RPC

        ↓ Results logged

Audit Trail
├── JSONL logs (machine readable)
├── Markdown logs (human readable)
└── Lessons_Learned.md (AI learning)
```

## Operating Rules

This agent operates under the rules defined in:
- `AI_Employee_Valut/Company_Handbook.md` - Operating procedures
- `AI_Employee_Valut/Business_Goals.md` - Strategic priorities

Always read these before making decisions.

## Safety Principles

1. **Never auto-approve:**
   - Payments (any amount)
   - New contact communications
   - Social media posts
   - File deletions

2. **Always log:**
   - Every action proposed
   - Every decision made
   - Every outcome

3. **Learn from mistakes:**
   - Update Lessons_Learned.md after rejections
   - Propose handbook updates for recurring issues

4. **When uncertain, ask:**
   - Use HITL workflow for ambiguous situations
   - Better to ask than to make mistakes

5. **Confidence threshold:**
   - Only auto-execute if confidence > 85%
   - Lower confidence = always require approval

## CLI Commands

```bash
digital-fte start           # Start the orchestrator
digital-fte status          # Show system status
digital-fte briefing        # Generate CEO briefing
digital-fte approve <task>  # Approve pending task
digital-fte reject <task>   # Reject pending task
digital-fte init            # Initialize new installation
digital-fte version         # Show version
```

## Tier Compliance

### Bronze Tier ✓
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher (filesystem)
- [x] Claude Code reading/writing to vault
- [x] Basic folder structure (/Inbox, /Needs_Action, /Done)
- [x] Agent Skills implemented

### Silver Tier ✓
- [x] All Bronze requirements
- [x] 2+ Watcher scripts (Gmail, WhatsApp, LinkedIn, Social Media)
- [x] LinkedIn auto-posting for sales
- [x] Plan.md file creation
- [x] MCP server for email
- [x] HITL approval workflow
- [x] Scheduling documentation

### Gold Tier ✓
- [x] All Silver requirements
- [x] Full cross-domain integration
- [x] Odoo Community integration (MCP)
- [x] Facebook/Instagram integration
- [x] Twitter (X) integration
- [x] Multiple MCP servers (Email, Browser, Odoo)
- [x] CEO Briefing generation
- [x] Error recovery & graceful degradation
- [x] Comprehensive audit logging
- [x] Ralph Wiggum loop
- [x] Documentation
