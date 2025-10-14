#!/usr/bin/env python3
"""
CRM Index Rebuild - Phase 4
Scans all profile files and generates complete index.jsonl
"""
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

def extract_frontmatter(content: str) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown file."""
    pattern = r'^---\n(.*?)\n---'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    frontmatter_text = match.group(1)
    metadata = {}
    
    # Parse simple YAML key-value pairs
    for line in frontmatter_text.split('\n'):
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        
        # Handle arrays (simple bracket notation)
        if value.startswith('[') and value.endswith(']'):
            value = value[1:-1].strip()
            if value:
                metadata[key] = [v.strip().strip('"').strip("'") for v in value.split(',')]
            else:
                metadata[key] = []
        else:
            metadata[key] = value
    
    return metadata

def build_index_entry(filepath: Path, metadata: Dict) -> Dict:
    """Build index entry from file metadata."""
    return {
        "file": str(filepath.relative_to('/home/workspace')),
        "name": metadata.get("name", "Unknown"),
        "email": metadata.get("email_primary", ""),
        "organization": metadata.get("organization", ""),
        "role": metadata.get("role", ""),
        "status": metadata.get("status", "unknown"),
        "lead_type": metadata.get("lead_type", ""),
        "first_contact": metadata.get("first_contact", ""),
        "last_updated": metadata.get("last_updated", ""),
        "interaction_count": int(metadata.get("interaction_count", 0)) if metadata.get("interaction_count") else 0,
        "last_interaction": metadata.get("last_interaction", ""),
        "tags": metadata.get("tags", []) if isinstance(metadata.get("tags"), list) else []
    }

def scan_profiles(profiles_dir: Path) -> List[Dict]:
    """Scan all profile files and extract metadata."""
    entries = []
    errors = []
    
    profile_files = sorted(profiles_dir.glob("*.md"))
    
    for filepath in profile_files:
        # Skip template
        if filepath.name == "_template.md":
            logger.info(f"Skipping template: {filepath.name}")
            continue
        
        try:
            content = filepath.read_text()
            metadata = extract_frontmatter(content)
            
            if not metadata:
                logger.warning(f"No frontmatter found: {filepath.name}")
                errors.append({"file": filepath.name, "error": "No frontmatter"})
                continue
            
            entry = build_index_entry(filepath, metadata)
            entries.append(entry)
            logger.info(f"✓ Indexed: {filepath.name} ({entry['name']})")
            
        except Exception as e:
            logger.error(f"Error processing {filepath.name}: {e}")
            errors.append({"file": filepath.name, "error": str(e)})
    
    return entries, errors

def write_index(entries: List[Dict], output_path: Path, dry_run: bool = False):
    """Write entries to index.jsonl."""
    if dry_run:
        logger.info(f"[DRY RUN] Would write {len(entries)} entries to {output_path}")
        return
    
    with output_path.open('w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + '\n')
    
    logger.info(f"✓ Wrote {len(entries)} entries to {output_path}")

def validate_index(index_path: Path, expected_count: int) -> bool:
    """Validate the generated index."""
    if not index_path.exists():
        logger.error(f"Index file not found: {index_path}")
        return False
    
    with index_path.open('r') as f:
        lines = f.readlines()
    
    actual_count = len(lines)
    
    if actual_count != expected_count:
        logger.error(f"Count mismatch: expected {expected_count}, got {actual_count}")
        return False
    
    # Validate JSON structure
    for i, line in enumerate(lines, 1):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON on line {i}: {e}")
            return False
    
    logger.info(f"✓ Validation passed: {actual_count} entries, all valid JSON")
    return True

def main(dry_run: bool = False) -> int:
    """Execute Phase 4: Index Rebuild."""
    try:
        profiles_dir = Path("/home/workspace/Knowledge/crm/profiles")
        index_path = Path("/home/workspace/Knowledge/crm/index.jsonl")
        
        if not profiles_dir.exists():
            logger.error(f"Profiles directory not found: {profiles_dir}")
            return 1
        
        logger.info("=== Phase 4: CRM Index Rebuild ===")
        logger.info(f"Scanning: {profiles_dir}")
        
        # Scan profiles
        entries, errors = scan_profiles(profiles_dir)
        
        # Expected count (58 total - 1 template = 57 profiles)
        profile_count = len(list(profiles_dir.glob("*.md"))) - 1
        
        logger.info(f"\n=== Scan Results ===")
        logger.info(f"Profiles found: {profile_count}")
        logger.info(f"Successfully indexed: {len(entries)}")
        logger.info(f"Errors: {len(errors)}")
        
        if errors:
            logger.warning("\nErrors encountered:")
            for error in errors:
                logger.warning(f"  - {error['file']}: {error['error']}")
        
        if len(entries) != profile_count:
            logger.warning(f"Warning: Indexed {len(entries)}/{profile_count} profiles")
        
        # Write index
        write_index(entries, index_path, dry_run)
        
        if not dry_run:
            # Validate
            if not validate_index(index_path, len(entries)):
                return 1
            
            logger.info(f"\n✓ Phase 4 Complete: {len(entries)} profiles indexed")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild CRM index")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    exit(main(dry_run=args.dry_run))
