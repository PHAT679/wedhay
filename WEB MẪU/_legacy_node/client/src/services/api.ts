const API_BASE = '/api';

export function getToken(): string | null {
  return localStorage.getItem('emmay_token');
}

export function setToken(token: string) {
  localStorage.setItem('emmay_token', token);
}

export function removeToken() {
  localStorage.removeItem('emmay_token');
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.message || `Lỗi yêu cầu (${response.status})`);
  }

  return data as T;
}

export const api = {
  // Auth
  login: (credentials: { tenDangNhap: string; matKhau: string }) =>
    request<{ message: string; token: string; user: any }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  register: (payload: { hoTen: string; soDienThoai: string; tenDangNhap: string; matKhau: string }) =>
    request<{ message: string; token: string; user: any }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getMe: () => request<any>('/auth/me'),

  // Services
  getServices: (search?: string) =>
    request<any[]>(`/services${search ? `?search=${encodeURIComponent(search)}` : ''}`),

  getService: (id: string) => request<any>(`/services/${id}`),

  addService: (data: { tenDichVu: string; giaTien: number; thoiLuong: number; ghiChu?: string }) =>
    request<{ message: string; service: any }>('/services', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateService: (id: string, data: { tenDichVu: string; giaTien: number; thoiLuong: number; ghiChu?: string }) =>
    request<{ message: string; service: any }>(`/services/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteService: (id: string) =>
    request<{ message: string }>(`/services/${id}`, {
      method: 'DELETE',
    }),

  // Appointments
  getAvailableSlots: (date: string, duration: number) =>
    request<{ date: string; duration: number; totalStaff: number; availableSlots: any[] }>(
      `/appointments/available-slots?date=${date}&duration=${duration}`
    ),

  createAppointment: (payload: {
    tenLienHe: string;
    soDienThoaiLienHe: string;
    ngayGioBatDau: string;
    dichVuIds: string[];
    ghiChu?: string;
  }) =>
    request<{ message: string; data: any }>('/appointments', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getMyAppointments: () => request<any[]>('/appointments/my'),

  getTimeline: (date: string) =>
    request<{ date: string; total: number; appointments: any[] }>(`/appointments/timeline?date=${date}`),

  getAppointment: (id: string) => request<any>(`/appointments/${id}`),

  rescheduleAppointment: (id: string, ngayGioMoi: string) =>
    request<{ message: string; ngayGioMoi: string }>(`/appointments/${id}/reschedule`, {
      method: 'PUT',
      body: JSON.stringify({ ngayGioMoi }),
    }),

  cancelAppointment: (id: string, lyDoHuy?: string) =>
    request<{ message: string; isLateCancel?: boolean; note?: string }>(`/appointments/${id}/cancel`, {
      method: 'PUT',
      body: JSON.stringify({ lyDoHuy }),
    }),

  updateAppointmentStatus: (id: string, trangThai: string) =>
    request<{ message: string; trangThai: string }>(`/appointments/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ trangThai }),
    }),

  // Assignments
  getStaffAvailability: (startTime?: string, duration?: number, excludeAppointmentId?: string) => {
    let url = '/assignments/staff-availability';
    const params = new URLSearchParams();
    if (startTime) params.append('startTime', startTime);
    if (duration) params.append('duration', duration.toString());
    if (excludeAppointmentId) params.append('excludeAppointmentId', excludeAppointmentId);
    const qs = params.toString();
    return request<any[]>(qs ? `${url}?${qs}` : url);
  },

  getPendingAssignments: () => request<any[]>('/assignments/pending'),

  assignStaff: (maLichHen: string, maNhanVien: string) =>
    request<{ message: string }>('/assignments', {
      method: 'POST',
      body: JSON.stringify({ maLichHen, maNhanVien }),
    }),

  reassignStaff: (maLichHen: string, maNhanVienMoi: string) =>
    request<{ message: string }>(`/assignments/${maLichHen}`, {
      method: 'PUT',
      body: JSON.stringify({ maNhanVienMoi }),
    }),

  getMyTasks: () => request<any[]>('/assignments/my-tasks'),

  acceptTask: (maPhanCong: string) =>
    request<{ message: string }>(`/assignments/${maPhanCong}/accept`, {
      method: 'POST',
    }),

  rejectTask: (maPhanCong: string, lyDoTuChoi: string) =>
    request<{ message: string }>(`/assignments/${maPhanCong}/reject`, {
      method: 'POST',
      body: JSON.stringify({ lyDoTuChoi }),
    }),

  // Customers
  getCustomers: (search?: string) =>
    request<any[]>(`/customers${search ? `?search=${encodeURIComponent(search)}` : ''}`),

  addCustomer: (data: { hoTen: string; soDienThoai: string; linkFacebook?: string; linkZalo?: string }) =>
    request<{ message: string; customer: any }>('/customers', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCustomer: (id: string, data: { hoTen: string; soDienThoai: string; linkFacebook?: string; linkZalo?: string }) =>
    request<{ message: string; customer: any }>(`/customers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  getCustomerHistory: (id: string) =>
    request<{ customer: any; tongSoLanDat: number; history: any[] }>(`/customers/${id}/history`),

  // Payments
  generateQR: (maLichHen: string) =>
    request<{
      maLichHen: string;
      soTien: number;
      noiDung: string;
      nganHang: string;
      soTaiKhoan: string;
      chuTaiKhoan: string;
      qrUrl: string;
    }>('/payments/generate-qr', {
      method: 'POST',
      body: JSON.stringify({ maLichHen }),
    }),

  confirmPayment: (maLichHen: string, phuongThuc: 'Tiền Mặt' | 'QR') =>
    request<{ message: string; soTien: number; phuongThuc: string; trangThai: string }>('/payments/confirm', {
      method: 'POST',
      body: JSON.stringify({ maLichHen, phuongThuc }),
    }),

  // Notifications
  getNotifications: () =>
    request<{ unreadCount: number; notifications: any[] }>('/notifications'),

  markNotificationAsRead: (id: string) =>
    request<{ message: string }>(`/notifications/${id}/read`, {
      method: 'PATCH',
    }),

  markAllNotificationsAsRead: () =>
    request<{ message: string }>('/notifications/read-all', {
      method: 'PATCH',
    }),
};
