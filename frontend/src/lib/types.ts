export interface Message {
  id?: number;
  conversation?: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  media_type?: 'text' | 'image' | 'audio' | 'video';
  media_url?: string;
  created_at?: string;
}

export interface Diagnosis {
  id: number;
  conversation_id?: number;
  symptoms: string;
  diagnosis: string;
  severity: 'low' | 'medium' | 'high';
  recommendation: string;
  service: string;
  reasoning?: string;
  safety_warning?: string;
  vehicle?: string;
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
  vehicle_info?: string;
  is_rejected?: boolean;
}

export interface VehicleMakesResponse {
  makes: string[];
}

export interface VehicleModelsResponse {
  make: string;
  count: number;
  models: string[];
}
