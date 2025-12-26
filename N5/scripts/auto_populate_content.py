#!/usr/bin/env python3
"""
Auto-Populate Content Library from Meeting Blocks
Discovers resources and eloquent lines, adds to library with user approval
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

# Local imports for sibling modules
sys.path.insert(0, str(Path(__file__).parent))

# === V3 CONTENT LIBRARY IMPORT ===
from content_library_v3 import ContentLibraryV3
# === END V3 IMPORT ===

from b_block_parser import ResourceReference, EloquentLine

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class AutoPopulator:
    """Auto-populate Content Library from discovered content"""
    
    def __init__(self, dry_run: bool = False):
        self.content_library = ContentLibraryV3()
        self.dry_run = dry_run
        
    def process_blocks(self, blocks: Dict) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process B-blocks and add new items to library
        
        Returns:
            {
                "resources_added": [item_dict],
                "snippets_added": [item_dict],
                "skipped": [item_dict_or_reason]
            }
        """
        results: Dict[str, List[Any]] = {
            "resources_added": [],
            "snippets_added": [],
            "skipped": []
        }
        
        # 1. Process resources (only explicit ones for now)
        resources_explicit = [ResourceReference(**r) for r in blocks.get("resources_explicit", [])]
        for res in resources_explicit:
            result = self._add_resource(res)
            if result:
                results["resources_added"].append(result)
            else:
                results["skipped"].append({"type": "resource", "content": res.content})
        
        # 2. Process eloquent lines
        eloquent_lines = [EloquentLine(**e) for e in blocks.get("eloquent_lines", [])]
        for line in eloquent_lines:
            result = self._add_eloquent_line(line)
            if result:
                results["snippets_added"].append(result)
            else:
                results["skipped"].append({"type": "snippet", "content": line.cleaned_text[:50]})
        
        return results  # type: ignore[return-value]
    
    def _flatten_tags(self, tags: Dict[str, List[Any]]) -> Dict[str, str]:
        """Flatten legacy Dict[str, List[Any]] tags to Dict[str, str] for v3.
        
        Multiple values are joined with commas.
        """
        flat: Dict[str, str] = {}
        for key, values in tags.items():
            if not values:
                continue
            if isinstance(values, list):
                flat[key] = ",".join(str(v) for v in values)
            else:
                flat[key] = str(values)
        return flat
    
    def _add_resource(self, res: ResourceReference) -> Optional[Dict[str, Any]]:
        """Add resource to library via ContentLibraryV3 if not duplicate"""
        # Determine type: link or snippet
        is_link = res.content.startswith("http") or "." in res.content.split()[0]
        item_type = "link" if is_link else "snippet"
        
        # Check if already exists (simple text search by content and type)
        existing = self.content_library.search(
            query=res.content,
            item_type=item_type,
            limit=1,
        )
        if existing:
            logger.info("Resource already exists: %s", res.content[:50])
            return None
        
        tags_v1 = {
            "_source": ["meeting"],
            "confidence": [res.confidence],
        }
        notes = f"Auto-discovered from meeting. Context: {res.context[:100] if res.context else 'N/A'}"
        new_id = self._generate_id(res.title or res.content)
        title = res.title or res.content[:50]
        
        if self.dry_run:
            logger.info("[DRY RUN] Would add %s: %s", item_type, title)
            return {
                "id": new_id,
                "item_type": item_type,
                "title": title,
                "url": res.content if is_link else None,
                "content": None if is_link else res.content,
                "tags": self._flatten_tags(tags_v1),
                "notes": notes,
            }
        
        item = self.content_library.add(
            id=new_id,
            item_type=item_type,
            title=title,
            url=res.content if is_link else None,
            content=None if is_link else res.content,
            tags=self._flatten_tags(tags_v1),
            notes=notes,
        )
        logger.info("✓ Added %s: %s", item.get("item_type"), item.get("title"))
        return item
    
    def _add_eloquent_line(self, line: EloquentLine) -> Optional[Dict[str, Any]]:
        """Add eloquent line to library as snippet via ContentLibraryV3"""
        # Check if already exists
        existing = self.content_library.search(
            query=line.cleaned_text,
            item_type="snippet",
            limit=1,
        )
        if existing:
            logger.info("Snippet already exists: %s", line.cleaned_text[:50])
            return None
        
        # Auto-detect purpose/audience from content
        tags_v1: Dict[str, List[Any]] = {
            "_source": ["meeting"],
            "speaker": [line.speaker],
            "tone": ["eloquent"],
        }
        
        if line.audience_reaction:
            tags_v1.setdefault("reaction", []).append(line.audience_reaction)
        
        content_lower = line.cleaned_text.lower()
        if any(word in content_lower for word in ["divorce", "metaphor", "like"]):
            tags_v1.setdefault("purpose", []).extend(["hook", "analogy"])
        elif any(word in content_lower for word in ["helpless", "stuck", "frustrat"]):
            tags_v1.setdefault("purpose", []).extend(["empathy", "validation"])
        
        notes = f"Speaker: {line.speaker}. Original: {line.text[:100]}"
        new_id = self._generate_id(line.cleaned_text)
        title = f"Eloquent line: {line.cleaned_text[:50]}..."
        
        if self.dry_run:
            logger.info("[DRY RUN] Would add snippet: %s", title)
            return {
                "id": new_id,
                "item_type": "snippet",
                "title": title,
                "url": None,
                "content": line.cleaned_text,
                "tags": self._flatten_tags(tags_v1),
                "notes": notes,
            }
        
        item = self.content_library.add(
            id=new_id,
            item_type="snippet",
            title=title,
            url=None,
            content=line.cleaned_text,
            tags=self._flatten_tags(tags_v1),
            notes=notes,
        )
        logger.info("✓ Added snippet: %s", item.get("title"))
        return item
    
    def _generate_id(self, text: str) -> str:
        """Generate unique ID from text"""
        import re
        # Remove special chars, lowercase, truncate
        clean = re.sub(r'[^a-z0-9]+', '_', text.lower())
        return clean[:60].rstrip('_')


def main():
    parser = argparse.ArgumentParser(
        description="Auto-populate Content Library from meeting B-blocks"
    )
    parser.add_argument("blocks_json", help="Path to B-blocks JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without adding")
    parser.add_argument("--output", help="Output JSON with results")
    
    args = parser.parse_args()
    
    # Load blocks
    with open(args.blocks_json, 'r') as f:
        blocks = json.load(f)
    
    # Process
    populator = AutoPopulator(dry_run=args.dry_run)
    results = populator.process_blocks(blocks)
    
    # Output results
    summary = {
        "resources_added": len(results["resources_added"]),
        "snippets_added": len(results["snippets_added"]),
        "skipped": len(results["skipped"]),
        "dry_run": args.dry_run
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({
                "summary": summary,
                "results": {
                    "resources_added": [
                        {"id": i.get("id"), "title": i.get("title"), "type": i.get("item_type")} 
                        for i in results["resources_added"]
                    ],
                    "snippets_added": [
                        {"id": i.get("id"), "title": i.get("title"), "type": i.get("item_type")} 
                        for i in results["snippets_added"]
                    ],
                    "skipped": results["skipped"]
                }
            }, f, indent=2)
    else:
        logger.info(f"\n{'='*70}")
        logger.info("AUTO-POPULATION SUMMARY")
        logger.info(f"{'='*70}")
        logger.info(f"Resources added: {summary['resources_added']}")
        logger.info(f"Snippets added: {summary['snippets_added']}")
        logger.info(f"Skipped (duplicates): {summary['skipped']}")
        if args.dry_run:
            logger.info("\n[DRY RUN] No changes made to library")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

