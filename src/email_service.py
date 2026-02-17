"""
DebAI Email Assistant - Email Service MCP Server

Provides email sending tool via MCP with file attachment support.
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

# Create MCP server
mcp = FastMCP("Email Tool")


def send_email_direct(
    receiver_email: str, 
    subject: str, 
    message: str, 
    attachment_paths: Optional[List[str]] = None
) -> str:
    """Send an email using SMTP with automatic signature and optional attachments."""

    email_signature = f"\n\nBest regards,\n{SENDER_NAME}"
    full_message = message + email_signature

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Attach the email body
    msg.attach(MIMEText(full_message, "plain"))

    # Attach files if provided
    attached_files = []
    if attachment_paths:
        for file_path in attachment_paths:
            try:
                if not os.path.exists(file_path):
                    return f"❌ Error: File not found: {file_path}"
                
                filename = os.path.basename(file_path)
                
                # Open file in binary mode
                with open(file_path, "rb") as attachment:
                    # Create MIMEBase object
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                
                # Encode file in base64
                encoders.encode_base64(part)
                
                # Add header with filename
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                
                # Attach the file to the message
                msg.attach(part)
                attached_files.append(filename)
                
            except Exception as e:
                return f"❌ Error attaching file {file_path}: {str(e)}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()

        if attached_files:
            files_str = ", ".join(attached_files)
            return f"✅ Email sent successfully with attachments: {files_str}"
        else:
            return "✅ Email sent successfully!"

    except Exception as e:
        return f"❌ Error sending email: {str(e)}"


@mcp.tool()
def send_email(
    receiver_email: str, 
    subject: str, 
    message: str,
    attachment_paths: Optional[List[str]] = None
) -> str:
    """MCP-exposed tool wrapper for sending an email with optional attachments."""
    return send_email_direct(receiver_email, subject, message, attachment_paths)

if __name__ == "__main__":
    # Run MCP server via STDIO
    mcp.run()