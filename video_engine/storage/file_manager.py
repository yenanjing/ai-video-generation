"""
File management utilities.
"""
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from video_engine.config import config


class FileManager:
    """Manages file storage and cleanup."""

    @staticmethod
    def get_job_output_dir(job_id: str) -> Path:
        """
        Get output directory for a job.

        Args:
            job_id: Job identifier

        Returns:
            Path to job output directory
        """
        job_dir = config.VIDEO_OUTPUT_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    @staticmethod
    def get_shot_output_path(job_id: str, shot_id: str) -> Path:
        """
        Get output path for a shot video.

        Args:
            job_id: Job identifier
            shot_id: Shot identifier

        Returns:
            Path to shot video file
        """
        job_dir = FileManager.get_job_output_dir(job_id)
        return job_dir / f"{shot_id}.mp4"

    @staticmethod
    def get_final_output_path(job_id: str) -> Path:
        """
        Get path for final concatenated video.

        Args:
            job_id: Job identifier

        Returns:
            Path to final video file
        """
        job_dir = FileManager.get_job_output_dir(job_id)
        return job_dir / "final_output.mp4"

    @staticmethod
    def save_uploaded_file(file_data: bytes, filename: str) -> Path:
        """
        Save uploaded file.

        Args:
            file_data: File data
            filename: Original filename

        Returns:
            Path to saved file
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = Path(filename).stem[:50]  # Limit length
        extension = Path(filename).suffix

        output_path = config.VIDEO_UPLOAD_DIR / f"{timestamp}_{safe_filename}{extension}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_bytes(file_data)
        return output_path

    @staticmethod
    def cleanup_job(job_id: str):
        """
        Clean up all files for a job.

        Args:
            job_id: Job identifier
        """
        job_dir = config.VIDEO_OUTPUT_DIR / job_id

        if job_dir.exists():
            shutil.rmtree(job_dir)

    @staticmethod
    def cleanup_old_files(days: int = 7):
        """
        Clean up files older than specified days.

        Args:
            days: Number of days to keep files
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Clean up videos
        for job_dir in config.VIDEO_OUTPUT_DIR.iterdir():
            if job_dir.is_dir():
                mtime = datetime.fromtimestamp(job_dir.stat().st_mtime)
                if mtime < cutoff_date:
                    shutil.rmtree(job_dir)

        # Clean up uploads
        for upload_file in config.VIDEO_UPLOAD_DIR.iterdir():
            if upload_file.is_file():
                mtime = datetime.fromtimestamp(upload_file.stat().st_mtime)
                if mtime < cutoff_date:
                    upload_file.unlink()

        # Clean up temp files
        for temp_file in config.TEMP_DIR.iterdir():
            if temp_file.is_file():
                mtime = datetime.fromtimestamp(temp_file.stat().st_mtime)
                # Keep temp files for only 1 day
                if mtime < (datetime.now() - timedelta(days=1)):
                    temp_file.unlink()

    @staticmethod
    def get_disk_usage() -> dict:
        """
        Get disk usage statistics.

        Returns:
            Dictionary with usage stats
        """
        def get_dir_size(path: Path) -> int:
            """Get total size of directory in bytes."""
            total = 0
            for item in path.rglob("*"):
                if item.is_file():
                    total += item.stat().st_size
            return total

        return {
            "videos_mb": get_dir_size(config.VIDEO_OUTPUT_DIR) / (1024 * 1024),
            "uploads_mb": get_dir_size(config.VIDEO_UPLOAD_DIR) / (1024 * 1024),
            "temp_mb": get_dir_size(config.TEMP_DIR) / (1024 * 1024),
        }
