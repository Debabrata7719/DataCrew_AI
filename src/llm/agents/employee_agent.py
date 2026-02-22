"""
Employee Agent

Specialized agent for managing employee data in MongoDB.
Uses with_structured_output() for efficient data extraction.
"""

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from src.config import GROQ_API_KEY
from src.llm.schemas import EmployeeAction


_current_session_id = {"id": "default"}


def get_session_id() -> str:
    """Get current session_id."""
    return _current_session_id["id"]


def set_session_id(session_id: str):
    """Set session_id."""
    _current_session_id["id"] = session_id


def get_llm_employee():
    """Get the LLM instance for employee agent."""
    return ChatGroq(
        groq_api_key=GROQ_API_KEY, model="openai/gpt-oss-120b", temperature=0
    )


EMPLOYEE_SYSTEM_PROMPT = """You are an Employee Database Manager AI. Your role is to help manage employee data in the MongoDB database.

## YOUR TOOLS:
- add_employee: Add a new employee to the database
- update_employee: Update an existing employee's information  
- delete_employee: Delete an employee from the database
- search_employee: Search for employees by name or job role
- list_employees: List all employees or filter by job role

## HOW TO USE THE STRUCTURED OUTPUT:
The system will automatically extract the action type and employee details from user messages.
You just need to call the appropriate tool with the extracted information.

## EXAMPLES:
- "Add employee John Doe as data scientist email john@test.com phone 123456" -> add_employee
- "Update John Doe's phone to 9876543210" -> update_employee
- "Delete employee Jane Smith from database" -> delete_employee
- "Search for employees named John" -> search_employee
- "List all data scientists" -> list_employees
- "Show me all employees" -> list_employees

Be helpful and confirm when operations are successful.
"""


def get_structured_llm():
    """Get LLM with structured output for employee actions."""
    llm = get_llm_employee()
    return llm.with_structured_output(EmployeeAction)


def process_employee_request(natural_language_text: str) -> str:
    """
    Process employee request using structured output.
    Extracts action and data, then executes the appropriate operation.
    """
    try:
        structured_llm = get_structured_llm()
        result = structured_llm.invoke(natural_language_text)

        if not result:
            return "Error: Could not understand the request. Please try again."

        action = result.action
        name = result.name

        if action == "add":
            if not name:
                return "Error: Could not extract name. Please provide employee name."

            from src.services.employee_service import add_employee as _add_employee

            emp_result = _add_employee(
                name=name,
                email_id=result.email or "",
                phone_number=result.phone or "",
                job_type=result.job_type or "",
            )
            return emp_result

        elif action == "update":
            if not name:
                return "Error: Could not extract employee name."
            if not result.update_field or not result.update_value:
                return "Error: Please specify what field to update (email, phone, or job_type) and the new value."

            from src.data.repository import (
                find_employee_by_name,
                update_employee as _update_employee,
            )

            existing = find_employee_by_name(name)
            if not existing:
                return f"Error: Employee '{name}' not found in database."

            field_map = {
                "email": "email_id",
                "phone": "phone_number",
                "job": "job_type",
                "role": "job_type",
            }
            db_field = field_map.get(result.update_field.lower(), result.update_field)

            result_count = _update_employee(
                {"name": {"$regex": f"^{name}$", "$options": "i"}},
                {"$set": {db_field: result.update_value}},
            )

            if result_count > 0:
                return f"Successfully updated {result.update_field} for employee '{name}' to '{result.update_value}'."
            return "Error: Failed to update employee."

        elif action == "delete":
            if not name:
                return "Error: Could not extract employee name."

            from src.data.repository import (
                delete_employee as _delete_employee,
                find_employee_by_name,
            )

            existing = find_employee_by_name(name)
            if not existing:
                return f"Error: Employee '{name}' not found in database."

            result_count = _delete_employee(
                {"name": {"$regex": f"^{name}$", "$options": "i"}}
            )

            if result_count > 0:
                return f"Successfully deleted employee '{name}' from database."
            return "Error: Failed to delete employee."

        elif action == "search":
            from src.services.employee_service import search_employees

            employees = search_employees(name or "")

            if not employees:
                return f"No employees found matching '{name or ''}'."

            lines = [f"Found {len(employees)} employee(s):"]
            for emp in employees:
                lines.append(
                    f"- {emp.get('name', '?')} | {emp.get('job_type', 'N/A')} | {emp.get('email_id', 'N/A')}"
                )

            return "\n".join(lines)

        elif action == "list":
            from src.services.employee_service import (
                find_all_employees,
                find_employees_by_job,
            )

            role_filter = result.job_type or "all"

            if role_filter.lower() in ("all", "everyone", ""):
                employees = find_all_employees()
                header = "All employees"
            else:
                employees = find_employees_by_job(role_filter)
                header = f"Employees with role '{role_filter}'"

            if not employees:
                return "No employees found."

            lines = [f"{header} ({len(employees)} found):"]
            for emp in employees:
                lines.append(
                    f"- {emp.get('name', '?')} | {emp.get('job_type', 'N/A')} | {emp.get('email_id', 'N/A')}"
                )

            return "\n".join(lines)

        else:
            return f"Unknown action: {action}"

    except Exception as e:
        return f"Error processing request: {str(e)}"


@tool
def add_employee(natural_language_text: str) -> str:
    """Add a new employee to the database."""
    return process_employee_request(natural_language_text)


@tool
def update_employee(natural_language_text: str) -> str:
    """Update an existing employee's information."""
    return process_employee_request(natural_language_text)


@tool
def delete_employee(natural_language_text: str) -> str:
    """Delete an employee from the database."""
    return process_employee_request(natural_language_text)


@tool
def search_employee(query: str) -> str:
    """Search for employees by name or job role."""
    return process_employee_request(f"search for employee {query}")


@tool
def list_employees(filter_role: str = "all") -> str:
    """List all employees or filter by job role."""
    if filter_role.lower() in ("all", "everyone", ""):
        return process_employee_request("list all employees")
    return process_employee_request(f"list employees with role {filter_role}")


def create_employee_agent(session_id: str = "default"):
    """Create the employee database agent."""
    set_session_id(session_id)

    llm = get_llm_employee()

    agent = create_agent(
        model=llm,
        tools=[
            add_employee,
            update_employee,
            delete_employee,
            search_employee,
            list_employees,
        ],
        system_prompt=EMPLOYEE_SYSTEM_PROMPT,
        debug=False,
    )

    return agent
