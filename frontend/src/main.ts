import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';

// Vuetify
import 'vuetify/styles';
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
    VBtn: {
      rounded: 'lg',
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
    },
    VCard: {
      rounded: 'lg',
      elevation: 2,
    }
  }
});

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
      meta: { requiresAuth: true }
    },
    {
      path: '/verify/:token',
      name: 'verify',
      component: VerifyEmail,
      props: true
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage
    }
  ]
});

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


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function initializeCsrf() {
  try {
    await apiClient.get(API_BASE_URL + 'csrf-token/');
    // CSRF token otomatik olarak cookie'ye set edilir
    console.log('CSRF token alındı');
  } catch (error) {
    console.error('CSRF token alınamadı:', error);
  }
}

// Uygulama başlangıcında çağırın
initializeCsrf();

const app = createApp(App);

app.use(router);
app.use(vuetify);

app.mount('#app');