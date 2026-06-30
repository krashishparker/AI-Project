export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface Resume {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  parsed_text?: string;
  parsed_data?: ResumeData;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
}

export interface ResumeData {
  name?: string;
  email?: string;
  phone?: string;
  skills?: string[];
  education?: string[];
  experience?: string[];
  projects?: string[];
  certifications?: string[];
}

export interface ChatRequest {
  resume_id: number;
  question: string;
}

export interface ChatResponse {
  answer: string;
  context_chunks: ContextChunk[];
}

export interface ContextChunk {
  text: string;
  metadata: Record<string, any>;
}

export interface ChatHistory {
  id: number;
  question: string;
  answer: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}
