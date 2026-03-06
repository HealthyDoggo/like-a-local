import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Button } from '@/app/components/Button';
import { useNavigate } from 'react-router';
import { MapPin, Train, Coffee, MessageCircle, Globe, Users, Compass, Heart } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

const welcomeTranslations = [
  'Welcome',
  'Bienvenue',
  'Willkommen',
  'Bienvenido',
  'ようこそ',
  '欢迎',
  'مرحباً',
  'Benvenuto',
  'Bem-vindo',
  'Välkommen',
];

const floatingIcons = [
  { Icon: MapPin, x: -10, y: 15, delay: 0, duration: 25 },
  { Icon: Train, x: 85, y: 25, delay: 2, duration: 28 },
  { Icon: Coffee, x: 15, y: 60, delay: 4, duration: 30 },
  { Icon: MessageCircle, x: 75, y: 70, delay: 1, duration: 26 },
  { Icon: Globe, x: 5, y: 85, delay: 3, duration: 27 },
  { Icon: Users, x: 90, y: 50, delay: 5, duration: 29 },
  { Icon: Compass, x: 50, y: 10, delay: 2.5, duration: 24 },
  { Icon: Heart, x: 40, y: 90, delay: 4.5, duration: 31 },
];

export function SplashScreen() {
  const navigate = useNavigate();
  const [currentWelcomeIndex, setCurrentWelcomeIndex] = useState(0);
  const { reducedMotion } = useSettings();

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentWelcomeIndex((prev) => (prev + 1) % welcomeTranslations.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden" style={{ backgroundColor: 'var(--app-bg)' }}>
      {/* Animated Icon Background */}
      {!reducedMotion && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {floatingIcons.map(({ Icon, x, y, delay, duration }, index) => (
            <motion.div
              key={index}
              className="absolute"
              style={{
                left: `${x}%`,
                top: `${y}%`,
                opacity: 0.05,
                color: 'var(--teal)',
              }}
              initial={{ y: 0, x: 0, rotate: 0 }}
              animate={{
                y: [-20, -60],
                x: [0, Math.random() * 20 - 10],
                rotate: [0, 5, -5, 0],
              }}
              transition={{
                duration: duration,
                repeat: Infinity,
                delay: delay,
                ease: 'easeInOut',
              }}
            >
              <Icon className="w-32 h-32" strokeWidth={1} />
            </motion.div>
          ))}
        </div>
      )}

      {/* Multilingual Welcome Background Text with Gradient Mask */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
        <div 
          className="relative w-full max-w-[280px]"
          style={{
            maskImage: 'linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%)',
            WebkitMaskImage: 'linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%)',
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={currentWelcomeIndex}
              initial={{ opacity: 0, y: reducedMotion ? 0 : 15 }}
              animate={{ opacity: 0.18, y: 0 }}
              exit={{ opacity: 0, y: reducedMotion ? 0 : -15 }}
              transition={{ duration: reducedMotion ? 0.5 : 2, ease: 'easeInOut' }}
              className="text-[72px] font-light text-center select-none whitespace-nowrap"
              style={{
                color: 'var(--teal)',
                fontFamily: 'Inter, sans-serif',
                fontWeight: 200,
                letterSpacing: '-0.02em',
              }}
            >
              {welcomeTranslations[currentWelcomeIndex]}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Foreground Content */}
      <div className="relative z-10 flex flex-col items-center justify-between min-h-screen px-8 py-16">
        <div className="flex-1" />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-center"
        >
          <motion.h1
            className="text-[36px] leading-[40px] mb-4"
            style={{ color: 'var(--app-text-primary)', fontWeight: 700 }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            Like a Local
          </motion.h1>

          <motion.p
            className="text-[18px] leading-[26px] mb-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 500 }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            Understand everyday customs before you arrive
          </motion.p>

          <motion.p
            className="text-[15px] leading-[22px]"
            style={{ color: 'var(--app-text-secondary)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.6 }}
          >
            Tips shared by people who live there
          </motion.p>
        </motion.div>

        <div className="flex-1 flex flex-col items-center justify-end w-full gap-4">
          <motion.div
            className="w-full"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1, duration: 0.6 }}
          >
            <Button
              onClick={() => navigate('/sign-up')}
              className="w-full shadow-lg"
            >
              Get started
            </Button>
          </motion.div>
          
          <motion.button
            onClick={() => navigate('/sign-in')}
            className="text-[15px]"
            style={{ color: 'var(--app-text-accent)' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.3, duration: 0.6 }}
            whileTap={{ scale: 0.98 }}
          >
            I already have an account
          </motion.button>
        </div>
      </div>
    </div>
  );
}