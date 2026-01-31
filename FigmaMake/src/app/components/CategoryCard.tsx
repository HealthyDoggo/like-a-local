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
      className="flex-shrink-0 w-[160px] bg-white rounded-2xl p-4 shadow-sm"
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
        <div className="flex flex-col items-start">
          <h3 className="text-base font-semibold" style={{ color: '#1D3557' }}>
            {title}
          </h3>
          <p className="text-xs" style={{ color: '#6B7280' }}>
            {tipCount} {tipCount === 1 ? 'tip' : 'tips'}
          </p>
        </div>
      </div>
    </motion.button>
  );
}
