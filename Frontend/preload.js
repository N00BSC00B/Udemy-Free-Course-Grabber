// preload.js
const { contextBridge, ipcRenderer } = require("electron");

// Expose a controlled API to the renderer process (your React app)
contextBridge.exposeInMainWorld("electronAPI", {
  // This function can now be called from React via `window.electronAPI.fetchCourses`
  fetchCourses: (options) => ipcRenderer.invoke("fetch-courses", options),

  // Window controls
  windowMinimize: () => ipcRenderer.invoke("window-minimize"),
  windowMaximize: () => ipcRenderer.invoke("window-maximize"),
  windowClose: () => ipcRenderer.invoke("window-close"),

  // Open external links in default browser
  openExternal: (url) => ipcRenderer.invoke("open-external", url),
});
