<template>
  <v-row justify="center" class="mt-8">
    <v-col cols="12" sm="8" md="6" lg="5">
      
      <!-- Yükleniyor -->
      <v-card v-if="loading" class="pa-8 text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
          width="4"
          class="mb-4"
        ></v-progress-circular>
        <h2 class="text-h5 mb-2">Email doğrulanıyor...</h2>
        <p class="text-medium-emphasis">Lütfen bekleyin, doğrulama işlemi devam ediyor.</p>
      </v-card>

      <!-- Doğrulama Başarılı - Şifre Belirleme -->
      <v-card v-else-if="success && !passwordSet && !autoLoggedIn" class="pa-6">
        <v-card-title class="text-center flex-column">
          <v-icon size="64" color="success" class="mb-3">mdi-check-circle</v-icon>
          <span class="text-h4">Email Doğrulandı!</span>
        </v-card-title>
        
        <v-card-text class="text-center">
          <p class="text-h6 mb-4">Email adresiniz başarıyla doğrulandı.</p>
          
          <v-divider class="my-4"></v-divider>
          
          <h3 class="text-h6 mb-4">Şifre Belirleme</h3>
          <p class="text-medium-emphasis mb-4">
            Lütfen hesabınız için güvenli bir şifre belirleyin:
          </p>
          
          <v-form @submit.prevent="handleSetPassword">
            <v-text-field
              v-model="password"
              label="Şifre"
              :type="showPassword ? 'text' : 'password'"
              placeholder="En az 6 karakter"
              prepend-inner-icon="mdi-lock"
              :rules="passwordRules"
              :disabled="passwordLoading"
              variant="outlined"
              density="comfortable"
              required
            >
              <template v-slot:append-inner>
                <v-icon
                  @click="showPassword = !showPassword"
                  :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  size="small"
                ></v-icon>
              </template>
            </v-text-field>
            
            <v-text-field
              v-model="passwordConfirm"
              label="Şifre Tekrar"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Şifrenizi tekrar girin"
              prepend-inner-icon="mdi-lock-check"
              :rules="passwordConfirmRules"
              :disabled="passwordLoading"
              variant="outlined"
              density="comfortable"
              required
              class="mt-2"
            ></v-text-field>
            
            <!-- Hata Mesajı -->
            <v-alert
              v-if="passwordError"
              type="error"
              variant="tonal"
              class="mb-4"
              closable
              @click:close="passwordError = ''"
            >
              <template v-slot:title>
                Hata!
              </template>
              {{ passwordError }}
            </v-alert>
            
            <!-- Şifre Gücü Göstergesi -->
            <div v-if="password" class="mb-4">
              <div class="d-flex align-center mb-1">
                <span class="text-caption mr-2">Şifre Gücü:</span>
                <span class="text-caption font-weight-bold">{{ passwordStrengthText }}</span>
              </div>
              <v-progress-linear
                :model-value="passwordStrength"
                :color="passwordStrengthColor"
                height="8"
                rounded
              ></v-progress-linear>
            </div>
            
            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="passwordLoading"
              :disabled="passwordLoading || !password || !passwordConfirm"
              class="mt-2"
            >
              <v-icon start>mdi-key</v-icon>
              {{ passwordLoading ? 'Ayarlanıyor...' : 'Şifreyi Belirle ve Giriş Yap' }}
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>

      <!-- Otomatik Giriş Başarılı -->
      <v-card v-else-if="autoLoggedIn" class="pa-8 text-center">
        <v-icon size="64" color="success" class="mb-3">mdi-party-popper</v-icon>
        <h2 class="text-h4 mb-3">Hesabınız Hazır!</h2>
        <p class="text-h6 text-medium-emphasis mb-4">
          Şifreniz başarıyla belirlendi ve otomatik olarak giriş yaptınız.
        </p>
        
        <v-progress-linear
          indeterminate
          color="primary"
          class="mb-4"
        ></v-progress-linear>
        
        <p class="text-medium-emphasis">
          <v-icon size="small" class="mr-1">mdi-arrow-right</v-icon>
          Yönlendiriliyorsunuz...
        </p>
        
        <v-btn
          color="primary"
          variant="outlined"
          class="mt-4"
          @click="goToProfile"
        >
          <v-icon start>mdi-account</v-icon>
          Hemen Profile Git
        </v-btn>
      </v-card>

      <!-- Doğrulama Başarısız -->
      <v-card v-else class="pa-6">
        <v-card-title class="text-center flex-column">
          <v-icon size="64" color="error" class="mb-3">mdi-close-circle</v-icon>
          <span class="text-h4">Doğrulama Başarısız</span>
        </v-card-title>
        
        <v-card-text class="text-center">
          <v-alert
            type="error"
            variant="tonal"
            class="mb-4"
          >
            {{ errorMessage }}
          </v-alert>
          
          <p class="text-medium-emphasis mb-4">
            Doğrulama linki geçersiz veya süresi dolmuş olabilir.
          </p>
          
          <v-btn
            to="/register"
            color="primary"
            size="large"
            block
          >
            <v-icon start>mdi-account-plus</v-icon>
            Tekrar Kayıt Ol
          </v-btn>
          
          <v-btn
            to="/"
            variant="text"
            class="mt-2"
            block
          >
            Ana Sayfaya Dön
          </v-btn>
        </v-card-text>
      </v-card>
      
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient, { API_ENDPOINTS } from '../config/api';

