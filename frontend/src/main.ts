import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';

// Vuetify
import 'vuetify/dist/vuetify.min.css'; // veya 'vuetify/styles'
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css';

import HomePage from './views/HomePage.vue';
import RegisterPage from './views/RegisterPage.vue';
import ProfilePage from './views/ProfilePage.vue';
import LoginPage from './views/LoginPage.vue';
import VerifyEmail from './views/VerifyEmail.vue';
import apiClient from './config/api';

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#4CAF50',
          secondary: '#2196F3',
          accent: '#FF9800',
          error: '#f44336',
          success: '#4CAF50',
          background: '#f5f5f5',
          surface: '#ffffff',
        }
      }
    }
  },
  defaults: {
    VBtn: { rounded: 'lg' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
    VCard: { rounded: 'lg', elevation: 2 },
  }
});

// Varsayılan title
const DEFAULT_TITLE = '🍋 Stinpoll';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage,
      meta: { title: '🍋 Stinpoll - Eşleşme Platformu' }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
      meta: { title: 'Kayıt Ol - 🍋 Stinpoll' }
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
      meta: { 
        requiresAuth: true,
        title: 'Profilim - 🍋 Stinpoll'
      }
    },
    {
      path: '/verify/:token',
      name: 'verify',
      component: VerifyEmail,
      props: true,
      meta: { title: 'Email Doğrulama - 🍋 Stinpoll' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: { title: 'Giriş Yap - 🍋 Stinpoll' }
    }
  ]
});

// Kimlik doğrulama kontrolü
router.beforeEach((to, _from) => {
  const token = localStorage.getItem('token');
  
  if (to.meta.requiresAuth && !token) {
    return { name: 'login' };
  }
  
  if (token && (to.name === 'login' || to.name === 'register')) {
    return { name: 'home' };
  }
  
  return true;
});

// SAYFA BAŞLIĞINI GÜNCELLE - afterEach EKLENDİ
router.afterEach((to) => {
  const title = to.meta.title as string;
  document.title = title || DEFAULT_TITLE;
});

// CSRF token alma (baseURL zaten apiClient'te tanımlı)
async function initializeCsrf() {
  try {
    // apiClient baseURL'i zaten içeriyor, tekrar eklemeye gerek yok
    await apiClient.get('/csrf-token/');
    console.log('CSRF token alındı');
  } catch (error) {
    console.error('CSRF token alınamadı:', error);
  }
}

// CSRF token'ı al (production'da gerekebilir)
if (import.meta.env.PROD) {
  initializeCsrf();
}

const app = createApp(App);

app.use(router);
app.use(vuetify);

app.mount('#app');