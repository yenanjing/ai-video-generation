"""
Base model adapter interface.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from PIL import Image

from video_engine.models.schemas import (
    Shot,
    ModelCapabilities,
    MemoryRequirements,
    VideoGenerationResult,
)


class BaseModelAdapter(ABC):
    """Base class for video generation model adapters."""

    def __init__(self, model_id: str):
        """
        Initialize adapter.

        Args:
            model_id: Unique model identifier
        """
        self.model_id = model_id

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if model can be loaded/accessed.

        Returns:
            True if model is available
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> ModelCapabilities:
        """
        Return model capabilities.

        Returns:
            ModelCapabilities object
        """
        pass

    @abstractmethod
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
        Generate video with standardized parameters.

        Args:
            prompt: Text description of desired video
            reference_image: Optional reference image for I2V
            first_frame: Optional first frame conditioning
            last_frame: Optional last frame conditioning
            num_frames: Number of frames to generate
            fps: Frames per second
            guidance_scale: Guidance scale for generation
            num_inference_steps: Number of inference steps
            seed: Random seed for reproducibility
            progress_callback: Optional callback(message, progress) for progress updates
            **kwargs: Additional model-specific parameters

        Returns:
            VideoGenerationResult object
        """
        pass

    @abstractmethod
    def estimate_time(self, shot: Shot) -> float:
        """
        Estimate generation time in seconds.

        Args:
            shot: Shot specification

        Returns:
            Estimated time in seconds
        """
        pass

    @abstractmethod
    def get_memory_requirements(self) -> MemoryRequirements:
        """
        Return memory requirements.

        Returns:
            MemoryRequirements object
        """
        pass

    def generate_from_shot(
        self,
        shot: Shot,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> VideoGenerationResult:
        """
        Convenience method to generate video from Shot object.

        Args:
            shot: Shot specification
            progress_callback: Optional progress callback

        Returns:
            VideoGenerationResult
        """
        # Load images if paths provided
        reference_image = None
        first_frame = None
        last_frame = None

        if shot.reference_image_path:
            reference_image = Image.open(shot.reference_image_path).convert("RGB")

        if shot.first_frame_path:
            first_frame = Image.open(shot.first_frame_path).convert("RGB")

        if shot.last_frame_path:
            last_frame = Image.open(shot.last_frame_path).convert("RGB")

        return self.generate_video(
            prompt=shot.text_prompt,
            reference_image=reference_image,
            first_frame=first_frame,
            last_frame=last_frame,
            num_frames=shot.num_frames,
            fps=shot.fps,
            guidance_scale=shot.guidance_scale,
            num_inference_steps=shot.num_inference_steps,
            seed=shot.seed,
            progress_callback=progress_callback,
        )
