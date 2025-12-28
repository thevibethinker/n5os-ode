#!/usr/bin/env python3
"""
Acquisition Discovery Scanner - Semantic analysis to find NEW acquisition opportunities.

Unlike the entity matcher, this scanner:
1. Reads B01 content from meetings
2. Uses keyword + structural signals to identify potential acquisition/partnership conversations
3. Extracts the ORGANIZATION being discussed (not pre-configured)
4. Flags meetings where Careerspan is exploring strategic relationships

This is discovery, not confirmation.
"""

import argparse
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

MEETINGS_DIR = Path("/home/workspace/Personal/Meetings")

# Signals that suggest a strategic/acquisition conversation (not just any meeting)
STRATEGIC_SIGNALS = {
    # Direct acquisition language
    "acquisition": 3,
    "acquire": 3,
    "acqui-hire": 4,
    "buying": 2,
    "purchase": 2,
    "merger": 4,
    
    # Partnership/integration language
    "partnership": 2,
    "strategic partner": 3,
    "integration": 2,
    "integrate with": 2,
    "white-label": 3,
    "reseller": 2,
    "channel partner": 3,
    
    # Deal-making language
    "term sheet": 4,
    "due diligence": 4,
    "valuation": 3,
    "equity": 2,
    "deal structure": 4,
    "revenue share": 3,
    "licensing": 2,
    
    # Relationship exploration
    "synergy": 2,
    "complementary": 2,
    "mutual benefit": 2,
    "joint venture": 3,
    "collaboration": 1,
    
    # Careerspan-specific context
    "careerspan": 1,
    "job board": 1,
    "applicant tracking": 2,
    "recruiting": 1,
    "talent acquisition": 2,
    "hr tech": 2,
}

# Signals that this is likely internal/not a discovery
INTERNAL_SIGNALS = [
    "standup",
    "sprint",
    "retro",
    "1:1 with",
    "team sync",
    "internal",
    "mycareerspan.com",  # Internal team meetings
]

# Already tracked entities (to mark as "known" vs "new")
KNOWN_ENTITIES = ["ribbon", "futurefit", "teamwork online", "teamworkonline"]


def get_week_folders(weeks_back: int = 4) -> List[Path]:
    """Get week folders to scan."""
    week_folders = sorted(MEETINGS_DIR.glob("Week-of-*"))
    if weeks_back:
        cutoff = datetime.now() - timedelta(weeks=weeks_back)
        filtered = []
        for wf in week_folders:
            try:
                date_str = wf.name.replace("Week-of-", "")
                week_date = datetime.strptime(date_str, "%Y-%m-%d")
                if week_date >= cutoff:
                    filtered.append(wf)
            except ValueError:
                continue
        return filtered
    return week_folders


def read_b01_content(meeting_path: Path) -> Optional[str]:
    """Read B01 detailed recap content."""
    b01_files = list(meeting_path.glob("B01*.md"))
    if not b01_files:
        return None
    
    content = b01_files[0].read_text(encoding="utf-8", errors="ignore")
    
    # Strip YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    return content


def is_internal_meeting(content: str, folder_name: str) -> bool:
    """Check if this looks like an internal team meeting."""
    combined = (content + " " + folder_name).lower()
    
    for signal in INTERNAL_SIGNALS:
        if signal in combined:
            return True
    
    # Check for patterns like "Ilya-Logan" (internal 1:1s)
    if re.search(r"(ilya|logan|rochel|vrijen).*mycareerspan", combined):
        return True
    
    return False


def calculate_strategic_score(content: str) -> Tuple[int, List[str]]:
    """Calculate strategic relevance score and return matched signals."""
    content_lower = content.lower()
    score = 0
    matched = []
    
    for signal, weight in STRATEGIC_SIGNALS.items():
        if signal in content_lower:
            score += weight
            matched.append(signal)
    
    return score, matched


