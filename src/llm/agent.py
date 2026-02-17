"""
LLM Agent

Creates a LangChain agent with access to all MCP tools.
"""

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from src.config import GROQ_API_KEY
from src.mcp.tools.email import send_email_direct
from src.services.employee_service import (
    find_all_employees,
    search_employees,
    find_employees_by_job,
    list_all_job_types,
)
from src.services.document_service import DocumentGenerator

GENERATED_DIR = "generated_docs"

_current_session_id = {"id": "default"}


def get_session_id() -> str:
    """Get current session_id."""
    return _current_session_id["id"]


def set_session_id(session_id: str):
    """Set session_id."""
    _current_session_id["id"] = session_id


def get_llm():
    """Get the LLM instance."""
    return ChatGroq(
        groq_api_key=GROQ_API_KEY, model="openai/gpt-oss-120b", temperature=0
    )


@tool
def create_word_document(title: str, content: str, filename: str) -> str:
    """Create a Microsoft Word document (.docx)."""
    session_id = get_session_id()

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

        from pathlib import Path

        session_dir = Path(GENERATED_DIR) / session_id
        session_dir.mkdir(exist_ok=True)

        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_docx(
            filename, title, main_content, sections if sections else None
        )

        return f"Word document created: {filename}.docx"
    except Exception as e:
        return f"Error creating Word document: {str(e)}"


@tool
def create_pdf_document(title: str, content: str, filename: str) -> str:
    """Create a PDF document."""
    session_id = get_session_id()

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

        from pathlib import Path

        session_dir = Path(GENERATED_DIR) / session_id
        session_dir.mkdir(exist_ok=True)

        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_pdf(
            filename, title, main_content, sections if sections else None
        )

        return f"PDF document created: {filename}.pdf"
    except Exception as e:
        return f"Error creating PDF: {str(e)}"


@tool
def create_excel_spreadsheet(
    filename: str, sheet_name: str, headers_json: str, data_json: str, title: str = None
) -> str:
    """Create an Excel spreadsheet."""
    session_id = get_session_id()

    import json

    try:
        headers = json.loads(headers_json)
        data = json.loads(data_json)

        from pathlib import Path

        session_dir = Path(GENERATED_DIR) / session_id
        session_dir.mkdir(exist_ok=True)

        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_xlsx(filename, sheet_name, headers, data, title)

        return f"Excel spreadsheet created: {filename}.xlsx"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for headers or data"
    except Exception as e:
        return f"Error creating Excel file: {str(e)}"


@tool
def create_text_file(content: str, filename: str) -> str:
    """Create a plain text file."""
    session_id = get_session_id()

    try:
        from pathlib import Path

        session_dir = Path(GENERATED_DIR) / session_id
        session_dir.mkdir(exist_ok=True)

        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_txt(filename, content)

        return f"Text file created: {filename}.txt"
    except Exception as e:
        return f"Error creating text file: {str(e)}"


@tool
def lookup_employee(name_or_role: str) -> str:
    """Look up employee(s) from MongoDB by name OR job role."""
    try:
        query = name_or_role.strip().lower()

        if query in ("all", "everyone", "all employees", "everybody"):
            employees = find_all_employees()
        else:
            employees = search_employees(name_or_role)

        if not employees:
            return f"No employees found matching '{name_or_role}'."

        lines = []
        for emp in employees:
            email = emp.get("email_id", "N/A")
            valid = "valid" if email and "@" in email else "invalid"
            lines.append(
                f"- {emp.get('name', '?')} | {emp.get('job_type', '?')} | {email} ({valid})"
            )

        return f"Found {len(employees)} employee(s):\n" + "\n".join(lines)

    except Exception as e:
        return f"Database error: {str(e)}"


@tool
def list_employees(filter_role: str = "all") -> str:
    """List employees from database, optionally filtered by job role."""
    try:
        if filter_role.lower() in ("all", "everyone", ""):
            employees = find_all_employees()
            header = "All employees"
        else:
            employees = find_employees_by_job(filter_role)
            header = f"Employees matching '{filter_role}'"

        if not employees:
            return f"No employees found for '{filter_role}'."

        lines = [f"{header} ({len(employees)} found):"]
        for emp in employees:
            email = emp.get("email_id", "N/A")
            status = "valid" if email and "@" in email else "invalid"
            lines.append(
                f"  - {emp.get('name', '?'):20s} | {emp.get('job_type', '?'):25s} | {email} ({status})"
            )
        return "\n".join(lines)

    except Exception as e:
        return f"Database error: {str(e)}"


