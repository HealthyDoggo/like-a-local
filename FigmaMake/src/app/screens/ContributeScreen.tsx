import { useEffect } from 'react';
import { motion } from 'motion/react';
import { BottomNav } from '@/app/components/BottomNav';
import { Button } from '@/app/components/Button';
import { useNavigate } from 'react-router';
import { MapPin, MessageCircle, Plus, CheckCircle, Loader } from 'lucide-react';
import { LoadingSpinner } from '@/app/components/LoadingSpinner';
import { ErrorMessage } from '@/app/components/ErrorMessage';
import { useSettings } from '@/hooks/useSettings';
import { useMyTips } from '@/hooks/useTips';
import { useAuth } from '@/contexts/AuthContext';

export function ContributeScreen() {
  const navigate = useNavigate();
  const { reducedMotion, readingMode } = useSettings();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { tips: userTips, loading, error } = useMyTips();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/sign-in', { replace: true });
    }
  }, [isAuthenticated, authLoading, navigate]);

  if (authLoading || (!isAuthenticated && !authLoading)) {
    return null;
  }

  const uniqueCities = new Set(userTips.map(tip => tip.location_name).filter(Boolean));
  const processedCount = userTips.filter(t => t.status === 'processed').length;

  if (loading) {
    return (
      <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
        <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
          <h1 className={`${readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'} mb-6`} style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}>
            Your city insights
          </h1>
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
          <h1 className={`${readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'} mb-6`} style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}>
            Your city insights
          </h1>
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
          className="mb-6"
        >
          <div className="flex items-start justify-between">
            <div>
              <h1 className={`${readingMode ? 'text-[28px] leading-[34px]' : 'text-[24px] leading-[28px]'} mb-2`} style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}>
                Your city insights
              </h1>
              <p className={readingMode ? 'text-[18px] leading-[26px]' : 'text-[15px] leading-[22px]'} style={{ color: 'var(--app-text-secondary)' }}>
                Tips you've shared with visitors
              </p>
            </div>
            <motion.button
              onClick={() => navigate('/onboarding/country')}
              className="px-3 py-3 rounded-xl text-white"
              style={{ backgroundColor: 'var(--app-text-accent)' }}
              whileTap={{ scale: 0.95 }}
              whileHover={{ boxShadow: '0 4px 12px rgba(69, 123, 157, 0.3)' }}
              aria-label="Add a new tip"
            >
              <Plus className="w-5 h-5" />
            </motion.button>
          </div>
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
            <p className={`${readingMode ? 'text-[24px]' : 'text-[20px]'} font-semibold`} style={{ color: 'var(--app-text-primary)' }}>
              {userTips.length}
            </p>
            <p className={readingMode ? 'text-[13px]' : 'text-[11px]'} style={{ color: 'var(--app-text-secondary)' }}>Tips shared</p>
          </div>

          <div className="rounded-xl p-4 shadow-sm text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
            <div className="flex items-center justify-center mb-1">
              <MapPin className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <p className={`${readingMode ? 'text-[24px]' : 'text-[20px]'} font-semibold`} style={{ color: 'var(--app-text-primary)' }}>
              {uniqueCities.size}
            </p>
            <p className={readingMode ? 'text-[13px]' : 'text-[11px]'} style={{ color: 'var(--app-text-secondary)' }}>Cities covered</p>
          </div>

          <div className="rounded-xl p-4 shadow-sm text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
            <div className="flex items-center justify-center mb-1">
              <CheckCircle className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <p className={`${readingMode ? 'text-[24px]' : 'text-[20px]'} font-semibold`} style={{ color: 'var(--app-text-primary)' }}>
              {processedCount}
            </p>
            <p className={readingMode ? 'text-[13px]' : 'text-[11px]'} style={{ color: 'var(--app-text-secondary)' }}>Tips live</p>
          </div>
        </motion.div>

        {/* User Tips */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className={readingMode ? 'text-[22px] leading-[28px]' : 'text-[18px] leading-[24px]'} style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}>
              Your tips
            </h2>
            {userTips.length > 0 && userTips.length !== processedCount && (
              <span className={readingMode ? 'text-[14px]' : 'text-[12px]'} style={{ color: 'var(--app-text-secondary)' }}>
                {processedCount}/{userTips.length} live
              </span>
            )}
          </div>

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
                      className={`${readingMode ? 'text-[13px]' : 'text-[11px]'} px-2 py-1 rounded-full`}
                      style={{ backgroundColor: 'var(--app-surface-accent)', color: 'var(--app-text-accent)', fontWeight: 500 }}
                    >
                      {tip.location_name || 'General'}
                    </span>
                    <div className="flex items-center gap-1.5">
                      {tip.status === 'processed' ? (
                        <CheckCircle className="w-3.5 h-3.5" style={{ color: 'var(--app-success)' }} />
                      ) : (
                        <Loader className="w-3.5 h-3.5" style={{ color: 'var(--app-text-secondary)' }} />
                      )}
                      <span className={readingMode ? 'text-[13px]' : 'text-[11px]'} style={{ color: tip.status === 'processed' ? 'var(--app-success)' : 'var(--app-text-secondary)' }}>
                        {tip.status === 'processed' ? 'Live' : 'Pending'}
                      </span>
                    </div>
                  </div>

                  <p className={readingMode ? 'text-[18px] leading-[26px]' : 'text-[14px] leading-[20px]'} style={{ color: 'var(--app-text-primary)' }}>
                    {tip.tip_text.length > 120 ? tip.tip_text.substring(0, 120) + '...' : tip.tip_text}
                  </p>

                  <p className={`${readingMode ? 'text-[13px]' : 'text-[11px]'} mt-2`} style={{ color: 'var(--app-text-secondary)' }}>
                    {new Date(tip.submitted_at).toLocaleDateString()}
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
