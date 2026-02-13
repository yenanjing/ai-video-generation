# AI Video Generation API - Documentation

FastAPI REST API with WebSocket support for real-time progress updates.

## Base URL

```
http://localhost:8000
```

## Quick Start

### 1. Start the API Server

```bash
python run_api.py
```

Or:
```bash
python -m video_api.main
```

### 2. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## Authentication

Currently no authentication required (Phase 4 will add auth).

---

## REST API Endpoints

### Health Check

**GET** `/api/v1/health`

Check API health and configuration.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_keys_configured": {
    "anthropic": true,
    "replicate": true,
    "openai": false
  },
  "models_available": 2
}
```

---

### Models

#### List Models

**GET** `/api/v1/models?available_only=false`

List all video generation models.

**Query Parameters:**
- `available_only` (boolean): Only return available models

**Response:**
```json
{
  "models": [
    {
      "id": "replicate:svd-xt",
      "name": "SVD XT",
      "description": "svd-xt via replicate",
      "provider": "replicate",
      "is_available": true,
      "capabilities": {
        "supports_text_to_video": false,
        "supports_image_to_video": true,
        "max_frames": 81,
        "recommended_fps": 8
      }
    }
  ],
  "total": 2
}
```

#### Get Model Info

**GET** `/api/v1/models/{model_id}`

Get detailed information about a specific model.

**Response:**
```json
{
  "id": "replicate:svd-xt",
  "name": "SVD XT",
  "capabilities": {...},
  "memory_requirements": {
    "vram_gb": 0.0,
    "ram_gb": 1.0
  }
}
```

---

### Jobs

#### Create Job

**POST** `/api/v1/jobs`

Create a new video generation job.

**Request Body:**
```json
{
  "user_prompt": "A peaceful forest at sunrise",
  "model_id": "replicate:svd-xt",
  "max_shots": 3,
  "style_preferences": {
    "mood": "calm",
    "color_palette": "warm"
  }
}
```

**Response (201):**
```json
{
  "id": "job_abc123",
  "status": "queued",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "user_prompt": "A peaceful forest at sunrise",
  "generation_mode": "text_to_video",
  "model_id": "replicate:svd-xt",
  "current_step": "initializing",
  "progress_percentage": 0.0,
  "output_video_url": null,
  "storyboard": null,
  "error_message": null
}
```

#### List Jobs

**GET** `/api/v1/jobs?page=1&page_size=20&status=processing`

List all jobs with pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20)
- `status` (string): Filter by status (optional)

**Response:**
```json
{
  "jobs": [...],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

#### Get Job

**GET** `/api/v1/jobs/{job_id}`

Get detailed information about a specific job.

**Response:**
```json
{
  "id": "job_abc123",
  "status": "completed",
  "progress_percentage": 100.0,
  "output_video_url": "/videos/job_abc123/final_output.mp4",
  "storyboard": {
    "id": "storyboard_xyz",
    "title": "Forest Sunrise",
    "shots": [...]
  }
}
```

#### Delete Job

**DELETE** `/api/v1/jobs/{job_id}`

Delete a job and its associated files.

**Response:**
```json
{
  "message": "Job job_abc123 deleted successfully"
}
```

#### Download Video

**GET** `/api/v1/jobs/{job_id}/video`

Download the generated video file.

**Response:** Video file (video/mp4)

---

### File Upload

#### Upload Reference Image

**POST** `/api/v1/upload`

Upload a reference image for image-to-video generation.

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (image file)

**Supported Formats:** JPG, JPEG, PNG, WEBP  
**Max Size:** 10MB

**Response:**
```json
{
  "file_id": "upload_abc123",
  "filename": "reference.jpg",
  "file_path": "/workspace/uploads/20240115_103000_reference.jpg",
  "file_size_bytes": 1048576,
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

---

## WebSocket API

### Connect to Job Progress

**WS** `/ws/jobs/{job_id}`

Connect to receive real-time progress updates for a job.

#### Connection Example (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs/job_abc123');

ws.onopen = () => {
  console.log('Connected to job progress');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress update:', data);
  
  switch(data.type) {
    case 'connected':
      console.log('WebSocket connected');
      break;
    case 'progress':
      console.log(`${data.step}: ${data.progress}%`);
      break;
    case 'shot_complete':
      console.log(`Shot ${data.shot_id} complete`);
      break;
    case 'job_complete':
      console.log('Video generation complete!');
      break;
    case 'error':
      console.error('Error:', data.error);
      break;
  }
};

// Keep connection alive
setInterval(() => {
  ws.send('ping');
}, 30000);
```

#### Message Types

**Connected:**
```json
{
  "type": "connected",
  "job_id": "job_abc123",
  "message": "Connected to job job_abc123"
}
```

**Progress Update:**
```json
{
  "type": "progress",
  "job_id": "job_abc123",
  "step": "Generating shot 2 of 3",
  "progress": 45.0,
  "message": "Generating shot 2 of 3",
  "shot_id": "shot_002"
}
```

**Shot Complete:**
```json
{
  "type": "shot_complete",
  "job_id": "job_abc123",
  "shot_id": "shot_002",
  "video_path": "/workspace/videos/job_abc123/shot_002.mp4"
}
```

**Job Complete:**
```json
{
  "type": "job_complete",
  "job_id": "job_abc123",
  "output_path": "/workspace/videos/job_abc123/final_output.mp4",
  "message": "Video generation complete!"
}
```

**Error:**
```json
{
  "type": "error",
  "job_id": "job_abc123",
  "error": "Model inference failed: ..."
}
```

---

## Usage Examples

### Python Client

```python
import requests
import websocket
import json

# Create job
response = requests.post('http://localhost:8000/api/v1/jobs', json={
    'user_prompt': 'Ocean waves at sunset',
    'model_id': 'replicate:svd-xt',
    'max_shots': 3
})

job = response.json()
job_id = job['id']

print(f"Job created: {job_id}")

# Connect to WebSocket
def on_message(ws, message):
    data = json.loads(message)
    print(f"Progress: {data.get('progress', 0)}%")
    
    if data['type'] == 'job_complete':
        print("Complete!")
        ws.close()

ws = websocket.WebSocketApp(
    f'ws://localhost:8000/ws/jobs/{job_id}',
    on_message=on_message
)

ws.run_forever()
```

### cURL

```bash
# Create job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Mountain landscape",
    "model_id": "replicate:svd-xt",
    "max_shots": 3
  }'

# Get job status
curl http://localhost:8000/api/v1/jobs/job_abc123

# List all jobs
curl http://localhost:8000/api/v1/jobs?page=1&page_size=10

# Download video
curl -o video.mp4 http://localhost:8000/api/v1/jobs/job_abc123/video
```

---

## Error Responses

All errors return JSON with this format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

Currently no rate limiting (will be added in Phase 4).

## CORS

CORS is enabled for all origins (development mode).  
In production, configure specific allowed origins in `.env`.

---

## Testing

### Run API Tests

```bash
# Start the API server
python run_api.py

# In another terminal, run tests
python test_api.py
```

### Interactive Testing

Visit http://localhost:8000/docs for interactive API testing with Swagger UI.

---

## Configuration

Environment variables in `.env`:

```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000
ENABLE_CORS=true
MAX_CONCURRENT_JOBS=3
```

---

## Next Steps

- **Phase 3**: React frontend will consume this API
- **Phase 4**: Add authentication, rate limiting, and queue management

For more information, see `README_VIDEO.md`.
