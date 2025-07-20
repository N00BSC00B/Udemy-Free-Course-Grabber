// src/capacitor.js
import { App } from "@capacitor/app";
import { Network } from "@capacitor/network";
import { Device } from "@capacitor/device";

let isCapacitorReady = false;
let deviceInfo = null;
let networkStatus = null;

/**
 * Initialize Capacitor plugins and listeners
 */
export async function initializeCapacitor() {
  if (!window.Capacitor || isCapacitorReady) {
    return;
  }

  try {
    // Get device information
    deviceInfo = await Device.getInfo();
    console.log("Device Info:", deviceInfo);

    // Get initial network status
    networkStatus = await Network.getStatus();
    console.log("Network Status:", networkStatus);

    // Listen for network changes
    Network.addListener("networkStatusChange", (status) => {
      networkStatus = status;
      console.log("Network status changed:", status);

      // Dispatch custom event for app to handle
      window.dispatchEvent(
        new CustomEvent("networkStatusChange", {
          detail: status,
        })
      );
    });

    // Listen for app state changes
    App.addListener("appStateChange", ({ isActive }) => {
      console.log("App state changed. Is active:", isActive);

      // Dispatch custom event for app to handle
      window.dispatchEvent(
        new CustomEvent("appStateChange", {
          detail: { isActive },
        })
      );
    });

    // Handle back button on Android
    if (deviceInfo.platform === "android") {
      App.addListener("backButton", ({ canGoBack }) => {
        if (!canGoBack) {
          App.exitApp();
        } else {
          window.history.back();
        }
      });
    }

    isCapacitorReady = true;
    console.log("Capacitor initialized successfully");
  } catch (error) {
    console.error("Failed to initialize Capacitor:", error);
  }
}

/**
 * Get device information
 */
export function getDeviceInfo() {
  return deviceInfo;
}

/**
 * Get current network status
 */
export function getNetworkStatus() {
  return networkStatus;
}

/**
 * Check if device is online
 */
export function isOnline() {
  return networkStatus ? networkStatus.connected : navigator.onLine;
}

/**
 * Get platform name
 */
export function getPlatformName() {
  return deviceInfo ? deviceInfo.platform : "unknown";
}

/**
 * Check if running on mobile
 */
export function isMobileDevice() {
  return deviceInfo ? ["android", "ios"].includes(deviceInfo.platform) : false;
}
