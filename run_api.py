#!/usr/bin/env python
"""
Quick start script for FastAPI server.
"""
import sys
from video_api.main import run_server


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting AI Video Generation API")
    print("=" * 60)
    print()
    print("API will be available at:")
    print("  - Main: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - Health: http://localhost:8000/api/v1/health")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        run_server(reload=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)
