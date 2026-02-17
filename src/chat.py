"""
DebAI Email Assistant - MCP Powered AI Agent

This version uses an in-process FastMCP client and exposes an email tool
to the LangChain agent.
"""

import asyncio
from typing import Any

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from fastmcp import Client

from config import GROQ_API_KEY
from email_service import mcp as email_mcp_server


def _tool_result_to_text(result: Any) -> str:
    """Normalize FastMCP call result into a plain text response."""
    if getattr(result, "data", None) is not None:
        return str(result.data)
    if getattr(result, "structured_content", None) is not None:
        return str(result.structured_content)

    text_blocks: list[str] = []
    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if text:
            text_blocks.append(text)

    if text_blocks:
        return "\n".join(text_blocks)
    return "Tool executed successfully."


def _message_content_to_text(content: Any) -> str:
    """Extract readable text from model content blocks."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
                continue

            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    text_parts.append(text.strip())
                continue

            text = getattr(item, "text", None)
            if isinstance(text, str) and text.strip():
                text_parts.append(text.strip())

        if text_parts:
            return "\n".join(text_parts)

    return str(content)


async def _send_email_via_mcp(
    receiver_email: str,
    subject: str,
    message: str,
) -> str:
    """Call MCP `send_email` tool using in-process FastMCP server."""
    client = Client(email_mcp_server)

    async with client:
        result = await client.call_tool(
            "send_email",
            {
                "receiver_email": receiver_email,
                "subject": subject,
                "message": message,
            },
        )
    return _tool_result_to_text(result)


@tool
def send_email_tool(receiver_email: str, subject: str, message: str) -> str:
    """Send an email via MCP email service."""
    try:
        return asyncio.run(_send_email_via_mcp(receiver_email, subject, message))
    except Exception as exc:
        return f"Failed to send email via MCP: {exc}"


llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0,
)


agent = create_agent(
    model=llm,
    tools=[send_email_tool],
    system_prompt=(
        "You are an AI email assistant. "
        "You help users compose and send emails. "
        "When writing email body, do NOT include signatures "
        "because they are added automatically."
    ),
    debug=False,
)


def chatbot() -> None:
    """Run interactive CLI chat loop with short conversation memory."""
    print("DebAI MCP Email Assistant Ready!")
    print("Type 'exit' to quit.\n")

    conversation_history = []
    max_messages = 10

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("\nGoodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})
        if len(conversation_history) > max_messages:
            conversation_history = conversation_history[-max_messages:]

        response = agent.invoke({"messages": conversation_history})
        last_message = response["messages"][-1]
        bot_message = _message_content_to_text(
            getattr(last_message, "content", last_message)
        )

        conversation_history.append({"role": "assistant", "content": bot_message})
        if len(conversation_history) > max_messages:
            conversation_history = conversation_history[-max_messages:]

        print("\nBot:", bot_message, "\n")


if __name__ == "__main__":
    chatbot()
