"""
Router / Intent Classifier

Determines which specialized agent should handle the user's request.
Uses STRICT LLM-based intent classification as primary method.
"""

from enum import Enum
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from src.config import GROQ_API_KEY


class IntentType(str, Enum):
    EMPLOYEE = "employee"
    EMAIL = "email"
    UNKNOWN = "unknown"


class IntentClassification(BaseModel):
    intent: IntentType
    confidence: float
    reasoning: str


def classify_intent(message: str) -> IntentClassification:
    """
    Use LLM to classify the user's intent into employee or email.
    STRICT CLASSIFICATION - focuses on understanding the actual intent.
    """
    parser = JsonOutputParser(pydantic_object=IntentClassification)

    prompt = PromptTemplate(
        template="""You are a strict intent classifier. Classify user messages into:
- "employee": Any request to manage employee data (add, update, delete, list, search, store, insert, modify, change, etc.)
- "email": Any request to send/compose/write/send an email to someone

STRICT RULES:
1. If message mentions "employee" in any context (add employee, store employee, list employees, etc.) -> EMPLOYEE
2. If message contains names + job roles + phone numbers + emails together (like adding employee data) -> EMPLOYEE
3. If message has "send", "write", "compose" + recipient + subject/body -> EMAIL
4. If message is about "email", "mail" to someone -> EMAIL
5. When in doubt about employee data -> EMPLOYEE

EXAMPLES:
- "add employee John as developer email john@test.com" -> employee
- "ad a employee rahul das ukil job role is backend dev and email id is rahul@test.com phone 93940399403" -> employee
- "store name Rahul email rahul@test.com phone 123" -> employee
- "Send an email to boss@company.com about meeting" -> email
- "Email HR requesting vacation" -> email
- "List all employees" -> employee
- "Who are the data scientists?" -> employee
- "Send email to john@gmail.com" -> email

Message: {message}

Return JSON with:
- intent: "employee" or "email" (only these two, never "unknown")
- confidence: your confidence level (0.0 to 1.0)
- reasoning: brief explanation of why you chose this intent

{format_instructions}""",
        input_variables=["message"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY, model="openai/gpt-oss-120b", temperature=0
    )

    chain = prompt | llm | parser

    try:
        result = chain.invoke({"message": message})
        return IntentClassification(**result)
    except Exception as e:
        return IntentClassification(
            intent=IntentType.EMPLOYEE,
            confidence=0.5,
            reasoning=f"Classification failed: {str(e)}, defaulting to employee",
        )


def route_message(message: str) -> Literal["employee", "email"]:
    """
    STRICT routing function that uses LLM as PRIMARY method.
    Returns "employee" or "email" based on classified intent.

    Priority:
    1. LLM classification (PRIMARY) - Always runs
    2. Keywords (FALLBACK) - Only if LLM classification fails completely
    """
    message_lower = message.lower()

    # Quick keyword pre-check (optional, can be removed)
    # These are fast checks that might help in edge cases
    email_strong_signals = [
        "send email",
        "send mail",
        "send an email",
        "compose email",
        "write an email",
    ]

    employee_strong_signals = [
        "add employee",
        "store employee",
        "insert employee",
        "delete employee",
        "remove employee",
        "list employees",
        "show employees",
    ]

    # Check strong signals first (fast path)
    for signal in email_strong_signals:
        if signal in message_lower:
            return "email"

    for signal in employee_strong_signals:
        if signal in message_lower:
            return "employee"

    # PRIMARY: Use LLM classification for all other cases
    try:
        result = classify_intent(message)

        # Use LLM result if confidence is reasonable (>= 0.4)
        if result.confidence >= 0.4:
            return result.intent.value

        # If low confidence but still got a valid intent, use it
        if result.intent in (IntentType.EMPLOYEE, IntentType.EMAIL):
            return result.intent.value

    except Exception as e:
        pass

    # FALLBACK: Keyword matching for edge cases where LLM might fail
    employee_keywords = [
        "employee",
        "add",
        "store",
        "insert",
        "update",
        "modify",
        "edit",
        "delete",
        "remove",
        "list",
        "search",
        "find",
        "show",
        "get",
        "job",
        "role",
        "phone",
        "name",
        "database",
    ]

    email_keywords = [
        "email",
        "mail",
        "send",
        "write",
        "compose",
        "to ",
        "@",
    ]

    employee_score = sum(1 for kw in employee_keywords if kw in message_lower)
    email_score = sum(1 for kw in email_keywords if kw in message_lower)

    if employee_score > email_score:
        return "employee"
    elif email_score > employee_score:
        return "email"

    # Default to employee if completely ambiguous
    return "employee"
