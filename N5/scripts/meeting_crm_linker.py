#!/usr/bin/env python3
"""Meeting ↔ CRM Linker

Under Stakeholder Intelligence Interface Contract (V1).

Responsibilities (Enrichment/Orchestration side):
- Walk non-internal meetings under Personal/Meetings/**.
- Ensure each external participant has a CRM markdown profile.
- Write meeting_crm_links.json into each meeting folder mapping participants → CRM slugs.

Viewer/join responsibilities remain in stakeholder_intel.py (read-only).

UPDATED 2026-01-19: Now uses unified n5_core.db for person lookups.
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/home/workspace")

# Import canonical paths
import sys
sys.path.insert(0, str(Path(__file__).parent))
from crm_paths import CRM_INDIVIDUALS, CRM_INDEX as CANONICAL_INDEX, MEETINGS_ROOT as CANONICAL_MEETINGS
from db_paths import get_db_connection, PEOPLE_TABLE, INTERACTIONS_TABLE

# Import optimized lookup service (WS1 optimization)
try:
    from crm_lookup import CRMLookupService
    _CRM_LOOKUP_AVAILABLE = True
except ImportError:
    _CRM_LOOKUP_AVAILABLE = False

MEETINGS_ROOT = CANONICAL_MEETINGS
CRM_ROOT = CRM_INDIVIDUALS
CRM_INDEX = CANONICAL_INDEX

# Global lookup service instance (lazy initialized)
_crm_lookup_service = None


def get_crm_lookup_service():
    """Get or create the CRM lookup service singleton."""
    global _crm_lookup_service
    if _CRM_LOOKUP_AVAILABLE and _crm_lookup_service is None:
        _crm_lookup_service = CRMLookupService()
    return _crm_lookup_service


@dataclass
class Participant:
    raw: str
    name: str
    organization: Optional[str]
    is_internal: bool


def load_manifest(path: Path) -> Optional[Dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def extract_participants_from_b03(meeting_folder: Path) -> List[str]:
    """Extract participant names from B03/B08 STAKEHOLDER_INTELLIGENCE.md.

    Handles two formats:
    1. Person names as headers: ## Gabi Zijderveld
    2. Name field in content: **Name:** Sara Schmitt
    """
    b03_paths = [
        meeting_folder / "B03_STAKEHOLDER_INTELLIGENCE.md",
        meeting_folder / "B03_STAKE_HOLDER_INTELLIGENCE.md",
        meeting_folder / "B08_STAKEHOLDER_INTELLIGENCE.md",
    ]

    for b03_path in b03_paths:
        if not b03_path.exists():
            continue
        content = b03_path.read_text(encoding="utf-8")
        participants = []

        # Method 1: Extract from **Name:** field (B08 format)
        for match in re.finditer(r'\*\*Name:\*\*\s*([^\n]+)', content):
            name = match.group(1).strip()
            if name and len(name.split()) >= 2:
                participants.append(name)

        # Method 2: Extract person names from ## or ### headers (B03 format)
        if not participants:
            # Try ### headers first (nested under ## Participants)
            for match in re.finditer(r'^###\s+\*{0,2}([^#\n*]+)', content, re.MULTILINE):
                name = match.group(1).strip()
                name_lower = name.lower()

                # Skip common section headers that aren't people
                skip_keywords = {
                    'participants', 'group dynamics', 'stakeholder intelligence', 'stakeholder_intelligence',
                    'meeting context', 'relationship with v', 'relationship dynamics', 'identity',
                    'professional intelligence', 'interaction history', 'quick reference',
                    'auto-generated metadata', 'intelligence log', 'enrichment data',
                    'gmail intelligence', 'linkedin intelligence', 'founder profiles',
                    'dynamic between', 'threat assessment', 'information asymmetries',
                    'knowledge gaps', 'market influencer', 'potential acquirer', 'foundational profile',
                    'what resonated', 'crm integration', 'howie integration', 'domain authority',
                    'source credibility', 'internal stakeholders', 'external stakeholders',
                    'communication patterns', 'relationship notes', 'integration points',
                    'team dynamics', 'interpersonal patterns', 'cultural observations',
                    'conflict zones', 'intelligence gaps', 'follow-up trigger', 'relationship intelligence',
                }

                # Skip if matches any skip keyword
                if any(kw in name_lower for kw in skip_keywords):
                    continue

                # Skip numbered lists like "1. Name"
                if re.match(r'^\d+\.\s', name):
                    name = re.sub(r'^\d+\.\s*', '', name)

                # Skip if starts with B0 (block names)
                if name.upper().startswith('B0'):
                    continue

                # Skip if contains parenthetical role descriptions (except names like "John (Company)")
                bad_parens = ['role', 'inferred', 'unclear', 'referenced', 'investors', 'advisors', 'team']
                if any(bp in name_lower for bp in bad_parens if '(' in name):
                    continue

                # Skip if it looks like a section title (has colon)
                if ':' in name:
                    continue

                # Basic name validation: should have 2-5 words, start with capital
                # Remove parenthetical suffix for counting
                name_for_count = re.sub(r'\s*\([^)]+\)\s*$', '', name)
                words = name_for_count.split()
                if len(words) >= 2 and len(words) <= 5 and name[0].isupper():
                    participants.append(name)

        # If no ### headers found, try ## headers (alternate B03 format)
        if not participants:
            for match in re.finditer(r'^##\s+([^#\n]+)', content, re.MULTILINE):
                name = match.group(1).strip()
                name_lower = name.lower()

                # Skip common section headers
                skip_keywords = {
                    'participants', 'group dynamics', 'stakeholder intelligence', 'stakeholder_intelligence',
                    'meeting context', 'relationship with v', 'relationship dynamics', 'identity',
                    'professional intelligence', 'interaction history', 'quick reference',
                    'auto-generated metadata', 'intelligence log', 'enrichment data',
                    'gmail intelligence', 'linkedin intelligence', 'founder profiles',
                    'dynamic between', 'threat assessment', 'information asymmetries',
                    'knowledge gaps', 'market influencer', 'potential acquirer', 'foundational profile',
                    'what resonated', 'crm integration', 'howie integration', 'domain authority',
                    'source credibility', 'internal stakeholders', 'external stakeholders',
                    'communication patterns', 'relationship notes', 'integration points',
                    'team dynamics', 'interpersonal patterns', 'cultural observations',
                    'conflict zones', 'intelligence gaps', 'follow-up trigger', 'relationship intelligence',
                }

                if any(kw in name_lower for kw in skip_keywords):
                    continue
                if ':' in name or name.upper().startswith('B0'):
                    continue

                name_for_count = re.sub(r'\s*\([^)]+\)\s*$', '', name)
                words = name_for_count.split()
                if len(words) >= 2 and len(words) <= 5 and name[0].isupper():
                    participants.append(name)

        if participants:
            return participants

    return []


def extract_participants_from_folder_name(folder_name: str) -> List[str]:
    """Extract participant names from meeting folder name.

    Only extracts names that look like person names (First Last pattern).
    Skips folder names that are clearly meeting topics or descriptions.

    Examples:
        "2025-11-17_Vrijen-Attawar-And-Paula-Mcmahon" → ["Vrijen Attawar", "Paula Mcmahon"]
        "2025-12-16_Victor-hu-Lumos-capital" → ["Victor Hu"]
        "2025-11-10_Daily-Standup" → []  # Not a person name
    """
    # Remove date prefix
    name_part = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', folder_name)
    # Remove common suffixes
    name_part = re.sub(r'_\[M\]$|_\[P\]$|_Internal$|_external.*$', '', name_part, flags=re.IGNORECASE)

    # Skip clearly non-person folder names
    skip_patterns = [
        r'^daily[-_]', r'[-_]standup', r'[-_]meeting', r'[-_]sync',
        r'^internal[-_]', r'[-_]internal$', r'^team[-_]', r'[-_]team$',
        r'[-_]review', r'[-_]planning', r'[-_]strategy', r'[-_]admin',
        r'[-_]war[-_]room', r'^acquisition', r'[-_]coaching',
        r'[-_]financial', r'[-_]discovery', r'[-_]intelligence',
    ]
    name_lower = name_part.lower()
    if any(re.search(pat, name_lower) for pat in skip_patterns):
        return []

    # Split on common separators for multiple participants
    # Handle "And", "_And_", "-And-" between names
    parts = re.split(r'[-_]And[-_]|[-_]and[-_]|-x-|_x_', name_part, flags=re.IGNORECASE)

    participants = []
    for part in parts:
        # Convert dashes/underscores to spaces
        name = re.sub(r'[-_]', ' ', part).strip()
        words = name.split()

        # Skip if doesn't look like a name (needs 2+ words, no numbers, etc.)
        if len(words) < 2:
            continue

        # Take first 2-3 words as name
        candidate = ' '.join(words[:3]).title()

        # Basic validation: both parts should be capitalized words
        name_words = candidate.split()
        if all(w[0].isupper() and w.isalpha() for w in name_words[:2] if len(w) > 0):
            participants.append(candidate)

    return participants


def parse_participant(raw: str) -> Participant:
    # Examples: "Jake Gates (Marvin)", "Vrijen Attawar (Careerspan)"
    m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", raw)
    if m:
        name = m.group(1).strip()
        org = m.group(2).strip() or None
    else:
        name = raw.strip()
        org = None

    # Simple internal heuristic: Careerspan or V's own slug/org
    is_internal = False
    lower = raw.lower()
    if "careerspan" in lower or "vrijen" in lower or "attawar" in lower:
        is_internal = True

    return Participant(raw=raw, name=name, organization=org, is_internal=is_internal)


def load_crm_index() -> Dict[str, Dict[str, str]]:
    """Load Knowledge/crm/individuals/index.jsonl into a dict keyed by slug.

    Value shape: {"person_id": slug, "path": relative_path, "name": name}
    """
    index: Dict[str, Dict[str, str]] = {}
    if not CRM_INDEX.exists():
        return index
    with CRM_INDEX.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            slug = rec.get("person_id")
            if slug:
                index[slug] = rec
    return index


def find_crm_slug_by_name(name: str, crm_index: Dict[str, Dict[str, str]], email: Optional[str] = None) -> Optional[str]:
    """Name→slug resolution using optimized lookup service with legacy fallback.

    Uses the SQLite-indexed CRMLookupService for O(1) lookups when available,
    falling back to the legacy O(n) scan for backwards compatibility.

    Args:
        name: Person name to look up.
        crm_index: Legacy in-memory index dict (used as fallback).
        email: Optional email for higher-confidence matching.

    Returns:
        CRM slug if found, None otherwise.
    """
    # Try optimized O(1) lookup first (WS1 optimization)
    lookup_service = get_crm_lookup_service()
    if lookup_service:
        result = lookup_service.lookup_participant(name, email)
        if result:
            return result.slug

    # Legacy O(n) fallback
    return _find_crm_slug_by_name_legacy(name, crm_index)


def _find_crm_slug_by_name_legacy(name: str, crm_index: Dict[str, Dict[str, str]]) -> Optional[str]:
    """Legacy O(n) name→slug resolution. Kept for backwards compatibility.

    This is the original implementation that does a linear scan through
    all index entries. Deprecated in favor of CRMLookupService.
    """
    target = name.strip().lower()
    # Exact match on name field
    for slug, rec in crm_index.items():
        if rec.get("name", "").strip().lower() == target:
            return slug
    # Fallback: slug match on simplified name (e.g., "Jake Weissbourd" → "jake-weissbourd")
    simplified = "-".join(target.split())
    if simplified in crm_index:
        return simplified
    return None


def find_person_in_db(name: str = None, email: str = None) -> Optional[Dict]:
    """Find person in unified database by name or email.
    
    Returns dict with id, full_name, email, markdown_path or None if not found.
    """
    if not name and not email:
        return None
    
    conn = get_db_connection(readonly=True)
    try:
        if email:
            row = conn.execute(
                f"SELECT id, full_name, email, markdown_path FROM {PEOPLE_TABLE} WHERE email = ?",
                (email,)
            ).fetchone()
            if row:
                return dict(row)
        
        if name:
            # Try exact match first
            row = conn.execute(
                f"SELECT id, full_name, email, markdown_path FROM {PEOPLE_TABLE} WHERE full_name = ?",
                (name,)
            ).fetchone()
            if row:
                return dict(row)
            
            # Try case-insensitive match
            row = conn.execute(
                f"SELECT id, full_name, email, markdown_path FROM {PEOPLE_TABLE} WHERE LOWER(full_name) = LOWER(?)",
                (name,)
            ).fetchone()
            if row:
                return dict(row)
        
        return None
    finally:
        conn.close()


def create_person_in_db(name: str, organization: str = None, markdown_path: str = None) -> int:
    """Create a new person record in the unified database.
    
    Returns the new person's id.
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            f"""INSERT INTO {PEOPLE_TABLE} (full_name, company, markdown_path, source_db)
               VALUES (?, ?, ?, 'meeting_linker')""",
            (name, organization, markdown_path)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def record_meeting_interaction(person_id: int, meeting_id: str, meeting_folder: str, meeting_date: str = None):
    """Record a meeting interaction for a person."""
    from datetime import datetime
    
    conn = get_db_connection()
    try:
        # Check if interaction already exists
        existing = conn.execute(
            f"SELECT id FROM {INTERACTIONS_TABLE} WHERE person_id = ? AND source_ref = ?",
            (person_id, meeting_folder)
        ).fetchone()
        
        if not existing:
            occurred_at = meeting_date or datetime.now().isoformat()
            conn.execute(
                f"""INSERT INTO {INTERACTIONS_TABLE} 
                   (person_id, type, summary, source_ref, occurred_at)
                   VALUES (?, 'meeting', ?, ?, ?)""",
                (person_id, f"Meeting: {meeting_id}", meeting_folder, occurred_at)
            )
            conn.commit()
    finally:
        conn.close()


