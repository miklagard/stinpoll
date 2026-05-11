import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,  // Cookie'leri gönder/al
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
});

// CSRF token'ı cookie'den oku
function getCsrfToken(): string | null {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
}

// CSRF token'ı almak için istek at
async function fetchCsrfToken(): Promise<string | null> {
  try {
    // Django'nun CSRF endpoint'ine istek at
    await apiClient.get('/csrf-token/');
    return getCsrfToken();
  } catch (error) {
    console.warn('CSRF token alınamadı:', error);
    return null;
  }
}

// CSRF token'ı sakla
let csrfToken: string | null = null;

// Uygulama başlangıcında CSRF token'ı al
fetchCsrfToken().then(token => {
  csrfToken = token;
  console.log('CSRF token alındı:', csrfToken);
});

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    // Token varsa ekle
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // CSRF token'ı varsa ekle (POST, PUT, PATCH, DELETE için)
    const method = config.method?.toUpperCase();
    if (method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      // CSRF token yoksa almaya çalış
      if (!csrfToken) {
        csrfToken = getCsrfToken();
        if (!csrfToken) {
          csrfToken = await fetchCsrfToken();
        }
      }
      
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    
    // FormData ise Content-Type'ı sil
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Yanıttan yeni CSRF token'ı al
    const newToken = getCsrfToken();
    if (newToken) {
      csrfToken = newToken;
    }
    return response;
  },
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
  CSRF_TOKEN: '/csrf-token/',
  REGISTER: '/register/',
  LOGIN: '/login/',
  VERIFY_EMAIL: (token: string) => `/verify/${token}/`,
  SET_PASSWORD: (token: string) => `/set-password/${token}/`,
  DELETE_ACCOUNT: (token: string) => `/delete-account/${token}/`,
  PROFILES: '/profiles/',
  PROFILE_DETAIL: (id: string) => `/profiles/${id}/`,
};

export default apiClient;