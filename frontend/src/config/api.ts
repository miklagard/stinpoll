// API yapılandırması
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Axios instance oluştur
import axios from 'axios';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
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

export default apiClient;