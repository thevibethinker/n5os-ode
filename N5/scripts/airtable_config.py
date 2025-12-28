#!/usr/bin/env python3
"""
Airtable Configuration for Acquisition Deal Tracking
Central config for IDs, watched entities, and field mappings.
"""

# Airtable Base and Table IDs
AIRTABLE_BASE_ID = "appL2OJHiwBmOoU8z"

TABLES = {
    "organizations": "tbll78YaQL4SyJtFn",
    "contacts": "tbl67Zvy7bFQJwft3",
    "deals": "tblVvlBtY4QtmA7ss",
    "meeting_audit": "tbl2mFQSHP5bOIus4",
}

# Field IDs for Deals table
DEAL_FIELDS = {
    "deal_name": "fldXPfrTi5PkECaCo",
    "organization": "fld9S4B25w5KkA9CI",
    "main_contact": "fldlZK4iSzo2eiP7T",
    "status": "fldL07Wj7Zf7TBGcD",
    "intelligence_summary": "fldE4ZDZNtPgUeVBp",  # Main append-only field
    "meeting_audit_trail": "fldKiOYa0Sh4JYodV",
}

# Field IDs for Meeting Audit Trail table
AUDIT_FIELDS = {
    "meeting_id": "fldUXDoC26CymXPSB",
    "meeting_title": "fldla3trUsT4XBAHh",
    "associated_deal": "fldHYaYnE2BjCtw10",
}

# Watched Entities - companies we're tracking for acquisition deals
WATCHED_ENTITIES = [
    {
        "name": "Ribbon",
        "aliases": ["ribbon", "christine song", "christine"],
        "org_record_id": "recieutq4bTwIMu8M",
        "deal_record_id": "reciLb0wbBghPSEp5",
    },
    {
        "name": "Teamwork Online",
        "aliases": ["teamwork online", "teamworkonline", "davis"],
        "org_record_id": "recEKj9HNFKedQVuO",
        "deal_record_id": "recuhPdi3SS8lfykg",
    },
    {
        "name": "FutureFit",
        "aliases": ["futurefit", "future fit", "hamoon", "hamoon ekhtiari"],
        "org_record_id": "rec9hfRn2fRH6oOD9",
        "deal_record_id": "recOE1cKT42g0rwwE",
    },
    {
        "name": "Elly AI",
        "aliases": ["elly ai", "elly.ai", "kristen habacht", "kristen"],
        "org_record_id": "recDnijkygjpgg1ha",
        "deal_record_id": "recP8lZv6yFBFgF03",
    },
    {
        "name": "Coffee Space",
        "aliases": ["coffee space", "coffeespace"],
        "org_record_id": "recpDSdJ7cRgL9AtR",
        "deal_record_id": "rec9NZKbIrnYMGr8Z",
    },
]

# Acquisition signal keywords for semantic sensing
ACQUISITION_KEYWORDS = [
    "acquisition",
    "partnership",
    "integration",
    "merge",
    "buy",
    "acquire",
    "deal",
    "strategic fit",
    "synergy",
    "partnership opportunity",
    "strategic alignment",
    "joint venture",
    "M&A",
]

# B-Block to Intelligence mapping
BLOCK_MAPPING = {
    "B01": "strategic_recap",       # Detailed Recap -> Strategic insights
    "B08": "stakeholder_map",       # Stakeholder Intel -> Key people
    "B13": "risks_opportunities",   # Risks & Opportunities
    "B21": "key_moments",           # Key Moments -> Pivotal points
    "B25": "deliverables",          # Deliverables -> Action items
}

# Meetings directory
MEETINGS_DIR = "/home/workspace/Personal/Meetings"




