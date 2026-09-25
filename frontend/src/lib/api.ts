import axios from 'axios';
import {
  ChatResponse,
  UploadResponse,
  Diagnosis,
  Booking,
  Conversation,
  VehicleMakesResponse,
  VehicleModelsResponse,
  DiagnosticSessionData,
  DiagnosticApiResponse
} from './types';

const rawUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';
const cleanUrl = rawUrl.trim().replace(/\/+$/, '');
const API_BASE_URL = cleanUrl.endsWith('/api') ? cleanUrl : `${cleanUrl}/api`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ApiError {
  status: number;
  message: string;
  details?: unknown;
}

export function parseApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status || 500;
    const data = error.response?.data;

    let message = 'An unexpected network error occurred.';
    if (data?.message) {
      message = data.message;
    } else if (status === 400) {
      message = 'Invalid request data. Please check your inputs.';
    } else if (status === 404) {
      message = 'Requested information was not found.';
    } else if (status === 413) {
      message = 'Uploaded file is too large (maximum 25MB).';
    } else if (status === 415) {
      message = 'Unsupported file type. Please upload JPEG/PNG images, MP3/WAV audio, or MP4/WEBM video.';
    } else if (status === 429) {
      message = 'Rate limit reached or AI service is busy. Please try again in a few moments.';
    } else if (status === 500) {
      message = 'Internal server error. Please try again.';
    }

    return {
      status,
      message,
      details: data?.details || data,
    };
  }

  return {
    status: 500,
    message: (error as Error)?.message || 'Something went wrong.',
  };
}

// API methods
export const api = {
  async checkHealth() {
    const res = await apiClient.get('/health/');
    return res.data;
  },

  async sendChatMessage(payload: {
    message: string;
    conversation_id?: number | null;
    media_url?: string | null;
    media_type?: string | null;
  }): Promise<ChatResponse> {
    const res = await apiClient.post<ChatResponse>('/chat/', payload);
    return res.data;
  },

  async uploadMedia(file: File, onUploadProgress?: (progressEvent: { loaded: number; total?: number }) => void): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<UploadResponse>('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return res.data;
  },

  async requestDiagnosis(conversation_id: number): Promise<Diagnosis> {
    const res = await apiClient.post<Diagnosis>('/diagnosis/', { conversation_id });
    return res.data;
  },

  async createBooking(bookingData: {
    diagnosis_id?: number | null;
    customer_name: string;
    phone: string;
    vehicle: string;
    preferred_date: string;
    preferred_time: string;
    service: string;
    notes?: string;
  }): Promise<Booking> {
    const res = await apiClient.post<Booking>('/booking/', bookingData);
    return res.data;
  },

  async getBooking(id: number | string): Promise<Booking> {
    const res = await apiClient.get<Booking>(`/booking/${id}/`);
    return res.data;
  },

  async listBookings(): Promise<Booking[]> {
    const res = await apiClient.get<Booking[]>('/booking/');
    return res.data;
  },

  async listConversations(): Promise<Conversation[]> {
    const res = await apiClient.get<Conversation[]>('/conversations/');
    return res.data;
  },

  async getConversation(id: number | string): Promise<Conversation> {
    const res = await apiClient.get<Conversation>(`/conversations/${id}/`);
    return res.data;
  },

  async getVehicleMakes(): Promise<VehicleMakesResponse> {
    const res = await apiClient.get<VehicleMakesResponse>('/vehicles/makes/');
    return res.data;
  },

  async getVehicleModels(make: string): Promise<VehicleModelsResponse> {
    const res = await apiClient.get<VehicleModelsResponse>(`/vehicles/models/?make=${encodeURIComponent(make)}`);
    return res.data;
  },

  async createDiagnosticSession(payload: {
    message: string;
    vehicle?: { make?: string; model?: string; year?: number };
    vehicle_id?: string;
  }): Promise<DiagnosticApiResponse<DiagnosticSessionData>> {
    const res = await apiClient.post<DiagnosticApiResponse<DiagnosticSessionData>>('/v1/diagnostic/sessions/', payload);
    return res.data;
  },

  async submitDiagnosticAnswer(
    sessionId: string,
    questionId: string,
    answer: { text: string } | string
  ): Promise<DiagnosticApiResponse<DiagnosticSessionData>> {
    const formattedAnswer = typeof answer === 'string' ? { text: answer } : answer;
    const res = await apiClient.post<DiagnosticApiResponse<DiagnosticSessionData>>(
      `/v1/diagnostic/sessions/${sessionId}/answers/`,
      {
        question_id: questionId,
        answer: formattedAnswer,
      }
    );
    return res.data;
  },

  async assessDiagnosticSession(sessionId: string): Promise<DiagnosticApiResponse<DiagnosticSessionData>> {
    const res = await apiClient.post<DiagnosticApiResponse<DiagnosticSessionData>>(
      `/v1/diagnostic/sessions/${sessionId}/assess/`,
      { confirm: true }
    );
    return res.data;
  },

  async getDiagnosticSession(sessionId: string): Promise<DiagnosticApiResponse<DiagnosticSessionData>> {
    const res = await apiClient.get<DiagnosticApiResponse<DiagnosticSessionData>>(
      `/v1/diagnostic/sessions/${sessionId}/`
    );
    return res.data;
  },
};
