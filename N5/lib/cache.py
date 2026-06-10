"""
N5 Caching Utilities
====================

Provides in-memory caching with file-based invalidation for preferences
and other frequently accessed configuration files.

Features:
- LRU cache for parsed YAML/JSON files
- Automatic invalidation when source files change (mtime check)
- Thread-safe operations
- Cache statistics

Usage:
    from N5.lib.cache import get_cached_yaml, get_cached_preferences

    # Cache a YAML file (auto-invalidates on file change)
    data = get_cached_yaml("/path/to/config.yaml")

    # Get cached preferences for a context
    prefs = get_cached_preferences("system_ops")
"""

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from functools import lru_cache
import os

# Try to import yaml
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Import paths
from N5.lib.paths import N5_CONFIG_DIR, WORKSPACE_ROOT


class FileCache:
    """
    Thread-safe file cache with mtime-based invalidation.

    Caches parsed file contents and automatically invalidates
    when the source file is modified.
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of entries to cache
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, path: str, loader: Callable[[str], Any]) -> Any:
        """
        Get cached value or load from file.

        Args:
            path: File path to cache
            loader: Function to load/parse the file if not cached

        Returns:
            Parsed file contents
        """
        path = str(path)

        with self._lock:
            # Check if file exists
            if not os.path.exists(path):
                self._misses += 1
                return None

            current_mtime = os.path.getmtime(path)

            # Check cache
            if path in self._cache:
                entry = self._cache[path]
                if entry['mtime'] == current_mtime:
                    self._hits += 1
                    # Move to end (LRU behavior)
                    self._cache[path] = self._cache.pop(path)
                    return entry['data']

            # Cache miss or stale - load file
            self._misses += 1
            data = loader(path)

            # Evict oldest if at capacity
            if len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            # Store in cache
            self._cache[path] = {
                'data': data,
                'mtime': current_mtime,
                'cached_at': time.time()
            }

            return data

    def invalidate(self, path: str = None):
        """
        Invalidate cache entry or entire cache.

        Args:
            path: Specific path to invalidate, or None for all
        """
        with self._lock:
            if path is None:
                self._cache.clear()
            elif path in self._cache:
                del self._cache[path]

    @property
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'entries': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.1f}%"
            }


# =============================================================================
# GLOBAL CACHE INSTANCES
# =============================================================================

_yaml_cache = FileCache(max_size=50)
_json_cache = FileCache(max_size=50)
_preferences_cache: Dict[str, Dict[str, Any]] = {}
_preferences_lock = threading.RLock()
_hub_mtime: Optional[float] = None


# =============================================================================
# YAML/JSON CACHING
# =============================================================================

def _load_yaml(path: str) -> Any:
    """Load and parse YAML file."""
    if not HAS_YAML:
        raise ImportError("PyYAML not installed")
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def _load_json(path: str) -> Any:
    """Load and parse JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def get_cached_yaml(path: str | Path) -> Any:
    """
    Get cached YAML file contents.

    Automatically invalidates when file is modified.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML contents
    """
    return _yaml_cache.get(str(path), _load_yaml)


def get_cached_json(path: str | Path) -> Any:
    """
    Get cached JSON file contents.

    Automatically invalidates when file is modified.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON contents
    """
    return _json_cache.get(str(path), _load_json)


# =============================================================================
# PREFERENCES CACHING
# =============================================================================

def _get_hub_file() -> Path:
    """Get path to preferences hub file."""
    return N5_CONFIG_DIR / "user_preferences.yaml"


def _hub_changed() -> bool:
    """Check if hub file has been modified since last load."""
    global _hub_mtime
    hub_path = _get_hub_file()
    if not hub_path.exists():
        return True
    current_mtime = hub_path.stat().st_mtime
    if _hub_mtime is None or current_mtime != _hub_mtime:
        return True
    return False


