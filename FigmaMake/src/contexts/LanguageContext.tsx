import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api/client';

interface Language {
  code: string;
  name: string;
  native_name: string;
}

interface LanguageContextType {
  language: string;
  setLanguage: (code: string) => void;
  availableLanguages: Language[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{children: React.ReactNode}> = ({children}) => {
  const [language, setLanguageState] = useState<string>(() => {
    // Load from localStorage or browser language
    const stored = localStorage.getItem('preferredLanguage');
    if (stored) return stored;

    // Try to use browser language
    const browserLang = navigator.language.split('-')[0];
    return browserLang || 'en';
  });

  const [availableLanguages, setAvailableLanguages] = useState<Language[]>([]);

  // Load available languages from API on mount
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const data = await apiClient.get<{ languages: Language[] }>('/api/languages');
        setAvailableLanguages(data.languages);
      } catch (error) {
        console.error('Failed to load languages:', error);
        // Fallback to default languages
        setAvailableLanguages([
          { code: 'en', name: 'English', native_name: 'English' },
        ]);
      }
    };
    loadLanguages();
  }, []);

  const setLanguage = (code: string) => {
    setLanguageState(code);
    localStorage.setItem('preferredLanguage', code);
  };

  return (
    <LanguageContext.Provider value={{language, setLanguage, availableLanguages}}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};
