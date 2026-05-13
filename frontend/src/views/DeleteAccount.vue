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
        <h2 class="text-h5">Doğrulanıyor...</h2>
      </v-card>

      <!-- Onay Formu -->
      <v-card v-else-if="!deleted && !error" class="pa-6">
        <v-card-title class="text-center flex-column">
          <v-icon size="64" color="error" class="mb-3">mdi-alert-circle</v-icon>
          <span class="text-h4">Hesabını Sil</span>
        </v-card-title>
        
        <v-card-text class="text-center">
          <v-alert
            type="warning"
            variant="tonal"
            class="mb-4"
          >
            <template v-slot:title>
              ⚠️ Bu işlem geri alınamaz!
            </template>
            <p class="mb-0">
              Hesabınızı sildiğinizde tüm verileriniz (profil, fotoğraflar, eşleşmeler) 
              <strong>kalıcı olarak</strong> silinecektir.
            </p>
          </v-alert>
          
          <v-list class="mb-4 text-left">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="error">mdi-close-circle</v-icon>
              </template>
              <v-list-item-title>Profiliniz silinecek</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="error">mdi-close-circle</v-icon>
              </template>
              <v-list-item-title>Fotoğraflarınız silinecek</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="error">mdi-close-circle</v-icon>
              </template>
              <v-list-item-title>Tüm verileriniz kalıcı olarak kaldırılacak</v-list-item-title>
            </v-list-item>
          </v-list>
          
          <v-checkbox
            v-model="confirmed"
            color="error"
            label="Hesabımı silmek istediğimi onaylıyorum"
            class="mb-4"
          ></v-checkbox>
          
          <div class="d-flex gap-2">
            <v-btn
              to="/"
              color="primary"
              variant="outlined"
              size="large"
              class="flex-1"
            >
              <v-icon start>mdi-home</v-icon>
              Vazgeç
            </v-btn>
            
            <v-btn
              @click="handleDelete"
              color="error"
              size="large"
              :loading="deleting"
              :disabled="!confirmed || deleting"
              class="flex-1"
            >
              <v-icon start>mdi-delete</v-icon>
              {{ deleting ? 'Siliniyor...' : 'Hesabımı Sil' }}
            </v-btn>
          </div>
        </v-card-text>
      </v-card>

      <!-- Başarılı -->
      <v-card v-else-if="deleted" class="pa-8 text-center">
        <v-icon size="64" color="success" class="mb-3">mdi-check-circle</v-icon>
        <h2 class="text-h4 mb-4">Hesabınız Silindi</h2>
        <p class="text-h6 text-medium-emphasis mb-4">
          Hesabınız ve tüm verileriniz başarıyla silindi.
        </p>
        <p class="text-medium-emphasis mb-6">
          Bizi tercih ettiğiniz için teşekkür ederiz. 🍋
        </p>
        <v-btn to="/" color="primary" size="large">
          <v-icon start>mdi-home</v-icon>
          Ana Sayfaya Dön
        </v-btn>
      </v-card>

      <!-- Hata -->
      <v-card v-else class="pa-6 text-center">
        <v-icon size="64" color="error" class="mb-3">mdi-close-circle</v-icon>
        <h2 class="text-h4 mb-4">Bir Hata Oluştu</h2>
        <v-alert type="error" variant="tonal" class="mb-4">
          {{ error }}
        </v-alert>
        <v-btn to="/" color="primary" size="large">
          Ana Sayfaya Dön
        </v-btn>
      </v-card>
      
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '../config/api';

const route = useRoute();
const token = route.params.token as string;

const loading = ref(true);
const deleting = ref(false);
const deleted = ref(false);
const confirmed = ref(false);
const error = ref('');

// Sayfa yüklendiğinde token'ı doğrula
const init = async () => {
  try {
    // Token'ın geçerli olup olmadığını kontrol et (opsiyonel)
    await apiClient.get(`/verify/${token}/`);
    loading.value = false;
  } catch (err: any) {
    loading.value = false;
    // Token geçersiz olsa bile silme işlemine izin ver
    // Sadece bilgilendirme amaçlı
    console.log('Token kontrolü:', err.response?.data);
  }
};

const handleDelete = async () => {
  if (!confirmed.value) return;
  
  deleting.value = true;
  error.value = '';
  
  try {
    await apiClient.delete(`/delete-account/${token}/`);
    deleted.value = true;
  } catch (err: any) {
    error.value = err.response?.data?.error || 
      'Hesap silinirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.';
    console.error('Silme hatası:', err);
  } finally {
    deleting.value = false;
  }
};

init();
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.flex-1 {
  flex: 1;
}
</style>