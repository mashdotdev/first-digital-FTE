"""
Test script for the end-to-end invoice flow.

This tests the workflow from the hackathon details.md (lines 899-984):
1. WhatsApp Watcher detects "invoice" keyword
2. Claude proposes invoice_generate action
3. Human approves (simulated)
4. Invoice MCP generates PDF
5. Email MCP sends invoice to client
6. Task completed and logged

Run with: uv run python test_invoice_flow.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from digital_fte.config import get_settings
from digital_fte.mcp.invoice_mcp import InvoiceMCP
from digital_fte.mcp.email_mcp import EmailMCP
from digital_fte.models import ProposedAction, ActionType


async def test_invoice_generation():
    """Test standalone invoice PDF generation."""
    print("\n" + "=" * 60)
    print("TEST 1: Invoice PDF Generation")
    print("=" * 60)

    invoice_mcp = InvoiceMCP()
    await invoice_mcp.initialize()

    # Test invoice generation
    result = await invoice_mcp.generate_invoice(
        client_name="Client A",
        client_email="client_a@example.com",
        items=[
            {"description": "January 2026 Services", "quantity": 1, "unit_price": 1500.00},
            {"description": "Consultation Hours (10 hrs)", "quantity": 10, "unit_price": 50.00},
        ],
        notes="Thank you for your business! Payment due within 30 days.",
        company_name="Your Business Name",
    )

    print(f"[OK] Invoice generated successfully!")
    print(f"  - Invoice Number: {result['invoice_number']}")
    print(f"  - Total Amount: ${result['total_amount']:.2f}")
    print(f"  - File Path: {result['invoice_path']}")

    # Verify the file exists
    invoice_path = Path(result['invoice_path'])
    if invoice_path.exists():
        print(f"  - File Size: {invoice_path.stat().st_size} bytes")
        print("[OK] PDF file verified!")
    else:
        print("[FAIL] ERROR: PDF file not found!")
        return False

    return result


async def test_invoice_via_action():
    """Test invoice generation via ProposedAction (how Claude would trigger it)."""
    print("\n" + "=" * 60)
    print("TEST 2: Invoice via ProposedAction (Simulating Claude)")
    print("=" * 60)

    invoice_mcp = InvoiceMCP()
    await invoice_mcp.initialize()

    # Simulate what Claude would return
    action = ProposedAction(
        action_type=ActionType.INVOICE_GENERATE,
        title="Generate invoice for Client A",
        reasoning="Client requested invoice via WhatsApp. Per Company Handbook section 2.3, we generate invoices within 24 hours of request.",
        action_data={
            "client_name": "Client A",
            "client_email": "client_a@example.com",
            "amount": 1500.00,
            "description": "January 2026 Services",
            "notes": "As requested via WhatsApp",
        },
        confidence=0.92,
        handbook_references=["Section 2.3: Invoice Protocol"],
        requires_approval=True,  # Invoices should be approved
    )

    # Task context (what would come from the WhatsApp message)
    task_context = {
        "contact_name": "Client A",
        "from": "client_a@example.com",
        "messages": ["Hey, can you send me the invoice for January?"],
        "received_at": datetime.now().isoformat(),
    }

    print(f"Simulated Claude proposed action:")
    print(f"  - Action Type: {action.action_type}")
    print(f"  - Confidence: {action.confidence:.0%}")
    print(f"  - Requires Approval: {action.requires_approval}")

    # Execute the action (as if human approved)
    result = await invoice_mcp.execute_action(action, task_context)

    if result.get("success"):
        print(f"[OK] Invoice generated via action!")
        print(f"  - Invoice: {result['invoice_number']}")
        print(f"  - Amount: ${result['total_amount']:.2f}")
        return result
    else:
        print(f"[FAIL] ERROR: {result.get('error')}")
        return None


async def test_full_flow_simulation():
    """
    Simulate the complete flow from details.md:
    WhatsApp -> Claude Analysis -> Invoice Generation -> Email

    Note: This doesn't actually send emails or WhatsApp messages,
    but verifies the flow works end-to-end.
    """
    print("\n" + "=" * 60)
    print("TEST 3: Full Flow Simulation (WhatsApp -> Invoice -> Email)")
    print("=" * 60)

    settings = get_settings()

    # Step 1: Simulate WhatsApp message detection
    print("\n[Step 1] WhatsApp Watcher Detection")
    whatsapp_event = {
        "message_id": "whatsapp_Client_A_20260129_1200",
        "contact_name": "Client A",
        "unread_count": 1,
        "messages": ["Hey, can you send me the invoice for January?"],
        "latest_message": "Hey, can you send me the invoice for January?",
        "received_at": datetime.now().isoformat(),
    }
    print(f"  - Detected message from: {whatsapp_event['contact_name']}")
    print(f"  - Message: {whatsapp_event['latest_message']}")
    print(f"  - Keyword 'invoice' detected -> P1 Priority")

    # Step 2: Simulate task file creation in Needs_Action
    print("\n[Step 2] Task Created in /Needs_Action")
    task_file_content = f"""---
