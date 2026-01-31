import { useState, useEffect, useRef } from 'react';
import { locationsService } from '@/services/api';
import { CountriesCitiesResponse } from '@/types/api.types';
import { ApiError } from '@/services/api/client';

export function useCountriesAndCities() {
  const [data, setData] = useState<CountriesCitiesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (!hasFetched.current) {
      hasFetched.current = true;
      loadData();
    }
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await locationsService.getCountriesAndCities();
      setData(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Failed to load countries and cities: ${err.message}`);
      } else {
        setError('An unexpected error occurred');
      }
      console.error('Error loading countries and cities:', err);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, reload: loadData };
}
