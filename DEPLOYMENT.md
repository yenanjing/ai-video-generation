# AI Video Generation - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Prerequisites

### System Requirements
- **OS**: macOS, Linux, or Windows (WSL2)
- **Python**: 3.11+
- **Node.js**: 18+
- **FFmpeg**: Latest version
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Storage**: 10GB+ free space for videos

### API Keys Required
- Anthropic Claude API key (for storyboard generation)
- Replicate API token (for video generation)
- OpenAI API key (optional, if using GPT models)

---

## Development Deployment

### 1. Quick Start (Automated)

```bash
# Clone repository
git clone https://github.com/yenanjing/ai-video-generation.git
cd ai-video-generation

# Install system dependencies
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Install Python dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-api.txt

# Install Node dependencies
cd video_ui
npm install
cd ..

# Start development environment
./start_dev.sh
```

The script will:
- Start FastAPI backend on http://localhost:8000
- Start React dev server on http://localhost:3000
- Set up WebSocket connections
- Create necessary workspace directories

### 2. Manual Start (Individual Services)

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
uvicorn video_api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - React UI:**
```bash
cd video_ui
npm start
```

### 3. Verify Installation

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check available models
curl http://localhost:8000/api/v1/models

# Open browser
open http://localhost:3000  # macOS
xdg-open http://localhost:3000  # Linux
```

---

## Production Deployment

### 1. Build React Frontend

```bash
cd video_ui
npm run build
```

This creates optimized production files in `video_ui/build/`.

### 2. Serve Frontend with FastAPI

Update `video_api/main.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

# Mount static files
app.mount("/", StaticFiles(directory="video_ui/build", html=True), name="static")
```

### 3. Run with Production ASGI Server

```bash
# Using Uvicorn with workers
uvicorn video_api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info

# Or using Gunicorn + Uvicorn workers
gunicorn video_api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### 4. Process Manager (systemd)

Create `/etc/systemd/system/ai-video.service`:

```ini
[Unit]
Description=AI Video Generation Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/ai-video-generation
Environment="PATH=/opt/ai-video-generation/venv/bin"
ExecStart=/opt/ai-video-generation/venv/bin/uvicorn video_api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-video
sudo systemctl start ai-video
sudo systemctl status ai-video
```

### 5. Reverse Proxy (Nginx)

Create `/etc/nginx/sites-available/ai-video`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # API and WebSocket
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static files (React app)
    location / {
        root /opt/ai-video-generation/video_ui/build;
        try_files $uri $uri/ /index.html;
    }

    # File size limits for video uploads
    client_max_body_size 100M;
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-video /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t ai-video-generation:latest .
```

### 2. Run with Docker Compose

```bash
# Create .env file with API keys
cp .env.example .env
# Edit .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Docker Commands

```bash
# Build and start
docker-compose up --build -d

# Scale workers (Phase 4 with Celery)
docker-compose up -d --scale worker=4

# Health check
docker-compose ps

# Clean up
docker-compose down -v
docker system prune -a
```

---

## Environment Configuration

### Production .env Example

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
REPLICATE_API_TOKEN=r8_xxxxx
OPENAI_API_KEY=sk-xxxxx  # Optional

# Video Configuration
VIDEO_OUTPUT_DIR=/app/workspace/videos
VIDEO_UPLOAD_DIR=/app/workspace/uploads
MAX_VIDEO_DURATION=60
MAX_SHOTS_PER_VIDEO=10
DEFAULT_VIDEO_MODEL=replicate:svd-xt

# Model Configuration
ENABLE_LOCAL_MODELS=false
GPU_MEMORY_FRACTION=0.9

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENABLE_CORS=true
MAX_CONCURRENT_JOBS=3

# Logging
LOG_LEVEL=info
LOG_FILE=/app/logs/ai-video.log

