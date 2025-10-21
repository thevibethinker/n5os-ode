#!/usr/bin/env python3
"""
N5 Command: gfetch
Intelligently search and retrieve content from Google Drive or Gmail based on query.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

def parse_args():
    parser = argparse.ArgumentParser(description="Search and retrieve from Google Drive or Gmail")
    parser.add_argument("query", help="Search query string")
    parser.add_argument("--source", choices=["drive", "gmail", "both"], default="both",
                        help="Where to search: drive, gmail, or both (default: both)")
    parser.add_argument("--limit", type=int, default=10, help="Max results to return (default: 10)")
    parser.add_argument("--output-dir", default="/home/workspace/Records/Retrieved",
                        help="Directory to save retrieved files (default: /home/workspace/Records/Retrieved)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be retrieved without downloading")
    return parser.parse_args()

def main():
    args = parse_args()
    
    logging.info(f"Starting gfetch: query='{args.query}', source={args.source}, limit={args.limit}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory: {output_dir.absolute()}")
    
    results = {
        "query": args.query,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sources_searched": [],
        "results": []
    }
    
    # Search Google Drive
    if args.source in ["drive", "both"]:
        logging.info("Searching Google Drive...")
        results["sources_searched"].append("google_drive")
        
        try:
            # NOTE: This is a placeholder that would use use_app_google_drive
            # The actual implementation requires calling the Zo tool system
            drive_results = search_google_drive(args.query, args.limit)
            results["results"].extend(drive_results)
            logging.info(f"Found {len(drive_results)} results in Google Drive")
        except Exception as e:
            logging.error(f"Error searching Google Drive: {e}")
    
    # Search Gmail
    if args.source in ["gmail", "both"]:
        logging.info("Searching Gmail...")
        results["sources_searched"].append("gmail")
        
        try:
            # NOTE: This is a placeholder that would use use_app_gmail
            # The actual implementation requires calling the Zo tool system
            gmail_results = search_gmail(args.query, args.limit)
            results["results"].extend(gmail_results)
            logging.info(f"Found {len(gmail_results)} results in Gmail")
        except Exception as e:
            logging.error(f"Error searching Gmail: {e}")
    
    # Display results
    print(f"\n=== GFETCH RESULTS ===")
    print(f"Query: {args.query}")
    print(f"Sources: {', '.join(results['sources_searched'])}")
    print(f"Total results: {len(results['results'])}\n")
    
    for i, result in enumerate(results["results"], 1):
        print(f"{i}. [{result['source']}] {result['title']}")
        if result.get('snippet'):
            print(f"   {result['snippet'][:100]}...")
        print(f"   ID: {result['id']}")
        print()
    
    if args.dry_run:
        print("[DRY RUN] No files downloaded.")
        return 0
    
    # Save results manifest
    manifest_path = output_dir / f"gfetch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(manifest_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logging.info(f"Results manifest saved to: {manifest_path.absolute()}")
    
    print(f"\n✓ Results saved to: {manifest_path.absolute()}")
    return 0

def search_google_drive(query: str, limit: int) -> list:
    """
    Search Google Drive for files matching the query.
    NOTE: This is a placeholder. The actual implementation should use:
    use_app_google_drive(tool_name="google_drive-search-files", configured_props={...})
    """
    # Placeholder implementation
    return []

def search_gmail(query: str, limit: int) -> list:
    """
    Search Gmail for messages matching the query.
    NOTE: This is a placeholder. The actual implementation should use:
    use_app_gmail(tool_name="gmail-search-messages", configured_props={...})
    """
    # Placeholder implementation
    return []

if __name__ == "__main__":
    sys.exit(main())