def ensure_crm_profile(p: Participant, crm_index: Dict) -> Tuple[Optional[str], Optional[int]]:
    """Ensure participant has a CRM profile in both markdown and database.
    
    Returns tuple of (crm_slug, person_id) where person_id is from n5_core.db.
    """
    # First check if person exists in the database
    person = find_person_in_db(name=p.name)
    
    if person:
        # Person exists in DB, get their slug from markdown_path
        if person.get('markdown_path'):
            slug = Path(person['markdown_path']).stem
        else:
            slug = None
        return (slug, person['id'])
    
    # Check markdown index fallback
    slug = find_crm_slug_by_name(p.name, crm_index)
    
    if slug:
        # Found in markdown, need to create DB entry
        profile_path = CRM_ROOT / f"{slug}.md"
        markdown_path = str(profile_path.relative_to(WORKSPACE)) if profile_path.exists() else None
        person_id = create_person_in_db(p.name, p.organization, markdown_path)
        return (slug, person_id)
    
    # Need to create both markdown and DB entry
    slug = generate_slug(p.name)
    profile_path = CRM_ROOT / f"{slug}.md"
    
    if not profile_path.exists():
        from crm_paths import ensure_crm_dirs
        ensure_crm_dirs()
        
        # Create markdown profile
        profile_content = f"""---
created: {__import__('datetime').date.today().isoformat()}
last_edited: {__import__('datetime').date.today().isoformat()}
version: 1.0
provenance: meeting_crm_linker
---

# {p.name}

**Organization:** {p.organization or '[Unknown]'}
**Role:** [To be determined]
**Status:** active

## Interaction History

*No interactions recorded yet.*
"""
        profile_path.write_text(profile_content, encoding="utf-8")
    
    # Create DB entry
    markdown_path = str(profile_path.relative_to(WORKSPACE))
    person_id = create_person_in_db(p.name, p.organization, markdown_path)
    
    return (slug, person_id)


