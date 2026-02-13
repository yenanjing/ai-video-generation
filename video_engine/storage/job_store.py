"""
Job storage and metadata management.
"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from video_engine.models.schemas import VideoJob, Storyboard
from video_engine.config import config


class JobStore:
    """Manages job persistence."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize job store.

        Args:
            storage_dir: Directory for job metadata (defaults to config.JOBS_DIR)
        """
        self.storage_dir = storage_dir or config.JOBS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_job(self, job: VideoJob):
        """
        Save job to disk.

        Args:
            job: VideoJob to save
        """
        job_file = self.storage_dir / f"{job.id}.json"

        with open(job_file, "w") as f:
            json.dump(job.model_dump(), f, indent=2, default=str)

    def load_job(self, job_id: str) -> Optional[VideoJob]:
        """
        Load job from disk.

        Args:
            job_id: Job identifier

        Returns:
            VideoJob or None if not found
        """
        job_file = self.storage_dir / f"{job_id}.json"

        if not job_file.exists():
            return None

        with open(job_file, "r") as f:
            data = json.load(f)

        # Parse datetime fields
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Parse nested storyboard
        if data.get("storyboard"):
            storyboard_data = data["storyboard"]
            if "generated_at" in storyboard_data and isinstance(storyboard_data["generated_at"], str):
                storyboard_data["generated_at"] = datetime.fromisoformat(storyboard_data["generated_at"])
            data["storyboard"] = Storyboard(**storyboard_data)

        return VideoJob(**data)

    def delete_job(self, job_id: str) -> bool:
        """
        Delete job from disk.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted
        """
        job_file = self.storage_dir / f"{job_id}.json"

        if job_file.exists():
            job_file.unlink()
            return True

        return False

    def list_jobs(self) -> list[str]:
        """
        List all job IDs.

        Returns:
            List of job IDs
        """
        return [f.stem for f in self.storage_dir.glob("*.json")]

    def save_storyboard(self, storyboard: Storyboard):
        """
        Save storyboard to disk.

        Args:
            storyboard: Storyboard to save
        """
        storyboard_file = self.storage_dir / f"storyboard_{storyboard.id}.json"

        with open(storyboard_file, "w") as f:
            json.dump(storyboard.model_dump(), f, indent=2, default=str)

    def load_storyboard(self, storyboard_id: str) -> Optional[Storyboard]:
        """
        Load storyboard from disk.

        Args:
            storyboard_id: Storyboard identifier

        Returns:
            Storyboard or None if not found
        """
        storyboard_file = self.storage_dir / f"storyboard_{storyboard_id}.json"

        if not storyboard_file.exists():
            return None

        with open(storyboard_file, "r") as f:
            data = json.load(f)

        # Parse datetime
        if "generated_at" in data and isinstance(data["generated_at"], str):
            data["generated_at"] = datetime.fromisoformat(data["generated_at"])

        return Storyboard(**data)
