// electron.js (Dependency-Free Version)
const { app, BrowserWindow, ipcMain, shell } = require("electron");
const path = require("path");
const https = require("https"); // Use Node's built-in HTTPS module

console.log("LOG: Starting electron.js...");

// --- API Fetching Logic (using built-in https) ---
const SORT_MAP = {
  Date: "sale_start",
  Popularity: "views",
  Rating: "rating",
  Duration: "lectures",
};

function fetchCoursesAPI({
  page = 1,
  category = "All",
  sort = "Date",
  search = "",
}) {
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

  // We must wrap the https.get call in a Promise to use it with async/await
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        if (res.statusCode < 200 || res.statusCode >= 300) {
          return reject(
            new Error(`API request failed with status: ${res.statusCode}`)
          );
        }
        let body = "";
        res.on("data", (chunk) => {
          body += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            reject(new Error("Failed to parse JSON response.: " + e.message));
          }
        });
      })
      .on("error", (e) => {
        reject(new Error(`HTTPS Request Error: ${e.message}`));
      });
  });
}

console.log("LOG: API function defined.");

// --- Electron Window Creation ---
function createWindow() {
  console.log("LOG: createWindow() called.");

  // Define icon path for both dev and production
  const iconPath = app.isPackaged
    ? path.join(process.resourcesPath, "assets", "icon.png")
    : path.join(__dirname, "assets", "icon.png");

  console.log(`LOG: Using icon path: ${iconPath}`);

  // Define preload path for both dev and production
  const preloadPath = app.isPackaged
    ? path.join(__dirname, "preload.js")
    : path.join(__dirname, "preload.js");

  console.log(`LOG: Using preload path: ${preloadPath}`);

  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: preloadPath,
      nodeIntegration: false,
      contextIsolation: true,
    },
    icon: iconPath,
    titleBarStyle: "hidden",
    titleBarOverlay: {
      color: "#1f2937",
      symbolColor: "#ffffff",
    },
    frame: false,
    show: false, // Don't show until ready
  });

  console.log("LOG: BrowserWindow created.");

  const appURL = app.isPackaged
    ? `file://${path.join(__dirname, "dist", "index.html")}`
    : "http://localhost:5173";

  console.log(`LOG: Loading URL: ${appURL}`);
  console.log(`LOG: App is packaged: ${app.isPackaged}`);
  console.log(`LOG: __dirname: ${__dirname}`);

  // Check if file exists when packaged
  if (app.isPackaged) {
    const fs = require("fs");
    const indexPath = path.join(__dirname, "dist", "index.html");
    console.log(`LOG: Checking if index.html exists at: ${indexPath}`);
    console.log(`LOG: File exists: ${fs.existsSync(indexPath)}`);
  }

  win.loadURL(appURL).catch((error) => {
    console.error("LOG: Error loading URL:", error);
  });

  // Show window when ready
  win.once("ready-to-show", () => {
    win.show();
    console.log("LOG: Window shown");
  });

  // Add timeout fallback to show window even if content doesn't load
  setTimeout(() => {
    if (!win.isVisible()) {
      console.log("LOG: Forcing window to show after timeout");
      win.show();
    }
  }, 5000);

  if (!app.isPackaged) {
    win.webContents.openDevTools();
  }

  // Add more detailed error handling
  win.webContents.on(
    "did-fail-load",
    (event, errorCode, errorDescription, validatedURL) => {
      console.error(
        `LOG: Failed to load: ${errorCode} - ${errorDescription} - URL: ${validatedURL}`
      );

      // Try to load a fallback page or show an error
      if (app.isPackaged) {
        const fallbackHTML = `
        <html>
          <head><title>Loading Error</title></head>
          <body style="font-family: Arial; padding: 20px; background: #1f2937; color: white;">
            <h2>Application Loading Error</h2>
            <p>Error Code: ${errorCode}</p>
            <p>Description: ${errorDescription}</p>
            <p>URL: ${validatedURL}</p>
            <p>__dirname: ${__dirname}</p>
          </body>
        </html>
      `;
        win.loadURL(
          `data:text/html;charset=utf-8,${encodeURIComponent(fallbackHTML)}`
        );
      }
    }
  );

  win.webContents.on("did-finish-load", () => {
    console.log("LOG: Page finished loading successfully");
  });

  // Add window event listeners
  win.on("closed", () => {
    console.log("LOG: Window closed");
  });

  win.on("close", () => {
    console.log("LOG: Window close event triggered");
    // Normal close behavior
  });

  return win;
}

// --- IPC Handler ---
ipcMain.handle("fetch-courses", async (event, options) => {
  try {
    const data = await fetchCoursesAPI(options);
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Window control handlers
ipcMain.handle("window-minimize", () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.minimize();
});

ipcMain.handle("window-maximize", () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) {
    if (win.isMaximized()) {
      win.unmaximize();
    } else {
      win.maximize();
    }
  }
});

ipcMain.handle("window-close", () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.close();
});

// Open external links in default browser
ipcMain.handle("open-external", (event, url) => {
  shell.openExternal(url);
});

// --- App Lifecycle Events ---
app
  .whenReady()
  .then(() => {
    console.log("LOG: App is ready.");

    // Set app user model ID for Windows taskbar
    if (process.platform === "win32") {
      app.setAppUserModelId("com.udemy.coupon-grabber");
    }

    createWindow();
  })
  .catch((error) => {
    console.error("LOG: Error during app ready:", error);
  });

app.on("window-all-closed", () => {
  console.log("LOG: All windows closed");
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  console.log("LOG: App activated");
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// Add error handling
process.on("uncaughtException", (error) => {
  console.error("LOG: Uncaught Exception:", error);
});

process.on("unhandledRejection", (error) => {
  console.error("LOG: Unhandled Rejection:", error);
});
