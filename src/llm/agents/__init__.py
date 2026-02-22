"""
LLM Agents Package

Contains specialized agents for different tasks.
"""

from src.llm.agents.router import route_message, classify_intent
from src.llm.agents.employee_agent import create_employee_agent
from src.llm.agents.email_agent import create_email_agent
