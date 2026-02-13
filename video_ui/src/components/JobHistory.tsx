/**
 * Job history component showing list of all jobs
 */
import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import type { Job } from '../types/api';

interface JobHistoryProps {
  jobs: Job[];
  selectedJobId?: string;
  onSelectJob: (jobId: string) => void;
  onDeleteJob: (jobId: string) => void;
}

const JobHistory: React.FC<JobHistoryProps> = ({
  jobs,
  selectedJobId,
  onSelectJob,
  onDeleteJob,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
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

  if (jobs.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No jobs yet. Create your first video!
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">
          Job History ({jobs.length})
        </Typography>
      </Box>

      <List sx={{ maxHeight: 400, overflow: 'auto' }}>
        {jobs.map((job, index) => (
          <React.Fragment key={job.id}>
            {index > 0 && <Divider />}
            <ListItem
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => onDeleteJob(job.id)}
                  size="small"
                >
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemButton
                selected={job.id === selectedJobId}
                onClick={() => onSelectJob(job.id)}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                        {job.user_prompt.substring(0, 50)}
                        {job.user_prompt.length > 50 && '...'}
                      </Typography>
                      <Chip
                        label={job.status}
                        size="small"
                        color={getStatusColor(job.status) as any}
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {new Date(job.created_at).toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {job.progress_percentage.toFixed(0)}%
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default JobHistory;
