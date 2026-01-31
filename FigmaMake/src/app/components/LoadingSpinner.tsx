import { motion } from 'motion/react';
import { useSettings } from '@/hooks/useSettings';

export function LoadingSpinner() {
  const { reducedMotion } = useSettings();
  
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <motion.div
        animate={reducedMotion ? {} : { rotate: 360 }}
        transition={reducedMotion ? { duration: 0 } : { duration: 1, repeat: Infinity, ease: 'linear' }}
        className="w-12 h-12 border-4 rounded-full"
        style={{
          borderColor: 'var(--app-border)',
          borderTopColor: 'var(--app-text-accent)',
        }}
      />
    </div>
  );
}
