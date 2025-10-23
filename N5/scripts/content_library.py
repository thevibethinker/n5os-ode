#!/usr/bin/env python3
"""
Content Library (Links + Snippets)
- JSON-backed SSOT for links and reusable text snippets
- CLI + importable API

File path (default): /home/workspace/N5/prefs/communication/content-library.json

Usage examples:
  # Ensure file exists
  python3 N5/scripts/content_library.py init

  # Add a link
  python3 N5/scripts/content_library.py add --type link --title "Zo Referral" --url "https://www.zo.computer/?promo=VATT50" --tag topic=zo --tag category=referrals --tag entity=careerspan

  # Add a snippet
  python3 N5/scripts/content_library.py add --type snippet --title "Bio (short)" --content "Founder, Careerspan..." --tag audience=investors --tag tone=confident

  # Search by keyword and tags
  python3 N5/scripts/content_library.py search --query zo --tag category=referrals

  # Deprecate an item
  python3 N5/scripts/content_library.py deprecate --id zo_referral

  # Migrate from essential-links.json
  python3 N5/scripts/content_library.py migrate-from-essential
"""

from __future__ import annotations
import argparse
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("content_library")

DEFAULT_PATH = Path("/home/workspace/N5/prefs/communication/content-library.json")
ESSENTIAL_PATH = Path("/home/workspace/N5/prefs/communication/essential-links.json")


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class Item:
    id: str
    type: str  # "link" | "snippet"
    title: str
    content: Optional[str] = None  # for snippets
    url: Optional[str] = None      # for links
    tags: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "created": now_iso(),
        "updated": now_iso(),
        "deprecated": False,
        "expires_at": None,
        "version": 1,
        "last_used": None
    })

    def matches(self, query: Optional[str], tag_filters: Dict[str, List[str]]) -> bool:
        if query:
            hay = " ".join([self.title or "", self.content or "", self.url or ""]).lower()
            if query.lower() not in hay:
                return False
        for k, vals in tag_filters.items():
            item_vals = self.tags.get(k, [])
            if not any(v in item_vals for v in vals):
                return False
        if self.metadata.get("deprecated"):
            return False
        exp = self.metadata.get("expires_at")
        if exp:
            try:
                if datetime.fromisoformat(exp) < datetime.now():
                    return False
            except Exception:
                pass
        return True


class ContentLibrary:
    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = Path(path)
        self.data: Dict[str, Any] = {}
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = {"meta": {"version": "1.0.0", "last_updated": now_iso(), "format": "N5-content-library"}, "items": []}
            self.save()

    def save(self) -> None:
        self.data["meta"]["last_updated"] = now_iso()
        ensure_parent(self.path)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def list_items(self) -> List[Item]:
        return [Item(**i) for i in self.data.get("items", [])]

    def upsert(self, item: Item) -> None:
        items = self.data.setdefault("items", [])
        for i, existing in enumerate(items):
            if existing.get("id") == item.id:
                items[i] = asdict(item)
                self.save()
                return
        items.append(asdict(item))
        self.save()

    def get(self, item_id: str) -> Optional[Item]:
        for i in self.list_items():
            if i.id == item_id:
                return i
        return None

    def search(self, query: Optional[str], tags: Dict[str, List[str]]) -> List[Item]:
        return [i for i in self.list_items() if i.matches(query, tags)]

    def deprecate(self, item_id: str, expires_at: Optional[str] = None) -> bool:
        item = self.get(item_id)
        if not item:
            return False
        item.metadata["deprecated"] = True
        item.metadata["updated"] = now_iso()
        item.metadata["expires_at"] = expires_at
        self.upsert(item)
        return True

    def migrate_from_essential(self, essential_path: Path = ESSENTIAL_PATH) -> int:
        if not essential_path.exists():
            logger.warning(f"Essential links file not found at {essential_path}")
            return 0
        data = json.loads(essential_path.read_text())
        count = 0

        def add_link(item_id: str, title: str, url: str, tag_path: List[str]):
            nonlocal count
            if not url:
                return
            tags = {
                "category_path": tag_path,
                "type": ["link"],
            }
            item = Item(
                id=item_id,
                type="link",
                title=title,
                url=url,
                tags=tags,
            )
            self.upsert(item)
            count += 1

        # Flatten known sections
        for cat, val in data.items():
            if cat in ("meta",):
                continue
            if isinstance(val, dict):
                # Nested categories
                for subk, subv in val.items():
                    if isinstance(subv, dict):
                        for leafk, leafv in subv.items():
                            if isinstance(leafv, str):
                                item_id = f"{cat}_{subk}_{leafk}"
                                title = f"{cat} / {subk} / {leafk}"
                                add_link(item_id, title, leafv, [cat, subk])
                    elif isinstance(subv, str):
                        item_id = f"{cat}_{subk}"
                        title = f"{cat} / {subk}"
                        add_link(item_id, title, subv, [cat])
            elif isinstance(val, str):
                item_id = cat
                title = cat
                add_link(item_id, title, val, [cat])

        logger.info(f"Migrated {count} links from Essential Links")
        return count


