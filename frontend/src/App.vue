<template>
  <v-app>
    <!-- Navigasyon Bar -->
    <v-app-bar color="primary" elevation="1">
      <v-container class="d-flex align-center">
        <v-app-bar-title>
          <router-link to="/" class="text-white text-decoration-none font-weight-bold">
            🍋  Stinpoll
          </router-link>
        </v-app-bar-title>
        
        <v-spacer></v-spacer>
        
        <!-- Giriş yapmamış kullanıcı -->
        <template v-if="!isAuthenticated">
          <v-btn to="/register" variant="outlined" color="white" class="mr-2">
            Kayıt Ol
          </v-btn>
          <v-btn to="/login" color="white" variant="flat">
            Giriş Yap
          </v-btn>
        </template>
        
        <!-- Giriş yapmış kullanıcı -->
        <template v-else>
          <v-btn to="/profile" variant="text" color="white" class="mr-2">
            <v-icon start>mdi-account</v-icon>
            Profilim
          </v-btn>
          <v-btn @click="handleLogout" color="error" variant="flat" size="small">
            <v-icon start>mdi-logout</v-icon>
            Çıkış
          </v-btn>
        </template>
      </v-container>
    </v-app-bar>
    
    <!-- Ana İçerik -->
    <v-main class="bg-grey-lighten-4">
      <v-container>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const isAuthenticated = computed(() => !!localStorage.getItem('token'));

const handleLogout = () => {
  localStorage.removeItem('token');
  delete axios.defaults.headers.common['Authorization'];
  router.push('/');
};

onMounted(() => {
  const token = localStorage.getItem('token');
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`;
  }
});
</script>

<style>
.v-app-bar-title a {
  color: white !important;
}
</style>