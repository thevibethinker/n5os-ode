#!/usr/bin/env python3
"""
N5 System Upgrades Add: Interactive command for adding items to the N5 system upgrades list.

This script provides a safe, validated way to add new upgrade items to the system,
with duplicate detection, backup creation, and support for both markdown and JSONL formats.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import sys
import shutil
import difflib
from lib import system_upgrades_sync
import re
from difflib import SequenceMatcher
from system_upgrades_backup_manager import BackupManager
import jsonschema
from lib.system_upgrades_validator import SystemUpgradesValidator, ValidationResult

# Constants
ROOT = Path(__file__).resolve().parents[1]
UPGRADES_MD = ROOT / "lists" / "system-upgrades.md"
UPGRADES_JSONL = ROOT / "lists" / "system-upgrades.jsonl"
BACKUP_DIR = ROOT / "backups" / "system-upgrades"

# Categories and priorities
CATEGORIES = ["Planned", "In Progress", "Done"]
PRIORITIES = {"L": "Low", "M": "Medium", "H": "High"}

def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def jaccard_similarity(a: str, b: str, n: int = 3) -> float:
    a_shingles = set(a[i:i+n] for i in range(len(a)-n+1))
    b_shingles = set(b[i:i+n] for i in range(len(b)-n+1))
    if not a_shingles or not b_shingles:
        return 0.0
    intersection = len(a_shingles.intersection(b_shingles))
    union = len(a_shingles.union(b_shingles))
    return intersection / union

class UpgradeManager:
    def __init__(self):
        self.md_path = UPGRADES_MD
        self.jsonl_path = UPGRADES_JSONL
        self.backup_manager = BackupManager()
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path:
        """Create timestamped backup of both files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_md = self.backup_dir / f"system-upgrades_{timestamp}.md"
        backup_jsonl = self.backup_dir / f"system-upgrades_{timestamp}.jsonl"

        if self.md_path.exists():
            shutil.copy2(self.md_path, backup_md)
        if self.jsonl_path.exists():
            shutil.copy2(self.jsonl_path, backup_jsonl)

        return backup_md

    def load_existing_items(self) -> Tuple[List[Dict], str]:
        return system_upgrades_sync.list_upgrades(self.jsonl_path), open(self.md_path, 'r', encoding='utf-8').read() if self.md_path.exists() else ""

    def check_duplicates(self, title: str, items: List[Dict], threshold: float = 0.82) -> List[Tuple[str, float]]:
        duplicates = []
        norm_title = normalize_title(title)

        for item in items:
            existing_title = item.get('title', '')
            norm_existing = normalize_title(existing_title)
            if norm_existing == norm_title:
                duplicates.append((existing_title, 1.0))
                continue

            jacc = jaccard_similarity(norm_title, norm_existing)
            lev = SequenceMatcher(None, norm_title, norm_existing).ratio()
            score = (jacc + lev) / 2
            if score >= threshold:
                duplicates.append((existing_title, score))

        return duplicates

    def generate_item_id(self) -> str:
        """Generate a unique item ID."""
        return str(uuid.uuid4())

    def add_upgrade_item(self, title: str = None, category: str = "Planned",
                        description: str = None, priority: str = "M",
                        tags: List[str] = None, interactive: bool = True, force: bool = False,
                        dry_run: bool = False, verify: bool = False, rollback: bool = False,
                        dupe_threshold: float = 0.82) -> Tuple[str, Path, Path]:
        if rollback:
            print("[33mAttempting rollback from latest backup...[0m")
            success = self.backup_manager.restore_from_backup()
            if success:
                print("[32mRollback successful.[0m")
            else:
                print("[31mRollback failed.[0m")
            return None, None, None

        # Create backup
        print("[36mCreating backup before add operation...[0m")
        try:
            backup_md, backup_jsonl, metadata = self.backup_manager.create_backup(operation_type="add")
        except Exception as e:
            print(f"[31mError creating backup: {e}[0m")
            if not force:
                raise

        # Get input data
        if interactive and (title is None or description is None):
            item_data = self.interactive_input()
        else:
            if not title or not description:
                raise ValueError("Title and description are required when not in interactive mode")
            item_data = {
                'title': title,
                'category': category,
                'description': description,
                'priority': priority,
                'tags': tags or []
            }

        # Validate category
        if item_data['category'] not in CATEGORIES:
            raise ValueError(f"Invalid category: {item_data['category']}. Must be one of: {', '.join(CATEGORIES)}")

        # Load existing items
        print("Loading existing items...")
        items = system_upgrades_sync.list_upgrades(self.jsonl_path)
        current_md = open(self.md_path, 'r', encoding='utf-8').read() if self.md_path.exists() else ""

        # Check for duplicates
        print("Checking for duplicates...")
        duplicates = self.check_duplicates(item_data['title'], items, threshold=dupe_threshold)
        if duplicates and not force:
            print("Warning: Potential duplicates found")
            for dup_title, score in duplicates:
                print(f"  - {dup_title} (score: {score:.2f})")
            if interactive and not force:
                if not input("Continue anyway? (y/N): ").lower().startswith('y'):
                    # Log duplicate prevention
                    self.log_telemetry_event('dupe_prevented', {'count': len(duplicates)})
                    raise ValueError("Operation cancelled due to potential duplicates")
            else:
                # Log duplicate prevention
                self.log_telemetry_event('dupe_prevented', {'count': len(duplicates)})
                raise ValueError("Potential duplicates found; use --force to proceed")

        # Generate item
        item_id = self.generate_item_id()
        now = datetime.now(timezone.utc)

        item = {
            'id': item_id,
            'title': item_data['title'],
            'summary': item_data['description'][:200] + "..." if len(item_data['description']) > 200 else item_data['description'],
            'status': 'open',
            'created_at': now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'priority': item_data['priority'],
            'tags': item_data['tags'],
            'category': item_data['category'],
            'body': item_data['description']
        }

        # Validate item
        validator = SystemUpgradesValidator(schema_path=ROOT / "schemas" / "system-upgrades.schema.json")
        validation_result = validator.validate_item(item)
        if not validation_result.is_valid:
            print("Validation failed with the following errors:")
            for err in validation_result.errors:
                print(f"  - {err}")
            if not force:
                raise ValueError("Validation failed. Use --force to override.")

        if dry_run:
            print("Dry-run mode: No files will be modified.")
            print(f"New item would be:\n{json.dumps(item, indent=2)}")
            simulated_md = system_upgrades_sync.render_markdown(items + [item])
            diff = difflib.unified_diff(current_md.splitlines(), simulated_md.splitlines(), fromfile='current.md', tofile='simulated.md', lineterm='')
            print("Markdown diff:")
            print('\n'.join(diff))
            return None, None, None

        # Add to stores
        print("Adding item atomically...")

        try:
            system_upgrades_sync.write_upgrade(self.md_path, self.jsonl_path, item)
        except Exception as e:
            print(f"Error writing item: {e}")
            print("Attempting rollback...")
            self.backup_manager.restore_from_backup()
            raise

        if verify:
            print("Verifying write operation...")
            new_items = system_upgrades_sync.list_upgrades(self.jsonl_path)
            if not any(it.get('id') == item_id for it in new_items):
                print("Verification failed: item missing in JSONL")
                print("Attempting rollback...")
                self.backup_manager.restore_from_backup()
                raise ValueError("Verification failed: item missing in JSONL")

            new_md = open(self.md_path, 'r', encoding='utf-8').read()
            if item['title'] not in new_md:
                print("Verification failed: item missing in Markdown")
                print("Attempting rollback...")
                self.backup_manager.restore_from_backup()
                raise ValueError("Verification failed: item missing in Markdown")

            print("Verification successful.")

        print(f"Item {item_id} added successfully.")

        return item_id, self.md_path, self.jsonl_path

    def edit_upgrade_item(self, item_id: str, field: str, value: str) -> None:
        print(f"📝 Editing item {item_id}...")

        # Create backup
        self.create_backup()

        # Patch
        patch = {field: value}

        # Edit atomically
        print("🔧 Applying update atomically...")
        system_upgrades_sync.edit_upgrade(self.jsonl_path, item_id, patch)

        print(f"✅ Item {item_id} updated successfully!")

    def list_upgrades(self, category: str = None, format: str = "table") -> None:
        items = system_upgrades_sync.list_upgrades(self.jsonl_path, filters={'category': category} if category else None)

        if not items:
            print("No upgrade items found.")
            return

        if format == "json":
            print(json.dumps(items, indent=2))
        elif format == "table":
            self._print_table(items)
        else:
            self._print_summary(items)

    def _print_table(self, items: List[Dict]) -> None:
        """Print items in table format."""
        print(f"{'ID':<36} {'Title':<50} {'Category':<15} {'Priority':<8} {'Status':<10}")
        print("-" * 120)
        for item in items:
            item_id = item.get('id', '')[:36]
            title = item.get('title', '')[:49]
            category = item.get('category', '')[:14]
            priority = item.get('priority', '')[:7]
            status = item.get('status', '')[:9]
            print(f"{item_id:<36} {title:<50} {category:<15} {priority:<8} {status:<10}")

    def _print_summary(self, items: List[Dict]) -> None:
        """Print items in summary format."""
        for category in CATEGORIES:
            cat_items = [item for item in items if item.get('category') == category]
            if cat_items:
                print(f"\n## {category} ({len(cat_items)} items)")
                for item in cat_items:
                    print(f"- {item.get('title', '')} [{item.get('priority', 'M')}]")

    def interactive_input(self) -> Dict:
        """Collect input interactively from user."""
        print("🆕 N5 System Upgrades Add")
        print("=" * 40)

        # Title
        while True:
            title = input("Title: ").strip()
            if title:
                break
            print("❌ Title is required.")

        # Category
        print(f"\nCategories: {', '.join(CATEGORIES)}")
        while True:
            category = input("Category [Planned]: ").strip()
            if not category:
                category = "Planned"
            if category in CATEGORIES:
                break
            print(f"❌ Invalid category. Choose from: {', '.join(CATEGORIES)}")

        # Description
        while True:
            description = input("Description: ").strip()
            if description:
                break
            print("❌ Description is required.")

        # Priority
        print(f"\nPriorities: L=Low, M=Medium, H=High")
        while True:
            priority_input = input("Priority [M]: ").strip().upper()
            if not priority_input:
                priority_input = "M"
            if priority_input in PRIORITIES:
                priority = priority_input
                break
            print("❌ Invalid priority. Choose L, M, or H.")

        # Tags (optional)
        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else []

        return {
            'title': title,
            'category': category,
            'description': description,
            'priority': priority,
            'tags': tags
        }

    def rollback(self, backup_timestamp: str = None):
        backups = sorted(self.backup_dir.glob("system-upgrades_*.md"))
        if not backups:
            raise ValueError("No backups available")
        
        if backup_timestamp:
            backup_md = self.backup_dir / f"system-upgrades_{backup_timestamp}.md"
            backup_jsonl = self.backup_dir / f"system-upgrades_{backup_timestamp}.jsonl"
            if not backup_md.exists() or not backup_jsonl.exists():
                raise ValueError(f"Backup {backup_timestamp} not found")
        else:
            print("Available backups:")
            for i, b in enumerate(backups, 1):
                print(f"{i}: {b.stem.split('_')[1]}")
            choice = int(input("Select backup number: "))
            backup_md = backups[choice-1]
            backup_jsonl = backup_md.with_suffix(".jsonl")

        print(f"Restoring from {backup_md.stem}...")
        shutil.copy2(backup_md, self.md_path)
        shutil.copy2(backup_jsonl, self.jsonl_path)
        print("✅ Restore complete")

    def log_telemetry_event(self, event_type: str, data: dict = None):
        """Log telemetry event for metrics collection."""
        import logging
        from pathlib import Path
        
        log_dir = Path(__file__).resolve().parents[1] / "logs" / "system-upgrades"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        log_file = log_dir / f"telemetry_events_{today_str}.log"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data or {}
            }
            f.write(json.dumps(event, ensure_ascii=False) + '\n')

