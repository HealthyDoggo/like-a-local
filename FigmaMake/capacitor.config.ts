import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.likealocal.app',
  appName: 'Like a Local',
  webDir: 'dist',
  ios: {
    scheme: 'App',
  },
  server: {
    androidScheme: 'https',
    cleartext: true, // Allow HTTP for development API
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
      launchAutoHide: true,
      backgroundColor: '#FFFFFF',
      showSpinner: false,
    },
    SocialLogin: {
      google: {
        webClientId: process.env.VITE_GOOGLE_WEB_CLIENT_ID || '',
        iOSClientId: process.env.VITE_GOOGLE_IOS_CLIENT_ID || '',
        androidClientId: process.env.VITE_GOOGLE_ANDROID_CLIENT_ID || '',
      },
    },
  },
};

export default config;
