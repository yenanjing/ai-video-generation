/**
 * Main App component
 */
import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  AppBar,
  Toolbar,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';
import { Movie as MovieIcon } from '@mui/icons-material';
import PromptInput from './components/PromptInput';
import ProgressPanel from './components/ProgressPanel';
import VideoPlayer from './components/VideoPlayer';
import StoryboardViewer from './components/StoryboardViewer';
import JobHistory from './components/JobHistory';
import apiClient from './services/api';
import { useWebSocket } from './hooks/useWebSocket';
import type { Job, ModelInfo, CreateJobRequest } from './types/api';

const App: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [currentJob, setCurrentJob] = useState<Job | null>(null);
  const [isCreatingJob, setIsCreatingJob] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // WebSocket connection for current job
  const { isConnected } = useWebSocket(currentJob?.id || null, {
    onProgress: (update) => {
      if (currentJob) {
        setCurrentJob({
          ...currentJob,
          current_step: update.step || currentJob.current_step,
          progress_percentage: update.progress || currentJob.progress_percentage,
        });
      }
    },
    onJobComplete: async () => {
      if (currentJob) {
        const updatedJob = await apiClient.getJob(currentJob.id);
        setCurrentJob(updatedJob);
        refreshJobs();
      }
    },
    onError: (errorMsg) => {
      setError(errorMsg);
    },
  });

  useEffect(() => {
    loadModels();
    refreshJobs();
    const interval = setInterval(refreshJobs, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadModels = async () => {
    try {
      const modelList = await apiClient.listModels();
      setModels(modelList);
    } catch (err) {
      setError('Failed to load models');
    }
  };

  const refreshJobs = async () => {
    try {
      const { jobs: jobList } = await apiClient.listJobs();
      setJobs(jobList);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    }
  };

  const handleCreateJob = async (request: CreateJobRequest) => {
    setIsCreatingJob(true);
    setError(null);
    try {
      const job = await apiClient.createJob(request);
      setCurrentJob(job);
      setJobs([job, ...jobs]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job');
    } finally {
      setIsCreatingJob(false);
    }
  };

  const handleSelectJob = async (jobId: string) => {
    try {
      const job = await apiClient.getJob(jobId);
      setCurrentJob(job);
    } catch (err) {
      setError('Failed to load job');
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!window.confirm('Delete this job?')) return;
    try {
      await apiClient.deleteJob(jobId);
      setJobs(jobs.filter(j => j.id !== jobId));
      if (currentJob?.id === jobId) setCurrentJob(null);
    } catch (err) {
      setError('Failed to delete job');
    }
  };

  const handleDownloadVideo = async () => {
    if (!currentJob?.id) return;
    try {
      const blob = await apiClient.downloadVideo(currentJob.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentJob.id}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to download video');
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <MovieIcon sx={{ mr: 2 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            AI Video Generation
          </Typography>
          {isConnected && (
            <Typography variant="caption" sx={{ color: 'success.light' }}>
              ● Live
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <PromptInput models={models} onSubmit={handleCreateJob} isLoading={isCreatingJob} />
              <ProgressPanel job={currentJob} />
            </Box>
          </Grid>
          <Grid item xs={12} md={5}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <VideoPlayer job={currentJob} onDownload={handleDownloadVideo} />
              <StoryboardViewer storyboard={currentJob?.storyboard || null} />
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <JobHistory
              jobs={jobs}
              selectedJobId={currentJob?.id}
              onSelectJob={handleSelectJob}
              onDeleteJob={handleDeleteJob}
            />
          </Grid>
        </Grid>
      </Container>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>

      <Box sx={{ py: 3, bgcolor: 'grey.100', textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          AI Video Generation • Phase 3 Complete
        </Typography>
      </Box>
    </Box>
  );
};

export default App;
