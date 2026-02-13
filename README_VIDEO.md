# AI Video Generation System

A multi-stage AI video generation pipeline that creates videos from text prompts using LLM-powered storyboarding and state-of-the-art video generation models.

## Features

- **Intelligent Storyboarding**: Uses Claude/GPT to break down prompts into detailed shot sequences
- **Multiple Models**: Support for Replicate, HuggingFace, and local models
- **Image-to-Video**: Generate videos from reference images
- **Real-time Progress**: Track generation progress for each shot
- **Production-Ready**: FastAPI backend + React frontend (Phases 2-3)

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg
```

### 2. Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-xxx  # Required: for storyboard generation
REPLICATE_API_TOKEN=r8_xxx     # Required: for video generation
```

Get your API keys:
- Anthropic: https://console.anthropic.com/
- Replicate: https://replicate.com/account/api-tokens

### 3. Generate Your First Video

```bash
python -m video_engine.cli generate "A peaceful forest at dawn, camera slowly panning through trees"
```

This will:
1. Generate a storyboard with 3-5 shots
2. Create video for each shot using Stable Video Diffusion
3. Concatenate shots into a final video
4. Save to `workspace/videos/{job_id}/final_output.mp4`

## CLI Usage

### Generate Video

```bash
# Basic generation
python -m video_engine.cli generate "Your prompt here"

# With options
python -m video_engine.cli generate "Mountain sunset" \
  --model replicate:svd-xt \
  --max-shots 3 \
  --output my_video.mp4
```

### Generate Storyboard Only

```bash
python -m video_engine.cli storyboard "Your prompt" --output storyboard.json
```

### List Available Models

```bash
python -m video_engine.cli list-models
```

### Manage Jobs

```bash
# List all jobs
python -m video_engine.cli list-jobs

# Get job details
python -m video_engine.cli get-job job_abc123
```

## Architecture

```
User Prompt
    ↓
LLM Storyboard Generation (Claude/GPT)
    ↓
Individual Shot Generation (Replicate/HF/Local)
    ↓
Video Concatenation (FFmpeg)
    ↓
Final Video Output
```

## Project Structure

```
ai-video/
├── video_engine/           # Core video generation engine
│   ├── cli.py             # Command-line interface
│   ├── config.py          # Configuration
│   ├── core/
│   │   └── orchestrator.py # Pipeline coordinator
│   ├── llm/
│   │   ├── claude_client.py
│   │   └── storyboard_generator.py
│   ├── models/
│   │   ├── schemas.py     # Data models
│   │   ├── registry.py    # Model registry
│   │   └── adapters/
│   │       ├── base.py
│   │       └── replicate_adapter.py
│   ├── storage/
│   │   ├── job_store.py
│   │   └── file_manager.py
│   └── utils/
│       └── video_utils.py  # FFmpeg utilities
├── workspace/
│   ├── videos/            # Generated videos
│   ├── uploads/           # User uploads
│   ├── jobs/              # Job metadata
│   └── temp/              # Temporary files
└── README_VIDEO.md        # This file
```

## Models

### Currently Supported

- **Replicate: SVD** - Stable Video Diffusion (14-25 frames)
- **Replicate: SVD-XT** - Extended version (up to 81 frames)

### Coming Soon

- CogVideoX (text-to-video)
- Local HuggingFace models
- Custom fine-tuned models

## Development Roadmap

### ✅ Phase 1: Core Engine (Complete)
- LLM storyboard generation
- Replicate adapter
- Video concatenation
- CLI interface

### 🚧 Phase 2: API Backend (Next)
- FastAPI REST endpoints
- WebSocket progress streaming
- Background job management
- File upload handling

### 📋 Phase 3: React Frontend
- Web UI with real-time updates
- Storyboard editor
- Video player
- Model selection

### 🔮 Phase 4: Production Features
- Additional model adapters
- Job queue with Celery
- User authentication
- Video editing/post-processing

## Examples

### Text-to-Video with Multiple Shots

```bash
python -m video_engine.cli generate \
  "A day in the life of a robot: waking up, making coffee, going to work" \
  --max-shots 5 \
  --output robot_day.mp4
```

### Image-to-Video

```bash
python -m video_engine.cli generate \
  "The image comes to life with subtle movements" \
  --reference-image my_image.jpg \
  --output animated.mp4
```

## Configuration Options

Edit `.env` to customize:

```bash
# Limits
MAX_VIDEO_DURATION=60           # Maximum total video length
MAX_SHOTS_PER_VIDEO=10          # Maximum shots per video

# Model defaults
DEFAULT_VIDEO_MODEL=replicate:svd-xt
DEFAULT_LLM=claude

# Future: Local GPU models
ENABLE_LOCAL_MODELS=false
GPU_MEMORY_FRACTION=0.9
```

## Troubleshooting

### FFmpeg not found

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

### API Key Errors

Verify your `.env` file has valid API keys:

```bash
cat .env | grep API_KEY
```

### Out of Memory (for local models)

Adjust GPU memory fraction:

```bash
GPU_MEMORY_FRACTION=0.7  # Use 70% of GPU memory
```

## API Documentation (Phase 2)

Coming soon: FastAPI with Swagger docs at `http://localhost:8000/docs`

## License

MIT License - See LICENSE file

## Credits

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Video models via [Replicate](https://replicate.com/)
- FFmpeg for video processing
