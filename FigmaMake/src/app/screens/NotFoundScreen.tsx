import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { Home, ArrowLeft } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

export function NotFoundScreen() {
  const navigate = useNavigate();
  const { reducedMotion } = useSettings();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-5" style={{ backgroundColor: 'var(--app-bg)' }}>
      <motion.div
        initial={reducedMotion ? false : { opacity: 0, y: -20 }}
        animate={reducedMotion ? false : { opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-[72px] font-bold mb-4" style={{ color: 'var(--app-text-accent)' }}>
          404
        </h1>
        <h2 className="text-[24px] leading-[28px] mb-3" style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}>
          Page not found
        </h2>
        <p className="text-[15px] leading-[22px] mb-8" style={{ color: 'var(--app-text-secondary)' }}>
          The page you're looking for doesn't exist or is still being built.
        </p>

        <div className="flex flex-col gap-3">
          <motion.button
            onClick={() => navigate(-1)}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl"
            style={{ backgroundColor: 'var(--app-text-accent)', color: 'var(--app-surface)' }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Go back</span>
          </motion.button>

          <motion.button
            onClick={() => navigate('/home')}
            className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl border-2"
            style={{ borderColor: 'var(--app-border)', color: 'var(--app-text-primary)' }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
          >
            <Home className="w-5 h-5" />
            <span className="font-medium">Go home</span>
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
