#!/usr/bin/env python3
"""
Document & Media Curator - Interactive approval workflow
Presents extracted intelligence for V review and approval
"""
import argparse
import logging
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

WORKSPACE = Path("/home/workspace")
PATHS_YAML = WORKSPACE / "N5/prefs/paths/knowledge_paths.yaml"


def _load_pk_roots() -> dict:
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


def resolve_destination_dir(destination: str) -> Path:
    """Route legacy Knowledge/* destinations into Personal/Knowledge buckets.

    Heuristics:
    - Choices containing "market_intelligence" → market intelligence root.
    - external_research/hypotheses/semi_stable/evolving → ContentLibrary/content under that path.
    - Custom/other choices → Intelligence root under the provided relative path.
    """
    roots = _load_pk_roots()
    norm = (destination or "").lstrip("/")

    if "market_intelligence" in norm:
        suffix = norm.split("market_intelligence/", 1)[1] if "market_intelligence/" in norm else ""
        return roots["market_root"] / suffix if suffix else roots["market_root"]

    top = norm.split("/", 1)[0]
    content_buckets = {"external_research", "hypotheses", "semi_stable", "evolving"}
    if top in content_buckets:
        return roots["content_root"] / norm

    # Default to Intelligence bucket
    return roots["intelligence_root"] / norm


