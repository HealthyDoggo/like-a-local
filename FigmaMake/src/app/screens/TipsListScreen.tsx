import { useState } from 'react';
import { motion } from 'motion/react';
import { useLocation } from 'react-router';
import { TipCard } from '@/app/components/TipCard';
import { SignUpModal } from '@/app/components/SignUpModal';
import { BottomNav } from '@/app/components/BottomNav';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router';
import { usePromotedTips } from '@/hooks/useTips';
import { useSavedTips } from '@/hooks/useSavedTips';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';

export function TipsListScreen() {
  const location = useLocation();
  const navigate = useNavigate();
  const { city = 'Tokyo', country = 'Japan', categoryId, category = 'All Tips' } = location.state || {};

  const { tips: apiTips, loading, error } = usePromotedTips(city, country, categoryId, 100);
  const { toggleSave, isSaved } = useSavedTips();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const { reducedMotion, readingMode } = useSettings();

  // Map API response to UI format
  const tips = apiTips.map(tip => ({
    id: String(tip.id),
    category: category,
    text: tip.tip_text,
    nativeText: tip.original_text,
    supportingText: `${tip.mention_count} locals mentioned this`,
    city: city,
    country: country,
  }));

  const handleSave = (tipId: string) => {
    const tip = tips.find(t => t.id === tipId);
    if (tip) {
      toggleSave(tipId, tip);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: -10 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            className="flex items-center gap-3 mb-6"
          >
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2"
              style={{ color: 'var(--app-text-accent)' }}
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1
                className={readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'}
                style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
              >
                {category}
              </h1>
              <p className={readingMode ? 'text-[16px]' : 'text-[13px]'} style={{ color: 'var(--app-text-secondary)' }}>
                {city}
              </p>
            </div>
          </motion.div>
          <LoadingSpinner />
        </div>
        <BottomNav />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: -10 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            className="flex items-center gap-3 mb-6"
          >
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2"
              style={{ color: 'var(--app-text-accent)' }}
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1
                className={readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'}
                style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
              >
                {category}
              </h1>
              <p className={readingMode ? 'text-[16px]' : 'text-[13px]'} style={{ color: 'var(--app-text-secondary)' }}>
                {city}
              </p>
            </div>
          </motion.div>
          <ErrorMessage message={error} />
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-6"
        >
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2"
            style={{ color: 'var(--app-text-accent)' }}
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1
              className={readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'}
              style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
            >
              {category}
            </h1>
            <p className={readingMode ? 'text-[16px]' : 'text-[13px]'} style={{ color: 'var(--app-text-secondary)' }}>
              {city}
            </p>
          </div>
        </motion.div>

        <div className="flex flex-col gap-4">
          {tips.length === 0 ? (
            <p className="text-center text-[14px] py-8" style={{ color: 'var(--app-text-secondary)' }}>
              No tips found for this category yet.
            </p>
          ) : (
            tips.map((tip) => (
              <div key={tip.id}>
                <TipCard
                  id={tip.id}
                  category={tip.category}
                  text={tip.text}
                  nativeText={tip.nativeText}
                  supportingText={tip.supportingText}
                  isSaved={isSaved(tip.id)}
                  onSave={handleSave}
                  onAuthRequired={() => setShowAuthModal(true)}
                />
              </div>
            ))
          )}
        </div>
      </div>

      <BottomNav />
      <SignUpModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </div>
  );
}