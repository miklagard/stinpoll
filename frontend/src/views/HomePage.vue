<template>
  <div>
    <!-- Hero Section -->
    <v-sheet color="primary" rounded="lg" class="pa-8 mb-8 text-center hero-section">
      <div class="lemon-icon mb-4">🍋</div>
      <h1 class="text-h2 font-weight-bold mb-4">Dünyanın En Naif Eşleştirme Platformu</h1>
      <p class="text-h6 mb-6 opacity-80">Sizleri eşleştirip müşteri kaybetmeyi hedefliyoruz</p>
      
      <div v-if="!isAuthenticated" class="d-flex gap-4 justify-center flex-wrap">
        <v-btn to="/register" color="white" variant="flat" size="large" class="px-8 mb-2">
          <v-icon start>mdi-account-plus</v-icon>
          Hemen Kayıt Ol
        </v-btn>
        <v-btn to="/login" variant="outlined" color="white" size="large" class="px-8 mb-2">
          <v-icon start>mdi-login</v-icon>
          Giriş Yap
        </v-btn>
      </div>
      
      <div v-else class="d-flex gap-4 justify-center flex-wrap">
        <v-btn to="/profile" color="white" variant="flat" size="large" class="px-8 mb-2">
          <v-icon start>mdi-account</v-icon>
          Profilime Git
        </v-btn>
        <v-btn @click="handleLogout" color="error" variant="flat" size="large" class="px-8 mb-2">
          <v-icon start>mdi-logout</v-icon>
          Çıkış Yap
        </v-btn>
      </div>
    </v-sheet>

    <!-- Hoş geldin mesajı (giriş yapmış kullanıcılar için) -->
    <v-alert
      v-if="isAuthenticated"
      type="success"
      variant="tonal"
      class="mb-6"
    >
      🍋 Hoş geldiniz! Profilinizi düzenleyebilir veya eşleşme sürecini başlatabilirsiniz.
    </v-alert>

    <!-- Nasıl Çalışır? -->
    <v-card class="mb-8 pa-6">
      <h2 class="text-h4 text-center mb-6">🍋 Nasıl Çalışır?</h2>
      
      <v-timeline side="end" density="compact">
        <v-timeline-item
          v-for="(step, index) in steps"
          :key="index"
          :dot-color="step.color"
          size="small"
        >
          <v-card :color="step.color" theme="dark" class="pa-4">
            <h3 class="text-h6 mb-2">{{ step.title }}</h3>
            <p class="text-body-1">{{ step.description }}</p>
          </v-card>
        </v-timeline-item>
      </v-timeline>
    </v-card>

    <!-- Değerlerimiz -->
    <h2 class="text-h4 text-center mb-6">🍋 Değerlerimiz</h2>
    <v-row class="mb-8">
      <v-col cols="12" md="4" v-for="(value, index) in values" :key="index">
        <v-card height="100%" class="pa-6 text-center value-card">
          <div class="value-icon mb-4">{{ value.emoji }}</div>
          <h3 class="text-h5 mb-3">{{ value.title }}</h3>
          <p class="text-body-1 text-medium-emphasis">{{ value.description }}</p>
        </v-card>
      </v-col>
    </v-row>

    <!-- Süreç Detayları -->
    <v-card class="mb-8 pa-6 process-card">
      <h2 class="text-h4 text-center mb-6">🍋 Tanışma Süreci</h2>
      
      <v-row>
        <v-col cols="12" md="6" v-for="(detail, index) in processDetails" :key="index">
          <v-card variant="outlined" class="pa-4 mb-4 h-100">
            <div class="d-flex align-start">
              <v-avatar :color="detail.color" size="48" class="mr-4">
                <span class="text-h5 text-white">{{ index + 1 }}</span>
              </v-avatar>
              <div>
                <h3 class="text-h6 mb-2">{{ detail.title }}</h3>
                <p class="text-body-1 text-medium-emphasis">{{ detail.description }}</p>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-card>

    <!-- Geri Bildirim Vurgusu -->
    <v-card color="secondary" theme="dark" class="pa-8 text-center mb-8">
      <div class="text-h2 mb-4">📝</div>
      <h2 class="text-h4 mb-4">Geri Bildirimleriniz Bizim İçin Değerli</h2>
      <p class="text-h6 mb-4 opacity-90">
        Tanıştığınız kişi ile ilgili deneyimlerinizi paylaşmanız, 
        platformumuzu daha iyi hale getirmemize yardımcı olur.
      </p>
      <p class="text-body-1 opacity-80">
        Her geri bildirim, bir sonraki eşleşmenin daha sağlıklı olmasını sağlar.
      </p>
    </v-card>

    <!-- Alt CTA -->
    <div v-if="!isAuthenticated" class="text-center mb-8">
      <h2 class="text-h4 mb-4">🍋 Haydi Başlayalım!</h2>
      <p class="text-h6 text-medium-emphasis mb-6">
        Naif bir tanışma deneyimi için hemen kaydolun.
      </p>
      <v-btn to="/register" color="primary" size="x-large" class="px-12">
        <v-icon start>mdi-account-plus</v-icon>
        Ücretsiz Kayıt Ol
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '../config/api';