const route = useRoute();
const router = useRouter();
const token = route.params.token as string;

// State'ler
const loading = ref(true);
const success = ref(false);
const autoLoggedIn = ref(false);
const errorMessage = ref('');

// Şifre belirleme state'leri
const password = ref('');
const passwordConfirm = ref('');
const showPassword = ref(false);
const passwordError = ref('');
const passwordLoading = ref(false);
const passwordSet = ref(false);

// Validasyon kuralları
const passwordRules = [
  (v: string) => !!v || 'Şifre zorunludur',
  (v: string) => (v && v.length >= 6) || 'Şifre en az 6 karakter olmalıdır',
  (v: string) => (v && v.length <= 128) || 'Şifre çok uzun',
];

const passwordConfirmRules = [
  (v: string) => !!v || 'Şifre tekrarı zorunludur',
  (v: string) => v === password.value || 'Şifreler eşleşmiyor',
];

// Şifre gücü hesaplama
const passwordStrength = computed(() => {
  if (!password.value) return 0;
  
  let strength = 0;
  
  // Uzunluk kontrolü
  if (password.value.length >= 6) strength += 20;
  if (password.value.length >= 8) strength += 10;
  if (password.value.length >= 12) strength += 10;
  
  // Karakter çeşitliliği
  if (/[a-z]/.test(password.value)) strength += 15;  // Küçük harf
  if (/[A-Z]/.test(password.value)) strength += 15;  // Büyük harf
  if (/[0-9]/.test(password.value)) strength += 15;  // Rakam
  if (/[^a-zA-Z0-9]/.test(password.value)) strength += 15;  // Özel karakter
  
  return Math.min(strength, 100);
});

const passwordStrengthColor = computed(() => {
  if (passwordStrength.value < 30) return 'error';
  if (passwordStrength.value < 60) return 'warning';
  if (passwordStrength.value < 80) return 'info';
  return 'success';
});

const passwordStrengthText = computed(() => {
  if (passwordStrength.value < 30) return 'Zayıf';
  if (passwordStrength.value < 60) return 'Orta';
  if (passwordStrength.value < 80) return 'İyi';
  return 'Güçlü';
});

onMounted(async () => {
  await verifyEmail();
});

const verifyEmail = async () => {
  try {
    const response = await apiClient.get(API_ENDPOINTS.VERIFY_EMAIL(token));
    
    if (response.data.message) {
      success.value = true;
      loading.value = false;
    }
  } catch (error: any) {
    loading.value = false;
    
    if (error.response?.data?.error) {
      errorMessage.value = error.response.data.error;
    } else {
      errorMessage.value = 'Doğrulama sırasında bir hata oluştu.';
    }
    
    console.error('Doğrulama hatası:', error);
  }
};

const handleSetPassword = async () => {
  passwordError.value = '';
  
  // Validasyon
  if (!password.value || password.value.length < 6) {
    passwordError.value = 'Şifre en az 6 karakter olmalıdır.';
    return;
  }
  
  if (password.value !== passwordConfirm.value) {
    passwordError.value = 'Şifreler eşleşmiyor.';
    return;
  }
  
  passwordLoading.value = true;
  
  try {
    const response = await apiClient.post(
      API_ENDPOINTS.SET_PASSWORD(token),
      { password: password.value }
    );
    
    if (response.data.token) {
      // Token'ı kaydet
      localStorage.setItem('token', response.data.token);
      apiClient.defaults.headers.common['Authorization'] = `Token ${response.data.token}`;
      
      // Başarılı - otomatik giriş
      passwordSet.value = true;
      autoLoggedIn.value = true;
      
      // 2 saniye sonra profile sayfasına yönlendir
      setTimeout(() => {
        router.push('/profile');
      }, 2000);
    }
  } catch (error: any) {
    console.error('Şifre ayarlama hatası:', error);
    
    if (error.response?.data?.error) {
      passwordError.value = error.response.data.error;
    } else {
      passwordError.value = 'Şifre belirlenirken bir hata oluştu. Lütfen tekrar deneyin.';
    }
  } finally {
    passwordLoading.value = false;
  }
};

const goToProfile = () => {
  router.push('/profile');
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

/* Animasyon */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-card {
  animation: fadeIn 0.5s ease-out;
}

/* Progress bar rengi */
:deep(.v-progress-linear__determinate) {
  transition: width 0.3s ease;
}
</style>