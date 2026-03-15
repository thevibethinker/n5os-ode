#!/usr/bin/env python3
"""
List Utilities: Process text input and automatically categorize into appropriate lists.
Supports quick text/SMS input with smart categorization and diagnostic questions when uncertain.
"""

import json, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
import uuid
import re
from typing import List, Tuple, Optional

try:
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"


# --- Built-in tag extraction and classification ---

def extract_tags(text: str) -> List[str]:
    """Extract hashtag-style tags from text."""
    return re.findall(r'#(\w+)', text)


def classify_list(text: str, available_slugs: List[str]) -> Tuple[str, str]:
    """
    Simple keyword-based classifier to assign text to a list slug.
    Returns (slug, rationale).
    """
    text_lower = text.lower()

    keyword_map = {
        'tasks': ['todo', 'task', 'need to', 'should', 'must', 'deadline', 'due'],
        'todos': ['todo', 'task', 'need to', 'should', 'must'],
        'reading': ['read', 'article', 'book', 'blog', 'paper', 'http', 'https'],
        'ideas': ['idea', 'what if', 'maybe', 'concept', 'brainstorm'],
        'projects': ['project', 'build', 'create', 'develop', 'implement'],
        'contacts': ['contact', 'meet', 'person', 'introduce', 'connect with'],
        'notes': ['note', 'remember', 'memo', 'jot'],
        'shopping': ['buy', 'purchase', 'order', 'shop', 'need'],
        'social': ['post', 'tweet', 'share', 'social', 'content'],
    }

    best_slug = None
    best_score = 0

    for slug in available_slugs:
        keywords = keyword_map.get(slug, [slug.replace('-', ' ')])
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_slug = slug

    if best_slug and best_score > 0:
        return best_slug, f"Keyword match detected for '{best_slug}' (score: {best_score})"

    return available_slugs[0], f"No clear match; defaulting to '{available_slugs[0]}'"


# --- Core utilities ---

