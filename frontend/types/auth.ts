export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  role: 'CANDIDATE' | 'ADMIN';
  is_email_verified: boolean;
  is_active: boolean;
}

export interface CandidateProfile {
  id: string;
  user_id: string;
  years_experience: number;
  current_company: string | null;
  target_role: string;
  technical_skills: string[];
  linkedin_url: string | null;
}

export interface AuthResponse {
  user: User;
  profile: CandidateProfile | null;
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  csrf_token: string;
  message?: string;
}
