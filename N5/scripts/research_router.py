#!/usr/bin/env python3
"""
Research Router - LLM-powered routing for research artifacts.

Determines the canonical path for research artifacts by:
1. Scanning existing categories in Research/
2. Using LLM to classify the topic
3. Matching to existing category or suggesting new one
4. Returning the canonical path

Usage:
    python3 N5/scripts/research_router.py "<topic>" [--create] [--slug <slug>]
    
Examples:
    python3 N5/scripts/research_router.py "Even Realities G2 smart glasses setup guide"
    python3 N5/scripts/research_router.py "Calendly competitor analysis" --create --slug calendly-research
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
import requests

RESEARCH_ROOT = Path("/home/workspace/Research")
ZO_API_URL = "https://api.zo.computer/zo/ask"

def get_existing_categories() -> list[dict]:
    """Scan Research/ for existing category folders and their descriptions."""
    categories = []
    
    if not RESEARCH_ROOT.exists():
        return categories
    
    for item in RESEARCH_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Try to read README for description
            readme = item / "README.md"
            description = ""
            if readme.exists():
                content = readme.read_text()
                # Extract first paragraph after frontmatter
                lines = content.split('\n')
                in_frontmatter = False
                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if not in_frontmatter and line.strip() and not line.startswith('#'):
                        description = line.strip()
                        break
            
            categories.append({
                "slug": item.name,
                "path": str(item),
                "description": description or f"Research related to {item.name.replace('-', ' ')}"
            })
    
    return categories


def classify_topic(topic: str, existing_categories: list[dict]) -> dict:
    """Use LLM to classify the research topic."""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        # Fallback to simple heuristics if no token
        return fallback_classify(topic, existing_categories)
    
    categories_desc = "\n".join([
        f"- {c['slug']}: {c['description']}" 
        for c in existing_categories
    ]) or "No existing categories yet."
    
    prompt = f"""Classify this research topic into a category.

TOPIC: {topic}

EXISTING CATEGORIES:
{categories_desc}

TASK:
1. Determine if this topic fits an existing category (semantic match, not exact)
2. If yes, return that category slug
3. If no, suggest a new category slug (lowercase, hyphenated, broad enough to contain related research)

Respond with JSON only:
{{
    "matches_existing": true/false,
    "category_slug": "the-category-slug",
    "category_description": "Brief description if new category",
    "reasoning": "One sentence explaining the match/creation"
}}"""

    try:
        resp = requests.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "object",
                    "properties": {
                        "matches_existing": {"type": "boolean"},
                        "category_slug": {"type": "string"},
                        "category_description": {"type": "string"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["matches_existing", "category_slug", "reasoning"]
                }
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            return resp.json().get("output", {})
    except Exception as e:
        print(f"LLM classification failed: {e}", file=sys.stderr)
    
    return fallback_classify(topic, existing_categories)


def fallback_classify(topic: str, existing_categories: list[dict]) -> dict:
    """Simple keyword-based fallback classification."""
    topic_lower = topic.lower()
    
    # Keyword mappings
    mappings = {
        "consumer-tech": ["glasses", "ring", "device", "gadget", "hardware", "phone", "watch", "earbuds", "headphones", "smart"],
        "market-intel": ["competitor", "market", "analysis", "due diligence", "company", "startup", "industry"],
        "health": ["health", "supplement", "nutrition", "fitness", "medical", "wellness"],
        "productivity": ["workflow", "productivity", "tool", "app", "software"],
    }
    
    for category, keywords in mappings.items():
        if any(kw in topic_lower for kw in keywords):
            existing_match = next((c for c in existing_categories if c["slug"] == category), None)
            return {
                "matches_existing": existing_match is not None,
                "category_slug": category,
                "category_description": f"Research related to {category.replace('-', ' ')}",
                "reasoning": f"Matched keywords for {category}"
            }
    
    # Default to general
    return {
        "matches_existing": False,
        "category_slug": "general",
        "category_description": "General research and investigations",
        "reasoning": "No specific category match found"
    }


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')[:50]


def route_research(topic: str, create: bool = False, custom_slug: str = None) -> dict:
    """Main routing function."""
    existing = get_existing_categories()
    classification = classify_topic(topic, existing)
    
    category_slug = classification["category_slug"]
    category_path = RESEARCH_ROOT / category_slug
    
    # Generate item slug from topic if not provided
    item_slug = custom_slug or slugify(topic)
    item_path = category_path / item_slug
    
    result = {
        "topic": topic,
        "category": category_slug,
        "category_path": str(category_path),
        "item_slug": item_slug,
        "item_path": str(item_path),
        "is_new_category": not classification["matches_existing"],
        "reasoning": classification["reasoning"]
    }
    
    if create:
        # Create category if new
        if not category_path.exists():
            category_path.mkdir(parents=True)
            # Create category README
            readme_content = f"""---
created: 2026-01-27
last_edited: 2026-01-27
version: 1.0
---

# {category_slug.replace('-', ' ').title()}

{classification.get('category_description', f'Research related to {category_slug}')}
"""
            (category_path / "README.md").write_text(readme_content)
            result["created_category"] = True
        
        # Create item folder
        if not item_path.exists():
            item_path.mkdir(parents=True)
            result["created_item"] = True
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Route research artifacts to canonical paths")
    parser.add_argument("topic", help="Research topic or description")
    parser.add_argument("--create", action="store_true", help="Create directories if they don't exist")
    parser.add_argument("--slug", help="Custom slug for the research item")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    result = route_research(args.topic, create=args.create, custom_slug=args.slug)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Category: {result['category']}")
        print(f"Item path: {result['item_path']}")
        if result.get('is_new_category'):
            print(f"Note: New category (reason: {result['reasoning']})")
        if result.get('created_category'):
            print(f"✓ Created category directory")
        if result.get('created_item'):
            print(f"✓ Created item directory")


if __name__ == "__main__":
    main()
