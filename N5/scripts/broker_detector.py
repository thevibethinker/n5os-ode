#!/usr/bin/env python3
"""
Broker Detector — Identifies potential deal brokers from meeting transcripts

Uses unified n5_core.db database with people table and deal_roles junction.

A broker is someone who can introduce Careerspan to acquirers/partners without
being the deal target themselves (e.g., advisors, well-connected contacts).

Signals:
- Offers to make introductions
- Has relevant network access
- Advisory role (not decision-maker for deals)
- Previous M&A experience mentioned

Usage:
    from broker_detector import detect_brokers, BrokerCandidate
    
    candidates = detect_brokers(transcript_text, attendees)
    for c in candidates:
        if c.confidence >= 0.8:
            # Auto-create broker record
        else:
            # Queue for review
"""

import re
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from db_paths import get_db_connection


@dataclass
class BrokerCandidate:
    """A potential broker identified from meeting content."""
    name: str
    confidence: float  # 0.0 to 1.0
    signals: List[str] = field(default_factory=list)
    context: str = ""  # Relevant quote or context
    relationship: str = ""  # How they relate to V/Careerspan
    network_access: List[str] = field(default_factory=list)  # Who they can intro to
    source_meeting: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "confidence": self.confidence,
            "signals": self.signals,
            "context": self.context,
            "relationship": self.relationship,
            "network_access": self.network_access,
            "source_meeting": self.source_meeting
        }


# Detection patterns with point values
BROKER_SIGNALS = {
    # High confidence signals (25-30 points each)
    "intro_offer": {
        "patterns": [
            r"send me.{0,30}(stuff|materials|deck|info)",
            r"i('ll| will| can) (intro|introduce|connect) you",
            r"i know (someone|people|folks).{0,30}(who|that|at)",
            r"let me (intro|introduce|connect|put you in touch)",
            r"i('ll| can) send (it|this|that) (to|over)",
        ],
        "points": 30,
        "label": "Offered to make introductions"
    },
    "network_mention": {
        "patterns": [
            r"i('m| am) connected to",
            r"i have (contacts|connections|relationships) (at|with)",
            r"i know (the|a) (founder|ceo|head|vp|director)",
            r"my (friend|colleague|contact) (at|who|is)",
        ],
        "points": 25,
        "label": "Mentioned network access"
    },
    "advisory_role": {
        "patterns": [
            r"(as|from) (my|an?) (advisor|mentor|coach)",
            r"i('ve| have) (sold|exited|been through)",
            r"when i sold (my|the) company",
            r"(my|the) acquisition (experience|process)",
            r"let me (share|tell you) (what|how)",
        ],
        "points": 25,
        "label": "Advisory/mentor role indicated"
    },
    
    # Medium confidence signals (15-20 points each)
    "ma_experience": {
        "patterns": [
            r"(acquisition|acqui-?hire|m&a|merger)",
            r"(due diligence|earnout|valuation)",
            r"(term sheet|loi|letter of intent)",
            r"sold.{0,20}(company|startup|business)",
        ],
        "points": 20,
        "label": "M&A experience mentioned"
    },
    "advice_giving": {
        "patterns": [
            r"(my advice|i('d| would) (suggest|recommend))",
            r"(keep in mind|be careful|watch out for)",
            r"(what (i|we) did was|how (i|we) handled)",
            r"(lesson|mistake|learning).{0,20}(learned|made|from)",
        ],
        "points": 15,
        "label": "Giving strategic advice"
    },
    "potential_lead": {
        "patterns": [
            r"there('s| is).{0,20}(another|one other|at least one)",
            r"(potential|possible).{0,20}(acquirer|buyer|interest)",
            r"(might|may|could) be interested",
        ],
        "points": 20,
        "label": "Mentioned potential leads"
    },
    
    # Lower confidence signals (10 points each)
    "relationship_indicator": {
        "patterns": [
            r"good to (see|catch up with) you",
            r"(friend|buddy|we go way back)",
            r"(helped|supported|backed) (me|us|you)",
        ],
        "points": 10,
        "label": "Pre-existing relationship"
    },
}

# Negative signals (reduce confidence) - ONLY check in "Them:" speaker content
NEGATIVE_SIGNALS = {
    "is_target": {
        "patterns": [
            r"them:\s*[^\n]*?(we|our company) (would|might|could) (acquire|buy)",
            r"them:\s*[^\n]*?(we're|we are|i'm|i am) (interested|looking) (in|to) (acquir|buy)",
        ],
        "points": -40,
        "label": "Appears to be deal target, not broker"
    },
    "internal_team": {
        "patterns": [
            r"(co-?founder|cofounder|partner) (at|of) careerspan",
        ],
        "points": -50,
        "label": "Internal team member"
    },
}


