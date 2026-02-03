import { apiClient } from './client';
import { AuthResponse, EmailSignUpData, EmailSignInData, User } from '@/types/auth.types';

export const authService = {
  async signUpWithEmail(data: EmailSignUpData): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/auth/signup/email', data);
  },

  async signInWithEmail(data: EmailSignInData): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/auth/signin/email', data);
  },

  async signInWithGoogle(idToken: string): Promise<AuthResponse> {
    return apiClient.post<AuthResponse>('/api/auth/google', { id_token: idToken });
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
