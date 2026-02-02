import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import {
  LocationResponse,
  PromotedTipResponse,
  PromotedTipsParams,
  CountriesCitiesResponse,
} from '@/types/api.types';

export const locationsService = {
  async getAll(): Promise<LocationResponse[]> {
    return apiClient.get<LocationResponse[]>(ENDPOINTS.LOCATIONS);
  },

  async search(params: { name: string; country: string }): Promise<LocationResponse | null> {
    return apiClient.get<LocationResponse | null>(ENDPOINTS.LOCATION_SEARCH, params);
  },

  async getCountriesAndCities(): Promise<CountriesCitiesResponse> {
    return apiClient.get<CountriesCitiesResponse>(ENDPOINTS.COUNTRIES_CITIES);
  },

  async getPromotedTipsByName(params: PromotedTipsParams): Promise<PromotedTipResponse[]> {
    return apiClient.get<PromotedTipResponse[]>(ENDPOINTS.PROMOTED_TIPS, params);
  },

  async getCategoryCounts(locationId: number): Promise<Record<string, number>> {
    return apiClient.get<Record<string, number>>(
      `${ENDPOINTS.LOCATIONS}/${locationId}/category-counts`
    );
  },
};
