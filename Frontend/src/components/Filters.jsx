// src/components/Filters.jsx
import {
  SlidersHorizontal,
  ChevronDown,
  Tag,
  Palette,
  Search,
  X,
} from "lucide-react";
import ThemeIcon from "./ThemeIcon";
import PortalDropdown from "./PortalDropdown";
import { useState, useEffect } from "react";

const CATEGORIES = [
  "All",
  "Development",
  "IT & Software",
  "Business",
  "Design",
  "Marketing",
  "Personal Development",
  "Health & Fitness",
  "Finance & Accounting",
  "Lifestyle",
  "Music",
  "Office Productivity",
  "Photography & Video",
  "Teaching & Academics",
];
const SORT_BY = ["Date", "Popularity", "Rating", "Duration"];
const THEMES = [
  "light",
  "dark",
  "cupcake",
  "bumblebee",
  "emerald",
  "corporate",
  "synthwave",
  "retro",
  "cyberpunk",
  "valentine",
  "halloween",
  "garden",
  "forest",
  "aqua",
  "lofi",
  "pastel",
  "fantasy",
  "wireframe",
  "black",
  "luxury",
  "dracula",
  "cmyk",
  "autumn",
  "business",
  "acid",
  "lemonade",
  "night",
  "coffee",
  "winter",
];

const Filters = ({
  activeCategory,
  onCategoryChange,
  activeSort,
  onSortChange,
  activeTheme,
  onThemeChange,
  searchValue,
  onSearchChange,
}) => {
  const [search, setSearch] = useState(searchValue || "");
  const [isFocused, setIsFocused] = useState(false);

  useEffect(() => {
    const handler = setTimeout(() => {
      onSearchChange && onSearchChange(search);
    }, 400);
    return () => clearTimeout(handler);
  }, [search, onSearchChange]);

  return (
    <div className="w-full flex justify-center mb-4 md:mb-6">
      <div className="bg-gradient-to-r from-base-200 to-base-300 rounded-2xl shadow-lg backdrop-blur-sm border border-base-300/50 p-3 md:p-4 w-full max-w-[95vw] lg:max-w-[70vw]">
        {/* Mobile: Stack vertically, Desktop: Horizontal layout */}
        <div className="flex flex-col space-y-3 md:space-y-0 md:flex-row md:items-center md:gap-3">
          {/* Search Bar - Full width on mobile */}
          <div className="relative flex-1 min-w-0">
            <span
              className={`absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none z-10 transition-all duration-200 ${
                isFocused ? "text-primary scale-110" : "text-base-content/50"
              }`}
            >
              <Search className="w-4 h-4" />
            </span>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search courses..."
              className="input input-sm md:input-md input-bordered w-full pl-10 pr-10 bg-base-100/70 backdrop-blur-sm border-base-content/20 focus:border-primary focus:bg-base-100 transition-all duration-200"
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
            />
            {search && (
              <button
                className="absolute right-3 top-1/2 -translate-y-1/2 text-base-content/40 hover:text-error transition-colors z-20"
                onClick={() => setSearch("")}
                tabIndex={-1}
                aria-label="Clear search"
                type="button"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Filter Controls - Better mobile layout with proper spacing */}
          <div className="flex justify-between items-center w-full md:w-auto md:gap-3">
            {/* Left side: Sort and Category */}
            <div className="flex gap-2 md:gap-3">
              {/* Sort Dropdown with Portal */}
              <PortalDropdown
                position="bottom-start"
                trigger={
                  <button className="btn btn-sm btn-ghost bg-base-100/50 backdrop-blur-sm border border-base-content/10 hover:bg-base-100 hover:border-primary/30 transition-all duration-200">
                    <SlidersHorizontal className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="text-xs md:text-sm">Sort:</span>
                    <span className="text-xs md:text-sm font-medium">
                      {activeSort}
                    </span>
                    <ChevronDown className="w-3 h-3 md:w-4 md:h-4" />
                  </button>
                }
              >
                <div className="p-2 shadow-2xl bg-base-100 backdrop-blur-md rounded-xl border border-base-content/10 w-48 max-h-60 overflow-y-auto">
                  {SORT_BY.map((sort) => (
                    <div key={sort}>
                      <button
                        className={`block w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-primary hover:text-primary-content transition-colors ${
                          activeSort === sort
                            ? "bg-primary text-primary-content"
                            : ""
                        }`}
                        onClick={() => onSortChange(sort)}
                      >
                        {sort}
                      </button>
                    </div>
                  ))}
                </div>
              </PortalDropdown>

              {/* Category Dropdown with Portal */}
              <PortalDropdown
                position="bottom-start"
                trigger={
                  <button className="btn btn-sm btn-ghost bg-base-100/50 backdrop-blur-sm border border-base-content/10 hover:bg-base-100 hover:border-primary/30 transition-all duration-200">
                    <Tag className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="text-xs md:text-sm">Category:</span>
                    <span className="text-xs md:text-sm font-medium truncate max-w-[60px] md:max-w-none">
                      {activeCategory}
                    </span>
                    <ChevronDown className="w-3 h-3 md:w-4 md:h-4" />
                  </button>
                }
              >
                <div className="p-2 shadow-2xl bg-base-100 backdrop-blur-md rounded-xl border border-base-content/10 w-64 max-h-60 overflow-y-auto">
                  {CATEGORIES.map((cat) => (
                    <div key={cat}>
                      <button
                        className={`block w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-primary hover:text-primary-content transition-colors ${
                          activeCategory === cat
                            ? "bg-primary text-primary-content"
                            : ""
                        }`}
                        onClick={() => onCategoryChange(cat)}
                      >
                        {cat}
                      </button>
                    </div>
                  ))}
                </div>
              </PortalDropdown>
            </div>

            {/* Right side: Theme - Always show "Theme" text */}
            <div className="flex-shrink-0">
              <PortalDropdown
                position="bottom-end"
                trigger={
                  <button className="btn btn-sm btn-ghost bg-base-100/50 backdrop-blur-sm border border-base-content/10 hover:bg-base-100 hover:border-primary/30 transition-all duration-200">
                    <Palette className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="text-xs md:text-sm">Theme</span>
                  </button>
                }
              >
                <div className="p-2 shadow-2xl bg-base-100 backdrop-blur-md rounded-xl border border-base-content/10 w-52 max-h-60 overflow-y-auto">
                  {THEMES.map((theme) => (
                    <div key={theme}>
                      <button
                        className={`flex items-center gap-2 w-full text-left px-3 py-2 text-sm rounded-lg hover:bg-primary hover:text-primary-content transition-colors ${
                          activeTheme === theme
                            ? "bg-primary text-primary-content"
                            : ""
                        }`}
                        onClick={() => onThemeChange(theme)}
                      >
                        <ThemeIcon theme={theme} />
                        <span className="capitalize">{theme}</span>
                      </button>
                    </div>
                  ))}
                </div>
              </PortalDropdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Filters;
