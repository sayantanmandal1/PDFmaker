import { apiClient } from './api';
import { 
  Project, 
  ProjectCreate, 
  ProjectResponse,
  SectionConfig,
  SlideConfig,
  TemplateResponse,
  GenerationResponse
} from '@/types';

export const projectsApi = {
  async getProjects(): Promise<{ projects: Project[] }> {
    return apiClient.get('/api/projects');
  },

  async createProject(data: ProjectCreate): Promise<{ project: Project }> {
    return apiClient.post('/api/projects', data);
  },

  async getProject(projectId: string): Promise<ProjectResponse> {
    return apiClient.get(`/api/projects/${projectId}`);
  },

  async updateConfiguration(
    projectId: string, 
    config: { sections?: SectionConfig[] } | { slides?: SlideConfig[] }
  ): Promise<{ project: Project }> {
    return apiClient.put(`/api/projects/${projectId}/configuration`, config);
  },

  async deleteProject(projectId: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/projects/${projectId}`);
  },

  async generateContent(projectId: string): Promise<GenerationResponse> {
    return apiClient.post(`/api/projects/${projectId}/generate`);
  },

  async generateTemplate(
    projectId: string, 
    data: { topic: string; document_type: string }
  ): Promise<TemplateResponse> {
    return apiClient.post(`/api/projects/${projectId}/generate-template`, data);
  },

  async exportProject(projectId: string): Promise<Blob> {
    return apiClient.downloadFile(`/api/projects/${projectId}/export`);
  },
};