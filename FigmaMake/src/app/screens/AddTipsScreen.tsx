import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Plus, ChevronDown, ChevronUp, ArrowLeft } from 'lucide-react';
import { Button } from '@/app/components/Button';
import { useNavigate, useLocation } from 'react-router';
import { useCreateTip } from '@/hooks/useTips';
import { useSettings } from '@/hooks/useSettings';
import { ErrorMessage } from '@/app/components/ErrorMessage';

const prompts = [
  'Share a dining etiquette tip',
  'What is a local custom visitors should notice?',
  'Recommend a hidden gem',
  'Give advice for enjoying your city respectfully',
  'Share a small action that makes a big difference',
];

interface TipCard {
  id: number;
  title: string;
  body: string;
  supportingInfo: string;
  showSupportingInfo: boolean;
}

export function AddTipsScreen() {
  const [currentPromptIndex, setCurrentPromptIndex] = useState(0);
  const [tips, setTips] = useState<TipCard[]>([
    { id: 1, title: '', body: '', supportingInfo: '', showSupportingInfo: false }
  ]);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const navigate = useNavigate();
  const location = useLocation();
  const { country, city } = location.state || { country: null, city: null };
  const { createTip, loading, error: apiError } = useCreateTip();
  const { reducedMotion } = useSettings();
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Redirect if no location data
  useEffect(() => {
    if (!city || !country) {
      navigate('/onboarding/country', { replace: true });
    }
  }, [city, country, navigate]);

  useEffect(() => {
    if (!reducedMotion) {
      const interval = setInterval(() => {
        setCurrentPromptIndex((prev) => (prev + 1) % prompts.length);
      }, 4000);
      return () => clearInterval(interval);
    }
  }, [reducedMotion]);

  const addTip = () => {
    const newId = Math.max(...tips.map(t => t.id), 0) + 1;
    setTips([...tips, { id: newId, title: '', body: '', supportingInfo: '', showSupportingInfo: false }]);
  };

  const updateTip = (id: number, field: keyof TipCard, value: string | boolean) => {
    setTips(tips.map(tip => tip.id === id ? { ...tip, [field]: value } : tip));
  };

  const toggleSupportingInfo = (id: number) => {
    setTips(tips.map(tip => 
      tip.id === id ? { ...tip, showSupportingInfo: !tip.showSupportingInfo } : tip
    ));
  };

  const handleSubmit = async () => {
    setSubmitError(null);
    const tipsWithContent = tips.filter(tip => tip.body.trim());

    if (tipsWithContent.length === 0) {
      setSubmitError('Please add at least one tip before continuing.');
      return;
    }

    try {
      // Submit all tips with content
      for (const tip of tipsWithContent) {
        const tipText = tip.title
          ? `${tip.title}: ${tip.body}`
          : tip.body;

        const fullText = tip.supportingInfo
          ? `${tipText}\n\n${tip.supportingInfo}`
          : tipText;

        await createTip({
          tip_text: fullText,
          location_name: city,
          location_country: country,
          category_id: selectedCategory,
        });
      }

      navigate('/home');
    } catch (err) {
      setSubmitError(apiError || 'Failed to submit tips. Please try again.');
    }
  };

  if (!city || !country) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen px-5 pb-32" style={{ backgroundColor: 'var(--app-bg)', paddingTop: 'max(2rem, calc(env(safe-area-inset-top) + 1rem))' }}>
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
            className="text-[24px] leading-[28px]"
            style={{ color: 'var(--app-text-primary)', fontWeight: 600 }}
          >
            Help visitors fit in
          </h1>
          <p className="text-[13px]" style={{ color: 'var(--app-text-secondary)' }}>
            {city}, {country}
          </p>
        </div>
      </motion.div>

      <p className="text-[15px] leading-[22px] mb-6" style={{ color: 'var(--app-text-secondary)' }}>
        Share tips to help visitors enjoy your city respectfully
      </p>

      {!reducedMotion && (
        <AnimatePresence mode="wait">
          <motion.div
            key={currentPromptIndex}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.5 }}
            className="mb-4 text-[14px] font-medium"
            style={{ color: 'var(--app-text-accent)' }}
          >
            💡 {prompts[currentPromptIndex]}
          </motion.div>
        </AnimatePresence>
      )}

      {submitError && (
        <div className="mb-4">
          <ErrorMessage message={submitError} />
        </div>
      )}

      <motion.div
        className="flex flex-col gap-4 mb-6"
        initial={reducedMotion ? false : { opacity: 0 }}
        animate={reducedMotion ? false : { opacity: 1 }}
        transition={reducedMotion ? { duration: 0 } : { delay: 0.1 }}
      >
        {tips.map((tip, index) => (
          <motion.div
            key={tip.id}
            initial={reducedMotion ? false : { opacity: 0, x: -20, scale: 0.95 }}
            animate={reducedMotion ? false : { opacity: 1, x: 0, scale: 1 }}
            exit={reducedMotion ? false : { opacity: 0, x: 20, scale: 0.95 }}
            transition={reducedMotion ? { duration: 0 } : { delay: index * 0.05 }}
            className="rounded-xl p-4 border-2 transition-all duration-200"
            style={{ backgroundColor: 'var(--app-surface)', borderColor: 'var(--app-border)' }}
            onFocus={(e) => {
              if (e.currentTarget.contains(e.target)) {
                e.currentTarget.style.borderColor = 'var(--app-text-accent)';
              }
            }}
            onBlur={(e) => {
              if (!e.currentTarget.contains(e.relatedTarget as Node)) {
                e.currentTarget.style.borderColor = 'var(--app-border)';
              }
            }}
          >
            <input
              type="text"
              placeholder="Tip title (optional)"
              value={tip.title}
              onChange={(e) => updateTip(tip.id, 'title', e.target.value)}
              className="w-full mb-3 px-0 py-1 bg-transparent border-0 outline-none text-[15px] font-medium placeholder:font-normal"
              style={{ color: 'var(--app-text-primary)' }}
            />
            
            <textarea
              placeholder="Write your tip here"
              value={tip.body}
              onChange={(e) => updateTip(tip.id, 'body', e.target.value)}
              rows={3}
              className="w-full px-0 py-1 bg-transparent border-0 outline-none resize-none text-[15px]"
              style={{ color: 'var(--app-text-primary)' }}
            />

            <button
              onClick={() => toggleSupportingInfo(tip.id)}
              className="flex items-center gap-2 mt-2 text-[13px]"
              style={{ color: 'var(--app-text-accent)' }}
            >
              {tip.showSupportingInfo ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span>Add extra details</span>
            </button>

            <AnimatePresence>
              {tip.showSupportingInfo && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <textarea
                    placeholder="Add extra details if you like"
                    value={tip.supportingInfo}
                    onChange={(e) => updateTip(tip.id, 'supportingInfo', e.target.value)}
                    rows={2}
                    className="w-full mt-3 px-3 py-2 rounded-lg border-0 outline-none resize-none text-[13px]"
                    style={{ backgroundColor: 'var(--app-surface-accent)', color: 'var(--app-text-primary)' }}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </motion.div>

      <motion.button
        onClick={addTip}
        className="flex items-center gap-2 mb-8"
        style={{ color: 'var(--app-text-accent)' }}
        whileTap={reducedMotion ? {} : { scale: 0.95 }}
      >
        <Plus className="w-5 h-5" />
        <span className="text-[15px] font-medium">Add another tip</span>
      </motion.button>

      <div className="fixed bottom-0 left-0 right-0 px-5 py-6 border-t" style={{ backgroundColor: 'var(--app-surface)', borderColor: 'var(--app-border)' }}>
        <Button onClick={handleSubmit} className="w-full" disabled={loading}>
          {loading ? 'Submitting...' : 'Continue'}
        </Button>
      </div>
    </div>
  );
}
