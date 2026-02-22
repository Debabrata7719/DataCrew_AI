"""
Email Agent

Specialized agent for sending emails.
"""

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from src.config import GROQ_API_KEY
from src.mcp.tools.email import send_email_direct


_current_session_id = {"id": "default"}


def get_session_id() -> str:
    """Get current session_id."""
    return _current_session_id["id"]


def set_session_id(session_id: str):
    """Set session_id."""
    _current_session_id["id"] = session_id


def get_llm_email():
    """Get the LLM instance for email agent."""
    return ChatGroq(
        groq_api_key=GROQ_API_KEY, model="openai/gpt-oss-120b", temperature=0
    )


EMAIL_SYSTEM_PROMPT = """You are an Email Sending Assistant AI. Your role is to help send emails to recipients.

## YOUR TOOLS:
- send_email_to_direct: Send an email to a direct email address (e.g., boss@gmail.com)
- send_email_to_employees: Send an email to employees from the database by name or job role

## ACTIONS:

1. DIRECT EMAIL - When user provides a direct email address (contains @):
   - Extract: receiver email, subject, message
   - Call send_email_to_direct tool

2. EMPLOYEE EMAIL - When user mentions employee name or job role:
   - Extract: name or job role to find employees, subject, message
   - Call send_email_to_employees tool

## EMAIL EXTRACTION:
- Extract the RECIPIENT (email address OR name/job role of employees)
- Extract the SUBJECT (what the email is about)
- Extract the MESSAGE (body of the email)

## EXAMPLES:
- "Send an email to boss@company.com about tomorrow's meeting at 10am"
- "Email the team about project update - we need to finish by Friday"
- "Send to john@test.com with subject Meeting Request - can we schedule for 3pm?"
- "Email all data scientists about the new policy"
- "Write to hr@company.com requesting vacation leave"

Be concise and helpful. Always confirm when emails are sent.
"""


@tool
def send_email_to_direct(receiver_email: str, subject: str, message: str) -> str:
    """
    Send an email to a direct email address.
    """
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
    """
    Send an email to employees by name or job role from the database.
    """
    session_id = get_session_id()

    try:
        from src.api.session_state import get_all_session_files
        from src.services.employee_service import search_employees, find_all_employees

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
                results.append(f"- {name} ({role}) - skipped: invalid email")
                failed_count += 1
                continue

            try:
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
                    results.append(f"- {name} ({role}) -> {email} - Failed")
                    failed_count += 1
            except Exception as e:
                results.append(f"- {name} ({role}) -> {email} - Error: {str(e)}")
                failed_count += 1

        summary = f"Email sent to {sent_count} recipient(s):\n" + "\n".join(
            [r for r in results if "->" in r]
        )

        if failed_count > 0:
            summary += f"\n\nSkipped/Failed ({failed_count}):\n" + "\n".join(
                [
                    r
                    for r in results
                    if "skipped" in r.lower()
                    or "failed" in r.lower()
                    or "error" in r.lower()
                ]
            )

        return summary

    except Exception as e:
        return f"Error sending email: {str(e)}"


def create_email_agent(session_id: str = "default"):
    """Create the email sending agent."""
    set_session_id(session_id)

    llm = get_llm_email()

    agent = create_agent(
        model=llm,
        tools=[
            send_email_to_direct,
            send_email_to_employees,
        ],
        system_prompt=EMAIL_SYSTEM_PROMPT,
        debug=False,
    )

    return agent
