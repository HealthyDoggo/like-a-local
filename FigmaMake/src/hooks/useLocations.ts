import { useState, useEffect, useRef } from 'react';
import { locationsService } from '@/services/api';
import { LocationResponse } from '@/types/api.types';
import { ApiError } from '@/services/api/client';

export function useLocations() {
  const [locations, setLocations] = useState<LocationResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      loadLocations();
    }
  }, []);

  const loadLocations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await locationsService.getAll();
      setLocations(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Failed to load locations: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
      console.error('Error loading locations:', err);
    } finally {
      setLoading(false);
    }
  };

  return { locations, loading, error, reload: loadLocations };
}
