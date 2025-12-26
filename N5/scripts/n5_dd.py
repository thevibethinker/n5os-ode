#!/usr/bin/env python3
"""
N5 Due Diligence Orchestrator

Purpose-driven deep research on individuals and organizations.
This script handles the mechanical parts; LLM handles synthesis.

Usage:
    # Initialize DD for an individual
    python3 n5_dd.py individual --name "Adam Alpert" --org "Pangea" --type acquisition

    # Initialize DD for an organization
    python3 n5_dd.py organization --name "Pangea" --domain "pangea.com" --type acquisition_inbound

    # Check DD status
    python3 n5_dd.py status --subject "Adam Alpert"

    # List all DDs
    python3 n5_dd.py list

    # Link DD to CRM profile
    python3 n5_dd.py link --dd-path "/path/to/DD.md" --crm-id "adam_alpert"
"""

import argparse
import json
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE = Path("/home/workspace")
DD_BASE = WORKSPACE / "Knowledge" / "market and competitor intel" / "due-diligence"
CRM_PROFILES = WORKSPACE / "N5" / "crm_v3" / "profiles"
SCHEMAS = WORKSPACE / "N5" / "schemas"

INDIVIDUAL_TYPES = ["acquisition", "investment", "partnership", "employment", "advisory", "vendor", "customer", "networking"]
ORG_TYPES = ["acquisition_inbound", "acquisition_outbound", "investment_from", "investment_into", "partnership", "vendor", "customer", "competitor_analysis"]


def slugify(name: str) -> str:
    """Convert name to filesystem-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def init_individual_dd(name: str, org: str, interaction_type: str, thesis: str = None) -> dict:
    """Initialize a DD workspace for an individual."""
    
    if interaction_type not in INDIVIDUAL_TYPES:
        logger.error(f"Invalid interaction type. Must be one of: {INDIVIDUAL_TYPES}")
        sys.exit(1)
    
    slug = slugify(name)
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Create DD directory
    dd_dir = DD_BASE / slug
    dd_dir.mkdir(parents=True, exist_ok=True)
    
    # DD file path
    dd_filename = f"DD_{name.replace(' ', '_')}_{date_str}.md"
    dd_path = dd_dir / dd_filename
    
    # Check for existing CRM profile
    crm_match = None
    for profile in CRM_PROFILES.glob("*.yaml"):
        if slug in profile.stem.lower() or name.lower().replace(' ', '_') in profile.stem.lower():
            crm_match = profile.stem
            break
    
    # Create skeleton DD file
    skeleton = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
last_edited: {datetime.now().strftime("%Y-%m-%d")}
version: 1.0
type: dd_individual
subject: {name}
organization: {org}
interaction_type: {interaction_type}
crm_profile_id: {crm_match or "TO_BE_CREATED"}
status: in_progress
---

# Due Diligence: {name}

## Thesis

**Question:** {thesis or "[TO BE DEFINED - What specific question is this DD answering?]"}

**Context:** [Why was this DD triggered?]

**Stakes:** [What's at risk if we get this wrong?]

**Interaction Type:** {interaction_type}

---

## Summary

**Recommendation:** [proceed | proceed_with_caution | caution | decline | insufficient_data]

**Confidence:** [high | medium | low]

**One-liner:** [Single sentence synthesis]

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

---

## Evidence

### Evidence FOR Proceeding
| Claim | Source | Strength | Citation |
|-------|--------|----------|----------|
| | | | |

### Evidence AGAINST Proceeding
| Claim | Source | Strength | Citation |
|-------|--------|----------|----------|
| | | | |

### Unknown / Could Not Determine
- [ ] [Important question we couldn't answer]

---

## WIIFM Analysis

### For V
**Opportunities:**
- 

**Risks:**
- 

**Leverage Points (what V brings they need):**
- 

### For Careerspan
**Opportunities:**
- 

**Risks:**
- 

**Strategic Fit:**
[How does this align with Careerspan's trajectory?]

---

## Network Intel

### Shared Connections
| Name | Relationship to Subject | Relationship to V | Usable for Reference? |
|------|------------------------|-------------------|----------------------|
| | | | |

### Reputation Signals
| Signal | Source | Sentiment |
|--------|--------|-----------|
| | | |

**Reference Check Recommended:** [Yes/No]

**Suggested References:**
- 

---

## Profile Snapshot

**Current Role:** 

**Career Trajectory:** 

**Notable Achievements:**
- 

**Red Flags:**
- 

**LinkedIn:** 

---

## Raw Sources Consulted

- [ ] Aviato
- [ ] Gmail history
- [ ] LinkedIn
- [ ] Web search: [queries used]
- [ ] News search
- [ ] Crunchbase
- [ ] Other: 

---

## Next Actions

| Action | Priority | Owner |
|--------|----------|-------|
| | | |

---

*DD initiated: {datetime.now().strftime("%Y-%m-%d %H:%M")} ET*
"""
    
    dd_path.write_text(skeleton)
    logger.info(f"Created DD skeleton: {dd_path}")
    
    result = {
        "dd_path": str(dd_path),
        "dd_dir": str(dd_dir),
        "subject": name,
        "organization": org,
        "interaction_type": interaction_type,
        "crm_profile_id": crm_match,
        "status": "skeleton_created",
        "next_steps": [
            "Define thesis question if not provided",
            "Run Aviato enrichment if not done",
            "Execute web searches per protocol",
            "Check Gmail history",
            "Identify network connections",
            "Synthesize findings with WIIFM lens",
            "Link to CRM when complete"
        ]
    }
    
    return result


