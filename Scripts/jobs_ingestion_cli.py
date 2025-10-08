#!/usr/bin/env python3
"""CLI wrapper for the jobs ingestion pipeline"""

import sys
import argparse
from jobs_implementation_plan_20250920_120000 import JobsIngestionPipeline

def main():
    parser = argparse.ArgumentParser(description='N5 Jobs Ingestion Pipeline')
    parser.add_argument('companies', nargs='+', help='Companies to process')
    parser.add_argument('--filters', nargs='*', help='Role filters (e.g., engineer developer)')
    parser.add_argument('--setup-only', action='store_true', help='Only setup the subsystem')
    
    args = parser.parse_args()
    
    pipeline = JobsIngestionPipeline()
    
    if args.setup_only:
        result = pipeline.setup_jobs_ingestion_subsystem()
        print(f"Setup result: {result}")
        return
    
    # Setup first
    setup_result = pipeline.setup_jobs_ingestion_subsystem()
    if setup_result['status'] != 'success':
        print(f"Setup failed: {setup_result}")
        sys.exit(1)
    
    # Process companies
    result = pipeline.process_companies_batch(args.companies, args.filters)
    print(f"Pipeline result: {result}")

if __name__ == '__main__':
    main()
