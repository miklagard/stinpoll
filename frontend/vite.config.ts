import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/media': 'http://localhost:8000',
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 1000, // Uyarı limitini 1MB'a çıkar
    
    rollupOptions: {
      output: {
        // Manuel chunk bölme
        manualChunks(id) {
          // Vuetify'ı parçalara ayır
          if (id.includes('vuetify/lib')) {
            return 'vuetify-lib';
          }
          if (id.includes('vuetify')) {
            return 'vuetify';
          }
          
          // Vue çekirdeğini ayır
          if (id.includes('vue/dist') || id.includes('vue/index')) {
            return 'vue-core';
          }
          
          // Vue Router
          if (id.includes('vue-router')) {
            return 'vue-router';
          }
          
          // Axios
          if (id.includes('axios')) {
            return 'axios';
          }
          
          // Material Design Icons
          if (id.includes('@mdi')) {
            return 'material-icons';
          }
          
          // Diğer node_modules
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
        
        // Chunk isimlendirme
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    
    // Minify ayarları
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Production'da console.log'ları kaldır
        drop_debugger: true,
      },
    },
  },
  
  // Bundle analizi için (opsiyonel)
  // plugins: [vue(), visualizer()],
});