def init_org_dd(name: str, domain: str, interaction_type: str, key_contact: str = None, thesis: str = None) -> dict:
    """Initialize a DD workspace for an organization."""
    
    if interaction_type not in ORG_TYPES:
        logger.error(f"Invalid interaction type. Must be one of: {ORG_TYPES}")
        sys.exit(1)
    
    slug = slugify(name)
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Create DD directory
    dd_dir = DD_BASE / slug
    dd_dir.mkdir(parents=True, exist_ok=True)
    
    # DD file path
    dd_filename = f"DD_{name.replace(' ', '_')}_{date_str}.md"
    dd_path = dd_dir / dd_filename
    
    # Create skeleton DD file
    skeleton = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
last_edited: {datetime.now().strftime("%Y-%m-%d")}
version: 1.0
type: dd_organization
organization: {name}
domain: {domain}
interaction_type: {interaction_type}
key_contact: {key_contact or ""}
status: in_progress
---

# Due Diligence: {name}

## Thesis

**Question:** {thesis or "[TO BE DEFINED - What specific question is this DD answering?]"}

**Context:** [Why was this DD triggered?]

**Stakes:** [What's at risk if we get this wrong?]

**Decision Timeline:** [When does V need to decide?]

**Interaction Type:** {interaction_type}

---

## Summary

**Recommendation:** [proceed | proceed_with_caution | caution | decline | insufficient_data]

**Confidence:** [high | medium | low]

**One-liner:** [Single sentence synthesis]

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

---

## Evidence

### Evidence FOR Proceeding
| Claim | Source | Strength | Citation |
|-------|--------|----------|----------|
| | | | |

### Evidence AGAINST Proceeding
| Claim | Source | Strength | Citation |
|-------|--------|----------|----------|
| | | | |

### Unknown / Could Not Determine
- [ ] [Important question we couldn't answer]

---

## WIIFM Analysis

### For V
**Opportunities:**
- 

**Risks:**
- 

**Leverage Points:**
- 

**Exit Scenarios (if acquisition/investment):**
- 

### For Careerspan
**Opportunities:**
- 

**Risks:**
- 

**Strategic Fit:**
[How does this align with Careerspan's trajectory?]

**Product Synergies:**
- 

**Customer Overlap:**
[Complementary or cannibalistic?]

---

## Company Intel

### Overview
| Attribute | Value |
|-----------|-------|
| Founded | |
| Headquarters | |
| Employee Count | |
| Industry | |
| Business Model | |
| Target Market | |

### Financials
| Attribute | Value |
|-----------|-------|
| Total Funding | |
| Last Round | |
| Last Round Date | |
| Key Investors | |
| Revenue Estimate | |
| Financial Health | [strong / stable / concerning / unknown] |

**Burn Rate Signals:**


### Leadership
| Name | Role | Background | Red Flags |
|------|------|------------|-----------|
| | | | |

### Product
**Core Offering:** 

**Differentiation:** 

**Tech Stack Signals:** 

**Customer Reviews:** 

### Market Position
**Competitors:**
- 

**Competitive Advantage:** 

**Recent Wins/Losses:**
- 

### Reputation
**Glassdoor Signals:** 

**Customer Sentiment:** 

**Press Coverage:**
- 

**Controversies:**
- 

---

## Network Intel

### People We Know There
| Name | Role | Relationship to V |
|------|------|-------------------|
| | | |

### Backdoor References
[People who left who could give candid intel]
- 

### Shared Connections
| Name | Role at Org | Relationship to V | Usable? |
|------|-------------|-------------------|---------|
| | | | |

---

## Raw Sources Consulted

- [ ] Aviato (company)
- [ ] Crunchbase
- [ ] LinkedIn Company
- [ ] PitchBook
- [ ] Web search: [queries]
- [ ] News search
- [ ] SEC filings
- [ ] Glassdoor
- [ ] G2/Capterra
- [ ] Other:

---

## Next Actions

| Action | Priority | Owner |
|--------|----------|-------|
| | | |

---

*DD initiated: {datetime.now().strftime("%Y-%m-%d %H:%M")} ET*
"""
    
    dd_path.write_text(skeleton)
    logger.info(f"Created DD skeleton: {dd_path}")
    
    result = {
        "dd_path": str(dd_path),
        "dd_dir": str(dd_dir),
        "organization": name,
        "domain": domain,
        "interaction_type": interaction_type,
        "key_contact": key_contact,
        "status": "skeleton_created",
        "next_steps": [
            "Define thesis question if not provided",
            "Research company overview and financials",
            "Identify and assess leadership team",
            "Analyze product and market position",
            "Check reputation signals",
            "Map network connections",
            "Synthesize with WIIFM lens",
            "Cross-link to individual DD if key contact has one"
        ]
    }
    
    return result


def list_dds() -> list:
    """List all DD reports."""
    dds = []
    
    if not DD_BASE.exists():
        return dds
    
    for dd_dir in DD_BASE.iterdir():
        if dd_dir.is_dir() and not dd_dir.name.startswith('.'):
            for dd_file in dd_dir.glob("DD_*.md"):
                # Parse frontmatter
                content = dd_file.read_text()
                fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                
                dd_info = {
                    "path": str(dd_file),
                    "subject": dd_dir.name,
                    "filename": dd_file.name,
                    "modified": datetime.fromtimestamp(dd_file.stat().st_mtime).isoformat()
                }
                
                if fm_match:
                    for line in fm_match.group(1).split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            dd_info[key.strip()] = val.strip()
                
                dds.append(dd_info)
    
    return sorted(dds, key=lambda x: x.get('modified', ''), reverse=True)


def get_dd_status(subject: str) -> dict:
    """Get status of DD for a subject."""
    slug = slugify(subject)
    dd_dir = DD_BASE / slug
    
    if not dd_dir.exists():
        return {"status": "not_found", "subject": subject}
    
    dds = list(dd_dir.glob("DD_*.md"))
    if not dds:
        return {"status": "empty_dir", "subject": subject, "path": str(dd_dir)}
    
    # Get most recent
    latest = max(dds, key=lambda x: x.stat().st_mtime)
    content = latest.read_text()
    
    # Check completion signals
    has_recommendation = "**Recommendation:**" in content and "[proceed" not in content.split("**Recommendation:**")[1][:50]
    has_evidence = "| " in content.split("## Evidence")[1] if "## Evidence" in content else False
    
    status = "complete" if has_recommendation and has_evidence else "in_progress"
    
    return {
        "status": status,
        "subject": subject,
        "path": str(latest),
        "modified": datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
    }


def link_dd_to_crm(dd_path: str, crm_id: str) -> dict:
    """Add DD link to CRM profile."""
    dd_file = Path(dd_path)
    if not dd_file.exists():
        return {"error": f"DD file not found: {dd_path}"}
    
    # Find CRM profile
    crm_file = None
    for profile in CRM_PROFILES.glob("*.yaml"):
        if crm_id.lower() in profile.stem.lower():
            crm_file = profile
            break
    
    if not crm_file:
        return {"error": f"CRM profile not found for: {crm_id}"}
    
    # Read DD to get interaction type
    dd_content = dd_file.read_text()
    interaction_type = "unknown"
    if "interaction_type:" in dd_content:
        match = re.search(r'interaction_type:\s*(\w+)', dd_content)
        if match:
            interaction_type = match.group(1)
    
    # Append DD link to CRM profile
    crm_content = crm_file.read_text()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    dd_link_section = f"""

## Due Diligence
- {date_str}: [{dd_file.name}]({dd_file.relative_to(WORKSPACE)}) - {interaction_type}
"""
    
    if "## Due Diligence" not in crm_content:
        crm_content += dd_link_section
        crm_file.write_text(crm_content)
        logger.info(f"Added DD link to CRM profile: {crm_file}")
    else:
        # Append to existing section
        lines = crm_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("## Due Diligence"):
                # Insert after the header
                insert_line = f"- {date_str}: [{dd_file.name}]({dd_file.relative_to(WORKSPACE)}) - {interaction_type}"
                lines.insert(i + 1, insert_line)
                break
        crm_file.write_text('\n'.join(lines))
        logger.info(f"Appended DD link to CRM profile: {crm_file}")
    
    return {
        "success": True,
        "crm_profile": str(crm_file),
        "dd_path": str(dd_file),
        "interaction_type": interaction_type
    }


def main():
    parser = argparse.ArgumentParser(description="N5 Due Diligence Orchestrator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Individual DD
    ind_parser = subparsers.add_parser("individual", help="Initialize DD for an individual")
    ind_parser.add_argument("--name", required=True, help="Full name of the individual")
    ind_parser.add_argument("--org", required=True, help="Their organization")
    ind_parser.add_argument("--type", required=True, choices=INDIVIDUAL_TYPES, help="Interaction type")
    ind_parser.add_argument("--thesis", help="The specific question to answer")
    
    # Organization DD
    org_parser = subparsers.add_parser("organization", help="Initialize DD for an organization")
    org_parser.add_argument("--name", required=True, help="Organization name")
    org_parser.add_argument("--domain", help="Company domain (e.g., pangea.com)")
    org_parser.add_argument("--type", required=True, choices=ORG_TYPES, help="Interaction type")
    org_parser.add_argument("--key-contact", help="Primary contact person")
    org_parser.add_argument("--thesis", help="The specific question to answer")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Check DD status")
    status_parser.add_argument("--subject", required=True, help="Subject name")
    
    # List
    subparsers.add_parser("list", help="List all DDs")
    
    # Link
    link_parser = subparsers.add_parser("link", help="Link DD to CRM profile")
    link_parser.add_argument("--dd-path", required=True, help="Path to DD file")
    link_parser.add_argument("--crm-id", required=True, help="CRM profile ID/slug")
    
    args = parser.parse_args()
    
    if args.command == "individual":
        result = init_individual_dd(args.name, args.org, args.type, args.thesis)
    elif args.command == "organization":
        result = init_org_dd(args.name, args.domain or "", args.type, args.key_contact, args.thesis)
    elif args.command == "status":
        result = get_dd_status(args.subject)
    elif args.command == "list":
        result = list_dds()
    elif args.command == "link":
        result = link_dd_to_crm(args.dd_path, args.crm_id)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

