import { motion } from 'motion/react';
import { LucideIcon } from 'lucide-react';

interface CategoryCardProps {
  icon: LucideIcon;
  title: string;
  tipCount: number;
  onClick: () => void;
  iconColor?: 'teal' | 'yellow';
}

export function CategoryCard({ icon: Icon, title, tipCount, onClick, iconColor = 'teal' }: CategoryCardProps) {
  const colorVar = iconColor === 'teal' ? 'var(--teal)' : 'var(--golden-yellow)';
  const bgVar = iconColor === 'teal' ? 'var(--app-teal-alpha)' : 'var(--app-yellow-alpha)';

  return (
    <motion.button
      onClick={onClick}
      className="w-full rounded-2xl px-3 py-2.5 shadow-sm"
      style={{ backgroundColor: 'var(--app-surface)' }}
      whileTap={{ scale: 0.95 }}
      whileHover={{ boxShadow: '0 8px 20px rgba(0, 0, 0, 0.1)' }}
    >
      <div className="flex flex-row items-center gap-2.5">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
          style={{ backgroundColor: bgVar }}
        >
          <Icon className="w-4 h-4" style={{ color: colorVar }} />
        </div>
        <div className="flex flex-col items-start min-w-0">
          <h3 className="text-sm font-semibold text-left w-full" style={{ color: 'var(--app-text-primary)' }}>
            {title}
          </h3>
          <p className="text-xs text-left" style={{ color: 'var(--app-text-secondary)' }}>
            {tipCount} {tipCount === 1 ? 'tip' : 'tips'}
          </p>
        </div>
      </div>
    </motion.button>
  );
}
