/**
 * Type definitions for the video generation API
 */

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
export type GenerationMode = 'text_to_video' | 'image_to_video' | 'video_to_video';

export interface Shot {
  id: string;
  sequence_number: number;
  duration_seconds: number;
  description: string;
  text_prompt: string;
  camera_movement?: string;
  camera_angle?: string;
  motion_intensity?: number;
  output_video_path?: string;
}

export interface Storyboard {
  id: string;
  title: string;
  user_prompt: string;
  shots: Shot[];
  style: Record<string, any>;
  total_duration_seconds: number;
  shot_count: number;
  generated_at: string;
  generated_by: string;
}

export interface Job {
  id: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  user_prompt: string;
  generation_mode: GenerationMode;
  model_id: string;
  current_step: string;
  progress_percentage: number;
  current_shot_id?: string;
  output_video_url?: string;
  storyboard?: Storyboard;
  error_message?: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  description: string;
  provider: string;
  is_available: boolean;
  capabilities: {
    supports_text_to_video: boolean;
    supports_image_to_video: boolean;
    max_frames: number;
    recommended_fps: number;
  };
}

export interface CreateJobRequest {
  user_prompt: string;
  model_id?: string;
  max_shots?: number;
  style_preferences?: Record<string, any>;
}

export interface ProgressUpdate {
  type: 'connected' | 'progress' | 'shot_complete' | 'job_complete' | 'error';
  job_id: string;
  step?: string;
  progress?: number;
  message?: string;
  shot_id?: string;
  output_path?: string;
  error?: string;
}
