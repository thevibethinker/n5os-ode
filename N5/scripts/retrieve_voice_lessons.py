#!/usr/bin/env python3
"""
Retrieve voice lessons from semantic memory for content generation.

Part of Voice Optimization Loop (W3.2: Writer Integration).

Usage:
  python3 N5/scripts/retrieve_voice_lessons.py --content-type "cold_email" [--include-global] [--limit 10] [--format text|json]
  python3 N5/scripts/retrieve_voice_lessons.py --list-types

Process:
1. Query semantic memory for type = "voice_preference"
2. Filter by content_type tag (exact match)
3. If --include-global, also include lessons tagged "global"
4. Sort by relevance/recency (prefer recent learnings)
5. Return top N lessons
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

sys.path.insert(0, '/home/workspace')
from N5.cognition.n5_memory_client import N5MemoryClient


def parse_lesson_content(content: str) -> Dict[str, str]:
    """Parse structured lesson content into components."""
    result = {
        "lesson": "",
        "anti_pattern": "",
        "positive_pattern": "",
        "content_type": ""
    }
    
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        
        # Parse: "Voice preference (content_type): lesson text"
        pref_match = re.match(r'^Voice preference \(([^)]+)\):\s*(.+)$', line)
        if pref_match:
            result["content_type"] = pref_match.group(1)
            result["lesson"] = pref_match.group(2)
            continue
        
        # Parse: "Avoid: pattern"
        avoid_match = re.match(r'^Avoid:\s*(.+)$', line)
        if avoid_match:
            result["anti_pattern"] = avoid_match.group(1)
            continue
        
        # Parse: "Prefer: pattern"
        prefer_match = re.match(r'^Prefer:\s*(.+)$', line)
        if prefer_match:
            result["positive_pattern"] = prefer_match.group(1)
            continue
    
    return result


def retrieve_lessons(
    content_type: str,
    include_global: bool = False,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Retrieve voice lessons for a specific content type.
    
    Args:
        content_type: The content type to filter by (e.g., "cold_email")
        include_global: If True, also include global lessons
        limit: Maximum number of lessons to return
        
    Returns:
        Dict with lessons and global_lessons arrays
    """
    client = N5MemoryClient()
    
    # Search for voice preferences using block_type filter
    # We search broadly and filter by content in post-processing
    results = client.search(
        query=f"voice preference {content_type}",
        limit=limit * 3,  # Get extra for filtering
        metadata_filters={
            "block_type": "voice_preference"
        },
        use_hybrid=True
    )
    
    lessons = []
    global_lessons = []
    seen_hashes = set()
    
    for r in results:
        content = r.get("content", "")
        parsed = parse_lesson_content(content)
        
        # Dedup by content hash
        content_hash = hash(content)
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)
        
        # Extract lesson metadata
        lesson_data = {
            "id": r.get("block_id", ""),
            "lesson": parsed["lesson"],
            "anti_pattern": parsed["anti_pattern"],
            "positive_pattern": parsed["positive_pattern"],
            "content_type": parsed["content_type"],
            "learned_at": r.get("content_date", ""),
            "similarity": r.get("similarity", 0.0),
            "path": r.get("path", "")
        }
        
        # Determine if this is a global lesson
        path = r.get("path", "").lower()
        is_global = "global" in path or parsed["content_type"] == "global"
        
        # Filter by content type
        if parsed["content_type"] == content_type:
            lessons.append(lesson_data)
        elif is_global and include_global:
            global_lessons.append(lesson_data)
    
    # Sort by learned_at (most recent first), then by similarity
    lessons.sort(key=lambda x: (x.get("learned_at", ""), x.get("similarity", 0)), reverse=True)
    global_lessons.sort(key=lambda x: (x.get("learned_at", ""), x.get("similarity", 0)), reverse=True)
    
    return {
        "content_type": content_type,
        "lessons": lessons[:limit],
        "global_lessons": global_lessons[:limit] if include_global else []
    }


