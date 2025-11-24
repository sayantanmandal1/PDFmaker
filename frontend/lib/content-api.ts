import { apiClient } from './api';
import { 
  Section, 
  Slide, 
  RefinementRequest,
  RefinementHistory, 
  FeedbackCreate, 
  CommentCreate,
  Feedback,
  Comment
} from '@/types';

export const contentApi = {
  // Refinement endpoints
  async refineSection(sectionId: string, data: RefinementRequest): Promise<{ section: Section }> {
    return apiClient.post(`/api/sections/${sectionId}/refine`, data);
  },

  async refineSlide(slideId: string, data: RefinementRequest): Promise<{ slide: Slide }> {
    return apiClient.post(`/api/slides/${slideId}/refine`, data);
  },

  async getSectionRefinementHistory(sectionId: string): Promise<RefinementHistory[]> {
    return apiClient.get(`/api/sections/${sectionId}/refinement-history`);
  },

  async getSlideRefinementHistory(slideId: string): Promise<RefinementHistory[]> {
    return apiClient.get(`/api/slides/${slideId}/refinement-history`);
  },

  // Feedback endpoints
  async addSectionFeedback(sectionId: string, data: FeedbackCreate): Promise<{ feedback: Feedback }> {
    return apiClient.post(`/api/sections/${sectionId}/feedback`, data);
  },

  async addSlideFeedback(slideId: string, data: FeedbackCreate): Promise<{ feedback: Feedback }> {
    return apiClient.post(`/api/slides/${slideId}/feedback`, data);
  },

  // Comment endpoints
  async addSectionComment(sectionId: string, data: CommentCreate): Promise<{ comment: Comment }> {
    return apiClient.post(`/api/sections/${sectionId}/comments`, data);
  },

  async addSlideComment(slideId: string, data: CommentCreate): Promise<{ comment: Comment }> {
    return apiClient.post(`/api/slides/${slideId}/comments`, data);
  },

  async updateComment(commentId: string, data: CommentCreate): Promise<{ comment: Comment }> {
    return apiClient.put(`/api/comments/${commentId}`, data);
  },

  async deleteComment(commentId: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/comments/${commentId}`);
  },

  async getSectionComments(sectionId: string): Promise<Comment[]> {
    return apiClient.get(`/api/sections/${sectionId}/comments`);
  },

  async getSlideComments(slideId: string): Promise<Comment[]> {
    return apiClient.get(`/api/slides/${slideId}/comments`);
  },
};