export interface Message {
  id?: number;
  conversation?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  media_type?: 'text' | 'image' | 'audio' | 'video';
  media_url?: string;
  diagnosis?: Diagnosis;
  created_at?: string;
}

export interface Diagnosis {
  id: number;
  conversation_id?: number;
  symptoms: string;
  diagnosis: string;
  severity: 'low' | 'medium' | 'high';
  confidence?: 'low' | 'medium' | 'high';
  recommendation: string;
  service: string;
  reasoning?: string;
  safety_warning?: string;
  vehicle?: string;
  source?: 'rules' | 'gemini' | 'fallback';
  is_cached?: boolean;
  fingerprint?: string;
  created_at?: string;
}

export interface Booking {
  id: number;
  diagnosis_id?: number | null;
  diagnosis_details?: Diagnosis;
  customer_name: string;
  phone: string;
  vehicle: string;
  preferred_date: string;
  preferred_time: string;
  service: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes?: string;
  created_at?: string;
}

export interface Conversation {
  id: number;
  session_id: string;
  vehicle_info?: string;
  state?: Record<string, unknown>;
  gemini_calls?: number;
  input_tokens?: number;
  output_tokens?: number;
  estimated_cost?: number;
  messages: Message[];
  diagnoses: Diagnosis[];
  created_at: string;
  updated_at: string;
}

export interface UploadResponse {
  id: number;
  file_url: string;
  media_type: 'image' | 'audio' | 'video';
  file_name: string;
  file_size: number;
}

export interface ChatResponse {
  reply: string;
  conversation_id: number;
  needs_more_info: boolean;
  can_diagnose?: boolean;
  diagnostic_status?: string;
  vehicle_info?: string;
  is_rejected?: boolean;
  is_security_refusal?: boolean;
  is_safety_critical?: boolean;
  progress?: {
    completed: number;
    estimated_required: number;
  };
  next_field?: string;
  quick_replies?: string[];
  candidate_issues?: Array<{ issue: string; score: number }>;
}

export interface VehicleMakesResponse {
  makes: string[];
}

export interface VehicleModelsResponse {
  make: string;
  count: number;
  models: string[];
}

export interface DiagnosticQuestionOption {
  id: string;
  label: string;
}

export interface DiagnosticQuestion {
  id: string;
  answer_type: 'text' | 'choice' | 'boolean' | 'number' | string;
  options?: DiagnosticQuestionOption[];
}

export interface DiagnosticProgressInfo {
  answered: number;
  total: number;
  percentage: number;
}

export interface DiagnosticConcern {
  title: string;
  system?: string;
  likelihood?: string;
  severity?: string;
  explanation?: string;
}

export interface DiagnosticAssessment {
  summary: string;
  severity: 'caution' | 'warning' | 'critical' | 'low' | 'medium' | 'high' | string;
  primary_concern: string;
  possible_concerns: DiagnosticConcern[];
  recommended_actions: string[];
  safety?: {
    level?: string;
    message?: string;
  };
  limitations?: string[];
  questions_asked?: number;
  questions_answered?: number;
  evidence_used?: string[];
}

export interface DiagnosticSessionData {
  session: {
    id: string;
    status: 'planning' | 'collecting_answers' | 'ready_for_assessment' | 'assessing' | 'completed' | 'failed' | string;
  };
  progress: DiagnosticProgressInfo;
  message?: {
    role: 'assistant' | 'user';
    type?: string;
    content: string;
  };
  question?: DiagnosticQuestion | null;
  assessment?: DiagnosticAssessment;
  diagnosis_id?: number;
}

export interface DiagnosticApiResponse<T = DiagnosticSessionData> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  } | null;
}

