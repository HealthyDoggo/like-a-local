import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Moon, Sun, BookOpen, Volume2, Zap } from 'lucide-react';
import { BottomNav } from '@/app/components/BottomNav';
import { notifySettingsChange } from '@/hooks/useSettings';

export function SettingsScreen() {
  const navigate = useNavigate();
  
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true';
  });
  
  const [readingMode, setReadingMode] = useState(() => {
    return localStorage.getItem('readingMode') === 'true';
  });
  
  const [readAloud, setReadAloud] = useState(() => {
    return localStorage.getItem('readAloud') === 'true';
  });
  
  const [reducedMotion, setReducedMotion] = useState(() => {
    return localStorage.getItem('reducedMotion') === 'true';
  });

  useEffect(() => {
    localStorage.setItem('darkMode', darkMode.toString());
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    notifySettingsChange();
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('readingMode', readingMode.toString());
    if (readingMode) {
      document.documentElement.classList.add('reading-mode');
    } else {
      document.documentElement.classList.remove('reading-mode');
    }
    notifySettingsChange();
  }, [readingMode]);

  useEffect(() => {
    localStorage.setItem('readAloud', readAloud.toString());
    notifySettingsChange();
  }, [readAloud]);

  useEffect(() => {
    localStorage.setItem('reducedMotion', reducedMotion.toString());
    if (reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }
    notifySettingsChange();
  }, [reducedMotion]);

  const ToggleItem = ({
    icon: Icon,
    title,
    description,
    value,
    onChange
  }: {
    icon: any;
    title: string;
    description: string;
    value: boolean;
    onChange: (value: boolean) => void;
  }) => (
    <motion.div
      className="flex items-center justify-between py-4 border-b"
      style={{ borderColor: 'var(--app-border)' }}
      whileTap={reducedMotion ? {} : { scale: 0.99 }}
    >
      <div className="flex items-start gap-3 flex-1">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: 'var(--app-surface-accent)' }}
        >
          <Icon className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
        </div>
        <div className="flex-1">
          <h3
            className="text-[15px] leading-[20px] mb-1"
            style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}
          >
            {title}
          </h3>
          <p className="text-[13px] leading-[18px]" style={{ color: 'var(--app-text-secondary)' }}>
            {description}
          </p>
        </div>
      </div>
      <button
        onClick={() => onChange(!value)}
        className="ml-3 w-12 h-7 rounded-full relative transition-colors flex-shrink-0"
        style={{ 
          backgroundColor: value ? 'var(--app-text-accent)' : 'var(--app-border)'
        }}
      >
        <motion.div
          className="w-5 h-5 rounded-full absolute top-1"
          style={{ backgroundColor: 'var(--app-surface)' }}
          animate={{ left: value ? '26px' : '4px' }}
          transition={reducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 500, damping: 30 }}
        />
      </button>
    </motion.div>
  );

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2"
            style={{ color: 'var(--app-text-accent)' }}
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1
            className="text-[24px] leading-[28px]"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Settings
          </h1>
        </motion.div>

        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
        >
          <h2
            className="text-[13px] uppercase tracking-wider mb-4"
            style={{ color: 'var(--app-text-secondary)', fontWeight: 600 }}
          >
            Accessibility
          </h2>

          <div className="rounded-xl shadow-sm p-5" style={{ backgroundColor: 'var(--app-surface)' }}>
            <ToggleItem
              icon={darkMode ? Moon : Sun}
              title="Dark mode"
              description="Switch to a darker color scheme"
              value={darkMode}
              onChange={setDarkMode}
            />

            <ToggleItem
              icon={BookOpen}
              title="Reading mode"
              description="Larger text and increased spacing"
              value={readingMode}
              onChange={setReadingMode}
            />

            <ToggleItem
              icon={Volume2}
              title="Read aloud"
              description="Enable text-to-speech for tips"
              value={readAloud}
              onChange={setReadAloud}
            />

            <ToggleItem
              icon={Zap}
              title="Reduced motion"
              description="Minimize animations and transitions"
              value={reducedMotion}
              onChange={setReducedMotion}
            />
          </div>

          <motion.div
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={reducedMotion ? false : { opacity: 1 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.3 }}
            className="mt-6"
          >
            <p className="text-[13px] leading-[20px] text-center px-4" style={{ color: 'var(--app-text-secondary)' }}>
              These settings help make the app more comfortable and accessible for everyone
            </p>
          </motion.div>
        </motion.div>
      </div>

      <BottomNav />
    </div>
  );
}
