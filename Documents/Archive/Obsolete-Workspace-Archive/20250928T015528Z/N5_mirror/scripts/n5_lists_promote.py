#!/usr/bin/env python3
import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone

# Import safety layer
from n5_safety import execute_with_safety, load_command_spec

ROOT = Path(__file__).resolve().parents[1]
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"
SCRIPTS_DIR = ROOT / "scripts"
KNOWLEDGE_DIR = ROOT / "knowledge"
FACTS_FILE = KNOWLEDGE_DIR / "facts.jsonl"

def read_jsonl(p: Path):
    items = []
    if not p.exists():
        return items
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            ln = line.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSON on line {i} of {p}: {e}")
    return items

def write_jsonl(p: Path, items):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, separators=(',', ':')) + '\n')

def create_knowledge_links(slug: str, title: str, now: str):
    """Create cross-links to knowledge base for promoted list."""
    facts = read_jsonl(FACTS_FILE)
    
    # Create a fact about the promoted list
    fact_id = f"list_{slug}_promoted"
    fact = {
        "id": fact_id,
        "subject": slug,
        "predicate": "is_promoted",
        "object": "true",
        "source": "lists_promote",
        "confidence": 1.0,
        "tags": ["list", "promoted"],
        "created_at": now,
        "updated_at": now
    }
    
    # Check if fact already exists
    existing_fact = next((f for f in facts if f.get("id") == fact_id), None)
    if not existing_fact:
        facts.append(fact)
        write_jsonl(FACTS_FILE, facts)
        print(f"Created knowledge fact: {fact_id}")
    else:
        print(f"Knowledge fact already exists: {fact_id}")

def main():
    parser = argparse.ArgumentParser(description="Promote an N5 list (requires approval).")
    parser.add_argument("list", help="List slug")
    parser.add_argument("--approve", action="store_true", help="Approve promotion")
    parser.add_argument("--dry-run", action="store_true", help="Dry run")
    args = parser.parse_args()

    # Load command spec for safety checks
    command_spec = load_command_spec("lists-promote")

    def execute_lists_promote(args):
        if not args.approve:
            print("Promotion requires explicit approval. Use --approve to proceed.")
            sys.exit(1)

        slug = args.list.strip()

        registry = read_jsonl(INDEX_FILE)
        reg_item = next((r for r in registry if r.get("slug") == slug), None)
        if not reg_item:
            raise SystemExit(f"List '{slug}' not found in registry")

        if reg_item.get("promoted"):
            print(f"List '{slug}' is already promoted.")
            return

        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        md_file = LISTS_DIR / f"{slug}.md"

        # Ensure files exist
        if not jsonl_file.exists():
            jsonl_file.touch()
        if not md_file.exists():
            md_file.write_text(f"# {reg_item['title']}\n\n<!-- Generated MD view -->\n\n", encoding="utf-8")

        now = datetime.now(timezone.utc).isoformat()

        # Create knowledge links
        create_knowledge_links(slug, reg_item['title'], now)

        reg_item["promoted"] = True
        reg_item["promoted_at"] = now
        reg_item["updated_at"] = now

        if not args.dry_run:
            write_jsonl(INDEX_FILE, registry)
            # Run docgen to update MD
            import subprocess
            result = subprocess.run([sys.executable, str(SCRIPTS_DIR / "n5_lists_docgen.py"), "--list", slug],
                                    capture_output=True, text=True, cwd=ROOT)
            if result.returncode != 0:
                print("Docgen failed:", result.stderr)
                sys.exit(1)
            print(f"Promoted list '{slug}'")
            print(f"Registry: {INDEX_FILE}")
            print(f"JSONL: {jsonl_file}")
            print(f"MD: {md_file}")
        else:
            print("Dry run: would promote list")
            print(json.dumps(reg_item, indent=2))

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_lists_promote)
    return result

if __name__ == "__main__":
    main()