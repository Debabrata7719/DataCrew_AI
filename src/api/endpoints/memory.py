"""
API - Memory Endpoints

Handles memory/stats requests.
"""

from fastapi import APIRouter
from src.memory import get_stats, get_context_for_ai

router = APIRouter(prefix="", tags=["memory"])


@router.get("/memory/stats/{session_id}")
async def memory_stats(session_id: str):
    """Get memory statistics for a session."""
    stats = get_stats(session_id)
    context = get_context_for_ai(session_id)

    return {"session_id": session_id, "stats": stats, "context_summary": context}
