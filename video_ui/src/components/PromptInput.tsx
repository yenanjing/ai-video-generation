/**
 * Prompt input component for creating video generation jobs
 */
import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Typography,
  Paper,
  CircularProgress,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import type { ModelInfo, CreateJobRequest } from '../types/api';

interface PromptInputProps {
  models: ModelInfo[];
  onSubmit: (request: CreateJobRequest) => void;
  isLoading?: boolean;
}

const PromptInput: React.FC<PromptInputProps> = ({ models, onSubmit, isLoading = false }) => {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [maxShots, setMaxShots] = useState(3);

  const availableModels = models.filter(m => m.is_available);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim()) {
      alert('Please enter a prompt');
      return;
    }

    onSubmit({
      user_prompt: prompt,
      model_id: selectedModel || undefined,
      max_shots: maxShots,
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <Typography variant="h6" gutterBottom>
            Create Video
          </Typography>

          <TextField
            label="Video Prompt"
            placeholder="Describe the video you want to generate..."
            multiline
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
            fullWidth
            required
            helperText="Be specific about scenes, camera movements, and visual details"
          />

          <FormControl fullWidth>
            <InputLabel>Model</InputLabel>
            <Select
              value={selectedModel}
              label="Model"
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={isLoading}
            >
              <MenuItem value="">
                <em>Default (replicate:svd-xt)</em>
              </MenuItem>
              {availableModels.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name} - {model.provider}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box>
            <Typography gutterBottom>
              Max Shots: {maxShots}
            </Typography>
            <Slider
              value={maxShots}
              onChange={(_, value) => setMaxShots(value as number)}
              min={1}
              max={10}
              marks
              disabled={isLoading}
              valueLabelDisplay="auto"
            />
            <Typography variant="caption" color="text.secondary">
              More shots = longer video but slower generation
            </Typography>
          </Box>

          <Button
            type="submit"
            variant="contained"
            size="large"
            startIcon={isLoading ? <CircularProgress size={20} /> : <SendIcon />}
            disabled={isLoading || !prompt.trim()}
            fullWidth
          >
            {isLoading ? 'Generating...' : 'Generate Video'}
          </Button>
        </Box>
      </form>
    </Paper>
  );
};

export default PromptInput;
