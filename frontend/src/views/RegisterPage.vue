<template>
  <v-row justify="center" class="mt-8">
    <v-col cols="12" sm="8" md="6" lg="4">
      <v-card class="pa-6">
        <!-- Başlık -->
        <v-card-title class="text-h4 text-center mb-4">
          <v-icon size="48" color="primary" class="mb-2">mdi-account-plus</v-icon>
          <div>Kayıt Ol</div>
        </v-card-title>
        
        <v-card-text>
          <!-- Kayıt Formu -->
          <v-form @submit.prevent="handleRegister" ref="formRef" validate-on="submit lazy">
            <v-text-field
              v-model="email"
              label="Email Adresi"
              type="email"
              placeholder="ornek@email.com"
              prepend-inner-icon="mdi-email"
              :rules="emailRules"
              :disabled="loading"
              variant="outlined"
              density="comfortable"
              required
              autocomplete="email"
              validate-on="blur"
            ></v-text-field>
            
            <!-- Bilgi Mesajı -->
            <v-alert
              v-if="message"
              :type="isError ? 'error' : 'success'"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="message = ''"
            >
              <template v-slot:title>
                {{ isError ? 'Hata!' : 'Başarılı!' }}
              </template>
              {{ message }}
            </v-alert>
            
            <!-- Kayıt Butonu -->
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="loading"
              :disabled="loading"
              class="mt-2"
            >
              <v-icon start>mdi-account-plus</v-icon>
              {{ loading ? 'Kayıt yapılıyor...' : 'Kayıt Ol' }}
            </v-btn>
          </v-form>
          
          <!-- Giriş Linki -->
          <div class="text-center mt-4">
            <span class="text-medium-emphasis">Zaten hesabınız var mı?</span>
            <router-link 
              to="/login" 
              class="text-primary font-weight-bold ms-1 text-decoration-none"
            >
              Giriş Yap
            </router-link>
          </div>
        </v-card-text>
        
        <!-- Bilgi Kartı -->
        <v-card-text>
          <v-alert
            type="info"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <template v-slot:text>
              <p class="mb-1">
                <v-icon size="small" class="me-1">mdi-email-check</v-icon>
                Kayıt olduktan sonra email adresinize bir doğrulama linki gönderilecektir.
              </p>
              <p class="mb-0">
                <v-icon size="small" class="me-1">mdi-shield-check</v-icon>
                Emailinizi doğruladıktan sonra şifrenizi belirleyip giriş yapabilirsiniz.
              </p>
            </template>
          </v-alert>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import apiClient, { API_ENDPOINTS } from '../config/api';

// Form verisi
const email = ref('');
const formRef = ref(null);

// Mesaj state'leri
const message = ref('');
const isError = ref(false);
const loading = ref(false);

// Validasyon kuralları
const emailRules = [
  (v: string) => !!v || 'Email adresi zorunludur',
  (v: string) => /.+@.+\..+/.test(v) || 'Geçerli bir email adresi giriniz',
  (v: string) => (v && v.length <= 254) || 'Email adresi çok uzun',
];

// Kayıt işlemi
const handleRegister = async () => {
  // Form validasyonu - Vuetify 3 için doğru kullanım
  if (formRef.value) {
    const { valid } = await (formRef.value as any).validate();
    if (!valid) return;
  }
  
  // Email boş mu kontrol et
  if (!email.value || !email.value.trim()) {
    message.value = 'Email adresi zorunludur.';
    isError.value = true;
    return;
  }
  
  // State'leri sıfırla
  message.value = '';
  isError.value = false;
  loading.value = true;
  
  try {
    const response = await apiClient.post(API_ENDPOINTS.REGISTER, {
      email: email.value,
      password: 'temporary-password'  // Geçici şifre
    });
    
    // Başarılı mesajı
    message.value = response.data.message || 
      'Doğrulama emaili gönderildi. Lütfen emailinizi kontrol edin.';
    isError.value = false;
    
    // Email alanını temizle
    email.value = '';
    
  } catch (error: any) {
    isError.value = true;
    
    // Hata mesajını belirle
    if (error.response?.data) {
      const data = error.response.data;
      
      if (data.email) {
        // Email ile ilgili hata
        if (Array.isArray(data.email)) {
          message.value = data.email[0];
        } else {
          message.value = data.email;
        }
      } else if (data.error) {
        message.value = data.error;
      } else if (data.detail) {
        message.value = data.detail;
      } else {
        // Diğer alan hataları
        message.value = Object.values(data).flat().join(', ');
      }
    } else if (error.message === 'Network Error') {
      message.value = 'Sunucuya bağlanılamadı. Lütfen internet bağlantınızı kontrol edin.';
    } else if (error.code === 'ECONNREFUSED') {
      message.value = 'Sunucuya bağlanılamadı. Lütfen daha sonra tekrar deneyin.';
    } else {
      message.value = 'Kayıt sırasında beklenmeyen bir hata oluştu.';
    }
    
    console.error('Kayıt hatası:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-card-title {
  white-space: normal;
  line-height: 1.4;
}

.text-decoration-none {
  text-decoration: none;
}

.text-decoration-none:hover {
  text-decoration: underline;
}

/* Animasyon */
.v-btn {
  transition: all 0.3s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}
</style>