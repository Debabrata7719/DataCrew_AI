"""Services package."""

from src.services.employee_service import (
    find_employee_by_name,
    find_employees_by_job,
    find_all_employees,
    search_employees,
    get_employee_emails_by_job,
    get_all_employee_emails,
    list_all_job_types,
    test_connection,
)
from src.services.document_service import DocumentGenerator, DocumentService

__all__ = [
    "find_employee_by_name",
    "find_employees_by_job",
    "find_all_employees",
    "search_employees",
    "get_employee_emails_by_job",
    "get_all_employee_emails",
    "list_all_job_types",
    "test_connection",
    "DocumentGenerator",
    "DocumentService",
]
