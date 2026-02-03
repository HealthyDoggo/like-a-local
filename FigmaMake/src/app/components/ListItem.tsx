import { motion } from 'motion/react';
import { ChevronRight } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

interface ListItemProps {
  flag?: string;
  title: string;
  subtitle?: string;
  onClick: () => void;
}

export function ListItem({ flag, title, subtitle, onClick }: ListItemProps) {
  const { reducedMotion } = useSettings();

  return (
    <motion.button
      onClick={onClick}
      className="w-full flex items-center justify-between p-4 rounded-xl shadow-sm"
      style={{ backgroundColor: 'var(--app-surface)' }}
      whileTap={reducedMotion ? {} : { scale: 0.98 }}
    >
      <div className="flex items-center gap-3">
        {flag && (
          <div className="w-8 h-8 rounded-full flex items-center justify-center overflow-hidden" style={{ backgroundColor: 'var(--app-surface-secondary)' }}>
            <img
              src={flag}
              alt=""
              className="w-full h-full object-cover"
            />
          </div>
        )}
        <div className="flex flex-col items-start">
          <span className="text-[15px] font-medium" style={{ color: 'var(--app-text-primary)' }}>
            {title}
          </span>
          {subtitle && (
            <span className="text-[13px]" style={{ color: 'var(--app-text-secondary)' }}>
              {subtitle}
            </span>
          )}
        </div>
      </div>
      <ChevronRight className="w-5 h-5" style={{ color: 'var(--app-text-secondary)' }} />
    </motion.button>
  );
}
