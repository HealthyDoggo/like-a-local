import { Capacitor } from '@capacitor/core';
import type { SecureStoragePluginPlugin } from 'capacitor-secure-storage-plugin';

const KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
};

const isNative = Capacitor.isNativePlatform();

// Lazy load SecureStorage only on native platforms
let SecureStorage: SecureStoragePluginPlugin | null = null;
if (isNative) {
  import('capacitor-secure-storage-plugin').then((module) => {
    SecureStorage = module.SecureStoragePlugin;
  });
}

// Token storage functions
export async function setTokens(accessToken: string, refreshToken: string): Promise<void> {
  if (isNative && SecureStorage) {
    await SecureStorage.set({ key: KEYS.ACCESS_TOKEN, value: accessToken });
    await SecureStorage.set({ key: KEYS.REFRESH_TOKEN, value: refreshToken });
  } else {
    localStorage.setItem(KEYS.ACCESS_TOKEN, accessToken);
    localStorage.setItem(KEYS.REFRESH_TOKEN, refreshToken);
  }
}

export async function getAccessToken(): Promise<string | null> {
  if (isNative && SecureStorage) {
    try {
      const result = await SecureStorage.get({ key: KEYS.ACCESS_TOKEN });
      return result.value;
    } catch {
      return null;
    }
  } else {
    return localStorage.getItem(KEYS.ACCESS_TOKEN);
  }
}

export async function getRefreshToken(): Promise<string | null> {
  if (isNative && SecureStorage) {
    try {
      const result = await SecureStorage.get({ key: KEYS.REFRESH_TOKEN });
      return result.value;
    } catch {
      return null;
    }
  } else {
    return localStorage.getItem(KEYS.REFRESH_TOKEN);
  }
}

export async function setUserData(userData: string): Promise<void> {
  if (isNative && SecureStorage) {
    await SecureStorage.set({ key: KEYS.USER_DATA, value: userData });
  } else {
    localStorage.setItem(KEYS.USER_DATA, userData);
  }
}

export async function getUserData(): Promise<string | null> {
  if (isNative && SecureStorage) {
    try {
      const result = await SecureStorage.get({ key: KEYS.USER_DATA });
      return result.value;
    } catch {
      return null;
    }
  } else {
    return localStorage.getItem(KEYS.USER_DATA);
  }
}

export async function clearAuth(): Promise<void> {
  if (isNative && SecureStorage) {
    try {
      await SecureStorage.remove({ key: KEYS.ACCESS_TOKEN });
      await SecureStorage.remove({ key: KEYS.REFRESH_TOKEN });
      await SecureStorage.remove({ key: KEYS.USER_DATA });
    } catch {
      // Ignore errors
    }
  } else {
    localStorage.removeItem(KEYS.ACCESS_TOKEN);
    localStorage.removeItem(KEYS.REFRESH_TOKEN);
    localStorage.removeItem(KEYS.USER_DATA);
  }
}

// Refresh token function (uses API client, will be imported by client.ts)
export async function refreshAuthToken(): Promise<boolean> {
  const refreshToken = await getRefreshToken();
  if (!refreshToken) {
    return false;
  }

  try {
    // Import dynamically to avoid circular dependency
    const { apiClient } = await import('@/services/api/client');
    const response = await fetch(`${apiClient.baseURL}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      await clearAuth();
      return false;
    }

    const data = await response.json();
    await setTokens(data.access_token, data.refresh_token);
    await setUserData(JSON.stringify(data.user));
    return true;
  } catch {
    await clearAuth();
    return false;
  }
}
