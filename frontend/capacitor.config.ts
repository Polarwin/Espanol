import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'org.duckdns.justinrecipes.espanol',
  appName: '¡Vamos! Español',
  webDir: 'dist',
  server: {
    url: 'https://espanol.justinrecipes.duckdns.org',
    cleartext: false,
  },
}

export default config
