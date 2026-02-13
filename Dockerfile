# Multi-stage Dockerfile for AI Video Generation System

# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app/video_ui
COPY video_ui/package*.json ./
RUN npm ci --only=production
COPY video_ui/ ./
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-api.txt

# Copy application code
COPY video_engine/ ./video_engine/
COPY video_api/ ./video_api/
COPY .env.example ./.env

# Copy built frontend from stage 1
COPY --from=frontend-build /app/video_ui/build ./video_api/static

# Create workspace directories
RUN mkdir -p workspace/videos workspace/uploads workspace/jobs workspace/temp

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start application
CMD ["uvicorn", "video_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
