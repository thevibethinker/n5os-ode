#!/usr/bin/env python3
"""
Quick validation sweep command

Usage:
    python3 sweep.py /path/to/project
    python3 sweep.py .  # validate current directory
"""

import sys
from pathlib import Path

# Import validation module
from validation import validate_project

def main():
    if len(sys.argv) < 2:
        print("Usage: sweep.py <project-directory>")
        return 1
    
    project_dir = Path(sys.argv[1]).resolve()
    
    if not project_dir.exists():
        print(f"Error: Directory not found: {project_dir}")
        return 1
    
    print(f"Sweeping {project_dir}...\n")
    
    result = validate_project(project_dir)
    
    if not result.has_errors:
        print("✓ Clean! No issues found.")
        return 0
    
    # Print detailed results
    print("=" * 60)
    print("VALIDATION ISSUES FOUND")
    print("=" * 60)
    
    if result.stubs:
        print(f"\n🔴 STUB IMPLEMENTATIONS ({len(result.stubs)}):")
        for file, func in result.stubs:
            print(f"   • {file} → {func}()")
    
    if result.broken_imports:
        print(f"\n🔴 BROKEN IMPORTS ({len(result.broken_imports)}):")
        for file, imp in result.broken_imports:
            print(f"   • {file} → {imp}")
    
    if result.placeholders:
        print(f"\n🟡 PLACEHOLDERS ({len(result.placeholders)}):")
        for file, line, text in result.placeholders[:10]:
            print(f"   • {file}:{line}")
            print(f"     {text[:80]}")
        if len(result.placeholders) > 10:
            print(f"   ... and {len(result.placeholders) - 10} more")
    
    if result.todos:
        print(f"\n🟡 TODO COMMENTS ({len(result.todos)}):")
        for file, line, text in result.todos[:10]:
            print(f"   • {file}:{line}")
            print(f"     {text[:80]}")
        if len(result.todos) > 10:
            print(f"   ... and {len(result.todos) - 10} more")
    
    if result.undefined_refs:
        print(f"\n🟠 UNDEFINED REFERENCES ({len(result.undefined_refs)}):")
        for file, ref in result.undefined_refs[:10]:
            print(f"   • {file} → {ref}")
        if len(result.undefined_refs) > 10:
            print(f"   ... and {len(result.undefined_refs) - 10} more")
    
    print("\n" + "=" * 60)
    print(f"Total issues: {len(result.stubs) + len(result.broken_imports) + len(result.placeholders) + len(result.todos) + len(result.undefined_refs)}")
    print("=" * 60)
    
    return 1 if (result.stubs or result.broken_imports) else 0


if __name__ == "__main__":
    sys.exit(main())
