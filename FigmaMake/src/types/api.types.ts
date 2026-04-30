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
  category_id?: string;
  category_confidence?: number;
}

export interface TipCreate {
  tip_text: string;
  location_name?: string;
  location_country?: string;
  latitude?: number;
  longitude?: number;
  user_id?: number;
  category_id?: string;
}

// Promoted Tip Types
export interface PromotedTipResponse {
  id: number;
  tip_text: string;
  original_text?: string;
  location_id: number;
  location_name?: string;
  location_country?: string;
  mention_count: number;
  similarity_score?: number;
  promoted_at: string;
  category_id?: string;
}

// Category Types
export interface CategoryResponse {
  id: string;
  title: string;
  description: string;
  icon_name?: string;
  color?: string;
  display_order?: number;
}

// Query Parameters
export interface TipsQueryParams {
  location_id?: number;
  category_id?: string;
  status?: string;
  language?: string;
  limit?: number;
  offset?: number;
}

export interface PromotedTipsParams {
  location_name: string;
  location_country: string;
  category_id?: string;
  language?: string;
  limit?: number;
}

// Countries and Cities Types
export interface CityInfo {
  name: string;
  latitude: number | null;
  longitude: number | null;
}

export interface CountryInfo {
  name: string;
  code: string;
  cities: CityInfo[];
}

export interface CountriesCitiesResponse {
  countries: CountryInfo[];
}
