"""
Request schemas for API endpoints.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class CreateJobRequest(BaseModel):
    """Request to create a new video generation job."""
    user_prompt: str = Field(..., min_length=1, max_length=2000, description="Text description of desired video")
    model_id: Optional[str] = Field(None, description="Model to use (defaults to config)")
    max_shots: int = Field(5, ge=1, le=10, description="Maximum number of shots")
    reference_image_url: Optional[str] = Field(None, description="URL to reference image for I2V")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Optional style guidance")

    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "A peaceful forest at sunrise, camera slowly panning through trees",
                "model_id": "replicate:svd-xt",
                "max_shots": 3,
                "style_preferences": {
                    "mood": "calm",
                    "color_palette": "warm"
                }
            }
        }


class GenerateStoryboardRequest(BaseModel):
    """Request to generate a storyboard only."""
    user_prompt: str = Field(..., min_length=1, max_length=2000)
    max_shots: int = Field(5, ge=1, le=10)
    style_preferences: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "A journey through space from Earth to distant galaxy",
                "max_shots": 5
            }
        }


class UpdateJobRequest(BaseModel):
    """Request to update job (e.g., cancel)."""
    action: str = Field(..., description="Action to perform: 'cancel'")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "cancel"
            }
        }
