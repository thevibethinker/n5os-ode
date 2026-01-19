#!/usr/bin/env python3
"""
Meeting Deal Intel — Worker 2 (Meeting Integration)

Purpose:
- Detect when a meeting involves a deal-related contact
- Generate B37_DEAL_INTEL.md block with extracted intelligence
- Update deals.db with meeting activity
- Queue Notion sync

CLI:
  python3 meeting_deal_intel.py --meeting-folder <path> [--dry-run]
  python3 meeting_deal_intel.py --scan-recent 10 [--dry-run]

Integrates with:
- deal_signal_router.py (Worker 1) for matching and extraction
- deal_meeting_router.py for B36 → B37 flow
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Broker detection
try:
    from broker_detector import detect_brokers, format_broker_section_md, BrokerCandidate, enrich_from_b_blocks
    BROKER_DETECTION_AVAILABLE = True
except ImportError:
    BROKER_DETECTION_AVAILABLE = False

# Import from Worker 1
try:
    from deal_signal_router import DealSignalRouter, DealMatch, SignalExtraction
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from deal_signal_router import DealSignalRouter, DealMatch, SignalExtraction

DB_PATH = "/home/workspace/N5/data/deals.db"
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")


@dataclass
class DealIntel:
    """Structured deal intelligence extracted from meeting."""
    deal_id: str
    deal_type: str  # leadership, broker, acquirer, zo_partnership
    company: str
    pipeline: str  # careerspan or zo
    
    # Meeting context
    meeting_date: str
    meeting_folder: str
    attendees: List[str] = field(default_factory=list)
    meeting_type: str = ""
    
    # Signal analysis
    stage_before: Optional[str] = None
    stage_after: Optional[str] = None
    stage_confidence: int = 0
    
    # Extracted intel by source block
    strategic_intel: List[str] = field(default_factory=list)  # from B01
    stakeholder_intel: List[str] = field(default_factory=list)  # from B03/B08
    risks_opportunities: List[str] = field(default_factory=list)  # from B13
    next_steps: List[str] = field(default_factory=list)  # from B25
    
    # Synthesized
    key_facts: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    urgency: str = "normal"
    
    # Raw signal data
    raw_signal: Optional[Dict[str, Any]] = None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_manifest(meeting_folder: Path) -> Dict:
    """Load meeting manifest.json."""
    manifest_path = meeting_folder / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {}


def load_block(meeting_folder: Path, block_prefix: str) -> Optional[str]:
    """Load a B-block file content by prefix (e.g., 'B01', 'B03')."""
    for f in meeting_folder.glob(f"{block_prefix}*.md"):
        with open(f) as fh:
            return fh.read()
    return None


def extract_attendees_from_manifest(manifest: Dict) -> List[str]:
    """Extract attendee names from manifest."""
    attendees = []
    # Try different manifest formats
    if "attendees" in manifest:
        attendees = manifest["attendees"]
    elif "participants" in manifest:
        attendees = manifest["participants"]
    return [a if isinstance(a, str) else a.get("name", "") for a in attendees]


def extract_attendees_from_b03(b03_content: str) -> List[str]:
    """Extract attendee names from B03 stakeholder block."""
    attendees = []
    # Look for ## Name patterns
    matches = re.findall(r'^## ([A-Z][a-zA-Z\s\-]+?)(?:\n|\s*\*\*)', b03_content, re.MULTILINE)
    for m in matches:
        name = m.strip()
        if name and name not in ["Profile", "Key", "Communication", "Leverage", "Skepticism", "Relationship"]:
            attendees.append(name)
    return attendees


def extract_meeting_date(meeting_folder: Path, manifest: Dict) -> str:
    """Extract meeting date from folder name or manifest."""
    # Try manifest first
    if "meeting_date" in manifest:
        return manifest["meeting_date"]
    if "generated_at" in manifest:
        return manifest["generated_at"][:10]
    
    # Parse from folder name (e.g., 2026-01-16_Tope-Awotona-x-Vrijen)
    folder_name = meeting_folder.name
    match = re.match(r"(\d{4}-\d{2}-\d{2})", folder_name)
    if match:
        return match.group(1)
    
    return datetime.now().strftime("%Y-%m-%d")


def detect_deal_meeting(meeting_folder: Path, router: DealSignalRouter) -> Optional[Tuple[DealMatch, Dict]]:
    """
    Check if meeting involves a deal-related contact.
    
    Returns (DealMatch, deal_record) if found, None otherwise.
    """
    manifest = load_manifest(meeting_folder)
    
    # Gather search texts from multiple sources
    search_texts = []
    
    # 1. Meeting title/folder name
    title = manifest.get("title", meeting_folder.name)
    search_texts.append(title)
    
    # 2. Attendees from manifest
    attendees = extract_attendees_from_manifest(manifest)
    search_texts.extend(attendees)
    
    # 3. Attendees from B03
    b03 = load_block(meeting_folder, "B03")
    if b03:
        b03_attendees = extract_attendees_from_b03(b03)
        search_texts.extend(b03_attendees)
    
    # 4. Companies mentioned in B01 (first 2000 chars)
    b01 = load_block(meeting_folder, "B01")
    if b01:
        # Extract company-like patterns
        company_matches = re.findall(r'\*\*(?:Company|Role):\*\*\s*([^,\n]+)', b01[:2000])
        search_texts.extend(company_matches)
    
    # Dedupe and try matching each search text
    seen = set()
    best_match: Optional[Tuple[DealMatch, Dict]] = None
    best_confidence = 0
    
    for text in search_texts:
        text = text.strip()
        if not text or text.lower() in seen:
            continue
        seen.add(text.lower())
        
        # match_deal handles both deal and contact matching internally
        match = router.match_deal(query=text, context="")
        if match.deal_id and match.confidence > best_confidence:
            deal = router.get_deal(match.deal_id)
            if deal:
                best_match = (match, deal)
                best_confidence = match.confidence
    
    # Return best match if confidence is high enough
    if best_match and best_confidence >= 70:
        return best_match
    
    return None


def extract_strategic_intel(b01_content: str, deal: Dict) -> List[str]:
    """Extract strategic intelligence from B01 recap."""
    intel = []
    company = deal.get("company", "").lower()
    
    # Look for key themes, decisions, or commitments
    lines = b01_content.split("\n")
    in_relevant_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Track sections
        if line.startswith("## ") or line.startswith("### "):
            in_relevant_section = any(kw in line_lower for kw in 
                ["theme", "key", "decision", "action", "next", "summary", "outcome", "commitment"])
        
        # Extract bullet points with deal-relevant content
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet = line.strip()[2:].strip()
            # Prioritize lines mentioning the company or containing key signals
            if (company and company in line_lower) or in_relevant_section:
                if len(bullet) > 20 and len(bullet) < 300:
                    intel.append(bullet)
    
    return intel[:5]  # Top 5


def extract_stakeholder_intel(b03_content: str, deal: Dict) -> List[str]:
    """Extract stakeholder mapping from B03/B08."""
    intel = []
    
    # Look for role/interest/leverage patterns
    patterns = [
        r'\*\*Role:\*\*\s*([^\n]+)',
        r'\*\*Key Interests[^:]*:\*\*([^\n]+)',
        r'- \*\*([^*]+)\*\*:\s*([^\n]+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, b03_content, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                text = f"{m[0]}: {m[1]}"
            else:
                text = m
            text = text.strip()
            if len(text) > 10 and len(text) < 200:
                intel.append(text)
    
    return intel[:5]


def extract_risks_opps(b13_content: str, deal: Dict) -> List[str]:
    """Extract risks and opportunities from B13."""
    intel = []
    
    lines = b13_content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            bullet = line[2:].strip()
            if len(bullet) > 15 and len(bullet) < 250:
                # Prioritize risk/opportunity keywords
                if any(kw in bullet.lower() for kw in 
                    ["risk", "opportunity", "concern", "advantage", "threat", "potential"]):
                    intel.insert(0, bullet)
                else:
                    intel.append(bullet)
    
    return intel[:4]


def extract_next_steps(b25_content: str, deal: Dict) -> List[str]:
    """Extract next steps/deliverables from B25."""
    steps = []
    
    # Look for numbered or bulleted action items
    patterns = [
        r'^\s*\d+\.\s*(.+)$',
        r'^\s*[-*]\s*(.+)$',
        r'\*\*Action:\*\*\s*(.+)',
    ]
    
    lines = b25_content.split("\n")
    for line in lines:
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                step = match.group(1).strip()
                if len(step) > 10 and len(step) < 200:
                    steps.append(step)
                break
    
    return steps[:5]


def infer_stage_change(intel: DealIntel, deal: Dict, b01_content: str) -> Tuple[Optional[str], Optional[str], int]:
    """Infer if stage changed based on meeting content."""
    current_stage = deal.get("stage")
    
    # Stage progression keywords
    stage_signals = {
        "identified": ["first contact", "discovered", "found out about"],
        "researched": ["researching", "learning about", "gathering info"],
        "outreach": ["reached out", "sent email", "made contact", "introduced"],
        "engaged": ["responded", "showed interest", "following up", "continuing discussion"],
        "qualified": ["confirmed interest", "budget approved", "decision maker", "timeline"],
        "negotiating": ["discussing terms", "proposal", "pricing", "contract", "deal terms"],
        "closed_won": ["signed", "closed", "deal done", "agreed"],
        "closed_lost": ["passed", "declined", "not interested", "went with competitor"],
    }
    
    text_lower = b01_content.lower() if b01_content else ""
    
    # Find strongest signal
    best_stage = None
    best_score = 0
    
    for stage, keywords in stage_signals.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_stage = stage
    
    if best_stage and best_score >= 2:
        confidence = min(90, 50 + best_score * 15)
        return (current_stage, best_stage, confidence)
    
    return (current_stage, None, 0)


def extract_deal_intel(meeting_folder: Path, deal_match: DealMatch, deal: Dict, router: DealSignalRouter) -> DealIntel:
    """
    Extract comprehensive deal intelligence from meeting B-blocks.
    """
    manifest = load_manifest(meeting_folder)
    
    intel = DealIntel(
        deal_id=deal["id"],
        deal_type=deal.get("deal_type", "unknown"),
        company=deal.get("company", "Unknown"),
        pipeline=deal.get("pipeline", ""),
        meeting_date=extract_meeting_date(meeting_folder, manifest),
        meeting_folder=str(meeting_folder),
        meeting_type=manifest.get("meeting_type", ""),
    )
    
    # Get attendees
    attendees = extract_attendees_from_manifest(manifest)
    b03 = load_block(meeting_folder, "B03")
    if b03:
        attendees.extend(extract_attendees_from_b03(b03))
    intel.attendees = list(set(attendees))
    
    # Extract from B01 (strategic recap)
    b01 = load_block(meeting_folder, "B01")
    if b01:
        intel.strategic_intel = extract_strategic_intel(b01, deal)
        
        # Use signal router for deeper extraction
        extraction = router.extract_signal(text=b01[:3000], deal_context=deal)
        intel.key_facts = extraction.key_facts
        intel.sentiment = extraction.sentiment
        intel.urgency = extraction.urgency
        
        if extraction.next_action:
            intel.recommended_actions.append(extraction.next_action)
        
        # Stage inference
        stage_before, stage_after, confidence = infer_stage_change(intel, deal, b01)
        intel.stage_before = stage_before
        if stage_after and stage_after != stage_before:
            intel.stage_after = stage_after
            intel.stage_confidence = confidence
    
    # Extract from B03/B08 (stakeholder)
    if b03:
        intel.stakeholder_intel = extract_stakeholder_intel(b03, deal)
    b08 = load_block(meeting_folder, "B08")
    if b08:
        intel.stakeholder_intel.extend(extract_stakeholder_intel(b08, deal))
    
    # Extract from B13 (risks/opportunities)
    b13 = load_block(meeting_folder, "B13")
    if b13:
        intel.risks_opportunities = extract_risks_opps(b13, deal)
    
    # Extract from B25 (next steps)
    b25 = load_block(meeting_folder, "B25")
    if b25:
        intel.next_steps = extract_next_steps(b25, deal)
        intel.recommended_actions.extend(intel.next_steps[:3])
    
    # Raw signal data
    intel.raw_signal = {
        "stage_change": intel.stage_after is not None,
        "sentiment": intel.sentiment,
        "urgency": intel.urgency,
        "next_action": intel.recommended_actions[0] if intel.recommended_actions else None,
        "confidence": deal_match.confidence,
        "match_reason": deal_match.match_reason,
    }
    
    return intel


def generate_b37_block(intel: DealIntel) -> str:
    """Generate B37_DEAL_INTEL.md content."""
    now = datetime.now().isoformat()
    
    md = f"""---
