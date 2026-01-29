"""Invoice MCP server for generating PDF invoices."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..config import get_settings
from ..models import ProposedAction

logger = logging.getLogger(__name__)

# FPDF2 is imported lazily to allow graceful failure
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    FPDF = Any


class InvoicePDF(FPDF if FPDF_AVAILABLE else object):
    """Custom PDF class for invoices."""

    def __init__(self, company_name: str = "Your Company"):
        if not FPDF_AVAILABLE:
            raise RuntimeError("fpdf2 not installed. Install with: pip install fpdf2")
        super().__init__()
        self.company_name = company_name

    def header(self) -> None:
        """PDF header with company name."""
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.company_name, align="L", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 5, "Invoice", align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def footer(self) -> None:
        """PDF footer with page number."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


class InvoiceMCP:
    """MCP server for generating PDF invoices."""

    def __init__(self):
        self.settings = get_settings()
        self.logger = logger
        self.invoices_dir = self.settings.vault_path / "Invoices"

    async def initialize(self) -> None:
        """Initialize the Invoice MCP server."""
        if not FPDF_AVAILABLE:
            self.logger.warning(
                "fpdf2 not installed. Invoice generation disabled. "
                "Install with: pip install fpdf2"
            )
        else:
            self.logger.info("Invoice MCP initialized")

        # Create invoices directory if it doesn't exist
        self.invoices_dir.mkdir(parents=True, exist_ok=True)

    async def generate_invoice(
        self,
        client_name: str,
        client_email: str,
        items: list[dict[str, Any]],
        invoice_number: Optional[str] = None,
        notes: str = "",
        company_name: str = "Digital FTE Services",
    ) -> dict[str, Any]:
        """
        Generate a PDF invoice.

        Args:
            client_name: Name of the client
            client_email: Client's email address
            items: List of invoice items [{"description": str, "quantity": int, "unit_price": float}]
            invoice_number: Optional invoice number (auto-generated if not provided)
            notes: Additional notes to include
            company_name: Your company name

        Returns:
            dict with invoice_path, invoice_number, total_amount
        """
        if not FPDF_AVAILABLE:
            raise RuntimeError("fpdf2 not installed. Install with: pip install fpdf2")

        # Generate invoice number if not provided
        if not invoice_number:
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Create PDF
        pdf = InvoicePDF(company_name=company_name)
        pdf.alias_nb_pages()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Invoice details
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Invoice Number: {invoice_number}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Date: {datetime.now().strftime('%B %d, %Y')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Bill To section
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, "Bill To:", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, client_name, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, client_email, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        # Items table header
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(100, 8, "Description", border=1, fill=True)
        pdf.cell(25, 8, "Qty", border=1, align="C", fill=True)
        pdf.cell(30, 8, "Unit Price", border=1, align="R", fill=True)
        pdf.cell(35, 8, "Amount", border=1, align="R", fill=True, new_x="LMARGIN", new_y="NEXT")

        # Items
        pdf.set_font("Helvetica", "", 10)
        total = 0.0
        for item in items:
            description = item.get("description", "Item")
            quantity = item.get("quantity", 1)
            unit_price = float(item.get("unit_price", 0))
            amount = quantity * unit_price
            total += amount

            pdf.cell(100, 7, description[:50], border=1)
            pdf.cell(25, 7, str(quantity), border=1, align="C")
            pdf.cell(30, 7, f"${unit_price:.2f}", border=1, align="R")
            pdf.cell(35, 7, f"${amount:.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

        # Total
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(155, 10, "Total:", border=0, align="R")
        pdf.cell(35, 10, f"${total:.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

        # Notes
        if notes:
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 8, "Notes:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 5, notes)

        # Payment instructions
        pdf.ln(10)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 6, "Thank you for your business!", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, "Payment due within 30 days.", new_x="LMARGIN", new_y="NEXT")

        # Save PDF
        filename = f"{invoice_number}.pdf"
        filepath = self.invoices_dir / filename
        pdf.output(str(filepath))

        self.logger.info(f"Generated invoice: {filepath}")

        return {
            "invoice_path": str(filepath),
            "invoice_number": invoice_number,
            "total_amount": total,
            "client_name": client_name,
            "client_email": client_email,
        }

    async def execute_action(self, action: ProposedAction, task_context: dict) -> dict[str, Any]:
        """
        Execute an invoice generation action.

        Args:
            action: The proposed action to execute
            task_context: Original task context

        Returns:
            dict with invoice details including:
            - success: bool
            - invoice_path, invoice_number, total_amount
            - email_missing: bool (if client email not provided)
            - delivery_method: "email" | "whatsapp" | "manual"
        """
        action_type = action.action_type
        if hasattr(action_type, 'value'):
            action_type = action_type.value

        if action_type != "invoice_generate":
            self.logger.error(f"Invalid action type for InvoiceMCP: {action_type}")
            return {"success": False, "error": "Invalid action type"}

        try:
            action_data = action.action_data

            # Check for placeholder values that need human input
            placeholder_fields = []
            for field in ["amount", "client_email"]:
                value = action_data.get(field, "")
                if isinstance(value, str) and ("NEEDS_APPROVAL" in value.upper() or "REQUIRED" in value.upper()):
                    placeholder_fields.append(field)

            if placeholder_fields:
                missing = ", ".join(placeholder_fields)
                error_msg = (
                    f"Invoice cannot be generated: missing required values for [{missing}]. "
                    f"Please edit the task file in Pending_Approval to fill in the actual values, "
                    f"then move to Approved."
                )
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}

            # Get client info from action data or task context
            client_name = action_data.get("client_name") or task_context.get("contact_name", "Client")
            client_email = action_data.get("client_email") or task_context.get("from", "")

            # Check if email is missing
            email_missing = not client_email or "@" not in client_email

            # Determine delivery method
            source = task_context.get("source", "")
            send_via_email = action_data.get("send_via_email", True)
            send_via_whatsapp = action_data.get("send_via_whatsapp", False)

            # If email is missing and request came from WhatsApp, default to WhatsApp delivery
            if email_missing and source == "whatsapp":
                send_via_whatsapp = True
                send_via_email = False

            # Get items - either from action data or create a simple item
            items = action_data.get("items", [])
            if not items:
                # Create a default item based on amount
                amount = action_data.get("amount", 0)
                description = action_data.get("description", "Services rendered")
                items = [{"description": description, "quantity": 1, "unit_price": amount}]

            # Generate the invoice
            result = await self.generate_invoice(
                client_name=client_name,
                client_email=client_email if not email_missing else "N/A",
                items=items,
                invoice_number=action_data.get("invoice_number"),
                notes=action_data.get("notes", ""),
                company_name=action_data.get("company_name", "Digital FTE Services"),
            )

            result["success"] = True
            result["email_missing"] = email_missing

            # Determine delivery method
            if send_via_email and not email_missing:
                result["delivery_method"] = "email"
            elif send_via_whatsapp:
                result["delivery_method"] = "whatsapp"
                result["whatsapp_contact"] = task_context.get("contact_name", client_name)
            else:
                result["delivery_method"] = "manual"
                self.logger.warning(
                    f"Invoice {result['invoice_number']} generated but no delivery method available. "
                    f"Email missing: {email_missing}, WhatsApp: {send_via_whatsapp}"
                )
            self.logger.info(f"Successfully generated invoice for {client_name}")
            return result

        except Exception as e:
            self.logger.error(f"Failed to generate invoice: {e}")
            return {"success": False, "error": str(e)}

    async def health_check(self) -> bool:
        """Check if the Invoice MCP is healthy."""
        return FPDF_AVAILABLE and self.invoices_dir.exists()

    async def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Invoice MCP cleaned up")
