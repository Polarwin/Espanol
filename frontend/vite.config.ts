import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync } from 'node:fs'

const lanHttps = process.env.VITE_LAN_HTTPS === 'true'
const certDir = process.env.VITE_LAN_CERT_DIR ?? '/home/justin/Projects/Espanol/.certs'
const certFile = process.env.VITE_LAN_CERT_FILE ?? `${certDir}/lan-cert.pem`
const keyFile = process.env.VITE_LAN_KEY_FILE ?? `${certDir}/lan-key.pem`

const httpsOptions = lanHttps ? {
  key: readFileSync(keyFile),
  cert: readFileSync(certFile),
} : undefined
const apiProxy = {
  '/api': 'http://localhost:8011',
  '/media': 'http://localhost:8011',
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: lanHttps ? 5174 : 5173,
    https: httpsOptions,
    allowedHosts: ['espanol.justinrecipes.duckdns.org'],
    proxy: apiProxy,
  },
})