created: {intel.meeting_date}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: meeting_deal_intel.py
block_type: B37
deal_id: {intel.deal_id}
pipeline: {intel.pipeline}
---

# B37: Deal Intelligence — {intel.company}

## Meeting Context
- **Date:** {intel.meeting_date}
- **Attendees:** {', '.join(intel.attendees) if intel.attendees else 'Unknown'}
- **Meeting Type:** {intel.meeting_type or 'General'}
- **Deal Type:** {intel.deal_type}
- **Pipeline:** {intel.pipeline}

## Signal Analysis
- **Stage Before:** {intel.stage_before or 'Unknown'}
- **Stage After:** {intel.stage_after or intel.stage_before or 'No change detected'}
- **Confidence:** {intel.stage_confidence}%
- **Sentiment:** {intel.sentiment}
- **Urgency:** {intel.urgency}

## Key Intelligence Extracted
"""

    if intel.strategic_intel:
        md += "\n### From B01 (Strategic Recap)\n"
        for item in intel.strategic_intel[:5]:
            md += f"- {item}\n"
    
    if intel.stakeholder_intel:
        md += "\n### From B03/B08 (Stakeholder Intel)\n"
        for item in intel.stakeholder_intel[:5]:
            md += f"- {item}\n"
    
    if intel.risks_opportunities:
        md += "\n### From B13 (Risks & Opportunities)\n"
        for item in intel.risks_opportunities[:4]:
            md += f"- {item}\n"
    
    if intel.key_facts:
        md += "\n### Key Facts\n"
        for fact in intel.key_facts[:5]:
            md += f"- {fact}\n"
    
    if intel.recommended_actions:
        md += "\n## Recommended Actions\n"
        for i, action in enumerate(intel.recommended_actions[:5], 1):
            md += f"{i}. {action}\n"
    
    # Broker detection (new feature)
    broker_section = ""
    if BROKER_DETECTION_AVAILABLE:
        try:
            # Load transcript for broker detection
            meeting_path = Path(intel.meeting_folder)
            transcript_path = meeting_path / "transcript.md"
            if transcript_path.exists():
                transcript = transcript_path.read_text()
                broker_candidates = detect_brokers(
                    transcript=transcript,
                    attendees=intel.attendees,
                    meeting_folder=meeting_path.name
                )
                if broker_candidates:
                    # Enrich from B-blocks
                    enriched = [enrich_from_b_blocks(c, meeting_path) for c in broker_candidates]
                    broker_section = format_broker_section_md(enriched)
        except Exception as e:
            broker_section = f"\n<!-- Broker detection error: {e} -->\n"
    
    if broker_section:
        md += broker_section
    
    # Raw signal JSON
    md += f"""
