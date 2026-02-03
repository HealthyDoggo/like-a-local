export interface User {
  id: number;
  email: string;
  full_name: string | null;
  profile_picture_url: string | null;
  preferred_language: string;
  auth_provider: 'email' | 'google';
  email_verified: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface EmailSignUpData {
  email: string;
  password: string;
  full_name: string;
  preferred_language?: string;
}

export interface EmailSignInData {
  email: string;
  password: string;
}
