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
    chunkSizeWarningLimit: 1000,
    
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('vuetify/lib')) return 'vuetify-lib';
          if (id.includes('vuetify')) return 'vuetify';
          if (id.includes('vue/dist') || id.includes('vue/index')) return 'vue-core';
          if (id.includes('vue-router')) return 'vue-router';
          if (id.includes('axios')) return 'axios';
          if (id.includes('@mdi')) return 'material-icons';
          if (id.includes('node_modules')) return 'vendor';
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    
    // 'terser' yazım düzeltmesi (isterseniz 'esbuild' de kullanabilirsiniz)
    minify: 'esbuild',  // veya 'terser' (terser kurulu olmalı)
  },
});