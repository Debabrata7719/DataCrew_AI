"""
Shared Session State

Stores session-level file storage for the API.
"""

from typing import Dict, List
from pathlib import Path
import os
import shutil

UPLOAD_DIR = Path("uploads")
GENERATED_DIR = Path("generated_docs")

session_files: Dict[str, List[str]] = {}
session_generated_files: Dict[str, List[str]] = {}


def cleanup_session_files(session_id: str):
    """Clean up all files for a session."""
    if session_id in session_files:
        for file_path in session_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        del session_files[session_id]

    if session_id in session_generated_files:
        for file_path in session_generated_files[session_id]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        del session_generated_files[session_id]

    for base_dir in [UPLOAD_DIR, GENERATED_DIR]:
        session_dir = base_dir / session_id
        if session_dir.exists():
            try:
                shutil.rmtree(session_dir)
            except Exception:
                pass


def get_session_files(session_id: str) -> List[str]:
    """Get list of uploaded files for a session."""
    return session_files.get(session_id, [])


def get_session_generated_files(session_id: str) -> List[str]:
    """Get list of generated files for a session."""
    return session_generated_files.get(session_id, [])


def add_session_file(session_id: str, file_path: str):
    """Add a file to session storage."""
    if session_id not in session_files:
        session_files[session_id] = []
    session_files[session_id].append(file_path)


def add_session_generated_file(session_id: str, file_path: str):
    """Add a generated file to session storage."""
    if session_id not in session_generated_files:
        session_generated_files[session_id] = []
    session_generated_files[session_id].append(file_path)


def get_all_session_files(session_id: str) -> List[str]:
    """Get all files (uploaded + generated) for a session."""
    files = []
    files.extend(session_files.get(session_id, []))
    files.extend(session_generated_files.get(session_id, []))
    return files
