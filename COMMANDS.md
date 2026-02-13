# Command Reference - AI Video Generation

Quick reference for all available commands and scripts.

## Setup and Verification

### Check System Readiness
```bash
python check_readiness.py
```
Checks all dependencies, configuration, and system requirements.

### Run Component Tests
```bash
python test_video_engine.py
```
Tests all core components without requiring API keys.

## Video Generation Commands

### Generate Complete Video
```bash
# Basic usage
python -m video_engine.cli generate "Your video description here"

# With options
python -m video_engine.cli generate "Your prompt" \
  --model replicate:svd-xt \
  --max-shots 5 \
  --output my_video.mp4
```

**Options:**
- `--model MODEL`: Video model to use (default: replicate:svd-xt)
- `--max-shots N`: Maximum number of shots (default: 5)
- `--output PATH`: Output file path
- `--reference-image PATH`: Reference image for I2V mode

## Storyboard Commands

### Generate Storyboard Only
```bash
# Basic usage
python -m video_engine.cli storyboard "Your video description"

# Save to file
python -m video_engine.cli storyboard "Space journey" --output storyboard.json
```

## Model Management

### List Available Models
```bash
python -m video_engine.cli list-models
```

## Job Management

### List All Jobs
```bash
python -m video_engine.cli list-jobs
```

### Get Job Details
```bash
python -m video_engine.cli get-job JOB_ID
```

See QUICKSTART.md for detailed usage examples.
