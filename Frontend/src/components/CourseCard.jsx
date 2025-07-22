import { Star, Copy, ExternalLink, Tag, Clock } from "lucide-react";
import { formatDistanceToNowStrict } from "date-fns";
// import { utcToZonedTime } from "date-fns-tz";
import toast from "react-hot-toast";
import { openUrl } from "../services/api";

const CourseCard = ({ course, onCategoryChange }) => {
  // --- Data Formatting and Validation ---

  // 1. Stricter check for rating: only show if it's a number greater than 0.
  const ratingValue = parseFloat(course.rating);
  const hasRating = !isNaN(ratingValue) && ratingValue > 0;

  // 2. Stricter check and formatting for duration.
  const durationValue = parseFloat(course.lectures);
  const hasDuration = !isNaN(durationValue) && durationValue > 0;

  const formatHours = (hours) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)} minutes`;
    }
    return `${hours} hours`;
  };

  // Format the "time ago" text.
  const timeAgo = course.sale_start
    ? formatDistanceToNowStrict(new Date(course.sale_start + "Z"))
    : null;

  const originalPrice = course.price > 0 ? `$${course.price.toFixed(0)}` : "";

  // A helper for the copy-to-clipboard function
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(course.url);
      toast.success("Link copied to clipboard!");
    } catch (error) {
      // Fallback for older browsers or when clipboard API is not available
      const textArea = document.createElement("textarea");
      textArea.value = course.url;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      toast.success("Link copied to clipboard!");
    }
  };

  // Helper function to open course using platform-agnostic method
  const openCourse = async () => {
    try {
      await openUrl(course.url);
    } catch (error) {
      console.error("Failed to open URL:", error);
      toast.error("Failed to open course link");
    }
  };

  return (
    <div className="w-full flex justify-center my-3 md:my-4 px-2 md:px-0">
      <div className="bg-gradient-to-br from-primary via-base-200 to-info p-[1.5px] md:p-[2px] rounded-xl md:rounded-2xl w-full max-w-[95vw] md:max-w-[90vw] lg:max-w-[70vw]">
        <div className="card lg:card-side bg-base-200 shadow-md transition-all duration-300 hover:bg-base-300 hover:shadow-xl w-full min-h-[200px] md:min-h-[260px]">
          <figure className="w-full lg:w-96 relative flex-shrink-0">
            <img
              src={course.image}
              alt={course.name}
              className="w-full h-36 md:h-48 object-cover rounded-t-lg lg:rounded-l-lg lg:rounded-tr-none"
            />
            {timeAgo && (
              <div
                className="
      absolute top-0 left-0 flex items-center
      px-2 py-1
      rounded-tl-xl rounded-bl-xl z-20
      bg-gradient-to-br from-black via-black/50 to-transparent
    "
                style={{
                  // Mobile
                  ...(window.innerWidth < 768 && {
                    width: "50%",
                    height: "30%",
                  }),
                  // Tablet
                  ...(window.innerWidth >= 768 &&
                    window.innerWidth < 1024 && {
                      width: "45%",
                      height: "20%",
                    }),
                  ...(window.innerWidth >= 1024 && {
                    width: "55%",
                    height: "15%",
                  }),
                  clipPath: "polygon(0 0, 100% 0, 85% 100%, 0% 100%)",
                }}
              >
                <span className="text-white font-medium text-xs whitespace-nowrap">
                  {timeAgo} ago
                </span>
              </div>
            )}
          </figure>

          <div className="card-body flex flex-col min-h-[160px] md:min-h-[260px] p-3 md:p-6">
            <h2 className="card-title text-sm md:text-base lg:text-lg text-base-content leading-snug mb-2">
              {course.name}
            </h2>

            {/* Tags and Details Area - Better layout */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 my-2">
              {/* Left side: Category tag */}
              <div className="flex-shrink-0">
                {course.category ? (
                  <button
                    className="btn btn-xs md:btn-sm btn-primary gap-1 text-xs min-h-[1.75rem] h-auto"
                    onClick={() => onCategoryChange(course.category)}
                  >
                    <Tag className="w-2.5 h-2.5 md:w-3 md:h-3 flex-shrink-0" />
                    <span className="truncate max-w-[120px] sm:max-w-none">
                      {course.category}
                    </span>
                  </button>
                ) : (
                  <div className="badge badge-neutral text-xs">No category</div>
                )}
              </div>

              {/* Right side: Duration and Rating */}
              <div className="flex flex-wrap gap-1.5 md:gap-2 items-center">
                {hasDuration && (
                  <div className="badge badge-info gap-1 text-info-content text-xs min-h-[1.5rem] px-2">
                    <Clock className="w-2.5 h-2.5 md:w-3 md:h-3 flex-shrink-0" />
                    <span className="whitespace-nowrap">
                      {formatHours(durationValue)}
                    </span>
                  </div>
                )}
                {hasRating && (
                  <div className="badge badge-warning gap-1 text-warning-content text-xs min-h-[1.5rem] px-2">
                    <Star className="w-2.5 h-2.5 md:w-3 md:h-3 flex-shrink-0" />
                    <span className="whitespace-nowrap">
                      {ratingValue.toFixed(1)}
                      <span className="hidden md:inline"> Rating</span>
                    </span>
                  </div>
                )}
                {!hasDuration && !hasRating && !course.category && (
                  <div className="badge badge-neutral text-xs">
                    No extra info
                  </div>
                )}
              </div>
            </div>

            <p className="text-base-content/70 text-xs md:text-sm hidden md:block flex-grow leading-relaxed">
              {course.description.replace(/<[^>]*>?/gm, "").substring(0, 120) +
                "..."}
            </p>

            <div className="card-actions justify-between items-center mt-auto pt-3 md:pt-4 gap-2">
              <div className="flex items-center gap-1 md:gap-2">
                <div className="font-bold text-base md:text-lg text-success animate-pulse">
                  FREE
                </div>
                {originalPrice && (
                  <div className="text-xs md:text-sm text-base-content/50 line-through">
                    {originalPrice}
                  </div>
                )}
              </div>

              <div className="flex gap-1.5 md:gap-2">
                <button
                  className="btn btn-ghost btn-xs md:btn-sm px-2 md:px-3"
                  onClick={copyLink}
                >
                  <Copy className="w-3 h-3 md:w-4 md:h-4" />
                  <span className="hidden md:inline ml-1">Copy</span>
                </button>
                <button
                  onClick={openCourse}
                  className="btn btn-primary btn-xs md:btn-sm px-2 md:px-3"
                >
                  <ExternalLink className="w-3 h-3 md:w-4 md:h-4" />
                  <span className="hidden sm:inline ml-1">View Course</span>
                  <span className="sm:hidden ml-1">View</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseCard;
