import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync } from 'node:fs'

const lanHttps = process.env.VITE_LAN_HTTPS === 'true'
const certDir = process.env.VITE_LAN_CERT_DIR ?? '/home/justin/Projects/nextERP/certs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: lanHttps ? 5174 : 5173,
    https: lanHttps ? {
      key: readFileSync(`${certDir}/192.168.0.9+2-key.pem`),
      cert: readFileSync(`${certDir}/192.168.0.9+2.pem`),
    } : undefined,
    allowedHosts: ['espanol.justinrecipes.duckdns.org'],
    proxy: {
      '/api': 'http://localhost:8011',
      '/media': 'http://localhost:8011',
    },
  },
})
