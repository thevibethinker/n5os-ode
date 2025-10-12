#!/usr/bin/env python3
"""
Test script for lessons extraction system

This creates a mock lesson, saves it, and tests the review flow
"""

import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/home/workspace")
PENDING_DIR = WORKSPACE / "N5/lessons/pending"

def create_test_lesson():
    """Create a test lesson for this thread"""
    
    lesson = {
        "lesson_id": str(uuid.uuid4()),
        "thread_id": "con_JB5UD88QWtAkoaXF",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "design_pattern",
        "title": "Modularize monolithic documents for selective loading",
        "description": "Split large monolithic configuration/principle documents into focused modules that can be loaded selectively based on task needs, reducing token usage and improving context efficiency.",
        "context": "Architectural principles document was 400+ lines and loaded entirely every time, wasting tokens. Needed selective loading based on actual task requirements.",
        "outcome": "Split into 5 focused modules (core, safety, quality, design, operations). Can now load index + 1-2 modules instead of entire document. Reduced context by ~70% for typical operations.",
        "principle_refs": ["20", "8"],
        "tags": ["modular-design", "context-efficiency", "token-optimization", "selective-loading"],
        "status": "pending"
    }
    
    return lesson


def main():
    """Create test lesson"""
    
    # Ensure directory exists
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create test lesson
    lesson = create_test_lesson()
    
    # Save to pending
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_{lesson['thread_id']}_test.lessons.jsonl"
    filepath = PENDING_DIR / filename
    
    with open(filepath, 'w') as f:
        f.write(json.dumps(lesson) + '\n')
    
    print(f"✓ Created test lesson: {filepath}")
    print(f"\nLesson details:")
    print(f"  Title: {lesson['title']}")
    print(f"  Type: {lesson['type']}")
    print(f"  Principles: {lesson['principle_refs']}")
    print(f"\nTo review:")
    print(f"  python3 /home/workspace/N5/scripts/n5_lessons_review.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
