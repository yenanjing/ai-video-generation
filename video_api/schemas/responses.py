"""
Response schemas for API endpoints.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from video_engine.models.schemas import (
    JobStatus,
    GenerationMode,
    Shot,
    Storyboard,
    ModelInfo,
)


class JobResponse(BaseModel):
    """Response containing job information."""
    id: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime

    user_prompt: str
    generation_mode: GenerationMode
    model_id: str

    current_step: str
    progress_percentage: float
    current_shot_id: Optional[str] = None

    output_video_url: Optional[str] = None
    storyboard: Optional[Storyboard] = None

    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job_abc123",
                "status": "processing",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:31:30Z",
                "user_prompt": "Forest at sunrise",
                "generation_mode": "text_to_video",
                "model_id": "replicate:svd-xt",
                "current_step": "Generating shot 2/3",
                "progress_percentage": 45.0,
                "output_video_url": None,
                "error_message": None
            }
        }


class JobListResponse(BaseModel):
    """Response containing list of jobs."""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int

    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [],
                "total": 10,
                "page": 1,
                "page_size": 20
            }
        }


class StoryboardResponse(BaseModel):
    """Response containing storyboard information."""
    id: str
    title: str
    user_prompt: str
    shots: List[Shot]
    style: Dict[str, Any]
    total_duration_seconds: float
    shot_count: int
    generated_at: datetime
    generated_by: str


class ModelListResponse(BaseModel):
    """Response containing list of available models."""
    models: List[ModelInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    api_keys_configured: Dict[str, bool]
    models_available: int


class UploadResponse(BaseModel):
    """File upload response."""
    file_id: str
    filename: str
    file_path: str
    file_size_bytes: int
    uploaded_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "file_id": "upload_abc123",
                "filename": "reference.jpg",
                "file_path": "/workspace/uploads/20240115_103000_reference.jpg",
                "file_size_bytes": 1048576,
                "uploaded_at": "2024-01-15T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Job not found",
                "detail": "Job with ID job_abc123 does not exist",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ProgressUpdate(BaseModel):
    """WebSocket progress update message."""
    type: str = "progress"  # "progress", "shot_complete", "job_complete", "error"
    job_id: str
    step: Optional[str] = None
    progress: Optional[float] = None
    message: Optional[str] = None
    shot_id: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "type": "progress",
                "job_id": "job_abc123",
                "step": "generating_shot_2",
                "progress": 45.0,
                "message": "Generating shot 2 of 3 using SVD-XT..."
            }
        }
