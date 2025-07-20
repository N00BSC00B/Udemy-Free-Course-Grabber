# app_gui.py
import csv
import customtkinter as ctk
from datetime import datetime, timezone
import json
import math
import os
import pyperclip
import re
import threading
import time
from tkinter import messagebox, filedialog
from typing import Optional, Dict, List
import webbrowser

from api_client import CATEGORIES, SORT_BY


def clean_html(text: str) -> str:
    """Remove HTML tags from text and clean it up"""
    if not text:
        return ""

    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', text)

    # Clean up multiple spaces and newlines
    clean_text = re.sub(r'\s+', ' ', clean_text)

    # Remove leading/trailing whitespace
    clean_text = clean_text.strip()

    return clean_text


def format_time_ago(sale_start: str) -> str:
    """
    Formats an ISO timestamp string into a 'time ago' format.
    Example: '5h ago', '2d ago', 'Just now'
    """
    if not sale_start:
        return "Unknown time"

    try:
        # Step 1: Parse the timestamp string
        # The .fromisoformat() method is smart enough to handle most cases,
        # but the 'Z' (Zulu) suffix needs to be replaced for compatibility.
        if sale_start.endswith('Z'):
            sale_time = datetime.fromisoformat(sale_start.replace('Z', '+00:00'))
        else:
            sale_time = datetime.fromisoformat(sale_start)

        # Step 2: Ensure the parsed time is timezone-aware (assume UTC if not)
        if sale_time.tzinfo is None:
            sale_time = sale_time.replace(tzinfo=timezone.utc)

        # Step 3: Calculate the difference from now in UTC
        now = datetime.now(timezone.utc)
        diff = now - sale_time

        # Ensure the time is not in the future
        if diff.total_seconds() < 0:
            return "In the future"

        # Step 4: Format the output based on the *total* duration
        total_seconds = int(diff.total_seconds())
        days = total_seconds // 86400
        hours = total_seconds // 3600
        minutes = total_seconds // 60

        if days > 0:
            return f"{days}d ago"
        if hours > 0:
            return f"{hours}h ago"
        if minutes > 0:
            return f"{minutes}m ago"

        return "Just now"

    except (ValueError, TypeError):
        # Handle cases where the timestamp is invalid or not a string
        return "Invalid time"


class LoadingSpinner(ctk.CTkFrame):
    """A custom loading spinner widget"""
    def __init__(self, master, size: int = 30, **kwargs):
        super().__init__(master, **kwargs)
        self.size = size
        self.angle = 0
        self.is_running = False

        self.canvas = ctk.CTkCanvas(self, width=size, height=size, highlightthickness=0, bg='#2B2B2B')
        self.canvas.pack()

    def start(self):
        """Start the spinning animation"""
        self.is_running = True
        self._animate()

    def stop(self):
        """Stop the spinning animation"""
        self.is_running = False
        self.canvas.delete("all")

    def _animate(self):
        """Internal animation method"""
        if not self.is_running:
            return

        self.canvas.delete("all")

        # Draw spinning circle
        center = self.size // 2
        radius = center - 5

        # Create gradient effect
        for i in range(8):
            angle = (self.angle + i * 45) % 360
            angle_rad = math.radians(angle)
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

            x1 = center + radius * 0.7 * cos_a
            y1 = center + radius * 0.7 * sin_a
            x2 = center + radius * cos_a
            y2 = center + radius * sin_a

            opacity = 1.0 - (i * 0.1)
            gray_val = int(64 + opacity * 191)
            color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"

            self.canvas.create_line(x1, y1, x2, y2, width=3, fill=color,
                                    capstyle='round')

        self.angle = (self.angle + 15) % 360
        self.after(50, self._animate)


