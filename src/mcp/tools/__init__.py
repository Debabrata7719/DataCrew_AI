"""MCP Tools package."""

from src.mcp.tools.email import (
    send_email,
    send_email_direct,
    get_mcp_server as get_email_server,
)

__all__ = [
    "send_email",
    "send_email_direct",
    "get_email_server",
]
