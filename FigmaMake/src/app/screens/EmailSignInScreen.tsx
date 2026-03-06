import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useSettings } from '@/hooks/useSettings';

export function EmailSignInScreen() {
  const navigate = useNavigate();
  const { signInWithEmail, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { reducedMotion } = useSettings();

  // Navigate once React has applied the auth state update
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/home', { replace: true });
    }
  }, [isAuthenticated]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await signInWithEmail(email, password);
      // Navigation is handled by the isAuthenticated useEffect above
    } catch (err: any) {
      setError(err.data?.detail || err.message || 'Sign-in failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        {/* Header with back button */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
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
          initial={reducedMotion ? false : { opacity: 0, y: 20 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          className="mb-8"
        >
          <h1
            className="text-[28px] leading-[34px] mb-3"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Sign in with email
          </h1>
          <p className="text-[16px] leading-[24px]" style={{ color: 'var(--app-text-secondary)' }}>
            Enter your email and password to continue
          </p>
        </motion.div>

        {/* Error message */}
        {error && (
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: -10 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            className="mb-6 px-4 py-3 rounded-xl"
            style={{ backgroundColor: 'var(--app-error-bg)', color: 'var(--app-error-text)' }}
          >
            <p className="text-sm">{error}</p>
          </motion.div>
        )}

        {/* Form */}
        <motion.form
          initial={reducedMotion ? false : { opacity: 0, y: 20 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          onSubmit={handleSubmit}
          className="flex flex-col gap-4"
        >
          {/* Email input */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--app-text-primary)' }}>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4" style={{ color: 'var(--app-text-accent)' }} />
                <span>Email</span>
              </div>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              className="w-full px-4 py-3 rounded-xl border-2"
              style={{
                borderColor: 'var(--app-border)',
                color: 'var(--app-text-primary)',
                backgroundColor: 'var(--app-bg)'
              }}
            />
          </div>

          {/* Password input */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--app-text-primary)' }}>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" style={{ color: 'var(--app-text-accent)' }} />
                <span>Password</span>
              </div>
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                className="w-full px-4 py-3 pr-12 rounded-xl border-2"
                style={{
                  borderColor: 'var(--app-border)',
                  color: 'var(--app-text-primary)',
                  backgroundColor: 'var(--app-bg)'
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1"
                style={{ color: 'var(--app-text-secondary)' }}
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Forgot password link (future) */}
          <div className="text-right">
            <button
              type="button"
              onClick={() => {/* TODO: implement forgot password */}}
              className="text-sm font-medium"
              style={{ color: 'var(--app-text-accent)' }}
            >
              Forgot password?
            </button>
          </div>

          {/* Submit button */}
          <motion.button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl disabled:opacity-50"
            style={{ backgroundColor: 'var(--app-text-accent)', color: '#fff' }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            ) : null}
            <span className="font-medium text-[15px]">
              {isLoading ? 'Signing in...' : 'Sign in'}
            </span>
          </motion.button>
        </motion.form>

        {/* Footer text */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.4 }}
          className="mt-8"
        >
          <p className="text-[13px] text-center leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
            Don't have an account?{' '}
            <button
              onClick={() => navigate('/sign-up')}
              className="font-medium"
              style={{ color: 'var(--app-text-accent)' }}
            >
              Sign up
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
