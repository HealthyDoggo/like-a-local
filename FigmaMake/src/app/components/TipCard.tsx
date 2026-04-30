import { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Heart, Volume2, Languages } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';
import { useAuth } from '@/contexts/AuthContext';

interface TipCardProps {
  id?: string;
  category?: string;
  title?: string;
  text: string;
  supportingText?: string;
  highlightKeywords?: string[];
  nativeText?: string;
  isSaved?: boolean;
  onSave?: (id: string) => void;
  onAuthRequired?: () => void;
  showCategory?: boolean;
}

export function TipCard({ 
  id = '1',
  category = 'General',
  title,
  text,
  supportingText,
  highlightKeywords = [],
  nativeText,
  isSaved = false,
  onSave,
  onAuthRequired,
  showCategory = true
}: TipCardProps) {
  const { isAuthenticated } = useAuth();
  const [isExpanded, setIsExpanded] = useState(false);
  const [saved, setSaved] = useState(isSaved);
  const [isReading, setIsReading] = useState(false);
  const [showNative, setShowNative] = useState(false);
  const settings = useSettings();
  const { readingMode, readAloud: readAloudEnabled, reducedMotion } = settings;

  const highlightText = (text: string) => {
    if (highlightKeywords.length === 0) return text;
    
    let result = text;
    highlightKeywords.forEach((keyword) => {
      const regex = new RegExp(`(${keyword})`, 'gi');
      result = result.replace(regex, '<span style="color: var(--app-text-accent); font-weight: 500;">$1</span>');
    });
    
    return result;
  };

  const handleSave = () => {
    if (!isAuthenticated && !saved) {
      // Show auth modal if trying to save while not logged in
      if (onAuthRequired) {
        onAuthRequired();
      }
      return;
    }
    
    setSaved(!saved);
    if (onSave) {
      onSave(id);
    }
  };

  const handleReadAloud = () => {
    if ('speechSynthesis' in window) {
      if (isReading) {
        window.speechSynthesis.cancel();
        setIsReading(false);
      } else {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onend = () => setIsReading(false);
        window.speechSynthesis.speak(utterance);
        setIsReading(true);
      }
    }
  };

  const displayText = showNative && nativeText ? nativeText : text;
  const truncatedText = displayText.length > 120 && !isExpanded ? displayText.substring(0, 120) + '...' : displayText;
  const textSize = readingMode ? 'text-[20px] leading-[30px]' : 'text-[15px] leading-[22px]';
  const spacing = readingMode ? 'p-5' : 'p-4';

  return (
    <motion.div
      className={`rounded-xl shadow-sm ${spacing}`}
      style={{ backgroundColor: 'var(--app-surface)' }}
      initial={reducedMotion ? false : { opacity: 0, y: 10 }}
      animate={reducedMotion ? false : { opacity: 1, y: 0 }}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          {showCategory && (
            <span
              className={`${readingMode ? 'text-[13px]' : 'text-[11px]'} px-2 py-1 rounded-full`}
              style={{ backgroundColor: 'var(--app-surface-accent)', color: 'var(--app-text-accent)', fontWeight: 500 }}
            >
              {category}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 -mt-1 -mr-1">
          {nativeText && (
            <motion.button
              onClick={() => setShowNative(!showNative)}
              className="p-1"
              whileTap={reducedMotion ? {} : { scale: 0.9 }}
            >
              <Languages
                className="w-5 h-5"
                style={{
                  color: showNative ? 'var(--app-text-accent)' : 'var(--app-text-secondary)',
                }}
              />
            </motion.button>
          )}
          {readAloudEnabled && (
            <motion.button
              onClick={handleReadAloud}
              className="p-1"
              whileTap={reducedMotion ? {} : { scale: 0.9 }}
            >
              <Volume2
                className="w-5 h-5"
                style={{
                  color: isReading ? 'var(--app-text-accent)' : 'var(--app-text-secondary)',
                  fill: isReading ? 'var(--app-text-accent)' : 'none',
                }}
              />
            </motion.button>
          )}
          <motion.button
            onClick={handleSave}
            className="p-1"
            whileTap={reducedMotion ? {} : { scale: 0.9 }}
          >
            <Heart
              className="w-5 h-5"
              style={{ 
                color: saved ? 'var(--app-heart)' : 'var(--app-text-secondary)',
                fill: saved ? 'var(--app-heart)' : 'none',
                strokeWidth: 2
              }}
            />
          </motion.button>
        </div>
      </div>

      {title && (
        <h3 className={`${readingMode ? 'text-[21px]' : 'text-[15px]'} font-semibold mb-2`} style={{ color: 'var(--app-text-primary)' }}>
          {title}
        </h3>
      )}

      <p 
        className={textSize}
        style={{ color: 'var(--app-text-primary)' }}
        dangerouslySetInnerHTML={{ __html: highlightText(truncatedText) }}
      />

      {supportingText && (
        <p className={`${readingMode ? 'text-[17px] leading-[26px]' : 'text-[13px] leading-[18px]'} mt-2`} style={{ color: 'var(--app-text-secondary)' }}>
          {supportingText}
        </p>
      )}

      {displayText.length > 120 && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`${readingMode ? 'text-[16px]' : 'text-[13px]'} mt-2`}
          style={{ color: 'var(--app-text-accent)', fontWeight: 500 }}
        >
          {isExpanded ? 'Show less' : 'Read more'}
        </button>
      )}
    </motion.div>
  );
}