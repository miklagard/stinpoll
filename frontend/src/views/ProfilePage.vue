<template>
  <div>
    <!-- Yükleniyor -->
    <div v-if="loading" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="mt-4">Profil yükleniyor...</p>
    </div>

    <!-- Profil Görüntüleme -->
    <v-card v-else-if="profileData && !isEditing" class="mb-4">
      <v-card-item>
        <template v-slot:prepend>
          <!-- Ana fotoğrafı göster -->
          <v-avatar v-if="getPrimaryPhoto()" size="80">
            <v-img :src="getPrimaryPhoto()" cover></v-img>
          </v-avatar>
          <v-avatar v-else color="primary" size="80">
            <v-icon size="40" color="white">mdi-account</v-icon>
          </v-avatar>
        </template>
        
        <v-card-title class="text-h4">{{ profileData.eksisozluk_username }}</v-card-title>
        <v-card-subtitle>{{ profileData.city }} - {{ profileData.age }} yaş</v-card-subtitle>
        
        <template v-slot:append>
          <v-btn color="primary" variant="tonal" @click="startEditing">
            <v-icon start>mdi-pencil</v-icon>
            Düzenle
          </v-btn>
        </template>
      </v-card-item>
      
      <v-divider></v-divider>
      
      <!-- Fotoğraflar -->
      <v-card-text>
        <h3 class="text-h6 mb-3">Fotoğraflar</h3>
        <v-row v-if="profileData.photos && profileData.photos.length > 0">
          <v-col 
            cols="12" sm="6" md="4" 
            v-for="photo in profileData.photos" 
            :key="photo.id"
          >
            <v-card variant="outlined">
              <v-img 
                :src="photo.photo" 
                height="200" 
                cover
                class="align-end"
              >
                <v-chip
                  v-if="photo.is_primary"
                  color="primary"
                  size="small"
                  class="ma-2"
                >
                  Ana Fotoğraf
                </v-chip>
              </v-img>
            </v-card>
          </v-col>
        </v-row>
        <v-alert v-else type="info" variant="tonal" class="mt-2">
          Henüz fotoğraf eklenmemiş.
        </v-alert>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <!-- Bilgiler -->
      <v-card-text>
        <h3 class="text-h6 mb-3">Profil Bilgileri</h3>
        <v-list density="comfortable">
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-email</v-icon>
            </template>
            <v-list-item-title>Email</v-list-item-title>
            <v-list-item-subtitle>{{ profileData.email }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-account</v-icon>
            </template>
            <v-list-item-title>Ekşisözlük</v-list-item-title>
            <v-list-item-subtitle>{{ profileData.eksisozluk_username }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-cake</v-icon>
            </template>
            <v-list-item-title>Yaş</v-list-item-title>
            <v-list-item-subtitle>{{ profileData.age }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-heart</v-icon>
            </template>
            <v-list-item-title>Medeni Durum</v-list-item-title>
            <v-list-item-subtitle>{{ getMaritalStatusText(profileData.marital_status) }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-human-male-female-child</v-icon>
            </template>
            <v-list-item-title>Çocuk</v-list-item-title>
            <v-list-item-subtitle>{{ profileData.has_children ? 'Var' : 'Yok' }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-city</v-icon>
            </template>
            <v-list-item-title>Şehir</v-list-item-title>
            <v-list-item-subtitle>{{ profileData.city }}</v-list-item-subtitle>
          </v-list-item>
          
          <v-list-item>
            <template v-slot:prepend>
              <v-icon color="primary">mdi-star</v-icon>
            </template>
            <v-list-item-title>Dini Görüş</v-list-item-title>
            <v-list-item-subtitle>
              <v-rating
                :model-value="profileData.religious_view"
                max="5"
                readonly
                color="amber"
                density="compact"
                half-increments
              ></v-rating>
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- Profil Düzenleme Formu -->
    <v-card v-else-if="isEditing" class="pa-6">
      <v-card-title class="text-h4 mb-4">
        {{ profileExists ? 'Profili Düzenle' : 'Profil Oluştur' }}
      </v-card-title>
      
      <v-form @submit.prevent="handleSubmit">
        <v-text-field
          v-model="formData.eksisozluk_username"
          label="Ekşisözlük Kullanıcı Adı"
          prepend-inner-icon="mdi-account"
          :rules="[rules.required]"
          required
        ></v-text-field>
        
        <!-- Mevcut Fotoğraflar (Düzenleme modunda) -->
        <div v-if="profileExists && profileData?.photos?.length" class="mb-4">
          <label class="text-subtitle-2 mb-2 d-block">Mevcut Fotoğraflar</label>
          <v-row>
            <v-col 
              cols="6" sm="4" md="3" 
              v-for="photo in profileData.photos" 
              :key="photo.id"
            >
              <v-card variant="outlined" class="position-relative">
                <v-img :src="photo.photo" height="120" cover></v-img>
                <v-btn
                  icon="mdi-delete"
                  size="x-small"
                  color="error"
                  variant="flat"
                  class="position-absolute"
                  style="top: 4px; right: 4px;"
                  @click="markPhotoForDeletion(photo.id)"
                ></v-btn>
                <v-chip
                  v-if="photo.is_primary"
                  color="primary"
                  size="x-small"
                  class="position-absolute"
                  style="bottom: 4px; left: 4px;"
                >
                  Ana
                </v-chip>
              </v-card>
            </v-col>
          </v-row>
        </div>
        
        <!-- Yeni Fotoğraf Ekleme -->
        <v-file-input
          v-model="newPhotos"
          label="Yeni Fotoğraf Ekle"
          accept="image/*"
          multiple
          prepend-inner-icon="mdi-camera-plus"
          :show-size="true"
          :rules="[rules.maxPhotos]"
          hint="En fazla 5 fotoğraf (mevcut + yeni)"
          persistent-hint
          chips
          @update:model-value="onPhotosSelected"
        ></v-file-input>
        
        <!-- Yeni Fotoğraf Önizlemeleri -->
        <v-row v-if="newPhotoPreviews.length > 0" class="mb-4">
          <v-col 
            cols="6" sm="4" md="3" 
            v-for="(preview, index) in newPhotoPreviews" 
            :key="'new-' + index"
          >
            <v-card variant="outlined" class="position-relative">
              <v-img :src="preview" height="120" cover></v-img>
              <v-btn
                icon="mdi-close"
                size="x-small"
                color="error"
                variant="flat"
                class="position-absolute"
                style="top: 4px; right: 4px;"
                @click="removeNewPhoto(index)"
              ></v-btn>
            </v-card>
          </v-col>
        </v-row>
        
        <v-text-field
          v-model.number="formData.age"
          label="Yaş"
          type="number"
          min="18"
          prepend-inner-icon="mdi-cake"
          :rules="[rules.required, rules.minAge]"
          required
        ></v-text-field>
        
        <v-select
          v-model="formData.marital_status"
          label="Medeni Durum"
          :items="maritalStatusOptions"
          prepend-inner-icon="mdi-heart"
          :rules="[rules.required]"
          required
        ></v-select>
        
        <v-checkbox
          v-model="formData.has_children"
          label="Çocuğum var"
          color="primary"
        ></v-checkbox>
        
        <v-text-field
          v-model="formData.city"
          label="Şehir"
          prepend-inner-icon="mdi-city"
          :rules="[rules.required]"
          required
        ></v-text-field>
        
        <div class="mb-4">
          <label class="text-subtitle-2 mb-2 d-block">
            Dini Görüş: {{ formData.religious_view }}/5
          </label>
          <v-slider
            v-model="formData.religious_view"
            min="0"
            max="5"
            step="1"
            thumb-label
            color="primary"
            show-ticks="always"
            tick-size="4"
          ></v-slider>
        </div>
        
        <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable @click:close="error = ''">
          {{ error }}
        </v-alert>
        
        <v-alert v-if="success" type="success" variant="tonal" class="mb-4" closable @click:close="success = ''">
          {{ success }}
        </v-alert>
        
        <div class="d-flex gap-2">
          <v-btn
            v-if="profileExists"
            @click="cancelEditing"
            color="error"
            variant="outlined"
            size="large"
            class="mr-2"
          >
            <v-icon start>mdi-close</v-icon>
            İptal
          </v-btn>
          
          <v-btn
            type="submit"
            color="primary"
            :loading="submitting"
            :disabled="submitting"
            block
            size="large"
          >
            <v-icon start>mdi-content-save</v-icon>
            {{ profileExists ? 'Güncelle' : 'Profili Oluştur' }}
          </v-btn>
        </div>
      </v-form>
    </v-card>

    <!-- Profil yok - oluşturma formu -->
    <v-card v-else-if="!profileExists && !loading" class="pa-6">
      <v-card-title class="text-h4 mb-4">Profil Oluştur</v-card-title>
      <v-alert type="info" variant="tonal" class="mb-4">
        Henüz bir profiliniz yok. Hemen oluşturmak için başlayın!
      </v-alert>
      <v-btn color="primary" size="large" block @click="isEditing = true">
        <v-icon start>mdi-plus</v-icon>
        Profil Oluştur
      </v-btn>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient, { API_ENDPOINTS } from '../config/api';

const router = useRouter();

// State
const loading = ref(true);
const profileExists = ref(false);
const isEditing = ref(false);
const submitting = ref(false);
const error = ref('');
const success = ref('');
const profileData = ref<any>(null);
const newPhotos = ref<File[]>([]);
const photosToDelete = ref<string[]>([]);

// Form data
const formData = reactive({
  eksisozluk_username: '',
  age: 18,
  marital_status: 'bekar',
  has_children: false,
  city: '',
  religious_view: 0
});

// Medeni durum seçenekleri
const maritalStatusOptions = [
  { title: 'Bekar', value: 'bekar' },
  { title: 'Boşanmış', value: 'bosanmis' },
];

// Form kuralları
const rules = {
  required: (v: any) => !!v || 'Bu alan zorunludur',
  minAge: (v: number) => v >= 18 || 'En az 18 yaşında olmalısınız',
  maxPhotos: (v: File[]) => {
    if (!v) return true;
    const existingCount = profileData.value?.photos?.length || 0;
    return (existingCount + v.length - photosToDelete.value.length) <= 5 || 
           'En fazla 5 fotoğraf yükleyebilirsiniz';
  }
};

// Yeni fotoğraf önizlemeleri
const newPhotoPreviews = computed(() => {
  if (!newPhotos.value || newPhotos.value.length === 0) return [];
  return newPhotos.value.map(file => URL.createObjectURL(file));
});

onMounted(() => {
  loadProfile();
});

const getPrimaryPhoto = () => {
  if (!profileData.value?.photos) return null;
  const primary = profileData.value.photos.find((p: any) => p.is_primary);
  if (primary) return primary.photo;
  // Primary yoksa ilk fotoğrafı göster
  if (profileData.value.photos.length > 0) {
    return profileData.value.photos[0].photo;
  }
  return null;
};

const loadProfile = async () => {
  loading.value = true;
  error.value = '';
  
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  try {
    const response = await apiClient.get(API_ENDPOINTS.PROFILES);
    
    console.log('Profil verisi:', response.data);
    
    if (response.data && response.data.count) {
      profileData.value = response.data.results[0];
      profileExists.value = true;
      fillFormData();
    } else {

      profileExists.value = false;
      profileData.value = null;
    }
  } catch (err: any) {
    console.error('Profil yükleme hatası:', err);
    error.value = 'Profil yüklenirken bir hata oluştu.';
    
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      router.push('/login');
    }
  } finally {
    loading.value = false;
  }
};

const fillFormData = () => {
  if (!profileData.value) return;
  
  formData.eksisozluk_username = profileData.value.eksisozluk_username || '';
  formData.age = profileData.value.age || 18;
  formData.marital_status = profileData.value.marital_status || 'bekar';
  formData.has_children = profileData.value.has_children || false;
  formData.city = profileData.value.city || '';
  formData.religious_view = profileData.value.religious_view || 0;
  newPhotos.value = [];
  photosToDelete.value = [];
};

const startEditing = () => {
  isEditing.value = true;
  error.value = '';
  success.value = '';
  fillFormData();
};

const cancelEditing = () => {
  isEditing.value = false;
  error.value = '';
  success.value = '';
  fillFormData();
};

const onPhotosSelected = (files: File | File[]) => {
  console.log('Seçilen fotoğraflar:', files);
};

const removeNewPhoto = (index: number) => {
  newPhotos.value.splice(index, 1);
};

const handleSubmit = async () => {
  error.value = '';
  success.value = '';
  submitting.value = true;
  
  const token = localStorage.getItem('token');
  if (!token) {
    router.push('/login');
    return;
  }
  
  // Validasyon
  if (!formData.eksisozluk_username) {
    error.value = 'Ekşisözlük kullanıcı adı gerekli.';
    submitting.value = false;
    return;
  }
  
  if (!profileExists.value && newPhotos.value.length === 0) {
    error.value = 'En az bir fotoğraf yüklemelisiniz.';
    submitting.value = false;
    return;
  }
  
  if (!formData.age || formData.age < 18) {
    error.value = 'Geçerli bir yaş girin (en az 18).';
    submitting.value = false;
    return;
  }
  
  if (!formData.city) {
    error.value = 'Şehir girin.';
    submitting.value = false;
    return;
  }
  
  const apiFormData = new FormData();
  apiFormData.append('eksisozluk_username', formData.eksisozluk_username);
  apiFormData.append('age', formData.age.toString());
  apiFormData.append('marital_status', formData.marital_status);
  apiFormData.append('has_children', formData.has_children.toString());
  apiFormData.append('city', formData.city);
  apiFormData.append('religious_view', formData.religious_view.toString());
  
  try {
    if (profileExists.value && profileData.value) {
      // Güncelleme
      photosToDelete.value.forEach(id => {
        apiFormData.append('delete_photo_ids', id);
      });
      
      newPhotos.value.forEach(photo => {
        apiFormData.append('new_photos', photo);
      });
    
     const updateResponse = await apiClient.patch(
        API_ENDPOINTS.PROFILE_DETAIL(profileData.value.id),
        apiFormData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );

      console.log('Güncelleme yanıtı:', updateResponse.data);

      success.value = 'Profil başarıyla güncellendi!';
    } else {
      // Yeni oluşturma
      newPhotos.value.forEach(photo => {
        apiFormData.append('uploaded_photos', photo);
      });
      
      await apiClient.post(API_ENDPOINTS.PROFILES, apiFormData,         {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Token ${token}`
          }
      });

      success.value = 'Profil başarıyla oluşturuldu!';
    }
    
    // Başarılı işlem sonrası
    setTimeout(async () => {
      isEditing.value = false;
      await loadProfile();
    }, 1000);
    
  } catch (err: any) {
    console.error('Profil kaydetme hatası:', err.response?.data);
    
    if (err.response?.status === 401) {
      error.value = 'Oturum süreniz dolmuş.';
      localStorage.removeItem('token');
      router.push('/login');
    } else if (err.response?.data) {
      const data = err.response.data;
      if (typeof data === 'object') {
        error.value = Object.values(data).flat().join(', ');
      } else {
        error.value = data.detail || data.error || 'İşlem başarısız';
      }
    } else {
      error.value = 'Sunucuya bağlanılamadı';
    }
  } finally {
    submitting.value = false;
  }
};

const markPhotoForDeletion = (photoId: string) => {
  photosToDelete.value.push(photoId);
  if (profileData.value?.photos) {
    profileData.value.photos = profileData.value.photos.filter(
      (p: any) => p.id !== photoId
    );
  }
};

const getMaritalStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'bekar': 'Bekar',
    'bosanmis': 'Boşanmış'
  };
  return statusMap[status] || status;
};
</script>

<style scoped>
.position-relative {
  position: relative;
}

.position-absolute {
  position: absolute;
}

.v-card-item {
  align-items: center;
}

.gap-2 {
  gap: 0.5rem;
}
</style>