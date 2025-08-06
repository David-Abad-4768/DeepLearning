// vite.config.ts
import tailwindcss from '@tailwindcss/vite';
import basicSsl from '@vitejs/plugin-basic-ssl';
import react from '@vitejs/plugin-react';
import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss(), basicSsl()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: { https: {}, port: 5173, host: 'localhost' },
});
