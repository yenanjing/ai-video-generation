#!/bin/bash
# Start both API server and React dev server

echo "=========================================="
echo "Starting AI Video Generation System"
echo "=========================================="
echo ""

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Starting services in tmux..."
    
    # Create new tmux session
    tmux new-session -d -s ai-video
    
    # Split window
    tmux split-window -h
    
    # Start API in left pane
    tmux select-pane -t 0
    tmux send-keys "python run_api.py" C-m
    
    # Start React in right pane
    tmux select-pane -t 1
    tmux send-keys "cd video_ui && npm start" C-m
    
    # Attach to session
    tmux attach-session -t ai-video
    
else
    echo "tmux not found. Starting services in background..."
    echo ""
    
    # Start API
    echo "Starting API server..."
    python run_api.py &
    API_PID=$!
    
    # Wait for API to start
    sleep 3
    
    # Start React
    echo "Starting React dev server..."
    cd video_ui && npm start &
    REACT_PID=$!
    
    echo ""
    echo "=========================================="
    echo "Services Started!"
    echo "=========================================="
    echo "API Server: http://localhost:8000"
    echo "React App: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Wait for Ctrl+C
    trap "kill $API_PID $REACT_PID; exit" INT
    wait
fi
