# Audit Logger Skill

## Description
Log all AI actions, decisions, and outcomes for accountability and learning. Maintains both machine-readable (JSONL) and human-readable (Markdown) formats.

## Instructions

1. **What to Log**
   - Every task processed
   - Every action proposed
   - Every human decision (approve/reject)
   - Every action executed
   - All errors and failures
   - Health checks

2. **Log Formats**

   **JSONL Format** (in `Logs/audit_YYYYMM.jsonl`):
   ```json
   {
     "timestamp": "2026-01-23T10:30:00Z",
     "event_type": "action_proposed|action_executed|human_decision|error",
     "task_id": "EMAIL_123",
     "action_type": "email_reply",
     "actor": "digital_fte",
     "confidence": 0.92,
     "requires_approval": true,
     "result": "pending_approval|success|failed",
     "details": {}
   }
   ```

   **Markdown Format** (in `Logs/daily_log_YYYYMMDD.md`):
   ```markdown
   ## 2026-01-23 Activity Log

   ### 10:30 - Email Reply Proposed
   - Task: EMAIL_123
   - Action: Draft reply to client@example.com
   - Confidence: 92%
   - Status: Awaiting approval

   ### 10:45 - Email Approved & Sent
   - Task: EMAIL_123
   - Approved by: Human
   - Result: Success
   ```

3. **Lessons Learned**
   When a task is rejected or fails:
   - Document what went wrong in `Logs/Lessons_Learned.md`
   - Extract the lesson for future reference
   - Suggest handbook updates if pattern emerges

4. **Log Retention**
   - Keep JSONL logs for 90+ days
   - Archive monthly summaries
   - Never delete audit trails

## Example Usage

```
Log the successful execution of EMAIL_123 email send
```

## Tools Used
- Write (for log entries)
- Edit (for appending to logs)
- Read (for checking existing logs)
