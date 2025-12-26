#!/usr/bin/env python3
"""
N5 Content Library - Generic link and snippet management for startups
Manages reusable content (links, text snippets) with auto-classification and retrieval
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Default paths (relative to N5 root)
DEFAULT_CONFIG_PATH = "N5/config/content-library.json"
DEFAULT_LIBRARY_PATH = "Knowledge/content-library.json"


class ContentLibrary:
    """Manages content library with links and snippets"""
    
    def __init__(self, library_path: Path, config_path: Optional[Path] = None):
        self.library_path = library_path
        self.config = self._load_config(config_path) if config_path else self._default_config()
        self.library = self._load_library()
        
    def _default_config(self) -> Dict[str, Any]:
        """Returns default configuration"""
        return {
            "auto_classify": True,
            "classification_rules": {
                "purpose_signals": {
                    "bio": ["founder", "ceo", "background", "experience", "career", "about me"],
                    "education": ["guide", "how to", "learn", "tutorial", "course", "training"],
                    "scheduling": ["calendly", "meeting", "book", "schedule", "calendar"],
                    "referral": ["promo", "referral", "discount", "code", "affiliate"],
                    "product": ["feature", "product", "demo", "walkthrough", "launch"],
                    "hook": ["pitch", "hook", "opening", "intro", "value prop"],
                    "signature": ["signature", "footer", "contact", "reach me"],
                    "resource": ["article", "resource", "link", "reference", "documentation"],
                    "pitch": ["pitch deck", "investor", "fundraising", "series"],
                    "onboarding": ["onboarding", "welcome", "getting started", "new hire"],
                    "support": ["support", "help", "faq", "troubleshooting"],
                    "marketing": ["marketing", "campaign", "announcement", "press"],
                    "sales": ["sales", "proposal", "quote", "pricing"],
                    "hiring": ["job", "hiring", "position", "candidate", "interview"],
                    "fundraising": ["raise", "round", "investment", "funding"]
                },
                "audience_signals": {
                    "founders": ["founder", "startup", "entrepreneur", "building"],
                    "investors": ["investor", "fundraising", "pitch", "cap table"],
                    "customers": ["customer", "user", "client", "buyer"],
                    "candidates": ["candidate", "applicant", "hire", "job seeker"],
                    "team": ["team", "employee", "staff", "internal"],
                    "partners": ["partner", "partnership", "collaboration", "integration"],
                    "media": ["media", "press", "journalist", "reporter"],
                    "advisors": ["advisor", "mentor", "board", "consultant"]
                },
                "tone_signals": {
                    "concise": {"max_words": 50},
                    "detailed": {"min_words": 200},
                    "formal": {"keywords": ["hereby", "pursuant", "accordance", "respectfully"]},
                    "casual": {"keywords": ["hey", "cool", "awesome", "yeah", "folks"]},
                    "technical": {"keywords": ["api", "database", "architecture", "algorithm", "deployment"]},
                    "storytelling": {"keywords": ["imagine", "story", "journey", "before", "after"]},
                    "data-driven": {"keywords": ["metric", "data", "growth", "conversion", "roi"]}
                }
            },
            "search_defaults": {
                "include_deprecated": False,
                "include_expired": False,
                "max_results": 50
            }
        }
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if not config_path.exists():
                logger.warning(f"Config not found at {config_path}, using defaults")
                return self._default_config()
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _load_library(self) -> Dict[str, Any]:
        """Load library from file, creating if needed"""
        if not self.library_path.exists():
            logger.info(f"Creating new library at {self.library_path}")
            self.library_path.parent.mkdir(parents=True, exist_ok=True)
            initial = {
                "meta": {
                    "version": "1.0.0",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "format": "N5-content-library"
                },
                "items": []
            }
            self._save_library(initial)
            return initial
        
        try:
            with open(self.library_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading library: {e}", exc_info=True)
            sys.exit(1)
    
    def _save_library(self, library: Optional[Dict[str, Any]] = None) -> None:
        """Save library to file"""
        if library is None:
            library = self.library
        
        library["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        try:
            with open(self.library_path, 'w') as f:
                json.dump(library, f, indent=2)
            logger.debug(f"Saved library to {self.library_path}")
        except Exception as e:
            logger.error(f"Error saving library: {e}", exc_info=True)
            sys.exit(1)
    
    def _generate_id(self, title: str) -> str:
        """Generate URL-safe ID from title"""
        # Convert to lowercase, replace spaces/special chars with hyphens
        id_base = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        # Truncate to 50 chars
        id_base = id_base[:50]
        # Add short unique suffix
        suffix = str(uuid4())[:8]
        return f"{id_base}-{suffix}"
    
    def _classify_content(self, title: str, content: str) -> Dict[str, List[str]]:
        """Auto-classify content based on signals"""
        if not self.config.get("auto_classify", True):
            return {}
        
        text = f"{title} {content}".lower()
        tags = {}
        rules = self.config["classification_rules"]
        
        # Purpose classification
        purpose = []
        for purpose_type, signals in rules["purpose_signals"].items():
            if any(signal in text for signal in signals):
                purpose.append(purpose_type)
        if purpose:
            tags["purpose"] = purpose
        
        # Audience classification
        audience = []
        for audience_type, signals in rules["audience_signals"].items():
            if any(signal in text for signal in signals):
                audience.append(audience_type)
        if audience:
            tags["audience"] = audience
        
        # Tone classification
        tone = []
        word_count = len(content.split())
        
        for tone_type, criteria in rules["tone_signals"].items():
            if "max_words" in criteria and word_count <= criteria["max_words"]:
                tone.append(tone_type)
            elif "min_words" in criteria and word_count >= criteria["min_words"]:
                tone.append(tone_type)
            elif "keywords" in criteria:
                if any(kw in text for kw in criteria["keywords"]):
                    tone.append(tone_type)
        
        if tone:
            tags["tone"] = tone
        
        return tags
    
    def add_item(
        self,
        item_type: str,
        title: str,
        content: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[Dict[str, List[str]]] = None,
        item_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add new item to library"""
        
        # Validate
        if item_type not in ["link", "snippet"]:
            raise ValueError(f"Invalid type: {item_type}")
        
        if item_type == "link" and not url:
            raise ValueError("URL required for link items")
        
        if item_type == "snippet" and not content:
            raise ValueError("Content required for snippet items")
        
        # Generate ID if not provided
        if not item_id:
            item_id = self._generate_id(title)
        
        # Check for duplicate ID
        if any(item["id"] == item_id for item in self.library["items"]):
            raise ValueError(f"Item with id '{item_id}' already exists")
        
        # Auto-classify
        auto_tags = self._classify_content(
            title,
            content or url or ""
        )
        
        # Merge tags
        final_tags = {**auto_tags}
        if tags:
            for key, values in tags.items():
                if key in final_tags:
                    final_tags[key] = list(set(final_tags[key] + values))
                else:
                    final_tags[key] = values
        
        # Build item
        now = datetime.now(timezone.utc).isoformat()
        item = {
            "id": item_id,
            "type": item_type,
            "title": title,
            "tags": final_tags,
            "metadata": {
                "created": now,
                "updated": now,
                "deprecated": False,
                "version": 1,
                "source": "manual"
            }
        }
        
        if item_type == "link":
            item["url"] = url
            if content:
                item["content"] = content  # Optional description
        else:
            item["content"] = content
        
        if notes:
            item["metadata"]["notes"] = notes
        
        # Add to library
        self.library["items"].append(item)
        self._save_library()
        
        logger.info(f"✓ Added {item_type}: {title} (id: {item_id})")
        return item
    
    def search(
        self,
        query: Optional[str] = None,
        item_type: Optional[str] = None,
        tags: Optional[Dict[str, List[str]]] = None,
        include_deprecated: Optional[bool] = None,
        include_expired: Optional[bool] = None,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search library items"""
        
        # Apply defaults
        if include_deprecated is None:
            include_deprecated = self.config["search_defaults"]["include_deprecated"]
        if include_expired is None:
            include_expired = self.config["search_defaults"]["include_expired"]
        if max_results is None:
            max_results = self.config["search_defaults"]["max_results"]
        
        results = []
        now = datetime.now(timezone.utc)
        
        for item in self.library["items"]:
            # Filter deprecated
            if not include_deprecated and item["metadata"].get("deprecated", False):
                continue
            
            # Filter expired
            if not include_expired:
                expires = item["metadata"].get("expires_at")
                if expires:
                    exp_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                    if exp_dt < now:
                        continue
            
            # Filter by type
            if item_type and item["type"] != item_type:
                continue
            
            # Filter by tags
            if tags:
                match = True
                for tag_key, tag_values in tags.items():
                    item_tags = item.get("tags", {}).get(tag_key, [])
                    if not any(v in item_tags for v in tag_values):
                        match = False
                        break
                if not match:
                    continue
            
            # Filter by query
            if query:
                query_lower = query.lower()
                searchable = " ".join([
                    item.get("title", ""),
                    item.get("content", ""),
                    item.get("url", ""),
                    json.dumps(item.get("tags", {}))
                ]).lower()
                
                if query_lower not in searchable:
                    continue
            
            results.append(item)
            
            if len(results) >= max_results:
                break
        
        return results
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID"""
        for item in self.library["items"]:
            if item["id"] == item_id:
                # Update last_used
                item["metadata"]["last_used"] = datetime.now(timezone.utc).isoformat()
                self._save_library()
                return item
        return None
    
    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        url: Optional[str] = None,
        tags: Optional[Dict[str, List[str]]] = None,
        deprecated: Optional[bool] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update existing item"""
        
        item = self.get_item(item_id)
        if not item:
            raise ValueError(f"Item not found: {item_id}")
        
        # Update fields
        if title:
            item["title"] = title
        if content:
            item["content"] = content
        if url:
            item["url"] = url
        if tags:
            item["tags"] = tags
        if deprecated is not None:
            item["metadata"]["deprecated"] = deprecated
        if notes:
            item["metadata"]["notes"] = notes
        
        # Update metadata
        item["metadata"]["updated"] = datetime.now(timezone.utc).isoformat()
        item["metadata"]["version"] = item["metadata"].get("version", 1) + 1
        
        self._save_library()
        logger.info(f"✓ Updated {item['type']}: {item['title']} (id: {item_id})")
        return item
    
    def delete_item(self, item_id: str) -> None:
        """Delete item by ID"""
        initial_count = len(self.library["items"])
        self.library["items"] = [
            item for item in self.library["items"]
            if item["id"] != item_id
        ]
        
        if len(self.library["items"]) == initial_count:
            raise ValueError(f"Item not found: {item_id}")
        
        self._save_library()
        logger.info(f"✓ Deleted item: {item_id}")
    
    def stats(self) -> Dict[str, Any]:
        """Get library statistics"""
        items = self.library["items"]
        
        stats = {
            "total_items": len(items),
            "by_type": {},
            "deprecated": 0,
            "expired": 0,
            "by_purpose": {},
            "by_audience": {}
        }
        
        now = datetime.now(timezone.utc)
        
        for item in items:
            # Type counts
            item_type = item["type"]
            stats["by_type"][item_type] = stats["by_type"].get(item_type, 0) + 1
            
            # Deprecated count
            if item["metadata"].get("deprecated", False):
                stats["deprecated"] += 1
            
            # Expired count
            expires = item["metadata"].get("expires_at")
            if expires:
                exp_dt = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                if exp_dt < now:
                    stats["expired"] += 1
            
            # Purpose counts
            for purpose in item.get("tags", {}).get("purpose", []):
                stats["by_purpose"][purpose] = stats["by_purpose"].get(purpose, 0) + 1
            
            # Audience counts
            for audience in item.get("tags", {}).get("audience", []):
                stats["by_audience"][audience] = stats["by_audience"].get(audience, 0) + 1
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="N5 Content Library - Manage links and snippets"
    )
    parser.add_argument(
        "--library",
        type=Path,
        default=Path.home() / "workspace" / DEFAULT_LIBRARY_PATH,
        help="Path to library JSON file"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config JSON file (optional)"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add new item")
    add_parser.add_argument("type", choices=["link", "snippet"])
    add_parser.add_argument("title", help="Item title")
    add_parser.add_argument("--content", help="Content (for snippets) or description (for links)")
    add_parser.add_argument("--url", help="URL (for links)")
    add_parser.add_argument("--id", help="Custom ID (optional)")
    add_parser.add_argument("--notes", help="Notes about this item")
    add_parser.add_argument("--tags", help="Tags as JSON object")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search items")
    search_parser.add_argument("--query", help="Search query")
    search_parser.add_argument("--type", choices=["link", "snippet"], help="Filter by type")
    search_parser.add_argument("--tags", help="Filter by tags (JSON object)")
    search_parser.add_argument("--include-deprecated", action="store_true")
    search_parser.add_argument("--include-expired", action="store_true")
    search_parser.add_argument("--max", type=int, help="Max results")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get item by ID")
    get_parser.add_argument("id", help="Item ID")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update item")
    update_parser.add_argument("id", help="Item ID")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--content", help="New content")
    update_parser.add_argument("--url", help="New URL")
    update_parser.add_argument("--tags", help="New tags (JSON object)")
    update_parser.add_argument("--deprecate", action="store_true", help="Mark as deprecated")
    update_parser.add_argument("--notes", help="Update notes")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete item")
    delete_parser.add_argument("id", help="Item ID")
    
    # Stats command
    subparsers.add_parser("stats", help="Show library statistics")
    
    args = parser.parse_args()
    
    try:
        lib = ContentLibrary(args.library, args.config)
        
        if args.command == "add":
            tags = json.loads(args.tags) if args.tags else None
            item = lib.add_item(
                args.type,
                args.title,
                content=args.content,
                url=args.url,
                tags=tags,
                item_id=args.id,
                notes=args.notes
            )
            print(json.dumps(item, indent=2))
        
        elif args.command == "search":
            tags = json.loads(args.tags) if args.tags else None
            results = lib.search(
                query=args.query,
                item_type=args.type,
                tags=tags,
                include_deprecated=args.include_deprecated,
                include_expired=args.include_expired,
                max_results=args.max
            )
            print(json.dumps(results, indent=2))
            print(f"\n✓ Found {len(results)} items")
        
        elif args.command == "get":
            item = lib.get_item(args.id)
            if not item:
                print(f"✗ Item not found: {args.id}")
                return 1
            print(json.dumps(item, indent=2))
        
        elif args.command == "update":
            tags = json.loads(args.tags) if args.tags else None
            item = lib.update_item(
                args.id,
                title=args.title,
                content=args.content,
                url=args.url,
                tags=tags,
                deprecated=args.deprecate,
                notes=args.notes
            )
            print(json.dumps(item, indent=2))
        
        elif args.command == "delete":
            lib.delete_item(args.id)
        
        elif args.command == "stats":
            stats = lib.stats()
            print(json.dumps(stats, indent=2))
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
