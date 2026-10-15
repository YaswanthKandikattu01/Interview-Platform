export interface InterviewPrice {
  id: string;
  interview_type_id: string;
  amount_paise: number;
  currency: string;
  duration_min_minutes: number;
  duration_max_minutes: number;
  duration_display: string;
  is_active: boolean;
  created_at: string;
}

export interface InterviewCategory {
  id: string;
  slug: string;
  title: string;
  short_description: string;
  detailed_topics: string[];
  display_order: number;
  is_active: boolean;
  active_price: InterviewPrice | null;
}

export interface CanonicalPricing {
  amount_paise: number;
  currency: string;
  duration_display: string;
  duration_min_minutes: number;
  duration_max_minutes: number;
  price_formatted: string;
  guarantee: string;
  scheduling_promise: string;
}
