#!/usr/bin/env python3
"""
Add opportunities to the opportunity calendar.

Usage:
    python3 N5/scripts/add-opportunity.py "Title" "Organization" "2025-12-31" "funding" "pre-seed" "high" "Description here"
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def add_opportunity(title, organization, deadline=None, opp_type="funding", stage=None,
                   priority="medium", description="", source="", source_url=""):

    # Generate ID from title
    opp_id = title.lower().replace(" ", "-").replace(",", "").replace("'", "")[:50]

    opportunity = {
        "id": opp_id,
        "title": title,
        "organization": organization,
        "type": opp_type,
        "stage": stage,
        "deadline": deadline,
        "status": "active",
        "priority": priority,
        "description": description,
        "application_method": None,
        "warm_intro_required": None,
        "careerspan_fit": "unknown",
        "source": source,
        "source_url": source_url,
        "added_date": datetime.now().isoformat() + "Z",
        "last_updated": datetime.now().isoformat() + "Z"
    }

    # Add to JSONL file
    calendar_file = Path("/home/workspace/Lists/opportunity-calendar.jsonl")
    with open(calendar_file, 'a') as f:
        f.write(json.dumps(opportunity) + '\n')

    print(f"✓ Added opportunity: {title}")
    return opportunity

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 add-opportunity.py 'Title' 'Organization' [deadline] [type] [stage] [priority] [description] [source] [source_url]")
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]
    title = args[0]
    organization = args[1]
    deadline = args[2] if len(args) > 2 else None
    opp_type = args[3] if len(args) > 3 else "funding"
    stage = args[4] if len(args) > 4 else None
    priority = args[5] if len(args) > 5 else "medium"
    description = args[6] if len(args) > 6 else ""
    source = args[7] if len(args) > 7 else ""
    source_url = args[8] if len(args) > 8 else ""

    add_opportunity(title, organization, deadline, opp_type, stage, priority, description, source, source_url)