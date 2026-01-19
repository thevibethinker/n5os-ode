#!/usr/bin/env python3
"""
Test Writer integration with voice lessons and primitives.

Part of Voice Optimization Loop (W3.2: Writer Integration).

Usage:
  python3 N5/scripts/test_writer_integration.py --content-type "cold_email"
  python3 N5/scripts/test_writer_integration.py --content-type "linkedin_post" --verbose

This script:
1. Retrieves voice lessons for the content type
2. Retrieves relevant primitives
3. Outputs combined context that Writer would use
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


def run_script(cmd: List[str]) -> Dict[str, Any]:
    """Run a script and return parsed JSON output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/home/workspace"
        )
        if result.returncode != 0:
            return {"error": result.stderr or "Script failed", "stdout": result.stdout}
        
        # Try to parse as JSON
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"text": result.stdout}
    except Exception as e:
        return {"error": str(e)}


def retrieve_lessons(content_type: str, include_global: bool = True) -> Dict[str, Any]:
    """Retrieve voice lessons for content type."""
    cmd = [
        "python3", "N5/scripts/retrieve_voice_lessons.py",
        "--content-type", content_type,
        "--format", "json"
    ]
    if include_global:
        cmd.append("--include-global")
    
    return run_script(cmd)


def retrieve_primitives(content_type: str, limit: int = 5) -> Dict[str, Any]:
    """Retrieve relevant primitives for content type."""
    cmd = [
        "python3", "N5/scripts/retrieve_primitives.py",
        "--domains", content_type,
        "--count", str(limit),
        "--json"
    ]
    
    result = run_script(cmd)
    
    # Fallback: try topic-based search
    if not result.get("primitives") and "error" not in result:
        cmd = [
            "python3", "N5/scripts/retrieve_primitives.py",
            "--topic", content_type,
            "--count", str(limit),
            "--json"
        ]
        result = run_script(cmd)
    
    return result


def format_writer_context(lessons: Dict, primitives: Dict, content_type: str) -> str:
    """Format combined context for Writer prompt injection."""
    lines = []
    
    lines.append("=" * 60)
    lines.append(f"VOICE CONTEXT FOR: {content_type}")
    lines.append("=" * 60)
    lines.append("")
    
    # Voice Lessons Section
    lines.append("## Voice Lessons (from V's past corrections)")
    lines.append("")
    
    lesson_list = lessons.get("lessons", [])
    global_list = lessons.get("global_lessons", [])
    
    if lesson_list:
        for i, lesson in enumerate(lesson_list, 1):
            lines.append(f"### {i}. {lesson.get('lesson', 'Unknown')}")
            if lesson.get("anti_pattern"):
                lines.append(f"   ❌ AVOID: {lesson['anti_pattern']}")
            if lesson.get("positive_pattern"):
                lines.append(f"   ✓ PREFER: {lesson['positive_pattern']}")
            lines.append("")
    else:
        lines.append("*No specific lessons for this content type yet.*")
        lines.append("")
    
    if global_list:
        lines.append("### Global Patterns (apply to all content)")
        for lesson in global_list:
            lines.append(f"- {lesson.get('lesson', 'Unknown')}")
            if lesson.get("anti_pattern"):
                lines.append(f"  ❌ {lesson['anti_pattern']}")
            if lesson.get("positive_pattern"):
                lines.append(f"  ✓ {lesson['positive_pattern']}")
        lines.append("")
    
    # Voice Primitives Section
    lines.append("## Voice Primitives (distinctive phrases to consider)")
    lines.append("")
    
    prim_list = primitives.get("primitives", [])
    if prim_list:
        for p in prim_list:
            text = p.get("exact_text", p.get("text", "?"))
            ptype = p.get("primitive_type", p.get("type", "?"))
            lines.append(f"- \"{text}\" ({ptype})")
        lines.append("")
    else:
        lines.append("*No primitives matched for this content type.*")
        lines.append("")
    
    # Application Instructions
    lines.append("## How to Apply")
    lines.append("")
    lines.append("1. **Avoid anti-patterns** - These are things V has corrected before")
    lines.append("2. **Use preferred patterns** - These reflect V's actual writing style")
    lines.append("3. **Consider primitives** - Use naturally where they fit (don't force)")
    lines.append("4. **When in doubt** - Direct > Hedging, Specific > Vague")
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Test Writer integration with voice context"
    )
    parser.add_argument(
        "--content-type", "-t",
        required=True,
        help="Content type to test (e.g., cold_email, linkedin_post)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show raw API responses"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted context"
    )
    parser.add_argument(
        "--primitives-limit",
        type=int,
        default=5,
        help="Max primitives to retrieve (default: 5)"
    )
    
    args = parser.parse_args()
    
    print(f"Testing Writer integration for: {args.content_type}\n")
    
    # Retrieve lessons
    print("Retrieving voice lessons...")
    lessons = retrieve_lessons(args.content_type)
    if args.verbose:
        print(f"Lessons response: {json.dumps(lessons, indent=2)}\n")
    
    # Retrieve primitives
    print("Retrieving primitives...")
    primitives = retrieve_primitives(args.content_type, args.primitives_limit)
    if args.verbose:
        print(f"Primitives response: {json.dumps(primitives, indent=2)}\n")
    
    # Check for errors
    if lessons.get("error"):
        print(f"⚠️  Lessons retrieval error: {lessons['error']}")
    if primitives.get("error"):
        print(f"⚠️  Primitives retrieval error: {primitives['error']}")
    
    print("\n" + "-" * 60 + "\n")
    
    # Output
    if args.json:
        combined = {
            "content_type": args.content_type,
            "lessons": lessons,
            "primitives": primitives
        }
        print(json.dumps(combined, indent=2))
    else:
        context = format_writer_context(lessons, primitives, args.content_type)
        print(context)
    
    # Summary
    lesson_count = len(lessons.get("lessons", [])) + len(lessons.get("global_lessons", []))
    prim_count = len(primitives.get("primitives", []))
    
    print("\n" + "-" * 60)
    print(f"Summary: {lesson_count} lessons, {prim_count} primitives retrieved")
    
    if lesson_count == 0 and prim_count == 0:
        print("ℹ️  No voice context found. Writer will use general voice guidance.")
    elif lesson_count == 0:
        print("ℹ️  No lessons found. As V makes corrections, they'll accumulate here.")


if __name__ == "__main__":
    main()
