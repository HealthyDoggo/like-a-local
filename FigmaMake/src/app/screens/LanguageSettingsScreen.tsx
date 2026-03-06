import { motion } from 'motion/react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Check } from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { useSettings } from '@/hooks/useSettings';
import { useState } from 'react';

export function LanguageSettingsScreen() {
  const navigate = useNavigate();
  const { language, setLanguage, availableLanguages } = useLanguage();
  const { reducedMotion } = useSettings();
  const [showSuccess, setShowSuccess] = useState(false);

  const handleLanguageSelect = (code: string) => {
    setLanguage(code);
    setShowSuccess(true);
    setTimeout(() => {
      setShowSuccess(false);
      setTimeout(() => navigate(-1), 200);
    }, 800);
  };

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--app-bg)' }}
    >
      <div
        className="px-5"
        style={{
          paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))',
          paddingBottom: '2rem'
        }}
      >
        {/* Header */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0, y: -10 }}
          animate={reducedMotion ? false : { opacity: 1, y: 0 }}
          className="flex items-center mb-8"
        >
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2"
            style={{ color: 'var(--app-text-accent)' }}
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <h1
            className="text-[24px] leading-[28px] ml-2"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Language
          </h1>
        </motion.div>

        {/* Description */}
        <motion.p
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
          className="text-[14px] leading-[20px] mb-6"
          style={{ color: 'var(--app-text-secondary)' }}
        >
          Select your preferred language. Travel tips will be displayed in this language when available.
        </motion.p>

        {/* Success message */}
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-4 p-4 rounded-xl flex items-center gap-3"
            style={{ backgroundColor: 'var(--app-success)', color: '#fff' }}
          >
            <Check className="w-5 h-5" />
            <span className="text-[14px] font-medium">Language updated successfully</span>
          </motion.div>
        )}

        {/* Language options */}
        <motion.div
          initial={reducedMotion ? false : { opacity: 0 }}
          animate={reducedMotion ? false : { opacity: 1 }}
          transition={reducedMotion ? { duration: 0 } : { delay: 0.2 }}
          className="space-y-2"
        >
          {availableLanguages.map((lang, index) => (
            <motion.button
              key={lang.code}
              onClick={() => handleLanguageSelect(lang.code)}
              initial={reducedMotion ? false : { opacity: 0, x: -20 }}
              animate={reducedMotion ? false : { opacity: 1, x: 0 }}
              transition={reducedMotion ? { duration: 0 } : { delay: 0.3 + index * 0.05 }}
              className={`w-full p-4 rounded-xl text-left transition-all ${
                language === lang.code ? 'ring-2' : ''
              }`}
              style={{
                backgroundColor: language === lang.code
                  ? 'var(--app-surface-accent)'
                  : 'var(--app-surface)',
                borderColor: language === lang.code
                  ? 'var(--app-text-accent)'
                  : 'transparent',
                ringColor: language === lang.code
                  ? 'var(--app-text-accent)'
                  : 'transparent'
              }}
              whileTap={reducedMotion ? {} : { scale: 0.98 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p
                    className="text-[16px] leading-[20px] font-medium"
                    style={{ color: 'var(--app-text-primary)' }}
                  >
                    {lang.native_name}
                  </p>
                  <p
                    className="text-[13px] leading-[18px] mt-1"
                    style={{ color: 'var(--app-text-secondary)' }}
                  >
                    {lang.name}
                  </p>
                </div>
                {language === lang.code && (
                  <Check className="w-5 h-5" style={{ color: 'var(--app-text-accent)' }} />
                )}
              </div>
            </motion.button>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
