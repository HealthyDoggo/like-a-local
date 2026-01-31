// Location Types
export interface LocationResponse {
  id: number;
  name: string;
  country: string;
  latitude?: number;
  longitude?: number;
}

// Tip Types
export interface TipResponse {
  id: number;
  tip_text: string;
  original_language?: string;
  translated_text?: string;
  location_id?: number;
  location_name?: string;
  location_country?: string;
  user_id?: number;
  submitted_at: string;
  processed_at?: string;
  status: string;
}

export interface TipCreate {
  tip_text: string;
  location_name?: string;
  location_country?: string;
  latitude?: number;
  longitude?: number;
  user_id?: number;
}

// Promoted Tip Types
export interface PromotedTipResponse {
  id: number;
  tip_text: string;
  location_id: number;
  location_name?: string;
  location_country?: string;
  mention_count: number;
  similarity_score?: number;
  promoted_at: string;
}

// Query Parameters
export interface TipsQueryParams {
  location_id?: number;
  status?: string;
  language?: string;
  limit?: number;
  offset?: number;
}

export interface PromotedTipsParams {
  location_name: string;
  location_country: string;
  language?: string;
  limit?: number;
}

// Countries and Cities Types
export interface CityInfo {
  name: string;
  latitude: number;
  longitude: number;
}

export interface CountryInfo {
  name: string;
  code: string;
  cities: CityInfo[];
}

export interface CountriesCitiesResponse {
  countries: CountryInfo[];
}
