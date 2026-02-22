"""
API - Employee Chat Endpoint

Handles employee database management requests.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from src.llm.agents.employee_agent import create_employee_agent
from src.memory import (
    add_user_message,
    add_ai_message,
    get_conversation_history,
    clear_conversation,
)
from src.api.session_state import (
    session_files,
    session_generated_files,
    UPLOAD_DIR,
    GENERATED_DIR,
    get_all_session_files,
    cleanup_session_files,
)

router = APIRouter(prefix="", tags=["employee"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    uploaded_files: Optional[List[str]] = None
    generated_files: Optional[List[str]] = None


@router.post("/chat/employee", response_model=ChatResponse)
async def chat_employee(request: ChatRequest):
    """
    Employee management endpoint.
    Handles add, update, delete, search, and list employee operations.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_id = request.session_id or "default"

    UPLOAD_DIR.mkdir(exist_ok=True)
    GENERATED_DIR.mkdir(exist_ok=True)

    agent = create_employee_agent(session_id)

    add_user_message(session_id, request.message)

    conversation_history = get_conversation_history(session_id)

    messages_for_agent = []
    for msg in conversation_history:
        if msg["role"] in ["user", "assistant", "system"]:
            messages_for_agent.append({"role": msg["role"], "content": msg["content"]})

    response = agent.invoke({"messages": messages_for_agent})

    bot_message = response["messages"][-1].content

    add_ai_message(session_id, bot_message)

    uploaded = [os.path.basename(f) for f in session_files.get(session_id, [])]
    generated = [
        os.path.basename(f) for f in session_generated_files.get(session_id, [])
    ]

    return ChatResponse(
        response=bot_message,
        session_id=session_id,
        uploaded_files=uploaded if uploaded else None,
        generated_files=generated if generated else None,
    )
