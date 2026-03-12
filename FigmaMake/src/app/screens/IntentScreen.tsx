import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, MapPin, Heart } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

export function IntentScreen() {
  const navigate = useNavigate();
  const { reducedMotion } = useSettings();

  const handleChoice = (intent: 'visit' | 'contribute') => {
    if (intent === 'visit') {
      navigate('/visit');
    } else {
      navigate('/onboarding/contribute-country');
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-8 flex flex-col h-screen" style={{ paddingTop: 'max(4rem, calc(env(safe-area-inset-top) + 2rem))' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: 20 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          className="mb-12"
        >
          <div className="flex items-center mb-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2"
              style={{ color: 'var(--app-text-accent)' }}
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <h1
              className="text-[28px] leading-[34px] ml-2"
              style={{ color: 'var(--app-text-primary)', fontWeight: 700 }}
            >
              What would you like to do today?
            </h1>
          </div>
          <p className="text-[15px] leading-[22px]" style={{ color: 'var(--app-text-secondary)' }}>
            You can always do both later
          </p>
        </motion.div>

        <div className="flex-1 flex flex-col gap-4">
          {/* Visit Card */}
          <motion.button
            onClick={() => handleChoice('visit')}
            initial={reducedMotion ? false : { opacity: 0, y: 20 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
            className="flex flex-col items-start p-6 rounded-2xl text-left shadow-sm border-2"
            style={{ backgroundColor: 'var(--app-surface)', borderColor: 'transparent' }}
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
              style={{ backgroundColor: 'var(--app-text-accent)' }}
            >
              <MapPin className="w-6 h-6" style={{ color: 'var(--app-surface)' }} />
            </div>
            <h2
              className="text-[18px] leading-[24px] mb-2"
              style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
            >
              I'm visiting somewhere new
            </h2>
            <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
              Find local tips for your trip
            </p>
          </motion.button>

          {/* Contribute Card */}
          <motion.button
            onClick={() => handleChoice('contribute')}
            initial={reducedMotion ? false : { opacity: 0, y: 20 }}
            animate={reducedMotion ? false : { opacity: 1, y: 0 }}
            transition={reducedMotion ? { duration: 0 } : { delay: 0.3 }}
            whileTap={reducedMotion ? {} : { scale: 0.98 }}
            className="flex flex-col items-start p-6 rounded-2xl text-left shadow-sm border-2"
            style={{ backgroundColor: 'var(--app-surface)', borderColor: 'transparent' }}
          >
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
              style={{ backgroundColor: 'var(--app-text-accent)' }}
            >
              <Heart className="w-6 h-6" style={{ color: 'var(--app-surface)' }} />
            </div>
            <h2
              className="text-[18px] leading-[24px] mb-2"
              style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
            >
              I want to share local tips
            </h2>
            <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
              Help visitors feel welcome
            </p>
          </motion.button>
        </div>

        {/* Skip Option */}
        <motion.button
          onClick={() => navigate('/home')}
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.5 }}
          className="text-[15px] py-4"
          style={{ color: 'var(--app-text-accent)' }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          I'll decide later
        </motion.button>
      </div>
    </div>
  );
}
