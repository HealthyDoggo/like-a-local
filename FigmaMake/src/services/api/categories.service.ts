import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { CategoryResponse } from '@/types/api.types';

export const categoriesService = {
  async getAll(): Promise<CategoryResponse[]> {
    return apiClient.get<CategoryResponse[]>(ENDPOINTS.CATEGORIES);
  },
};
