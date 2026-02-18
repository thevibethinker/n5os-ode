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
from crm_identity_resolver import CRMIdentityResolver
from crm_semantic_memory import record_person_interaction, sync_person_to_semantic_memory

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
_identity_resolver = CRMIdentityResolver(auto_link_threshold=0.99)


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


_NON_PERSON_KEYWORDS = {
    "participants", "group", "dynamics", "stakeholder", "intelligence", "meeting",
    "context", "relationship", "identity", "professional", "interaction", "history",
    "quick", "reference", "generated", "metadata", "enrichment", "gmail", "linkedin",
    "profiles", "profile", "threat", "assessment", "information", "asymmetries",
    "knowledge", "gaps", "market", "influencer", "potential", "acquirer", "foundational",
    "resonated", "integration", "domain", "credibility", "internal", "external",
    "communication", "notes", "team", "interpersonal", "cultural", "conflict",
    "follow-up", "followup", "strategic", "alignment", "actions", "next", "steps",
    "implications", "challenges", "opportunity", "opportunities", "takeaway",
    "trust", "building", "moments", "long-term", "longterm", "philosophy", "key",
    "quotes", "role", "conversation", "proposition", "current", "state", "talent",
    "mention", "mentioned", "situation", "founders", "engineers", "target", "candidates",
    "organizational", "insights", "sentiment", "analysis", "parties",
    "careerspan", "linear",
}


def _normalize_candidate_name(raw: str) -> str:
    candidate = raw.strip().strip("*#-").strip()
    candidate = re.sub(r"^\d+\.\s*", "", candidate)
    candidate = re.sub(r"\s+", " ", candidate)
    return candidate


def _looks_like_person_name(raw: str) -> bool:
    candidate = _normalize_candidate_name(raw)
    if not candidate:
        return False
    if any(ch in candidate for ch in [":", "/", "[", "]", "`"]):
        return False
    if candidate.upper().startswith("B0"):
        return False

    # Allow optional trailing organization in parentheses; validate core name only.
    core = re.sub(r"\s*\([^)]+\)\s*$", "", candidate).strip()
    words = core.split()
    if not (2 <= len(words) <= 5):
        return False

    for word in words:
        cleaned = word.strip(".,;!?")
        if not cleaned:
            return False
        if cleaned.lower() in _NON_PERSON_KEYWORDS:
            return False
        if not re.fullmatch(r"[A-Za-z][A-Za-z'\-]*", cleaned):
            return False

    # Require at least two title-like tokens (helps reject sentence fragments).
    title_like = sum(1 for w in words if w[:1].isupper())
    return title_like >= 2


def _dedupe_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for v in values:
        key = _normalize_candidate_name(v).lower()
        if key and key not in seen:
            seen.add(key)
            out.append(_normalize_candidate_name(v))
    return out


def _filter_candidate_participants(candidates: List[str]) -> List[str]:
    filtered: List[str] = []
    for raw in candidates:
        candidate = _normalize_candidate_name(raw)
        if not candidate:
            continue
        if "@" in candidate:
            filtered.append(candidate)
            continue
        if _looks_like_person_name(candidate):
            filtered.append(candidate)
    return _dedupe_preserve_order(filtered)


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
            name = _normalize_candidate_name(match.group(1))
            if _looks_like_person_name(name):
                participants.append(name)

        # Method 2: Extract person names from ## or ### headers (B03 format)
        if not participants:
            # Try ### headers first (nested under ## Participants)
            for match in re.finditer(r'^###\s+\*{0,2}([^#\n*]+)', content, re.MULTILINE):
                name = _normalize_candidate_name(match.group(1))
                if _looks_like_person_name(name):
                    participants.append(name)

        # If no ### headers found, try ## headers (alternate B03 format)
        if not participants:
            for match in re.finditer(r'^##\s+([^#\n]+)', content, re.MULTILINE):
                name = _normalize_candidate_name(match.group(1))
                if _looks_like_person_name(name):
                    participants.append(name)

        participants = _dedupe_preserve_order(participants)
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
        words = [w for w in name.split() if w]

        # Skip if doesn't look like a name (needs 2+ words, no numbers, etc.)
        if len(words) < 2:
            continue

        # Use first two tokens as likely person name; extra tokens are usually org/topic descriptors.
        candidate = ' '.join(words[:2]).title()
        if _looks_like_person_name(candidate):
            participants.append(candidate)

    return _dedupe_preserve_order(participants)


def extract_participants(meeting_folder: Path, manifest: Dict) -> List[str]:
    """Extract participant names from manifest, intelligence docs, or folder name."""
    for key in ("participants", "attendees", "external_participants"):
        val = manifest.get(key)
        if isinstance(val, list) and val:
            names: List[str] = []
            for item in val:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("display_name") or item.get("email")
                    if name:
                        names.append(str(name))
            names = _filter_candidate_participants(names)
            if names:
                return names

    b03_names = extract_participants_from_b03(meeting_folder)
    b03_names = _filter_candidate_participants(b03_names)
    if b03_names:
        return b03_names

    return _filter_candidate_participants(extract_participants_from_folder_name(meeting_folder.name))


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
            if result.markdown_path:
                return Path(result.markdown_path).stem
            return _find_crm_slug_by_name_legacy(result.display_name, crm_index)

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


