"""
WebSocket route for real-time progress updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from video_api.websocket_manager import manager


router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates.

    Connect to this endpoint to receive updates about a specific job:
    - Progress updates
    - Shot completion notifications
    - Job completion
    - Error messages

    Args:
        websocket: WebSocket connection
        job_id: Job identifier

    Message format:
        {
            "type": "progress" | "shot_complete" | "job_complete" | "error",
            "job_id": "job_123",
            "step": "Generating shot 2",
            "progress": 45.0,
            "message": "...",
            ...
        }
    """
    await manager.connect(websocket, job_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "job_id": job_id,
            "message": f"Connected to job {job_id}",
        })

        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages (client can send ping to keep alive)
            data = await websocket.receive_text()

            # Echo back (for ping/pong)
            if data == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"WebSocket error for job {job_id}: {e}")
        manager.disconnect(websocket, job_id)
