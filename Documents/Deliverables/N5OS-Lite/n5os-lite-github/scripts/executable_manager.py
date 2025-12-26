#!/usr/bin/env python3
"""
Executable Manager - Stub for N5OS Lite

This is a simplified stub to make n5_docgen.py functional.
For full functionality, implement database-backed executable tracking.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class Executable:
    """Represents an executable command/prompt"""
    name: str
    slug: str
    type: str
    description: str
    location: str
    tags: List[str] = None
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "slug": self.slug,
            "type": self.type,
            "description": self.description,
            "location": self.location,
            "tags": self.tags or []
        }


def list_executables(type_filter: Optional[str] = None) -> List[Executable]:
    """
    List available executables (prompts, scripts, etc.)
    
    This stub reads from Lists/ directory or returns empty list.
    """
    executables = []
    
    # Try to read from lists
    workspace = Path.home() / "workspace"
    lists_dir = workspace / "Lists"
    
    if not lists_dir.exists():
        lists_dir = workspace / ".n5os" / "lists"
    
    # Try to read tools list
    tools_file = lists_dir / "tools.jsonl" if lists_dir.exists() else None
    
    if tools_file and tools_file.exists():
        try:
            with open(tools_file) as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if not type_filter or item.get("type") == type_filter:
                            executables.append(Executable(
                                name=item.get("name", ""),
                                slug=item.get("slug", ""),
                                type=item.get("type", "unknown"),
                                description=item.get("description", ""),
                                location=item.get("location", ""),
                                tags=item.get("tags", [])
                            ))
        except Exception:
            pass
    
    return executables


def get_executable(slug: str) -> Optional[Executable]:
    """Get executable by slug"""
    all_execs = list_executables()
    for exe in all_execs:
        if exe.slug == slug:
            return exe
    return None


if __name__ == '__main__':
    # Simple test
    execs = list_executables()
    print(f"Found {len(execs)} executables")
    for exe in execs[:5]:
        print(f"  - {exe.name} ({exe.type})")
