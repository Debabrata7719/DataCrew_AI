"""MCP Tools package."""

from src.mcp.tools.email import (
    send_email,
    send_email_direct,
    get_mcp_server as get_email_server,
)
from src.mcp.tools.employee import (
    lookup_employee,
    list_employees,
    get_employee_emails,
    get_mcp_server as get_employee_server,
)
from src.mcp.tools.document import (
    create_word_document,
    create_pdf_document,
    create_excel_spreadsheet,
    create_text_file,
    get_mcp_server as get_document_server,
)

__all__ = [
    "send_email",
    "send_email_direct",
    "lookup_employee",
    "list_employees",
    "get_employee_emails",
    "create_word_document",
    "create_pdf_document",
    "create_excel_spreadsheet",
    "create_text_file",
    "get_email_server",
    "get_employee_server",
    "get_document_server",
]
