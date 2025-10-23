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
from typing import Dict, List
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from content_library import ContentLibrary, Item
from b_block_parser import ResourceReference, EloquentLine

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class AutoPopulator:
    """Auto-populate Content Library from discovered content"""
    
    def __init__(self, dry_run: bool = False):
        self.content_library = ContentLibrary()
        self.dry_run = dry_run
        
    def process_blocks(self, blocks: Dict) -> Dict[str, List[Item]]:
        """
        Process B-blocks and add new items to library
        
        Returns:
            {
                "resources_added": [Item],
                "snippets_added": [Item],
                "skipped": [Item]
            }
        """
        results = {
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
        
        return results
    
    def _add_resource(self, res: ResourceReference) -> Item:
        """Add resource to library if not duplicate"""
        # Check if already exists
        existing = self.content_library.search(query=res.content, tags={})
        if existing:
            logger.info(f"Resource already exists: {res.content[:50]}")
            return None
        
        # Determine type: link or snippet
        is_link = res.content.startswith("http") or "." in res.content.split()[0]
        
        item = Item(
            id=self._generate_id(res.title or res.content),
            type="link" if is_link else "snippet",
            title=res.title or res.content[:50],
            content=res.content,
            url=res.content if is_link else None,
            tags={
                "_source": ["meeting"],
                "confidence": [res.confidence]
            },
            metadata={
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "deprecated": False,
                "version": 1,
                "notes": f"Auto-discovered from meeting. Context: {res.context[:100] if res.context else 'N/A'}",
                "source": "auto-populated"
            }
        )
        
        if not self.dry_run:
            self.content_library.upsert(item)
            logger.info(f"✓ Added {item.type}: {item.title}")
        else:
            logger.info(f"[DRY RUN] Would add {item.type}: {item.title}")
        
        return item
    
    def _add_eloquent_line(self, line: EloquentLine) -> Item:
        """Add eloquent line to library as snippet"""
        # Check if already exists
        existing = self.content_library.search(query=line.cleaned_text, tags={})
        if existing:
            logger.info(f"Snippet already exists: {line.cleaned_text[:50]}")
            return None
        
        # Auto-detect purpose/audience from content
        tags = {
            "_source": ["meeting"],
            "speaker": [line.speaker],
            "tone": ["eloquent"]
        }
        
        if line.audience_reaction:
            tags["reaction"] = [line.audience_reaction]
        
        # Detect purpose from content
        content_lower = line.cleaned_text.lower()
        if any(word in content_lower for word in ["divorce", "metaphor", "like"]):
            tags["purpose"] = ["hook", "analogy"]
        elif any(word in content_lower for word in ["helpless", "stuck", "frustrat"]):
            tags["purpose"] = ["empathy", "validation"]
        
        item = Item(
            id=self._generate_id(line.cleaned_text),
            type="snippet",
            title=f"Eloquent line: {line.cleaned_text[:50]}...",
            content=line.cleaned_text,
            url=None,
            tags=tags,
            metadata={
                "created": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "deprecated": False,
                "version": 1,
                "notes": f"Speaker: {line.speaker}. Original: {line.text[:100]}",
                "source": "auto-populated"
            }
        )
        
        if not self.dry_run:
            self.content_library.upsert(item)
            logger.info(f"✓ Added snippet: {item.title}")
        else:
            logger.info(f"[DRY RUN] Would add snippet: {item.title}")
        
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
                    "resources_added": [{"id": i.id, "title": i.title, "type": i.type} for i in results["resources_added"]],
                    "snippets_added": [{"id": i.id, "title": i.title, "type": i.type} for i in results["snippets_added"]],
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