# Database (Phase 4)
# DATABASE_URL=postgresql://user:pass@localhost/aivideo
# REDIS_URL=redis://localhost:6379/0
```

### Security Considerations

1. **API Keys**: Never commit `.env` to version control
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Implement rate limiting (Phase 4)
4. **File Validation**: Validate all uploads
5. **User Auth**: Add authentication (Phase 4)

---

## Monitoring and Maintenance

### 1. Health Checks

```bash
# API health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### 2. Logs

```bash
# Application logs
tail -f logs/ai-video.log

# Systemd logs
sudo journalctl -u ai-video -f

# Docker logs
docker-compose logs -f ai-video-api
```

### 3. Disk Space Management

```bash
# Check disk usage
du -sh workspace/videos

# Clean old videos (older than 7 days)
find workspace/videos -type f -name "*.mp4" -mtime +7 -delete

# Clean temp files
rm -rf workspace/temp/*
```

### 4. Performance Monitoring

```bash
# CPU and memory usage
htop

# API performance
ab -n 100 -c 10 http://localhost:8000/api/v1/health

# WebSocket connections
netstat -an | grep 8000
```

### 5. Backup Strategy

```bash
# Backup jobs metadata
tar -czf backup-$(date +%Y%m%d).tar.gz workspace/jobs/

# Backup videos (optional, large files)
rsync -avz workspace/videos/ /backup/videos/
```

### 6. Update Deployment

```bash
# Pull latest code
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt -r requirements-api.txt

# Rebuild React frontend
cd video_ui
npm install
npm run build
cd ..

# Restart services
sudo systemctl restart ai-video

# Or with Docker
docker-compose down
docker-compose up --build -d
```

---

## Troubleshooting

### Common Issues

**1. FFmpeg not found**
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Ubuntu
```

**2. API key errors**
```bash
# Verify .env file exists and contains keys
cat .env | grep API_KEY
```

**3. Port already in use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

**4. WebSocket connection failed**
- Check CORS settings in `video_api/main.py`
- Verify WebSocket URL in React app (`video_ui/src/hooks/useWebSocket.ts`)
- Check firewall rules

**5. Video generation fails**
```bash
# Check Replicate API status
curl https://api.replicate.com/v1/models

# Verify API token
curl -H "Authorization: Token $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models
```

---

## Performance Tuning

### 1. FastAPI Workers

```bash
# Adjust based on CPU cores
uvicorn video_api.main:app --workers $(nproc)
```

### 2. Connection Pooling

Update `video_api/main.py`:
```python
from fastapi import FastAPI
import httpx

app = FastAPI()
client = httpx.AsyncClient(limits=httpx.Limits(max_connections=100))
```

### 3. Caching

Implement Redis caching (Phase 4):
```python
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

---

## Scaling Strategies

### Horizontal Scaling

1. **Load Balancer**: Nginx/HAProxy
2. **Multiple API Instances**: Docker Swarm or Kubernetes
3. **Shared Storage**: NFS or S3 for videos
4. **Message Queue**: Redis/RabbitMQ for job distribution

### Vertical Scaling

1. **GPU Instances**: For local models (Phase 4)
2. **High Memory**: For concurrent jobs
3. **Fast Storage**: SSD for video I/O

---

## Cost Optimization

### API Usage
- **Anthropic Claude**: ~$0.02 per storyboard (200 tokens)
- **Replicate SVD**: ~$0.003 per second of video
- **Storage**: Implement auto-cleanup of old videos

### Estimated Monthly Costs (1000 videos/month)
- Claude API: $20
- Replicate: $90 (avg 3 seconds per shot, 3 shots per video)
- Hosting: $50-200 (depending on provider)
- **Total**: ~$160-310/month

---

## Support and Documentation

- **GitHub**: https://github.com/yenanjing/ai-video-generation
- **API Docs**: http://localhost:8000/docs
- **Issues**: https://github.com/yenanjing/ai-video-generation/issues

---

Last Updated: 2024-02-13
Version: 1.0.0 (Phase 3 Complete)
