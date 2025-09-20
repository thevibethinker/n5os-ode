#!/usr/bin/env python3
"""
Job Description Enrichment Script
Takes job URLs and enriches them with actual job descriptions using web scraping
"""

import csv
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from bs4 import BeautifulSoup
import re

def enrich_job_description(job_url: str) -> Optional[str]:
    """Main function to enrich a job with its description"""
    print(f"Enriching job from: {job_url}")
    
    try:
        # Import and use read_webpage inside the function to avoid global scope issues
        from read_webpage import read_webpage
        webpage_result = read_webpage(job_url)
        html_content = webpage_result.text
        return extract_job_description(html_content, job_url)
    except Exception as e:
        print(f"Error enriching {job_url}: {e}")
        return None

def extract_job_description(html_content: str, url: str) -> Optional[str]:
    """Extract job description from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Look for common job description containers
        selectors = [
            'div[class*="job-description"]',
            'div[class*="description"]',
            'div[id*="job-description"]',
            'div[id*="description"]',
            'section[class*="job-details"]',
            'div[class*="job-content"]',
            'div[class*="position-description"]',
            'main',
            'article',
            '.job-details',
            '.description',
            '#job-description',
            '#description'
        ]
        
        job_content = None
        for selector in selectors:
            element = soup.select_one(selector)
            if element and len(element.get_text().strip()) > 200:  # Minimum meaningful content
                job_content = element.get_text()
                break
        
        # Fallback: if no specific container found, look for substantial text blocks
        if not job_content:
            text_blocks = soup.find_all(['div', 'section', 'article'])
            for block in text_blocks:
                text = block.get_text().strip()
                if len(text) > 500 and any(keyword in text.lower() for keyword in ['responsibilities', 'requirements', 'qualifications', 'experience']):
                    job_content = text
                    break
        
        # Final cleanup
        if job_content:
            # Clean up whitespace and line breaks
            job_content = re.sub(r'\s+', ' ', job_content)
            job_content = re.sub(r'\n\s*\n', '\n\n', job_content).strip()
            
            return job_content
        
        return job_content
        
    except Exception as e:
        print(f"Error extracting description from {url}: {e}")
        return None

def process_jobs_from_csv(csv_path: str) -> List[Dict]:
    """Process job descriptions from CSV file"""
    enriched_jobs = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            jobs = list(reader)
    
        print(f"Found {len(jobs)} jobs to process")
        
        for i, job in enumerate(jobs):
            title = job.get('Title', 'Unknown Title') or 'Unknown Title'
            print(f"Processing job {i+1}/{len(jobs)}: {title}")
            
            # Check if we need to enrich the description
            current_desc = job.get('Description', '')
            if current_desc and len(current_desc) > 100 and 'scraped' not in current_desc.lower():
                print("  -> Description already looks good, skipping")
                enriched_jobs.append(job)
                continue
            
            job_url = job.get('URL', '')
            if not job_url:
                print("  -> No URL found, skipping")
                enriched_jobs.append(job)
                continue
            
            # Try to enrich the description
            try:
                new_description = enrich_job_description(job_url)
                if new_description:
                    job['Description'] = new_description
                    print(f"  -> Successfully enriched with {len(new_description)} characters")
                else:
                    print("  -> Could not enrich description (might be behind JS/login)")
                    job['Description'] = 'Unable to fetch full description - requires JavaScript or login'
                    
            except Exception as e:
                print(f"  -> Error enriching: {e}")
                job['Description'] = f'Error fetching description: {str(e)}'
            
            enriched_jobs.append(job)
            
            # Small delay to be respectful
            time.sleep(1)
        
        return enriched_jobs
        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return []

def save_enriched_jobs_csv(jobs: List[Dict], output_path: str):
    """Save enriched jobs back to CSV"""
    if not jobs:
        print("No jobs to save")
        return
    
    # Get all fieldnames from all jobs to ensure we don't lose any fields
    fieldnames = set()
    for job in jobs:
        if job:  # Check if job is not None
            fieldnames.update(job.keys())
    fieldnames = sorted([str(name) for name in fieldnames if name is not None])
    
    # Write to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            if job:  # Only write non-None jobs
                writer.writerow(job)
    
    print(f"Saved {len(jobs)} enriched jobs to {output_path}")

if __name__ == "__main__":
    # Process the jobs_export.csv file
    input_file = "/home/workspace/jobs_export.csv"
    output_file = "/home/workspace/jobs_enriched.csv"
    
    print("Starting job description enrichment process...")
    enriched_jobs = process_jobs_from_csv(input_file)
    
    if enriched_jobs:
        save_enriched_jobs_csv(enriched_jobs, output_file)
        print(f"\nProcess completed! Enriched {len(enriched_jobs)} jobs.")
    else:
        print("\nNo jobs were successfully enriched.")