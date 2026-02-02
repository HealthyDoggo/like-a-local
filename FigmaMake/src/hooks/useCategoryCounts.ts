import { useState, useEffect } from 'react';
import { locationsService } from '@/services/api';
import { ApiError } from '@/services/api/client';

export function useCategoryCounts(locationName: string, locationCountry: string) {
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!locationName || !locationCountry) {
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchCounts = async () => {
      try {
        setLoading(true);
        setError(null);

        // First, search for the location
        const location = await locationsService.search({
          name: locationName,
          country: locationCountry,
        });

        if (!cancelled) {
          if (location) {
            // Get category counts for this location
            const counts = await locationsService.getCategoryCounts(location.id);
            setCategoryCounts(counts);
          } else {
            // Location not found - set empty counts
            setCategoryCounts({});
          }
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            setError(`Failed to load category counts: ${err.message}`);
          } else {
            setError('An unexpected error occurred');
          }
          console.error('Error loading category counts:', err);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchCounts();

    return () => {
      cancelled = true;
    };
  }, [locationName, locationCountry]);

  return { categoryCounts, loading, error };
}
