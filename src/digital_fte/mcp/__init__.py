"""MCP (Model Context Protocol) server integrations."""

from .email_mcp import EmailMCP
from .browser_mcp import BrowserMCP
from .odoo_mcp import OdooMCP

__all__ = ["EmailMCP", "BrowserMCP", "OdooMCP"]