class DocumentMediaCurator:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        # Legacy extracts live under Knowledge/intelligence; approved items
        # will be routed into Personal/Knowledge via resolve_destination_dir.
        self.intelligence_dir = WORKSPACE / "Knowledge/intelligence"
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            
    def get_pending_items(self):
        """Get all intelligence extracts pending review"""
        cursor = self.conn.cursor()
        
        # Get documents that have been processed
        docs = cursor.execute("""
            SELECT id, filename, filepath, processing_status, curation_score
            FROM documents
            WHERE processing_status = 'processed'
        """).fetchall()
        
        # Filter to only those with intelligence files not yet moved
        docs_with_intel = []
        for doc in docs:
            intel_path = self.intelligence_dir / "documents" / f"{doc['id']}_intelligence.md"
            if intel_path.exists():
                docs_with_intel.append((dict(doc), intel_path))
        
        # Check media table if it exists
        media_with_intel = []
        try:
            media = cursor.execute("""
                SELECT id, filename, filepath, processing_status, curation_score
                FROM media
                WHERE processing_status = 'processed'
            """).fetchall()
            
            for m in media:
                intel_path = self.intelligence_dir / "media" / f"{m['id']}_intelligence.md"
                if intel_path.exists():
                    media_with_intel.append((dict(m), intel_path))
        except sqlite3.OperationalError:
            pass  # Media table doesn't exist yet
        
        return docs_with_intel, media_with_intel
        
    def display_item(self, item, intel_path, item_type, index, total):
        """Display intelligence item for review"""
        print(f"\n{'='*80}")
        print(f"Item {index}/{total} ({item_type})")
        print(f"{'='*80}\n")
        
        print(f"**Filename:** {item['filename']}")
        print(f"**File:** {item['filepath']}")
        print(f"**Curation Score:** {item.get('curation_score', 0)}/10")
            
        # Show intelligence content
        if intel_path.exists():
            print(f"\n**Intelligence Extract:**\n")
            content = intel_path.read_text()
            # Show first 600 chars as preview
            preview = content[:600]
            if len(content) > 600:
                preview += "\n\n[... truncated, use [V] to view full intelligence ...]"
            print(preview)
            print(f"\n**Full intelligence path:** {intel_path}")
        else:
            print(f"\n**Intelligence file not found:** {intel_path}")
            
    def get_user_decision(self, intel_path):
        """Get V's decision on this item"""
        while True:
            print(f"\n{'-'*80}")
            print("Options:")
            print("  [A] Approve - Internalize to Knowledge/")
            print("  [R] Reject - Move to rejected/")
            print("  [S] Skip - Review later")
            print("  [V] View full intelligence file")
            print("  [Q] Quit curation session")
            
            choice = input("\nYour choice [A/R/S/V/Q]: ").strip().upper()
            
            if choice == 'V':
                if intel_path.exists():
                    print(f"\n{'-'*80}\n{intel_path.read_text()}\n{'-'*80}\n")
                else:
                    print(f"\n**File not found:** {intel_path}\n")
                continue
                
            if choice in ['A', 'R', 'S', 'Q']:
                return choice
                
            print("Invalid choice, please try again.")
            
    def get_knowledge_destination(self):
        """Get destination path in Knowledge/ for approved item"""
        print(f"\n**Destination options:**")
        print("  [1] external_research/ - Research papers, external studies")
        print("  [2] market_intelligence/ - Market reports, industry analysis")
        print("  [3] hypotheses/ - Working theories, product insights")
        print("  [4] semi_stable/ - Strategic positions, evolving knowledge")
        print("  [5] evolving/ - Active development, temporary knowledge")
        print("  [6] Custom path")
        
        destinations = {
            '1': 'external_research/',
            '2': 'market_intelligence/',
            '3': 'hypotheses/',
            '4': 'semi_stable/',
            '5': 'evolving/'
        }
        
        choice = input("\nChoice [1-6]: ").strip()
        
        if choice in destinations:
            return destinations[choice]
        elif choice == '6':
            custom = input("Enter path (relative to Knowledge/): ").strip()
            if not custom.endswith('/'):
                custom += '/'
            return custom
        else:
            print("Invalid choice, using evolving/ as default")
            return 'evolving/'
        
    def internalize_item(self, item_id, intel_path, destination, item_type):
        """Move intelligence to Knowledge/ and update database"""
        if not intel_path.exists():
            logging.error(f"Intelligence file not found: {intel_path}")
            return False
            
        # Route legacy Knowledge/* destination into Personal/Knowledge buckets
        dest_dir = resolve_destination_dir(destination)
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Move intelligence file to destination
        dest_file = dest_dir / intel_path.name
        
        # If file exists, version it
        if dest_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = dest_file.stem
            suffix = dest_file.suffix
            dest_file = dest_dir / f"{stem}_{timestamp}{suffix}"
            
        intel_path.rename(dest_file)
        logging.info(f"Moved intelligence to: {dest_file}")
        
        # Update curation log
        log_file = self.intelligence_dir / "curation_log.jsonl"
        import json
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "approved",
            "item_id": item_id,
            "item_type": item_type,
            "destination": str(dest_file)
        }
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return True
        
    def reject_item(self, item_id, intel_path, item_type):
        """Move intelligence to rejected/"""
        if not intel_path.exists():
            logging.warning(f"Intelligence file not found: {intel_path}")
            return False
            
        # Move to rejected/
        rejected_dir = self.intelligence_dir / "rejected"
        rejected_dir.mkdir(parents=True, exist_ok=True)
        
        dest_file = rejected_dir / intel_path.name
        intel_path.rename(dest_file)
        logging.info(f"Moved to rejected: {dest_file}")
        
        # Update curation log
        log_file = self.intelligence_dir / "curation_log.jsonl"
        import json
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "rejected",
            "item_id": item_id,
            "item_type": item_type,
            "destination": str(dest_file)
        }
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return True
        
    def run_curation_session(self, limit: int = None):
        """Interactive curation session"""
        docs, media = self.get_pending_items()
        
        # Combine into single list with item type
        all_items = [(item, path, 'document') for item, path in docs] + \
                    [(item, path, 'media') for item, path in media]
        
        if not all_items:
            print("\n✅ No items pending review!")
            return 0
            
        if limit:
            all_items = all_items[:limit]
            
        total = len(all_items)
        approved = 0
        rejected = 0
        skipped = 0
        
        print(f"\n📋 **Curation Session Started**")
        print(f"Total items to review: {total}")
        
        for idx, (item, intel_path, item_type) in enumerate(all_items, 1):
            self.display_item(item, intel_path, item_type, idx, total)
            
            decision = self.get_user_decision(intel_path)
            
            if decision == 'Q':
                print(f"\n⏸️  Curation session paused.")
                print(f"Reviewed: {idx-1}/{total}")
                print(f"Approved: {approved}, Rejected: {rejected}, Skipped: {skipped}")
                return 0
                
            if decision == 'A':
                destination = self.get_knowledge_destination()
                if self.internalize_item(item['id'], intel_path, destination, item_type):
                    print(f"\n✅ Internalized to Knowledge/{destination}")
                    approved += 1
                else:
                    print(f"\n❌ Failed to internalize")
                    
            elif decision == 'R':
                if self.reject_item(item['id'], intel_path, item_type):
                    print(f"\n🗑️  Rejected")
                    rejected += 1
                else:
                    print(f"\n❌ Failed to reject")
                    
            elif decision == 'S':
                print(f"\n⏭️  Skipped for later review")
                skipped += 1
                
        print(f"\n{'='*80}")
        print(f"**Curation Session Complete**")
        print(f"{'='*80}")
        print(f"Total reviewed: {total}")
        print(f"  Approved: {approved}")
        print(f"  Rejected: {rejected}")
        print(f"  Skipped: {skipped}")
        
        return 0

def main():
    parser = argparse.ArgumentParser(
        description="Interactive curator for documents & media intelligence"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of items to review (for quick sessions)"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("/home/workspace/N5/data/documents_media.db"),
        help="Database path"
    )
    
    args = parser.parse_args()
    
    if not args.db.exists():
        logging.error(f"Database not found: {args.db}")
        return 1
        
    try:
        with DocumentMediaCurator(args.db) as curator:
            return curator.run_curation_session(limit=args.limit)
    except KeyboardInterrupt:
        print("\n\n⏸️  Curation interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Curation error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

