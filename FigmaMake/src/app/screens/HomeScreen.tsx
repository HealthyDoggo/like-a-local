import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { BottomNav } from '@/app/components/BottomNav';
import { MapPin, PenLine } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

export function HomeScreen() {
  const navigate = useNavigate();
  const { reducedMotion } = useSettings();

  return (
    <div className="min-h-screen pb-20" style={{ backgroundColor: 'var(--app-bg)' }}>
      <div className="px-5" style={{ paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))', paddingBottom: '2rem' }}>
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1
            className="text-[28px] leading-[34px] mb-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Explore cities with local insight
          </h1>
          <p className="text-[15px] leading-[22px]" style={{ color: 'var(--app-text-secondary)' }}>
            Cultural tips shared by people who live there
          </p>
        </motion.div>

        {/* Primary Action Card */}
        <motion.button
          onClick={() => navigate('/visit')}
          className="w-full rounded-2xl p-6 shadow-md mb-4"
          style={{ backgroundColor: 'var(--app-surface)' }}
          initial={reducedMotion ? false : { opacity: 0, scale: 0.95 }}
          animate={reducedMotion ? false : { opacity: 1, scale: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          whileHover={reducedMotion ? {} : { boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)' }}
        >
          <div className="flex items-start gap-4">
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: 'var(--app-teal-alpha)' }}
            >
              <MapPin className="w-6 h-6" style={{ color: 'var(--app-text-accent)' }} />
            </div>
            <div className="flex-1 text-left">
              <h2 
                className="text-[18px] leading-[24px] font-semibold mb-1"
                style={{ color: 'var(--app-text-primary)' }}
              >
                Find tips for your trip
              </h2>
              <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
                Learn everyday customs, habits, and expectations
              </p>
            </div>
          </div>
          <div className="mt-4">
            <span 
              className="inline-block px-4 py-2 rounded-lg text-[15px] font-medium"
              style={{ backgroundColor: 'var(--app-text-accent)', color: 'var(--app-surface)' }}
            >
              Choose a city
            </span>
          </div>
        </motion.button>

        {/* Secondary Action Card */}
        <motion.button
          onClick={() => navigate('/contribute')}
          className="w-full rounded-2xl p-6 shadow-md"
          style={{ backgroundColor: 'var(--app-surface)' }}
          initial={reducedMotion ? false : { opacity: 0, scale: 0.95 }}
          animate={reducedMotion ? false : { opacity: 1, scale: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          whileHover={reducedMotion ? {} : { boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)' }}
        >
          <div className="flex items-start gap-4">
            <div 
              className="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: 'var(--app-yellow-alpha)' }}
            >
              <PenLine className="w-6 h-6" style={{ color: 'var(--golden-yellow)' }} />
            </div>
            <div className="flex-1 text-left">
              <h2 
                className="text-[18px] leading-[24px] font-semibold mb-1"
                style={{ color: 'var(--app-text-primary)' }}
              >
                Share local knowledge
              </h2>
              <p className="text-[14px] leading-[20px]" style={{ color: 'var(--app-text-secondary)' }}>
                Help visitors feel welcome in your city
              </p>
            </div>
          </div>
          <div className="mt-4">
            <span 
              className="inline-block px-4 py-2 rounded-lg text-[15px] font-medium border-2"
              style={{ borderColor: 'var(--app-text-accent)', color: 'var(--app-text-accent)' }}
            >
              Add local tips
            </span>
          </div>
        </motion.button>
      </div>

      <BottomNav />
    </div>
  );
}
