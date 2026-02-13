/**
 * Progress panel showing real-time job progress
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  HourglassEmpty as ProcessingIcon,
} from '@mui/icons-material';
import type { Job } from '../types/api';

interface ProgressPanelProps {
  job: Job | null;
}

const ProgressPanel: React.FC<ProgressPanelProps> = ({ job }) => {
  if (!job) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography color="text.secondary">
          No job in progress. Create a video to see progress here.
        </Typography>
      </Paper>
    );
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <ProcessingIcon color="primary" />;
    }
  };

  const getStatusColor = () => {
    switch (job.status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        {getStatusIcon()}
        <Typography variant="h6" sx={{ flex: 1 }}>
          Video Generation
        </Typography>
        <Chip
          label={job.status.toUpperCase()}
          color={getStatusColor() as any}
          size="small"
        />
      </Box>

      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {job.current_step}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {job.progress_percentage.toFixed(1)}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={job.progress_percentage}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Job Details
        </Typography>
        <List dense>
          <ListItem>
            <ListItemText
              primary="Job ID"
              secondary={job.id}
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Prompt"
              secondary={job.user_prompt}
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Model"
              secondary={job.model_id}
            />
          </ListItem>
          {job.storyboard && (
            <ListItem>
              <ListItemText
                primary="Storyboard"
                secondary={`${job.storyboard.shot_count} shots, ${job.storyboard.total_duration_seconds.toFixed(1)}s total`}
              />
            </ListItem>
          )}
        </List>
      </Box>

      {job.error_message && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {job.error_message}
        </Alert>
      )}

      {job.status === 'completed' && job.output_video_url && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Video generation complete! Check the video player below.
        </Alert>
      )}
    </Paper>
  );
};

export default ProgressPanel;
