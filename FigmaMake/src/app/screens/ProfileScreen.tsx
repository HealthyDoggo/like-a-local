import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { Settings, User, Heart, MessageSquare, ChevronRight, Globe } from 'lucide-react';
import { BottomNav } from '@/app/components/BottomNav';
import { useSettings } from '@/hooks/useSettings';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/contexts/AuthContext';
import { tipsService } from '@/services/api';

export function ProfileScreen() {
  const navigate = useNavigate();
  const { isAuthenticated: isLoggedIn, user } = useAuth();
  const { reducedMotion, readingMode } = useSettings();
  const { language, availableLanguages } = useLanguage();
  const currentLanguage = availableLanguages.find(l => l.code === language);
  const [contributionCount, setContributionCount] = useState<number | null>(null);

  useEffect(() => {
    if (!isLoggedIn) return;
    tipsService.getMyTips().then(tips => setContributionCount(tips.length)).catch(() => setContributionCount(0));
  }, [isLoggedIn]);

  const MenuItem = ({ 
    icon: Icon, 
    title, 
    subtitle, 
    onClick 
  }: { 
    icon: any; 
    title: string; 
    subtitle?: string; 
    onClick: () => void;
  }) => (
    <motion.button
      onClick={onClick}
      className="flex items-center justify-between w-full py-4 border-b"
      style={{ borderColor: 'var(--app-border)' }}
      whileTap={reducedMotion ? {} : { scale: 0.99 }}
    >
      <div className="flex items-center gap-3">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: 'var(--app-surface-accent)' }}
        >
          <Icon className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
        </div>
        <div className="text-left">
          <p
            className={readingMode ? 'text-[18px] leading-[26px]' : 'text-[15px] leading-[20px]'}
            style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}
          >
            {title}
          </p>
          {subtitle && (
            <p className={readingMode ? 'text-[15px] leading-[22px]' : 'text-[13px] leading-[18px]'} style={{ color: 'var(--app-text-secondary)' }}>
              {subtitle}
            </p>
          )}
        </div>
      </div>
      <ChevronRight className="w-5 h-5" style={{ color: 'var(--app-text-secondary)' }} />
    </motion.button>
  );

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.h1
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className={readingMode ? 'text-[28px] leading-[34px] mb-8' : 'text-[24px] leading-[28px] mb-8'}
          style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
        >
          Profile
        </motion.h1>

        {!isLoggedIn ? (
          <motion.div
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={reducedMotion ? false : { opacity: 1 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
            className="mb-8"
          >
            <div className="rounded-xl shadow-sm p-6 text-center" style={{ backgroundColor: 'var(--app-surface)' }}>
              <div
                className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: 'var(--app-surface-accent)' }}
              >
                <User className="w-8 h-8" style={{ color: 'var(--app-text-accent)' }} />
              </div>
              <h2
                className="text-[18px] leading-[24px] mb-2"
                style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
              >
                Sign in to save your progress
              </h2>
              <p className="text-[14px] leading-[20px] mb-4" style={{ color: 'var(--app-text-secondary)' }}>
                Keep your saved tips and contributions across devices
              </p>
              <motion.button
                onClick={() => navigate('/sign-in')}
                className="w-full px-6 py-3 rounded-xl text-[15px] font-medium"
                style={{ backgroundColor: 'var(--app-text-accent)', color: 'var(--app-surface)' }}
                whileTap={reducedMotion ? {} : { scale: 0.98 }}
              >
                Sign in
              </motion.button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={reducedMotion ? false : { opacity: 1 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
            className="mb-8"
          >
            <div className="rounded-xl shadow-sm p-6" style={{ backgroundColor: 'var(--app-surface)' }}>
              <div className="flex items-center gap-4 mb-6">
                <div
                  className="w-16 h-16 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: 'var(--app-surface-accent)' }}
                >
                  <User className="w-8 h-8" style={{ color: 'var(--app-text-accent)' }} />
                </div>
                <div>
                  <h2
                    className={readingMode ? 'text-[22px] leading-[28px] mb-1' : 'text-[18px] leading-[24px] mb-1'}
                    style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
                  >
                    {user?.full_name || user?.email?.split('@')[0] || 'Traveler'}
                  </h2>
                  <p className={readingMode ? 'text-[16px]' : 'text-[14px]'} style={{ color: 'var(--app-text-secondary)' }}>
                    {user?.email}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 rounded-lg" style={{ backgroundColor: 'var(--app-surface-secondary)' }}>
                  <Heart className="w-5 h-5 mx-auto mb-1" style={{ color: 'var(--app-text-accent)' }} />
                  <p className={`${readingMode ? 'text-[24px]' : 'text-[20px]'} font-semibold`} style={{ color: 'var(--app-text-primary)' }}>
                    {JSON.parse(localStorage.getItem('savedTips') || '[]').length}
                  </p>
                  <p className={readingMode ? 'text-[14px]' : 'text-[12px]'} style={{ color: 'var(--app-text-secondary)' }}>Saved tips</p>
                </div>
                <div className="text-center p-3 rounded-lg" style={{ backgroundColor: 'var(--app-surface-secondary)' }}>
                  <MessageSquare className="w-5 h-5 mx-auto mb-1" style={{ color: 'var(--app-text-accent)' }} />
                  <p className={`${readingMode ? 'text-[24px]' : 'text-[20px]'} font-semibold`} style={{ color: 'var(--app-text-primary)' }}>
                    {contributionCount ?? '—'}
                  </p>
                  <p className={readingMode ? 'text-[14px]' : 'text-[12px]'} style={{ color: 'var(--app-text-secondary)' }}>Contributions</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          className="rounded-xl shadow-sm p-5"
          style={{ backgroundColor: 'var(--app-surface)' }}
        >
          <MenuItem
            icon={Globe}
            title="Language"
            subtitle={currentLanguage?.native_name || "English"}
            onClick={() => navigate('/settings/language')}
          />
          <MenuItem
            icon={Settings}
            title="Settings"
            subtitle="Accessibility, appearance, and more"
            onClick={() => navigate('/settings')}
          />
        </motion.div>
      </div>

      <BottomNav />
    </div>
  );
}