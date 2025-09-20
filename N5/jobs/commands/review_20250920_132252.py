#!/usr/bin/env python3
"""
CLI wrapper for jobs-review command (thin adapter to Command Authoring version)
This wrapper provides backward compatibility while delegating to the new Command Authoring framework.
"""

import argparse
import sys
sys.path.append('/home/workspace')

# Import the Command Authoring version
from N5.command_authoring.jobs_review_command import jobs_review_command_entry

def main():
    """Thin adapter CLI wrapper that delegates to Command Authoring framework."""
    parser = argparse.ArgumentParser(
        description="Interactive TUI to review and approve pending jobs (Command Authoring framework)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Delegate to Command Authoring framework entry point
    try:
        result = jobs_review_command_entry(verbose=args.verbose)
        
        if not result['success']:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
        
        # Result summary is already printed by the command itself
        # Just exit cleanly
        
    except KeyboardInterrupt:
        print("\nReview interrupted by user.")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()