def extract_organization_mentions(content: str) -> List[str]:
    """Extract potential organization names from content.
    
    Looks for patterns like:
    - "meeting with [Company]"
    - "[Company] is a..."
    - "their product/platform"
    - Title Case names that might be companies
    """
    orgs = set()
    
    # Pattern: "with [Company Name]" or "from [Company Name]"
    with_pattern = re.findall(r"(?:with|from|at)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", content)
    orgs.update(with_pattern)
    
    # Pattern: "[Name] is a [type] company/platform/startup"
    is_a_pattern = re.findall(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+is\s+a\s+(?:\w+\s+)?(?:company|platform|startup|tool|solution)", content)
    orgs.update(is_a_pattern)
    
    # Filter out common non-org words
    stopwords = {"The", "This", "That", "They", "Their", "There", "What", "When", "Where", "Which", 
                 "Vrijen", "Ilya", "Logan", "Rochel", "Careerspan", "Monday", "Tuesday", "Wednesday",
                 "Thursday", "Friday", "Saturday", "Sunday", "January", "February", "March", "April",
                 "May", "June", "July", "August", "September", "October", "November", "December"}
    
    orgs = {o for o in orgs if o not in stopwords and len(o) > 2}
    
    return list(orgs)


def is_known_entity(content: str) -> bool:
    """Check if this meeting involves a known/tracked entity."""
    content_lower = content.lower()
    for entity in KNOWN_ENTITIES:
        if entity in content_lower:
            return True
    return False


def scan_meeting(meeting_path: Path) -> Optional[Dict[str, Any]]:
    """Scan a single meeting for strategic/acquisition signals."""
    folder_name = meeting_path.name
    
    # Extract date
    date_match = re.match(r"(\d{4}-\d{2}-\d{2})", folder_name)
    meeting_date = date_match.group(1) if date_match else "unknown"
    
    # Read B01 content
    content = read_b01_content(meeting_path)
    if not content:
        return None
    
    # Skip internal meetings
    if is_internal_meeting(content, folder_name):
        return None
    
    # Calculate strategic score
    score, signals = calculate_strategic_score(content)
    
    # Threshold: need at least score of 4 to be considered
    if score < 4:
        return None
    
    # Extract organization mentions
    orgs = extract_organization_mentions(content)
    
    # Check if this involves known entities
    known = is_known_entity(content)
    
    return {
        "folder": folder_name,
        "date": meeting_date,
        "path": str(meeting_path),
        "strategic_score": score,
        "signals": signals,
        "potential_orgs": orgs[:5],  # Top 5 potential org names
        "involves_known_entity": known,
        "discovery_type": "KNOWN" if known else "NEW",
        "content_preview": content[:500] + "..." if len(content) > 500 else content,
    }


def main():
    parser = argparse.ArgumentParser(description="Discover acquisition opportunities semantically")
    parser.add_argument("--weeks", type=int, default=4, help="Weeks back to scan")
    parser.add_argument("--min-score", type=int, default=4, help="Minimum strategic score")
    parser.add_argument("--show-known", action="store_true", help="Also show known entity matches")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    week_folders = get_week_folders(args.weeks)
    logger.info(f"Scanning {len(week_folders)} week folders...")
    
    discoveries = []
    known_matches = []
    
    for week_folder in week_folders:
        for meeting_path in week_folder.iterdir():
            if not meeting_path.is_dir():
                continue
            
            result = scan_meeting(meeting_path)
            if result and result["strategic_score"] >= args.min_score:
                if result["involves_known_entity"]:
                    known_matches.append(result)
                else:
                    discoveries.append(result)
    
    # Sort by score descending
    discoveries.sort(key=lambda x: x["strategic_score"], reverse=True)
    known_matches.sort(key=lambda x: x["strategic_score"], reverse=True)
    
    if args.json:
        print(json.dumps({
            "new_discoveries": discoveries,
            "known_entity_matches": known_matches if args.show_known else [],
            "summary": {
                "new_opportunities": len(discoveries),
                "known_matches": len(known_matches),
                "weeks_scanned": args.weeks,
            }
        }, indent=2))
    else:
        print("\n" + "="*70)
        print("🔍 ACQUISITION DISCOVERY SCAN")
        print("="*70)
        
        print(f"\n🆕 NEW OPPORTUNITIES (not in tracked entities): {len(discoveries)}")
        print("-"*70)
        
        if discoveries:
            for d in discoveries[:15]:  # Show top 15
                print(f"\n  [{d['date']}] {d['folder']}")
                print(f"      Score: {d['strategic_score']} | Signals: {', '.join(d['signals'][:5])}")
                if d['potential_orgs']:
                    print(f"      Potential orgs: {', '.join(d['potential_orgs'])}")
        else:
            print("  No new discoveries found.")
        
        if args.show_known:
            print(f"\n📌 KNOWN ENTITY MATCHES: {len(known_matches)}")
            print("-"*70)
            for k in known_matches[:10]:
                print(f"\n  [{k['date']}] {k['folder']}")
                print(f"      Score: {k['strategic_score']} | Signals: {', '.join(k['signals'][:5])}")
        
        print(f"\n{'='*70}")
        print(f"Summary: {len(discoveries)} new opportunities, {len(known_matches)} known entity matches")
        print(f"Scanned: {args.weeks} weeks of meetings")
        print("="*70)


if __name__ == "__main__":
    main()

