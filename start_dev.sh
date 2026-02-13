#!/bin/bash

# AI Video Generation - Development Environment Startup Script
# This script starts both the FastAPI backend and React frontend

set -e

echo "🚀 Starting AI Video Generation Development Environment"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create a .env file with the following variables:"
    echo "  ANTHROPIC_API_KEY=your_key_here"
    echo "  REPLICATE_API_TOKEN=your_token_here"
    exit 1
fi

# Check if workspace directory exists
if [ ! -d workspace ]; then
    echo -e "${YELLOW}Creating workspace directory...${NC}"
    mkdir -p workspace/videos workspace/uploads workspace/jobs workspace/temp
fi

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $API_PID $UI_PID 2>/dev/null
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI backend
echo -e "\n${GREEN}[1/2] Starting FastAPI Backend...${NC}"
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || echo -e "${YELLOW}Note: Virtual environment not activated${NC}"

uvicorn video_api.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

echo -e "${GREEN}✓ API Server started on http://localhost:8000${NC}"
echo -e "  API Docs: http://localhost:8000/docs"

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: API failed to start${NC}"
        kill $API_PID
        exit 1
    fi
    sleep 1
done

# Start React frontend
echo -e "\n${GREEN}[2/2] Starting React Frontend...${NC}"
cd video_ui

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

npm start &
UI_PID=$!

echo -e "${GREEN}✓ React Dev Server started on http://localhost:3000${NC}"

# Display status
echo -e "\n${GREEN}=================================================="
echo "✓ All services are running!"
echo "==================================================${NC}"
echo ""
echo "Services:"
echo "  • API Server:    http://localhost:8000"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • Web UI:        http://localhost:3000"
echo "  • WebSocket:     ws://localhost:8000/ws/jobs/{job_id}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $API_PID $UI_PID