def process_meeting(meeting_folder: Path, dry_run: bool = False) -> Optional[Dict]:
    """Process a single meeting folder, linking participants to CRM."""
    manifest = load_manifest(meeting_folder / "manifest.json")
    if not manifest:
        return None

    meeting_type = manifest.get("meeting_type", "")
    # Skip internal meetings
    if meeting_type and meeting_type.lower() == "internal":
        return None

    crm_index = load_crm_index()
    raw_participants = extract_participants(meeting_folder, manifest)

    if not raw_participants:
        return None

    participants: List[Participant] = [parse_participant(r) for r in raw_participants]

    links = {
        "meeting_id": manifest.get("meeting_id"),
        "meeting_type": meeting_type,
        "participants": [],
    }

    meeting_date = manifest.get("start_time") or manifest.get("date")

    for p in participants:
        # Skip pure internal participants for linking, per enrichment posture
        if p.is_internal:
            links["participants"].append(
                {
                    "raw": p.raw,
                    "name": p.name,
                    "organization": p.organization,
                    "is_internal": True,
                    "crm_slug": None,
                    "person_id": None,
                }
            )
            continue

        if dry_run:
            slug = find_crm_slug_by_name(p.name, crm_index)
            person = find_person_in_db(name=p.name)
            person_id = person['id'] if person else None
        else:
            slug, person_id = ensure_crm_profile(p, crm_index)
            
            # Record the meeting interaction
            if person_id:
                record_meeting_interaction(
                    person_id, 
                    manifest.get("meeting_id", "unknown"),
                    str(meeting_folder),
                    meeting_date
                )
        
        links["participants"].append(
            {
                "raw": p.raw,
                "name": p.name,
                "organization": p.organization,
                "is_internal": False,
                "crm_slug": slug,
                "person_id": person_id,
            }
        )

    if not dry_run:
        out_path = meeting_folder / "meeting_crm_links.json"
        out_path.write_text(json.dumps(links, indent=2), encoding="utf-8")

    return links


