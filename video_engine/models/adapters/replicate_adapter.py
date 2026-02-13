"""
Replicate API adapter for video generation models.
"""
import time
from typing import Optional, Callable
from pathlib import Path
import replicate
from PIL import Image

from video_engine.models.adapters.base import BaseModelAdapter
from video_engine.models.schemas import (
    Shot,
    ModelCapabilities,
    MemoryRequirements,
    VideoGenerationResult,
)
from video_engine.config import config


class ReplicateAdapter(BaseModelAdapter):
    """Adapter for Replicate cloud models."""

    # Model configurations
    MODELS = {
        "replicate:svd": {
            "name": "Stable Video Diffusion",
            "version": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
            "supports_i2v": True,
            "supports_t2v": False,
            "max_frames": 25,
        },
        "replicate:svd-xt": {
            "name": "Stable Video Diffusion XT",
            "version": "stability-ai/stable-video-diffusion:3f0457e4619daac51203dedb472816fd4af51f3149fa7a9e0b5ffcf1b8172438",
            "supports_i2v": True,
            "supports_t2v": False,
            "max_frames": 81,
        },
    }

    def __init__(self, model_id: str = "replicate:svd-xt"):
        """
        Initialize Replicate adapter.

        Args:
            model_id: Model identifier (e.g., "replicate:svd-xt")
        """
        super().__init__(model_id)

        if not config.REPLICATE_API_TOKEN:
            raise ValueError("REPLICATE_API_TOKEN not configured")

        # Set API token
        self.client = replicate.Client(api_token=config.REPLICATE_API_TOKEN)

        # Get model config
        if model_id not in self.MODELS:
            raise ValueError(f"Unknown Replicate model: {model_id}")

        self.model_config = self.MODELS[model_id]

    def is_available(self) -> bool:
        """Check if Replicate is available."""
        return bool(config.REPLICATE_API_TOKEN)

    def get_capabilities(self) -> ModelCapabilities:
        """Return model capabilities."""
        return ModelCapabilities(
            supports_text_to_video=self.model_config["supports_t2v"],
            supports_image_to_video=self.model_config["supports_i2v"],
            supports_video_to_video=False,
            supports_first_frame_conditioning=True,
            supports_last_frame_conditioning=False,
            max_frames=self.model_config["max_frames"],
            max_duration_seconds=10.0,
            recommended_fps=8,
            requires_gpu=False,  # Cloud model
            estimated_vram_gb=0.0,  # Cloud handles this
        )

    def generate_video(
        self,
        prompt: str,
        *,
        reference_image: Optional[Image.Image] = None,
        first_frame: Optional[Image.Image] = None,
        last_frame: Optional[Image.Image] = None,
        num_frames: int = 81,
        fps: int = 8,
        guidance_scale: float = 6.0,
        num_inference_steps: int = 25,
        seed: Optional[int] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        **kwargs,
    ) -> VideoGenerationResult:
        """
        Generate video using Replicate API.

        Args:
            prompt: Text prompt (note: SVD doesn't use text, only for I2V)
            reference_image: Input image for I2V
            first_frame: First frame conditioning
            num_frames: Number of frames to generate
            fps: Frames per second
            guidance_scale: Motion bucket ID (higher = more motion)
            num_inference_steps: Number of inference steps
            seed: Random seed
            progress_callback: Progress callback
            **kwargs: Additional parameters

        Returns:
            VideoGenerationResult
        """
        start_time = time.time()

        try:
            # Determine input image
            input_image = first_frame or reference_image

            if input_image is None:
                return VideoGenerationResult(
                    success=False,
                    error_message="SVD requires an input image (reference_image or first_frame)",
                )

            # Save image to temporary file
            temp_image_path = config.TEMP_DIR / f"temp_input_{int(time.time())}.png"
            input_image.save(temp_image_path)

            if progress_callback:
                progress_callback("Uploading image to Replicate", 10.0)

            # Prepare inputs for Replicate
            inputs = {
                "input_image": open(temp_image_path, "rb"),
                "video_length": "14_frames_with_svd" if num_frames <= 25 else "25_frames_with_svd_xt",
                "sizing_strategy": "maintain_aspect_ratio",
                "frames_per_second": fps,
                "motion_bucket_id": int(guidance_scale * 20),  # Convert to motion bucket (0-255)
                "cond_aug": 0.02,
            }

            if seed is not None:
                inputs["seed"] = seed

            if progress_callback:
                progress_callback("Starting video generation on Replicate", 20.0)

            # Run prediction
            output = self.client.run(
                self.model_config["version"],
                input=inputs,
            )

            # Clean up temp image
            temp_image_path.unlink(missing_ok=True)

            if progress_callback:
                progress_callback("Downloading generated video", 90.0)

            # Output is a URL to the video file
            if isinstance(output, str):
                video_url = output
            elif isinstance(output, list) and len(output) > 0:
                video_url = output[0]
            else:
                return VideoGenerationResult(
                    success=False,
                    error_message=f"Unexpected output format from Replicate: {type(output)}",
                )

            # Download video
            import requests
            response = requests.get(video_url)
            response.raise_for_status()

            # Save to output file
            output_path = config.TEMP_DIR / f"replicate_output_{int(time.time())}.mp4"
            output_path.write_bytes(response.content)

            generation_time = time.time() - start_time

            if progress_callback:
                progress_callback("Video generation complete", 100.0)

            return VideoGenerationResult(
                success=True,
                output_path=str(output_path),
                duration_seconds=num_frames / fps,
                num_frames=num_frames,
                generation_time_seconds=generation_time,
                metadata={
                    "model": self.model_id,
                    "provider": "replicate",
                },
            )

        except Exception as e:
            return VideoGenerationResult(
                success=False,
                error_message=f"Replicate generation failed: {str(e)}",
                generation_time_seconds=time.time() - start_time,
            )

    def estimate_time(self, shot: Shot) -> float:
        """
        Estimate generation time.

        Args:
            shot: Shot specification

        Returns:
            Estimated time in seconds
        """
        # Replicate typically takes 30-90 seconds depending on queue
        base_time = 60.0

        # Longer videos take more time
        if shot.num_frames > 50:
            base_time += 30.0

        return base_time

    def get_memory_requirements(self) -> MemoryRequirements:
        """Return memory requirements (cloud model)."""
        return MemoryRequirements(
            vram_gb=0.0,  # Cloud handles this
            ram_gb=1.0,  # Minimal local RAM
            disk_space_gb=0.5,  # For temporary files
        )
