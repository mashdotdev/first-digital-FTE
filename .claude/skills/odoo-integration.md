# Odoo ERP Integration Skill

## Description
Integrate with Odoo Community Edition for accounting, invoicing, and business management through the JSON-RPC API.

## Instructions

### 1. Odoo Capabilities

**Accounting:**
- Chart of accounts management
- Journal entries
- Bank reconciliation
- Financial reports

**Invoicing:**
- Create customer invoices
- Track payment status
- Send invoice reminders
- Generate statements

**Contacts:**
- Customer/vendor management
- Contact history
- Credit limits

**Inventory (if applicable):**
- Stock levels
- Product management
- Purchase orders

### 2. Authentication

Odoo uses XML-RPC and JSON-RPC APIs:

```python
# JSON-RPC Authentication
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "authenticate",
        "args": [
            "database_name",
            "username",
            "password",
            {}
        ]
    }
}
```

**Required Credentials (in .env):**
```
ODOO_URL=http://localhost:8069
ODOO_DB=mycompany
ODOO_USER=admin
ODOO_PASSWORD=secure_password
```

### 3. Common Operations

**Create Invoice:**
```python
# Create draft invoice
invoice = {
    "partner_id": customer_id,
    "move_type": "out_invoice",
    "invoice_line_ids": [
        (0, 0, {
            "name": "Service description",
            "quantity": 1,
            "price_unit": 500.00,
        })
    ]
}
```

**Get Account Balances:**
```python
# Read account balances
accounts = execute_kw(
    db, uid, password,
    'account.account', 'search_read',
    [[['account_type', 'in', ['asset_receivable', 'liability_payable']]]],
    {'fields': ['name', 'balance']}
)
```

**Get Unpaid Invoices:**
```python
# Find unpaid invoices
unpaid = execute_kw(
    db, uid, password,
    'account.move', 'search_read',
    [[
        ['move_type', '=', 'out_invoice'],
        ['payment_state', '!=', 'paid'],
        ['state', '=', 'posted']
    ]],
    {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date_due']}
)
```

### 4. Workflow Integration

**Weekly Accounting Audit:**

1. **Pull Data from Odoo**
   - Current receivables
   - Overdue invoices
   - Recent transactions
   - Bank balance

2. **Create Summary**
   ```markdown
   ## Odoo Accounting Summary

   ### Receivables
   - Total outstanding: $XX,XXX
   - Overdue (>30 days): $X,XXX

   ### Recent Transactions
   | Date | Description | Amount |
   |------|-------------|--------|
   | ... | ... | ... |

   ### Action Items
   - [ ] Follow up on Invoice #XXX (45 days overdue)
   - [ ] Reconcile bank transactions
   ```

3. **Include in CEO Briefing**

### 5. Approval Workflow

**For Creating Invoices:**
```markdown
---
type: approval_request
action: odoo_invoice
status: draft
---

# Invoice Creation Approval

## Customer
[Customer name]

## Line Items
| Description | Qty | Unit Price | Total |
|-------------|-----|------------|-------|
| [Service] | 1 | $500.00 | $500.00 |

## Total: $500.00

## To Approve
Move to /Approved to create invoice in Odoo
```

**For Posting Invoices:**
- Draft invoices can be created automatically
- ALWAYS require approval before posting (making official)
- ALWAYS require approval for payments

### 6. MCP Integration

The Odoo MCP server provides these tools:

```typescript
// Available MCP Tools
tools: [
    {
        name: "odoo_create_invoice",
        description: "Create a draft invoice in Odoo",
        inputSchema: {...}
    },
    {
        name: "odoo_get_receivables",
        description: "Get current accounts receivable",
        inputSchema: {...}
    },
    {
        name: "odoo_get_payables",
        description: "Get current accounts payable",
        inputSchema: {...}
    },
    {
        name: "odoo_search_partners",
        description: "Search customers/vendors",
        inputSchema: {...}
    },
    {
        name: "odoo_get_financial_report",
        description: "Generate financial report",
        inputSchema: {...}
    }
]
```

### 7. Data Sync to Vault

Keep local copies in Obsidian for offline access:

```
AI_Employee_Valut/
└── Accounting/
    ├── Current_Month.md      # Transaction summary
    ├── Receivables.md        # Outstanding invoices
    ├── Payables.md           # Bills to pay
    └── Reports/
        └── 2026-01_Summary.md
```

**Sync Frequency:**
- Receivables: Every 4 hours
- Transactions: Daily
- Full sync: Weekly

### 8. Safety Rules

- NEVER auto-post invoices (always draft first)
- NEVER auto-process payments
- NEVER delete accounting records
- All financial actions require HITL approval
- Keep audit trail of all Odoo operations
- Validate data before creating records

### 9. Error Handling

**Common Issues:**
- Connection timeout: Retry with exponential backoff
- Authentication failure: Alert human, pause operations
- Validation error: Log details, don't retry blindly
- Duplicate record: Check existing before creating

## Example Usage

```
Create a draft invoice in Odoo for Client ABC for $1,500 consulting services
```

```
Get all unpaid invoices older than 30 days from Odoo
```

```
Generate a financial summary from Odoo for the CEO briefing
```

## Tools Used
- Bash (for JSON-RPC API calls)
- Read/Write (for vault sync)
- MCP Odoo server (when available)
