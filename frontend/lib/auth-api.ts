import { apiClient } from './api';
import { 
  User, 
  LoginCredentials, 
  RegisterData, 
  AuthResponse 
} from '@/types';

export const authApi = {
  async register(data: RegisterData): Promise<{ message: string; user_id: string }> {
    return apiClient.post('/api/auth/register', data);
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', credentials);
    // Set the token in the API client
    apiClient.setToken(response.access_token);
    return response;
  },

  async getCurrentUser(): Promise<{ user: User }> {
    return apiClient.get('/api/auth/me');
  },

  logout() {
    apiClient.setToken(null);
  },
};