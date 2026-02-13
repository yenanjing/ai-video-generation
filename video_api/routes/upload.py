"""
File upload endpoints.
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path

from video_engine.storage.file_manager import FileManager
from video_api.schemas.responses import UploadResponse


router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a reference image for image-to-video generation.

    Supported formats: JPG, JPEG, PNG, WEBP

    Returns:
        Upload information including file path and ID
    """
    # Check file type
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file data
    try:
        file_data = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read file: {str(e)}"
        )

    # Check file size (limit to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_data) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB"
        )

    # Save file
    try:
        file_path = FileManager.save_uploaded_file(file_data, file.filename)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # Generate file ID
    file_id = f"upload_{uuid.uuid4().hex[:12]}"

    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        file_path=str(file_path),
        file_size_bytes=len(file_data),
        uploaded_at=datetime.now(),
    )
