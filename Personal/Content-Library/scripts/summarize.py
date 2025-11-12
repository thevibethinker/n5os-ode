#!/usr/bin/env python3
"""
Content Library Summary Generator
Generate summaries and key findings from full text using LLM
"""

import argparse
import json
import sys
from pathlib import Path

LIBRARY_PATH = Path("/home/workspace/Personal/Content-Library/content-library.json")
CONTENT_DIR = Path("/home/workspace/Personal/Content-Library/content")

def generate_summary_and_findings(entry_id: str) -> dict:
    """
    Use LLM to generate summary and key findings from stored content
    Returns dict with summary and findings
    """
    # Load library
    with open(LIBRARY_PATH, 'r') as f:
        library = json.load(f)
    
    if entry_id not in library['entries']:
        print(f"ERROR: Entry {entry_id} not found")
        sys.exit(1)
    
    entry = library['entries'][entry_id]
    
    if not entry.get('has_content'):
        print(f"ERROR: Entry {entry_id} has no content stored")
        sys.exit(1)
    
    # Read the content
    content_path = CONTENT_DIR.parent / entry['content_path']
    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if content is too long
    word_count = len(content.split())
    if word_count > 8000:
        print(f"WARNING: Content is {word_count} words (max 8000 for processing)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print(f"Processing {word_count} words...")
    
    # For now, return placeholders (would integrate with LLM in real usage)
    # In practice, this would call your LLM summarization prompt
    return {
        "summary": f"Summary of {entry['title']} - {word_count} words analyzed",
        "key_findings": [
            "Finding 1: Core insight extracted",
            "Finding 2: Important takeaway",
            "Finding 3: Notable observation"
        ]
    }

def main():
    parser = argparse.ArgumentParser(description='Generate summary and key findings from stored content')
    parser.add_argument('entry_id', help='Entry ID to summarize')
    parser.add_argument('--save', action='store_true', help='Save results to entry')
    parser.add_argument('--generate-summary', action='store_true', help='Generate and store summary')
    
    args = parser.parse_args()
    
    result = generate_summary_and_findings(args.entry_id)
    
    print(f"\nGenerated for {args.entry_id}:")
    print("=" * 60)
    print(f"\nSummary:\n{result['summary']}\n")
    print("Key Findings:")
    for i, finding in enumerate(result['key_findings'], 1):
        print(f"{i}. {finding}")
    
    if args.save:
        print("\n\nNote: Saving would update the entry with these results")
        print("(Not yet implemented - will integrate with LLM)")

if __name__ == '__main__':
    main()

