#!/usr/bin/env python3
"""
Jobboard Link Scanner - Creates short.io links for new Careerspan job postings.

Usage:
    python3 N5/scripts/jobboard_scan.py [--dry-run] [--force-id <notion_page_id>]

Options:
    --dry-run       Show what would be created without actually creating links
    --force-id ID   Force processing of a specific Notion page ID (even if already tracked)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = Path("/home/workspace/N5/data")
TRACKING_FILE = DATA_DIR / "jobboard_links.jsonl"

# Notion database ID
NOTION_DATABASE_ID = "29c5c3d6-a5db-81a3-9aa6-000b1c83fa24"

# Location abbreviations for slugs
LOCATION_ABBREV = {
    "nyc": "nyc",
    "new york": "nyc",
    "san francisco": "sf",
    "boston": "boston",
    "london": "london",
    "los angeles": "la",
    "continental usa": "usa",
    "worldwide": "remote",
    "emea": "emea",
    "latm": "latm",
    "cape town": "capetown",
}

# Hiring type prefixes for slugs
HIRING_TYPE_PREFIX = {
    "full-time": "jb",
    "part-time": "pt",
    "contract": "jb",      # Treat contract as job
    "internship": "it",
    "talent call": "tc",
}

def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    # Remove special characters, keep alphanumeric and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

def get_location_slug(locations: list) -> str:
    """Get abbreviated location for slug, or empty if ambiguous/missing."""
    if not locations:
        return ""
    # Use first location
    loc = locations[0].lower()
    for key, abbrev in LOCATION_ABBREV.items():
        if key in loc:
            return abbrev
    # Fallback: slugify the location
    return slugify(locations[0])

def load_tracked_ids() -> set:
    """Load already-tracked Notion page IDs from tracking file."""
    tracked = set()
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    tracked.add(record.get("notion_page_id", ""))
    return tracked

def load_existing_slugs() -> set:
    """Load existing slugs to check for collisions."""
    slugs = set()
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    slugs.add(record.get("slug", ""))
    return slugs

def query_notion_database() -> list:
    """Query Notion database via zo's pipedream integration using a subprocess."""
    # We'll use a helper script that calls the Notion API
    # For now, we'll read from a cached file or make the API call inline
    
    # Actually, we need to call the Notion API. Let's do this via a Python approach
    # that mimics what the Zo tools do, but since we can't directly call use_app_notion
    # from a script, we'll need to either:
    # 1. Cache the data from the conversation
    # 2. Use the Notion API directly with our own token
    
    # For this implementation, we'll assume the script is called from Zo context
    # and we pass the data via stdin or a temp file
    
    # Check for cached data file
    cache_file = DATA_DIR / "jobboard_cache.json"
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    print("ERROR: No cached Notion data found. Run this script from Zo context first.")
    print(f"       Expected cache file: {cache_file}")
    sys.exit(1)

def generate_unique_slug(base_prefix: str, company: str, role: str, locations: list, existing_slugs: set) -> str:
    """Generate a unique slug, handling collisions."""
    company_slug = slugify(company)
    role_slug = slugify(role)
    location_slug = get_location_slug(locations)
    
    # Try without location first
    slug = f"{base_prefix}-{company_slug}-{role_slug}"
    if slug not in existing_slugs:
        return slug
    
    # Add location
    if location_slug:
        slug = f"{base_prefix}-{company_slug}-{role_slug}-{location_slug}"
        if slug not in existing_slugs:
            return slug
    
    # Add number suffix
    counter = 2
    base_slug = slug if location_slug else f"{base_prefix}-{company_slug}-{role_slug}"
    while True:
        numbered_slug = f"{base_slug}-{counter}"
        if numbered_slug not in existing_slugs:
            return numbered_slug
        counter += 1
        if counter > 100:  # Safety limit
            raise ValueError(f"Could not generate unique slug for {company} - {role}")

