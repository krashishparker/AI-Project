import api from './api';
import { Resume, ChatRequest, ChatResponse, ChatHistory } from '@/types';

export const resumeService = {
  async uploadResume(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<Resume>('/api/resume/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getResumes(): Promise<Resume[]> {
    const response = await api.get<Resume[]>('/api/resume/');
    return response.data;
  },

  async getResume(id: number): Promise<Resume> {
    const response = await api.get<Resume>(`/api/resume/${id}`);
    return response.data;
  },

  async deleteResume(id: number): Promise<void> {
    await api.delete(`/api/resume/${id}`);
  },

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/api/resume/chat', request);
    return response.data;
  },

  async getChatHistory(resumeId: number): Promise<ChatHistory[]> {
    const response = await api.get<{ history: ChatHistory[] }>(`/api/resume/${resumeId}/chat-history`);
    return response.data.history;
  },
};