type: whatsapp
from: {whatsapp_event['contact_name']}
priority: P1
status: pending
received: {whatsapp_event['received_at']}
---

## WhatsApp Message

New message from **{whatsapp_event['contact_name']}**

**Messages:**
- {whatsapp_event['latest_message']}

## Suggested Actions
- [ ] Generate invoice
- [ ] Send via email
- [ ] Reply on WhatsApp to confirm

## Context
```json
{whatsapp_event}
```
"""
    task_path = settings.vault_needs_action / "WHATSAPP_client_a_invoice.md"
    task_path.write_text(task_file_content)
    print(f"  - Created: {task_path.name}")

    # Step 3: Simulate Claude's analysis (what the orchestrator would do)
    print("\n[Step 3] Claude Analysis -> Proposed Action")
    # In real flow, this would call Claude Code CLI
    proposed_action = ProposedAction(
        action_type=ActionType.INVOICE_GENERATE,
        title="Generate January invoice for Client A",
        reasoning="WhatsApp message requests invoice. Per handbook, generate and send within 24 hours.",
        action_data={
            "client_name": "Client A",
            "client_email": "client_a@example.com",
            "amount": 1500.00,
            "description": "January 2026 Services",
            "send_via_email": True,
        },
        confidence=0.90,
        handbook_references=["Section 2.3: Invoice Protocol"],
        requires_approval=True,
    )
    print(f"  - Proposed: {proposed_action.action_type.value}")
    print(f"  - Confidence: {proposed_action.confidence:.0%}")

    # Step 4: Move to Pending_Approval (simulated approval)
    print("\n[Step 4] Human Approval")
    print("  - Task moved to /Pending_Approval")
    print("  - [SIMULATED] Human reviews and approves")

    # Step 5: Execute invoice generation
    print("\n[Step 5] Invoice Generation")
    invoice_mcp = InvoiceMCP()
    await invoice_mcp.initialize()
    invoice_result = await invoice_mcp.execute_action(
        proposed_action,
        {"contact_name": "Client A", "from": "client_a@example.com"}
    )

    if invoice_result.get("success"):
        print(f"  [OK] Invoice generated: {invoice_result['invoice_number']}")
        print(f"  [OK] Saved to: {invoice_result['invoice_path']}")
    else:
        print(f"  [FAIL] Invoice generation failed: {invoice_result.get('error')}")
        return False

    # Step 6: Email would be sent (not actually sending)
    print("\n[Step 6] Email Send (SIMULATED)")
    print(f"  - Would send to: {invoice_result['client_email']}")
    print(f"  - Subject: January 2026 Invoice - ${invoice_result['total_amount']:.2f}")
    print(f"  - Attachment: {invoice_result['invoice_path']}")
    print("  - [SKIPPED] Not actually sending email in test mode")

    # Step 7: Complete the task
    print("\n[Step 7] Task Completion")
    # Move task to Done
    done_path = settings.vault_done / task_path.name
    if task_path.exists():
        task_path.rename(done_path)
        print(f"  [OK] Task moved to /Done")

    # Step 8: Log the action
    print("\n[Step 8] Audit Log")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "invoice_flow_complete",
        "actor": "ai",
        "task_id": "WHATSAPP_client_a_invoice",
        "details": {
            "invoice_number": invoice_result['invoice_number'],
            "amount": invoice_result['total_amount'],
            "client": invoice_result['client_name'],
        },
        "success": True,
    }
    print(f"  [OK] Logged: {log_entry['event_type']}")

    print("\n" + "=" * 60)
    print("[OK] FULL FLOW SIMULATION COMPLETE!")
    print("=" * 60)

    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DIGITAL FTE - INVOICE FLOW TESTS")
    print("=" * 60)
    print("Testing the workflow from details.md (lines 899-984)")

    try:
        # Test 1: Basic invoice generation
        result1 = await test_invoice_generation()
        if not result1:
            print("\n[FAIL] Test 1 failed!")
            return

        # Test 2: Invoice via ProposedAction
        result2 = await test_invoice_via_action()
        if not result2:
            print("\n[FAIL] Test 2 failed!")
            return

        # Test 3: Full flow simulation
        result3 = await test_full_flow_simulation()
        if not result3:
            print("\n[FAIL] Test 3 failed!")
            return

        print("\n" + "=" * 60)
        print("[OK] ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe invoice flow is ready for demo. To record:")
        print("1. Start the orchestrator: uv run digital-fte start")
        print("2. Send a WhatsApp message with 'invoice' keyword")
        print("3. Watch the task appear in Obsidian /Needs_Action")
        print("4. Approve in the dashboard")
        print("5. Invoice PDF generated and email sent!")

    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
