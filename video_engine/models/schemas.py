"""
Core data models for video generation system.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationMode(str, Enum):
    """Video generation mode."""
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"


class TransitionType(str, Enum):
    """Transition between shots."""
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE = "wipe"


class Shot(BaseModel):
    """Individual shot specification."""
    id: str = Field(..., description="Unique shot identifier")
    sequence_number: int = Field(..., ge=1)
    duration_seconds: float = Field(..., gt=0, le=10)
    description: str = Field(..., description="Human-readable shot description")
    text_prompt: str = Field(..., description="Prompt for video generation")

    # Optional inputs
    reference_image_path: Optional[str] = None
    first_frame_path: Optional[str] = None
    last_frame_path: Optional[str] = None

    # Generation parameters
    camera_movement: Optional[str] = Field(default="static", description="Camera movement type")
    camera_angle: Optional[str] = Field(default="eye_level", description="Camera angle")
    motion_intensity: float = Field(default=0.5, ge=0.0, le=1.0, description="Motion intensity")

    # Generation settings
    model_id: str = Field(default="replicate:svd-xt")
    num_frames: int = Field(default=81)
    fps: int = Field(default=8)
    guidance_scale: float = Field(default=6.0)
    num_inference_steps: int = Field(default=25)
    seed: Optional[int] = None

    # Transition
    transition_type: TransitionType = Field(default=TransitionType.CUT)
    transition_duration: float = Field(default=0.0, ge=0.0)

    # Output
    output_video_path: Optional[str] = None
    generation_time_seconds: Optional[float] = None


class Storyboard(BaseModel):
    """Complete storyboard for a video."""
    id: str
    title: str
    user_prompt: str
    shots: List[Shot]

    # Metadata
    style: Dict[str, Any] = Field(default_factory=dict)
    total_duration_seconds: float
    shot_count: int
    generated_at: datetime
    generated_by: str = Field(..., description="LLM used for generation")

    def calculate_total_duration(self) -> float:
        """Calculate total video duration including transitions."""
        total = sum(shot.duration_seconds for shot in self.shots)
        total += sum(shot.transition_duration for shot in self.shots[:-1])
        return total


class VideoJob(BaseModel):
    """Video generation job."""
    id: str
    status: JobStatus = Field(default=JobStatus.QUEUED)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Input
    user_prompt: str
    generation_mode: GenerationMode = Field(default=GenerationMode.TEXT_TO_VIDEO)
    model_id: str = Field(default="replicate:svd-xt")
    reference_image_path: Optional[str] = None

    # Storyboard
    storyboard: Optional[Storyboard] = None

    # Progress tracking
    current_step: str = Field(default="initializing")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    current_shot_id: Optional[str] = None

    # Output
    output_video_path: Optional[str] = None
    intermediate_videos: List[str] = Field(default_factory=list)

    # Error handling
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)

    def update_progress(self, step: str, percentage: float, shot_id: Optional[str] = None):
        """Update job progress."""
        self.current_step = step
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.current_shot_id = shot_id
        self.updated_at = datetime.now()

    def mark_failed(self, error: str):
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.now()

    def mark_completed(self, output_path: str):
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.output_video_path = output_path
        self.progress_percentage = 100.0
        self.updated_at = datetime.now()


class ModelCapabilities(BaseModel):
    """Model capabilities specification."""
    supports_text_to_video: bool = False
    supports_image_to_video: bool = False
    supports_video_to_video: bool = False
    supports_first_frame_conditioning: bool = False
    supports_last_frame_conditioning: bool = False

    max_frames: int = 81
    max_duration_seconds: float = 10.0
    recommended_fps: int = 8

    requires_gpu: bool = True
    estimated_vram_gb: float = 8.0


class MemoryRequirements(BaseModel):
    """Model memory requirements."""
    vram_gb: float
    ram_gb: float
    disk_space_gb: float


class VideoGenerationResult(BaseModel):
    """Result of video generation."""
    success: bool
    output_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    num_frames: Optional[int] = None
    error_message: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    name: str
    description: str
    provider: str  # "replicate", "diffusers", "hf_inference"
    capabilities: ModelCapabilities
    memory_requirements: MemoryRequirements
    is_available: bool = False
