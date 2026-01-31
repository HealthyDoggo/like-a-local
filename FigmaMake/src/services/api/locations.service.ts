import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import {
  LocationResponse,
  PromotedTipResponse,
  PromotedTipsParams,
} from '@/types/api.types';

export const locationsService = {
  async getAll(): Promise<LocationResponse[]> {
    return apiClient.get<LocationResponse[]>(ENDPOINTS.LOCATIONS);
  },

  async search(name: string, country: string): Promise<LocationResponse | null> {
    return apiClient.get<LocationResponse | null>(ENDPOINTS.LOCATION_SEARCH, {
      name,
      country,
    });
  },

  async getPromotedTipsByName(params: PromotedTipsParams): Promise<PromotedTipResponse[]> {
    return apiClient.get<PromotedTipResponse[]>(ENDPOINTS.PROMOTED_TIPS, params);
  },
};
