#!/usr/bin/env python3
"""
Capability Graduation System v1.0

Graduates completed builds into the capability registry and semantic memory.
Called during Tier 3 conversation close when a build is detected.

Workflow:
1. Detect completed build in conversation
2. Generate capability doc (LLM prompt injection point)
3. Write to N5/capabilities/<category>/
4. Register in semantic memory (brain.db)
5. Update capabilities index

Usage:
    # Check if build qualifies for graduation
    python3 capability_graduation.py check --build-slug <slug>
    
    # Graduate a build (generates scaffold for LLM to complete)
    python3 capability_graduation.py graduate --build-slug <slug> --convo-id <id>
    
    # Add to semantic memory after doc is written
    python3 capability_graduation.py embed --capability-path <path>

Cost: ~$0.02 for embedding | Time: <30s
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
LOG = logging.getLogger("capability_graduation")

WORKSPACE = Path("/home/workspace")
N5_ROOT = WORKSPACE / "N5"
BUILDS_DIR = N5_ROOT / "builds"
CAPABILITIES_DIR = N5_ROOT / "capabilities"
CAPABILITIES_INDEX = CAPABILITIES_DIR / "index.md"

# Categories for capability docs
CAPABILITY_CATEGORIES = {
    "internal": "Internal N5 systems and infrastructure",
    "integration": "External service integrations", 
    "workflow": "Automated workflows and pipelines",
    "prompt": "Prompt-based capabilities",
    "site": "Web applications and services",
}

# Build types that should NOT graduate (one-offs, meeting-specific, etc.)
EXCLUDE_PATTERNS = [
    r"^mg\d+-",           # Meeting-generated one-offs (mg2-*, etc.)
    r"^con_",             # Orphaned conversation builds
    r"-meeting-",         # Meeting-specific builds
    r"-davit-",           # Person-specific meeting builds
    r"-careerspan-\d{4}", # Dated Careerspan runs
]


def should_exclude(build_slug: str) -> bool:
    """Check if build should be excluded from graduation."""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, build_slug, re.IGNORECASE):
            return True
    return False


def get_build_status(build_slug: str) -> Dict:
    """Read build STATUS.md and extract completion info."""
    build_dir = BUILDS_DIR / build_slug
    status_file = build_dir / "STATUS.md"
    plan_file = build_dir / "PLAN.md"
    
    result = {
        "exists": build_dir.exists(),
        "has_status": status_file.exists(),
        "has_plan": plan_file.exists(),
        "is_complete": False,
        "progress_pct": 0,
        "slug": build_slug,
        "status_content": "",
        "plan_content": "",
    }
    
    if not build_dir.exists():
        return result
    
    if status_file.exists():
        content = status_file.read_text()
        result["status_content"] = content
        
        # Check for completion markers
        if any(marker in content.upper() for marker in ["100%", "COMPLETE", "✅ COMPLETE"]):
            result["is_complete"] = True
        
        # Extract progress percentage
        pct_match = re.search(r"(\d+)%", content)
        if pct_match:
            result["progress_pct"] = int(pct_match.group(1))
    
    if plan_file.exists():
        result["plan_content"] = plan_file.read_text()
    
    return result


def check_existing_capability(build_slug: str) -> Optional[Path]:
    """Check if capability doc already exists for this build."""
    # Normalize slug for matching
    normalized = build_slug.lower().replace("-", "").replace("_", "")
    
    for category_dir in CAPABILITIES_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        for cap_file in category_dir.glob("*.md"):
            cap_normalized = cap_file.stem.lower().replace("-", "").replace("_", "")
            if normalized in cap_normalized or cap_normalized in normalized:
                return cap_file
    
    return None


def infer_category(build_slug: str, plan_content: str) -> str:
    """Infer capability category from build slug and plan content."""
    slug_lower = build_slug.lower()
    content_lower = plan_content.lower()
    
    # Integration indicators
    if any(term in slug_lower for term in ["integration", "api", "sync"]):
        return "integration"
    if any(term in content_lower for term in ["api key", "external service", "third-party"]):
        return "integration"
    
    # Site/app indicators
    if any(term in slug_lower for term in ["site", "app", "dashboard", "ui"]):
        return "site"
    
    # Workflow indicators
    if any(term in slug_lower for term in ["pipeline", "workflow", "auto", "agent"]):
        return "workflow"
    
    # Prompt indicators
    if any(term in slug_lower for term in ["prompt", "copilot"]):
        return "prompt"
    
    # Default to internal
    return "internal"


def generate_capability_scaffold(build_status: Dict, category: str, convo_id: str) -> str:
    """Generate capability doc scaffold for LLM to complete."""
    slug = build_status["slug"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Extract key info from plan/status for context
    plan_excerpt = build_status.get("plan_content", "")[:2000]
    status_excerpt = build_status.get("status_content", "")[:1000]
    
    scaffold = f"""---
