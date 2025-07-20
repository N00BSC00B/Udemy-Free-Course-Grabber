import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.udemy.course.grabber',
  appName: 'Udemy Free Course Grabber',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    allowNavigation: [
      'https://cdn.real.discount',
      'https://*.udemy.com',
      'https://udemy.com'
    ]
  },
  plugins: {
    Browser: {
      presentationStyle: 'popover'
    },
    Network: {
      // Enable network monitoring
    },
    App: {
      // Handle app state changes
    }
  },
  android: {
    allowMixedContent: true,
    captureInput: true
  }
};

export default config;
