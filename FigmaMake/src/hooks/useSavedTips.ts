import { useState, useEffect } from 'react';
import { savesService } from '@/services/api';
import { getDeviceId } from '@/utils/deviceId';

const SAVED_TIPS_KEY = 'savedTips';
const SAVED_TIPS_DATA_KEY = 'savedTipsData';

export interface SavedTip {
  id: string;
  category: string;
  text: string;
  supportingText?: string;
  city?: string;
  country?: string;
}

export function useSavedTips() {
  const [savedTips, setSavedTips] = useState<string[]>(() => {
    const saved = localStorage.getItem(SAVED_TIPS_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  const [savedTipsData, setSavedTipsData] = useState<Record<string, SavedTip>>(() => {
    const saved = localStorage.getItem(SAVED_TIPS_DATA_KEY);
    return saved ? JSON.parse(saved) : {};
  });

  useEffect(() => {
    localStorage.setItem(SAVED_TIPS_KEY, JSON.stringify(savedTips));
    localStorage.setItem(SAVED_TIPS_DATA_KEY, JSON.stringify(savedTipsData));
  }, [savedTips, savedTipsData]);

  const toggleSave = (tipId: string, tipData?: SavedTip) => {
    setSavedTips(prev => {
      if (prev.includes(tipId)) {
        // Unsaving - remove from both lists
        setSavedTipsData(prevData => {
          const newData = { ...prevData };
          delete newData[tipId];
          return newData;
        });
        return prev.filter(id => id !== tipId);
      } else {
        // Saving - add to both lists
        if (tipData) {
          setSavedTipsData(prevData => ({
            ...prevData,
            [tipId]: tipData
          }));
        }
        savesService.recordSave(parseInt(tipId), getDeviceId()).catch(() => {});
        return [...prev, tipId];
      }
    });
  };

  const isSaved = (tipId: string) => savedTips.includes(tipId);

  const getSavedTipsData = (): SavedTip[] => {
    return Object.values(savedTipsData);
  };

  const updateSavedTipTexts = (updates: Record<string, string>) => {
    setSavedTipsData(prev => {
      const next = { ...prev };
      for (const [id, text] of Object.entries(updates)) {
        if (next[id]) next[id] = { ...next[id], text };
      }
      return next;
    });
  };

  return { savedTips, toggleSave, isSaved, getSavedTipsData, updateSavedTipTexts };
}