created: {today}
last_edited: {today}
version: 1.0
provenance: {convo_id}
---

# {slug.replace("-", " ").title()}

```yaml
# Zone 2: Capability metadata (machine-readable)
capability_id: {slug}
name: {slug.replace("-", " ").title()}
category: {category}
status: active
confidence: high
last_verified: '{today}'
tags: []
owner: V
purpose: |
  [LLM: Write 1-2 sentence purpose based on PLAN.md]
components:
  # [LLM: List key files from the build]
  - N5/builds/{slug}/PLAN.md
operational_behavior: |
  [LLM: Describe how this capability operates]
interfaces:
  # [LLM: List entry points - prompts, scripts, commands]
  - TBD
quality_metrics: |
  [LLM: Define success criteria]
```

## What This Does

[LLM: Write 2-5 sentences describing what this capability does and why it exists. 
Reference the PLAN.md content below for context.]

## How to Use It

[LLM: Describe how to trigger/use this capability. Include:
- Prompts (if applicable)
- Commands (if applicable)  
- UI entry points (if applicable)]

## Associated Files & Assets

[LLM: List key implementation files using `file '...'` syntax]

## Workflow

[LLM: Describe the execution flow. Include mermaid diagram if helpful.]

```mermaid
flowchart TD
  A[Trigger] --> B[Step 1]
  B --> C[Step 2]
  C --> D[Outputs]
```

## Notes / Gotchas

[LLM: Document edge cases, preconditions, safety considerations]

---

## Build Context (for LLM reference - remove after completion)

### PLAN.md Excerpt
```
{plan_excerpt}
```

### STATUS.md Excerpt  
```
{status_excerpt}
```
"""
    return scaffold


def write_capability_scaffold(build_slug: str, category: str, scaffold: str) -> Path:
    """Write capability scaffold to appropriate location."""
    category_dir = CAPABILITIES_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    
    cap_file = category_dir / f"{build_slug}.md"
    cap_file.write_text(scaffold)
    
    LOG.info(f"Wrote capability scaffold to {cap_file}")
    return cap_file


def embed_capability(capability_path: Path) -> bool:
    """Add capability doc to semantic memory."""
    try:
        sys.path.insert(0, str(WORKSPACE))
        from N5.cognition.n5_memory_client import N5MemoryClient
        import hashlib
        
        client = N5MemoryClient()
        content = capability_path.read_text()
        
        # Calculate file hash for dedup
        file_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Store resource (file-level record)
        resource_id = client.store_resource(
            path=str(capability_path),
            file_hash=file_hash,
            content_date=datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        
        # Add content as a block for embedding
        client.add_block(
            resource_id=resource_id,
            content=content,
            block_type="capability_doc"
        )
        
        LOG.info(f"Embedded capability in semantic memory: {capability_path} (resource_id={resource_id})")
        return True
        
    except Exception as e:
        LOG.error(f"Failed to embed capability: {e}")
        return False


def update_capabilities_index(capability_path: Path, category: str) -> bool:
    """Update the capabilities index.md with new entry."""
    try:
        if not CAPABILITIES_INDEX.exists():
            LOG.warning(f"Capabilities index not found at {CAPABILITIES_INDEX}")
            return False
        
        content = CAPABILITIES_INDEX.read_text()
        slug = capability_path.stem
        rel_path = capability_path.relative_to(CAPABILITIES_DIR)
        
        # Check if already indexed
        if slug in content:
            LOG.info(f"Capability {slug} already in index")
            return True
        
        # Find the right section and add entry
        # This is a simple append - could be smarter about section placement
        new_entry = f"\n- `{category}/{slug}` - [See doc]({rel_path})\n"
        
        # Append to end (LLM can reorganize later)
        with open(CAPABILITIES_INDEX, "a") as f:
            f.write(new_entry)
        
        LOG.info(f"Added {slug} to capabilities index")
        return True
        
    except Exception as e:
        LOG.error(f"Failed to update index: {e}")
        return False


def check_graduation_eligibility(build_slug: str) -> Dict:
    """Check if a build is eligible for graduation."""
    result = {
        "eligible": False,
        "reason": "",
        "build_status": None,
        "existing_capability": None,
        "suggested_category": None,
    }
    
    # Check exclusion
    if should_exclude(build_slug):
        result["reason"] = f"Build matches exclusion pattern (one-off/meeting-specific)"
        return result
    
    # Get build status
    status = get_build_status(build_slug)
    result["build_status"] = status
    
    if not status["exists"]:
        result["reason"] = f"Build directory does not exist"
        return result
    
    if not status["is_complete"]:
        result["reason"] = f"Build not complete (progress: {status['progress_pct']}%)"
        return result
    
    # Check for existing capability
    existing = check_existing_capability(build_slug)
    if existing:
        result["existing_capability"] = str(existing)
        result["reason"] = f"Capability doc already exists at {existing}"
        return result
    
    # All checks passed
    result["eligible"] = True
    result["reason"] = "Build is complete and no existing capability doc found"
    result["suggested_category"] = infer_category(build_slug, status.get("plan_content", ""))
    
    return result


def mark_build_graduated(build_slug: str, capability_path: Path) -> bool:
    """Mark build as graduated by updating STATUS.md."""
    try:
        status_file = BUILDS_DIR / build_slug / "STATUS.md"
        if not status_file.exists():
            return False
        
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        graduation_note = f"""

