import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, EmailSignUpData, EmailSignInData } from '@/types/auth.types';
import { authService } from '@/services/api/auth.service';
import { signInWithGoogle as googleSignIn, signOutGoogle } from '@/services/oauth/google.service';
import { getAccessToken, getRefreshToken, getUserData, setTokens, setUserData, clearAuth, refreshAuthToken } from '@/utils/tokenStorage';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signInWithEmail: (email: string, password: string) => Promise<void>;
  signUpWithEmail: (data: EmailSignUpData) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load auth on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  // Auto-refresh token every 14 minutes
  useEffect(() => {
    if (user) {
      const interval = setInterval(async () => {
        await refreshAuthToken();
      }, 14 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const initializeAuth = async () => {
    try {
      const token = await getAccessToken();
      if (token) {
        // Try to load user data from storage
        const userData = await getUserData();
        if (userData) {
          setUser(JSON.parse(userData));
        } else {
          // Fetch user data from API
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          await setUserData(JSON.stringify(currentUser));
        }
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error);
      await clearAuth();
    } finally {
      setIsLoading(false);
    }
  };

  const signInWithEmail = async (email: string, password: string) => {
    try {
      const response = await authService.signInWithEmail({ email, password });
      await setTokens(response.access_token, response.refresh_token);
      await setUserData(JSON.stringify(response.user));
      setUser(response.user);
    } catch (error) {
      console.error('Email sign-in failed:', error);
      throw error;
    }
  };

  const signUpWithEmail = async (data: EmailSignUpData) => {
    try {
      const response = await authService.signUpWithEmail(data);
      await setTokens(response.access_token, response.refresh_token);
      await setUserData(JSON.stringify(response.user));
      setUser(response.user);
    } catch (error) {
      console.error('Email sign-up failed:', error);
      throw error;
    }
  };

  const signInWithGoogle = async () => {
    try {
      const idToken = await googleSignIn();
      const response = await authService.signInWithGoogle(idToken);
      await setTokens(response.access_token, response.refresh_token);
      await setUserData(JSON.stringify(response.user));
      setUser(response.user);
    } catch (error) {
      console.error('Google sign-in failed:', error);
      throw error;
    }
  };

  const signOut = async () => {
    try {
      const refreshToken = await getRefreshToken();
      if (refreshToken) {
        await authService.logout(refreshToken);
      }
      await signOutGoogle();
      await clearAuth();
      setUser(null);
    } catch (error) {
      console.error('Sign-out failed:', error);
      await clearAuth();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      signInWithEmail,
      signUpWithEmail,
      signInWithGoogle,
      signOut,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
