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
      }
    });

    console.log('Full Google result:', JSON.stringify(result, null, 2));

    // Only accept ID tokens (JWTs) — the backend can't verify serverAuthCode or access tokens
    const token = result.result?.idToken
      || result.result?.authentication?.idToken;

    if (!token) {
      console.error('No ID token found in result. Full result:', JSON.stringify(result, null, 2));
      throw new Error('No ID token received from Google');
    }

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