def load_schema(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


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
    temp_file = p.with_suffix('.tmp')
    try:
        with temp_file.open("w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, separators=(',', ':')) + '\n')
        temp_file.replace(p)
    except Exception as e:
        if temp_file.exists():
            temp_file.unlink()
        raise SystemExit(f"Failed to write JSONL: {e}")


def validate_item(item, schema):
    if not HAS_JSONSCHEMA:
        return
    v = Draft202012Validator(schema)
    errors = sorted(v.iter_errors(item), key=lambda e: e.path)
    if errors:
        msgs = [f"- {'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
        raise SystemExit("Schema validation failed:\n" + "\n".join(msgs))


def parse_text_input(text: str) -> List[dict]:
    """
    Parse text input and extract actionable items.
    Returns list of parsed items with title, body, and potential tags.
    """
    items = []
    text = text.strip()

    if not text:
        return items

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    if len(lines) == 1 or not any(line.startswith(('-', '*', '\u2022')) for line in lines):
        items.append({
            'title': text,
            'body': None,
            'extracted_tags': extract_tags(text)
        })
        return items

    for line in lines:
        cleaned = re.sub(r'^[-*\u2022]\s*', '', line).strip()
        if cleaned:
            items.append({
                'title': cleaned,
                'body': None,
                'extracted_tags': extract_tags(cleaned)
            })

    return items


def generate_diagnostic_questions(text: str, available_slugs: List[str]) -> List[str]:
    """
    Generate diagnostic questions when categorization is uncertain.
    Returns list of questions to help determine the correct list.
    """
    questions = []

    url_pattern = r'https?://[^\s<>"\'`(){}[\]|\\^]+'
    urls = re.findall(url_pattern, text)

    if urls and len(available_slugs) > 2:
        questions.append(f"I see a URL ({urls[0][:50]}...). Is this for:")
        if 'contacts' in available_slugs:
            questions.append("- Professional contact/networking")
        if 'reading' in available_slugs:
            questions.append("- Article/content to read later")
        if 'projects' in available_slugs:
            questions.append("- Project reference/development")
        if 'social' in available_slugs or 'social-media' in available_slugs:
            questions.append("- Social media content/idea")

    action_words = ['need', 'should', 'todo', 'remember', 'follow up', 'call', 'email']
    if any(word in text.lower() for word in action_words):
        if 'tasks' in available_slugs or 'todos' in available_slugs:
            questions.append("This sounds like a task. Should it go in your task list?")

    if not questions and len(available_slugs) > 1:
        questions.append("Which category best fits this item?")
        for slug in available_slugs[:5]:
            questions.append(f"- {slug.replace('-', ' ').title()}")

    return questions


def process_text_to_lists(text: str, interactive: bool = True, dry_run: bool = False) -> List[dict]:
    """
    Process text input and add items to appropriate lists.
    Returns list of results for each processed item.
    """
    registry = read_jsonl(INDEX_FILE)
    available_slugs = [r.get("slug") for r in registry if r.get("slug")]
    if not registry:
        raise SystemExit("No lists defined in registry")

    parsed_items = parse_text_input(text)
    if not parsed_items:
        raise SystemExit("No actionable items found in text")

    results = []

    schema = None
    schema_path = SCHEMAS / "lists.item.schema.json"
    if schema_path.exists() and HAS_JSONSCHEMA:
        schema = load_schema(schema_path)

    for i, parsed in enumerate(parsed_items):
        print(f"\n--- Item {i+1}: '{parsed['title'][:50]}...' ---")

        slug, rationale = classify_list(parsed['title'], available_slugs)
        confidence_indicators = ['detected', 'explicit', 'clear']
        is_confident = any(indicator in rationale.lower() for indicator in confidence_indicators)

        final_slug = slug
        if not is_confident and interactive:
            questions = generate_diagnostic_questions(parsed['title'], available_slugs)
            if questions:
                print("\nCategorization uncertain. Please help:")
                for q in questions:
                    print(f"  {q}")

                while True:
                    user_input = input("\nEnter list name or number (or 'auto' to use suggestion): ").strip().lower()
                    if user_input == 'auto':
                        break
                    elif user_input in available_slugs:
                        final_slug = user_input
                        rationale = f"User selected '{user_input}'"
                        break
                    elif user_input.isdigit():
                        idx = int(user_input) - 1
                        if 0 <= idx < len(available_slugs):
                            final_slug = available_slugs[idx]
                            rationale = f"User selected option {user_input}"
                            break
                    print(f"Invalid input. Available lists: {', '.join(available_slugs)}")

        print(f"Assigned list: {final_slug}")
        print(f"Rationale: {rationale}")

        reg_item = next((r for r in registry if r.get("slug") == final_slug), None)
        if not reg_item:
            raise SystemExit(f"List '{final_slug}' not found in registry")

        jsonl_file = (LISTS_DIR / f"{final_slug}.jsonl").resolve()
        items = read_jsonl(jsonl_file)

        now = datetime.now(timezone.utc).isoformat()
        item_id = str(uuid.uuid4())

        item = {
            "id": item_id,
            "created_at": now,
            "updated_at": now,
            "title": parsed['title'],
            "status": "open"
        }

        if parsed['extracted_tags']:
            item["tags"] = parsed['extracted_tags']

        if parsed.get('body'):
            item["body"] = parsed['body']

        if schema:
            validate_item(item, schema)

        items.insert(0, item)

        result = {
            'item_id': item_id,
            'list': final_slug,
            'title': parsed['title'],
            'rationale': rationale,
            'file': str(jsonl_file)
        }

        if not dry_run:
            write_jsonl(jsonl_file, items)
            print(f"Added to {final_slug}")
            print(f"  Item ID: {item_id}")
        else:
            print("Dry run: would add to list")
            print(json.dumps(item, indent=2))

        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Process text input and add to appropriate lists.",
        epilog="Examples:\n"
               "  %(prog)s 'Buy groceries #shopping'\n"
               "  %(prog)s --stdin < items.txt\n"
               "  %(prog)s --dry-run 'Read this article https://example.com'\n"
               "  %(prog)s --non-interactive 'Todo: fix the login bug'",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("text", nargs='?', help="Text to process (or use --stdin)")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Skip diagnostic questions, use automatic categorization")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be added without writing to files")
    args = parser.parse_args()

    if args.stdin:
        text = sys.stdin.read().strip()
    elif args.text:
        text = args.text
    else:
        print("Enter text to process (Ctrl+D when done):")
        text = sys.stdin.read().strip()

    if not text:
        raise SystemExit("No text provided")

    try:
        results = process_text_to_lists(
            text,
            interactive=not args.non_interactive,
            dry_run=args.dry_run
        )

        print(f"\n=== Summary ===")
        print(f"Processed {len(results)} items:")
        for result in results:
            title_preview = result['title'][:40]
            print(f"  - '{title_preview}...' -> {result['list']}")

    except KeyboardInterrupt:
        print("\n\nCanceled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
