import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { BottomNav } from '@/app/components/BottomNav';
import { TipCard } from '@/app/components/TipCard';
import { tipsByCategory } from '@/app/data/tips';
import { Heart } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

export function SavedScreen() {
  const [savedTips, setSavedTips] = useState<string[]>(() => {
    const saved = localStorage.getItem('savedTips');
    return saved ? JSON.parse(saved) : [];
  });
  const { reducedMotion } = useSettings();

  useEffect(() => {
    const handleStorage = () => {
      const saved = localStorage.getItem('savedTips');
      setSavedTips(saved ? JSON.parse(saved) : []);
    };
    
    window.addEventListener('storage', handleStorage);
    const interval = setInterval(handleStorage, 500);
    
    return () => {
      window.removeEventListener('storage', handleStorage);
      clearInterval(interval);
    };
  }, []);

  const handleSave = (tipId: string) => {
    const newSavedTips = savedTips.filter(id => id !== tipId);
    setSavedTips(newSavedTips);
    localStorage.setItem('savedTips', JSON.stringify(newSavedTips));
  };

  // Get all tips from all categories
  const allTips = Object.values(tipsByCategory).flat();
  const savedTipObjects = allTips.filter(tip => savedTips.includes(tip.id));

  return (
    <div className="min-h-screen pb-20 max-w-[360px] mx-auto" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1
            className="text-[24px] leading-[28px] mb-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Saved tips
          </h1>
          <p className="text-[15px] leading-[22px]" style={{ color: 'var(--app-text-secondary)' }}>
            Tips you want to remember while traveling
          </p>
        </motion.div>

        {savedTipObjects.length === 0 ? (
          <motion.div
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={reducedMotion ? false : { opacity: 1 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
            className="flex flex-col items-center justify-center py-16 px-6"
          >
            <div 
              className="w-20 h-20 rounded-full flex items-center justify-center mb-4"
              style={{ backgroundColor: 'var(--app-surface-accent)' }}
            >
              <Heart className="w-10 h-10" style={{ color: 'var(--app-text-secondary)' }} />
            </div>
            <p 
              className="text-[15px] text-center leading-[22px]"
              style={{ color: 'var(--app-text-secondary)' }}
            >
              Tap the heart on any tip to save it here
            </p>
          </motion.div>
        ) : (
          <motion.div 
            className="flex flex-col gap-4"
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={reducedMotion ? false : { opacity: 1 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          >
            {savedTipObjects.map((tip, index) => (
              <motion.div
                key={tip.id}
                initial={reducedMotion ? false : { opacity: 0, y: 20 }}
                animate={reducedMotion ? false : { opacity: 1, y: 0 }}
                transition={reducedMotion ? { duration: 0 } : { delay: index * 0.05 }}
              >
                <TipCard
                  id={tip.id}
                  category={tip.category}
                  title={tip.title}
                  text={tip.text}
                  supportingText={tip.supportingText}
                  highlightKeywords={tip.keywords}
                  isSaved={true}
                  onSave={handleSave}
                />
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}