def scan_meetings(root: Path, limit: Optional[int] = None, dry_run: bool = False) -> List[Tuple[Path, Optional[Dict]]]:
    results: List[Tuple[Path, Optional[Dict]]] = []
    count = 0
    for path in sorted(root.rglob("manifest.json")):
        meeting_folder = path.parent
        # Skip quarantine folders
        if "_quarantine" in str(meeting_folder):
            continue
        # Process folders with manifest.json - check status instead of folder suffix
        manifest = load_manifest(meeting_folder / "manifest.json")
        if not manifest:
            continue
        status = manifest.get("status", "")
        # Process meetings that have been through initial processing
        if status not in ("processed", "manifest_generated", "mg2_completed", "intelligence_generated"):
            continue
        res = process_meeting(meeting_folder, dry_run=dry_run)
        results.append((meeting_folder, res))
        count += 1
        if limit is not None and count >= limit:
            break
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Link meetings to CRM people and write meeting_crm_links.json")
    parser.add_argument("--root", default=str(MEETINGS_ROOT), help="Meetings root (default: Personal/Meetings)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of meetings to process")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files, just print summary")
    args = parser.parse_args()

    root = Path(args.root)
    results = scan_meetings(root, limit=args.limit, dry_run=args.dry_run)

    for folder, links in results:
        if not links:
            continue
        print(f"{folder} → {links['meeting_id']} ({links['meeting_type']})")
        for p in links["participants"]:
            print(
                f"  - {p['raw']} | internal={p['is_internal']} | crm_person_id={p['crm_person_id']}"
            )


if __name__ == "__main__":
    main()