def parse_tag_args(tag_str: Optional[str]) -> Dict[str, List[str]]:
    """Parse comma-separated tags like 'key=val,key2=val2,key3=val3'"""
    tags: Dict[str, List[str]] = {}
    if not tag_str:
        return tags
    for t in tag_str.split(","):
        t = t.strip()
        if not t:
            continue
        if "=" in t:
            k, v = t.split("=", 1)
            tags.setdefault(k.strip(), []).append(v.strip())
        else:
            tags.setdefault("_", []).append(t)
    return tags


def classify_content(content: str, title: str = "") -> Tuple[str, Dict[str, List[str]]]:
    """
    Auto-classify content type and infer tags.
    Returns: (type, tags_dict)
    """
    content_lower = content.lower()
    title_lower = title.lower()
    combined = f"{title_lower} {content_lower}"
    
    # Detect type - check for URLs anywhere in content
    has_url = ("http://" in content or "https://" in content) or content.strip().startswith(("http://", "https://"))
    # If content is ONLY a URL, or title+content looks like a link reference
    is_pure_url = content.strip().startswith(("http://", "https://")) and len(content.split()) == 1
    is_link_ref = has_url and ("link" in title_lower or len(content.split()) <= 10)
    item_type = "link" if (is_pure_url or is_link_ref) else "snippet"
    
    tags = {}
    
    # Infer purpose
    purpose_signals = {
        "bio": ["founder", "ceo", "background", "experience", "career"],
        "education": ["guide", "how to", "learn", "tutorial", "readiness"],
        "scheduling": ["calendly", "meeting", "book", "schedule"],
        "referral": ["promo", "referral", "discount", "code"],
        "product": ["feature", "product", "demo", "walkthrough"],
        "hook": ["pitch", "hook", "opening", "intro"],
        "signature": ["signature", "footer", "contact"],
        "resource": ["article", "resource", "link", "reference"]
    }
    
    detected_purposes = []
    for purpose, keywords in purpose_signals.items():
        if any(kw in combined for kw in keywords):
            detected_purposes.append(purpose)
    
    if detected_purposes:
        tags["purpose"] = detected_purposes
    
    # Infer audience
    audience_signals = {
        "founders": ["founder", "startup", "entrepreneur"],
        "job_seekers": ["job", "career", "resume", "interview"],
        "investors": ["investor", "fundraising", "pitch"],
        "operators": ["operator", "leader", "executive"],
        "general": []  # default
    }
    
    detected_audiences = []
    for audience, keywords in audience_signals.items():
        if audience == "general":
            continue
        if any(kw in combined for kw in keywords):
            detected_audiences.append(audience)
    
    if not detected_audiences:
        detected_audiences.append("general")
    
    tags["audience"] = detected_audiences
    
    # Infer tone
    tone_signals = {
        "concise": len(content.split()) < 50,
        "detailed": len(content.split()) > 200,
        "formal": any(word in content_lower for word in ["hereby", "pursuant", "accordance"]),
        "casual": any(word in content_lower for word in ["hey", "cool", "awesome", "yeah"]),
        "provocative": any(char in content for char in ["?", "!"]) and len(content.split()) < 100
    }
    
    detected_tones = [tone for tone, condition in tone_signals.items() if condition]
    if detected_tones:
        tags["tone"] = detected_tones[:2]  # Max 2 tone tags
    
    # Infer entity
    entity_signals = {
        "vrijen": ["vrijen", "v at careerspan", "my", "i am"],
        "careerspan": ["careerspan", "career span"],
        "n5": ["n5", "n5 os", "operating system"],
        "zo": ["zo computer", "zo.computer"]
    }
    
    detected_entities = []
    for entity, keywords in entity_signals.items():
        if any(kw in combined for kw in keywords):
            detected_entities.append(entity)
    
    if detected_entities:
        tags["entity"] = detected_entities
    
    return item_type, tags


