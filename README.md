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

### 1. Install

```bash
# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

### 2. Configure

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=sk-ant-xxx
# REPLICATE_API_TOKEN=r8_xxx
```

Get API keys:
- Anthropic: https://console.anthropic.com/
- Replicate: https://replicate.com/account/api-tokens

### 3. Verify

```bash
python check_readiness.py
```

### 4. Generate!

```bash
python -m video_engine.cli generate "A peaceful forest at sunrise"
```

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Detailed setup and usage guide
- **[README_VIDEO.md](README_VIDEO.md)** - Complete system documentation
- **[COMMANDS.md](COMMANDS.md)** - Command reference
- **[IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)** - Development status

## 💡 Examples

### Text-to-Video
```bash
python -m video_engine.cli generate "Ocean waves at sunset" --output ocean.mp4
```

### Generate Storyboard Only
```bash
python -m video_engine.cli storyboard "Space journey" --output story.json
```

### Image-to-Video
```bash
python -m video_engine.cli generate "Scene comes alive" --reference-image photo.jpg
```

### Programmatic Usage
```python
from video_engine import VideoOrchestrator

orchestrator = VideoOrchestrator()
job = orchestrator.create_job(prompt="Mountain landscape")
job = orchestrator.execute_job(job.id)
print(f"Video: {job.output_video_path}")
```

## 🏗️ Architecture

```
User Prompt
    ↓
Claude LLM (Storyboard Generation)
    ↓
Video Models (Shot Generation)
    ↓
FFmpeg (Video Concatenation)
    ↓
Final Video
```

## 📁 Project Structure

```
ai-video/
├── video_engine/          # Core video generation engine
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration
│   ├── core/             # Orchestration
│   ├── llm/              # LLM clients
│   ├── models/           # Model adapters
│   ├── storage/          # Persistence
│   └── utils/            # Video utilities
├── workspace/            # Generated videos & jobs
├── examples/             # Example scripts
├── tests/                # Test suite
└── docs/                 # Documentation
```

## ⚡ CLI Commands

```bash
# Generate video
python -m video_engine.cli generate "Your prompt"

# Generate storyboard
python -m video_engine.cli storyboard "Your prompt"

# List models
python -m video_engine.cli list-models

# List jobs
python -m video_engine.cli list-jobs

# Check system
python check_readiness.py
```

## 🎯 Current Status

### ✅ Phase 1: Core Engine (COMPLETE)
- LLM storyboard generation
- Replicate adapter (SVD, SVD-XT)
- Video concatenation
- CLI interface
- Job management
- Progress tracking

### 🚧 Phase 2: API Backend (Planned)
- FastAPI REST endpoints
- WebSocket progress streaming
- Background job queue
- File upload handling

### 📋 Phase 3: React Frontend (Planned)
- Web UI with real-time updates
- Storyboard editor
- Video player
- Model selection

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
