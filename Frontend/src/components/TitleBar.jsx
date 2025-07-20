import { Minus, Square, X } from "lucide-react";

const TitleBar = () => {
  const handleMinimize = () => {
    if (window.electronAPI) {
      window.electronAPI.windowMinimize();
    }
  };

  const handleMaximize = () => {
    if (window.electronAPI) {
      window.electronAPI.windowMaximize();
    }
  };

  const handleClose = () => {
    if (window.electronAPI) {
      window.electronAPI.windowClose();
    }
  };

  // Only show title bar in Electron
  if (!window.electronAPI) {
    return null;
  }

  // Get the correct icon path for both development and production
  const getIconPath = () => {
    // In Electron, we can use a relative path or import the icon
    // The public folder contents are copied to dist root during build
    return "./icon.png";
  };

  return (
    <div
      className="flex items-center justify-between bg-base-200 h-8 px-4 select-none"
      style={{ WebkitAppRegion: "drag" }}
    >
      <div className="flex items-center space-x-2">
        <img src={getIconPath()} alt="App Icon" className="w-4 h-4" />
        <span className="text-sm font-medium">Udemy Course Grabber</span>
      </div>

      <div
        className="flex items-center space-x-1"
        style={{ WebkitAppRegion: "no-drag" }}
      >
        <button
          onClick={handleMinimize}
          className="p-1 hover:bg-base-300 rounded transition-colors"
          title="Minimize"
        >
          <Minus size={12} />
        </button>
        <button
          onClick={handleMaximize}
          className="p-1 hover:bg-base-300 rounded transition-colors"
          title="Maximize"
        >
          <Square size={12} />
        </button>
        <button
          onClick={handleClose}
          className="p-1 hover:bg-red-500 hover:text-white rounded transition-colors"
          title="Close"
        >
          <X size={12} />
        </button>
      </div>
    </div>
  );
};

export default TitleBar;
