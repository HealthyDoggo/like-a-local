import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Mail, Apple, Globe } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';

export function SignUpScreen() {
  const navigate = useNavigate();
  const { language, setLanguage, availableLanguages } = useLanguage();
  const { signInWithGoogle, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/intent', { replace: true });
    }
  }, [isAuthenticated]);

  const handleSignUp = async (method: 'email' | 'apple' | 'google') => {
    if (method === 'email') {
      navigate('/sign-up/email');
      return;
    }

    if (method === 'apple') {
      setError('Apple sign-up is not yet implemented');
      return;
    }

    if (method === 'google') {
      setIsLoading(true);
      setError(null);

      try {
        await signInWithGoogle();
        navigate('/intent');
      } catch (err: any) {
        const detail = err.data?.detail || err.message || 'Google sign-up failed';
        setError(detail);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-8 py-8">
        {/* Header with back button */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center mb-12"
        >
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2"
            style={{ color: 'var(--app-text-accent)' }}
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
        </motion.div>

        {/* Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-12"
        >
          <h1
            className="text-[32px] leading-[38px] mb-3"
            style={{ color: 'var(--app-text-primary)', fontWeight: 700 }}
          >
            Create an account
          </h1>
          <p className="text-[16px] leading-[24px]" style={{ color: 'var(--app-text-secondary)' }}>
            Save tips and share local knowledge with travelers
          </p>
        </motion.div>

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-4 px-4 py-3 rounded-lg"
            style={{ backgroundColor: '#fee', color: '#c00' }}
          >
            <p className="text-sm">{error}</p>
          </motion.div>
        )}

        {/* Sign-up options */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-col gap-4"
        >
          <motion.button
            onClick={() => handleSignUp('email')}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl disabled:opacity-50"
            style={{ backgroundColor: '#457B9D', color: '#fff' }}
            whileTap={{ scale: 0.98 }}
          >
            <Mail className="w-5 h-5" />
            <span className="font-medium text-[15px]">Continue with email</span>
          </motion.button>

          <motion.button
            onClick={() => handleSignUp('apple')}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl disabled:opacity-50"
            style={{ backgroundColor: '#000', color: '#fff' }}
            whileTap={{ scale: 0.98 }}
          >
            <Apple className="w-5 h-5" />
            <span className="font-medium text-[15px]">Continue with Apple</span>
          </motion.button>

          <motion.button
            onClick={() => handleSignUp('google')}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl border-2 disabled:opacity-50"
            style={{ borderColor: 'var(--app-border)', color: 'var(--app-text-primary)' }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="w-5 h-5 flex items-center justify-center">
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-600"></div>
              ) : (
                <svg viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              )}
            </div>
            <span className="font-medium text-[15px]">
              {isLoading ? 'Signing up...' : 'Continue with Google'}
            </span>
          </motion.button>
        </motion.div>

        {/* Language selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8"
        >
          <label className="block text-sm font-medium mb-2" style={{ color: 'var(--app-text-primary)' }}>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4" style={{ color: 'var(--app-text-accent)' }} />
              <span>Preferred Language</span>
            </div>
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border-2"
            style={{
              borderColor: 'var(--app-border)',
              color: 'var(--app-text-primary)',
              backgroundColor: 'var(--app-bg)'
            }}
          >
            {availableLanguages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.native_name} ({lang.name})
              </option>
            ))}
          </select>
          <p className="text-sm mt-1" style={{ color: 'var(--app-text-secondary)' }}>
            Tips will be shown in your preferred language
          </p>
        </motion.div>

        {/* Footer text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="mt-8"
        >
          <p className="text-[13px] text-center leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            Already have an account?{' '}
            <button
              onClick={() => navigate('/sign-in')}
              className="font-medium"
              style={{ color: 'var(--app-text-accent)' }}
            >
              Sign in
            </button>
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6"
        >
          <p className="text-[12px] text-center leading-[18px]" style={{ color: 'var(--app-text-secondary)', opacity: 0.7 }}>
            By continuing, you agree to our terms and privacy policy
          </p>
        </motion.div>
      </div>
    </div>
  );
}