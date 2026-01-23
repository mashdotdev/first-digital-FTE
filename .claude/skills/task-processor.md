# Task Processor Skill

## Description
Process tasks from the Obsidian vault's /Needs_Action folder, analyze them using context from Company_Handbook.md and Business_Goals.md, and propose appropriate actions.

## Instructions

When processing tasks:

1. **Read Context First**
   - Always read `AI_Employee_Valut/Company_Handbook.md` for operating rules
   - Always read `AI_Employee_Valut/Business_Goals.md` for strategic priorities
   - Check `AI_Employee_Valut/Logs/Lessons_Learned.md` for past mistakes to avoid

2. **Analyze the Task**
   - Determine task type (email, payment, file operation, social media, etc.)
   - Assess priority using the P0-P3 scale from Company Handbook
   - Identify if this involves a VIP contact
   - Check if action requires human approval per handbook rules

3. **Propose Action**
   - Create a detailed action proposal with:
     - Action type
     - Confidence score (0-100%)
     - Reasoning referencing handbook/goals
     - Draft content if applicable
     - Whether approval is required

4. **Route Appropriately**
   - High confidence (>85%) + auto-approvable → Execute
   - Requires approval → Move to /Pending_Approval with proposal
   - Uncertain → Ask for clarification

5. **Always Log**
   - Record all decisions in audit log
   - Update Dashboard.md with status

## Example Usage

```
Process the task in AI_Employee_Valut/Needs_Action/EMAIL_client_inquiry.md
```

## Tools Used
- Read (for vault files)
- Write (for proposals and logs)
- Edit (for updating Dashboard)
