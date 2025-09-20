#!/usr/bin/env python3
"""
Jobs Scrape Command
Thin CLI wrapper invoking the ScrapeWorkflow class.
Supports dry-run and detailed logging.
"""

import argparse
import sys
import json
from N5.jobs.workflows.scrape_workflow import ScrapeWorkflow


def main():
    parser = argparse.ArgumentParser(description="Scrape jobs from companies using ATS detection and fallback scraping.")
    parser.add_argument('companies_file', help='Path to text file containing company names')
    parser.add_argument('--roles', help='Comma-separated product role filters', default='')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without saving data')

    args = parser.parse_args()

    workflow = ScrapeWorkflow()

    validation = workflow.validate_inputs(args.companies_file, args.roles.split(",") if args.roles else [])
    if not validation['valid']:
        print("Input validation failed:")
        for err in validation['errors']:
            print(f"- {err}")
        sys.exit(1)

    companies = validation['companies']
    roles = validation['role_filters']

    if args.dry_run:
        sim = workflow.simulate_execution(companies, roles)
        print(f"Dry run simulation:")
        print(json.dumps(sim, indent=2))
        return

    result = workflow.execute_scraping(companies, roles, target_list="jobs-scraped")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