---

## Graduation Status

| Field | Value |
|-------|-------|
| **Graduated** | ✅ Yes |
| **Graduation Date** | {today} |
| **Capability Doc** | `{capability_path.relative_to(WORKSPACE)}` |

This build has been graduated to the capability registry. The capability doc is now the source of truth for "what this does."
"""
        
        with open(status_file, "a") as f:
            f.write(graduation_note)
        
        LOG.info(f"Marked {build_slug} as graduated in STATUS.md")
        return True
        
    except Exception as e:
        LOG.error(f"Failed to mark build as graduated: {e}")
        return False


def graduate_build(build_slug: str, convo_id: str, category: Optional[str] = None) -> Dict:
    """Graduate a build to the capability registry."""
    result = {
        "success": False,
        "capability_path": None,
        "embedded": False,
        "indexed": False,
        "message": "",
    }
    
    # Check eligibility first
    eligibility = check_graduation_eligibility(build_slug)
    if not eligibility["eligible"]:
        result["message"] = eligibility["reason"]
        return result
    
    # Use provided category or inferred one
    final_category = category or eligibility["suggested_category"]
    
    # Generate scaffold
    scaffold = generate_capability_scaffold(
        eligibility["build_status"],
        final_category,
        convo_id
    )
    
    # Write scaffold
    cap_path = write_capability_scaffold(build_slug, final_category, scaffold)
    result["capability_path"] = str(cap_path)
    
    # Mark build as graduated
    mark_build_graduated(build_slug, cap_path)
    
    result["success"] = True
    result["message"] = f"Generated capability scaffold at {cap_path}. LLM should complete the [LLM: ...] sections."
    
    return result


def extract_base_capability(build_slug: str) -> Tuple[str, Optional[str]]:
    """Extract base capability name and version from build slug.
    
    Returns (base_name, version) where version may be None.
    Examples:
        'wheres-v-revamp-v2' -> ('wheres-v-revamp', 'v2')
        'thought-provoker-v2' -> ('thought-provoker', 'v2')
        'content-library-v4' -> ('content-library', 'v4')
        'nyne-integration' -> ('nyne-integration', None)
    """
    # Match version suffix patterns
    version_match = re.search(r'[-_](v\d+(?:\.\d+)?)$', build_slug, re.IGNORECASE)
    if version_match:
        version = version_match.group(1)
        base = build_slug[:version_match.start()]
        return (base, version)
    
    return (build_slug, None)


def group_related_builds() -> Dict[str, List[Dict]]:
    """Group builds by base capability name, sorted by version/date.
    
    Returns dict mapping base_capability -> list of build info dicts, 
    sorted newest first.
    """
    groups: Dict[str, List[Dict]] = {}
    
    for build_dir in BUILDS_DIR.iterdir():
        if not build_dir.is_dir():
            continue
        
        slug = build_dir.name
        if should_exclude(slug):
            continue
            
        base, version = extract_base_capability(slug)
        status = get_build_status(slug)
        
        # Get modification time for sorting
        status_file = build_dir / "STATUS.md"
        mtime = status_file.stat().st_mtime if status_file.exists() else 0
        
        build_info = {
            "slug": slug,
            "base": base,
            "version": version,
            "mtime": mtime,
            "is_complete": status["is_complete"],
            "progress_pct": status["progress_pct"],
        }
        
        if base not in groups:
            groups[base] = []
        groups[base].append(build_info)
    
    # Sort each group: complete builds first, then by version/mtime
    for base in groups:
        groups[base].sort(key=lambda x: (
            not x["is_complete"],  # Complete first
            -_version_sort_key(x["version"]),  # Higher version first
            -x["mtime"],  # Newer first
        ))
    
    return groups


def _version_sort_key(version: Optional[str]) -> int:
    """Convert version string to sortable int. None -> 0, 'v2' -> 2, etc."""
    if not version:
        return 0
    match = re.search(r'(\d+)', version)
    return int(match.group(1)) if match else 0


def get_latest_for_capability(base_capability: str) -> Optional[Dict]:
    """Get the latest complete build for a base capability."""
    groups = group_related_builds()
    if base_capability not in groups:
        return None
    
    builds = groups[base_capability]
    # Return first complete build (already sorted)
    for build in builds:
        if build["is_complete"]:
            return build
    
    return None


def main():
    parser = argparse.ArgumentParser(description="Capability Graduation System")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check if build qualifies for graduation")
    check_parser.add_argument("--build-slug", required=True, help="Build slug to check")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Graduate command
    grad_parser = subparsers.add_parser("graduate", help="Graduate a build to capability registry")
    grad_parser.add_argument("--build-slug", required=True, help="Build slug to graduate")
    grad_parser.add_argument("--convo-id", required=True, help="Conversation ID for provenance")
    grad_parser.add_argument("--category", choices=list(CAPABILITY_CATEGORIES.keys()), help="Override category")
    grad_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Embed capability in semantic memory")
    embed_parser.add_argument("--capability-path", required=True, help="Path to capability doc")
    embed_parser.add_argument("--update-index", action="store_true", help="Also update capabilities index")
    
    # List eligible command
    list_parser = subparsers.add_parser("list-eligible", help="List all builds eligible for graduation")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # List grouped command (for backfill planning)
    grouped_parser = subparsers.add_parser("list-grouped", help="List builds grouped by capability (for backfill)")
    grouped_parser.add_argument("--json", action="store_true", help="Output as JSON")
    grouped_parser.add_argument("--eligible-only", action="store_true", help="Only show groups with eligible builds")
    
    args = parser.parse_args()
    
    if args.command == "check":
        result = check_graduation_eligibility(args.build_slug)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Build: {args.build_slug}")
            print(f"Eligible: {result['eligible']}")
            print(f"Reason: {result['reason']}")
            if result.get("suggested_category"):
                print(f"Suggested Category: {result['suggested_category']}")
    
    elif args.command == "graduate":
        result = graduate_build(args.build_slug, args.convo_id, args.category)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            if result.get("capability_path"):
                print(f"Capability Path: {result['capability_path']}")
    
    elif args.command == "embed":
        cap_path = Path(args.capability_path)
        if not cap_path.exists():
            print(f"Error: Capability file not found: {cap_path}")
            sys.exit(1)
        
        success = embed_capability(cap_path)
        if args.update_index:
            # Infer category from path
            category = cap_path.parent.name
            update_capabilities_index(cap_path, category)
        
        print(f"Embedded: {success}")
    
    elif args.command == "list-eligible":
        eligible = []
        for build_dir in BUILDS_DIR.iterdir():
            if not build_dir.is_dir():
                continue
            result = check_graduation_eligibility(build_dir.name)
            if result["eligible"]:
                eligible.append({
                    "slug": build_dir.name,
                    "category": result["suggested_category"],
                })
        
        if args.json:
            print(json.dumps(eligible, indent=2))
        else:
            print(f"Found {len(eligible)} eligible builds:\n")
            for item in eligible:
                print(f"  - {item['slug']} ({item['category']})")
    
    elif args.command == "list-grouped":
        groups = group_related_builds()
        
        output = []
        for base, builds in sorted(groups.items()):
            # Check if any build in group is eligible
            has_eligible = any(
                check_graduation_eligibility(b["slug"])["eligible"] 
                for b in builds
            )
            
            if args.eligible_only and not has_eligible:
                continue
            
            # Find the latest complete version
            latest = next((b for b in builds if b["is_complete"]), None)
            
            group_info = {
                "capability": base,
                "builds": [b["slug"] for b in builds],
                "latest_complete": latest["slug"] if latest else None,
                "has_eligible": has_eligible,
            }
            output.append(group_info)
        
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print(f"Found {len(output)} capability groups:\n")
            for g in output:
                status = "✓" if g["has_eligible"] else "○"
                latest = g["latest_complete"] or "(none complete)"
                print(f"  {status} {g['capability']}")
                print(f"      Latest: {latest}")
                if len(g["builds"]) > 1:
                    print(f"      All builds: {', '.join(g['builds'])}")
                print()


if __name__ == "__main__":
    main()