def main():
    parser = argparse.ArgumentParser(description="Manage N5 system upgrades list")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add new upgrade item")
    add_parser.add_argument("--title", help="Upgrade item title")
    add_parser.add_argument("--category", choices=CATEGORIES, default="Planned",
                           help="Category for the upgrade item")
    add_parser.add_argument("--description", help="Detailed description of the upgrade")
    add_parser.add_argument("--priority", choices=["L", "M", "H"], default="M",
                           help="Priority level")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--interactive", action="store_true", default=True,
                           help="Use interactive mode")
    add_parser.add_argument("--no-interactive", action="store_false", dest="interactive",
                           help="Disable interactive mode")
    add_parser.add_argument("--force", action="store_true", help="Force add even if duplicates found")
    add_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    add_parser.add_argument("--verify", action="store_true", help="Verify after write")
    add_parser.add_argument("--rollback", action="store_true", help="Rollback to latest backup")
    add_parser.add_argument("--dupe-threshold", type=float, default=0.82, help="Duplicate similarity threshold")
    add_parser.add_argument("--prune-backups", action="store_true", help="Manually prune old backups")

    # List command
    list_parser = subparsers.add_parser("list", help="List upgrade items")
    list_parser.add_argument("--category", choices=CATEGORIES,
                            help="Filter by category")
    list_parser.add_argument("--format", choices=["table", "json", "summary"], default="table",
                            help="Output format")

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit existing upgrade item")
    edit_parser.add_argument("item_id", help="Item ID to edit")
    edit_parser.add_argument("field", choices=["title", "description", "category", "priority", "status"],
                            help="Field to edit")
    edit_parser.add_argument("value", help="New value")

    rollback_parser = subparsers.add_parser("rollback", help="Rollback to a previous backup")
    rollback_parser.add_argument("--timestamp", help="Specific backup timestamp to restore")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        manager = UpgradeManager()

        if args.command == "add":
            # Parse tags
            tags = None
            if hasattr(args, 'tags') and args.tags:
                tags = [tag.strip() for tag in args.tags.split(',') if tag.strip()]

            item_id, md_path, jsonl_path = manager.add_upgrade_item(
                title=getattr(args, 'title', None),
                category=getattr(args, 'category', 'Planned'),
                description=getattr(args, 'description', None),
                priority=getattr(args, 'priority', 'M'),
                tags=tags,
                interactive=getattr(args, 'interactive', True),
                force=getattr(args, 'force', False),
                dry_run=getattr(args, 'dry_run', False),
                verify=getattr(args, 'verify', False),
                dupe_threshold=getattr(args, 'dupe_threshold', 0.82)
            )

            # Output for N5 system
            result = {
                'item_id': item_id,
                'path': str(md_path),
                'jsonl_path': str(jsonl_path)
            }
            print(json.dumps(result))

            if getattr(args, 'prune_backups', False):
                print("\u001b[36mPruning old backups...\u001b[0m")
                from system_upgrades_backup_manager import BackupManager
                bm = BackupManager()
                prune_result = bm.prune_backups()
                print(f"Pruning completed. Removed {prune_result['removed']} backups, retained {prune_result['retained']} backups.")

            # Auto prune after successful add
            if not getattr(args, 'prune_backups', False):
                bm = BackupManager()
                bm.prune_backups()

        elif args.command == "list":
            manager.list_upgrades(
                category=getattr(args, 'category', None),
                format=getattr(args, 'format', 'table')
            )

        elif args.command == "edit":
            manager.edit_upgrade_item(args.item_id, args.field, args.value)
            print(f"✅ Item {args.item_id} updated successfully!")

        elif args.command == "rollback":
            manager.rollback(getattr(args, 'timestamp', None))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()