"""
Services - Employee Service

Connects to MongoDB and provides employee lookup operations.
"""

from typing import List, Dict, Optional

from src.data.mongodb import get_collection
from src.data.repository import (
    find_employee_by_name as _find_by_name,
    find_employees_by_job as _find_by_job,
    find_all_employees as _find_all,
    search_employees as _search,
    get_employee_emails_by_job as _get_emails_by_job,
    get_all_employee_emails as _get_all_emails,
    list_all_job_types as _list_jobs,
    employee_exists as _employee_exists,
)


def find_employee_by_name(name: str) -> Optional[Dict]:
    """Find employee by name (case-insensitive, partial match)."""
    return _find_by_name(name)


def find_employees_by_job(job_type: str) -> List[Dict]:
    """Find all employees by job type."""
    return _find_by_job(job_type)


def find_all_employees() -> List[Dict]:
    """Get all employees."""
    return _find_all()


def search_employees(query: str) -> List[Dict]:
    """Search employees by name or job type."""
    return _search(query)


def get_employee_emails_by_job(job_type: str) -> List[str]:
    """Get valid emails for a job type."""
    return _get_emails_by_job(job_type)


def get_all_employee_emails() -> List[str]:
    """Get all valid employee emails."""
    return _get_all_emails()


def list_all_job_types() -> List[str]:
    """Get all unique job types."""
    return _list_jobs()


def check_employee_exists(
    name: str, email_id: str = None, job_type: str = None
) -> bool:
    """Check if employee already exists."""
    return _employee_exists(name, email_id, job_type)


def test_connection() -> bool:
    """Test MongoDB connection."""
    from src.data.mongodb import test_connection as _test

    return _test()


def add_employee(
    name: str, email_id: str = None, phone_number: str = None, job_type: str = None
) -> str:
    """
    Add a new employee to the database.

    Args:
        name: Employee name
        email_id: Employee email address
        phone_number: Employee phone number
        job_type: Job type/role (optional)

    Returns:
        Success message with inserted ID
    """
    from src.data.repository import insert_employee as _insert

    if check_employee_exists(name, email_id, job_type):
        return f"Error: Employee '{name}' already exists in the database with same name and email/job_type."

    employee = {"name": name}
    if email_id and email_id.strip():
        employee["email_id"] = email_id.strip()
    if phone_number and phone_number.strip():
        employee["phone_number"] = phone_number.strip()
    if job_type and job_type.strip():
        employee["job_type"] = job_type.strip()

    inserted_id = _insert(employee)
    return f"Employee '{name}' added successfully with ID: {inserted_id}"
