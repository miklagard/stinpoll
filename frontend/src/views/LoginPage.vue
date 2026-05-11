<template>
  <v-row justify="center" class="mt-8">
    <v-col cols="12" sm="8" md="6" lg="4">
      <v-card class="pa-6">
        <!-- Başlık -->
        <v-card-title class="text-h4 text-center mb-4">
          <v-icon size="48" color="primary" class="mb-2">mdi-login</v-icon>
          <div>Giriş Yap</div>
        </v-card-title>
        
        <v-card-text>
          <!-- Giriş Formu -->
          <v-form @submit.prevent="handleLogin" ref="form">
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
            ></v-text-field>
            
            <v-text-field
              v-model="password"
              label="Şifre"
              type="password"
              placeholder="Şifrenizi girin"
              prepend-inner-icon="mdi-lock"
              :rules="passwordRules"
              :disabled="loading"
              variant="outlined"
              density="comfortable"
              required
              autocomplete="current-password"
            >
              <template v-slot:append-inner>
                <v-icon
                  @click="showPassword = !showPassword"
                  :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  size="small"
                ></v-icon>
              </template>
            </v-text-field>
            
            <!-- Hata Mesajı -->
            <v-alert
              v-if="error"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="error = ''"
            >
              <template v-slot:title>
                Giriş Başarısız!
              </template>
              {{ error }}
            </v-alert>
            
            <!-- Giriş Butonu -->
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="loading"
              :disabled="loading || !email || !password"
              class="mt-2"
            >
              <v-icon start>mdi-login</v-icon>
              {{ loading ? 'Giriş yapılıyor...' : 'Giriş Yap' }}
            </v-btn>
          </v-form>
          
          <!-- Kayıt Linki -->
          <div class="text-center mt-4">
            <span class="text-medium-emphasis">Hesabınız yok mu?</span>
            <router-link 
              to="/register" 
              class="text-primary font-weight-bold ms-1 text-decoration-none"
            >
              Kayıt Ol
            </router-link>
          </div>
          
          <!-- Şifremi Unuttum Linki (Opsiyonel) -->
          <div class="text-center mt-2">
            <a 
              href="#" 
              class="text-caption text-medium-emphasis text-decoration-none"
              @click.prevent="forgotPassword"
            >
              Şifremi unuttum
            </a>
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
                <v-icon size="small" class="me-1">mdi-shield-lock</v-icon>
                Giriş bilgileriniz güvenli bir şekilde iletilir.
              </p>
              <p class="mb-0">
                <v-icon size="small" class="me-1">mdi-email-check</v-icon>
                Email adresiniz henüz doğrulanmamışsa giriş yapamazsınız.
              </p>
            </template>
          </v-alert>
        </v-card-text>
      </v-card>
      
      <!-- Başarılı Giriş Dialog'u -->
      <v-dialog v-model="showSuccessDialog" max-width="400" persistent>
        <v-card>
          <v-card-title class="text-h5 text-center pt-6">
            <v-icon size="64" color="success" class="mb-2">mdi-check-circle</v-icon>
            <div>Giriş Başarılı!</div>
          </v-card-title>
          <v-card-text class="text-center">
            <p>Başarıyla giriş yaptınız.</p>
            <p class="text-medium-emphasis">Yönlendiriliyorsunuz...</p>
            <v-progress-linear
              indeterminate
              color="primary"
              class="mt-4"
            ></v-progress-linear>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import apiClient, { API_ENDPOINTS } from '../config/api';

const router = useRouter();
const route = useRoute();

// Form verileri
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const form = ref(null);

// State'ler
const error = ref('');
const loading = ref(false);
const showSuccessDialog = ref(false);

// Validasyon kuralları
const emailRules = [
  (v: string) => !!v || 'Email adresi zorunludur',
  (v: string) => /.+@.+\..+/.test(v) || 'Geçerli bir email adresi giriniz',
];

const passwordRules = [
  (v: string) => !!v || 'Şifre zorunludur',
  (v: string) => (v && v.length >= 6) || 'Şifre en az 6 karakter olmalıdır',
];

// Şifre görünürlüğü değiştiğinde input type'ı güncelle
watch(showPassword, (_newVal) => {
  const passwordInput = document.querySelector('input[type="password"]');
  if (passwordInput) {
    // Type değişimi Vuetify tarafından yönetilir
  }
});

// Giriş işlemi
const handleLogin = async () => {
  // Form validasyonu
  const { valid } = await (form.value as any)?.validate() || { valid: false };
  if (!valid) return;
  
  // State'leri sıfırla
  error.value = '';
  loading.value = true;
  
  try {
    const response = await apiClient.post(API_ENDPOINTS.LOGIN, {
      email: email.value,
      password: password.value
    });
    
    const token = response.data.token;
    
    if (token) {
      // Token'ı kaydet
      localStorage.setItem('token', token);
      
      // Axios header'ına token ekle
      apiClient.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      // Başarılı giriş dialog'unu göster
      showSuccessDialog.value = true;
      
      // 1.5 saniye sonra yönlendir
      setTimeout(() => {
        showSuccessDialog.value = false;
        
        // Redirect varsa oraya, yoksa profile sayfasına
        const redirectPath = route.query.redirect as string;
        if (redirectPath) {
          router.push(redirectPath);
        } else {
          router.push('/profile');
        }
      }, 1500);
    }
    
  } catch (err: any) {
    // Hata mesajını belirle
    if (err.response?.data) {
      const data = err.response.data;
      
      if (data.error) {
        error.value = data.error;
      } else if (data.detail) {
        error.value = data.detail;
      } else if (data.non_field_errors) {
        error.value = data.non_field_errors[0];
      } else {
        error.value = 'Giriş yapılırken bir hata oluştu.';
      }
    } else if (err.message === 'Network Error') {
      error.value = 'Sunucuya bağlanılamadı. Lütfen internet bağlantınızı kontrol edin.';
    } else {
      error.value = 'Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin.';
    }
    
    console.error('Giriş hatası:', err);
    
    // Şifre alanını temizle
    password.value = '';
    
  } finally {
    loading.value = false;
  }
};

// Şifremi unuttum (henüz implemente edilmedi)
const forgotPassword = () => {
  alert('Şifre sıfırlama özelliği yakında eklenecektir.');
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

/* Dialog animasyonu */
.v-overlay {
  backdrop-filter: blur(2px);
}
</style>