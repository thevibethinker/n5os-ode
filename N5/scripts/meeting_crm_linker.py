#!/usr/bin/env python3
"""Meeting ↔ CRM Linker

Under Stakeholder Intelligence Interface Contract (V1).

Responsibilities (Enrichment/Orchestration side):
- Walk non-internal meetings under Personal/Meetings/**.
- Ensure each external participant has a CRM markdown profile.
- Write meeting_crm_links.json into each meeting folder mapping participants → CRM slugs.

Viewer/join responsibilities remain in stakeholder_intel.py (read-only).
"""

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path("/home/workspace")
MEETINGS_ROOT = WORKSPACE / "Personal" / "Meetings"
CRM_ROOT = WORKSPACE / "Personal" / "Knowledge" / "CRM" / "individuals"
CRM_INDEX = WORKSPACE / "Knowledge" / "crm" / "individuals" / "index.jsonl"


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


def find_crm_slug_by_name(name: str, crm_index: Dict[str, Dict[str, str]]) -> Optional[str]:
    """Very simple name→slug resolution: exact match or lowercase match.

    This is intentionally conservative; future versions can use richer heuristics.
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


def ensure_crm_profile(participant: Participant, crm_index: Dict[str, Dict[str, str]]) -> str:
    """Return a CRM slug for the participant, creating a stub profile if needed.

    Creation writes a minimal markdown file under Personal/Knowledge/CRM/individuals.
    This respects the contract that CRM markdown is canonical for identity.
    """
    # Try to resolve existing
    slug = find_crm_slug_by_name(participant.name, crm_index)
    if slug:
        return slug

    # Create a new slug from name (very simple; future: use central slugifier)
    base_slug = "-".join(participant.name.strip().lower().split()) or "external-unknown"
    slug = base_slug
    counter = 2
    while (CRM_ROOT / f"{slug}.md").exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Write minimal CRM profile markdown
    crm_path = CRM_ROOT / f"{slug}.md"
    crm_path.parent.mkdir(parents=True, exist_ok=True)
    content_lines = [
        "---",
        f"created: 2025-11-30",
        f"last_edited: 2025-11-30",
        "version: 1.0",
        "---",
        "",
        f"# {participant.name}",
        "",
        "## Identity",
        f"**Status:** {'internal' if participant.is_internal else 'external'}",
        f"**Organization:** {participant.organization or 'Unknown'}",
        "",
        "## Intelligence Log",
        "",
    ]
    crm_path.write_text("\n".join(content_lines), encoding="utf-8")

    # Update in-memory index (path is relative from existing convention)
    rel_path = f"Personal/Knowledge/CRM/individuals/{slug}.md"
    crm_index[slug] = {"person_id": slug, "path": rel_path, "name": slug}

    return slug


def process_meeting(meeting_folder: Path, dry_run: bool = False) -> Optional[Dict]:
    manifest_path = meeting_folder / "manifest.json"
    manifest = load_manifest(manifest_path)
    if not manifest:
        return None

    meeting_type = manifest.get("meeting_type", "external")
    if meeting_type == "internal":
        return None

    selection = manifest.get("selection_notes", {})
    raw_participants = selection.get("key_stakeholders", [])
    if not raw_participants:
        return None

    crm_index = load_crm_index()
    participants: List[Participant] = [parse_participant(r) for r in raw_participants]

    links = {
        "meeting_id": manifest.get("meeting_id"),
        "meeting_type": meeting_type,
        "participants": [],
    }

    for p in participants:
        # Skip pure internal participants for linking, per enrichment posture
        if p.is_internal:
            links["participants"].append(
                {
                    "raw": p.raw,
                    "name": p.name,
                    "organization": p.organization,
                    "is_internal": True,
                    "crm_person_id": None,
                }
            )
            continue

        slug = ensure_crm_profile(p, crm_index) if not dry_run else find_crm_slug_by_name(p.name, crm_index)
        links["participants"].append(
            {
                "raw": p.raw,
                "name": p.name,
                "organization": p.organization,
                "is_internal": False,
                "crm_person_id": slug,
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
        # Only process [M] or [P] suffixed meeting folders under Personal/Meetings
        if "_quarantine" in str(meeting_folder):
            continue
        if not (meeting_folder.name.endswith("_[M]") or meeting_folder.name.endswith("_[P]")):
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

