# Email Handler Skill

## Description
Handle email-related tasks including reading, drafting replies, and sending emails through the Gmail API integration.

## Instructions

When handling emails:

1. **For Incoming Emails (from /Needs_Action)**
   - Parse email metadata (from, subject, received date)
   - Check if sender is a VIP contact (see Company_Handbook.md)
   - Determine urgency based on keywords and sender
   - Draft appropriate response following handbook templates

2. **Response Guidelines (from Company Handbook)**
   - Client emails: Respond within 4 hours during business hours
   - VIP contacts: Respond within 1 hour
   - Use professional but warm tone
   - Always acknowledge their request
   - Provide clear next steps

3. **Email Templates**
   ```
   Subject: Re: [Original Subject]

   Hi [Name],

   Thank you for reaching out. [Acknowledgment of their request]

   [Specific response/answer]

   [Next steps if applicable]

   Best regards,
   [Your Name]
   ```

4. **Approval Requirements**
   - New contacts: Always require approval
   - Bulk emails: Always require approval
   - Sensitive topics (legal, financial): Always require approval
   - Known contacts with standard replies: Can auto-approve if confidence > 85%

5. **After Sending**
   - Log the action in audit trail
   - Move task to /Done
   - Update Dashboard.md

## Example Usage

```
Draft a reply to the email in AI_Employee_Valut/Needs_Action/EMAIL_123.md
```

## Tools Used
- Read (for email content)
- Write (for drafts)
- Bash (for sending via MCP/API)
