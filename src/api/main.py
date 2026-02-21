"""
FastAPI Application

Main entry point for the DataCrew AI Email Assistant API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.config import GROQ_API_KEY, EMAIL_ADDRESS
from src.api.endpoints import files, memory, employee, email, router

app = FastAPI(
    title="DataCrew AI - Email Assistant API",
    description="AI-powered email assistant with document generation",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router)
app.include_router(memory.router)
app.include_router(employee.router)
app.include_router(email.router)
app.include_router(router.router)

UPLOAD_DIR = Path("uploads")
GENERATED_DIR = Path("generated_docs")
UPLOAD_DIR.mkdir(exist_ok=True)
GENERATED_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "DataCrew AI Email Assistant API",
        "version": "4.0.0",
        "status": "active",
        "features": [
            "conversation_memory",
            "file_uploads",
            "document_generation",
            "ai_chat",
        ],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "groq_api_configured": bool(GROQ_API_KEY),
        "email_configured": bool(EMAIL_ADDRESS),
        "upload_dir": str(UPLOAD_DIR),
        "generated_dir": str(GENERATED_DIR),
    }


app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    print("DataCrew AI Email Assistant API v4.0.0")
    print("Frontend: http://127.0.0.1:8000/app/")
    print("API docs: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
