import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';

// Vuetify
import 'vuetify/dist/vuetify.min.css';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css';

// Doğrudan import yerine lazy loading kullanın
const HomePage = () => import('./views/HomePage.vue');
const RegisterPage = () => import('./views/RegisterPage.vue');
const LoginPage = () => import('./views/LoginPage.vue');
const ProfilePage = () => import('./views/ProfilePage.vue');
const VerifyEmail = () => import('./views/VerifyEmail.vue');
const DeleteAccount = () => import('./views/DeleteAccount.vue');


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
      component: HomePage,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage,
      meta: { requiresAuth: true },
    },
    {
      path: '/verify/:token',
      name: 'verify',
      component: VerifyEmail,
      props: true,
    },
    {
      path: '/delete-account/:token',
      name: 'delete-account',
      component: DeleteAccount,
      props: true,
      meta: { title: 'Hesap Silme - 🍋 Stinpoll' }
    },
  ],
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

const app = createApp(App);

app.use(router);
app.use(vuetify);

app.mount('#app');