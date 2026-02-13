# AI Video Generation - React Frontend

React + TypeScript frontend for the AI Video Generation system.

## Features

- **Create Videos**: Enter prompts and generate videos with AI
- **Real-time Progress**: WebSocket connection for live updates
- **Video Player**: Watch generated videos instantly
- **Storyboard Viewer**: See the shot-by-shot breakdown
- **Job History**: Track all your video generation jobs
- **Model Selection**: Choose from available video models

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd video_ui
npm install
```

### Development

```bash
npm start
```

Opens http://localhost:3000

### Build for Production

```bash
npm run build
```

## Configuration

Edit `.env` to change API endpoints:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000
```

## Components

- **PromptInput**: Create video generation requests
- **ProgressPanel**: Real-time job progress display
- **VideoPlayer**: Video playback and download
- **StoryboardViewer**: Shot-by-shot storyboard
- **JobHistory**: List of all jobs with status

## Tech Stack

- React 18
- TypeScript
- Material-UI (MUI)
- Axios (HTTP client)
- WebSocket API

## Usage

1. Start the backend API server
2. Start the React dev server
3. Open http://localhost:3000
4. Enter a prompt and click "Generate Video"
5. Watch real-time progress
6. View and download your video

## Architecture

```
App
├── PromptInput (create jobs)
├── ProgressPanel (track progress)
├── VideoPlayer (display results)
├── StoryboardViewer (show shots)
└── JobHistory (manage jobs)
```

WebSocket connection provides real-time updates for:
- Job progress
- Shot completion
- Final video ready
- Error notifications
