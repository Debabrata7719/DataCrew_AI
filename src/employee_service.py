"""
DebAI Email Assistant - MongoDB Employee Service

Connects to MongoDB Compass and looks up employees by name, job type, etc.
Supports smart search: single employee, by job role, all employees.
"""

from pymongo import MongoClient
from typing import List, Dict, Optional


# ─── MongoDB Connection ────────────────────────────────────────────────────────
MONGO_URI    = "mongodb://localhost:27017/"
DB_NAME      = "Employee's"
COLLECTION   = "Employee_data"


def get_collection():
    """Return the Employee_data collection."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION]


# ─── Core Search Functions ─────────────────────────────────────────────────────

def find_employee_by_name(name: str) -> Optional[Dict]:
    """
    Find a single employee by name (case-insensitive, partial match).

    Args:
        name: Employee name or partial name

    Returns:
        Employee dict or None
    """
    col = get_collection()
    result = col.find_one(
        {"name": {"$regex": name, "$options": "i"}},
        {"_id": 0}
    )
    return result


def find_employees_by_job(job_type: str) -> List[Dict]:
    """
    Find ALL employees matching a job type (case-insensitive, partial match).
    Handles variations like 'backend dev', 'backend developer', 'Backend Developer'.

    Args:
        job_type: Job role to search for

    Returns:
        List of matching employees
    """
    col = get_collection()
    results = list(col.find(
        {"job_type": {"$regex": job_type, "$options": "i"}},
        {"_id": 0}
    ))
    return results


def find_all_employees() -> List[Dict]:
    """
    Retrieve ALL employees from the database.

    Returns:
        List of all employee dicts
    """
    col = get_collection()
    return list(col.find({}, {"_id": 0}))


def search_employees(query: str) -> List[Dict]:
    """
    Smart search: searches across name, job_type fields.

    Args:
        query: Free-text search term

    Returns:
        List of matching employees
    """
    col = get_collection()
    results = list(col.find(
        {
            "$or": [
                {"name":     {"$regex": query, "$options": "i"}},
                {"job_type": {"$regex": query, "$options": "i"}},
            ]
        },
        {"_id": 0}
    ))
    return results


def get_employee_emails_by_job(job_type: str) -> List[str]:
    """
    Get email addresses of all employees with a given job type.

    Args:
        job_type: Job role

    Returns:
        List of email addresses (non-empty only)
    """
    employees = find_employees_by_job(job_type)
    return [
        emp["email_id"]
        for emp in employees
        if emp.get("email_id") and emp["email_id"].strip() and "@" in emp["email_id"]
    ]


def get_all_employee_emails() -> List[str]:
    """
    Get ALL valid employee email addresses.

    Returns:
        List of valid email addresses
    """
    employees = find_all_employees()
    return [
        emp["email_id"]
        for emp in employees
        if emp.get("email_id") and emp["email_id"].strip() and "@" in emp["email_id"]
    ]


def list_all_job_types() -> List[str]:
    """
    Get a unique list of all job types in the database.

    Returns:
        Sorted list of job type strings
    """
    col = get_collection()
    return sorted(col.distinct("job_type"))


def test_connection() -> bool:
    """
    Test whether MongoDB is reachable.

    Returns:
        True if connected, False otherwise
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()
        return True
    except Exception:
        return False
