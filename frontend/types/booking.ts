export interface FileUploadResponse {
  file_id: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  file_purpose: string;
}

export interface BookingDetailResponse {
  id: string;
  booking_reference: string;
  amount_paise: number;
  currency: string;
  payment_status: string;
  scheduling_status: string;
  category_title: string;
  category_slug: string;
  duration_display: string;
  years_experience: number;
  target_role: string;
  scheduled_start: string | null;
  scheduled_end: string | null;
  meeting_url: string | null;
  status_headline: string;
  status_message: string;
  created_at: string;
}