## Raw Signal Data
```json
{json.dumps(intel.raw_signal, indent=2)}
```
"""
    
    return md


def write_b37_block(meeting_folder: Path, intel: DealIntel, dry_run: bool = False) -> Path:
    """Write B37 block to meeting folder."""
    content = generate_b37_block(intel)
    output_path = meeting_folder / "B37_DEAL_INTEL.md"
    
    if dry_run:
        print(f"[DRY-RUN] Would write {output_path}")
        print("--- Content Preview ---")
        print(content[:1500] + "..." if len(content) > 1500 else content)
        return output_path
    
    with open(output_path, "w") as f:
        f.write(content)
    
    print(f"✓ Wrote {output_path}")
    return output_path


def update_db_from_meeting(intel: DealIntel, dry_run: bool = False) -> None:
    """Update deals.db with meeting activity."""
    if dry_run:
        print(f"[DRY-RUN] Would log meeting activity for {intel.deal_id}")
        if intel.stage_after:
            print(f"[DRY-RUN] Would update stage: {intel.stage_before} → {intel.stage_after}")
        return
    
    conn = get_db()
    c = conn.cursor()
    
    # Log activity - use actual schema columns
    description = f"Meeting: {Path(intel.meeting_folder).name}"
    if intel.key_facts:
        description += f" | Key: {intel.key_facts[0][:100]}" if intel.key_facts else ""
    
    c.execute("""
        INSERT INTO deal_activities (
            deal_id, activity_type, description, channel, outcome, meeting_path, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        intel.deal_id,
        "meeting",
        description,
        "in_person",  # channel
        intel.sentiment,  # outcome
        intel.meeting_folder,
        datetime.now().isoformat()
    ))
    
    # Update deal stage if changed
    if intel.stage_after and intel.stage_after != intel.stage_before:
        c.execute("""
            UPDATE deals SET stage = ?, last_touched = ? WHERE id = ?
        """, (intel.stage_after, datetime.now().isoformat(), intel.deal_id))
        print(f"✓ Updated stage: {intel.stage_before} → {intel.stage_after}")
    
    # Update last_touched
    c.execute("""
        UPDATE deals SET last_touched = ? WHERE id = ?
    """, (datetime.now().isoformat(), intel.deal_id))
    
    conn.commit()
    conn.close()
    print(f"✓ Logged meeting activity for {intel.deal_id}")


