#!/usr/bin/env python3
"""
Knowledge System V4 - Knowledge Integrator
Writes approved intelligence to Knowledge/ files.

Input: Knowledge/intelligence/extracts/{file}.yaml
Output: Writes to Knowledge/{target_file}
"""

import argparse
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

WORKSPACE = Path("/home/workspace")
PATHS_YAML = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"


def _load_pk_roots() -> dict:
    """Load Personal/Knowledge roots from knowledge_paths.yaml."""
    data = yaml.safe_load(PATHS_YAML.read_text()) or {}
    pk = data.get("personal_knowledge", {})

    pk_root = WORKSPACE / pk.get("root", "Personal/Knowledge")
    intelligence_root = WORKSPACE / pk.get("intelligence", str(pk_root / "Intelligence"))
    content_root = WORKSPACE / pk.get("content_library", str(pk_root / "ContentLibrary")) / "content"

    mi_cfg = pk.get("market_intelligence", {})
    market_root = WORKSPACE / mi_cfg.get(
        "root",
        str(intelligence_root / "World" / "Market"),
    )

    return {
        "pk_root": pk_root,
        "intelligence_root": intelligence_root,
        "content_root": content_root,
        "market_root": market_root,
    }


def resolve_target_path_from_legacy(target: str) -> Path:
    """Map legacy Knowledge/* targets into Personal/Knowledge buckets.

    Heuristics (minimal but directionally correct):
    - Targets mentioning "market_intelligence" or under intelligence/World/Market → market intelligence root.
    - Everything else defaults to Intelligence root, unless clearly a content bucket
      (external_research/hypotheses/semi_stable/evolving) in which case it goes to ContentLibrary/content.
    """
    if not target:
        raise ValueError("Empty knowledge_routing.target")

    roots = _load_pk_roots()
    norm = target.lstrip("/")

    # Explicit market intelligence cases
    if norm.startswith("market_intelligence/"):
        suffix = norm.split("market_intelligence/", 1)[1]
        return roots["market_root"] / suffix

    if norm.startswith("intelligence/World/Market/"):
        suffix = norm.split("intelligence/World/Market/", 1)[1]
        return roots["market_root"] / suffix

    # Simple content buckets based on legacy folder names
    top = norm.split("/", 1)[0]
    content_buckets = {"external_research", "hypotheses", "semi_stable", "evolving"}
    if top in content_buckets:
        return roots["content_root"] / norm

    # Default: treat as intelligence
    return roots["intelligence_root"] / norm


def load_extraction(yaml_file: Path) -> dict:
    """Load extraction YAML."""
    with yaml_file.open() as f:
        return yaml.safe_load(f)


