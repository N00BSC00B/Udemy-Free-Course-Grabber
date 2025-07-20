import { useState, useEffect, useCallback } from "react";
import { fetchCourses } from "./services/api";
import CourseCard from "./components/CourseCard";
import Pagination from "./components/Pagination";
import Filters from "./components/Filters";
import TitleBar from "./components/TitleBar";
import NetworkStatus from "./components/NetworkStatus";
import { LoaderCircle } from "lucide-react";
import Footer from "./components/Footer";
import { Toaster } from "react-hot-toast";
import { getCurrentPlatform, PLATFORMS } from "./utils/platform";

const THEME_CACHE_KEY = "udemy_theme";

const getInitialTheme = () => {
  return localStorage.getItem(THEME_CACHE_KEY) || "night";
};

const App = () => {
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
  });
  const [filters, setFilters] = useState({ category: "All", sort: "Date" });
  const [theme, setTheme] = useState(getInitialTheme());
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_CACHE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  useEffect(() => {
    const getCourses = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await fetchCourses({
          page: pagination.currentPage,
          category: filters.category,
          sort: filters.sort,
          search: debouncedSearch,
        });
        setCourses(data.items || []);
        setPagination({
          currentPage: data.currentPage,
          totalPages: data.totalPages,
        });
      } catch (err) {
        setError(err.message);
        setCourses([]);
      } finally {
        setIsLoading(false);
      }
    };

    getCourses();
  }, [pagination.currentPage, filters, debouncedSearch]);

  const handlePageChange = (newPage) => {
    setPagination((prev) => ({ ...prev, currentPage: newPage }));
  };

  const handleCategoryChange = (newCategory) => {
    setPagination((prev) => ({ ...prev, currentPage: 1 }));
    setFilters((prev) => ({ ...prev, category: newCategory }));
  };

  const handleSortChange = (newSort) => {
    setPagination((prev) => ({ ...prev, currentPage: 1 }));
    setFilters((prev) => ({ ...prev, sort: newSort }));
  };

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme);
  };

  const getIconPath = () => {
    // In Electron, we can use a relative path or import the icon
    // The public folder contents are copied to dist root during build
    return "./icon.png";
  };

  return (
    <div
      className="min-h-screen flex flex-col bg-base-100 text-base-content"
      data-theme={theme}
    >
      <TitleBar />
      <NetworkStatus />
      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: "hsl(var(--b3))",
            color: "hsl(var(--bc))",
            borderRadius: "0.5rem",
            boxShadow: "0 2px 16px 0 hsla(var(--p),0.07)",
            fontWeight: 500,
          },
          success: {
            iconTheme: {
              primary: "hsl(var(--su))",
              secondary: "#fff",
            },
          },
        }}
      />
      <main className="container mx-auto px-4 md:px-8 pt-8 mt-10 md:mt-2 pb-4 md:pb-8 flex-1 flex flex-col safe-area-inset">
        <div className="mx-auto w-full max-w-[90vw] lg:max-w-[70vw]">
          <h1 className="text-3xl md:text-4xl font-bold mb-4 md:mb-6 text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent flex items-center gap-2">
            <span role="img" aria-label="icon">
              <img
                src={getIconPath()}
                alt="Udemy Free Course Grabber Icon"
                className="w-6 h-6 md:w-8 md:h-8"
              />
            </span>
            <span className="text-2xl md:text-4xl">
              Udemy Free Course Grabber
            </span>
          </h1>
          <p className="mb-6 text-base-content/70 text-lg italic animate-fadeIn">
            <strong>Supercharge your learning—at zero cost.</strong> <br />
            Find and claim fresh 100% free Udemy courses every day. Don’t miss
            out—start your learning journey now!
          </p>
        </div>

        <Filters
          activeCategory={filters.category}
          onCategoryChange={handleCategoryChange}
          activeSort={filters.sort}
          onSortChange={handleSortChange}
          activeTheme={theme}
          onThemeChange={handleThemeChange}
          searchValue={search}
          onSearchChange={setSearch}
        />

        {isLoading ? (
          <div className="text-center p-20 flex-1 flex items-center justify-center">
            <span className="loading loading-dots loading-lg text-primary"></span>
          </div>
        ) : error ? (
          <div
            role="alert"
            className="alert alert-error flex-1 flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="stroke-current shrink-0 h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span>Error: {error}</span>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              {courses.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  onCategoryChange={handleCategoryChange}
                />
              ))}
            </div>

            <Pagination
              currentPage={pagination.currentPage}
              totalPages={pagination.totalPages}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </main>
      <Footer />
    </div>
  );
};

export default App;
