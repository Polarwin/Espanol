import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync } from 'node:fs'

const lanHttps = process.env.VITE_LAN_HTTPS === 'true'
const certDir = process.env.VITE_LAN_CERT_DIR ?? '/home/justin/Projects/Espanol/.certs'

const httpsOptions = lanHttps ? {
  key: readFileSync(`${certDir}/192.168.0.9+2-key.pem`),
  cert: readFileSync(`${certDir}/192.168.0.9+2.pem`),
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
  // Production web services run `vite preview` on the built dist/ bundle;
  // keep this in sync with `server` above (no HMR/watching here).
  preview: {
    host: '0.0.0.0',
    port: lanHttps ? 5174 : 5173,
    https: httpsOptions,
    allowedHosts: ['espanol.justinrecipes.duckdns.org'],
    proxy: apiProxy,
  },
})
