import { useState } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Mail, Lock, User, Eye, EyeOff, Globe } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';

export function EmailSignUpScreen() {
  const navigate = useNavigate();
  const { signUpWithEmail } = useAuth();
  const { language, setLanguage, availableLanguages } = useLanguage();
  const { reducedMotion } = useSettings();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPasswordStrength = (password: string): { strength: string; color: string; width: string } => {
    if (password.length === 0) return { strength: '', color: '', width: '0%' };
    if (password.length < 8) return { strength: 'Weak', color: '#ef4444', width: '33%' };

    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) return { strength: 'Fair', color: '#f59e0b', width: '66%' };
    return { strength: 'Strong', color: '#10b981', width: '100%' };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);

    try {
      await signUpWithEmail({
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName,
        preferred_language: language,
      });
      navigate('/intent');
    } catch (err: any) {
      setError(err.data?.detail || err.message || 'Sign-up failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="min-h-screen max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
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
            Create an account
          </h1>
          <p className="text-[16px] leading-[24px]" style={{ color: 'var(--app-text-secondary)' }}>
            Sign up to save tips and share local knowledge
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
          {/* Full name input */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--app-text-primary)' }}>
              <div className="flex items-center gap-2">
                <User className="w-4 h-4" style={{ color: 'var(--app-text-accent)' }} />
                <span>Full Name</span>
              </div>
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              placeholder="John Doe"
              required
              className="w-full px-4 py-3 rounded-xl border-2"
              style={{
                borderColor: 'var(--app-border)',
                color: 'var(--app-text-primary)',
                backgroundColor: 'var(--app-bg)'
              }}
            />
          </div>

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
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="At least 8 characters"
                required
                minLength={8}
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
            {/* Password strength indicator */}
            {formData.password.length > 0 && (
              <div className="mt-2">
                <div className="h-1 w-full bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-300"
                    style={{
                      width: passwordStrength.width,
                      backgroundColor: passwordStrength.color,
                    }}
                  />
                </div>
                <p className="text-xs mt-1" style={{ color: passwordStrength.color }}>
                  {passwordStrength.strength}
                </p>
              </div>
            )}
          </div>

          {/* Confirm password input */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--app-text-primary)' }}>
              <div className="flex items-center gap-2">
                <Lock className="w-4 h-4" style={{ color: 'var(--app-text-accent)' }} />
                <span>Confirm Password</span>
              </div>
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="Re-enter your password"
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
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1"
                style={{ color: 'var(--app-text-secondary)' }}
              >
                {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Language selector */}
          <div>
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
            <p className="text-xs mt-1" style={{ color: 'var(--app-text-secondary)' }}>
              Tips will be shown in your preferred language
            </p>
          </div>

          {/* Submit button */}
          <motion.button
            type="submit"
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-xl disabled:opacity-50 mt-2"
            style={{ backgroundColor: 'var(--app-text-accent)', color: '#fff' }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            ) : null}
            <span className="font-medium text-[15px]">
              {isLoading ? 'Creating account...' : 'Create account'}
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
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.5 }}
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
