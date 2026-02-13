"""
Job management endpoints.
"""
import asyncio
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse

from video_engine.core.orchestrator import VideoOrchestrator
from video_engine.models.schemas import JobStatus
from video_api.schemas.requests import CreateJobRequest, UpdateJobRequest
from video_api.schemas.responses import JobResponse, JobListResponse
from video_api.websocket_manager import manager


router = APIRouter()
orchestrator = VideoOrchestrator()


def convert_job_to_response(job) -> JobResponse:
    """Convert VideoJob to JobResponse."""
    # Generate video URL if available
    output_video_url = None
    if job.output_video_path:
        # Convert to relative URL
        output_video_url = f"/videos/{job.id}/final_output.mp4"

    return JobResponse(
        id=job.id,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        user_prompt=job.user_prompt,
        generation_mode=job.generation_mode,
        model_id=job.model_id,
        current_step=job.current_step,
        progress_percentage=job.progress_percentage,
        current_shot_id=job.current_shot_id,
        output_video_url=output_video_url,
        storyboard=job.storyboard,
        error_message=job.error_message,
    )


async def execute_job_async(job_id: str):
    """
    Execute job in background with WebSocket progress updates.

    Args:
        job_id: Job identifier
    """
    def progress_callback(step: str, progress: float, shot_id: Optional[str] = None):
        """Send progress updates via WebSocket."""
        asyncio.create_task(
            manager.send_progress_update(
                job_id=job_id,
                step=step,
                progress=progress,
                shot_id=shot_id,
            )
        )

    try:
        # Execute job
        job = orchestrator.execute_job(
            job_id=job_id,
            progress_callback=progress_callback,
        )

        # Send completion message
        await manager.send_job_complete(job_id, job.output_video_path)

    except Exception as e:
        # Send error message
        await manager.send_error(job_id, str(e))


@router.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
):
    """
    Create a new video generation job.

    The job will be queued and processed in the background.
    Use WebSocket connection at /ws/jobs/{job_id} to receive real-time progress updates.

    Args:
        request: Job creation parameters

    Returns:
        Created job information
    """
    try:
        # Create job
        job = orchestrator.create_job(
            prompt=request.user_prompt,
            model_id=request.model_id,
            max_shots=request.max_shots,
        )

        # Queue background task
        background_tasks.add_task(execute_job_async, job.id)

        return convert_job_to_response(job)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    page: int = 1,
    page_size: int = 20,
    status: Optional[JobStatus] = None,
):
    """
    List all video generation jobs.

    Args:
        page: Page number (1-indexed)
        page_size: Number of jobs per page
        status: Filter by job status

    Returns:
        Paginated list of jobs
    """
    try:
        # Get all jobs
        all_jobs = orchestrator.list_jobs()

        # Filter by status if specified
        if status:
            all_jobs = [j for j in all_jobs if j.status == status]

        # Sort by created_at (newest first)
        all_jobs.sort(key=lambda j: j.created_at, reverse=True)

        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        jobs_page = all_jobs[start:end]

        # Convert to response objects
        job_responses = [convert_job_to_response(j) for j in jobs_page]

        return JobListResponse(
            jobs=job_responses,
            total=len(all_jobs),
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """
    Get detailed information about a specific job.

    Args:
        job_id: Job identifier

    Returns:
        Job information including progress and storyboard
    """
    job = orchestrator.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    return convert_job_to_response(job)


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its associated files.

    Args:
        job_id: Job identifier

    Returns:
        Success message
    """
    job = orchestrator.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    # Delete job
    success = orchestrator.delete_job(job_id)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete job"
        )

    return {"message": f"Job {job_id} deleted successfully"}


@router.get("/jobs/{job_id}/video")
async def download_video(job_id: str):
    """
    Download the generated video file.

    Args:
        job_id: Job identifier

    Returns:
        Video file
    """
    job = orchestrator.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job not found: {job_id}"
        )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed yet. Current status: {job.status.value}"
        )

    if not job.output_video_path:
        raise HTTPException(
            status_code=404,
            detail="Video file not found"
        )

    from pathlib import Path
    video_path = Path(job.output_video_path)

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Video file not found on disk"
        )

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"{job_id}.mp4"
    )
