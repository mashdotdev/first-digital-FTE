# Human-in-the-Loop Workflow Skill

## Description
Manage the approval workflow for sensitive actions that require human oversight before execution.

## Instructions

1. **When to Require Approval**
   - All payments (any amount)
   - New contact communications
   - Social media posts
   - File deletions
   - Actions with confidence < 85%
   - Anything flagged in Company_Handbook.md

2. **Creating Approval Requests**

   Create file in `/Pending_Approval/` with format:
   ```markdown
   ---
   type: approval_request
   action: email_send|payment|social_post|file_delete
   created: 2026-01-23T10:30:00Z
   expires: 2026-01-24T10:30:00Z
   status: pending
   confidence: 0.85
   ---

   # Approval Required: [Action Type]

   ## Summary
   [Brief description of what will happen]

   ## Details
   - Target: [recipient/destination]
   - Content: [what will be sent/done]
   - Reasoning: [why AI proposed this]

   ## Draft Content
   ```
   [The actual content to be sent/executed]
   ```

   ## Risk Assessment
   - Confidence: [X]%
   - Reversible: Yes/No
   - Financial Impact: $X

   ## To Approve
   Move this file to `/Approved/` folder

   ## To Reject
   Move this file to `/Rejected/` folder (optionally add rejection reason)
   ```

3. **Monitoring for Decisions**
   - Watch `/Approved/` folder for approved actions
   - Watch `/Rejected/` folder for rejections
   - Execute approved actions immediately
   - Log rejections and learn from them

4. **After Human Decision**
   - If approved: Execute action, log success, move to /Done
   - If rejected: Log rejection reason, update Lessons_Learned.md, move to /Done

5. **Expiration Handling**
   - If approval expires (24h default), notify and re-queue if still relevant
   - Never execute expired approvals

## Example Usage

```
Create an approval request for sending email to new client john@example.com
```

## Tools Used
- Write (for approval files)
- Read (for checking folders)
- Edit (for status updates)
