#!/usr/bin/env python3
"""
N5 Lists Similarity Scanner: Analyzes lists and suggests potential merges based on similarity.
"""

import json
import itertools
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
LISTS_DIR = ROOT / "lists"
INDEX_FILE = LISTS_DIR / "index.jsonl"

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
                print(f"Warning: Invalid JSON on line {i} of {p}: {e}")
    return items

def jaccard_similarity(set1, set2):
    """Calculates Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def title_similarity(title1, title2):
    """Calculates a simple word-based similarity for titles."""
    words1 = set(title1.lower().split())
    words2 = set(title2.lower().split())
    return jaccard_similarity(words1, words2)

def calculate_similarity(list1, list2_content, list2_tags):
    """Calculates an overall similarity score between two lists."""
    # Tag similarity (weighted high)
    tag_sim = jaccard_similarity(set(list1.get('tags', [])), set(list2_tags))

    # Title similarity
    title_sim = title_similarity(list1.get('title', ''), list2_content.get('title', ''))

    # Content similarity (simple version: compare item titles)
    list1_items = read_jsonl(ROOT / list1['path_jsonl'])
    list2_items = read_jsonl(ROOT / list2_content['path_jsonl'])
    
    list1_item_titles = {item.get('title', '') for item in list1_items}
    list2_item_titles = {item.get('title', '') for item in list2_items}

    content_sim = 0
    if list1_item_titles and list2_item_titles:
        # A simple average Jaccard similarity of item titles
        all_sims = [jaccard_similarity(set(t1.lower().split()), set(t2.lower().split())) for t1 in list1_item_titles for t2 in list2_item_titles]
        if all_sims:
            content_sim = sum(all_sims) / len(all_sims)

    # Weighted average for overall score
    score = (tag_sim * 0.5) + (title_sim * 0.3) + (content_sim * 0.2)
    return score, {'tag_similarity': tag_sim, 'title_similarity': title_sim, 'content_similarity': content_sim}

def main():
    parser = argparse.ArgumentParser(description="Scan N5 lists for merge candidates.")
    parser.add_argument("--threshold", type=float, default=0.4, help="Similarity threshold for suggesting a merge (0.0 to 1.0).")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed similarity scores.")
    args = parser.parse_args()

    registry = read_jsonl(INDEX_FILE)
    if len(registry) < 2:
        print("Not enough lists to compare.")
        return

    print(f"Scanning {len(registry)} lists for merge candidates (threshold: {args.threshold})...")
    
    suggestions = []
    
    # Use itertools.combinations to get all unique pairs of lists
    for list1, list2 in itertools.combinations(registry, 2):
        list2_tags = set(list2.get('tags', []))
        
        score, details = calculate_similarity(list1, list2, list2_tags)
        
        if score >= args.threshold:
            suggestions.append({
                'list1': list1['slug'],
                'list2': list2['slug'],
                'score': score,
                'details': details
            })

    if not suggestions:
        print("\nNo merge candidates found.")
        return

    print(f"\nFound {len(suggestions)} potential merge candidates:")
    suggestions.sort(key=lambda x: x['score'], reverse=True)

    for suggestion in suggestions:
        print("-" * 40)
        print(f"Merge Suggestion: '{suggestion['list1']}' and '{suggestion['list2']}'")
        print(f"  Similarity Score: {suggestion['score']:.2f}")
        if args.verbose:
            print(f"  Details:")
            print(f"    - Tag Similarity:     {suggestion['details']['tag_similarity']:.2f}")
            print(f"    - Title Similarity:   {suggestion['details']['title_similarity']:.2f}")
            print(f"    - Content Similarity: {suggestion['details']['content_similarity']:.2f}")

    print("\nTo merge lists, you can use the 'n5_lists_merger.py' script (once created).")

if __name__ == "__main__":
    main()