def queue_notion_sync(intel: DealIntel, dry_run: bool = False) -> None:
    """Queue deal for Notion sync (Worker 3 handles actual sync)."""
    if dry_run:
        print(f"[DRY-RUN] Would queue Notion sync for {intel.deal_id}")
        return
    
    # Write to notion_outbox table for Worker 3 to pick up
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        INSERT OR REPLACE INTO notion_outbox (
            deal_id, intel_type, intel_json, created_at, synced
        ) VALUES (?, ?, ?, ?, 0)
    """, (
        intel.deal_id,
        "meeting_intel",
        json.dumps(asdict(intel)),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    print(f"✓ Queued Notion sync for {intel.deal_id}")


def process_meeting(meeting_folder: Path, router: DealSignalRouter, dry_run: bool = False) -> Optional[DealIntel]:
    """
    Process a single meeting folder for deal intelligence.
    
    Returns DealIntel if deal-related, None otherwise.
    """
    print(f"\nProcessing: {meeting_folder.name}")
    
    # Check if already processed
    b37_path = meeting_folder / "B37_DEAL_INTEL.md"
    if b37_path.exists() and not dry_run:
        print(f"  ⏭ Already has B37, skipping")
        return None
    
    # Detect if deal-related
    result = detect_deal_meeting(meeting_folder, router)
    if not result:
        print(f"  ⏭ Not deal-related")
        return None
    
    deal_match, deal = result
    print(f"  ✓ Matched: {deal['company']} ({deal['deal_type']}) — confidence: {deal_match.confidence}%")
    
    # Extract intelligence
    intel = extract_deal_intel(meeting_folder, deal_match, deal, router)
    
    # Generate B37
    write_b37_block(meeting_folder, intel, dry_run)
    
    # Update database
    update_db_from_meeting(intel, dry_run)
    
    # Queue Notion sync
    try:
        queue_notion_sync(intel, dry_run)
    except sqlite3.OperationalError as e:
        # notion_outbox table might not exist yet
        print(f"  ⚠ Could not queue Notion sync: {e}")
    
    return intel


def find_recent_meetings(limit: int = 10) -> List[Path]:
    """Find recent meeting folders."""
    meetings = []
    
    for week_dir in sorted(MEETINGS_ROOT.glob("Week-of-*"), reverse=True):
        for meeting_dir in sorted(week_dir.iterdir(), reverse=True):
            if not meeting_dir.is_dir():
                continue
            
            # Must have transcript or recap
            has_content = (
                (meeting_dir / "transcript.md").exists() or
                (meeting_dir / "B01_DETAILED_RECAP.md").exists()
            )
            if has_content:
                meetings.append(meeting_dir)
            
            if len(meetings) >= limit:
                return meetings
    
    return meetings


def main():
    parser = argparse.ArgumentParser(description="Extract deal intelligence from meetings")
    parser.add_argument("--meeting-folder", type=str, help="Process specific meeting folder")
    parser.add_argument("--scan-recent", type=int, default=0, help="Scan N most recent meetings")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    
    router = DealSignalRouter()
    
    if args.meeting_folder:
        folder = Path(args.meeting_folder)
        if not folder.exists():
            # Try to find in Meetings root
            for week_dir in MEETINGS_ROOT.glob("Week-of-*"):
                candidate = week_dir / args.meeting_folder
                if candidate.exists():
                    folder = candidate
                    break
        
        if not folder.exists():
            print(f"Error: Meeting folder not found: {args.meeting_folder}")
            return 1
        
        intel = process_meeting(folder, router, args.dry_run)
        if intel:
            print(f"\n✓ Generated B37 for {intel.company}")
        return 0
    
    elif args.scan_recent > 0:
        meetings = find_recent_meetings(args.scan_recent)
        print(f"Found {len(meetings)} recent meetings")
        
        processed = 0
        for meeting_folder in meetings:
            intel = process_meeting(meeting_folder, router, args.dry_run)
            if intel:
                processed += 1
        
        print(f"\n✓ Processed {processed}/{len(meetings)} deal-related meetings")
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
