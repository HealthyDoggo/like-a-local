import { SocialLogin } from '@capgo/capacitor-social-login';
import { Capacitor } from '@capacitor/core';

const WEB_CLIENT_ID = import.meta.env.VITE_GOOGLE_WEB_CLIENT_ID || '';
const IOS_CLIENT_ID = import.meta.env.VITE_GOOGLE_IOS_CLIENT_ID || '';
const ANDROID_CLIENT_ID = import.meta.env.VITE_GOOGLE_ANDROID_CLIENT_ID || '';

let initialized = false;

export async function initGoogleAuth(): Promise<void> {
  if (initialized) return;

  try {
    // Get the appropriate client ID for the platform
    let clientId = WEB_CLIENT_ID;
    const platform = Capacitor.getPlatform();

    if (platform === 'ios') {
      clientId = IOS_CLIENT_ID || WEB_CLIENT_ID;
    } else if (platform === 'android') {
      clientId = ANDROID_CLIENT_ID || WEB_CLIENT_ID;
    }

    await SocialLogin.initialize({
      google: {
        webClientId: clientId,
        iOSClientId: IOS_CLIENT_ID,
        androidClientId: ANDROID_CLIENT_ID,
      }
    });

    initialized = true;
  } catch (error) {
    console.error('Failed to initialize Google Auth:', error);
    throw error;
  }
}

export async function signInWithGoogle(): Promise<string> {
  if (!initialized) {
    await initGoogleAuth();
  }

  try {
    const result = await SocialLogin.login({
      provider: 'google',
      options: {
        scopes: ['profile', 'email'],
        grantOfflineAccess: true,
      }
    });

    console.log('Full Google result:', JSON.stringify(result, null, 2));

    // Check for ID token in various possible locations
    const token = result.result?.idToken
      || result.result?.authentication?.idToken
      || result.result?.serverAuthCode
      || result.result?.accessToken?.token;

    if (!token) {
      console.error('No token found in result');
      throw new Error('No token received from Google');
    }

    console.log('Using token type:', token.startsWith('ya29') ? 'access_token' : 'id_token');
    return token;
  } catch (error) {
    console.error('Google sign-in failed:', error);
    throw error;
  }
}

export async function signOutGoogle(): Promise<void> {
  try {
    await SocialLogin.logout({ provider: 'google' });
  } catch (error) {
    console.error('Google sign-out failed:', error);
  }
}
