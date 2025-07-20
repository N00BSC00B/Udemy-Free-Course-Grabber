# improved_main.py
import threading
from tkinter import messagebox
import traceback
from typing import Optional, Dict

from api_client import ImprovedAPIClient, APIError
from app_gui import ImprovedApp
from cache_manager import CacheManager


class ImprovedMainApplication(ImprovedApp):
    """Main application with production-ready features"""

    def __init__(self):
        super().__init__()

        # Center the window on the screen
        self.after(0, self._center_window)

        # Initialize components
        self.api_client = None
        self.cache_manager = None
        self._init_components()

        # Application state
        self.current_page = 1
        self.total_pages = 1
        self.current_category = "All"
        self.current_sort = "Date"
        self.current_search = ""
        self.is_loading = False
        self.auto_refresh_timer = None

        # Connect UI callbacks
        self._connect_callbacks()

        # Initial load
        self.after(100, self._initial_load)

        # Setup auto-refresh if enabled
        self._setup_auto_refresh()

    def _center_window(self):
        """Center the main window on the screen"""
        self.update_idletasks()
        width = 1000
        height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _init_components(self):
        """Initialize API client and cache manager"""
        try:
            self.api_client = ImprovedAPIClient(self.settings)
            self.cache_manager = CacheManager()

            # Test API connectivity
            self.after(500, self._test_api_connectivity)

        except Exception as e:
            print(f"Error initializing components: {e}")
            self.set_status("Error initializing application", "red")

    def _connect_callbacks(self):
        """Connect UI callbacks to methods"""
        try:
            # Pagination
            self.next_button.configure(command=self.next_page)
            self.prev_button.configure(command=self.prev_page)

            # Category buttons
            for cat_name, btn in self.category_buttons.items():
                btn.configure(command=lambda c=cat_name: self.filter_by_category(c))

            # Search
            self.search_entry.bind("<Return>", lambda e: self._perform_search())

            # Sort change
            self.sort_var.trace("w", self._on_sort_change_trace)

            # Window close event
            self.protocol("WM_DELETE_WINDOW", self._on_closing)

        except Exception as e:
            print(f"Error connecting callbacks: {e}")

    def _test_api_connectivity(self):
        """Test API connectivity in background"""
        def test_worker():
            try:
                if self.api_client and self.api_client.test_connection():
                    self.after(0, lambda: self.set_status("API connected", "green"))
                else:
                    self.after(0, lambda: self.set_status("API connection failed", "orange"))
            except Exception:
                self.after(0, lambda: self.set_status("API error", "red"))

        threading.Thread(target=test_worker, daemon=True).start()

    def _initial_load(self):
        """Perform initial data load - load All categories with default sort"""
        # Load with "All" category and "Date" sort by default
        self.current_category = "All"
        self.current_sort = "Date"
        self.current_page = 1

        # Highlight the "All" category button
        if "All" in self.category_buttons:
            self.category_buttons["All"].configure(fg_color=("gray75", "gray25"))

        # Start loading courses immediately
        self.fetch_and_display_courses(force_cache_first=True, force_refresh=True)

    def _setup_auto_refresh(self):
        """Setup auto-refresh timer if enabled"""
        if self.settings.get('auto_refresh', False):
            # Refresh every hour
            self.auto_refresh_timer = self.after(3600000, self._auto_refresh)

    def _auto_refresh(self):
        """Auto-refresh courses"""
        if not self.is_loading:
            self.set_status("Auto-refreshing courses...")
            self._refresh_courses()

        # Schedule next auto-refresh
        if self.settings.get('auto_refresh', False):
            self.auto_refresh_timer = self.after(3600000, self._auto_refresh)

    def fetch_and_display_courses(
        self,
        page: int = None,
        category: str = None,
        sort: str = None,
        search: str = None,
        force_refresh: bool = False,
        force_cache_first: bool = False
    ):
        """Fetch and display courses with improved error handling"""
        if self.is_loading:
            return

        # Check if we need to fetch new data
        new_page = page or self.current_page
        new_category = category or self.current_category
        new_sort = sort or self.current_sort
        new_search = search if search is not None else self.current_search

        # If nothing changed and we're not forcing refresh, don't fetch
        if (
            not force_refresh and not force_cache_first and
            new_page == self.current_page and
            new_category == self.current_category and
            new_sort == self.current_sort and
            new_search == self.current_search
        ):
            return

        # Update state
        self.current_page = new_page
        self.current_category = new_category
        self.current_sort = new_sort
        self.current_search = new_search

        # Show loading
        self.is_loading = True
        self.show_loading(f"Loading {self.current_category} courses...")
        self.set_status("Loading courses...")

        # Disable pagination during loading
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")

        # Run in background thread
        threading.Thread(
            target=self._worker_fetch_courses,
            args=(force_refresh, force_cache_first),
            daemon=True
        ).start()

    def _worker_fetch_courses(self, force_refresh: bool = False,
                              force_cache_first: bool = False):
        """Worker thread for fetching courses"""
        try:
            data = None

            # Priority handling for force_cache_first (startup behavior)
            if force_cache_first and self.cache_manager:
                self.after(0, lambda: self.set_status("Loading from cache..."))
                data = self.cache_manager.get_cached_data(
                    self.current_page,
                    self.current_category,
                    self.current_sort,
                    self.current_search
                )
                if data:
                    # Found cache data, use it and return
                    self.after(0, lambda: self._update_ui_with_data(data))
                    return
                else:
                    # No cache available, show that we're fetching from API
                    self.after(0, lambda: self.set_status(
                        "No cache found, fetching from API..."))

            # Try cache first unless force refresh (normal behavior)
            elif not force_refresh and self.cache_manager:
                data = self.cache_manager.get_cached_data(
                    self.current_page,
                    self.current_category,
                    self.current_sort,
                    self.current_search
                )

            # Fetch from API if no cache data or force_refresh
            if not data and self.api_client:
                try:
                    self.after(0, lambda: self.set_status("Fetching from API..."))
                    self.after(0, lambda: self.progress_bar.show(
                        "Fetching courses from API..."))

                    data = self.api_client.get_courses(
                        page=self.current_page,
                        category=self.current_category,
                        sort=self.current_sort,
                        search=self.current_search or None
                    )

                    # Cache the data
                    if data and self.cache_manager:
                        self.cache_manager.set_cached_data(
                            self.current_page,
                            self.current_category,
                            self.current_sort,
                            data,
                            self.current_search or None
                        )

                except APIError as e:
                    self.after(0, lambda err=e: self._handle_api_error(err))
                    return
                except Exception as e:
                    self.after(0, lambda err=e: self._handle_unexpected_error(err))
                    return

            # Schedule UI update on main thread
            self.after(0, lambda: self._update_ui_with_data(data))

        except Exception as e:
            self.after(0, lambda err=e: self._handle_unexpected_error(err))

    def _update_ui_with_data(self, data: Optional[Dict]):
        """Update UI with fetched data (runs on main thread)"""
        try:
            self.is_loading = False
            self.hide_loading()
            self.progress_bar.hide()

            if data:
                # Extract course data
                courses = data.get("items", [])
                self.total_pages = data.get("totalPages", 1)

                # Validate courses data
                if not isinstance(courses, list):
                    courses = []

                # Display courses
                self.display_courses(courses)

                # Update pagination
                self.update_pagination(self.current_page, self.total_pages)

                # Update status
                cache_info = data.get('_cache_info', {})
                if cache_info.get('loaded_from_cache'):
                    age_minutes = cache_info.get('age_seconds', 0) / 60
                    self.set_status(f"Loaded from cache ({age_minutes:.1f} min old)", "blue")
                else:
                    self.set_status("Loaded from API", "green")

            else:
                # No data available
                self.display_courses([])
                self.update_pagination(1, 1)
                self.set_status("No data available", "orange")

        except Exception as e:
            self._handle_unexpected_error(e)

    def _handle_api_error(self, error: APIError):
        """Handle API-specific errors"""
        error_msg = str(error)

        if error.status_code == 429:
            # Rate limited
            self.set_status("Rate limited - please wait", "red")
            messagebox.showwarning(
                "Rate Limited",
                "Too many requests. Please wait a moment before trying again."
            )
        elif error.status_code and error.status_code >= 500:
            # Server error
            self.set_status("Server error", "red")
            messagebox.showerror(
                "Server Error",
                f"The API server is experiencing issues:\n{error_msg}"
            )
        elif "timeout" in error_msg.lower():
            # Timeout
            self.set_status("Request timeout", "red")
            messagebox.showerror(
                "Timeout",
                "Request timed out. Please check your internet connection and try again."
            )
        elif "connection" in error_msg.lower():
            # Connection error
            self.set_status("Connection error", "red")
            messagebox.showerror(
                "Connection Error",
                "Could not connect to the API. Please check your internet connection."
            )
        else:
            # Generic API error
            self.set_status("API error", "red")
            messagebox.showerror(
                "API Error",
                f"An error occurred while fetching data:\n{error_msg}"
            )

        # Always hide loading and enable controls
        self.is_loading = False
        self.hide_loading()
        self.progress_bar.hide()
        self._enable_pagination()

    def _handle_unexpected_error(self, error: Exception):
        """Handle unexpected errors"""
        error_msg = str(error)
        print(f"Unexpected error: {error}")
        print(traceback.format_exc())

        self.set_status("Unexpected error", "red")

        # Show user-friendly error dialog
        messagebox.showerror(
            "Unexpected Error",
            f"An unexpected error occurred:\n{error_msg}\n\n"
            "Please try again or restart the application."
        )

        # Reset state
        self.is_loading = False
        self.hide_loading()
        self.progress_bar.hide()
        self._enable_pagination()

    def _enable_pagination(self):
        """Re-enable pagination controls"""
        self.prev_button.configure(
            state="normal" if self.current_page > 1 else "disabled"
        )
        self.next_button.configure(
            state="normal" if self.current_page < self.total_pages else "disabled"
        )

    def next_page(self):
        """Go to next page"""
        if not self.is_loading and self.current_page < self.total_pages:
            self.fetch_and_display_courses(page=self.current_page + 1)

    def prev_page(self):
        """Go to previous page"""
        if not self.is_loading and self.current_page > 1:
            self.fetch_and_display_courses(page=self.current_page - 1)

    def filter_by_category(self, category: str):
        """Filter courses by category"""
        if self.is_loading:
            return  # Ignore if already loading

        if self.current_category != category:
            # Update button highlights immediately for better UX
            for cat_name, btn in self.category_buttons.items():
                if cat_name == category:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color="transparent")

            # Clear search when changing category
            self.search_entry.delete(0, 'end')

            # Fetch new courses
            self.fetch_and_display_courses(page=1, category=category)

    def _on_sort_change_trace(self, *args):
        """Handle sort option change (trace callback)"""
        if not self.is_loading:
            new_sort = self.sort_var.get()
            if new_sort != self.current_sort:
                self.fetch_and_display_courses(page=1, sort=new_sort)

    def _on_sort_change(self, value):
        """Handle sort option change (direct callback)"""
        if not self.is_loading and value != self.current_sort:
            self.fetch_and_display_courses(page=1, sort=value)

    def _perform_search(self):
        """Perform search"""
        search_text = self.search_entry.get().strip()
        if not self.is_loading:
            if search_text != self.current_search:
                self.fetch_and_display_courses(page=1, search=search_text)
            elif not search_text:
                # Empty search - show all courses
                self.fetch_and_display_courses(page=1, search="")

    def _clear_search(self):
        """Clear search and show all courses"""
        if not self.is_loading:
            self.search_entry.delete(0, 'end')
            self.fetch_and_display_courses(page=1, search="")

    def _refresh_courses(self):
        """Refresh current courses"""
        if not self.is_loading:
            self.fetch_and_display_courses(force_refresh=True)

    def _show_settings(self):
        """Show settings window"""
        try:
            from app_gui import SettingsWindow
            settings_window = SettingsWindow(self, self.settings)
            settings_window.show()
        except Exception as e:
            print(f"Error showing settings: {e}")
            messagebox.showerror("Error", "Could not open settings window.")

    def _export_courses(self):
        """Export current courses"""
        if not hasattr(self, 'current_courses_data') or not self.current_courses_data:
            messagebox.showwarning("Warning", "No courses to export.")
            return

        super()._export_courses()

    def _on_closing(self):
        """Handle application closing"""
        try:
            # Cancel auto-refresh timer
            if self.auto_refresh_timer:
                self.after_cancel(self.auto_refresh_timer)

            # Save any pending settings
            # (Settings are saved automatically in the settings window)

            # Clean up resources
            if hasattr(self, 'api_client') and self.api_client:
                # Close any open sessions
                if hasattr(self.api_client, 'session'):
                    self.api_client.session.close()

        except Exception as e:
            print(f"Error during cleanup: {e}")

        finally:
            self.destroy()


def main():
    """Main entry point"""
    try:
        app = ImprovedMainApplication()
        app.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        print(traceback.format_exc())
        try:
            messagebox.showerror(
                "Fatal Error",
                f"A fatal error occurred:\n{str(e)}\n\n"
                "The application will now exit."
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
