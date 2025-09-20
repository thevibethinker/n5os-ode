#!/usr/bin/env python3
"""
Cache Manager for System Prep
Manages temporary files and document distribution
"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class CacheManager:
    def __init__(self, cache_dir: str = "/home/workspace/system_prep/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"files": {}, "created_at": datetime.now().isoformat()}
    
    def _save_metadata(self):
        """Save cache metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def add_file(self, source_path: str, category: str = "general") -> str:
        """Add a file to cache with metadata"""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Generate unique filename with hash
        file_hash = hashlib.md5(source.read_bytes()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cached_filename = f"{category}_{timestamp}_{file_hash}{source.suffix}"
        cached_path = self.cache_dir / cached_filename
        
        # Copy file to cache
        shutil.copy2(source, cached_path)
        
        # Update metadata
        self.metadata["files"][cached_filename] = {
            "original_path": str(source.absolute()),
            "category": category,
            "timestamp": timestamp,
            "hash": file_hash,
            "size": source.stat().st_size
        }
        self._save_metadata()
        
        return str(cached_path)
    
    def list_files(self, category: Optional[str] = None) -> List[Dict]:
        """List cached files, optionally filtered by category"""
        files = []
        for filename, info in self.metadata["files"].items():
            if category is None or info["category"] == category:
                info["filename"] = filename
                info["cached_path"] = str(self.cache_dir / filename)
                files.append(info)
        return sorted(files, key=lambda x: x["timestamp"], reverse=True)
    
    def get_file(self, filename: str) -> Optional[str]:
        """Get full path to cached file"""
        cached_path = self.cache_dir / filename
        if cached_path.exists():
            return str(cached_path)
        return None
    
    def cleanup_old(self, days: int = 7):
        """Remove files older than specified days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        removed = []
        
        for filename, info in list(self.metadata["files"].items()):
            cached_path = self.cache_dir / filename
            if cached_path.exists() and cached_path.stat().st_mtime < cutoff:
                cached_path.unlink()
                removed.append(filename)
                del self.metadata["files"][filename]
        
        if removed:
            self._save_metadata()
        return removed
    
    def clear_category(self, category: str):
        """Clear all files in a specific category"""
        removed = []
        for filename, info in list(self.metadata["files"].items()):
            if info["category"] == category:
                cached_path = self.cache_dir / filename
                if cached_path.exists():
                    cached_path.unlink()
                removed.append(filename)
                del self.metadata["files"][filename]
        
        if removed:
            self._save_metadata()
        return removed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cache Manager")
    parser.add_argument("action", choices=["add", "list", "get", "cleanup", "clear"])
    parser.add_argument("--file", help="File path for add action")
    parser.add_argument("--category", default="general", help="Category for add/list actions")
    parser.add_argument("--filename", help="Filename for get action")
    parser.add_argument("--days", type=int, default=7, help="Days for cleanup")
    
    args = parser.parse_args()
    
    manager = CacheManager()
    
    if args.action == "add":
        if not args.file:
            parser.error("--file required for add action")
        result = manager.add_file(args.file, args.category)
        print(f"Cached file: {result}")
    
    elif args.action == "list":
        files = manager.list_files(args.category if args.category != "general" else None)
        for file_info in files:
            print(f"{file_info['filename']} ({file_info['category']}) - {file_info['size']} bytes")
    
    elif args.action == "get":
        if not args.filename:
            parser.error("--filename required for get action")
        path = manager.get_file(args.filename)
        print(path if path else "File not found")
    
    elif args.action == "cleanup":
        removed = manager.cleanup_old(args.days)
        print(f"Removed {len(removed)} old files")
    
    elif args.action == "clear":
        removed = manager.clear_category(args.category)
        print(f"Removed {len(removed)} files from category '{args.category}'")