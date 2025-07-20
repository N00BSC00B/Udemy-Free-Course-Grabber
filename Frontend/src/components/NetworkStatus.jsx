// src/components/NetworkStatus.jsx
import { useState, useEffect } from "react";
import { Wifi, WifiOff } from "lucide-react";
import { getCurrentPlatform, PLATFORMS } from "../utils/platform";
import { isOnline as getCapacitorOnlineStatus } from "../capacitor";

const NetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [showStatus, setShowStatus] = useState(false);
  const platform = getCurrentPlatform();

  useEffect(() => {
    const updateOnlineStatus = () => {
      const online =
        platform === PLATFORMS.CAPACITOR
          ? getCapacitorOnlineStatus()
          : navigator.onLine;

      setIsOnline(online);

      // Show status temporarily when it changes
      setShowStatus(true);
      const timer = setTimeout(() => setShowStatus(false), 3000);
      return () => clearTimeout(timer);
    };

    // Initial check
    updateOnlineStatus();

    if (platform === PLATFORMS.CAPACITOR) {
      // Listen for Capacitor network events
      const handleNetworkChange = (event) => {
        setIsOnline(event.detail.connected);
        setShowStatus(true);
        setTimeout(() => setShowStatus(false), 3000);
      };

      window.addEventListener("networkStatusChange", handleNetworkChange);
      return () =>
        window.removeEventListener("networkStatusChange", handleNetworkChange);
    } else {
      // Listen for browser network events
      window.addEventListener("online", updateOnlineStatus);
      window.addEventListener("offline", updateOnlineStatus);
      return () => {
        window.removeEventListener("online", updateOnlineStatus);
        window.removeEventListener("offline", updateOnlineStatus);
      };
    }
  }, [platform]);

  if (!showStatus && isOnline) {
    return null; // Don't show anything when online and not changing
  }

  return (
    <div
      className={`fixed top-4 right-4 z-50 transition-all duration-300 ${
        showStatus ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2"
      }`}
    >
      <div
        className={`alert ${
          isOnline ? "alert-success" : "alert-error"
        } shadow-lg`}
      >
        <div className="flex items-center gap-2">
          {isOnline ? (
            <Wifi className="w-5 h-5" />
          ) : (
            <WifiOff className="w-5 h-5" />
          )}
          <span className="text-sm font-medium">
            {isOnline ? "Back online" : "No internet connection"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default NetworkStatus;
