import { useState, useEffect } from 'react';

export interface AppSettings {
  darkMode: boolean;
  readingMode: boolean;
  readAloud: boolean;
  reducedMotion: boolean;
}

// Custom event for settings changes
const SETTINGS_CHANGE_EVENT = 'settingsChange';

export function useSettings() {
  const [settings, setSettings] = useState<AppSettings>(() => ({
    darkMode: localStorage.getItem('darkMode') === 'true',
    readingMode: localStorage.getItem('readingMode') === 'true',
    readAloud: localStorage.getItem('readAloud') === 'true',
    reducedMotion: localStorage.getItem('reducedMotion') === 'true',
  }));

  useEffect(() => {
    const handleSettingsChange = () => {
      setSettings({
        darkMode: localStorage.getItem('darkMode') === 'true',
        readingMode: localStorage.getItem('readingMode') === 'true',
        readAloud: localStorage.getItem('readAloud') === 'true',
        reducedMotion: localStorage.getItem('reducedMotion') === 'true',
      });
    };

    // Listen for settings changes from other components
    window.addEventListener(SETTINGS_CHANGE_EVENT, handleSettingsChange);
    window.addEventListener('storage', handleSettingsChange);

    return () => {
      window.removeEventListener(SETTINGS_CHANGE_EVENT, handleSettingsChange);
      window.removeEventListener('storage', handleSettingsChange);
    };
  }, []);

  return settings;
}

// Helper to notify all components when settings change
export function notifySettingsChange() {
  window.dispatchEvent(new Event(SETTINGS_CHANGE_EVENT));
}
