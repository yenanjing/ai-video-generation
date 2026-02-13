# AI Video Generation - Quick Start Guide

## Prerequisites

1. **Python 3.10+** installed
2. **FFmpeg** installed (for video processing)
3. **API Keys** for:
   - Anthropic Claude (for storyboard generation)
   - Replicate (for video generation)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

### 3. Get API Keys

**Anthropic Claude:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Create an API key
4. Copy the key (starts with `sk-ant-`)

**Replicate:**
1. Go to https://replicate.com/
2. Sign up or log in
3. Go to https://replicate.com/account/api-tokens
4. Create an API token
5. Copy the token (starts with `r8_`)

### 4. Configure Environment

Edit the `.env` file and add your API keys:

```bash
# Edit .env file
nano .env
```

Add your keys:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
REPLICATE_API_TOKEN=r8_your-token-here
```

Save and exit (Ctrl+X, then Y, then Enter).

## Verify Installation

Run the test script:

```bash
python test_video_engine.py
```

You should see all tests pass:
```
✓ All tests passed!
```

## Generate Your First Video

### Simple Text-to-Video

```bash
python -m video_engine.cli generate "A peaceful forest at sunrise, camera slowly panning through tall trees with mist"
```

This will:
1. Generate a storyboard (3-5 shots)
2. Create videos for each shot
3. Combine them into a final video
4. Save to `workspace/videos/{job_id}/final_output.mp4`

### Save to Specific Location

```bash
python -m video_engine.cli generate "Ocean waves crashing on beach at sunset" --output my_video.mp4
```

### Limit Number of Shots

```bash
python -m video_engine.cli generate "A day in Tokyo" --max-shots 3 --output tokyo.mp4
```

## Understanding the Process

The system works in stages:

```
1. STORYBOARD GENERATION (10%)
   - Claude analyzes your prompt
   - Breaks it into 3-5 shots
   - Each shot gets detailed instructions

2. SHOT GENERATION (10% → 85%)
   - Each shot is sent to video model (Replicate SVD)
   - Takes 60-90 seconds per shot
   - Progress shown for each shot

3. VIDEO CONCATENATION (85% → 95%)
   - FFmpeg combines all shots
   - Creates smooth transitions

4. FINALIZATION (95% → 100%)
   - Saves final video
   - Updates job metadata
```

## Expected Generation Times

- **Storyboard**: 5-10 seconds
- **Per Shot**: 60-90 seconds (cloud processing)
- **3-shot video**: ~3-4 minutes total
- **5-shot video**: ~5-7 minutes total

## CLI Commands Reference

### Generate Video
```bash
python -m video_engine.cli generate "YOUR_PROMPT" [OPTIONS]

Options:
  --model MODEL          Model to use (default: replicate:svd-xt)
  --max-shots N          Maximum shots (default: 5)
  --output PATH          Output file path
  --reference-image PATH Image for I2V mode
```

### Generate Storyboard Only
```bash
python -m video_engine.cli storyboard "YOUR_PROMPT" [OPTIONS]

Options:
  --max-shots N    Maximum shots (default: 5)
  --output PATH    Save storyboard as JSON
```

### List Available Models
```bash
python -m video_engine.cli list-models
```

### Manage Jobs
```bash
# List all jobs
python -m video_engine.cli list-jobs

# Get specific job details
python -m video_engine.cli get-job JOB_ID
```

## Example Prompts

### Nature & Landscapes
```bash
python -m video_engine.cli generate "Majestic mountain range at golden hour, clouds rolling over peaks"

python -m video_engine.cli generate "Underwater coral reef with colorful fish swimming"

python -m video_engine.cli generate "Northern lights dancing over snowy landscape"
```

### Urban & Architecture
```bash
python -m video_engine.cli generate "Busy Tokyo street at night, neon signs reflecting on wet pavement"

python -m video_engine.cli generate "Modern architecture, glass building reflections"
```

### Abstract & Artistic
```bash
python -m video_engine.cli generate "Ink spreading in water, creating beautiful patterns"

python -m video_engine.cli generate "Colorful paint mixing together in slow motion"
```

## Tips for Better Results

### 1. Be Specific About Movement
❌ "A forest"
✓ "A forest with camera slowly panning left through trees"

### 2. Describe Visual Details
❌ "A city"
✓ "A futuristic city with tall glass buildings, flying cars, at sunset"

### 3. Keep It Achievable
❌ "A 2-minute epic story with characters talking and complex actions"
✓ "A serene 10-second scene of waves on a beach"

### 4. Use Cinematic Language
- "Camera pans left/right"
- "Slow zoom in/out"
- "Close-up of..."
- "Wide shot of..."
- "Aerial view of..."

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"
- Make sure `.env` file exists
- Check the key starts with `sk-ant-`
- Verify no extra spaces in `.env` file

### "REPLICATE_API_TOKEN not configured"
- Add token to `.env` file
- Token should start with `r8_`

### "FFmpeg not found"
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

### Generation is Slow
- This is normal! Cloud processing takes time
- Each shot: 60-90 seconds
- Consider reducing `--max-shots` for faster results

### Out of Credits
- Check your Replicate account: https://replicate.com/account
- Replicate charges per second of GPU time
- Approximate cost: $0.10-0.30 per video

## File Locations

- **Generated Videos**: `workspace/videos/{job_id}/`
- **Job Metadata**: `workspace/jobs/{job_id}.json`
- **Uploads**: `workspace/uploads/`
- **Temp Files**: `workspace/temp/`

## Cost Estimation

Using Replicate SVD-XT:
- ~$0.002 per second of generation time
- Average shot: 60 seconds = $0.12
- 3-shot video: ~$0.36
- 5-shot video: ~$0.60

## Next Steps

1. **Experiment with prompts** - Try different styles and subjects
2. **Review generated storyboards** - Use `storyboard` command to see what Claude creates
3. **Check out Phase 2** - Web UI coming soon!

## Support

- Issues: https://github.com/your-repo/issues
- Documentation: See `README_VIDEO.md`
- API Docs: Coming in Phase 2

## Limits

Current system limits (configurable in `.env`):
- Maximum video duration: 60 seconds
- Maximum shots per video: 10
- Shot duration: 2-4 seconds each

Happy video generating! 🎥✨
