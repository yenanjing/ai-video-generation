/**
 * API client for video generation backend
 */
import axios from 'axios';
import type { Job, ModelInfo, CreateJobRequest } from '../types/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Health check
  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Models
  listModels: async (): Promise<ModelInfo[]> => {
    const response = await api.get('/models');
    return response.data.models;
  },

  getModel: async (modelId: string): Promise<ModelInfo> => {
    const response = await api.get(`/models/${modelId}`);
    return response.data;
  },

  // Jobs
  createJob: async (request: CreateJobRequest): Promise<Job> => {
    const response = await api.post('/jobs', request);
    return response.data;
  },

  listJobs: async (page: number = 1, pageSize: number = 20): Promise<{ jobs: Job[], total: number }> => {
    const response = await api.get('/jobs', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  getJob: async (jobId: string): Promise<Job> => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  deleteJob: async (jobId: string): Promise<void> => {
    await api.delete(`/jobs/${jobId}`);
  },

  downloadVideo: async (jobId: string): Promise<Blob> => {
    const response = await api.get(`/jobs/${jobId}/video`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Upload
  uploadFile: async (file: File): Promise<{ file_id: string, file_path: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default apiClient;