def cmd_quick_add(args) -> int:
    """Quick-add a file or text with auto-categorization."""
    lib = ContentLibrary(args.file)
    
    # Get content
    content = ""
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(json.dumps({"error": f"File not found: {args.input_file}"}))
            return 1
        content = input_path.read_text()
        if not args.title:
            args.title = input_path.stem.replace("_", " ").replace("-", " ").title()
    elif args.text:
        content = args.text
        if not args.title:
            # Generate title from first 5 words
            args.title = " ".join(content.split()[:5]) + "..."
    else:
        print(json.dumps({"error": "Must provide --input-file or --text"}))
        return 1
    
    # Auto-classify
    item_type, auto_tags = classify_content(content, args.title)
    
    # Merge with user tags
    if args.tags:
        user_tags = parse_tag_args(args.tags)
        for key, values in user_tags.items():
            if key in auto_tags:
                auto_tags[key] = list(set(auto_tags[key] + values))
            else:
                auto_tags[key] = values
    
    # Generate ID if not provided
    if not args.id:
        args.id = args.title.lower().replace(" ", "_").replace("'", "").replace('"', "")[:50]
    
    # Extract URL if link type
    url = None
    if item_type == "link":
        # Content is the URL for links
        url = content.strip()
    
    # Create item
    item = Item(
        id=args.id,
        type=item_type,
        title=args.title,
        content=content if item_type == "snippet" else url,
        url=url,
        tags=auto_tags,
        metadata={
            "created": now_iso(),
            "updated": now_iso(),
            "deprecated": False,
            "expires_at": None,
            "version": 1,
            "last_used": None,
            "notes": args.notes or "",
            "source": "quick-add"
        }
    )
    
    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "item": asdict(item),
            "auto_detected": {
                "type": item_type,
                "tags": auto_tags
            }
        }, indent=2, ensure_ascii=False))
        return 0
    
    lib.upsert(item)
    logger.info(f"✓ Added {item_type}: {args.title} (id: {args.id})")
    print(json.dumps(asdict(item), indent=2, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Content Library (Links + Snippets)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # quick-add
    p_quick = subparsers.add_parser("quick-add", help="Quick-add file or text with auto-categorization")
    p_quick.add_argument("--input-file", type=str, help="Path to file to add")
    p_quick.add_argument("--text", type=str, help="Direct text input")
    p_quick.add_argument("--title", type=str, help="Title (auto-generated if not provided)")
    p_quick.add_argument("--id", type=str, help="Item ID (auto-generated if not provided)")
    p_quick.add_argument("--tags", type=str, help="Additional tags: key=val,key=val2")
    p_quick.add_argument("--notes", type=str, help="Optional notes")
    p_quick.add_argument("--dry-run", action="store_true", help="Preview without saving")
    p_quick.add_argument("--file", type=str, default="/home/workspace/N5/prefs/communication/content-library.json")
    
    # Common fields
    parser.add_argument("--id", dest="id")
    parser.add_argument("--type", dest="type")
    parser.add_argument("--title", dest="title")
    parser.add_argument("--content", dest="content")
    parser.add_argument("--url", dest="url")
    parser.add_argument("--tag", dest="tags", action="append")
    parser.add_argument("--query", dest="query")
    parser.add_argument("--expires-at", dest="expires_at")

    args = parser.parse_args()
    lib = ContentLibrary(path=Path(args.file))

    if args.command == "init":
        lib.save()
        print(str(lib.path))
        return 0

    if args.command == "migrate-from-essential":
        n = lib.migrate_from_essential()
        print(json.dumps({"migrated": n, "file": str(lib.path)}))
        return 0

    if args.command == "add":
        if not args.id:
            # derive id from title
            safe = (args.title or "untitled").lower().strip().replace(" ", "_")
            safe = "".join(ch for ch in safe if ch.isalnum() or ch in ("_", "-"))
            item_id = safe
        else:
            item_id = args.id
        tags = parse_tag_args(args.tags)
        item = Item(
            id=item_id,
            type=args.type or "snippet",
            title=args.title or item_id,
            content=args.content,
            url=args.url,
            tags=tags,
        )
        lib.upsert(item)
        print(json.dumps(asdict(item), ensure_ascii=False))
        return 0

    if args.command == "search":
        tags = parse_tag_args(args.tags)
        results = [asdict(i) for i in lib.search(args.query, tags)]
        print(json.dumps({"count": len(results), "items": results}, ensure_ascii=False))
        return 0

    if args.command == "deprecate":
        if not args.id:
            print("--id required", file=sys.stderr)
            return 1
        ok = lib.deprecate(args.id, args.expires_at)
        print(json.dumps({"id": args.id, "deprecated": ok}))
        return 0

    if args.command == "update":
        if not args.id:
            print("--id required", file=sys.stderr)
            return 1
        item = lib.get(args.id)
        if not item:
            print(json.dumps({"error": "not_found", "id": args.id}))
            return 1
        changed = False
        if args.title:
            item.title = args.title; changed = True
        if args.content:
            item.content = args.content; changed = True
        if args.url:
            item.url = args.url; changed = True
        if args.tags:
            item.tags = parse_tag_args(args.tags); changed = True
        if changed:
            item.metadata["updated"] = now_iso()
            item.metadata["version"] = int(item.metadata.get("version", 1)) + 1
            lib.upsert(item)
        print(json.dumps(asdict(item), ensure_ascii=False))
        return 0

    if args.command == "quick-add":
        return cmd_quick_add(args)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
