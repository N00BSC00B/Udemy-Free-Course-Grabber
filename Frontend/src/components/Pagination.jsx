// src/components/Pagination.jsx
const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  return (
    <div className="flex justify-center mt-6 md:mt-10 px-4">
      <div className="join bg-base-200 rounded-xl shadow-md">
        <button
          className="join-item btn btn-sm md:btn-md"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          «
        </button>
        <button className="join-item btn btn-sm md:btn-md bg-primary text-primary-content pointer-events-none">
          <span className="hidden sm:inline">
            Page {currentPage} of {totalPages}
          </span>
          <span className="sm:hidden">
            {currentPage}/{totalPages}
          </span>
        </button>
        <button
          className="join-item btn btn-sm md:btn-md"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          »
        </button>
      </div>
    </div>
  );
};
export default Pagination;
