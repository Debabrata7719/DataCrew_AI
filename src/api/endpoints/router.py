"""
API - Router Endpoint

Routes incoming messages to the appropriate specialized agent.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from src.llm.agents.router import route_message

router = APIRouter(prefix="", tags=["router"])


class RouteRequest(BaseModel):
    message: str


class RouteResponse(BaseModel):
    endpoint: Literal["/chat/employee", "/chat/email"]
    intent: str


@router.post("/chat/route", response_model=RouteResponse)
async def route_chat_message(request: RouteRequest):
    """
    Route a chat message to the appropriate agent endpoint.
    Uses LLM-based intent classification to determine if message
    is about employee management or email sending.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    endpoint = route_message(request.message)

    return RouteResponse(endpoint=endpoint, intent=endpoint)
