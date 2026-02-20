import { apiClient } from './client';
import { ENDPOINTS } from './endpoints';
import { TipResponse, TipCreate, TipsQueryParams } from '@/types/api.types';

export const tipsService = {
  async create(tip: TipCreate): Promise<TipResponse> {
    return apiClient.post<TipResponse>(ENDPOINTS.TIPS, tip);
  },

  async getAll(params?: TipsQueryParams): Promise<TipResponse[]> {
    return apiClient.get<TipResponse[]>(ENDPOINTS.TIPS, params);
  },

  async getMyTips(language?: string): Promise<TipResponse[]> {
    return apiClient.get<TipResponse[]>(`${ENDPOINTS.TIPS}/me`, language ? { language } : undefined);
  },
};