def get_cached_hub() -> Dict[str, Any]:
    """
    Get cached preferences hub.

    Returns:
        Parsed hub configuration
    """
    global _hub_mtime
    hub_path = _get_hub_file()

    with _preferences_lock:
        if _hub_changed():
            # Invalidate all preference caches when hub changes
            _preferences_cache.clear()
            _hub_mtime = hub_path.stat().st_mtime if hub_path.exists() else None

        return get_cached_yaml(hub_path)


def get_cached_preferences(context: str, include_content: bool = False) -> Dict[str, Any]:
    """
    Get cached preferences for a context.

    Caches the resolved preferences (modules, overrides, etc.) for each context.
    Automatically invalidates when hub file changes.

    Args:
        context: Context name (e.g., 'system_ops', 'content_generation')
        include_content: Whether to include module file contents

    Returns:
        Resolved preferences dict with:
        - context: Context name
        - core: Core preferences
        - modules: List of module configs
        - overrides: User overrides
        - content: Module contents (if include_content=True)
    """
    cache_key = f"{context}:{'content' if include_content else 'no_content'}"

    with _preferences_lock:
        # Check if hub changed (this also clears cache if needed)
        hub = get_cached_hub()
        if hub is None:
            return {}

        # Check cache
        if cache_key in _preferences_cache:
            return _preferences_cache[cache_key]

        # Resolve preferences
        result = _resolve_preferences(hub, context, include_content)

        # Cache result
        _preferences_cache[cache_key] = result
        return result


def _resolve_preferences(hub: Dict[str, Any], context: str, include_content: bool) -> Dict[str, Any]:
    """
    Resolve preferences for a context (internal implementation).

    This mirrors the logic in load_preferences.py but uses caching.
    """
    result = {
        "context": context,
        "core": hub.get("core", {}),
        "precedence": hub.get("precedence", []),
        "modules": [],
        "overrides": {},
        "content": {}
    }

    # Get always-loaded modules
    always_modules = []
    for name, config in hub.get("modules", {}).items():
        if config.get("load") == "always" and not config.get("deprecated", False):
            always_modules.append(name)

    # Get context-specific modules
    context_modules = []
    contexts = hub.get("contexts", {})
    if context in contexts:
        ctx_config = contexts[context]
        load_spec = ctx_config.get("load", [])
        if load_spec == "all":
            context_modules = [
                name for name, config in hub.get("modules", {}).items()
                if not config.get("deprecated", False)
            ]
        else:
            context_modules = load_spec

    # Combine and dedupe
    all_module_names = list(dict.fromkeys(always_modules + context_modules))

    # Build module list with full config
    modules_config = hub.get("modules", {})
    for name in all_module_names:
        if name in modules_config:
            module = modules_config[name].copy()
            module["name"] = name
            result["modules"].append(module)

            if include_content:
                module_path = WORKSPACE_ROOT / module["path"]
                if module_path.exists():
                    # Use cached file read
                    try:
                        with open(module_path, 'r') as f:
                            result["content"][name] = f.read()
                    except Exception:
                        pass

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    result["modules"].sort(key=lambda m: priority_order.get(m.get("priority", "low"), 3))

    # Load overrides (cached)
    overrides_path = hub.get("overrides_file")
    if overrides_path:
        overrides_file = WORKSPACE_ROOT / overrides_path
        if overrides_file.exists():
            result["overrides"] = get_cached_yaml(overrides_file) or {}

    return result


def invalidate_preferences():
    """Invalidate all preference caches."""
    global _hub_mtime
    with _preferences_lock:
        _preferences_cache.clear()
        _hub_mtime = None
    _yaml_cache.invalidate()


# =============================================================================
# CACHE STATISTICS
# =============================================================================

def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all caches."""
    with _preferences_lock:
        return {
            'yaml_cache': _yaml_cache.stats,
            'json_cache': _json_cache.stats,
            'preferences_cache': {
                'entries': len(_preferences_cache),
                'contexts': list(_preferences_cache.keys())
            }
        }


def clear_all_caches():
    """Clear all caches (use for testing or manual refresh)."""
    global _hub_mtime
    with _preferences_lock:
        _preferences_cache.clear()
        _hub_mtime = None
    _yaml_cache.invalidate()
    _json_cache.invalidate()