@tool
def send_email_tool(receiver_email: str, subject: str, message: str) -> str:
    """Send an email to a direct email address with optional attachments."""
    session_id = get_session_id()

    try:
        from src.api.session_state import get_all_session_files

        all_files = get_all_session_files(session_id)

        result = send_email_direct(
            receiver_email, subject, message, all_files if all_files else None
        )

        return result
    except Exception as e:
        return f"Error sending email: {str(e)}"


@tool
def send_email_to_employees(name_or_role: str, subject: str, message: str) -> str:
    """Look up employees by name/job role and send them an email."""
    session_id = get_session_id()

    try:
        from src.api.session_state import (
            get_all_session_files,
            session_files,
            session_generated_files,
        )
        import shutil
        import os
        from pathlib import Path

        query = name_or_role.strip().lower()

        if query in ("all", "everyone", "all employees", "everybody"):
            employees = find_all_employees()
        else:
            employees = search_employees(name_or_role)

        if not employees:
            return f"No employees found matching '{name_or_role}'."

        all_files = get_all_session_files(session_id)

        results = []
        sent_count = 0
        failed_count = 0

        for emp in employees:
            email = emp.get("email_id", "").strip()
            name = emp.get("name", "Unknown")
            role = emp.get("job_type", "Unknown")

            if not email or "@" not in email:
                results.append(f"- {name} ({role}) - skipped: invalid email '{email}'")
                failed_count += 1
                continue

            result = send_email_direct(
                receiver_email=email,
                subject=subject,
                message=message,
                attachment_paths=all_files if all_files else None,
            )

            if "successfully" in result.lower():
                results.append(f"- {name} ({role}) -> {email}")
                sent_count += 1
            else:
                results.append(f"- {name} ({role}) -> {email} - {result}")
                failed_count += 1

        summary = f"Email sent to {sent_count} recipient(s):\n" + "\n".join(
            [r for r in results if "->" in r]
        )

        if failed_count > 0:
            summary += f"\n\nSkipped ({failed_count}):\n" + "\n".join(
                [r for r in results if "skipped" in r.lower()]
            )

        return summary

    except Exception as e:
        return f"Error sending email: {str(e)}"


SYSTEM_PROMPT = """You are DebAI, a professional AI email assistant with DIRECT ACCESS to a MongoDB employee database.

## IMPORTANT - ALWAYS USE TOOLS

When user asks to ADD/STORE/INSERT an employee (any variation like "add employee", "add to database", "store data", "insert employee", "new employee"), YOU MUST call the add_employee_to_database tool with the FULL user message.

## EXACTLY COPY ONE OF THESE FORMATS when adding employee:

Format 1 (with parentheses):
"Added employee Rahul Saha (backend developer) with email rahul@gmail.com and phone 8394847563 to the database."

Format 2 (with keywords):
"add a employee to the database name Rahul Saha email id rahul@gmail.com job type backend developer and phone number is 8394847563"

Format 3 (simple):
"add Rahul Saha as developer email rahul@test.com phone 12345"

Format 4 (short):
"store name John email john@test.com phone 555-1234 job_type engineer"

Pass the FULL user message to the add_employee_to_database tool.

## RULE 1 - DOCUMENTS: ONLY CREATE WHEN EXPLICITLY ASKED

## RULE 2 - EMPLOYEE DATA: ALWAYS CALL THE TOOL
When user says ANYTHING about adding/storing/inserting employee data -> call add_employee_to_database IMMEDIATELY with the full user message.

## YOUR TOOLS:
- add_employee_to_database: PASS THE ENTIRE USER MESSAGE when they want to add employee data
- send_email_tool: For direct email addresses
- send_email_to_employees: For names or job roles
- lookup_employee / list_employees: Show who is in database

## DECISION TABLE:
| What user says | What you do |
|---|---|
| "send email to data scientists" | send_email_to_employees |
| "email Rahul" | send_email_to_employees |
| "send to boss@gmail.com" | send_email_tool |
| "create a report and send" | create_word_document -> send_email_to_employees |
| "who are the backend developers?" | list_employees |

AFTER ACTING:
- Tell user what you did
- NEVER add sign-offs - added automatically
- Be brief and professional"""


