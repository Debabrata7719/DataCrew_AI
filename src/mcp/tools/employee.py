"""
MCP Tools - Employee Tool

Provides employee lookup functionality via MCP.
"""

from fastmcp import FastMCP
from typing import List, Optional

from src.services.employee_service import (
    find_employee_by_name,
    find_employees_by_job,
    find_all_employees,
    search_employees,
    get_employee_emails_by_job,
    get_all_employee_emails,
    list_all_job_types,
)

mcp = FastMCP("Employee Tool")


@mcp.tool()
def lookup_employee(name_or_role: str) -> str:
    """
    Look up employee(s) from the MongoDB database by name OR job role.
    Use this BEFORE sending an email when user mentions a person's name or a job title.

    Args:
        name_or_role: A person's name OR a job role OR 'all' for everyone
                      Examples: 'Rahul', 'backend developer', 'data scientist', 'all'

    Returns:
        Formatted list of matching employees with their email addresses
    """
    try:
        query = name_or_role.strip().lower()

        if query in ("all", "everyone", "all employees", "everybody"):
            employees = find_all_employees()
        else:
            employees = search_employees(name_or_role)

        if not employees:
            return (
                f"No employees found matching '{name_or_role}'.\n"
                f"Available job types: {', '.join(list_all_job_types())}"
            )

        lines = []
        for emp in employees:
            email = emp.get("email_id", "N/A")
            valid = "valid" if email and "@" in email else "invalid email"
            lines.append(
                f"- {emp.get('name', '?')} | {emp.get('job_type', '?')} | {email} ({valid})"
            )

        return f"Found {len(employees)} employee(s):\n" + "\n".join(lines)

    except Exception as e:
        return f"Database error: {str(e)}"


@mcp.tool()
def list_employees(filter_role: str = "all") -> str:
    """
    List employees from the database, optionally filtered by job role.
    Use when user asks 'who are the backend developers?' or 'show me all employees'.

    Args:
        filter_role: Job role to filter by, or 'all' for everyone

    Returns:
        Formatted list of employees
    """
    try:
        if filter_role.lower() in ("all", "everyone", ""):
            employees = find_all_employees()
            header = "All employees"
        else:
            employees = find_employees_by_job(filter_role)
            header = f"Employees matching '{filter_role}'"

        if not employees:
            return (
                f"No employees found for '{filter_role}'.\n"
                f"Available job types: {', '.join(list_all_job_types())}"
            )

        lines = [f"{header} ({len(employees)} found):"]
        for emp in employees:
            email = emp.get("email_id", "N/A")
            status = "valid" if email and "@" in email else "invalid"
            lines.append(
                f"  - {emp.get('name', '?'):20s} | "
                f"{emp.get('job_type', '?'):25s} | "
                f"{email} ({status})"
            )
        return "\n".join(lines)

    except Exception as e:
        return f"Database error: {str(e)}"


@mcp.tool()
def get_employee_emails(query: str) -> str:
    """
    Get email addresses for employees matching a name or job role.

    Args:
        query: Name or job role to search for, or 'all' for everyone

    Returns:
        List of email addresses
    """
    try:
        query = query.strip().lower()

        if query in ("all", "everyone", "all employees", "everybody"):
            emails = get_all_employee_emails()
        else:
            employees = search_employees(query)
            emails = [
                emp["email_id"]
                for emp in employees
                if emp.get("email_id") and "@" in emp["email_id"]
            ]

        if not emails:
            return f"No valid emails found for '{query}'"

        return f"Found {len(emails)} email(s):\n" + "\n".join(emails)

    except Exception as e:
        return f"Database error: {str(e)}"


def get_mcp_server():
    """Return the MCP server instance."""
    return mcp
