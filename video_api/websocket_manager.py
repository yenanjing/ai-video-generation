"""
WebSocket manager for real-time progress updates.
"""
from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages WebSocket connections for job progress updates."""

    def __init__(self):
        """Initialize connection manager."""
        # Map of job_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """
        Accept a new WebSocket connection for a job.

        Args:
            websocket: WebSocket connection
            job_id: Job identifier
        """
        await websocket.accept()

        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()

        self.active_connections[job_id].add(websocket)

    def disconnect(self, websocket: WebSocket, job_id: str):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection
            job_id: Job identifier
        """
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

            # Clean up empty sets
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

    async def send_message(self, job_id: str, message: dict):
        """
        Send a message to all connections for a job.

        Args:
            job_id: Job identifier
            message: Message dictionary
        """
        if job_id not in self.active_connections:
            return

        # Send to all connected clients
        disconnected = set()

        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection closed
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, job_id)

    async def send_progress_update(
        self,
        job_id: str,
        step: str,
        progress: float,
        shot_id: str = None,
    ):
        """
        Send a progress update.

        Args:
            job_id: Job identifier
            step: Current step description
            progress: Progress percentage (0-100)
            shot_id: Optional shot identifier
        """
        message = {
            "type": "progress",
            "job_id": job_id,
            "step": step,
            "progress": progress,
            "message": step,
        }

        if shot_id:
            message["shot_id"] = shot_id

        await self.send_message(job_id, message)

    async def send_shot_complete(
        self,
        job_id: str,
        shot_id: str,
        video_path: str,
    ):
        """
        Send shot completion notification.

        Args:
            job_id: Job identifier
            shot_id: Shot identifier
            video_path: Path to generated shot video
        """
        message = {
            "type": "shot_complete",
            "job_id": job_id,
            "shot_id": shot_id,
            "video_path": video_path,
        }

        await self.send_message(job_id, message)

    async def send_job_complete(
        self,
        job_id: str,
        output_path: str,
    ):
        """
        Send job completion notification.

        Args:
            job_id: Job identifier
            output_path: Path to final video
        """
        message = {
            "type": "job_complete",
            "job_id": job_id,
            "output_path": output_path,
            "message": "Video generation complete!",
        }

        await self.send_message(job_id, message)

    async def send_error(
        self,
        job_id: str,
        error: str,
    ):
        """
        Send error notification.

        Args:
            job_id: Job identifier
            error: Error message
        """
        message = {
            "type": "error",
            "job_id": job_id,
            "error": error,
        }

        await self.send_message(job_id, message)


# Global connection manager instance
manager = ConnectionManager()