const router = useRouter();

const steps = [
  {
    color: 'primary',
    title: '1. Profil Oluştur',
    description: 'Kendini tanıt, fotoğraflarını ekle, tercihlerini belirle.'
  },
  {
    color: 'secondary',
    title: '2. Eşleşme Önerisi',
    description: 'Sistem sana uygun profilleri önerir. İki taraf da ilgi gösterirse süreç başlar.'
  },
  {
    color: 'accent',
    title: '3. Zoom Toplantısı',
    description: 'Karşılıklı uygun bir zamanda, platform üzerinden güvenli bir Zoom görüşmesi.'
  },
  {
    color: 'success',
    title: '4. Bağlantı Paylaşımı',
    description: 'Görüşme sonrası iki taraf da kabul ederse iletişim bilgileri paylaşılır.'
  }
];

const values = [
  {
    emoji: '🔒',
    title: 'Gizlilik',
    description: 'Bilgileriniz diğer kullanıcılarla onayınız olmadan asla paylaşılmaz.'
  },
  {
    emoji: '🐢',
    title: 'Yavaş ve Kontrollü',
    description: 'Sola sağa kaydırıp katalogtan "ürün" seçmece yok. Tanışma süreci uzun ve anlamlı.'
  },
  {
    emoji: '🤝',
    title: 'Karşılıklı Saygı',
    description: 'Her adımda iki tarafın da onayı gerekir. Zorla eşleştirme yok.'
  }
];

const processDetails = [
  {
    color: 'primary',
    title: 'Profil Onayı',
    description: 'Her iki taraf da birbirinin profilini görüp onaylamadan süreç ilerlemez.'
  },
  {
    color: 'secondary',
    title: 'Zoom Entegrasyonu',
    description: 'Platform üzerinden güvenli Zoom toplantısı otomatik oluşturulur.'
  },
  {
    color: 'success',
    title: 'Geri Bildirim Sistemi',
    description: 'Tanışma sonrası deneyiminizi paylaşarak topluluğa katkıda bulunun.'
  },
  {
    color: 'accent',
    title: 'Sürekli İyileştirme',
    description: 'Geri bildirimlerle eşleştirme algoritmamızı sürekli geliştiriyoruz.'
  }
];

const isAuthenticated = computed(() => !!localStorage.getItem('token'));

const handleLogout = () => {
  localStorage.removeItem('token');
  delete apiClient.defaults.headers.common['Authorization'];
  router.push('/');
};
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 50%, #81C784 100%);
  border-radius: 16px !important;
}

.lemon-icon {
  font-size: 4rem;
  animation: lemonBounce 2s ease-in-out infinite;
}

@keyframes lemonBounce {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-5deg) scale(1.05); }
  75% { transform: rotate(5deg) scale(1.05); }
}

.value-card {
  transition: transform 0.3s ease;
  border-radius: 12px;
}

.value-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.value-icon {
  font-size: 3rem;
}

.process-card {
  background: linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%);
}

.opacity-80 {
  opacity: 0.9;
}

.opacity-90 {
  opacity: 0.9;
}

.h-100 {
  height: 100%;
}

/* Responsive */
@media (max-width: 600px) {
  .hero-section {
    padding: 2rem 1rem !important;
  }
  
  .hero-section h1 {
    font-size: 1.8rem !important;
  }
  
  .lemon-icon {
    font-size: 3rem;
  }
}
</style>