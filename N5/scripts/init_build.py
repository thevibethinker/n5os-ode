#!/usr/bin/env python3
"""
init_build.py - Initialize a new build workspace with standardized templates.

Usage:
    python3 N5/scripts/init_build.py <slug> [--title "Build Title"]

Creates:
    N5/builds/<slug>/
    ├── PLAN.md        (from plan_template.md)
    ├── STATUS.md      (from status_template.md)
    └── .n5protected   (prevents accidental deletion)

The plan is FOR AI execution. Architect fills it out; Builder executes it.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
TEMPLATES_DIR = WORKSPACE / "N5" / "templates" / "build"


def validate_slug(slug: str) -> bool:
    """Validate slug: lowercase, hyphens, no spaces, no special chars."""
    pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def init_build(slug: str, title: str | None = None) -> Path:
    """
    Initialize a new build workspace.
    
    Args:
        slug: Build identifier (lowercase-hyphenated)
        title: Optional human-readable title
        
    Returns:
        Path to the created build directory
    """
    # Validate slug
    if not validate_slug(slug):
        print(f"❌ Invalid slug: '{slug}'")
        print("   Slug must be lowercase with hyphens (e.g., 'my-new-feature')")
        sys.exit(1)
    
    # Check if build already exists
    build_dir = BUILDS_DIR / slug
    if build_dir.exists():
        print(f"❌ Build already exists: {build_dir}")
        print("   Choose a different slug or remove existing build first.")
        sys.exit(1)
    
    # Create build directory
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Title defaults to slug titlecased
    if title is None:
        title = slug.replace("-", " ").title()
    
    # Read and populate plan template
    plan_template = TEMPLATES_DIR / "plan_template.md"
    if plan_template.exists():
        plan_content = plan_template.read_text()
        plan_content = plan_content.replace("{{DATE}}", today)
        plan_content = plan_content.replace("{{TITLE}}", title)
        plan_content = plan_content.replace("{{SLUG}}", slug)
    else:
        # Fallback minimal plan if template missing
        plan_content = f"""---
created: {today}
last_edited: {today}
version: 1.0
type: build_plan
status: draft
---

# Plan: {title}

**Objective:** [TO BE FILLED BY ARCHITECT]

---

## Open Questions

- [ ] [TO BE FILLED]

---

## Checklist

### Phase 1: [NAME]
- ☐ [TASK]

---

## Phase 1: [NAME]

### Affected Files
- [TO BE FILLED]

### Changes
[TO BE FILLED]

### Unit Tests
- [TO BE FILLED]
"""
    
    # Write plan
    plan_file = build_dir / "PLAN.md"
    plan_file.write_text(plan_content)
    
    # Read and populate status template
    status_template = TEMPLATES_DIR / "status_template.md"
    if status_template.exists():
        status_content = status_template.read_text()
        status_content = status_content.replace("{{DATE}}", today)
        status_content = status_content.replace("{{TITLE}}", title)
        status_content = status_content.replace("{{SLUG}}", slug)
    else:
        # Fallback minimal status if template missing
        status_content = f"""---
created: {today}
build_slug: {slug}
---

# Build Status: {title}

## Quick Status
- **Progress:** 0%
- **Current Phase:** Not started
- **Plan:** `N5/builds/{slug}/PLAN.md`
"""
    
    # Write status
    status_file = build_dir / "STATUS.md"
    status_file.write_text(status_content)
    
    # Create .n5protected marker
    protected_file = build_dir / ".n5protected"
    protected_file.write_text(f"Protected build workspace created {today}\n")
    
    return build_dir


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new build workspace with standardized templates.",
        epilog="Example: python3 N5/scripts/init_build.py my-feature --title 'My Feature Build'"
    )
    parser.add_argument(
        "slug",
        help="Build identifier (lowercase-hyphenated, e.g., 'my-new-feature')"
    )
    parser.add_argument(
        "--title", "-t",
        help="Human-readable build title (defaults to slug titlecased)"
    )
    
    args = parser.parse_args()
    
    build_dir = init_build(args.slug, args.title)
    
    print(f"✓ Build workspace created: {build_dir}")
    print(f"  ├── PLAN.md      (fill out with Architect)")
    print(f"  ├── STATUS.md    (track progress)")
    print(f"  └── .n5protected (deletion protection)")
    print()
    print(f"Next: Architect creates plan in `file 'N5/builds/{args.slug}/PLAN.md'`")


if __name__ == "__main__":
    main()

