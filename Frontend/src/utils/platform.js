// src/utils/platform.js

/**
 * Utility functions for platform detection and handling
 */

export const PLATFORMS = {
  ELECTRON: "electron",
  CAPACITOR: "capacitor",
  WEB: "web",
};

/**
 * Detects the current platform
 * @returns {string} - The platform name
 */
export function getCurrentPlatform() {
  if (window.electronAPI) {
    return PLATFORMS.ELECTRON;
  }
  if (window.Capacitor) {
    return PLATFORMS.CAPACITOR;
  }
  return PLATFORMS.WEB;
}

/**
 * Checks if the app is running in Electron
 * @returns {boolean}
 */
export function isElectron() {
  return getCurrentPlatform() === PLATFORMS.ELECTRON;
}

/**
 * Checks if the app is running in Capacitor
 * @returns {boolean}
 */
export function isCapacitor() {
  return getCurrentPlatform() === PLATFORMS.CAPACITOR;
}

/**
 * Checks if the app is running in a web browser
 * @returns {boolean}
 */
export function isWeb() {
  return getCurrentPlatform() === PLATFORMS.WEB;
}

/**
 * Checks if the app is running on a mobile device (Capacitor context)
 * @returns {boolean}
 */
export function isMobile() {
  if (isCapacitor() && window.Capacitor) {
    return window.Capacitor.getPlatform() !== "web";
  }
  return false;
}

/**
 * Gets platform-specific configuration
 * @returns {object}
 */
export function getPlatformConfig() {
  const platform = getCurrentPlatform();

  return {
    platform,
    supportsFileSystem: platform === PLATFORMS.ELECTRON,
    supportsNativeSharing: platform === PLATFORMS.CAPACITOR,
    supportsSystemTheme: platform !== PLATFORMS.WEB,
    isMobile: isMobile(),
    hasBackButton: platform === PLATFORMS.CAPACITOR && isMobile(),
  };
}
