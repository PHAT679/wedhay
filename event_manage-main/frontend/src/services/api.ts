/**
 * EventFlow API Client
 * Connects frontend to the Express + Prisma REST API
 */

const BASE_URL = (import.meta as any).env?.VITE_API_URL || '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('eventflow_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('eventflow_token', token);
}

export function removeAuthToken(): void {
  localStorage.removeItem('eventflow_token');
}

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
    signal: options.signal || AbortSignal.timeout(15000),
  });

  if (!response.headers.get('content-type')?.includes('application/json')) {
    throw new Error('Không kết nối được API. Hãy chạy CHAY_FULLSTACK.bat trên máy chủ.');
  }
  const data = await response.json();

  if (!response.ok) {
    throw new Error(Array.isArray(data.data) ? data.data.map((item: any) => item.message).join('; ') : data.error || data.message || 'Yêu cầu API thất bại');
  }

  return data;
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<{ success: boolean; data: { token: string; user: any } }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getMe: () => request<{ success: boolean; data: any }>('/auth/me'),

  // Events
  getEvents: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<{ success: boolean; events: any[]; pagination: { totalPages: number } }>(`/events${qs}`);
  },
  getEventById: (id: string) => request<{ success: boolean; data: any }>(`/events/${id}`),
  createEvent: (data: any) =>
    request<{ success: boolean; data: any }>('/events', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateEvent: (id: string, data: any) =>
    request<{ success: boolean; data: any }>(`/events/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  submitEvent: (id: string) =>
    request<{ success: boolean; data: any; message: string }>(`/events/${id}/submit`, {
      method: 'POST',
    }),
  reviewEvent: (id: string, action: string, comments?: string, reason?: string) =>
    request<{ success: boolean; data: any; message: string }>(`/events/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, comments, reason }),
    }),
  getAvailableActions: (id: string) =>
    request<{ success: boolean; data: string[] }>(`/events/${id}/available-actions`),
  getEventHistory: (id: string) =>
    request<{ success: boolean; data: any[] }>(`/events/${id}/history`),

  // Bookings & Resources
  checkConflict: (facilityId: string, startTime: string, endTime: string, excludeBookingId?: string) =>
    request<{ success: boolean; conflict: boolean; conflictingBookings: any[] }>('/bookings/check-conflict', {
      method: 'POST',
      body: JSON.stringify({ facilityId, startTime, endTime, excludeBookingId }),
    }),
  createBooking: (data: any) =>
    request<{ success: boolean; data: any }>('/bookings', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  confirmBooking: (id: string) =>
    request<{ success: boolean; data: any; message: string }>(`/bookings/${id}/confirm`, {
      method: 'PUT',
    }),
  rejectBooking: (id: string) =>
    request<{ success: boolean; data: any; message: string }>(`/bookings/${id}/reject`, {
      method: 'PUT',
    }),
  getFacilityCalendar: (facilityId: string, startDate?: string, endDate?: string) => {
    const qs = new URLSearchParams({ ...(startDate && { startDate }), ...(endDate && { endDate }) }).toString();
    return request<{ success: boolean; data: any[] }>(`/bookings/facilities/${facilityId}/calendar?${qs}`);
  },

  // AI Assistant
  analyzeEvent: (eventData: any) =>
    request<{ success: boolean; data: any }>('/ai/analyze-event', {
      method: 'POST',
      body: JSON.stringify(eventData),
    }),
  suggestResources: (expectedAttendees: number, eventType: string) =>
    request<{ success: boolean; data: any }>('/ai/suggest-resources', {
      method: 'POST',
      body: JSON.stringify({ expectedAttendees, eventType }),
    }),
  draftReport: (eventId: string, actualAttendees?: number, highlights?: string[]) =>
    request<{ success: boolean; data: any }>('/ai/draft-report', {
      method: 'POST',
      body: JSON.stringify({ eventId, actualAttendees, highlights }),
    }),

  // Handover & Return
  createHandover: (data: any) =>
    request<{ success: boolean; data: any; message: string }>('/handover', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  createInspection: (data: any) =>
    request<{ success: boolean; data: any; message: string }>('/handover/inspection', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  createIncident: (data: any) =>
    request<{ success: boolean; data: any; message: string }>('/handover/incident', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getHandoverRecords: (eventId: string) =>
    request<{ success: boolean; data: { handovers: any[]; inspections: any[]; incidents: any[] } }>(`/handover/${eventId}`),

  // Settlement & Finance
  getSettlement: (eventId: string) =>
    request<{ success: boolean; data: any }>(`/settlements/${eventId}`),
  createSettlement: (data: any) =>
    request<{ success: boolean; data: any }>('/settlements', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  submitSettlement: (id: string) =>
    request<{ success: boolean; data: any; message: string }>(`/settlements/${id}/submit`, {
      method: 'POST',
    }),
  reviewSettlement: (id: string, decision: 'APPROVED' | 'REJECTED' | 'REQUEST_AMENDMENT', notes?: string) =>
    request<{ success: boolean; data: any; message: string }>(`/settlements/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ decision, notes }),
    }),

  // Analytics
  getDashboardStats: () =>
    request<{ success: boolean; data: any }>('/analytics/dashboard'),
  getWorkflowBottlenecks: () =>
    request<{ success: boolean; data: any }>('/analytics/workflow-bottlenecks'),
};
