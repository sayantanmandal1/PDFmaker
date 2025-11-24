// User types
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
}

// Project types
export interface Project {
  id: string;
  user_id: string;
  name: string;
  document_type: 'word' | 'powerpoint';
  topic: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  document_type: 'word' | 'powerpoint';
  topic: string;
}

export interface SectionConfig {
  header: string;
  position: number;
}

export interface SlideConfig {
  title: string;
  position: number;
}

// Content types
export interface Section {
  id: string;
  project_id: string;
  header: string;
  content: string | null;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface Slide {
  id: string;
  project_id: string;
  title: string;
  content: string | null;
  position: number;
  created_at: string;
  updated_at: string;
}

// Refinement types
export interface RefinementRequest {
  prompt: string;
}

export interface RefinementHistory {
  id: string;
  refinement_prompt: string;
  previous_content: string | null;
  new_content: string | null;
  created_at: string;
}

// Feedback types
export interface FeedbackCreate {
  feedback_type: 'like' | 'dislike';
}

export interface Feedback {
  id: string;
  feedback_type: string;
  created_at: string;
}

// Comment types
export interface CommentCreate {
  comment_text: string;
}

export interface Comment {
  id: string;
  comment_text: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface ProjectResponse {
  project: Project;
  sections?: Section[];
  slides?: Slide[];
}

export interface TemplateResponse {
  template: {
    headers?: string[];
    slide_titles?: string[];
  };
}

export interface GenerationResponse {
  status: string;
  message: string;
  project: Project;
}