def check_protection(target_path: Path) -> bool:
    """
    Check if target path is protected using n5_protect.py.
    
    Returns True if safe to write, False if protected.
    """
    if not N5_PROTECT_SCRIPT.exists():
        logging.warning("n5_protect.py not found, skipping protection check")
        return True
    
    try:
        result = subprocess.run(
            [sys.executable, str(N5_PROTECT_SCRIPT), "check", str(target_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        
        # If check command exits 0, path is NOT protected (safe)
        # If check command exits 1, path IS protected (unsafe)
        return result.returncode == 0
        
    except Exception as e:
        logging.warning(f"Protection check failed: {e}, proceeding cautiously")
        return True


def format_content(extraction: dict) -> str:
    """
    Format extraction content for human readability in Knowledge/ file.
    """
    content = extraction.get("content", {})
    entity = extraction.get("entity", {})
    metadata = extraction.get("metadata", {})
    tags = extraction.get("tags", {})
    
    entity_name = entity.get("name", "Unknown")
    captured_at = extraction.get("captured_at", "")
    
    # Try to format date nicely
    try:
        dt = datetime.fromisoformat(captured_at)
        date_str = dt.strftime("%Y-%m-%d")
    except:
        date_str = captured_at
    
    lines = []
    lines.append(f"### {entity_name}")
    if date_str:
        lines.append(f"*Captured: {date_str}*")
    lines.append("")
    
    # Main content
    if content.get("summary"):
        lines.append(f"**Summary:** {content['summary']}")
        lines.append("")
    
    if content.get("details"):
        lines.append(content["details"])
        lines.append("")
    
    if content.get("quote"):
        lines.append(f"> \"{content['quote']}\"")
        lines.append("")
    
    if content.get("implications"):
        lines.append(f"**Implications:** {content['implications']}")
        lines.append("")
    
    # Metadata footer
    source_type = extraction.get("source_type", "unknown")
    source_id = extraction.get("source_id", "unknown")
    confidence = extraction.get("confidence", 0)
    
    lines.append(f"*Source: {source_type} - {source_id}*  ")
    lines.append(f"*Confidence: {confidence:.2f}*")
    
    # Tags
    domain_tags = tags.get("domain", [])
    if domain_tags:
        lines.append(f"*Tags: {', '.join(domain_tags)}*")
    
    lines.append("")
    return "\n".join(lines)


def find_section(content: str, section_name: str) -> Optional[int]:
    """
    Find insertion point for section.
    
    Returns line index where section starts, or None if not found.
    """
    if not section_name:
        return None
    
    lines = content.split("\n")
    
    # Look for markdown heading matching section name
    for i, line in enumerate(lines):
        if line.strip().startswith("#") and section_name.lower() in line.lower():
            return i
    
    return None


def insert_at_section(content: str, section_name: str, new_content: str) -> str:
    """
    Insert content at end of specified section.
    
    If section not found, appends to end of file.
    """
    lines = content.split("\n")
    section_idx = find_section(content, section_name)
    
    if section_idx is None:
        # Section not found, append to end
        logging.warning(f"Section '{section_name}' not found, appending to end")
        return content + "\n\n" + new_content
    
    # Find end of section (next heading of same or higher level, or end of file)
    section_level = len(lines[section_idx].split()[0])  # Count # characters
    
    insert_idx = len(lines)  # Default to end
    for i in range(section_idx + 1, len(lines)):
        if lines[i].strip().startswith("#"):
            heading_level = len(lines[i].split()[0])
            if heading_level <= section_level:
                insert_idx = i
                break
    
    # Insert before the next section or at end
    lines.insert(insert_idx, new_content)
    return "\n".join(lines)


def write_to_knowledge(extraction: dict, target_override: str = "") -> bool:
    """
    Write extraction to Knowledge/ file.
    
    Returns True on success, False on failure.
    """
    try:
        routing = extraction.get("knowledge_routing", {})
        target = target_override or routing.get("target", "")
        action = routing.get("action", "append")
        section = routing.get("section", "")
        
        if not target:
            logging.error("No target specified in knowledge_routing")
            return False
        
        # Resolve target path into Personal/Knowledge buckets via routing helper
        target_path = resolve_target_path_from_legacy(target)
        
        # Check protection
        if not check_protection(target_path):
            logging.error(f"Target path is protected: {target_path}")
            return False
        
        # Format content
        formatted = format_content(extraction)
        
        # Handle different actions
        if action == "create":
            # Create new file with frontmatter
            if target_path.exists():
                logging.error(f"File already exists: {target_path} (action=create)")
                return False
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            today = datetime.now().strftime("%Y-%m-%d")
            frontmatter = f"""---
created: {today}
last_edited: {today}
version: 1.0
---

"""
            target_path.write_text(frontmatter + formatted)
            logging.info(f"✓ Created: {target_path}")
            
        elif action == "append":
            # Append to file or section
            if not target_path.exists():
                logging.warning(f"File doesn't exist, creating: {target_path}")
                target_path.parent.mkdir(parents=True, exist_ok=True)
                today = datetime.now().strftime("%Y-%m-%d")
                frontmatter = f"""---
created: {today}
last_edited: {today}
version: 1.0
---

"""
                target_path.write_text(frontmatter + formatted)
            else:
                existing = target_path.read_text()
                
                if section:
                    # Insert at section
                    updated = insert_at_section(existing, section, formatted)
                else:
                    # Append to end
                    updated = existing + "\n\n" + formatted
                
                target_path.write_text(updated)
                
                # Update last_edited in frontmatter
                try:
                    today = datetime.now().strftime("%Y-%m-%d")
                    updated = re.sub(
                        r"last_edited:\s*\d{4}-\d{2}-\d{2}",
                        f"last_edited: {today}",
                        updated
                    )
                    target_path.write_text(updated)
                except:
                    pass
            
            logging.info(f"✓ Appended to: {target_path}")
            
        elif action == "update":
            # Update existing content (not implemented - requires more context)
            logging.error(f"Update action not implemented")
            return False
        
        else:
            logging.error(f"Unknown action: {action}")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to write to Knowledge/: {e}", exc_info=True)
        return False


def main(yaml_file: Path, target_override: str = "", dry_run: bool = False) -> int:
    """Main execution."""
    try:
        logging.info(f"Processing extraction: {yaml_file}")
        
        if not yaml_file.exists():
            logging.error(f"File not found: {yaml_file}")
            return 1
        
        # Load extraction
        extraction = load_extraction(yaml_file)
        
        # Get target
        routing = extraction.get("knowledge_routing", {})
        target = target_override or routing.get("target", "")
        
        if not target:
            logging.error("No target specified")
            return 1
        
        logging.info(f"Target: {target}")
        
        if dry_run:
            logging.info("DRY RUN: Would write to Knowledge/")
            formatted = format_content(extraction)
            print("\n" + "="*60)
            print("Formatted content:")
            print("="*60)
            print(formatted)
            print("="*60)
            return 0
        
        # Write to Knowledge/
        success = write_to_knowledge(extraction, target_override=target_override)
        
        if success:
            logging.info("✓ Integration complete")
            return 0
        else:
            logging.error("Integration failed")
            return 1
        
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import re  # Import here for frontmatter updating
    
    parser = argparse.ArgumentParser(description="Integrate intelligence into Knowledge/ files")
    parser.add_argument("yaml_file", type=Path, help="Path to extraction YAML file")
    parser.add_argument("--target", type=str, help="Override target path")
    parser.add_argument("--dry-run", action="store_true", help="Preview but don't write")
    
    args = parser.parse_args()
    sys.exit(main(yaml_file=args.yaml_file, target_override=args.target, dry_run=args.dry_run))

