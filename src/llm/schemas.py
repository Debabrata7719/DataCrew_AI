from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr


class EmployeeAction(BaseModel):
    """Schema for employee database operations."""

    action: Literal["add", "update", "delete", "search", "list"] = Field(
        description="The action to perform: add (insert new employee), update (modify existing), delete (remove), search (find by name/role), list (show all)"
    )
    name: str = Field(
        description="Full name of the employee. For add: new employee's name. For update/delete/search: the employee's name to target."
    )
    email: Optional[str] = Field(
        default=None,
        description="Email address of the employee (e.g., john@example.com). Required for add action.",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the employee (digits only, e.g., 1234567890). Optional for add action.",
    )
    job_type: Optional[str] = Field(
        default=None,
        description="Job type, role, or position (e.g., 'data scientist', 'frontend developer', 'manager'). Use lowercase.",
    )
    update_field: Optional[str] = Field(
        default=None,
        description="For update action only: the field to update (email, phone, or job_type)",
    )
    update_value: Optional[str] = Field(
        default=None,
        description="For update action only: the new value for the field being updated",
    )


class EmployeeInput(BaseModel):
    """Schema for adding a new employee to the database."""

    name: str = Field(
        description="Full name of the employee to add (first and last name, e.g., 'John Doe')"
    )
    email: Optional[EmailStr] = Field(
        default=None,
        description="Email address of the employee (e.g., john.doe@company.com). Must contain @ symbol.",
    )
    phone: Optional[str] = Field(
        default=None,
        description="Phone number of the employee (digits only, e.g., '1234567890' or '123-456-7890').",
    )
    job_type: Optional[str] = Field(
        default=None,
        description="Job title or role (e.g., 'software engineer', 'data scientist', 'product manager', 'frontend developer').",
    )


class EmailInput(BaseModel):
    receiver_email: Optional[str] = Field(
        default=None, description="Direct email address of receiver"
    )
    name_or_role: Optional[str] = Field(
        default=None, description="Name or job role to lookup employees"
    )
    subject: str = Field(description="Subject of the email")
    message: str = Field(default="", description="Body message of the email")


class DocumentInput(BaseModel):
    filename: str = Field(description="Name of the file to create (without extension)")
    title: Optional[str] = Field(default=None, description="Title for the document")
    content: str = Field(description="Main content of the document")
    sheet_name: Optional[str] = Field(
        default=None, description="Sheet name for Excel files"
    )
    headers_json: Optional[str] = Field(
        default=None, description="JSON array of column headers for Excel"
    )
    data_json: Optional[str] = Field(
        default=None, description="JSON array of row data for Excel"
    )
