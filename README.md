# AI Video Generation System

An intelligent multi-stage AI video generation pipeline that creates videos from text prompts using LLM-powered storyboarding and state-of-the-art video generation models.

## 🎬 What It Does

1. **Takes a text prompt** like: "A peaceful forest at sunrise, camera panning through trees"
2. **Generates a detailed storyboard** using Claude AI (3-5 cinematic shots)
3. **Creates videos** for each shot using Stable Video Diffusion
4. **Combines them** into a final polished video

## ✨ Features

- 🤖 **Intelligent Storyboarding**: Claude breaks down your prompt into professional shot sequences
- 🎥 **Multiple Models**: Support for Replicate, HuggingFace, and local models
- 🖼️ **Image-to-Video**: Animate your photos with AI
- 📊 **Real-time Progress**: Track generation progress for each shot
- 🛠️ **CLI & Python API**: Use via command-line or programmatically
- 🎨 **Production Ready**: FastAPI backend + React frontend coming in Phase 2-3

## 🚀 Quick Start

### Option 1: Web UI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt -r requirements-api.txt
brew install ffmpeg  # macOS (or sudo apt install ffmpeg for Ubuntu)

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Start development environment
./start_dev.sh
```

Then open http://localhost:3000 in your browser.

### Option 2: API Server

```bash
# Start FastAPI server
uvicorn video_api.main:app --reload

# Access API docs
open http://localhost:8000/docs
```

### Option 3: CLI

```bash
# Install dependencies
pip install -r requirements.txt
brew install ffmpeg  # macOS

# Configure
cp .env.example .env
# Edit .env and add your API keys

# Generate video
python -m video_engine.cli generate "A peaceful forest at sunrise"
```

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[PHASE3_COMPLETE.md](PHASE3_COMPLETE.md)** - React frontend documentation
- **[PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)** - Complete project overview
- **[README_VIDEO.md](README_VIDEO.md)** - Detailed system documentation
- **API Docs**: http://localhost:8000/docs (when running)

## 💡 Examples

### Web UI
```bash
./start_dev.sh
# Open http://localhost:3000
# Enter prompt, select model, watch real-time progress
```

### REST API
```bash
# Create video generation job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Ocean waves at sunset", "model_id": "replicate:svd-xt"}'

# Get job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# List all jobs
curl http://localhost:8000/api/v1/jobs
```

### CLI
```bash
# Text-to-video
python -m video_engine.cli generate "Ocean waves at sunset" --output ocean.mp4

# Generate storyboard only
python -m video_engine.cli storyboard "Space journey" --output story.json

# List available models
python -m video_engine.cli list-models
```

### Python API
```python
from video_engine import VideoOrchestrator

orchestrator = VideoOrchestrator()
job = orchestrator.create_job(prompt="Mountain landscape")
job = orchestrator.execute_job(job.id)
print(f"Video: {job.output_video_path}")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         React Frontend (Phase 3)            │
│  Real-time UI with WebSocket updates       │
└────────────────┬────────────────────────────┘
                 │ REST API + WebSocket
                 ▼
┌─────────────────────────────────────────────┐
│       FastAPI Backend (Phase 2)             │
│  REST endpoints, WebSocket, Background jobs │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│      Video Generation Engine (Phase 1)     │
│                                              │
│  User Prompt                                │
│       ↓                                      │
│  Claude LLM (Storyboard)                    │
│       ↓                                      │
│  Model Adapter (Replicate/HF/Local)         │
│       ↓                                      │
│  FFmpeg (Concatenation)                     │
│       ↓                                      │
│  Final Video                                │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ai-video/
├── video_engine/          # Core video generation engine
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration
│   ├── core/             # Orchestration & job management
│   ├── llm/              # LLM clients (Claude, OpenAI)
│   ├── models/           # Model adapters & registry
│   ├── storage/          # Job store & file management
│   └── utils/            # Video utilities (FFmpeg)
├── video_api/            # FastAPI backend
│   ├── main.py           # API application
│   ├── routes/           # REST endpoints
│   ├── schemas/          # Request/response models
│   └── websocket_manager.py  # WebSocket handling
├── video_ui/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # WebSocket & custom hooks
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   └── public/           # Static assets
├── workspace/            # Generated videos & jobs
├── tests/                # Test suite
├── start_dev.sh          # Development startup script
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose setup
```

## ⚡ CLI Commands

```bash
# Generate video from prompt
python -m video_engine.cli generate "Your prompt" --output video.mp4

# Generate storyboard only
python -m video_engine.cli storyboard "Your prompt" --output story.json

# List available models
python -m video_engine.cli list-models

# List all jobs
python -m video_engine.cli list-jobs

# Get job details
python -m video_engine.cli get-job <job_id>
```

## 🌐 API Endpoints

```bash
# Health check
GET /api/v1/health

# Models
GET /api/v1/models
GET /api/v1/models/{model_id}

# Jobs
POST   /api/v1/jobs          # Create job
GET    /api/v1/jobs          # List jobs
GET    /api/v1/jobs/{id}     # Get job
DELETE /api/v1/jobs/{id}     # Delete job

# Files
POST /api/v1/upload           # Upload file
GET  /api/v1/files/{id}       # Download file

# WebSocket
WS /ws/jobs/{job_id}          # Real-time progress
```

## 🎯 Current Status

### ✅ Phase 1: Core Engine (COMPLETE)
- LLM storyboard generation
- Replicate adapter (SVD, SVD-XT)
- Video concatenation
- CLI interface
- Job management
- Progress tracking

### ✅ Phase 2: API Backend (COMPLETE)
- FastAPI REST endpoints
- WebSocket progress streaming
- Background job queue
- File upload handling
- API documentation (Swagger)

### ✅ Phase 3: React Frontend (COMPLETE)
- React + TypeScript web application
- Real-time progress updates
- WebSocket integration
- Video player
- Storyboard viewer
- Job history management

## 💰 Cost Estimates

Per 3-shot video (~10 seconds):
- Claude API (storyboard): ~$0.02
- Replicate SVD-XT: ~$0.36
- **Total**: ~$0.40 per video

## 🔧 Requirements

- Python 3.10+
- FFmpeg
- Anthropic API key
- Replicate API token

## 📊 Performance

- Storyboard generation: 5-10 seconds
- Video per shot: 60-90 seconds
- 3-shot video: ~3-4 minutes total
- 5-shot video: ~5-7 minutes total

## 🐛 Troubleshooting

Run the readiness check:
```bash
python check_readiness.py
```

Common issues:
- Missing API keys → Check `.env` file
- FFmpeg not found → Install FFmpeg
- Dependencies missing → Run `pip install -r requirements.txt`

## 🤝 Contributing

Phase 1 is complete! Next up:
1. Test with real-world prompts
2. Add more model adapters
3. Build FastAPI backend (Phase 2)
4. Create React frontend (Phase 3)

## 📝 License

MIT License

## 🙏 Credits

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Video models via [Replicate](https://replicate.com/)
- FFmpeg for video processing

---

**Ready to generate some amazing videos?** 🎥✨

Start here: `python check_readiness.py`
