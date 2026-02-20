import { useState, useEffect } from 'react';
import { tipsService, locationsService } from '@/services/api';
import { TipResponse, PromotedTipResponse, TipCreate } from '@/types/api.types';
import { ApiError } from '@/services/api/client';
import { useLanguage } from '@/contexts/LanguageContext';

export function usePromotedTips(
  locationName: string,
  locationCountry: string,
  categoryId?: string,
  limit = 20
) {
  const [tips, setTips] = useState<PromotedTipResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    if (!locationName || !locationCountry) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    const loadTips = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await locationsService.getPromotedTipsByName({
          location_name: locationName,
          location_country: locationCountry,
          category_id: categoryId,
          language,
          limit,
        });
        if (!cancelled) {
          setTips(data);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load tips: ${err.message}`);
          } else {
            setError('An unexpected error occurred');
          }
          console.error('Error loading promoted tips:', err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadTips();

    return () => {
      cancelled = true;
    };
  }, [locationName, locationCountry, categoryId, language, limit]);

  return { tips, loading, error };
}

export function useMyTips() {
  const [tips, setTips] = useState<TipResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { language } = useLanguage();

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await tipsService.getMyTips(language);
        if (!cancelled) setTips(data);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof ApiError ? err.message : 'Failed to load your tips');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [language]);

  return { tips, loading, error };
}

export function useCreateTip() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const createTip = async (tip: TipCreate): Promise<TipResponse | null> => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);
      const result = await tipsService.create(tip);
      setSuccess(true);
      return result;
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Failed to create tip: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
      console.error('Error creating tip:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { createTip, loading, error, success };
}