@tool
def add_employee_to_database(natural_language_text: str) -> str:
    """
    Add a new employee to MongoDB. Extract name, email, phone, job_type from the text.

    Input examples:
    - "Added employee Rahul Saha (backend developer) with email rahul@gmail.com and phone 8394847563"
    - "add john ibrahim with email john808@gmail.com and phone 83948"
    - "store name Sarah, email sarah@test.com, phone 555-1234"
    - "add Rahul Saha as developer email rahul@test.com phone 12345"

    Extract:
    - name: Look for patterns like "name X", "employee X", "add X"
    - email: Look for email pattern xxx@xxx.xxx
    - phone: Look for phone number (5+ digits)
    - job_type: Look for patterns like "(developer)", "as developer", "role X", "job_type X"
    """
    import re

    text = natural_language_text.lower()
    original_text = natural_language_text

    name = None
    email = None
    phone = None
    job_type = None

    name_patterns = [
        r"(?:employee|add|store|insert)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"name(?:\s+is)?[:\s]+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"(?:name|add)\s+(?:a\s+)?(?:employee\s+)?(?:to\s+)?(?:the\s+)?database\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
    ]
    for pattern in name_patterns:
        emp_match = re.search(pattern, text, re.IGNORECASE)
        if emp_match:
            name = emp_match.group(1).strip()
            excluded = [
                "email",
                "phone",
                "job",
                "type",
                "id",
                "the",
                "a",
                "an",
                "to",
                "in",
                "as",
                "is",
            ]
            if name and len(name) >= 2 and name.lower() not in excluded:
                break

    email_pattern = r"[\w\.-]+@[\w\.-]+\.\w+"
    email_match = re.search(email_pattern, original_text)
    if email_match:
        email = email_match.group(0)

    phone_patterns = [
        r"phone(?:\s+number)?[:\s]+(\d{5,})",
        r"(\d{10,})",
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text, re.IGNORECASE)
        if phone_match:
            phone = phone_match.group(1).strip()
            break

    job_type = None

    job_type_match = re.search(r"\(([a-zA-Z\s]+)\)", original_text)
    if job_type_match:
        job_type = job_type_match.group(1).strip()

    if not job_type:
        job_type_patterns = [
            r"job[_-]?type(?:\s+is)?[:\s]+([a-zA-Z]+)",
            r"\bas\s+([a-zA-Z]+)",
            r"\brole(?:\s+is)?[:\s]+([a-zA-Z]+)",
        ]
        for pattern in job_type_patterns:
            job_match = re.search(pattern, text, re.IGNORECASE)
            if job_match:
                job_type = job_match.group(1).strip()
                if job_type and job_type.lower() not in ["email", "phone"]:
                    break
            if job_match:
                job_type = job_match.group(1).strip()
                name_lower = name.lower() if name else ""
                if job_type and len(job_type) >= 2 and job_type.lower() != name_lower:
                    break

    if not name:
        return "Error: Could not extract name from input. Please provide a name."

    from src.services.employee_service import add_employee as _add_employee

    result = _add_employee(
        name=name,
        email_id=email if email else "",
        phone_number=phone if phone else "",
        job_type=job_type if job_type else "",
    )
    return result


def create_agent_with_tools(session_id: str = "default"):
    """Create an agent with all tools configured for a session."""
    set_session_id(session_id)

    llm = get_llm()

    agent = create_agent(
        model=llm,
        tools=[
            send_email_tool,
            send_email_to_employees,
            lookup_employee,
            list_employees,
            add_employee_to_database,
            create_word_document,
            create_pdf_document,
            create_excel_spreadsheet,
            create_text_file,
        ],
        system_prompt=SYSTEM_PROMPT,
        debug=True,
    )

    return agent


def get_agent():
    """Get default agent instance."""
    return create_agent_with_tools("default")
