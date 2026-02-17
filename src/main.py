"""
DebAI Email Assistant - FastAPI Server (Hybrid Edition)

Web API server with:
- User file uploads (Option B)
- AI document generation (Option A)
- Session-based conversation memory
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool
import os
import shutil
import json
from pathlib import Path

from src.email_service import send_email_direct
from src.config import GROQ_API_KEY, EMAIL_ADDRESS
from src.document_generator import DocumentGenerator, generate_report, generate_spreadsheet
from src.memory_system import (
    conversation_memory,
    add_user_message,
    add_ai_message,
    get_conversation_history,
    get_context_for_ai,
    clear_conversation,
    get_stats
)

# Initialize FastAPI app
app = FastAPI(
    title="DebAI - Email Assistant API (Hybrid)",
    description="AI-powered email assistant with file uploads AND document generation",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path("uploads")
GENERATED_DIR = Path("generated_docs")
UPLOAD_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)

# Initialize document generator
doc_generator = DocumentGenerator(str(GENERATED_DIR))

# Initialize LLM
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="openai/gpt-oss-120b",
    temperature=0
)

# Session storage
session_files: Dict[str, List[str]] = {}
session_generated_files: Dict[str, List[str]] = {}
current_session_context: Dict[str, str] = {}  # For passing session_id to tools

# Define document generation tools

@tool
def create_word_document(title: str, content: str, filename: str) -> str:
    """
    Create a Microsoft Word document (.docx) with the given content.
    
    Args:
        title: Document title
        content: Main text content
        filename: Filename without extension (e.g., 'report' not 'report.docx')
    
    Returns:
        Success message with filename
    """
    # Get session_id from global context
    session_id = current_session_context.get("session_id", "default")
    
    try:
        # Parse sections if content has headers
        sections = []
        if "\n## " in content or "\n# " in content:
            parts = content.split("\n## ")
            main_content = parts[0].strip()
            for part in parts[1:]:
                lines = part.split("\n", 1)
                heading = lines[0].strip()
                text = lines[1].strip() if len(lines) > 1 else ""
                sections.append({"heading": heading, "text": text})
        else:
            main_content = content
        
        # Create document in session subdirectory
        session_dir = GENERATED_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_docx(filename, title, main_content, sections if sections else None)
        
        # Store in session
        if session_id not in session_generated_files:
            session_generated_files[session_id] = []
        session_generated_files[session_id].append(filepath)
        
        print(f"[DEBUG] Created Word doc at: {filepath}")
        
        return f"✅ Word document created: {filename}.docx"
    except Exception as e:
        return f"❌ Error creating Word document: {str(e)}"


@tool
def create_pdf_document(title: str, content: str, filename: str) -> str:
    """
    Create a PDF document with the given content.
    
    Args:
        title: Document title
        content: Main text content
        filename: Filename without extension
    
    Returns:
        Success message with filename
    """
    # Get session_id from global context
    session_id = current_session_context.get("session_id", "default")
    
    try:
        # Parse sections
        sections = []
        if "\n## " in content:
            parts = content.split("\n## ")
            main_content = parts[0].strip()
            for part in parts[1:]:
                lines = part.split("\n", 1)
                heading = lines[0].strip()
                text = lines[1].strip() if len(lines) > 1 else ""
                sections.append({"heading": heading, "text": text})
        else:
            main_content = content
        
        session_dir = GENERATED_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_pdf(filename, title, main_content, sections if sections else None)
        
        if session_id not in session_generated_files:
            session_generated_files[session_id] = []
        session_generated_files[session_id].append(filepath)
        
        print(f"[DEBUG] Created PDF at: {filepath}")
        
        return f"✅ PDF document created: {filename}.pdf"
    except Exception as e:
        return f"❌ Error creating PDF: {str(e)}"


@tool
def create_excel_spreadsheet(
    filename: str,
    sheet_name: str,
    headers_json: str,
    data_json: str,
    title: Optional[str] = None
) -> str:
    """
    Create an Excel spreadsheet with the given data.
    
    Args:
        filename: Filename without extension
        sheet_name: Name for the worksheet
        headers_json: JSON string of column headers (e.g., '["Name", "Age", "City"]')
        data_json: JSON string of 2D array data (e.g., '[["John", 30, "NYC"], ["Jane", 25, "LA"]]')
        title: Optional title for the spreadsheet
    
    Returns:
        Success message with filename
    """
    # Get session_id from global context
    session_id = current_session_context.get("session_id", "default")
    
    try:
        headers = json.loads(headers_json)
        data = json.loads(data_json)
        
        session_dir = GENERATED_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_xlsx(filename, sheet_name, headers, data, title)
        
        if session_id not in session_generated_files:
            session_generated_files[session_id] = []
        session_generated_files[session_id].append(filepath)
        
        print(f"[DEBUG] Created Excel at: {filepath}")
        
        return f"✅ Excel spreadsheet created: {filename}.xlsx"
    except json.JSONDecodeError:
        return "❌ Error: Invalid JSON format for headers or data"
    except Exception as e:
        return f"❌ Error creating Excel file: {str(e)}"


@tool
def create_text_file(content: str, filename: str) -> str:
    """
    Create a plain text file with the given content.
    
    Args:
        content: Text content
        filename: Filename without extension
    
    Returns:
        Success message with filename
    """
    # Get session_id from global context
    session_id = current_session_context.get("session_id", "default")
    
    try:
        session_dir = GENERATED_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        generator = DocumentGenerator(str(session_dir))
        filepath = generator.create_txt(filename, content)
        
        if session_id not in session_generated_files:
            session_generated_files[session_id] = []
        session_generated_files[session_id].append(filepath)
        
        print(f"[DEBUG] Created text file at: {filepath}")
        
        return f"✅ Text file created: {filename}.txt"
    except Exception as e:
        return f"❌ Error creating text file: {str(e)}"


@tool
def send_email_tool(receiver_email: str, subject: str, message: str) -> str:
    """
    Send an email with optional attachments (uploaded files + generated documents).
    Automatically uses files from the current session.
    
    Args:
        receiver_email: Recipient email address
        subject: Email subject
        message: Email body
    
    Returns:
        Success/failure message
    """
    # Get session_id from global context
    session_id = current_session_context.get("session_id", "default")
    
    # Combine uploaded files and generated files
    all_files = []
    if session_id in session_files:
        all_files.extend(session_files[session_id])
        print(f"[DEBUG] Found {len(session_files[session_id])} uploaded files for session {session_id}")
    if session_id in session_generated_files:
        all_files.extend(session_generated_files[session_id])
        print(f"[DEBUG] Found {len(session_generated_files[session_id])} generated files for session {session_id}")
    
    print(f"[DEBUG] Total files to attach: {len(all_files)}")
    print(f"[DEBUG] File paths: {all_files}")
    
    result = send_email_direct(
        receiver_email, 
        subject, 
        message, 
        all_files if all_files else None
    )
    
    # Clean up all files after sending
    cleanup_session_files(session_id)
    
    return result


def cleanup_session_files(session_id: str):
    """Clean up all files (uploaded + generated) for a session."""
    # Clean uploaded files
    if session_id in session_files:
        for file_path in session_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up uploaded file: {e}")
        del session_files[session_id]
    
    # Clean generated files
    if session_id in session_generated_files:
        for file_path in session_generated_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up generated file: {e}")
        del session_generated_files[session_id]
    
    # Remove session directories
    for base_dir in [UPLOAD_DIR, GENERATED_DIR]:
        session_dir = base_dir / session_id
        if session_dir.exists():
            try:
                shutil.rmtree(session_dir)
            except Exception as e:
                print(f"Error removing session directory: {e}")


# Create agent with all tools
agent = create_agent(
    model=llm,
    tools=[
        send_email_tool,
        create_word_document,
        create_pdf_document,
        create_excel_spreadsheet,
        create_text_file
    ],
    system_prompt="""You are DebAI, an AI assistant that helps users send emails with attachments. You have two powerful capabilities:

