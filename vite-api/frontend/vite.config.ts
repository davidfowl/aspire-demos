import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/weatherforecast': {
        target: process.env.BACKEND_URL,
        changeOrigin: true
      }
    }
  }
})
