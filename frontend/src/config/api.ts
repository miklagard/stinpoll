// API yapılandırması
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Axios instance oluştur
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,  // Cookie'leri gönder
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// Request interceptor - token ekleme
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - hata yönetimi
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoint'leri
export const API_ENDPOINTS = {
  // Auth
  REGISTER: '/api/register/',
  LOGIN: '/api/login/',
  VERIFY_EMAIL: (token: string) => `/api/verify/${token}/`,
  SET_PASSWORD: (token: string) => `/api/set-password/${token}/`,
  DELETE_ACCOUNT: (token: string) => `/api/delete-account/${token}/`,
  
  // Profile
  PROFILES: '/api/profiles/',
  PROFILE_DETAIL: (id: string) => `/api/profiles/${id}/`,
  SET_PRIMARY_PHOTO: (id: string) => `/api/profiles/${id}/set_primary_photo/`,
};

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}


apiClient.interceptors.request.use(
  (config) => {
    // CSRF token'ı ekle
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    // Token varsa ekle
    const token = localStorage.getItem('token');
    if (token && !config.url?.includes('/register/')) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);


export default apiClient;