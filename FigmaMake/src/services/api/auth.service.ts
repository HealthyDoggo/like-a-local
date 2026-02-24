import { apiClient } from './client';
import { AuthResponse, EmailSignUpData, EmailSignInData, User } from '@/types/auth.types';

export const authService = {
  async signUpWithEmail(data: EmailSignUpData): Promise<AuthResponse> {
    return apiClient.request<AuthResponse>('/api/auth/signup/email', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    });
  },

  async signInWithEmail(data: EmailSignInData): Promise<AuthResponse> {
    return apiClient.request<AuthResponse>('/api/auth/signin/email', {
      method: 'POST',
      body: JSON.stringify(data),
      skipAuth: true,
    });
  },

  async signInWithGoogle(idToken: string): Promise<AuthResponse> {
    return apiClient.request<AuthResponse>('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify({ id_token: idToken }),
      skipAuth: true,
    });
  },

  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/auth/refresh', { refresh_token: refreshToken });
  },

  async logout(refreshToken: string): Promise<void> {
    return apiClient.post('/api/auth/logout', { refresh_token: refreshToken });
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/api/auth/me');
  },
};
