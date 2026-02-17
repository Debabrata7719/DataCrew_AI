"""
MCP Tools - Document Tool

Provides document creation functionality via MCP.
"""

from fastmcp import FastMCP
import json
from typing import List, Optional

from src.services.document_service import DocumentGenerator

mcp = FastMCP("Document Tool")

GENERATED_DIR = "generated_docs"


def _get_session_dir(session_id: str):
    """Get the session directory, creating it if needed."""
    from pathlib import Path

    session_dir = Path(GENERATED_DIR) / session_id
    session_dir.mkdir(exist_ok=True)
    return str(session_dir)


@mcp.tool()
def create_word_document(
    title: str, content: str, filename: str, session_id: str = "default"
) -> str:
    """
    Create a Microsoft Word document (.docx) with the given content.

    Args:
        title: Document title
        content: Main text content
        filename: Filename without extension (e.g., 'report' not 'report.docx')
        session_id: Session identifier

    Returns:
        Success message with filename
    """
    try:
        sections = []
        if "\n## " in content or "\n# " in content:
            parts = content.split("\n## ")
            main_content = parts[0].strip()
            for part in parts[1:]:
                lines = part.split("\n", 1)
                heading = lines[0].strip()
                text = lines[1].strip() if len(lines) > 1 else ""
                sections.append({"heading": heading, "text": text})
        else:
            main_content = content

        session_dir = _get_session_dir(session_id)
        generator = DocumentGenerator(session_dir)
        filepath = generator.create_docx(
            filename, title, main_content, sections if sections else None
        )

        return f"Word document created: {filename}.docx"

    except Exception as e:
        return f"Error creating Word document: {str(e)}"


@mcp.tool()
def create_pdf_document(
    title: str, content: str, filename: str, session_id: str = "default"
) -> str:
    """
    Create a PDF document with the given content.

    Args:
        title: Document title
        content: Main text content
        filename: Filename without extension
        session_id: Session identifier

    Returns:
        Success message with filename
    """
    try:
        sections = []
        if "\n## " in content:
            parts = content.split("\n## ")
            main_content = parts[0].strip()
            for part in parts[1:]:
                lines = part.split("\n", 1)
                heading = lines[0].strip()
                text = lines[1].strip() if len(lines) > 1 else ""
                sections.append({"heading": heading, "text": text})
        else:
            main_content = content

        session_dir = _get_session_dir(session_id)
        generator = DocumentGenerator(session_dir)
        filepath = generator.create_pdf(
            filename, title, main_content, sections if sections else None
        )

        return f"PDF document created: {filename}.pdf"

    except Exception as e:
        return f"Error creating PDF: {str(e)}"


@mcp.tool()
def create_excel_spreadsheet(
    filename: str,
    sheet_name: str,
    headers_json: str,
    data_json: str,
    title: Optional[str] = None,
    session_id: str = "default",
) -> str:
    """
    Create an Excel spreadsheet with the given data.

    Args:
        filename: Filename without extension
        sheet_name: Name for the worksheet
        headers_json: JSON string of column headers (e.g., '["Name", "Age", "City"]')
        data_json: JSON string of 2D array data (e.g., '[["John", 30, "NYC"], ["Jane", 25, "LA"]]')
        title: Optional title for the spreadsheet
        session_id: Session identifier

    Returns:
        Success message with filename
    """
    try:
        headers = json.loads(headers_json)
        data = json.loads(data_json)

        session_dir = _get_session_dir(session_id)
        generator = DocumentGenerator(session_dir)
        filepath = generator.create_xlsx(filename, sheet_name, headers, data, title)

        return f"Excel spreadsheet created: {filename}.xlsx"

    except json.JSONDecodeError:
        return "Error: Invalid JSON format for headers or data"
    except Exception as e:
        return f"Error creating Excel file: {str(e)}"


@mcp.tool()
def create_text_file(content: str, filename: str, session_id: str = "default") -> str:
    """
    Create a plain text file with the given content.

    Args:
        content: Text content
        filename: Filename without extension
        session_id: Session identifier

    Returns:
        Success message with filename
    """
    try:
        session_dir = _get_session_dir(session_id)
        generator = DocumentGenerator(session_dir)
        filepath = generator.create_txt(filename, content)

        return f"Text file created: {filename}.txt"

    except Exception as e:
        return f"Error creating text file: {str(e)}"


def get_mcp_server():
    """Return the MCP server instance."""
    return mcp
