/**
 * Video player component for displaying generated videos
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
} from '@mui/material';
import {
  Download as DownloadIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import type { Job } from '../types/api';

interface VideoPlayerProps {
  job: Job | null;
  onDownload?: () => void;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ job, onDownload }) => {
  if (!job || job.status !== 'completed' || !job.output_video_url) {
    return (
      <Paper elevation={3} sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.100' }}>
        <PlayIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
        <Typography color="text.secondary">
          Video will appear here when generation is complete
        </Typography>
      </Paper>
    );
  }

  const videoUrl = `http://localhost:8000${job.output_video_url}`;

  return (
    <Paper elevation={3} sx={{ overflow: 'hidden' }}>
      <Box sx={{ position: 'relative', bgcolor: 'black' }}>
        <video
          controls
          style={{
            width: '100%',
            display: 'block',
            maxHeight: '600px',
          }}
          src={videoUrl}
        >
          Your browser does not support the video tag.
        </video>
      </Box>

      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="subtitle2">
            {job.storyboard?.title || 'Generated Video'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {job.storyboard?.shot_count} shots • {job.storyboard?.total_duration_seconds.toFixed(1)}s
          </Typography>
        </Box>

        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          onClick={onDownload}
        >
          Download
        </Button>
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
