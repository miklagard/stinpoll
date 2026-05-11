<template>
  <div>
    <!-- Hero Section -->
    <v-sheet color="primary" rounded="lg" class="pa-8 mb-8 text-center">
      <h1 class="text-h3 font-weight-bold mb-4">Eşleşme Platformuna Hoş Geldiniz</h1>
      <p class="text-h6 mb-6 opacity-80">Hayatınızın aşkını bulmak için doğru yerdesiniz</p>
      
      <div v-if="!isAuthenticated" class="d-flex gap-4 justify-center">
        <v-btn to="/register" color="white" variant="flat" size="large" class="px-8">
          <v-icon start>mdi-account-plus</v-icon>
          Hemen Kayıt Ol
        </v-btn>
        <v-btn to="/login" variant="outlined" color="white" size="large" class="px-8">
          <v-icon start>mdi-login</v-icon>
          Giriş Yap
        </v-btn>
      </div>
      
      <div v-else>
        <v-btn to="/profile" color="white" variant="flat" size="large" class="px-8 mr-4">
          <v-icon start>mdi-account</v-icon>
          Profilime Git
        </v-btn>
        <v-btn @click="handleLogout" color="error" variant="flat" size="large" class="px-8">
          <v-icon start>mdi-logout</v-icon>
          Çıkış Yap
        </v-btn>
      </div>
    </v-sheet>
    
    <!-- Özellikler -->
    <v-row class="mb-8">
      <v-col cols="12" md="4" v-for="(feature, index) in features" :key="index">
        <v-card height="100%" class="pa-6 text-center">
          <v-icon :icon="feature.icon" size="48" color="primary" class="mb-4"></v-icon>
          <h3 class="text-h5 mb-3">{{ feature.title }}</h3>
          <p class="text-body-1 text-medium-emphasis">{{ feature.description }}</p>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Hoş geldin mesajı -->
    <v-alert
      v-if="isAuthenticated"
      type="success"
      variant="tonal"
      class="mb-4"
    >
      Hoş geldiniz! Profilinizi düzenleyebilir veya yeni eşleşmeleri keşfedebilirsiniz.
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const features = [
  {
    icon: 'mdi-shield-lock',
    title: '🔒 Gizli Profiller',
    description: 'Bilgileriniz sadece sizin kontrolünüzde'
  },
  {
    icon: 'mdi-email-check',
    title: '✉️ Email Doğrulama',
    description: 'Güvenli kayıt ve doğrulama sistemi'
  },
  {
    icon: 'mdi-heart-multiple',
    title: '🎯 Detaylı Eşleşme',
    description: 'Size en uygun kişilerle tanışın'
  }
];

const isAuthenticated = computed(() => !!localStorage.getItem('token'));

const handleLogout = () => {
  localStorage.removeItem('token');
  delete axios.defaults.headers.common['Authorization'];
  router.push('/');
};
</script>

<style scoped>
.opacity-80 {
  opacity: 0.9;
}
</style>