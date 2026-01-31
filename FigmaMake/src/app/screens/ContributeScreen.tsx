import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { BottomNav } from '@/app/components/BottomNav';
import { Button } from '@/app/components/Button';
import { useNavigate } from 'react-router';
import { MapPin, MessageCircle, Heart, Plus } from 'lucide-react';
import { tipsService } from '@/services/api';
import { TipResponse } from '@/types/api.types';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';
import { ApiError } from '@/services/api/client';

export function ContributeScreen() {
  const navigate = useNavigate();
  const [userTips, setUserTips] = useState<TipResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { reducedMotion } = useSettings();

  useEffect(() => {
    const loadTips = async () => {
      try {
        setLoading(true);
        setError(null);
        const tips = await tipsService.getAll({ status: 'processed', limit: 50 });
        setUserTips(tips);
      } catch (err) {
        console.error('Error loading tips:', err);
        if (err instanceof ApiError) {
          if (err.status === 404) {
            setError('No tips found. Start by adding your first tip!');
          } else if (err.status >= 500) {
            setError('Server error. Please try again later.');
          } else {
            setError('Failed to load tips. Please try again.');
          }
        } else {
          setError('Network error. Please check your connection.');
        }
      } finally {
        setLoading(false);
      }
    };
    loadTips();
  }, []);

  const retryLoad = () => {
    setError(null);
    setLoading(true);
    const loadTips = async () => {
      try {
        const tips = await tipsService.getAll({ status: 'processed', limit: 50 });
        setUserTips(tips);
      } catch (err) {
        console.error('Error loading tips:', err);
        setError('Failed to load tips. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    loadTips();
  };

  if (loading) {
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
              Your city insights
            </h1>
          </motion.div>
          <LoadingSpinner />
        </div>
        <BottomNav />
      </div>
    );
  }

  if (error) {
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
              Your city insights
            </h1>
          </motion.div>
          <ErrorMessage message={error} onRetry={retryLoad} />
        </div>
        <BottomNav />
      </div>
    );
  }

  // Get unique cities count
  const uniqueCities = new Set(userTips.map(tip => tip.location_name).filter(Boolean));

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
            Your city insights
          </h1>
          <p className="text-[15px] leading-[22px]" style={{ color: 'var(--app-text-secondary)' }}>
            Tips you've shared with visitors
          </p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, scale: 0.95 }}
          animate={reducedMotion ? false : { opacity: 1, scale: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          className="grid grid-cols-3 gap-3 mb-6"
        >
          <div className="rounded-xl p-4 shadow-sm text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
            <div className="flex items-center justify-center mb-1">
              <MessageCircle className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <p className="text-[20px] font-semibold" style={{ color: 'var(--app-text-primary)' }}>
              {userTips.length}
            </p>
            <p className="text-[11px]" style={{ color: 'var(--app-text-secondary)' }}>
              Tips shared
            </p>
          </div>

          <div className="rounded-xl p-4 shadow-sm text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
            <div className="flex items-center justify-center mb-1">
              <MapPin className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <p className="text-[20px] font-semibold" style={{ color: 'var(--app-text-primary)' }}>
              {uniqueCities.size}
            </p>
            <p className="text-[11px]" style={{ color: 'var(--app-text-secondary)' }}>
              Cities covered
            </p>
          </div>

          <div className="rounded-xl p-4 shadow-sm text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
            <div className="flex items-center justify-center mb-1">
              <Heart className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <p className="text-[20px] font-semibold" style={{ color: 'var(--app-text-primary)' }}>
              42
            </p>
            <p className="text-[11px]" style={{ color: 'var(--app-text-secondary)' }}>
              Saved by visitors
            </p>
          </div>
        </motion.div>

        {/* User Tips */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          className="mb-6"
        >
          <h2 className="text-[18px] leading-[24px] mb-4" style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}>
            Your tips
          </h2>
          
          <div className="flex flex-col gap-3">
            {userTips.length === 0 ? (
              <p className="text-center text-[14px]" style={{ color: 'var(--app-text-secondary)' }}>
                You haven't shared any tips yet
              </p>
            ) : (
              userTips.map((tip, index) => (
                <motion.div
                  key={tip.id}
                  initial={reducedMotion ? false : { opacity: 0, x: -20 }}
                  animate={reducedMotion ? false : { opacity: 1, x: 0 }}
                  transition={reducedMotion ? { duration: 0 } : { delay: 0.3 + index * 0.05 }}
                  className="rounded-xl p-4 shadow-sm"
                  style={{ backgroundColor: 'var(--app-surface)' }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span
                      className="text-[11px] px-2 py-1 rounded-full"
                      style={{ backgroundColor: 'var(--app-surface-accent)', color: 'var(--app-text-accent)', fontWeight: 500 }}
                    >
                      {tip.location_name || 'General'}
                    </span>
                    <span className="text-[11px]" style={{ color: 'var(--app-text-secondary)' }}>
                      {new Date(tip.submitted_at).toLocaleDateString()}
                    </span>
                  </div>

                  <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-primary)' }}>
                    {tip.tip_text.length > 120
                      ? tip.tip_text.substring(0, 120) + '...'
                      : tip.tip_text}
                  </p>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Add New Tip Button */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.4 }}
        >
          <Button 
            onClick={() => navigate('/onboarding/country')} 
            className="w-full flex items-center justify-center gap-2"
          >
            <Plus className="w-5 h-5" />
            <span>Add a new tip</span>
          </Button>
        </motion.div>
      </div>

      <BottomNav />
    </div>
  );
}
