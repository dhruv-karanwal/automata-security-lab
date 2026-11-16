import { defineConfig, mergeConfig } from 'vite';
import baseConfig from './vite.config.ts';

// Local fallback while another application occupies port 3000.
export default defineConfig((env) => mergeConfig(baseConfig(env), {
  define: { 'import.meta.env.VITE_API_BASE_URL': JSON.stringify('http://localhost:3001') },
  server: {
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
}));
