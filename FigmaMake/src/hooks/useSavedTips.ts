import { useState, useEffect } from 'react';

const SAVED_TIPS_KEY = 'savedTips';

export function useSavedTips() {
  const [savedTips, setSavedTips] = useState<string[]>(() => {
    const saved = localStorage.getItem(SAVED_TIPS_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(SAVED_TIPS_KEY, JSON.stringify(savedTips));
  }, [savedTips]);

  const toggleSave = (tipId: string) => {
    setSavedTips(prev =>
      prev.includes(tipId)
        ? prev.filter(id => id !== tipId)
        : [...prev, tipId]
    );
  };

  const isSaved = (tipId: string) => savedTips.includes(tipId);

  return { savedTips, toggleSave, isSaved };
}
