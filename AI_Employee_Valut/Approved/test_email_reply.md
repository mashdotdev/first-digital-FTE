# Task: Email Reply Request

**Source:** Manual Test
**Priority:** P2
**Created:** 2026-01-23

## Context

Received an email from a potential client asking about our services:

```
From: john.doe@example.com
Subject: Inquiry about your consulting services

Hi,

I came across your website and I'm interested in learning more about
your consulting services. Specifically, I need help with:
- Web application development
- API integration
- Database optimization

Could you provide information about your rates and availability?

Best regards,
John Doe
```

## Task

Draft a professional reply to this potential client. The email should:
- Thank them for their interest
- Briefly describe our expertise in the areas they mentioned
- Suggest a call to discuss their needs in detail
- Be warm and professional

## Notes

- This is a potential high-value client
- Respond within 4 hours (per Company Handbook)
- Make sure to highlight our strengths

---

## Proposed Action (Requires Approval)

**Action ID:** action_20260123_111726
**Type:** ActionType.EMAIL_SEND
**Confidence:** 95%

### Reasoning
This task aligns with our Q1 business goals to onboard new clients and maintain quick response times. The proposed action follows the 'Email Reply Template' from the Company Handbook (Section: Communication Templates) and addresses the client's specific interests. As per 'Prioritization Rules' (P1 for client inquiries) and 'Decision Authority Levels' (new contact requires approval), this reply is drafted for review to ensure alignment with all guidelines.

### Proposed Details
```json
{
  "recipient": "john.doe@example.com",
  "subject": "Re: Inquiry about your consulting services",
  "body": "Hi John,\n\nThank you for reaching out and for your interest in our consulting services! We appreciate you considering us for your needs.\n\nWe have extensive experience in the areas you mentioned, including web application development, robust API integration, and optimizing database performance to ensure efficiency and scalability. We're confident we can provide significant value in these areas.\n\nTo give you the most accurate information regarding rates and our current availability, it would be best to schedule a brief call. This will allow us to understand the specifics of your project requirements and discuss how our expertise can best support your goals.\n\nPlease let me know what time works best for you in the coming days, or feel free to suggest a few slots.\n\nBest regards,\n[Your Name]"
}
```

### Handbook References
- 1. Safety First
- 2. Communication Style
- 3. Prioritization Rules (P1)
- 4. Decision Authority Levels (Email Replies)
- Communication Templates (Email Reply Template)
- Prohibited Actions

---

**To approve:** Move this file to `/Approved`
**To reject:** Move this file to `/Rejected`
