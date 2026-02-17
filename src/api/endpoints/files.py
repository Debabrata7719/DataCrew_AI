"""
API - Files Endpoints

Handles file upload, delete, and list operations.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import os

from src.api.session_state import (
    session_files,
    session_generated_files,
    UPLOAD_DIR,
    GENERATED_DIR,
    add_session_file,
)

router = APIRouter(prefix="", tags=["files"])


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), session_id: str = Form("default")):
    """Upload a file to attach to an email."""
    try:
        UPLOAD_DIR.mkdir(exist_ok=True)

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 25MB)")

        session_dir = UPLOAD_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        file_path = session_dir / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        add_session_file(session_id, str(file_path))

        return {
            "status": "success",
            "filename": file.filename,
            "message": f"File '{file.filename}' uploaded successfully",
            "session_id": session_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.delete("/delete-file")
async def delete_file(
    filename: str, session_id: str = "default", file_type: str = "uploaded"
):
    """Delete an uploaded or generated file."""
    try:
        files_dict = (
            session_files if file_type == "uploaded" else session_generated_files
        )

        if session_id in files_dict:
            for i, file_path in enumerate(files_dict[session_id]):
                if os.path.basename(file_path) == filename:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    files_dict[session_id].pop(i)
                    return {
                        "status": "success",
                        "message": f"File '{filename}' deleted",
                    }

        raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/list-files/{session_id}")
async def list_files(session_id: str):
    """List all files (uploaded + generated) for a session."""
    uploaded = [os.path.basename(f) for f in session_files.get(session_id, [])]
    generated = [
        os.path.basename(f) for f in session_generated_files.get(session_id, [])
    ]

    return {
        "session_id": session_id,
        "uploaded_files": uploaded,
        "generated_files": generated,
        "total_count": len(uploaded) + len(generated),
    }