def detect_brokers(
    transcript: str,
    attendees: Optional[List[str]] = None,
    meeting_folder: str = "",
    existing_context: Optional[Dict] = None
) -> List[BrokerCandidate]:
    """
    Detect potential brokers from meeting transcript.
    
    Args:
        transcript: Full meeting transcript text
        attendees: List of attendee names (optional)
        meeting_folder: Source meeting folder name
        existing_context: Optional dict with B01/B03 context
        
    Returns:
        List of BrokerCandidate objects sorted by confidence (highest first)
    """
    candidates = []
    transcript_lower = transcript.lower()
    
    # If we have specific attendees, check each
    # Otherwise, try to extract "Them" speaker as potential broker
    speakers_to_check = []
    
    if attendees:
        # Filter out V/Vrijen
        speakers_to_check = [
            a for a in attendees 
            if a.lower() not in ("vrijen", "vrijen attawar", "v", "me")
        ]
    else:
        # Check if there's a "Them" speaker who might be broker
        if re.search(r'\bthem\s*:', transcript_lower):
            # Try to extract name from meeting folder or title
            extracted_name = "Meeting Counterpart"  # Default
            
            # Try meeting folder name (e.g., "2026-01-15_Ray-Acquisition-Debrief")
            if meeting_folder:
                folder_match = re.search(r'_([A-Z][a-z]+)[-_]', meeting_folder)
                if folder_match:
                    extracted_name = folder_match.group(1)
            
            # Try meeting title in transcript
            title_match = re.search(r'Meeting Title:\s*([^\n]+)', transcript, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                # Extract name from patterns like "from Ray" or "with Ray"
                name_match = re.search(r'(?:from|with|and)\s+([A-Z][a-z]+)', title)
                if name_match:
                    extracted_name = name_match.group(1)
            
            speakers_to_check = [extracted_name]
    
    # If no speakers identified but we have existing_context, extract from there
    if not speakers_to_check and existing_context:
        stakeholders = existing_context.get("stakeholders", [])
        speakers_to_check = [s.get("name", "") for s in stakeholders if s.get("name")]
    
    # Score the transcript overall for broker signals
    total_points = 0
    signals_found = []
    context_quotes = []
    network_hints = []
    
    for signal_name, signal_config in BROKER_SIGNALS.items():
        for pattern in signal_config["patterns"]:
            matches = list(re.finditer(pattern, transcript_lower))
            if matches:
                total_points += signal_config["points"]
                signals_found.append(signal_config["label"])
                # Capture context
                for m in matches[:2]:  # Max 2 quotes per pattern
                    start = max(0, m.start() - 50)
                    end = min(len(transcript), m.end() + 50)
                    context_quotes.append(transcript[start:end].strip())
                    
                    # Extract network hints from intro offers
                    if signal_name in ("intro_offer", "network_mention", "potential_lead"):
                        network_hints.append(m.group(0))
                break  # Only count each signal type once
    
    # Check negative signals
    for signal_name, signal_config in NEGATIVE_SIGNALS.items():
        for pattern in signal_config["patterns"]:
            if re.search(pattern, transcript_lower):
                total_points += signal_config["points"]  # Negative points
                signals_found.append(signal_config["label"])
                break
    
    # Calculate confidence (0-100 points → 0.0-1.0)
    # Max realistic positive is ~130 points
    confidence = max(0.0, min(1.0, total_points / 100.0))
    
    # Only return candidate if confidence > 0.3
    if confidence > 0.3 and speakers_to_check:
        for speaker in speakers_to_check:
            candidate = BrokerCandidate(
                name=speaker,
                confidence=round(confidence, 2),
                signals=list(set(signals_found)),  # Dedupe
                context=context_quotes[0] if context_quotes else "",
                relationship="Advisory contact",  # Default
                network_access=network_hints[:3],  # Max 3
                source_meeting=meeting_folder
            )
            candidates.append(candidate)
    
    return sorted(candidates, key=lambda x: x.confidence, reverse=True)


def enrich_from_b_blocks(
    candidate: BrokerCandidate,
    meeting_folder: Path
) -> BrokerCandidate:
    """
    Enrich broker candidate with info from existing B-blocks.
    """
    # Try to read B03 stakeholder intel
    b03_path = meeting_folder / "B03_STAKEHOLDER_INTELLIGENCE.md"
    if b03_path.exists():
        b03_content = b03_path.read_text()
        
        # Extract relationship info
        if "relationship" in b03_content.lower():
            rel_match = re.search(
                r'\*\*relationship\*\*[:\s]+([^\n]+)',
                b03_content, 
                re.IGNORECASE
            )
            if rel_match:
                candidate.relationship = rel_match.group(1).strip()
    
    # Try B01 for network mentions
    b01_path = meeting_folder / "B01_DETAILED_RECAP.md"
    if b01_path.exists():
        b01_content = b01_path.read_text()
        
        # Look for company/person mentions that could be network
        company_pattern = r'(calendly|future ?fit|hearth|[A-Z][a-z]+(?:ly|\.ai|\.io))'
        companies = re.findall(company_pattern, b01_content, re.IGNORECASE)
        if companies:
            candidate.network_access.extend(list(set(companies))[:5])
    
    return candidate


def format_broker_section_md(candidates: List[BrokerCandidate]) -> str:
    """
    Format broker candidates as markdown section for B37.
    """
    if not candidates:
        return ""
    
    lines = [
        "",
        "## 🤝 Broker Intelligence",
        ""
    ]
    
    for c in candidates:
        conf_emoji = "🟢" if c.confidence >= 0.8 else "🟡" if c.confidence >= 0.5 else "🟠"
        
        lines.append(f"### {c.name}")
        lines.append(f"- **Confidence**: {conf_emoji} {c.confidence:.0%}")
        lines.append(f"- **Relationship**: {c.relationship}")
        
        if c.signals:
            lines.append(f"- **Signals**: {', '.join(c.signals)}")
        
        if c.network_access:
            clean_network = [n for n in c.network_access if len(n) > 3]
            if clean_network:
                lines.append(f"- **Network Access**: {', '.join(clean_network[:5])}")
        
        if c.context:
            # Clean up context quote
            clean_context = c.context.replace('\n', ' ').strip()
            if len(clean_context) > 150:
                clean_context = clean_context[:147] + "..."
            lines.append(f"- **Key Quote**: \"{clean_context}\"")
        
        lines.append("")
    
    return "\n".join(lines)


def format_broker_frontmatter(candidates: List[BrokerCandidate]) -> Dict:
    """
    Format broker candidates for YAML frontmatter in B37.
    """
    if not candidates:
        return {}
    
    return {
        "brokers_detected": [
            {
                "name": c.name,
                "confidence": c.confidence,
                "signals": c.signals,
            }
            for c in candidates
        ]
    }


def persist_broker(candidate: BrokerCandidate) -> Optional[int]:
    """
    Persist broker to n5_core.db people table + deal_roles.
    
    Creates a person entry and optionally a deal_role with role='broker'.
    
    Returns:
        person_id if created, None on error
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        # Check if person already exists by name
        c.execute("""
            SELECT id FROM people 
            WHERE LOWER(full_name) = LOWER(?)
        """, (candidate.name,))
        existing = c.fetchone()
        
        if existing:
            # Update existing person's broker metadata in notes
            person_id = existing['id']
            c.execute("SELECT notes FROM people WHERE id = ?", (person_id,))
            row = c.fetchone()
            existing_notes = row['notes'] if row and row['notes'] else ""
            
            broker_note = f"\n[{now[:10]}] Broker signal (confidence: {candidate.confidence:.0%})"
            broker_note += f" from {candidate.source_meeting}" if candidate.source_meeting else ""
            broker_note += f"\nSignals: {', '.join(candidate.signals)}" if candidate.signals else ""
            
            c.execute("""
                UPDATE people 
                SET notes = ?, updated_at = ?
                WHERE id = ?
            """, (
                (existing_notes + broker_note).strip(),
                now,
                person_id
            ))
        else:
            # Insert new person
            broker_notes = f"Broker (confidence: {candidate.confidence:.0%})"
            broker_notes += f"\nSource: {candidate.source_meeting}" if candidate.source_meeting else ""
            broker_notes += f"\nSignals: {', '.join(candidate.signals)}" if candidate.signals else ""
            broker_notes += f"\nNetwork access: {', '.join(candidate.network_access)}" if candidate.network_access else ""
            broker_notes += f"\nRelationship: {candidate.relationship}" if candidate.relationship else ""
            
            c.execute("""
                INSERT INTO people (full_name, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """, (
                candidate.name,
                broker_notes,
                now,
                now
            ))
            person_id = c.lastrowid
        
        conn.commit()
        conn.close()
        return person_id
        
    except Exception as e:
        print(f"Error persisting broker: {e}")
        return None


def queue_broker_notion_sync(candidate: BrokerCandidate) -> bool:
    """
    Queue broker for Notion sync.
    
    Uses the notion_outbox table if it exists in n5_core.db.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if notion_outbox table exists
        c.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='notion_outbox'
        """)
        if not c.fetchone():
            conn.close()
            return False
        
        safe_name = candidate.name.lower().replace(' ', '_').replace('-', '_')
        safe_meeting = candidate.source_meeting[:10] if candidate.source_meeting else 'unknown'
        entity_id = f"broker_{safe_name}_{safe_meeting}"
        
        c.execute("""
            INSERT INTO notion_outbox (
                entity_type, entity_id, notion_page_id, action_type, 
                payload_json, status, created_at
            ) VALUES (?, ?, '', 'create', ?, 'pending', ?)
        """, (
            "deal_broker",
            entity_id,
            json.dumps(candidate.to_dict()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error queuing broker sync: {e}")
        return False


# CLI for testing
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: broker_detector.py <transcript_path> [--json]")
        sys.exit(1)
    
    transcript_path = Path(sys.argv[1])
    output_json = "--json" in sys.argv
    
    if not transcript_path.exists():
        print(f"Error: File not found: {transcript_path}")
        sys.exit(1)
    
    transcript = transcript_path.read_text()
    meeting_folder = transcript_path.parent.name
    
    candidates = detect_brokers(transcript, meeting_folder=meeting_folder)
    
    if output_json:
        print(json.dumps([c.to_dict() for c in candidates], indent=2))
    else:
        if candidates:
            print(format_broker_section_md(candidates))
        else:
            print("No broker candidates detected.")
