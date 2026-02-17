"""
MCP Server - Combines all MCP tools.

This module creates a unified MCP server with all available tools.
"""

from fastmcp import FastMCP
from src.mcp.tools.email import mcp as email_mcp
from src.mcp.tools.employee import mcp as employee_mcp
from src.mcp.tools.document import mcp as document_mcp

mcp = FastMCP("DebAI Tools")

from src.mcp.tools.email import send_email, send_email_direct
from src.mcp.tools.employee import lookup_employee, list_employees, get_employee_emails
from src.mcp.tools.document import (
    create_word_document,
    create_pdf_document,
    create_excel_spreadsheet,
    create_text_file,
)

__all__ = [
    "mcp",
    "send_email",
    "send_email_direct",
    "lookup_employee",
    "list_employees",
    "get_employee_emails",
    "create_word_document",
    "create_pdf_document",
    "create_excel_spreadsheet",
    "create_text_file",
]