def retrieve_lessons_fallback(
    content_type: str,
    include_global: bool = False,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Fallback retrieval that reads from voice-lessons.md file.
    
    Used when semantic memory doesn't have lessons yet.
    """
    lessons_file = Path("/home/workspace/N5/prefs/communication/voice-lessons.md")
    
    if not lessons_file.exists():
        return {
            "content_type": content_type,
            "lessons": [],
            "global_lessons": []
        }
    
    content = lessons_file.read_text()
    lessons = []
    global_lessons = []
    
    # Parse markdown sections
    current_type = None
    current_lesson = {}
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Section header: ### Cold Email
        type_match = re.match(r'^###\s+(.+)$', line)
        if type_match:
            current_type = type_match.group(1).lower().replace(' ', '_')
            continue
        
        # Lesson header: #### Lesson: Lead with Action
        lesson_match = re.match(r'^####\s+Lesson:\s*(.+)$', line)
        if lesson_match:
            if current_lesson:
                # Save previous lesson
                target = lessons if current_lesson.get("content_type") == content_type else global_lessons
                if current_lesson.get("content_type") == content_type or (include_global and current_lesson.get("content_type") == "global"):
                    target.append(current_lesson)
            
            current_lesson = {
                "id": f"lesson_{len(lessons) + len(global_lessons)}",
                "lesson": lesson_match.group(1),
                "content_type": current_type,
                "anti_pattern": "",
                "positive_pattern": "",
                "learned_at": ""
            }
            continue
        
        # Learned date
        learned_match = re.match(r'^\*\*Learned:\*\*\s*(\d{4}-\d{2}-\d{2})', line)
        if learned_match and current_lesson:
            current_lesson["learned_at"] = learned_match.group(1)
            continue
        
        # Avoid pattern
        avoid_match = re.match(r'^\*\*Avoid:\*\*\s*(.+)$', line)
        if avoid_match and current_lesson:
            current_lesson["anti_pattern"] = avoid_match.group(1)
            continue
        
        # Prefer pattern
        prefer_match = re.match(r'^\*\*Prefer:\*\*\s*(.+)$', line)
        if prefer_match and current_lesson:
            current_lesson["positive_pattern"] = prefer_match.group(1)
            continue
    
    # Don't forget last lesson
    if current_lesson:
        target = lessons if current_lesson.get("content_type") == content_type else global_lessons
        if current_lesson.get("content_type") == content_type or (include_global and current_lesson.get("content_type") == "global"):
            target.append(current_lesson)
    
    return {
        "content_type": content_type,
        "lessons": lessons[:limit],
        "global_lessons": global_lessons[:limit] if include_global else []
    }


def format_text_output(data: Dict[str, Any]) -> str:
    """Format lessons as human-readable text."""
    lines = []
    
    total = len(data["lessons"]) + len(data.get("global_lessons", []))
    lines.append(f"=== Voice Preferences for {data['content_type']} ({total} lessons) ===\n")
    
    if not data["lessons"] and not data.get("global_lessons"):
        lines.append("No lessons found for this content type.")
        lines.append("Proceed with general voice guidance.\n")
        return "\n".join(lines)
    
    # Content-type specific lessons
    for i, lesson in enumerate(data["lessons"], 1):
        lines.append(f"{i}. {lesson['lesson']}")
        if lesson.get("anti_pattern"):
            lines.append(f"   Avoid: {lesson['anti_pattern']}")
        if lesson.get("positive_pattern"):
            lines.append(f"   Prefer: {lesson['positive_pattern']}")
        if lesson.get("learned_at"):
            lines.append(f"   (learned: {lesson['learned_at']})")
        lines.append("")
    
    # Global lessons
    if data.get("global_lessons"):
        lines.append("--- Global Lessons ---\n")
        for i, lesson in enumerate(data["global_lessons"], 1):
            lines.append(f"G{i}. {lesson['lesson']}")
            if lesson.get("anti_pattern"):
                lines.append(f"    Avoid: {lesson['anti_pattern']}")
            if lesson.get("positive_pattern"):
                lines.append(f"    Prefer: {lesson['positive_pattern']}")
            if lesson.get("learned_at"):
                lines.append(f"    (learned: {lesson['learned_at']})")
            lines.append("")
    
    return "\n".join(lines)


def list_content_types() -> List[str]:
    """List all content types that have lessons."""
    # Check semantic memory
    client = N5MemoryClient()
    
    # Search broadly for voice preferences
    results = client.search(
        query="voice preference",
        limit=100,
        metadata_filters={
            "block_type": "voice_preference"
        }
    )
    
    types = set()
    for r in results:
        content = r.get("content", "")
        parsed = parse_lesson_content(content)
        if parsed["content_type"]:
            types.add(parsed["content_type"])
    
    # Also check voice-lessons.md fallback
    lessons_file = Path("/home/workspace/N5/prefs/communication/voice-lessons.md")
    if lessons_file.exists():
        content = lessons_file.read_text()
        for match in re.finditer(r'^###\s+(.+)$', content, re.MULTILINE):
            types.add(match.group(1).lower().replace(' ', '_'))
    
    return sorted(types)


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve voice lessons for content generation"
    )
    parser.add_argument(
        "--content-type", "-t",
        help="Content type to filter by (e.g., cold_email, linkedin_post)"
    )
    parser.add_argument(
        "--include-global", "-g",
        action="store_true",
        help="Include global lessons that apply to all content types"
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=10,
        help="Maximum number of lessons to return (default: 10)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List all content types that have lessons"
    )
    parser.add_argument(
        "--fallback-only",
        action="store_true",
        help="Only use voice-lessons.md fallback, skip semantic memory"
    )
    
    args = parser.parse_args()
    
    if args.list_types:
        types = list_content_types()
        if types:
            print("Content types with lessons:")
            for t in types:
                print(f"  - {t}")
        else:
            print("No content types found yet.")
        return
    
    if not args.content_type:
        parser.error("--content-type is required (or use --list-types)")
    
    # Try semantic memory first, fall back to file
    if args.fallback_only:
        data = retrieve_lessons_fallback(
            args.content_type,
            args.include_global,
            args.limit
        )
    else:
        data = retrieve_lessons(
            args.content_type,
            args.include_global,
            args.limit
        )
        
        # If no results from semantic memory, try fallback
        if not data["lessons"] and not data.get("global_lessons"):
            data = retrieve_lessons_fallback(
                args.content_type,
                args.include_global,
                args.limit
            )
    
    # Output
    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(format_text_output(data))


if __name__ == "__main__":
    main()
