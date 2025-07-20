import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { initializeCapacitor } from "./capacitor.js";
import { getCurrentPlatform, PLATFORMS } from "./utils/platform.js";

// Initialize Capacitor if running in Capacitor environment
if (getCurrentPlatform() === PLATFORMS.CAPACITOR) {
  initializeCapacitor().catch(console.error);
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
