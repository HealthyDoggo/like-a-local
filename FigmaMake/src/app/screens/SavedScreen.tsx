import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { BottomNav } from '@/app/components/BottomNav';
import { TipCard } from '@/app/components/TipCard';
import { Heart } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';
import { useSavedTips, SavedTip } from '@/hooks/useSavedTips';
import { useLanguage } from '@/contexts/LanguageContext';
import { locationsService } from '@/services/api';

export function SavedScreen() {
  const { getSavedTipsData, toggleSave, isSaved, updateSavedTipTexts } = useSavedTips();
  const [savedTipObjects, setSavedTipObjects] = useState<SavedTip[]>(getSavedTipsData());
  const { reducedMotion } = useSettings();
  const { language } = useLanguage();

  // On mount or language change: translate and persist back to localStorage
  useEffect(() => {
    setSavedTipObjects(getSavedTipsData());
    const current = getSavedTipsData();
    if (current.length === 0 || !navigator.onLine) return;

    let cancelled = false;
    Promise.all(
      current.map(async (tip) => {
        try {
          const fresh = await locationsService.getPromotedTip(parseInt(tip.id), language);
          return [tip.id, fresh.tip_text] as const;
        } catch {
          return null;
        }
      })
    ).then((results) => {
      if (cancelled) return;
      const updates = Object.fromEntries(results.filter(Boolean) as [string, string][]);
      updateSavedTipTexts(updates);
      // Build display objects directly — don't re-read storage (state update is async)
      setSavedTipObjects(current.map(tip =>
        updates[tip.id] ? { ...tip, text: updates[tip.id] } : tip
      ));
    });

    return () => { cancelled = true; };
  }, [language]);

  // Sync from storage when saves change in another tab
  useEffect(() => {
    const handleStorage = () => setSavedTipObjects(getSavedTipsData());
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const handleUnsave = (tipId: string) => {
    toggleSave(tipId);
    setSavedTipObjects(getSavedTipsData());
  };

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
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
                  text={tip.text}
                  supportingText={tip.supportingText}
                  isSaved={isSaved(tip.id)}
                  onSave={handleUnsave}
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