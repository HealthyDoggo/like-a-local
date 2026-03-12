import { motion } from 'motion/react';
import { Home, Plus, Heart, User } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router';
import { useSettings } from '@/hooks/useSettings';

interface NavItem {
  icon: typeof Home;
  label: string;
  path: string;
}

const navItems: NavItem[] = [
  { icon: Home, label: 'Explore', path: '/home' },
  { icon: Heart, label: 'Saved', path: '/saved' },
  { icon: Plus, label: 'Contribute', path: '/contribute' },
  { icon: User, label: 'Profile', path: '/profile' },
];

export function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const { reducedMotion } = useSettings();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 border-t px-4"
      style={{
        backgroundColor: 'var(--app-surface)',
        borderColor: 'var(--app-border)',
        paddingTop: '0.75rem',
        paddingBottom: 'max(0.75rem, env(safe-area-inset-bottom))'
      }}
    >
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <motion.button
              key={item.label}
              onClick={() => navigate(item.path)}
              className="flex flex-col items-center gap-1 min-w-[44px] min-h-[44px] justify-center"
              whileTap={reducedMotion ? {} : { scale: 0.9 }}
              animate={reducedMotion ? {} : (isActive ? { scale: 1.1 } : { scale: 1 })}
            >
              <Icon
                className="w-6 h-6"
                style={{ 
                  color: isActive ? 'var(--app-text-accent)' : 'var(--app-text-secondary)',
                  strokeWidth: isActive ? 2.5 : 2
                }}
              />
              <span
                className="text-[10px]"
                style={{ color: isActive ? 'var(--app-text-accent)' : 'var(--app-text-secondary)' }}
              >
                {item.label}
              </span>
            </motion.button>
          );
        })}
      </div>
    </nav>
  );
}