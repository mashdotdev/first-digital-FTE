"""MCP (Model Context Protocol) server integrations."""

from .email_mcp import EmailMCP
from .browser_mcp import BrowserMCP
from .odoo_mcp import OdooMCP
from .whatsapp_mcp import WhatsAppMCP
from .twitter_mcp import TwitterMCP
from .invoice_mcp import InvoiceMCP

__all__ = ["EmailMCP", "BrowserMCP", "OdooMCP", "WhatsAppMCP", "TwitterMCP", "InvoiceMCP"]
