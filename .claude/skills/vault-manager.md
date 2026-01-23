# Vault Manager Skill

## Description
Manage the Obsidian vault structure, move files between folders, update the Dashboard, and maintain the organizational system.

## Vault Structure

```
AI_Employee_Valut/
├── Inbox/                  # Raw incoming items (manual drops)
├── Needs_Action/           # Tasks waiting to be processed
├── In_Progress/            # Currently being worked on
├── Pending_Approval/       # Awaiting human review
├── Approved/               # Human approved, ready to execute
├── Rejected/               # Human rejected, learn from it
├── Done/                   # Completed tasks
├── Plans/                  # Project plans and strategies
├── Briefings/              # CEO briefings and reports
├── Accounting/             # Financial tracking
├── People/                 # Contact/relationship history
├── Metrics/                # Performance metrics
├── Logs/                   # Audit logs and lessons learned
├── Dashboard.md            # Real-time status summary
├── Company_Handbook.md     # Operating rules
└── Business_Goals.md       # Strategic objectives
```

## Instructions

1. **Moving Tasks**
   - When starting work: Move from /Needs_Action to /In_Progress
   - When proposing action: Move to /Pending_Approval
   - When approved: Move from /Approved, execute, then to /Done
   - When rejected: Move to /Rejected, log lesson learned

2. **Dashboard Updates**
   - Update task counts in Dashboard.md after any file move
   - Add recent activity entries
   - Keep "Current Focus" section updated

3. **File Naming Conventions**
   - Emails: `EMAIL_[id]_[date].md`
   - WhatsApp: `WHATSAPP_[contact]_[date].md`
   - Approvals: `APPROVAL_[action]_[target]_[date].md`
   - Plans: `PLAN_[project]_[date].md`

4. **Metadata Format**
   All task files should have YAML frontmatter:
   ```yaml
   ---
   type: email|whatsapp|payment|task|social
   priority: P0|P1|P2|P3
   status: pending|in_progress|needs_approval|approved|rejected|done
   created: ISO-8601 timestamp
   from: sender (if applicable)
   ---
   ```

## Example Usage

```
Move the completed task EMAIL_123.md from /In_Progress to /Done and update Dashboard
```

## Tools Used
- Read (for file content)
- Write (for creating files)
- Edit (for updating files)
- Bash (for file operations)
