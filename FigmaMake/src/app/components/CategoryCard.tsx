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
  const colorValue = iconColor === 'teal' ? '#457B9D' : '#F4D35E';
  
  return (
    <motion.button
      onClick={onClick}
      className="w-full rounded-2xl p-4 shadow-sm"
      style={{ backgroundColor: 'var(--app-surface)' }}
      whileTap={{ scale: 0.95 }}
      whileHover={{ boxShadow: '0 8px 20px rgba(0, 0, 0, 0.1)' }}
    >
      <div className="flex flex-col items-start gap-3">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center"
          style={{ backgroundColor: `${colorValue}20` }}
        >
          <Icon className="w-6 h-6" style={{ color: colorValue }} />
        </div>
        <div className="flex flex-col items-start w-full">
          <h3 className="text-base font-semibold text-left w-full break-words overflow-hidden" style={{ color: 'var(--app-text-primary)' }}>
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
