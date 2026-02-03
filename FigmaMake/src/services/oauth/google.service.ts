import { GoogleAuth } from '@codetrix-studio/capacitor-google-auth';
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

    await GoogleAuth.initialize({
      clientId,
      scopes: ['profile', 'email'],
      grantOfflineAccess: true,
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
    const result = await GoogleAuth.signIn();
    if (!result.authentication?.idToken) {
      throw new Error('No ID token received from Google');
    }
    return result.authentication.idToken;
  } catch (error) {
    console.error('Google sign-in failed:', error);
    throw error;
  }
}

export async function signOutGoogle(): Promise<void> {
  try {
    await GoogleAuth.signOut();
  } catch (error) {
    console.error('Google sign-out failed:', error);
  }
}