def find_person_in_db(name: str = None, email: str = None, company: str = None) -> Optional[Dict]:
    """High-precision person lookup in n5_core via shared resolver."""
    if not name and not email:
        return None

    result = _identity_resolver.auto_link(name=name, email=email, company=company)
    if result.person_id is None:
        return None

    return {
        "id": result.person_id,
        "full_name": result.full_name,
        "email": result.email,
        "markdown_path": result.markdown_path,
        "match_method": result.method,
        "match_confidence": result.confidence,
    }

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


def queue_identity_review(name: str, organization: Optional[str], candidate_person_id: int, confidence: float) -> None:
    """Queue ambiguous identity matches for review in pending_approvals."""
    context = json.dumps(
        {
            "name": name,
            "organization": organization,
            "candidate_person_id": candidate_person_id,
            "confidence": round(confidence, 4),
        }
    )
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO pending_approvals (entity_type, name, person_id, context, source_text, pipeline, status, created_at)
            VALUES ('person_identity', ?, ?, ?, ?, 'meeting_crm_linker', 'pending', datetime('now'))
            """,
            (
                name,
                candidate_person_id,
                context,
                f"Ambiguous identity match for {name}",
            ),
        )
        conn.commit()
    finally:
        conn.close()


def record_meeting_interaction(person_id: int, meeting_id: str, meeting_folder: str, meeting_date: str = None):
    """Record a meeting interaction for a person."""
    occurred_at = meeting_date or __import__("datetime").datetime.now().isoformat()
    record_person_interaction(
        person_id=person_id,
        interaction_type="meeting",
        summary=f"Meeting: {meeting_id}",
        source_ref=meeting_folder,
        occurred_at=occurred_at,
    )
    sync_person_to_semantic_memory(
        person_id,
        trigger="meeting_linked",
        metadata={"meeting_id": meeting_id, "meeting_folder": meeting_folder},
    )


def ensure_crm_profile(p: Participant, crm_index: Dict) -> Tuple[Optional[str], Optional[int]]:
    """Ensure participant has a CRM profile in both markdown and database.

    Returns tuple of (crm_slug, person_id) where person_id is from n5_core.db.
    """
    resolver_candidate = _identity_resolver.resolve(name=p.name, company=p.organization)
    if resolver_candidate.person_id and 0.75 <= resolver_candidate.confidence < _identity_resolver.auto_link_threshold:
        queue_identity_review(
            name=p.name,
            organization=p.organization,
            candidate_person_id=resolver_candidate.person_id,
            confidence=resolver_candidate.confidence,
        )
        existing_slug = Path(resolver_candidate.markdown_path).stem if resolver_candidate.markdown_path else None
        return (existing_slug, resolver_candidate.person_id)

    person = find_person_in_db(name=p.name, company=p.organization)

    if person:
        if person.get('markdown_path'):
            slug = Path(person['markdown_path']).stem
        else:
            slug = None
        sync_person_to_semantic_memory(
            int(person['id']),
            trigger="meeting_identity_resolved",
            metadata={"name": p.name, "organization": p.organization},
        )
        return (slug, person['id'])

    slug = find_crm_slug_by_name(p.name, crm_index)

    if slug:
        profile_path = CRM_ROOT / f"{slug}.md"
        markdown_path = str(profile_path.relative_to(WORKSPACE)) if profile_path.exists() else None
        person_id = create_person_in_db(p.name, p.organization, markdown_path)
        sync_person_to_semantic_memory(
            person_id,
            trigger="meeting_identity_created_from_slug",
            metadata={"name": p.name, "organization": p.organization, "slug": slug},
        )
        return (slug, person_id)

    slug = generate_slug(p.name)
    profile_path = CRM_ROOT / f"{slug}.md"

    if not profile_path.exists():
        from crm_paths import ensure_crm_dirs
        ensure_crm_dirs()

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

    markdown_path = str(profile_path.relative_to(WORKSPACE))
    person_id = create_person_in_db(p.name, p.organization, markdown_path)
    sync_person_to_semantic_memory(
        person_id,
        trigger="meeting_identity_created",
        metadata={"name": p.name, "organization": p.organization, "slug": slug},
    )

    return (slug, person_id)


def preview_identity_resolution(p: Participant, crm_index: Dict[str, Dict[str, str]]) -> Tuple[Optional[str], Optional[int]]:
    """Preview identity resolution without side effects (dry-run parity with live logic)."""
    candidate = _identity_resolver.resolve(name=p.name, company=p.organization)
    if candidate.person_id and candidate.confidence >= 0.75:
        slug = Path(candidate.markdown_path).stem if candidate.markdown_path else find_crm_slug_by_name(p.name, crm_index)
        return slug, candidate.person_id

    slug = find_crm_slug_by_name(p.name, crm_index)
    if slug:
        return slug, None
    return None, None

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
            slug, person_id = preview_identity_resolution(p, crm_index)
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
                f"  - {p['raw']} | internal={p['is_internal']} | person_id={p['person_id']}"
            )


if __name__ == "__main__":
    main()