def create_shortio_link(slug: str, destination_url: str, dry_run: bool = False) -> dict:
    """Create a short.io link using the existing service."""
    if dry_run:
        return {
            "short_url": f"https://careerspan.short.gy/{slug}",
            "slug": slug,
            "dry_run": True
        }
    
    # Call the shortio_link_service.py script
    cmd = [
        "python3",
        str(SCRIPT_DIR / "shortio_link_service.py"),
        "create",
        "--url", destination_url,
        "--path", slug,
        "--domain", "careerspan.short.gy"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR creating link: {result.stderr}")
        return None
    
    # Parse the output to get the short URL
    output = result.stdout.strip()
    
    # Check for success indicators in the output
    if "success" in output.lower() and "true" in output.lower():
        return {
            "short_url": f"https://careerspan.short.gy/{slug}",
            "slug": slug,
            "success": True
        }
    
    if "Created:" in output or "already exists" in output.lower():
        return {
            "short_url": f"https://careerspan.short.gy/{slug}",
            "slug": slug,
            "success": True
        }
    
    # Try to parse as JSON to check for success
    try:
        data = json.loads(output)
        if data.get("success") or data.get("shortURL"):
            return {
                "short_url": data.get("shortURL", f"https://careerspan.short.gy/{slug}"),
                "slug": slug,
                "success": True
            }
    except json.JSONDecodeError:
        pass
    
    return {"error": output, "slug": slug}

def append_tracking_record(record: dict):
    """Append a record to the tracking file."""
    with open(TRACKING_FILE, 'a') as f:
        f.write(json.dumps(record) + "\n")

def extract_job_data(page: dict) -> dict:
    """Extract relevant fields from a Notion page object."""
    props = page.get("properties", {})
    
    # Extract title (Name field)
    name_prop = props.get("Name", {}).get("title", [])
    title = "".join([t.get("plain_text", "") for t in name_prop]).strip()
    
    # Extract company
    company_prop = props.get("Company", {}).get("select")
    company = company_prop.get("name", "") if company_prop else ""
    
    # Extract job title (role)
    job_title_prop = props.get("Job title", {}).get("select")
    job_title = job_title_prop.get("name", "") if job_title_prop else ""
    
    # If no separate job title, try to extract from the Name field
    if not job_title and "@" in title:
        job_title = title.split("@")[0].strip()
    elif not job_title:
        job_title = title
    
    # Extract locations (multi-select)
    location_prop = props.get("Location", {}).get("multi_select", [])
    locations = [loc.get("name", "") for loc in location_prop]
    
    # Extract hiring type
    hiring_type_prop = props.get("Hiring Type", {}).get("select")
    hiring_type = hiring_type_prop.get("name", "Full-time") if hiring_type_prop else "Full-time"
    
    # Notion URLs
    notion_url = page.get("public_url") or page.get("url", "")
    
    return {
        "notion_page_id": page.get("id", ""),
        "title": title,
        "company": company,
        "job_title": job_title,
        "locations": locations,
        "hiring_type": hiring_type,
        "notion_url": notion_url,
    }

def main():
    parser = argparse.ArgumentParser(description="Create short.io links for Careerspan job postings")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating")
    parser.add_argument("--force-id", type=str, help="Force processing of a specific Notion page ID")
    args = parser.parse_args()
    
    print("=" * 60)
    print("JOBBOARD LINK SCANNER")
    print("=" * 60)
    
    # Load existing data
    tracked_ids = load_tracked_ids()
    existing_slugs = load_existing_slugs()
    print(f"Tracked jobs: {len(tracked_ids)}")
    print(f"Existing slugs: {len(existing_slugs)}")
    
    # Load Notion data from cache
    jobs_data = query_notion_database()
    print(f"Jobs in Notion: {len(jobs_data)}")
    
    # Find new jobs (or forced job)
    new_jobs = []
    for page in jobs_data:
        page_id = page.get("id", "")
        # Normalize ID format (remove hyphens for comparison)
        page_id_normalized = page_id.replace("-", "")
        tracked_normalized = {tid.replace("-", "") for tid in tracked_ids}
        
        if args.force_id:
            force_id_normalized = args.force_id.replace("-", "")
            if page_id_normalized == force_id_normalized:
                new_jobs.append(page)
                break
        elif page_id_normalized not in tracked_normalized:
            new_jobs.append(page)
    
    if not new_jobs:
        print("\n✓ No new jobs to process.")
        return
    
    print(f"\nNew jobs to process: {len(new_jobs)}")
    print("-" * 60)
    
    created_links = []
    
    for page in new_jobs:
        job = extract_job_data(page)
        
        # Determine prefix based on hiring type
        hiring_type_lower = job["hiring_type"].lower()
        prefix = HIRING_TYPE_PREFIX.get(hiring_type_lower, "jb")  # Default to jb if unknown
        
        # Generate unique slug
        try:
            slug = generate_unique_slug(
                prefix,
                job["company"],
                job["job_title"],
                job["locations"],
                existing_slugs
            )
        except ValueError as e:
            print(f"ERROR: {e}")
            continue
        
        # Add to existing slugs to prevent collisions in this batch
        existing_slugs.add(slug)
        
        print(f"\n📋 {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Role: {job['job_title']}")
        print(f"   Location: {', '.join(job['locations']) if job['locations'] else 'Not specified'}")
        print(f"   Hiring Type: {job['hiring_type']}")
        print(f"   Slug: {slug}")
        print(f"   → https://careerspan.short.gy/{slug}")
        
        if args.dry_run:
            print("   [DRY RUN - not created]")
            created_links.append({"slug": slug, "dry_run": True})
        else:
            # Create the short.io link
            result = create_shortio_link(slug, job["notion_url"], dry_run=False)
            
            if result and result.get("success"):
                print(f"   ✓ Created!")
                
                # Record to tracking file
                record = {
                    "notion_page_id": job["notion_page_id"],
                    "title": job["title"],
                    "company": job["company"],
                    "job_title": job["job_title"],
                    "locations": job["locations"],
                    "hiring_type": job["hiring_type"],
                    "slug": slug,
                    "short_url": result["short_url"],
                    "notion_url": job["notion_url"],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                append_tracking_record(record)
                created_links.append(record)
            else:
                print(f"   ✗ Failed: {result}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if args.dry_run:
        print(f"Would create {len(created_links)} links (dry run)")
    else:
        print(f"Created {len(created_links)} links")
    
    for link in created_links:
        print(f"  • {link.get('slug')}: https://careerspan.short.gy/{link.get('slug')}")

if __name__ == "__main__":
    main()




