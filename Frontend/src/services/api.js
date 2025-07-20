// src/services/api.js
import { Browser } from "@capacitor/browser";
import { Network } from "@capacitor/network";

const SORT_MAP = {
  Date: "sale_start",
  Popularity: "views",
  Rating: "rating",
  Duration: "lectures",
};

/**
 * Detects the current platform (electron, capacitor, or web)
 * @returns {string} - The platform name
 */
function getPlatform() {
  if (window.electronAPI) {
    return "electron";
  }
  if (window.Capacitor) {
    return "capacitor";
  }
  return "web";
}

/**
 * Fetches courses using the appropriate method based on the platform
 * @param {object} options - The query options.
 * @returns {Promise<object>} - The API response data.
 */
export async function fetchCourses(options) {
  const platform = getPlatform();

  switch (platform) {
    case "electron":
      return await fetchCoursesElectron(options);
    case "capacitor":
      return await fetchCoursesCapacitor(options);
    case "web":
      return await fetchCoursesWeb(options);
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}

/**
 * Fetches courses using Electron IPC
 */
async function fetchCoursesElectron(options) {
  const result = await window.electronAPI.fetchCourses(options);
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.error);
  }
}

/**
 * Fetches courses using Capacitor HTTP plugin or fetch API
 */
async function fetchCoursesCapacitor(options) {
  // Check network connectivity first
  const networkStatus = await Network.getStatus();
  if (!networkStatus.connected) {
    throw new Error("No network connection available");
  }

  return await fetchCoursesWeb(options);
}

/**
 * Fetches courses using standard fetch API (for web and as fallback)
 */
async function fetchCoursesWeb(options) {
  const { page = 1, category = "All", sort = "Date", search = "" } = options;

  const params = new URLSearchParams({
    page,
    limit: 20,
    sortBy: SORT_MAP[sort] || "sale_start",
    store: "Udemy",
    freeOnly: "true",
  });

  if (category && category !== "All") {
    params.append("category", category);
  }
  if (search) {
    params.append("search", search);
  }

  const url = `https://cdn.real.discount/api/courses?${params.toString()}`;

  try {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed with status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    throw new Error(`Failed to fetch courses: ${error.message}`);
  }
}

/**
 * Opens a URL using the appropriate method based on the platform
 * @param {string} url - The URL to open
 */
export async function openUrl(url) {
  const platform = getPlatform();

  switch (platform) {
    case "electron":
      if (window.electronAPI && window.electronAPI.openExternal) {
        await window.electronAPI.openExternal(url);
      } else {
        window.open(url, "_blank");
      }
      break;
    case "capacitor":
      await Browser.open({ url });
      break;
    case "web":
      window.open(url, "_blank");
      break;
  }
}
