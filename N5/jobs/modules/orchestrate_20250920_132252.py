#!/usr/bin/env python3
"""
Orchestrator Module
Coordinates the full scrape flow: detect → scrape → dedup → filter → enrich → save
Output: {"new_jobs": int, "rejected": int, "errors": []}
"""

import json
from typing import Dict, List
from .ats_detector import detect_ats
from .ats_scraper import scrape_jobs
from .dedup import deduplicate
from .bs_filter import filter_job
from .description_enricher import enrich_description
from .list_writer import append_job

def scrape_flow(companies: List[str], role_filters: List[str], target_list: str) -> Dict:
    """
    Full orchestration for company list scraping.
    """
    all_new_jobs = []
    rejected_count = 0
    errors = []
    
    for company in companies:
        try:
            ats_info = detect_ats(company)
            if not ats_info:
                errors.append(f"No ATS found for {company}")
                continue
            
            raw_jobs = scrape_jobs(ats_info['careers_url'], role_filters)
            # Dedup early
            deduped = deduplicate(raw_jobs, f"/home/workspace/N5/jobs/lists/{target_list}.jsonl")
            
            for job in deduped:
                filter_result = filter_job(job)
                if filter_result['verdict'] == 'pass':
                    desc = enrich_description(job['url'])
                    job['description'] = desc
                    append_job(job, target_list)
                    all_new_jobs.append(job)
                else:
                    rejected_count += 1
        
        except Exception as e:
            errors.append(f"Error with {company}: {str(e)}")
    
    # Placeholder: SMS digest
    return {"new_jobs": len(all_new_jobs), "rejected": rejected_count, "errors": errors}

if __name__ == "__main__":
    # Smoke test
    result = scrape_flow(["stripe"], ["backend"], "jobs-scraped")
    print(json.dumps(result))