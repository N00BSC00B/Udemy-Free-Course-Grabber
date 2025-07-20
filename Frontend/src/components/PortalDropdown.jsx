// src/components/PortalDropdown.jsx
import { useState, useRef, useEffect, useCallback } from "react";
import Portal from "./Portal";

const PortalDropdown = ({ trigger, children, position = "bottom-start" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef(null);
  const dropdownRef = useRef(null);

  const calculatePosition = useCallback(() => {
    if (!triggerRef.current) return;

    const triggerRect = triggerRef.current.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft =
      window.pageXOffset || document.documentElement.scrollLeft;

    let top = triggerRect.bottom + scrollTop + 4; // 4px gap
    let left = triggerRect.left + scrollLeft;

    // Adjust for screen edges
    if (position.includes("end")) {
      left = triggerRect.right + scrollLeft - 200; // Assume dropdown width ~200px
    }

    // Prevent going off-screen
    const maxLeft = window.innerWidth - 250; // Account for dropdown width
    if (left > maxLeft) left = maxLeft;
    if (left < 0) left = 0;

    setDropdownPosition({ top, left });
  }, [position]);

  useEffect(() => {
    if (isOpen) {
      calculatePosition();
    }
  }, [isOpen, calculatePosition]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    const handleScroll = () => {
      if (isOpen) {
        calculatePosition();
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("scroll", handleScroll, true);
      window.addEventListener("resize", handleScroll);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("scroll", handleScroll, true);
      window.removeEventListener("resize", handleScroll);
    };
  }, [isOpen, calculatePosition]);

  const handleTriggerClick = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <div ref={triggerRef} onClick={handleTriggerClick}>
        {trigger}
      </div>

      {isOpen && (
        <Portal>
          <div
            ref={dropdownRef}
            className="fixed pointer-events-auto"
            style={{
              top: `${dropdownPosition.top}px`,
              left: `${dropdownPosition.left}px`,
              zIndex: 9999,
            }}
          >
            <div className="animate-in fade-in-0 zoom-in-95 duration-200">
              {children}
            </div>
          </div>
        </Portal>
      )}
    </>
  );
};

export default PortalDropdown;
