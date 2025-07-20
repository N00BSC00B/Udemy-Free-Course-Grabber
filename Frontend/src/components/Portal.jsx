// src/components/Portal.jsx
import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

const Portal = ({ children, containerId = "portal-root" }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);

    // Create portal container if it doesn't exist
    let portalContainer = document.getElementById(containerId);
    if (!portalContainer) {
      portalContainer = document.createElement("div");
      portalContainer.id = containerId;
      portalContainer.style.position = "fixed";
      portalContainer.style.top = "0";
      portalContainer.style.left = "0";
      portalContainer.style.zIndex = "9999";
      portalContainer.style.pointerEvents = "none";
      document.body.appendChild(portalContainer);
    }

    return () => setMounted(false);
  }, [containerId]);

  return mounted
    ? createPortal(children, document.getElementById(containerId))
    : null;
};

export default Portal;
