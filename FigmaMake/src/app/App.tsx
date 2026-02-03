import { useEffect } from 'react';
import { RouterProvider } from 'react-router';
import { router } from '@/app/routes';
import { LanguageProvider } from '@/contexts/LanguageContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { initGoogleAuth } from '@/services/oauth/google.service';

export default function App() {
  // Initialize Google Auth on app start
  useEffect(() => {
    initGoogleAuth().catch((error) => {
      console.error('Failed to initialize Google Auth:', error);
    });
  }, []);

  return (
    <AuthProvider>
      <LanguageProvider>
        <RouterProvider router={router} />
      </LanguageProvider>
    </AuthProvider>
  );
}
