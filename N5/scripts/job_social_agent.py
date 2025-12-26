#!/usr/bin/env python3
"""
Jobboard Social Agent
Scans for new jobs in N5/data/jobboard_links.jsonl and generates social media blurbs.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
import requests

# Config
LINKS_FILE = Path("/home/workspace/N5/data/jobboard_links.jsonl")
PROCESSED_FILE = Path("/home/workspace/N5/data/social_agent_processed.json")
STATE_FILE = PROCESSED_FILE
OUTPUT_DIR = Path("/home/workspace/Drafts/Social/Jobs")
DIGEST_FILE = OUTPUT_DIR / "new_jobs_digest.md"

def load_processed_ids():
    if not STATE_FILE.exists():
        return set()
    try:
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_processed_id(page_id):
    ids = load_processed_ids()
    ids.add(page_id)
    with open(STATE_FILE, 'w') as f:
        json.dump(list(ids), f)

def get_all_jobs():
    jobs = []
    if not LINKS_FILE.exists():
        return []
    with open(LINKS_FILE, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    jobs.append(json.loads(line))
                except:
                    pass
    return jobs

def get_category(job_title):
    t = job_title.lower()
    if 'product' in t or 'pm' in t: return 'Product'
    if 'engineer' in t or 'developer' in t or 'swe' in t: return 'Engineering'
    if 'design' in t or 'ux' in t: return 'Design'
    if 'sales' in t or 'account' in t or 'ae' in t: return 'Sales'
    if 'marketing' in t or 'growth' in t: return 'Marketing'
    if 'ops' in t or 'operations' in t: return 'Operations'
    return 'General'

def count_related_roles(category, all_jobs):
    # Count ACTIVE roles in this category (simplified: assume all in jsonl are potentially active/recent enough for the "multiplier" claim)
    # In a real system we'd check "status", but here we'll just count recent ones or all. 
    # Let's count all for now as a proxy for "roles on the board".
    return sum(1 for j in all_jobs if get_category(j.get('job_title', j.get('title', ''))) == category)

def get_blurb_for_job(job, count_in_category=1):
    """
    Calls Zo/Ask to generate a modular, high-agency Discord blurb.
    """
    company = job.get('company', 'Unknown Company')
    title = job.get('job_title', 'Unknown Role')
    short_url = job.get('short_url', '')
    category = job.get('category', 'Technology')
    
    # Calculate multiplier math
    # Careerspan math: 1 app = 30m (2 stories). N apps = 30m. 
    # Savings = (N-1) * 30m? Or per your logic: "spend no additional time personalizing".
    avg_time = 30 / count_in_category if count_in_category > 0 else 30
    
    prompt = f"""
    Generate a high-agency, modular Discord blurb for the following job:
    Role: {title}
    Company: {company}
    Link: {short_url}
    
    Context:
    - Careerspan replaces cover letters with "two stories" (30 mins total).
    - There are {count_in_category} total roles in this category currently on the board.
    - Applying to all {count_in_category} takes the same 30 mins.
    - Average time per application now = {avg_time:.1f} minutes.
    
    Structure:
    1. Modular Header: "## [{title} @ {company}]" (So I can delete the block easily)
    2. The "Alpha": 1-2 sentences of due diligence on why this company matters.
    3. The Call to Action: Link + the "two stories" framework.
    4. The Math: Mention the {avg_time:.1f} min/app efficiency.
    
    Tone: Warm, punchy, anti-corporate, high-signal. Use exactly this style.
    """
    
    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json={"input": prompt}
    )
    return response.json().get("output", "Error generating blurb.")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    links = get_all_jobs()
    processed_ids = load_processed_ids()
    
    new_jobs = [j for j in links if j.get('notion_page_id') not in processed_ids]
    
    if not new_jobs:
        print("No new jobs to process.")
        return

    # Sort by category for modular grouping
    new_jobs.sort(key=lambda x: get_category(x.get('job_title', x.get('title', ''))))
    
    email_body = "# 🚀 New Careerspan Jobs Digest\n\n"
    email_body += "Hey! Here are the new roles added to the board. This post is modular—you can delete any block and the rest will still flow.\n\n"
    
    for job in new_jobs:
        # Check how many of this category are on the board total for the multiplier math
        cat = get_category(job.get('job_title', job.get('title', '')))
        cat_count = count_related_roles(cat, links)
        
        blurb = get_blurb_for_job(job, count_in_category=cat_count)
        email_body += blurb + "\n\n---\n\n"
        save_processed_id(job.get('notion_page_id'))

    # Final Email send
    requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": os.environ["ZO_CLIENT_IDENTITY_TOKEN"],
            "content-type": "application/json"
        },
        json={
            "input": f"Send an email to V with the following subject and body. \nSubject: 🚀 New Careerspan Jobs Digest\nBody: {email_body}"
        }
    )
    
    print(f"Processed {len(new_jobs)} jobs and sent email.")

if __name__ == "__main__":
    main()