1. **Sending Uploaded Files**: When users upload files, you can send them via email.

2. **Creating Documents**: You can CREATE documents on-demand:
   - Word documents (.docx) - use create_word_document
   - PDF documents (.pdf) - use create_pdf_document  
   - Excel spreadsheets (.xlsx) - use create_excel_spreadsheet
   - Text files (.txt) - use create_text_file

**When to Create Documents:**
- User says "create a report/document/spreadsheet"
- User says "generate a [document type]"
- User wants you to write content and send it as a file
- User asks for formatted documents

**Examples:**
- "Create a sales report and send it to boss@company.com" → create_word_document → send_email_tool
- "Generate a meeting agenda PDF" → create_pdf_document
- "Make a spreadsheet with Q1 data and email it" → create_excel_spreadsheet → send_email_tool

**Important:**
- For Word/PDF: Pass title, content, and filename
- For Excel: Use JSON format for headers and data
- Always create the document BEFORE sending the email
- Files are automatically attached when you call send_email_tool
- Don't include sign-offs in email body - they're added automatically
- Be professional and helpful!""",
    debug=True,
)

# Session storage for conversation - Now handled by memory_system.py
# conversation_memory is imported from memory_system

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    uploaded_files: Optional[List[str]] = None
    generated_files: Optional[List[str]] = None

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "DebAI Email Assistant API (Hybrid Edition)",
        "version": "3.0.0",
        "status": "active",
        "features": [
            "conversation_memory",
            "file_uploads",
            "document_generation",
            "ai_powered_document_creation"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_api_configured": bool(GROQ_API_KEY),
        "email_configured": bool(EMAIL_ADDRESS),
        "upload_dir": str(UPLOAD_DIR),
        "generated_dir": str(GENERATED_DIR)
    }

@app.post("/upload-file")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form("default")
):
    """Upload a file to attach to an email."""
    try:
        # Check file size (25MB limit)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 25MB)")
        
        session_dir = UPLOAD_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        file_path = session_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if session_id not in session_files:
            session_files[session_id] = []
        session_files[session_id].append(str(file_path))
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": f"File '{file.filename}' uploaded successfully",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@app.delete("/delete-file")
async def delete_file(filename: str, session_id: str = "default", file_type: str = "uploaded"):
    """Delete an uploaded or generated file."""
    try:
        files_dict = session_files if file_type == "uploaded" else session_generated_files
        
        if session_id in files_dict:
            for i, file_path in enumerate(files_dict[session_id]):
                if os.path.basename(file_path) == filename:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    files_dict[session_id].pop(i)
                    return {"status": "success", "message": f"File '{filename}' deleted"}
        
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.get("/list-files/{session_id}")
async def list_files(session_id: str):
    """List all files (uploaded + generated) for a session."""
    uploaded = [os.path.basename(f) for f in session_files.get(session_id, [])]
    generated = [os.path.basename(f) for f in session_generated_files.get(session_id, [])]
    
    return {
        "session_id": session_id,
        "uploaded_files": uploaded,
        "generated_files": generated,
        "total_count": len(uploaded) + len(generated)
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with enhanced memory system."""
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        session_id = request.session_id or "default"
        
        # SET GLOBAL SESSION CONTEXT
        current_session_context["session_id"] = session_id
        
        # Debug logging
        print(f"\n[DEBUG] === New Chat Request ===")
        print(f"[DEBUG] Session ID: {session_id}")
        print(f"[DEBUG] Message: {request.message}")
        print(f"[DEBUG] Uploaded files: {session_files.get(session_id, [])}")
        print(f"[DEBUG] Generated files: {session_generated_files.get(session_id, [])}")
        
        # Get session stats
        stats = get_stats(session_id)
        print(f"[DEBUG] Session stats: {stats}")
        
        # Add user message to memory
        add_user_message(session_id, request.message)
        
        # Get conversation history from memory system
        conversation_history = get_conversation_history(session_id)
        
        # Convert to format expected by agent
        messages_for_agent = []
        for msg in conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages_for_agent.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        print(f"[DEBUG] Memory contains {len(messages_for_agent)} messages")
        
        # Invoke agent with conversation history
        response = agent.invoke(
            {"messages": messages_for_agent}
        )
        
        bot_message = response["messages"][-1].content
        
        print(f"[DEBUG] AI Response: {bot_message}")
        
        # Add AI response to memory
        add_ai_message(session_id, bot_message)
        
        print(f"[DEBUG] === End Chat Request ===\n")
        
        # Get file info
        uploaded = [os.path.basename(f) for f in session_files.get(session_id, [])]
        generated = [os.path.basename(f) for f in session_generated_files.get(session_id, [])]
        
        return ChatResponse(
            response=bot_message,
            session_id=session_id,
            uploaded_files=uploaded if uploaded else None,
            generated_files=generated if generated else None
        )
    
    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/chat/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history and all files using enhanced memory system."""
    # Clear memory system
    clear_conversation(session_id)
    
    # Clean up files
    cleanup_session_files(session_id)
    
    return {"status": "success", "message": f"History and files cleared for session: {session_id}"}

@app.get("/memory/stats/{session_id}")
async def memory_stats(session_id: str):
    """Get memory statistics for a session."""
    stats = get_stats(session_id)
    context = get_context_for_ai(session_id)
    
    return {
        "session_id": session_id,
        "stats": stats,
        "context_summary": context
    }

# Mount static files
app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting DebAI Email Assistant API v3.0 (Hybrid Edition)...")
    print("📧 Frontend: http://127.0.0.1:8000/app/")
    print("🔗 API docs: http://127.0.0.1:8000/docs")
    print("📎 File uploads: ENABLED")
    print("📝 Document generation: ENABLED")
    uvicorn.run(app, host="127.0.0.1", port=8000)
