# improved_cache_manager.py
import hashlib
import json
from pathlib import Path
import threading
import time
from typing import Optional, Dict, Any


class CacheManager:
    """Improved cache manager with thread safety and better error handling"""

    def __init__(self, cache_dir: str = "cache", default_duration: int = 6 * 60 * 60):
        self.cache_dir = Path(cache_dir)
        self.default_duration = default_duration  # 6 hours in seconds
        self.lock = threading.RLock()

        # Ensure cache directory exists
        self._ensure_cache_dir()

        # Clean up expired cache on startup
        self._cleanup_expired_cache()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Warning: Could not create cache directory {self.cache_dir}: {e}")

    def _cleanup_expired_cache(self):
        """Clean up expired cache files on startup"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                if self._is_cache_expired(cache_file):
                    try:
                        cache_file.unlink()
                        print(f"Removed expired cache file: {cache_file.name}")
                    except OSError as e:
                        print(f"Warning: Could not remove expired cache file {cache_file}: {e}")
        except Exception as e:
            print(f"Warning: Error during cache cleanup: {e}")

    def _get_cache_path(self, page: int, category: str, sort: str, search: Optional[str] = None) -> Path:
        """Creates a unique filename for each API request"""
        # Create a hash for the search parameter to handle special characters
        search_hash = ""
        if search:
            search_hash = hashlib.md5(search.encode('utf-8')).hexdigest()[:8]

        if search_hash:
            filename = f"{category}_{sort}_{page}_{search_hash}.json"
        else:
            filename = f"{category}_{sort}_{page}.json"

        return self.cache_dir / filename

    def _is_cache_expired(self, cache_path: Path, duration: Optional[int] = None) -> bool:
        """Check if cache file is expired"""
        if not cache_path.exists():
            return True

        cache_duration = duration or self.default_duration
        try:
            file_age = time.time() - cache_path.stat().st_mtime
            return file_age > cache_duration
        except OSError:
            return True

    def get_cached_data(
        self,
        page: int,
        category: str,
        sort: str,
        search: Optional[str] = None,
        max_age: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Retrieves data from cache if it's not expired.

        Args:
            page: Page number
            category: Course category
            sort: Sort method
            search: Search query
            max_age: Maximum age in seconds (overrides default)

        Returns:
            Cached data or None if not found/expired
        """
        with self.lock:
            cache_path = self._get_cache_path(page, category, sort, search)

            if not cache_path.exists():
                return None

            # Check if cache is expired
            if self._is_cache_expired(cache_path, max_age):
                print(f"Cache expired for {cache_path.name}")
                try:
                    cache_path.unlink()
                except OSError as e:
                    print(f"Warning: Could not remove expired cache file: {e}")
                return None

            # Load and validate cache data
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Validate cache structure
                if not isinstance(data, dict):
                    print(f"Invalid cache structure in {cache_path.name}")
                    return None

                # Add cache metadata
                data['_cache_info'] = {
                    'loaded_from_cache': True,
                    'cache_file': cache_path.name,
                    'cached_at': cache_path.stat().st_mtime,
                    'age_seconds': time.time() - cache_path.stat().st_mtime
                }

                print(f"Loading from cache: {cache_path.name}")
                return data

            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading cache file {cache_path.name}: {e}")
                try:
                    cache_path.unlink()
                except OSError:
                    pass
                return None

    def set_cached_data(
        self,
        page: int,
        category: str,
        sort: str,
        data: Dict,
        search: Optional[str] = None
    ) -> bool:
        """
        Saves data to a cache file.

        Args:
            page: Page number
            category: Course category
            sort: Sort method
            data: Data to cache
            search: Search query

        Returns:
            True if successfully cached, False otherwise
        """
        with self.lock:
            cache_path = self._get_cache_path(page, category, sort, search)

            try:
                # Add cache metadata to data
                cache_data = data.copy()
                cache_data['_cache_info'] = {
                    'cached_at': time.time(),
                    'cache_file': cache_path.name,
                    'page': page,
                    'category': category,
                    'sort': sort,
                    'search': search,
                    'version': '1.0'
                }

                # Write to temporary file first, then rename for atomic operation
                temp_path = cache_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)

                # Atomic rename
                temp_path.replace(cache_path)
                print(f"Cached data to: {cache_path.name}")
                return True

            except (OSError, TypeError) as e:
                print(f"Error caching data to {cache_path.name}: {e}")
                # Clean up temporary file if it exists
                temp_path = cache_path.with_suffix('.tmp')
                if temp_path.exists():
                    try:
                        temp_path.unlink()
                    except OSError:
                        pass
                return False

    def clear_cache(self, category: Optional[str] = None) -> int:
        """
        Clear cache files.

        Args:
            category: If specified, only clear cache for this category

        Returns:
            Number of files removed
        """
        with self.lock:
            removed_count = 0
            try:
                pattern = f"{category}_*.json" if category else "*.json"
                for cache_file in self.cache_dir.glob(pattern):
                    try:
                        cache_file.unlink()
                        removed_count += 1
                        print(f"Removed cache file: {cache_file.name}")
                    except OSError as e:
                        print(f"Warning: Could not remove cache file {cache_file}: {e}")

            except Exception as e:
                print(f"Error during cache clear: {e}")

            return removed_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            stats = {
                'total_files': 0,
                'total_size_bytes': 0,
                'expired_files': 0,
                'categories': set(),
                'oldest_file': None,
                'newest_file': None,
                'cache_dir': str(self.cache_dir),
                'default_duration_hours': self.default_duration / 3600
            }

            try:
                cache_files = list(self.cache_dir.glob("*.json"))
                stats['total_files'] = len(cache_files)

                if cache_files:
                    file_times = []
                    for cache_file in cache_files:
                        try:
                            file_stat = cache_file.stat()
                            stats['total_size_bytes'] += file_stat.st_size
                            file_times.append(file_stat.st_mtime)

                            # Check if expired
                            if self._is_cache_expired(cache_file):
                                stats['expired_files'] += 1

                            # Extract category from filename
                            parts = cache_file.stem.split('_')
                            if parts:
                                stats['categories'].add(parts[0])

                        except OSError:
                            continue

                    if file_times:
                        stats['oldest_file'] = time.ctime(min(file_times))
                        stats['newest_file'] = time.ctime(max(file_times))

                # Convert set to list for JSON serialization
                stats['categories'] = list(stats['categories'])

            except Exception as e:
                print(f"Error getting cache stats: {e}")

            return stats

    def optimize_cache(self) -> Dict[str, int]:
        """
        Optimize cache by removing expired files and duplicates.

        Returns:
            Dictionary with optimization results
        """
        with self.lock:
            results = {
                'expired_removed': 0,
                'duplicates_removed': 0,
                'total_removed': 0
            }

            try:
                # Remove expired files
                for cache_file in self.cache_dir.glob("*.json"):
                    if self._is_cache_expired(cache_file):
                        try:
                            cache_file.unlink()
                            results['expired_removed'] += 1
                        except OSError as e:
                            print(f"Warning: Could not remove expired file {cache_file}: {e}")

                # TODO: Implement duplicate detection based on content hash
                # This would be useful for identical API responses cached with different keys

                results['total_removed'] = results['expired_removed'] + results['duplicates_removed']

            except Exception as e:
                print(f"Error during cache optimization: {e}")

            return results

    def export_cache_data(self, output_path: str) -> bool:
        """
        Export all cache data to a single file.

        Args:
            output_path: Path to output file

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                all_data = {}
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            all_data[cache_file.stem] = data
                    except (json.JSONDecodeError, OSError) as e:
                        print(f"Warning: Could not read cache file {cache_file}: {e}")
                        continue

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)

                print(f"Exported cache data to: {output_path}")
                return True

            except Exception as e:
                print(f"Error exporting cache data: {e}")
                return False


# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get or create the global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Backward compatibility functions
def get_cached_data(page: int, category: str, sort: str, search: Optional[str] = None) -> Optional[Dict]:
    """Get cached data (backward compatibility)"""
    manager = get_cache_manager()
    return manager.get_cached_data(page, category, sort, search)


def set_cached_data(page: int, category: str, sort: str, data: Dict, search: Optional[str] = None) -> bool:
    """Set cached data (backward compatibility)"""
    manager = get_cache_manager()
    return manager.set_cached_data(page, category, sort, data, search)


def clear_cache(category: Optional[str] = None) -> int:
    """Clear cache (backward compatibility)"""
    manager = get_cache_manager()
    return manager.clear_cache(category)


def get_cache_info() -> Dict[str, Any]:
    """Get cache information"""
    manager = get_cache_manager()
    return {
        'stats': manager.get_cache_stats(),
        'cache_dir': str(manager.cache_dir),
        'default_duration_hours': manager.default_duration / 3600
    }
