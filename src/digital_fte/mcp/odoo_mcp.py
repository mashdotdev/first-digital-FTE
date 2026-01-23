"""
Odoo MCP Server for Digital FTE

Provides integration with Odoo Community Edition via JSON-RPC API
for accounting, invoicing, and business management operations.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


class OdooMCP:
    """
    MCP Server for Odoo ERP integration.

    Provides tools for:
    - Invoice management (create, read, update)
    - Accounts receivable/payable queries
    - Financial reporting
    - Contact management
    """

    def __init__(
        self,
        url: str,
        database: str,
        username: str,
        password: str,
        dry_run: bool = True,
    ):
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password
        self.dry_run = dry_run
        self.uid: Optional[int] = None
        self._request_id = 0

    def _json_rpc(self, endpoint: str, method: str, params: list) -> Any:
        """Execute a JSON-RPC call to Odoo."""
        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": endpoint,
                "method": method,
                "args": params,
            },
            "id": self._request_id,
        }

        data = json.dumps(payload).encode('utf-8')
        request = Request(
            f"{self.url}/jsonrpc",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))

            if result.get("error"):
                error = result["error"]
                raise Exception(f"Odoo error: {error.get('message', error)}")

            return result.get("result")

        except (URLError, HTTPError) as e:
            logger.error(f"Odoo connection error: {e}")
            raise

    def authenticate(self) -> bool:
        """Authenticate with Odoo and store user ID."""
        try:
            self.uid = self._json_rpc(
                "common",
                "authenticate",
                [self.database, self.username, self.password, {}]
            )

            if self.uid:
                logger.info(f"Authenticated with Odoo as user ID: {self.uid}")
                return True
            else:
                logger.error("Odoo authentication failed")
                return False

        except Exception as e:
            logger.error(f"Odoo authentication error: {e}")
            return False

    def _execute_kw(
        self,
        model: str,
        method: str,
        args: list,
        kwargs: Optional[dict] = None,
    ) -> Any:
        """Execute a model method via JSON-RPC."""
        if self.uid is None:
            if not self.authenticate():
                raise Exception("Not authenticated with Odoo")

        return self._json_rpc(
            "object",
            "execute_kw",
            [
                self.database,
                self.uid,
                self.password,
                model,
                method,
                args,
                kwargs or {},
            ]
        )

    # ============ Invoice Operations ============

    def create_invoice(
        self,
        partner_id: int,
        lines: list[dict],
        invoice_date: Optional[str] = None,
    ) -> dict:
        """
        Create a draft invoice in Odoo.

        Args:
            partner_id: Customer ID in Odoo
            lines: List of invoice lines with description, quantity, price_unit
            invoice_date: Optional invoice date (defaults to today)

        Returns:
            Dict with invoice details
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create invoice for partner {partner_id}")
            return {
                "status": "dry_run",
                "partner_id": partner_id,
                "lines": lines,
                "timestamp": datetime.now().isoformat(),
            }

        invoice_lines = [
            (0, 0, {
                "name": line.get("description", "Service"),
                "quantity": line.get("quantity", 1),
                "price_unit": line.get("price_unit", 0),
            })
            for line in lines
        ]

        vals = {
            "partner_id": partner_id,
            "move_type": "out_invoice",
            "invoice_line_ids": invoice_lines,
        }

        if invoice_date:
            vals["invoice_date"] = invoice_date

        invoice_id = self._execute_kw("account.move", "create", [vals])

        # Fetch the created invoice
        invoice = self._execute_kw(
            "account.move",
            "read",
            [[invoice_id]],
            {"fields": ["name", "partner_id", "amount_total", "state"]}
        )

        logger.info(f"Created invoice {invoice[0]['name']}")
        return invoice[0]

    def get_unpaid_invoices(
        self,
        days_overdue: int = 0,
    ) -> list[dict]:
        """Get all unpaid invoices, optionally filtered by days overdue."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fetch unpaid invoices")
            return [{
                "status": "dry_run",
                "message": "Would return unpaid invoices",
                "timestamp": datetime.now().isoformat(),
            }]

        domain = [
            ("move_type", "=", "out_invoice"),
            ("payment_state", "!=", "paid"),
            ("state", "=", "posted"),
        ]

        if days_overdue > 0:
            from datetime import timedelta
            cutoff = (datetime.now() - timedelta(days=days_overdue)).strftime("%Y-%m-%d")
            domain.append(("invoice_date_due", "<", cutoff))

        invoices = self._execute_kw(
            "account.move",
            "search_read",
            [domain],
            {
                "fields": [
                    "name", "partner_id", "amount_total",
                    "amount_residual", "invoice_date", "invoice_date_due"
                ]
            }
        )

        return invoices

    # ============ Financial Reports ============

    def get_receivables_summary(self) -> dict:
        """Get accounts receivable summary."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fetch receivables summary")
            return {
                "status": "dry_run",
                "total_receivable": 0,
                "overdue_amount": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # Get all posted customer invoices
        invoices = self._execute_kw(
            "account.move",
            "search_read",
            [[
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
            ]],
            {"fields": ["amount_total", "amount_residual", "payment_state", "invoice_date_due"]}
        )

        total = sum(inv["amount_residual"] for inv in invoices)
        overdue = sum(
            inv["amount_residual"] for inv in invoices
            if inv["invoice_date_due"] and inv["invoice_date_due"] < datetime.now().strftime("%Y-%m-%d")
        )

        return {
            "total_receivable": total,
            "overdue_amount": overdue,
            "invoice_count": len(invoices),
            "timestamp": datetime.now().isoformat(),
        }

    def get_payables_summary(self) -> dict:
        """Get accounts payable summary."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fetch payables summary")
            return {
                "status": "dry_run",
                "total_payable": 0,
                "overdue_amount": 0,
                "timestamp": datetime.now().isoformat(),
            }

        # Get all posted vendor bills
        bills = self._execute_kw(
            "account.move",
            "search_read",
            [[
                ("move_type", "=", "in_invoice"),
                ("state", "=", "posted"),
            ]],
            {"fields": ["amount_total", "amount_residual", "payment_state", "invoice_date_due"]}
        )

        total = sum(bill["amount_residual"] for bill in bills)
        overdue = sum(
            bill["amount_residual"] for bill in bills
            if bill["invoice_date_due"] and bill["invoice_date_due"] < datetime.now().strftime("%Y-%m-%d")
        )

        return {
            "total_payable": total,
            "overdue_amount": overdue,
            "bill_count": len(bills),
            "timestamp": datetime.now().isoformat(),
        }

    # ============ Contact Operations ============

    def search_partners(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        is_customer: bool = True,
    ) -> list[dict]:
        """Search for customers/vendors in Odoo."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would search partners")
            return [{
                "status": "dry_run",
                "search_criteria": {"name": name, "email": email},
                "timestamp": datetime.now().isoformat(),
            }]

        domain = []
        if name:
            domain.append(("name", "ilike", name))
        if email:
            domain.append(("email", "ilike", email))
        if is_customer:
            domain.append(("customer_rank", ">", 0))

        partners = self._execute_kw(
            "res.partner",
            "search_read",
            [domain],
            {"fields": ["name", "email", "phone", "street", "city", "country_id"]}
        )

        return partners

    def create_partner(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_customer: bool = True,
    ) -> dict:
        """Create a new customer/vendor in Odoo."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create partner: {name}")
            return {
                "status": "dry_run",
                "name": name,
                "timestamp": datetime.now().isoformat(),
            }

        vals = {
            "name": name,
            "customer_rank": 1 if is_customer else 0,
            "supplier_rank": 0 if is_customer else 1,
        }
        if email:
            vals["email"] = email
        if phone:
            vals["phone"] = phone

        partner_id = self._execute_kw("res.partner", "create", [vals])

        partner = self._execute_kw(
            "res.partner",
            "read",
            [[partner_id]],
            {"fields": ["name", "email", "phone"]}
        )

        return partner[0]

    # ============ Health Check ============

    def health_check(self) -> dict:
        """Check Odoo connection health."""
        try:
            # Try to get server version
            version = self._json_rpc("common", "version", [])
            return {
                "status": "healthy",
                "server_version": version.get("server_version", "unknown"),
                "authenticated": self.uid is not None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # ============ MCP Tool Interface ============

    async def execute_action(self, action: dict) -> dict:
        """
        Execute an Odoo action from the orchestrator.

        Action types:
        - odoo_create_invoice
        - odoo_get_receivables
        - odoo_get_payables
        - odoo_search_partners
        - odoo_financial_report
        """
        action_type = action.get("type", "")
        params = action.get("parameters", {})

        if action_type == "odoo_create_invoice":
            return self.create_invoice(
                partner_id=params.get("partner_id"),
                lines=params.get("lines", []),
                invoice_date=params.get("invoice_date"),
            )

        elif action_type == "odoo_get_receivables":
            return self.get_receivables_summary()

        elif action_type == "odoo_get_payables":
            return self.get_payables_summary()

        elif action_type == "odoo_search_partners":
            return self.search_partners(
                name=params.get("name"),
                email=params.get("email"),
            )

        elif action_type == "odoo_get_unpaid":
            return self.get_unpaid_invoices(
                days_overdue=params.get("days_overdue", 0)
            )

        else:
            return {
                "status": "error",
                "message": f"Unknown action type: {action_type}",
            }


# Factory function
def create_odoo_mcp(
    url: str,
    database: str,
    username: str,
    password: str,
    dry_run: bool = True,
) -> OdooMCP:
    """Create an Odoo MCP instance."""
    return OdooMCP(
        url=url,
        database=database,
        username=username,
        password=password,
        dry_run=dry_run,
    )
