"""
MCP Tools - Email Tool

Provides email sending functionality via MCP.
"""

from fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional

from src.config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD, SENDER_NAME

mcp = FastMCP("Email Tool")


def send_email_direct(
    receiver_email: str,
    subject: str,
    message: str,
    attachment_paths: Optional[List[str]] = None,
) -> str:
    """Send an email using SMTP with automatic signature and optional attachments."""

    email_signature = f"\n\nBest regards,\n{SENDER_NAME}"
    full_message = message + email_signature

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(full_message, "plain"))

    attached_files = []
    if attachment_paths:
        for file_path in attachment_paths:
            try:
                if not os.path.exists(file_path):
                    return f"File not found: {file_path}"

                filename = os.path.basename(file_path)

                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )

                msg.attach(part)
                attached_files.append(filename)

            except Exception as e:
                return f"Error attaching file {file_path}: {str(e)}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        if attached_files:
            files_str = ", ".join(attached_files)
            return f"Email sent successfully with attachments: {files_str}"
        else:
            return "Email sent successfully!"

    except Exception as e:
        return f"Error sending email: {str(e)}"


@mcp.tool()
def send_email(
    receiver_email: str,
    subject: str,
    message: str,
    attachment_paths: Optional[List[str]] = None,
) -> str:
    """Send an email with optional attachments."""
    return send_email_direct(receiver_email, subject, message, attachment_paths)


def get_mcp_server():
    """Return the MCP server instance."""
    return mcp
