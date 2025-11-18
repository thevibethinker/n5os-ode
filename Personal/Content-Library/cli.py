#!/usr/bin/env python3
"""
Content Library Query CLI - Main Entry Point
"""

import sys
from pathlib import Path

# Add the query module to path
query_path = Path(__file__).parent / "query"
sys.path.insert(0, str(query_path))

from cli import main

if __name__ == '__main__':
    main()

