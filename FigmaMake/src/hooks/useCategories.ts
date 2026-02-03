import { useState, useEffect } from 'react';
import { categoriesService, locationsService } from '@/services/api';
import { ApiError } from '@/services/api/client';
import { CategoryResponse } from '@/types/api.types';
import { getIconComponent, getColorVariant } from '@/utils/iconMapper';
import { LucideIcon } from 'lucide-react';

export interface Category {
  id: string;
  icon: LucideIcon;
  title: string;
  tipCount: number;
  color: 'teal' | 'yellow';
  displayOrder?: number;
}

export function useCategories(locationName?: string, locationCountry?: string) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch categories from backend
        const backendCategories = await categoriesService.getAll();

        // Fetch category counts if location is provided
        let categoryCounts: Record<string, number> = {};
        if (locationName && locationCountry) {
          try {
            const location = await locationsService.search({
              name: locationName,
              country: locationCountry,
            });

            if (location) {
              categoryCounts = await locationsService.getCategoryCounts(location.id);
            }
          } catch (err) {
            console.error('Error fetching category counts:', err);
            // Continue with empty counts
          }
        }

        if (!cancelled) {
          // Transform backend categories to frontend format
          const transformedCategories = backendCategories
            .map((cat: CategoryResponse) => ({
              id: cat.id,
              icon: getIconComponent(cat.icon_name),
              title: cat.title,
              tipCount: categoryCounts[cat.id] || 0,
              color: getColorVariant(cat.color),
              displayOrder: cat.display_order ?? 999,
            }))
            .sort((a, b) => (a.displayOrder ?? 999) - (b.displayOrder ?? 999));

          setCategories(transformedCategories);
        }
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ApiError) {
            console.error('API Error loading categories:', {
              status: err.status,
              statusText: err.statusText,
              data: err.data,
              message: err.message,
            });
            setError(`Failed to load categories: ${err.status} ${err.statusText}`);
          } else {
            console.error('Unexpected error loading categories:', err);
            setError(`An unexpected error occurred: ${err instanceof Error ? err.message : 'Unknown error'}`);
          }
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [locationName, locationCountry]);

  return { categories, loading, error };
}
