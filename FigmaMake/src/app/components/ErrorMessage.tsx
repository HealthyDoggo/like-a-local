import { AlertCircle } from 'lucide-react';
import { motion } from 'motion/react';
import { useSettings } from '@/hooks/useSettings';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  const { reducedMotion } = useSettings();
  
  return (
    <motion.div
      initial={reducedMotion ? false : { opacity: 0, y: -10 }}
      animate={reducedMotion ? false : { opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center min-h-[200px] px-6"
    >
      <AlertCircle className="w-12 h-12 mb-4" style={{ color: '#EF4444' }} />
      <p className="text-center mb-4" style={{ color: 'var(--app-text-secondary)' }}>
        {message}
      </p>
      {onRetry && (
        <motion.button
          onClick={onRetry}
          className="px-6 py-2 rounded-lg"
          style={{ backgroundColor: 'var(--app-text-accent)', color: 'var(--app-surface)' }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          Try Again
        </motion.button>
      )}
    </motion.div>
  );
}
