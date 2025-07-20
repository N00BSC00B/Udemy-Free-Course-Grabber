# improved_api_client.py
import json
import re
import requests
import time
from typing import Optional, Dict


# Filter dicts for the UI to use
SORT_BY = {
    "Date": "sale_start",
    "Duration": "lectures",
    "Popularity": "views",
    "Rating": "rating",
}

# Simplified category list - no URL encoding here, will be done in request
CATEGORIES = [
    "Business",
    "Design",
    "Development",
    "Finance & Accounting",
    "Health & Fitness",
    "IT & Software",
    "Lifestyle",
    "Marketing",
    "Music",
    "Office Productivity",
    "Personal Development",
    "Photography & Video",
    "Teaching & Academics"
]


class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class RateLimiter:
    """Simple rate limiter to avoid API abuse"""
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def can_make_request(self) -> bool:
        """Check if we can make a request"""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

        return len(self.requests) < self.max_requests

    def record_request(self):
        """Record that a request was made"""
        self.requests.append(time.time())

    def wait_time(self) -> float:
        """Get the time to wait before next request"""
        if not self.requests:
            return 0

        oldest_request = min(self.requests)
        return max(0, self.time_window - (time.time() - oldest_request))


class ImprovedAPIClient:
    """Improved API client with retry logic, error handling, and rate limiting"""

    def __init__(self, settings: Optional[Dict] = None):
        self.settings = settings or self._load_default_settings()
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)
        self.base_url = "https://cdn.real.discount/api/courses"
        self.session = requests.Session()

        # Configure session
        self.session.headers.update({
            'User-Agent': 'Udemy-Course-Grabber/1.0 (Educational Use)',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })

    def _load_default_settings(self) -> Dict:
        """Load default settings"""
        return {
            'timeout': 10,
            'retry_attempts': 3,
            'retry_delay': 1.0,
            'courses_per_page': 20
        }

    def get_courses(
        self,
        page: int = 1,
        sort: str = "Date",
        category: str = "All",
        search: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Fetches free Udemy courses from the RealDiscount API with improved error handling.

        Args:
            page: Page number to fetch
            sort: Sort method ("Date", "Duration", "Popularity", "Rating")
            category: Course category filter
            search: Search query (if supported by API)
            limit: Number of courses per page

        Returns:
            Dictionary containing course data and metadata, or None if failed
        """
        # Check rate limiting
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            raise APIError(f"Rate limit exceeded. Please wait {wait_time:.1f} seconds.")

        # Prepare parameters
        sort_val = SORT_BY.get(sort, "sale_start")

        params = {
            "page": page,
            "limit": limit or self.settings.get('courses_per_page', 20),
            "sortBy": sort_val,
        }

        if search:
            params["search"] = search
        if category and category != "All" and category in CATEGORIES:
            params["category"] = category
        params["store"] = "Udemy"
        params["freeOnly"] = "true"

        # Make request with retry logic
        for attempt in range(self.settings.get('retry_attempts', 3)):
            try:
                response = self._make_request(params)
                self.rate_limiter.record_request()

                if response:
                    # Add metadata
                    response['_metadata'] = {
                        'fetched_at': time.time(),
                        'page': page,
                        'category': category,
                        'sort': sort,
                        'search': search,
                        'api_version': '1.0'
                    }

                return response

            except APIError as e:
                if attempt == self.settings.get('retry_attempts', 3) - 1:
                    # Last attempt failed
                    raise e

                # Wait before retry with exponential backoff
                wait_time = self.settings.get('retry_delay', 1.0) * (2 ** attempt)
                print(f"API request failed (attempt {attempt + 1}), retrying in {wait_time:.1f}s: {e}")
                time.sleep(wait_time)

            except Exception as e:
                if attempt == self.settings.get('retry_attempts', 3) - 1:
                    raise APIError(f"Unexpected error: {str(e)}")

                wait_time = self.settings.get('retry_delay', 1.0) * (2 ** attempt)
                print(f"Unexpected error (attempt {attempt + 1}), retrying in {wait_time:.1f}s: {e}")
                time.sleep(wait_time)

        return None

    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make the actual HTTP request"""
        try:
            timeout = self.settings.get('timeout', 10)
            response = self.session.get(self.base_url, params=params, timeout=timeout)
            print(response.url)

            # Check for HTTP errors
            if response.status_code == 429:
                raise APIError("Rate limited by server", response.status_code)
            elif response.status_code == 503:
                raise APIError("Service temporarily unavailable", response.status_code)
            elif response.status_code >= 500:
                raise APIError(f"Server error: {response.status_code}", response.status_code)
            elif response.status_code == 404:
                raise APIError("API endpoint not found", response.status_code)
            elif response.status_code >= 400:
                raise APIError(f"Client error: {response.status_code}", response.status_code, response.text)

            response.raise_for_status()

            # Parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise APIError(f"Invalid JSON response: {e}", response.status_code, response.text)

            # Validate response structure
            if not isinstance(data, dict):
                raise APIError("Invalid response format: expected object")

            # Ensure we have the expected fields
            if 'items' not in data:
                # Some APIs might return courses directly as a list
                if isinstance(data, list):
                    data = {'items': data, 'totalPages': 1, 'currentPage': 1}
                else:
                    # Assume the entire response is the items
                    data = {'items': [data] if data else [], 'totalPages': 1, 'currentPage': 1}

            # Validate and clean course data
            cleaned_items = []
            for item in data.get('items', []):
                cleaned_item = self._clean_course_data(item)
                if cleaned_item:
                    cleaned_items.append(cleaned_item)

            data['items'] = cleaned_items

            return data

        except requests.exceptions.Timeout:
            raise APIError(f"Request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIError("Network connection error")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request error: {str(e)}")

    def _clean_course_data(self, course: Dict) -> Optional[Dict]:
        """Clean and validate individual course data"""
        if not isinstance(course, dict):
            return None

        # Required fields with defaults
        cleaned = {
            'name': course.get('name') or course.get('title') or 'Unknown Course',
            'url': course.get('url') or course.get('link') or '',
            'category': course.get('category') or 'General',
            'rating': self._clean_rating(course.get('rating')),
            'image': course.get('image') or course.get('thumbnail') or '',
            'description': course.get('description') or course.get('summary') or '',
            'instructor': course.get('instructor') or course.get('author') or 'Unknown',
            'duration': self._clean_duration(course.get('duration')),
            'price': course.get('price') or 'Free',
            'discount': course.get('discount') or '100%',
            'students': course.get('students') or course.get('enrollments') or 0,
            'level': course.get('level') or 'All Levels',
            'language': course.get('language') or 'English',
            'last_updated': course.get('last_updated') or course.get('updated_at') or '',
            'lectures': course.get('lectures') or course.get('lessons') or 0,
            'expiry_date': course.get('expiry_date') or course.get('expires_at') or '',
            'sale_start': course.get('sale_start') or course.get('saleStart') or '',
            'sale_price': course.get('sale_price') or 0,
            'views': course.get('views') or 0,
        }

        # Only return courses with valid URLs
        if not cleaned['url']:
            return None

        return cleaned

    def _clean_rating(self, rating) -> str:
        """Clean and format rating value"""
        if rating is None:
            return "N/A"

        try:
            if isinstance(rating, (int, float)):
                return f"{float(rating):.1f}"
            elif isinstance(rating, str):
                # Try to extract number from string
                match = re.search(r'(\d+\.?\d*)', rating)
                if match:
                    return f"{float(match.group(1)):.1f}"

            return str(rating)
        except (ValueError, TypeError):
            return "N/A"

    def _clean_duration(self, duration) -> str:
        """Clean and format duration value"""
        if duration is None:
            return "N/A"

        try:
            if isinstance(duration, (int, float)):
                # Assume it's in hours
                if duration < 1:
                    return f"{int(duration * 60)}m"
                else:
                    return f"{duration:.1f}h"
            elif isinstance(duration, str):
                # Return as-is if it's already a string
                return duration

            return str(duration)
        except (ValueError, TypeError):
            return "N/A"

    def test_connection(self) -> bool:
        """Test if the API is accessible"""
        try:
            response = self.session.get(
                self.base_url,
                params={"page": 1, "limit": 1, "store": "Udemy", "freeOnly": "true", "sortBy": "sale_start"},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def get_api_status(self) -> Dict:
        """Get API status information"""
        status = {
            'accessible': False,
            'response_time': None,
            'last_error': None,
            'rate_limit_remaining': self.rate_limiter.max_requests - len(self.rate_limiter.requests)
        }

        try:
            start_time = time.time()
            accessible = self.test_connection()
            end_time = time.time()

            status['accessible'] = accessible
            status['response_time'] = round((end_time - start_time) * 1000, 2)  # ms

        except Exception as e:
            status['last_error'] = str(e)

        return status


# Global instance for backward compatibility
_default_client = None


def get_default_client(settings: Optional[Dict] = None) -> ImprovedAPIClient:
    """Get or create the default API client"""
    global _default_client
    if _default_client is None:
        _default_client = ImprovedAPIClient(settings)
    return _default_client


# Backward compatibility functions
def get_courses(page: int = 1, sort: str = "Date", category: str = "All") -> Optional[Dict]:
    """Legacy function for backward compatibility"""
    try:
        client = get_default_client()
        return client.get_courses(page=page, sort=sort, category=category)
    except Exception as e:
        print(f"Error fetching from API: {e}")
        return None


def test_api() -> bool:
    """Test API connectivity"""
    try:
        client = get_default_client()
        return client.test_connection()
    except Exception:
        return False


def get_api_info() -> Dict:
    """Get API information and status"""
    client = get_default_client()
    return {
        'status': client.get_api_status(),
        'base_url': client.base_url,
        'categories': ["All"] + CATEGORIES,
        'sort_options': list(SORT_BY.keys()),
        'rate_limit': {
            'max_requests': client.rate_limiter.max_requests,
            'time_window': client.rate_limiter.time_window,
            'current_requests': len(client.rate_limiter.requests)
        }
    }
