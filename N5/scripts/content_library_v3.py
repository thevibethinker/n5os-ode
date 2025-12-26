#!/usr/bin/env python3
"""
Content Library V3 - Compatibility Wrapper
==========================================
This module is deprecated. Use content_library.py directly.

All functionality has been consolidated into content_library.py.
This wrapper exists for backward compatibility.
"""

# Re-export everything from the canonical module
from content_library import (
    ContentLibrary,
    ContentLibraryV3,
    ContentItem,
    DB_PATH,
    main,
)

__all__ = ["ContentLibrary", "ContentLibraryV3", "ContentItem", "DB_PATH", "main"]

if __name__ == "__main__":
    main()

