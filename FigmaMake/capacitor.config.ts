import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'com.likealocal.app',
  appName: 'Like a Local',
  webDir: 'dist',
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
    GoogleAuth: {
      scopes: ['profile', 'email'],
      serverClientId: process.env.VITE_GOOGLE_WEB_CLIENT_ID || '',
      forceCodeForRefreshToken: true,
    },
  },
};

export default config;
