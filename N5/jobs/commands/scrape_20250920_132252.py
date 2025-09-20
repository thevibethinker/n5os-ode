#!/usr/bin/env python3
"""
CLI wrapper for jobs-scrape command (thin adapter to Command Authoring version)
This wrapper provides backward compatibility while delegating to the new Command Authoring framework.
"""

import argparse
import json
import sys
sys.path.append('/home/workspace')

# Import the Command Authoring version
from N5.command_authoring.jobs_scrape_command import jobs_scrape_command_entry

def main():
    """Thin adapter CLI wrapper that delegates to Command Authoring framework."""
    parser = argparse.ArgumentParser(
        description="Scrape jobs from company list (Command Authoring framework)"
    )
    parser.add_argument("companies_file", help="Path to companies.txt")
    parser.add_argument("--roles", help="Comma-separated roles", default="")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Delegate to Command Authoring framework entry point
    try:
        result = jobs_scrape_command_entry(
            companies_file=args.companies_file,
            roles=args.roles,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if result['success']:
            if args.dry_run:
                print("Dry run completed:")
                print(json.dumps(result['simulation_result'], indent=2))
            else:
                print(f"Scraping completed successfully:")
                print(f"Jobs added: {result['execution_result']['jobs_added']}")
                print(f"Jobs rejected: {result['execution_result']['jobs_rejected']}")
                print(f"Companies processed: {result['execution_result']['companies_processed']}")
                if args.verbose:
                    print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()