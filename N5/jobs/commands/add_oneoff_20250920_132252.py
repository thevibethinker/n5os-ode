#!/usr/bin/env python3
"""
CLI wrapper for jobs-add command (thin adapter to Command Authoring version)
This wrapper provides backward compatibility while delegating to the new Command Authoring framework.
"""

import argparse
import json
import sys
sys.path.append('/home/workspace')

# Import the Command Authoring version
from N5.command_authoring.jobs_add_command import jobs_add_command_entry

def main():
    """Thin adapter CLI wrapper that delegates to Command Authoring framework."""
    parser = argparse.ArgumentParser(
        description="Add one-off job to private list (Command Authoring framework)"
    )
    parser.add_argument("job_string", help="Title@Company [location] [salary]")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Delegate to Command Authoring framework entry point
    try:
        result = jobs_add_command_entry(
            job_string=args.job_string,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        if result['success']:
            if args.dry_run:
                print("Dry run - would add job:")
                print(json.dumps(result['job_record'], indent=2))
                
                if result.get('validation_result', {}).get('warnings'):
                    print("\nWarnings:")
                    for warning in result['validation_result']['warnings']:
                        print(f"  - {warning}")
            else:
                print("Job added successfully:")
                job = result['job_record']
                print(f"  Title: {job['title']}")
                print(f"  Company: {job['company']}")
                if job.get('location'):
                    print(f"  Location: {job['location']}")
                if job.get('salary'):
                    print(f"  Salary: {job['salary']}")
                print(f"  UID: {job['uid']}")
                
                if args.verbose:
                    print("\nFull result:")
                    print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            if result.get('validation_result', {}).get('errors'):
                print("Validation errors:", file=sys.stderr)
                for error in result['validation_result']['errors']:
                    print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()