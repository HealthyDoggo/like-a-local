import { getAccessToken, refreshAuthToken, clearAuth } from '@/utils/tokenStorage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://149.86.36.226:8001';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

interface RequestConfig extends RequestInit {
  params?: Record<string, any>;
  skipAuth?: boolean;
}

export const apiClient = {
  baseURL: API_BASE_URL,

  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const { params, skipAuth, ...fetchConfig } = config;

    let url = `${API_BASE_URL}${endpoint}`;
    if (params) {
      const queryString = new URLSearchParams(
        Object.entries(params)
          .filter(([_, value]) => value !== undefined && value !== null)
          .map(([key, value]) => [key, String(value)])
      ).toString();
      if (queryString) url += `?${queryString}`;
    }

    // Add auth header if token exists (unless skipAuth is true)
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(fetchConfig.headers as Record<string, string>),
    };

    if (!skipAuth) {
      const token = await getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    console.log('Making API request to:', url);
    console.log('Request headers:', headers);
    console.log('Request body:', fetchConfig.body);

    let response;
    try {
      response = await fetch(url, {
        ...fetchConfig,
        headers,
      });
      console.log('Response status:', response.status, response.statusText);
    } catch (error: any) {
      console.error('Network error during fetch:', error);
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      throw new Error(`Network error: ${error.message || 'Failed to connect to server'}`);
    }

    // Handle 401 with token refresh
    if (response.status === 401 && !skipAuth) {
      const token = await getAccessToken();
      if (token) {
        const refreshed = await refreshAuthToken();
        if (refreshed) {
          // Retry with new token
          const newToken = await getAccessToken();
          if (newToken) {
            headers['Authorization'] = `Bearer ${newToken}`;
            response = await fetch(url, {
              ...fetchConfig,
              headers,
            });
          }
        } else {
          await clearAuth();
          throw new ApiError(401, 'Session expired', null);
        }
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new ApiError(response.status, response.statusText, errorData);
    }

    return response.json();
  },

  get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params });
  },

  post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
