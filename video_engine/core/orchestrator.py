"""
Video generation orchestrator - coordinates the full pipeline.
"""
import uuid
import time
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

from video_engine.models.schemas import (
    VideoJob,
    JobStatus,
    GenerationMode,
    Storyboard,
    Shot,
)
from video_engine.llm.storyboard_generator import StoryboardGenerator
from video_engine.models.registry import registry
from video_engine.storage.job_store import JobStore
from video_engine.storage.file_manager import FileManager
from video_engine.utils.video_utils import concatenate_videos
from video_engine.config import config


class VideoOrchestrator:
    """Orchestrates end-to-end video generation pipeline."""

    def __init__(self):
        """Initialize orchestrator."""
        config.ensure_directories()
        self.job_store = JobStore()
        self.file_manager = FileManager()

    def create_job(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        reference_image_path: Optional[str] = None,
        max_shots: int = 5,
        llm: str = "claude",
    ) -> VideoJob:
        """
        Create a new video generation job.

        Args:
            prompt: User's video description
            model_id: Model to use (defaults to config)
            reference_image_path: Optional reference image
            max_shots: Maximum number of shots
            llm: LLM to use for storyboard generation

        Returns:
            VideoJob object
        """
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        model_id = model_id or config.DEFAULT_VIDEO_MODEL

        # Validate model
        if not registry.is_model_available(model_id):
            raise ValueError(f"Model not available: {model_id}")

        # Determine generation mode
        generation_mode = GenerationMode.TEXT_TO_VIDEO
        if reference_image_path:
            generation_mode = GenerationMode.IMAGE_TO_VIDEO

        job = VideoJob(
            id=job_id,
            user_prompt=prompt,
            model_id=model_id,
            generation_mode=generation_mode,
            reference_image_path=reference_image_path,
            status=JobStatus.QUEUED,
        )

        # Save job
        self.job_store.save_job(job)

        return job

    def execute_job(
        self,
        job_id: str,
        progress_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
    ) -> VideoJob:
        """
        Execute a video generation job.

        Args:
            job_id: Job identifier
            progress_callback: Optional callback(step, progress, shot_id)

        Returns:
            Updated VideoJob
        """
        # Load job
        job = self.job_store.load_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        try:
            # Update status
            job.status = JobStatus.PROCESSING
            job.update_progress("Starting video generation", 0.0)
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback("Starting video generation", 0.0, None)

            # Step 1: Generate storyboard (10% of progress)
            job.update_progress("Generating storyboard", 5.0)
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback("Generating storyboard", 5.0, None)

            storyboard = self._generate_storyboard(job)
            job.storyboard = storyboard
            job.update_progress("Storyboard generated", 10.0)
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback("Storyboard generated", 10.0, None)

            # Step 2: Generate individual shots (10% -> 85%)
            shot_videos = self._generate_shots(job, progress_callback)

            # Step 3: Concatenate videos (85% -> 95%)
            job.update_progress("Combining videos", 85.0)
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback("Combining videos", 85.0, None)

            final_video_path = self._concatenate_shots(job, shot_videos)

            # Step 4: Finalize (95% -> 100%)
            job.update_progress("Finalizing", 95.0)
            job.mark_completed(str(final_video_path))
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback("Complete", 100.0, None)

            return job

        except Exception as e:
            # Handle failure
            job.mark_failed(str(e))
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback(f"Failed: {e}", job.progress_percentage, None)

            raise

    def _generate_storyboard(self, job: VideoJob) -> Storyboard:
        """Generate storyboard from job prompt."""
        generator = StoryboardGenerator(llm=config.DEFAULT_LLM)

        # Calculate max shots based on duration limit
        max_shots = min(
            config.MAX_SHOTS_PER_VIDEO,
            int(config.MAX_VIDEO_DURATION / config.DEFAULT_SHOT_DURATION),
        )

        storyboard = generator.generate(
            user_prompt=job.user_prompt,
            max_shots=max_shots,
        )

        # Update shots with job's model and reference image
        for shot in storyboard.shots:
            shot.model_id = job.model_id

            # If job has a reference image, use it for first shot
            if job.reference_image_path and shot.sequence_number == 1:
                shot.reference_image_path = job.reference_image_path

        # Save storyboard
        self.job_store.save_storyboard(storyboard)

        return storyboard

    def _generate_shots(
        self,
        job: VideoJob,
        progress_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
    ) -> list[Path]:
        """Generate individual shot videos."""
        if not job.storyboard:
            raise ValueError("Job has no storyboard")

        shot_videos = []
        shots = job.storyboard.shots
        num_shots = len(shots)

        # Progress range: 10% -> 85% (75% total for all shots)
        progress_per_shot = 75.0 / num_shots

        for i, shot in enumerate(shots):
            # Update progress
            base_progress = 10.0 + (i * progress_per_shot)
            job.update_progress(
                f"Generating shot {i+1}/{num_shots}",
                base_progress,
                shot.id,
            )
            self.job_store.save_job(job)

            if progress_callback:
                progress_callback(
                    f"Generating shot {i+1}/{num_shots}: {shot.description}",
                    base_progress,
                    shot.id,
                )

            # Generate video for shot
            video_path = self._generate_single_shot(
                job=job,
                shot=shot,
                progress_callback=lambda msg, pct: (
                    progress_callback(
                        msg,
                        base_progress + (pct / 100.0 * progress_per_shot * 0.9),  # 90% of shot progress
                        shot.id,
                    ) if progress_callback else None
                ),
            )

            shot_videos.append(video_path)
            job.intermediate_videos.append(str(video_path))

            # Update shot with output path
            shot.output_video_path = str(video_path)

        job.update_progress("All shots generated", 85.0)
        self.job_store.save_job(job)

        return shot_videos

    def _generate_single_shot(
        self,
        job: VideoJob,
        shot: Shot,
        progress_callback: Optional[Callable[[str, float], None]] = None,
    ) -> Path:
        """Generate video for a single shot."""
        # Get model adapter
        adapter = registry.get_adapter(shot.model_id)
        if not adapter:
            raise ValueError(f"Model not found: {shot.model_id}")

        # Generate video
        result = adapter.generate_from_shot(
            shot=shot,
            progress_callback=progress_callback,
        )

        if not result.success:
            raise RuntimeError(f"Shot generation failed: {result.error_message}")

        # Move to job output directory
        output_path = self.file_manager.get_shot_output_path(job.id, shot.id)
        temp_path = Path(result.output_path)

        if temp_path != output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.rename(output_path)

        # Update shot metadata
        shot.generation_time_seconds = result.generation_time_seconds

        return output_path

    def _concatenate_shots(self, job: VideoJob, shot_videos: list[Path]) -> Path:
        """Concatenate shot videos into final output."""
        output_path = self.file_manager.get_final_output_path(job.id)

        # Get transition duration from first shot (if any)
        transition_duration = 0.0
        if job.storyboard and job.storyboard.shots:
            transition_duration = job.storyboard.shots[0].transition_duration

        success = concatenate_videos(
            input_paths=shot_videos,
            output_path=output_path,
            transition_duration=transition_duration,
        )

        if not success:
            raise RuntimeError("Failed to concatenate videos")

        return output_path

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        """Get job by ID."""
        return self.job_store.load_job(job_id)

    def list_jobs(self) -> list[VideoJob]:
        """List all jobs."""
        jobs = []
        for job_id in self.job_store.list_jobs():
            job = self.job_store.load_job(job_id)
            if job:
                jobs.append(job)
        return jobs

    def delete_job(self, job_id: str) -> bool:
        """Delete job and its files."""
        self.file_manager.cleanup_job(job_id)
        return self.job_store.delete_job(job_id)