class ProgressBar(ctk.CTkFrame):
    """Custom progress bar with text"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))

        self.progress_label = ctk.CTkLabel(self, text="")
        self.progress_label.pack(pady=(0, 10))

        self.hide()

    def show(self, text: str = "Loading..."):
        """Show progress bar with text"""
        self.progress_label.configure(text=text)
        self.progress_bar.set(0)
        # Don't use pack() since we're already in grid - just make visible
        self.grid(row=1, column=1, padx=(5, 10), pady=0, sticky="ew")

    def update(self, value: float, text: str = None):
        """Update progress bar value and text"""
        self.progress_bar.set(value)
        if text:
            self.progress_label.configure(text=text)

    def hide(self):
        """Hide progress bar"""
        self.grid_remove()  # Use grid_remove instead of pack_forget


class SettingsWindow:
    """Settings window for application preferences"""
    def __init__(self, parent, current_settings: Dict):
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.window = None

    def show(self):
        """Show settings window"""
        if self.window is not None:
            self.window.focus()
            return

        self.window = ctk.CTkToplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("500x500")
        self.window.resizable(False, False)

        # Center the window on the screen
        self.window.update_idletasks()
        width = 500
        height = 550
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()

        self._create_settings_widgets()

        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)

    def _create_settings_widgets(self):
        """Create settings widgets"""
        # Main container
        main_frame = ctk.CTkScrollableFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Appearance Settings
        appearance_label = ctk.CTkLabel(main_frame, text="Appearance", font=ctk.CTkFont(size=16, weight="bold"))
        appearance_label.pack(anchor="w", pady=(0, 10))

        # Theme selection
        theme_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left")
        self.theme_var = ctk.StringVar(value=self.current_settings.get('theme', 'Dark'))
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            variable=self.theme_var,
            command=self._update_theme
        )
        theme_menu.pack(side="right")

        # Caching Settings
        cache_label = ctk.CTkLabel(main_frame, text="Cache Settings", font=ctk.CTkFont(size=16, weight="bold"))
        cache_label.pack(anchor="w", pady=(20, 10))

        # Cache duration
        cache_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cache_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(cache_frame, text="Cache Duration (hours):").pack(side="left")
        self.cache_var = ctk.StringVar(value=str(self.current_settings.get('cache_duration', 6)))
        cache_entry = ctk.CTkEntry(cache_frame, textvariable=self.cache_var, width=60)
        cache_entry.pack(side="right")

        # Auto-refresh
        self.auto_refresh_var = ctk.BooleanVar(value=self.current_settings.get('auto_refresh', False))
        auto_refresh_check = ctk.CTkCheckBox(
            main_frame,
            text="Auto-refresh courses every hour",
            variable=self.auto_refresh_var
        )
        auto_refresh_check.pack(anchor="w", pady=(0, 10))

        # Network Settings
        network_label = ctk.CTkLabel(main_frame, text="Network Settings", font=ctk.CTkFont(size=16, weight="bold"))
        network_label.pack(anchor="w", pady=(20, 10))

        # Request timeout
        timeout_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        timeout_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(timeout_frame, text="Request Timeout (seconds):").pack(side="left")
        self.timeout_var = ctk.StringVar(value=str(self.current_settings.get('timeout', 10)))
        timeout_entry = ctk.CTkEntry(timeout_frame, textvariable=self.timeout_var, width=60)
        timeout_entry.pack(side="right")

        # Retry attempts
        retry_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        retry_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(retry_frame, text="Retry Attempts:").pack(side="left")
        self.retry_var = ctk.StringVar(value=str(self.current_settings.get('retry_attempts', 3)))
        retry_entry = ctk.CTkEntry(retry_frame, textvariable=self.retry_var, width=60)
        retry_entry.pack(side="right")

        # Display Settings
        display_label = ctk.CTkLabel(main_frame, text="Display Settings", font=ctk.CTkFont(size=16, weight="bold"))
        display_label.pack(anchor="w", pady=(20, 10))

        # Courses per page
        courses_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        courses_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(courses_frame, text="Courses per page:").pack(side="left")
        self.courses_per_page_var = ctk.StringVar(value=str(self.current_settings.get('courses_per_page', 20)))
        courses_menu = ctk.CTkOptionMenu(
            courses_frame,
            values=["10", "20", "30", "50"],
            variable=self.courses_per_page_var
        )
        courses_menu.pack(side="right")

        # Show course descriptions
        self.show_descriptions_var = ctk.BooleanVar(value=self.current_settings.get('show_descriptions', True))
        desc_check = ctk.CTkCheckBox(
            main_frame,
            text="Show course descriptions",
            variable=self.show_descriptions_var
        )
        desc_check.pack(anchor="w", pady=(0, 10))

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        save_btn = ctk.CTkButton(button_frame, text="Save", command=self._save_settings)
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="gray40",
            hover_color="gray30",
            command=self._close_window
        )
        cancel_btn.pack(side="right")

        # Reset button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            width=120,
            fg_color="transparent",
            hover_color="gray30",
            border_width=1,
            command=self._reset_settings
        )
        reset_btn.pack(side="left")

    def _update_theme(self, theme):
        """Update application theme"""
        ctk.set_appearance_mode(theme.lower() if theme != "System" else "system")

    def _save_settings(self):
        """Save current settings"""
        try:
            self.current_settings.update({
                'theme': self.theme_var.get(),
                'cache_duration': int(self.cache_var.get()),
                'auto_refresh': self.auto_refresh_var.get(),
                'timeout': int(self.timeout_var.get()),
                'retry_attempts': int(self.retry_var.get()),
                'courses_per_page': int(self.courses_per_page_var.get()),
                'show_descriptions': self.show_descriptions_var.get()
            })

            # Save to file
            settings_path = os.path.join("cache", "settings.json")
            os.makedirs("cache", exist_ok=True)
            with open(settings_path, 'w') as f:
                json.dump(self.current_settings, f, indent=2)

            messagebox.showinfo("Success", "Settings saved successfully!")
            self._close_window()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value entered: {e}")

    def _reset_settings(self):
        """Reset settings to defaults"""
        defaults = {
            'theme': 'Dark',
            'cache_duration': 6,
            'auto_refresh': False,
            'timeout': 10,
            'retry_attempts': 3,
            'courses_per_page': 20,
            'show_descriptions': True
        }

        self.theme_var.set(defaults['theme'])
        self.cache_var.set(str(defaults['cache_duration']))
        self.auto_refresh_var.set(defaults['auto_refresh'])
        self.timeout_var.set(str(defaults['timeout']))
        self.retry_var.set(str(defaults['retry_attempts']))
        self.courses_per_page_var.set(str(defaults['courses_per_page']))
        self.show_descriptions_var.set(defaults['show_descriptions'])

    def _close_window(self):
        """Close settings window"""
        self.window.grab_release()
        self.window.destroy()
        self.window = None


class ImprovedApp(ctk.CTk):
    """Improved Udemy Course Grabber with production-ready features"""

    def __init__(self):
        super().__init__()

        # Initialize components
        self.settings = self._load_settings()
        self.course_cards = []
        self.current_courses_data = []

        # Apply saved theme
        ctk.set_appearance_mode(self.settings.get('theme', 'Dark').lower())

        # Configure window
        self.title("Udemy Course Grabber - Modern UI")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Configure grid weights
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()
        self._setup_menu()

    def _load_settings(self) -> Dict:
        """Load application settings"""
        try:
            settings_path = os.path.join("cache", "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")

        # Return defaults
        return {
            'theme': 'Dark',
            'cache_duration': 6,
            'auto_refresh': False,
            'timeout': 10,
            'retry_attempts': 3,
            'courses_per_page': 20,
            'show_descriptions': True
        }

    def _create_widgets(self):
        """Create and layout all widgets"""
        # Left sidebar for categories
        self._create_sidebar()

        # Top toolbar
        self._create_toolbar()

        # Main content area
        self._create_main_content()

        # Bottom status bar
        self._create_status_bar()

    def _create_sidebar(self):
        """Create left sidebar with categories and filters"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.sidebar.grid(row=0, column=0, rowspan=3, padx=(10, 5), pady=10, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="FILTERS",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        sidebar_title.pack(pady=(15, 10))

        # Categories
        categories_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        categories_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(categories_frame, text="Categories", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.category_buttons = {}

        # Create scrollable frame for categories
        cat_scroll = ctk.CTkScrollableFrame(categories_frame, height=200)
        cat_scroll.pack(fill="both", expand=True, pady=(5, 0))

        # Add "All" category first, then the others
        all_categories = ["All"] + CATEGORIES
        for cat_name in all_categories:
            btn = ctk.CTkButton(
                cat_scroll,
                text=cat_name,
                anchor="w",
                fg_color="transparent",
                hover_color="gray30",
                height=30
            )
            btn.pack(fill="x", pady=2)
            self.category_buttons[cat_name] = btn

        # Sort options
        sort_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sort_frame.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(sort_frame, text="Sort By", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        self.sort_var = ctk.StringVar(value="Date")
        sort_menu = ctk.CTkOptionMenu(
            sort_frame,
            values=list(SORT_BY.keys()),
            variable=self.sort_var,
            command=self._on_sort_change
        )
        sort_menu.pack(fill="x", pady=(5, 0))

        # Quick actions
        actions_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(20, 0))

        ctk.CTkLabel(actions_frame, text="Quick Actions", font=ctk.CTkFont(weight="bold")).pack(anchor="w")

        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="Refresh",
            command=self._refresh_courses,
            height=35
        )
        refresh_btn.pack(fill="x", pady=(5, 2))

        export_btn = ctk.CTkButton(
            actions_frame,
            text="Export",
            command=self._export_courses,
            fg_color="gray40",
            hover_color="gray30",
            height=35
        )
        export_btn.pack(fill="x", pady=2)

        settings_btn = ctk.CTkButton(
            actions_frame,
            text="Settings",
            command=self._show_settings,
            fg_color="transparent",
            hover_color="gray30",
            border_width=1,
            height=35
        )
        settings_btn.pack(fill="x", pady=2)

    def _create_toolbar(self):
        """Create top toolbar with search and controls"""
        self.toolbar = ctk.CTkFrame(self, height=60, corner_radius=10)
        self.toolbar.grid(row=0, column=1, padx=(5, 10), pady=(10, 5), sticky="ew")
        self.toolbar.grid_columnconfigure(1, weight=1)

        # Search section
        search_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        search_frame.grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search courses by title, category, or instructor...",
            height=35
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", self._on_search_enter)  # Only search on Enter

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            height=35,
            command=self._perform_search
        )
        search_btn.grid(row=0, column=2)

        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            width=60,
            height=35,
            fg_color="gray40",
            hover_color="gray30",
            command=self._clear_search
        )
        clear_btn.grid(row=0, column=3, padx=(5, 0))

    def _create_main_content(self):
        """Create main content area"""
        # Progress bar (initially hidden)
        self.progress_bar = ProgressBar(self)
        # Don't grid it initially - let show() method handle placement

        # Main scrollable content
        self.main_content = ctk.CTkScrollableFrame(
            self,
            label_text="COURSES",
            label_font=ctk.CTkFont(size=16, weight="bold")
        )
        self.main_content.grid(row=1, column=1, padx=(5, 10), pady=(5, 5), sticky="nsew")

        # Loading spinner (initially hidden)
        self.loading_frame = ctk.CTkFrame(self.main_content)
        self.loading_spinner = LoadingSpinner(self.loading_frame)
        self.loading_spinner.pack(pady=20)
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Loading courses...")
        self.loading_label.pack(pady=(0, 20))

    def _create_status_bar(self):
        """Create bottom status bar with pagination and info"""
        self.status_bar = ctk.CTkFrame(self, height=50, corner_radius=10)
        self.status_bar.grid(row=2, column=1, padx=(5, 10), pady=(5, 10), sticky="ew")
        self.status_bar.grid_columnconfigure(1, weight=1)

        # Pagination controls
        pagination_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        pagination_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.prev_button = ctk.CTkButton(
            pagination_frame,
            text="< Previous",
            width=100,
            state="disabled"
        )
        self.prev_button.pack(side="left", padx=(0, 5))

        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="Page 1 / 1",
            font=ctk.CTkFont(weight="bold")
        )
        self.page_label.pack(side="left", padx=10)

        self.next_button = ctk.CTkButton(
            pagination_frame,
            text="Next >",
            width=100,
            state="disabled"
        )
        self.next_button.pack(side="left", padx=(5, 0))

        # Status info
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            text_color="gray70"
        )
        self.status_label.grid(row=0, column=1, pady=5)

        # Course count
        self.count_label = ctk.CTkLabel(
            self.status_bar,
            text="0 courses",
            font=ctk.CTkFont(weight="bold")
        )
        self.count_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")

    def _setup_menu(self):
        """Setup application menu (placeholder for future enhancement)"""
        # In a production app, you might want to add a proper menu bar
        pass

    def display_courses(self, courses_data: Optional[List[Dict]]):
        """Display courses with improved performance using background threading"""
        # Clear existing course cards immediately
        for card in self.course_cards:
            card.destroy()
        self.course_cards.clear()

        if not courses_data:
            # Hide loading and show "no courses" message
            self.loading_frame.pack_forget()

            no_courses_frame = ctk.CTkFrame(self.main_content)
            no_courses_frame.pack(fill="x", padx=20, pady=50)

            no_courses_label = ctk.CTkLabel(
                no_courses_frame,
                text="No courses found",
                font=ctk.CTkFont(size=18, weight="bold")
            )
            no_courses_label.pack(pady=20)

            suggestion_label = ctk.CTkLabel(
                no_courses_frame,
                text="Try changing your search criteria or category filter",
                text_color="gray60"
            )
            suggestion_label.pack(pady=(0, 20))

            self.course_cards.append(no_courses_frame)
            self.count_label.configure(text="0 courses")
            return

        # Store current data for search
        self.current_courses_data = courses_data

        # Update status to show we're building the UI
        self.set_status("Building course cards...", "blue")
        self.loading_label.configure(text=f"Building {len(courses_data)} course cards...")

        # Start background thread to create course cards
        threading.Thread(
            target=self._create_course_cards_background,
            args=(courses_data,),
            daemon=True
        ).start()

    def _create_course_cards_background(self, courses_data: List[Dict]):
        """Create course cards in background thread with batching for smooth UI"""
        try:
            # Process courses in batches for smoother loading
            batch_size = 5
            total_courses = len(courses_data)
            created_cards = []

            for i in range(0, total_courses, batch_size):
                batch = courses_data[i:i + batch_size]
                batch_cards = []

                # Create cards for this batch (still in background)
                for course in batch:
                    try:
                        # Pre-process course data to avoid main thread work
                        processed_course = self._preprocess_course_data(course)
                        batch_cards.append(processed_course)
                    except Exception as e:
                        print(f"Error preprocessing course: {e}")
                        # Add a simple error placeholder
                        batch_cards.append({
                            'name': course.get('name', 'Error loading course'),
                            'error': str(e)[:100],
                            'category': course.get('category', 'Unknown'),
                            'rating': 'N/A',
                            'description': 'Error loading course data'
                        })

                created_cards.extend(batch_cards)

                # Update progress on main thread
                progress = (i + len(batch)) / total_courses
                self.after(0, lambda p=progress, count=len(created_cards):
                           self._update_card_creation_progress(p, count, total_courses))

                # Small delay between batches to keep UI responsive
                time.sleep(0.01)

            # Schedule final UI update on main thread
            self.after(0, lambda: self._finalize_course_display(created_cards))

        except Exception as e:
            print(f"Error in background card creation: {e}")
            # Fallback to main thread
            self.after(0, lambda err=e: self._handle_card_creation_error(str(err)))

    def _preprocess_course_data(self, course: Dict) -> Dict:
        """Preprocess course data in background to reduce main thread work"""
        processed = course.copy()

        # Pre-clean HTML description
        description = course.get('description', '')
        if description:
            clean_desc = clean_html(description)
            processed['clean_description'] = clean_desc[:120] + "..." if len(clean_desc) > 120 else clean_desc
        else:
            processed['clean_description'] = ''

        # Pre-format time ago
        sale_start = course.get('sale_start', '')
        processed['time_ago'] = format_time_ago(sale_start) if sale_start else ""

        # Pre-process price
        price = course.get('price', 0)
        try:
            if isinstance(price, str):
                processed['price_val'] = float(price) if price.replace('.', '', 1).isdigit() else 0
            else:
                processed['price_val'] = float(price) if price else 0
        except (ValueError, TypeError):
            processed['price_val'] = 0

        # Pre-process lectures/duration
        lectures = course.get('lectures', 'N/A')
        try:
            if lectures != 'N/A' and lectures:
                if isinstance(lectures, (int, float)):
                    processed['duration'] = f"{lectures} hours"
                elif isinstance(lectures, str) and lectures.replace('.', '', 1).isdigit():
                    processed['duration'] = f"{float(lectures):.0f} hours"
                else:
                    processed['duration'] = "Duration N/A"
            else:
                processed['duration'] = "Duration N/A"
        except (ValueError, TypeError):
            processed['duration'] = "Duration N/A"

        return processed

    def _update_card_creation_progress(self, progress: float, created_count: int, total_count: int):
        """Update progress during card creation"""
        self.loading_label.configure(text=f"Creating course cards... ({created_count}/{total_count})")
        # Update progress bar if visible
        if hasattr(self, 'progress_bar') and self.progress_bar.winfo_viewable():
            self.progress_bar.update(progress, f"Creating cards: {created_count}/{total_count}")

    def _finalize_course_display(self, processed_courses: List[Dict]):
        """Finalize course display on main thread with preprocessed data"""
        try:
            # Hide loading first
            self.loading_frame.pack_forget()

            # Create optimized course cards using preprocessed data
            for processed_course in processed_courses:
                if 'error' in processed_course:
                    # Create simple error card
                    card = self._create_error_card(processed_course)
                else:
                    # Create optimized course card
                    card = self._create_optimized_course_card(processed_course)

                if card:
                    card.pack(fill="x", padx=10, pady=8)
                    self.course_cards.append(card)

            # Update UI
            self.count_label.configure(text=f"{len(processed_courses)} courses")
            self.set_status(f"Loaded {len(processed_courses)} courses", "green")

        except Exception as e:
            print(f"Error finalizing course display: {e}")
            self._handle_card_creation_error(str(e))

    def _create_error_card(self, course_data: Dict) -> ctk.CTkFrame:
        """Create a simple error card for failed courses"""
        card = ctk.CTkFrame(
            self.main_content,
            corner_radius=8,
            fg_color="#2a1a1a",
            border_width=1,
            border_color="#ff4444"
        )

        error_label = ctk.CTkLabel(
            card,
            text=f"Error loading: {course_data.get('name', 'Unknown course')}\n"
                 f"{course_data.get('error', 'Unknown error')}",
            text_color="#ff6666",
            font=ctk.CTkFont(size=12),
            wraplength=600
        )
        error_label.pack(pady=15, padx=20)

        return card

    def _create_optimized_course_card(self, processed_course: Dict) -> ctk.CTkFrame:
        """Create an optimized course card using preprocessed data"""
        try:
            # Create the main card frame
            card = ctk.CTkFrame(
                self.main_content,
                corner_radius=12,
                fg_color="#1a1a1a",
                border_width=1,
                border_color="#333333"
            )
            card.grid_columnconfigure(0, weight=1)

            # Header with title and rating
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            header_frame.grid_columnconfigure(0, weight=1)

            # Course Title
            title_text = processed_course.get('name', 'Unknown Course')
            title_label = ctk.CTkLabel(
                header_frame,
                text=title_text,
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w",
                wraplength=600,
                justify="left",
                text_color="#ffffff"
            )
            title_label.grid(row=0, column=0, sticky="ew")

            # Rating badge
            rating = processed_course.get('rating', 'N/A')
            if rating != 'N/A':
                rating_frame = ctk.CTkFrame(header_frame, fg_color="#FF6B35", corner_radius=8)
                rating_frame.grid(row=0, column=1, padx=(10, 0), sticky="e")

                rating_label = ctk.CTkLabel(
                    rating_frame,
                    text=f"RATING: {rating}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#ffffff"
                )
                rating_label.pack(padx=8, pady=4)

            # Meta information using preprocessed data
            meta_frame = ctk.CTkFrame(card, fg_color="transparent")
            meta_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

            category = processed_course.get('category', 'General')
            duration = processed_course.get('duration', 'Duration N/A')
            time_ago = processed_course.get('time_ago', "")
            meta_items = [
                ("Category", category, "#4A90E2"),
                ("Duration", duration, "#50C878"),
            ]
            if time_ago:
                meta_items.append(("Posted", time_ago, "#9B59B6"))

            for i, (label, value, color) in enumerate(meta_items):
                chip_frame = ctk.CTkFrame(meta_frame, fg_color=color, corner_radius=6)
                chip_frame.grid(row=0, column=i, padx=(0, 8), sticky="w")

                chip_label = ctk.CTkLabel(
                    chip_frame,
                    text=f"{label}: {value}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#ffffff"
                )
                chip_label.pack(padx=6, pady=2)

            # Description using preprocessed clean description
            clean_desc = processed_course.get('clean_description', '')
            if clean_desc:
                desc_label = ctk.CTkLabel(
                    card,
                    text=clean_desc,
                    text_color="#CCCCCC",
                    anchor="w",
                    wraplength=700,
                    justify="left",
                    font=ctk.CTkFont(size=11)
                )
                desc_label.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")

            # Action buttons
            buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
            buttons_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

            # Primary action button
            enroll_btn = ctk.CTkButton(
                buttons_frame,
                text="View Course",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#00A86B",
                hover_color="#008F5A",
                corner_radius=8,
                height=36,
                command=lambda: self._open_course_url(processed_course.get('url', ''))
            )
            enroll_btn.pack(side="left")

            # Secondary action
            share_btn = ctk.CTkButton(
                buttons_frame,
                text="Copy Link",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#333333",
                border_width=1,
                border_color="#555555",
                corner_radius=8,
                height=36,
                command=lambda: self._copy_course_url(processed_course.get('url', ''))
            )
            share_btn.pack(side="left", padx=(10, 0))

            # Price info using preprocessed price
            price_val = processed_course.get('price_val', 0)
            if price_val > 0:
                price_label = ctk.CTkLabel(
                    buttons_frame,
                    text=f"FREE (WAS ${price_val:.0f})",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#FF6B35"
                )
                price_label.pack(side="right")
            else:
                free_label = ctk.CTkLabel(
                    buttons_frame,
                    text="FREE",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#00A86B"
                )
                free_label.pack(side="right")

            return card

        except Exception as e:
            print(f"Error creating optimized course card: {e}")
            # Return a simple error card instead
            return self._create_error_card({
                'name': processed_course.get('name', 'Unknown Course'),
                'error': str(e)
            })

    def _open_course_url(self, url: str):
        """Open course URL in browser"""
        if url:
            webbrowser.open(url)
        else:
            messagebox.showwarning("Warning", "No URL available for this course.")

    def _copy_course_url(self, url: str):
        """Copy course URL to clipboard"""
        if url:
            pyperclip.copy(url)
            messagebox.showinfo("Success", "Course URL copied to clipboard!")
        else:
            messagebox.showwarning("Warning", "No URL available for this course.")

    def _handle_card_creation_error(self, error_msg: str):
        """Handle errors during card creation"""
        self.loading_frame.pack_forget()
        self.set_status(f"Error creating course cards: {error_msg}", "red")

        # Show error message
        error_frame = ctk.CTkFrame(self.main_content)
        error_frame.pack(fill="x", padx=20, pady=50)

        error_label = ctk.CTkLabel(
            error_frame,
            text="Error loading courses. Please try refreshing.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ff6666"
        )
        error_label.pack(pady=20)

        self.course_cards.append(error_frame)

    def show_loading(self, message: str = "Loading courses..."):
        """Show loading indicator"""
        # Clear existing content
        for card in self.course_cards:
            card.destroy()
        self.course_cards.clear()

        # Show loading
        self.loading_label.configure(text=message)
        self.loading_frame.pack(fill="x", padx=20, pady=50)
        self.loading_spinner.start()

        # Update status
        self.status_label.configure(text="Loading...")
        self.count_label.configure(text="...")

    def hide_loading(self):
        """Hide loading indicator"""
        self.loading_spinner.stop()
        self.loading_frame.pack_forget()

    def update_pagination(self, current_page: int, total_pages: int):
        """Update pagination controls"""
        self.page_label.configure(text=f"Page {current_page} / {total_pages}")

        # Update button states
        self.prev_button.configure(
            state="normal" if current_page > 1 else "disabled"
        )
        self.next_button.configure(
            state="normal" if current_page < total_pages else "disabled"
        )

    def set_status(self, message: str, color: str = "gray70"):
        """Update status bar message"""
        self.status_label.configure(text=message, text_color=color)

    def _on_sort_change(self, value):
        """Handle sort option change"""
        # This would be connected to the main application logic
        self.set_status(f"Sorting by {value}...")

    def _on_search_enter(self, event):
        """Handle search when Enter is pressed"""
        self._perform_search()

    def _perform_search(self):
        """Perform search - either local filtering or API search"""
        search_text = self.search_entry.get().lower().strip()

        if not search_text:
            # Show all courses
            self.display_courses(self.current_courses_data)
            self.set_status("Search cleared")
            return

        # Filter courses locally
        filtered_courses = []
        for course in self.current_courses_data:
            title = course.get('name', '').lower()
            category = course.get('category', '').lower()
            instructor = course.get('instructor', '').lower()

            if (
                search_text in title or
                search_text in category or
                search_text in instructor
            ):
                filtered_courses.append(course)

        self.display_courses(filtered_courses)
        self.set_status(f"Found {len(filtered_courses)} courses matching '{search_text}'")

    def _clear_search(self):
        """Clear search and show all courses"""
        self.search_entry.delete(0, 'end')
        self.display_courses(self.current_courses_data)
        self.set_status("Search cleared")

    def _refresh_courses(self):
        """Refresh course list"""
        self.set_status("Refreshing courses...")
        # This would be connected to the main application logic

    def _export_courses(self):
        """Export courses to file"""
        if not self.current_courses_data:
            messagebox.showwarning("Warning", "No courses to export.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Courses",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_courses_data, f, indent=2, ensure_ascii=False)
                elif file_path.endswith('.csv'):
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        if self.current_courses_data:
                            writer = csv.DictWriter(f, fieldnames=self.current_courses_data[0].keys())
                            writer.writeheader()
                            writer.writerows(self.current_courses_data)
                else:
                    # Text format
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for course in self.current_courses_data:
                            f.write(f"Title: {course.get('name', 'N/A')}\n")
                            f.write(f"Category: {course.get('category', 'N/A')}\n")
                            f.write(f"Rating: {course.get('rating', 'N/A')}\n")
                            f.write(f"URL: {course.get('url', 'N/A')}\n")
                            f.write("-" * 50 + "\n")

                messagebox.showinfo("Success", f"Courses exported to {file_path}")
                self.set_status(f"Exported {len(self.current_courses_data)} courses")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export courses: {e}")

    def _show_settings(self):
        """Show settings window"""
        settings_window = SettingsWindow(self, self.settings)
        settings_window.show()
