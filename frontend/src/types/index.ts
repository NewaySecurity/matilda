// Video generation related interfaces
export interface VideoGenerationRequest {
  prompt: string;
  duration?: number;
  aspectRatio?: string;
  quality?: 'standard' | 'hd' | '4k';
}

export interface VideoGenerationResponse {
  success: boolean;
  message: string;
  data: {
    prompt: string;
    requestId: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    estimatedCompletionTime?: string;
    duration?: number;
    aspectRatio?: string;
    quality?: string;
  };
}

export interface VideoGenerationError {
  error: string;
  details?: string;
  code?: string;
}

// Image generation related interfaces
export interface ImageGenerationRequest {
  prompt: string;
  style?: ImageGenerationStyle;
  width?: number;
  height?: number;
  quality?: 'standard' | 'hd';
}

export interface ImageGenerationResponse {
  success: boolean;
  message: string;
  data: {
    prompt: string;
    requestId: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    imageUrl?: string;
    style?: ImageGenerationStyle;
    width?: number;
    height?: number;
  };
}

export interface ImageGenerationError {
  error: string;
  details?: string;
  code?: string;
}

export type ImageGenerationStyle = 
  | 'realistic' 
  | 'artistic' 
  | 'cartoon' 
  | 'abstract' 
  | 'minimalist'
  | 'cinematic';

// API response interfaces
export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

// Application state interfaces
export interface VideoState {
  isLoading: boolean;
  requestId: string | null;
  url: string | null;
  error: string | null;
  status?: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number;
}

export interface ImageState {
  isLoading: boolean;
  requestId: string | null;
  url: string | null;
  error: string | null;
  status?: 'queued' | 'processing' | 'completed' | 'failed';
  progress?: number;
}

// Theme interfaces
export type ColorMode = 'light' | 'dark';

export interface ThemeContextType {
  mode: ColorMode;
  toggleColorMode: () => void;
}

// User preferences
export interface UserPreferences {
  theme: ColorMode;
  defaultVideoQuality: 'standard' | 'hd' | '4k';
  defaultImageStyle: ImageGenerationStyle;
  autoSave: boolean;
}
