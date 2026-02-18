#!/usr/bin/env python3
"""Org profile enrichment backfill for relationship-intelligence-os.

Scans historical meeting intelligence blocks, extracts organization deltas,
merges into canonical org profiles with provenance, and optionally projects
compact representations into semantic memory (`brain.db` entities table).
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

BLOCK_FILE_PREFIXES: dict[str, str] = {
    "B08": "B08_",
    "B03": "B03_",
    "B40": "B40_",
    "B02_B05": "B02_B05_",
    "B41": "B41_",
    "B32": "B32_",
    "B33": "B33_",
}

DELTA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "priority_shift": ("priority", "focus", "roadmap", "initiative", "goal"),
    "budget_change": ("budget", "runway", "burn", "cost", "funding", "pricing"),
    "process_change": ("process", "workflow", "approval", "procurement", "decision path"),
    "technology_adoption": ("adopt", "tooling", "platform", "automation", "ai"),
    "strategic_initiative": ("partnership", "expand", "launch", "go-to-market", "gtm"),
    "operational_challenge": ("challenge", "constraint", "blocked", "friction", "risk"),
    "competitive_landscape": ("competitor", "competitive", "alternative", "vs", "market pressure"),
    "timeline_update": ("timeline", "deadline", "quarter", "q1", "q2", "q3", "q4"),
    "leadership_change": ("new leader", "hiring", "head of", "vp", "chief", "reorg"),
}

POSITIVE_MARKERS = ("increase", "improve", "grow", "expand", "accelerate", "win")
NEGATIVE_MARKERS = ("decrease", "decline", "risk", "block", "delay", "cut", "concern")

BAD_ORG_VALUES = {
    "",
    "v",
    "unknown",
    "n/a",
    "none",
    "internal",
    "external",
    "founder",
    "chief of staff",
}


@dataclass
class OrgDelta:
    """Organization delta extracted from a meeting block."""

    delta_id: str
    org_id: str
    org_name: str
    meeting_id: str
    meeting_dir: str
    block_type: str
    delta_type: str
    confidence: float
    polarity: str
    impact_level: int
    evidence: list[str]
    source_file: str
    extracted_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "delta_id": self.delta_id,
            "organization_id": self.org_id,
            "organization_name": self.org_name,
            "meeting_id": self.meeting_id,
            "meeting_dir": self.meeting_dir,
            "block_type": self.block_type,
            "delta_type": self.delta_type,
            "confidence": self.confidence,
            "polarity": self.polarity,
            "impact_level": self.impact_level,
            "evidence": self.evidence,
            "provenance": {
                "source_file": self.source_file,
                "processor": "org_profile_backfill.py",
                "processed_at": self.extracted_at,
            },
        }


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""

    return datetime.now(UTC).isoformat()


def log(level: str, message: str) -> None:
    """Emit a timestamped log line."""

    print(f"[{utc_now_iso()}] [{level}] {message}")


def stable_id(prefix: str, *parts: str, length: int = 12) -> str:
    """Create deterministic IDs from input parts."""

    payload = "||".join(parts).encode("utf-8")
    return f"{prefix}_{sha256(payload).hexdigest()[:length]}"


def normalize_org_name(value: str) -> str:
    """Normalize organization names for consistent matching."""

    cleaned = re.sub(r"\s+", " ", value.replace("\n", " ")).strip(" -|")
    cleaned = re.sub(r"\(.*?\)", "", cleaned).strip()
    return cleaned


def load_json(path: Path) -> dict[str, Any] | None:
    """Load JSON object from file, return None on parse or IO error."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        log("WARN", f"Invalid JSON in {path}: {exc}")
        return None
    except OSError as exc:
        log("WARN", f"Cannot read {path}: {exc}")
        return None


def iter_meeting_dirs(meetings_root: Path) -> list[Path]:
    """Return sorted meeting directories that contain relevant block files."""

    candidate_dirs: set[Path] = set()
    for prefix in BLOCK_FILE_PREFIXES.values():
        for block_file in meetings_root.rglob(f"{prefix}*.md"):
            candidate_dirs.add(block_file.parent)
    return sorted(candidate_dirs)


def extract_orgs_from_links(meeting_dir: Path) -> set[str]:
    """Extract organizations from meeting CRM link metadata."""

    orgs: set[str] = set()
    links = load_json(meeting_dir / "meeting_crm_links.json")
    if not links:
        return orgs

    for participant in links.get("participants", []):
        if participant.get("is_internal"):
            continue
        org_raw = str(participant.get("organization") or "").strip()
        org = normalize_org_name(org_raw)
        if org and org.lower() not in BAD_ORG_VALUES:
            orgs.add(org)
    return orgs


def extract_orgs_from_manifest(meeting_dir: Path) -> set[str]:
    """Extract organizations from manifest enrichment payloads."""

    orgs: set[str] = set()
    manifest = load_json(meeting_dir / "manifest.json")
    if not manifest:
        return orgs

    crm = manifest.get("crm_enrichment") or {}
    for match in crm.get("participant_matches", []):
        company_raw = str(match.get("company") or "").strip()
        company = normalize_org_name(company_raw)
        if company and company.lower() not in BAD_ORG_VALUES:
            orgs.add(company)
    return orgs


def extract_orgs_from_b08(meeting_dir: Path) -> set[str]:
    """Fallback extraction from B08 table rows."""

    orgs: set[str] = set()
    for b08_file in meeting_dir.glob("B08_*.md"):
        try:
            text = b08_file.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            log("WARN", f"Cannot read {b08_file}: {exc}")
            continue
        for match in re.finditer(r"\|\s*\*\*Organization\*\*\s*\|\s*(.*?)\s*\|", text, flags=re.IGNORECASE):
            org = normalize_org_name(match.group(1))
            if org and org.lower() not in BAD_ORG_VALUES:
                orgs.add(org)
    return orgs


def extract_organizations(meeting_dir: Path) -> set[str]:
    """Extract organization names using metadata-first strategy."""

    orgs = set()
    orgs.update(extract_orgs_from_links(meeting_dir))
    orgs.update(extract_orgs_from_manifest(meeting_dir))
    orgs.update(extract_orgs_from_b08(meeting_dir))
    return {o for o in orgs if o and o.lower() not in BAD_ORG_VALUES}


def infer_meeting_id(meeting_dir: Path) -> str:
    """Infer meeting ID from manifest or directory name."""

    manifest = load_json(meeting_dir / "manifest.json")
    if manifest and manifest.get("meeting_id"):
        return str(manifest["meeting_id"])
    return meeting_dir.name


def polarity_from_text(content: str) -> str:
    """Infer coarse polarity from marker counts."""

    lower = content.lower()
    pos = sum(lower.count(marker) for marker in POSITIVE_MARKERS)
    neg = sum(lower.count(marker) for marker in NEGATIVE_MARKERS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def score_confidence(block_type: str, hit_count: int, evidence_count: int) -> float:
    """Compute deterministic confidence for extracted deltas."""

    base = 0.45
    if block_type in {"B08", "B03"}:
        base += 0.15
    elif block_type in {"B32", "B33"}:
        base += 0.1
    elif block_type in {"B40", "B41", "B02_B05"}:
        base += 0.08

    base += min(0.2, hit_count * 0.04)
    base += min(0.1, evidence_count * 0.03)
    return round(min(0.95, max(0.35, base)), 3)


def extract_evidence_lines(content: str, keywords: tuple[str, ...], max_items: int = 3) -> list[str]:
    """Extract short evidence snippets containing target keywords."""

    snippets: list[str] = []
    lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in keywords):
            normalized = re.sub(r"\s+", " ", line)
            snippets.append(normalized[:240])
        if len(snippets) >= max_items:
            break
    return snippets


def extract_deltas_from_block(
    *,
    org_name: str,
    org_id: str,
    meeting_id: str,
    meeting_dir: Path,
    block_file: Path,
    block_type: str,
) -> list[OrgDelta]:
    """Extract typed org deltas from one block file."""

    try:
        content = block_file.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        log("WARN", f"Failed to read block {block_file}: {exc}")
        return []

    lower = content.lower()
    deltas: list[OrgDelta] = []

    for delta_type, keywords in DELTA_KEYWORDS.items():
        hit_count = sum(lower.count(keyword) for keyword in keywords)
        if hit_count == 0:
            continue

        evidence = extract_evidence_lines(content, keywords)
        confidence = score_confidence(block_type, hit_count, len(evidence))
        polarity = polarity_from_text("\n".join(evidence) if evidence else content[:400])
        impact_level = max(1, min(5, 1 + hit_count // 2))
        delta_id = stable_id(
            "od",
            org_name.lower(),
            meeting_id,
            block_type,
            delta_type,
            "|".join(evidence)[:240],
        )

        deltas.append(
            OrgDelta(
                delta_id=delta_id,
                org_id=org_id,
                org_name=org_name,
                meeting_id=meeting_id,
                meeting_dir=str(meeting_dir),
                block_type=block_type,
                delta_type=delta_type,
                confidence=confidence,
                polarity=polarity,
                impact_level=impact_level,
                evidence=evidence,
                source_file=str(block_file),
                extracted_at=utc_now_iso(),
            )
        )

    return deltas


def load_canonical_profiles(canonical_path: Path) -> dict[str, dict[str, Any]]:
    """Load canonical profiles keyed by org_id."""

    if not canonical_path.exists():
        return {}
    try:
        payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Cannot load canonical profiles: {canonical_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"Canonical profile file must be JSON object: {canonical_path}")
    return payload


def load_existing_jsonl_ids(jsonl_path: Path, id_field: str) -> set[str]:
    """Load existing IDs from JSONL file for idempotent append."""

    ids: set[str] = set()
    if not jsonl_path.exists():
        return ids
    try:
        with jsonl_path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                item_id = item.get(id_field)
                if item_id:
                    ids.add(str(item_id))
    except OSError as exc:
        raise RuntimeError(f"Cannot read JSONL IDs from {jsonl_path}: {exc}") from exc
    return ids


def ensure_profile(org_id: str, org_name: str, profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Create default profile structure if absent."""

    if org_id not in profiles:
        profiles[org_id] = {
            "org_id": org_id,
            "organization_name": org_name,
            "aliases": [org_name],
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
            "confidence_score": 0.0,
            "delta_history": [],
            "latest_by_type": {},
            "signal_counts": {},
            "sources": [],
            "applied_delta_ids": [],
            "unresolved_conflicts": [],
        }
    return profiles[org_id]


def merge_delta_into_profile(delta: OrgDelta, profile: dict[str, Any], merge_audit: list[dict[str, Any]]) -> str:
    """Merge a delta into a profile with confidence and conflict handling."""

    applied_ids = set(profile.get("applied_delta_ids", []))
    if delta.delta_id in applied_ids:
        merge_audit.append(
            {
                "delta_id": delta.delta_id,
                "org_id": delta.org_id,
                "outcome": "duplicate_skipped",
                "confidence": delta.confidence,
                "at": utc_now_iso(),
            }
        )
        return "duplicate_skipped"

    prior = profile.get("latest_by_type", {}).get(delta.delta_type)
    conflict = False
    if prior:
        prior_conf = float(prior.get("confidence", 0.0))
        prior_pol = str(prior.get("polarity", "neutral"))
        if prior_pol != "neutral" and delta.polarity != "neutral":
            if prior_pol != delta.polarity and prior_conf >= 0.72 and delta.confidence >= 0.72:
                conflict = True

    if conflict:
        profile.setdefault("unresolved_conflicts", []).append(
            {
                "delta_id": delta.delta_id,
                "delta_type": delta.delta_type,
                "new_polarity": delta.polarity,
                "previous_polarity": prior.get("polarity"),
                "new_confidence": delta.confidence,
                "previous_confidence": prior.get("confidence"),
                "meeting_id": delta.meeting_id,
                "raised_at": utc_now_iso(),
            }
        )
        outcome = "conflict_flagged"
    elif delta.confidence >= 0.75:
        outcome = "applied_high_confidence"
    elif delta.confidence >= 0.55:
        outcome = "applied_medium_confidence"
    else:
        outcome = "queued_low_confidence"

    profile.setdefault("delta_history", []).append(delta.as_dict())
    profile["delta_history"] = profile["delta_history"][-300:]

    if outcome in {"applied_high_confidence", "applied_medium_confidence"}:
        profile.setdefault("latest_by_type", {})[delta.delta_type] = {
            "delta_id": delta.delta_id,
            "meeting_id": delta.meeting_id,
            "polarity": delta.polarity,
            "confidence": delta.confidence,
            "updated_at": utc_now_iso(),
        }

        signal_counts = profile.setdefault("signal_counts", {})
        signal_counts[delta.delta_type] = int(signal_counts.get(delta.delta_type, 0)) + 1

        prior_score = float(profile.get("confidence_score", 0.0))
        profile["confidence_score"] = round((prior_score * 0.7) + (delta.confidence * 0.3), 3)

    profile.setdefault("sources", []).append(
        {
            "meeting_id": delta.meeting_id,
            "block_type": delta.block_type,
            "source_file": delta.source_file,
            "processed_at": delta.extracted_at,
        }
    )
    profile["sources"] = profile["sources"][-100:]

    applied_ids.add(delta.delta_id)
    profile["applied_delta_ids"] = sorted(applied_ids)
    profile["updated_at"] = utc_now_iso()

    merge_audit.append(
        {
            "delta_id": delta.delta_id,
            "org_id": delta.org_id,
            "outcome": outcome,
            "confidence": delta.confidence,
            "at": utc_now_iso(),
        }
    )
    return outcome


def summarize_projection(profile: dict[str, Any]) -> str:
    """Build compact projection text for semantic memory."""

    top_signals = sorted(
        profile.get("signal_counts", {}).items(),
        key=lambda kv: (-kv[1], kv[0]),
    )[:5]
    top_str = ", ".join(f"{k}:{v}" for k, v in top_signals) if top_signals else "none"
    conflicts = len(profile.get("unresolved_conflicts", []))
    return (
        f"Org {profile['organization_name']} | confidence={profile.get('confidence_score', 0.0)} | "
        f"signals={top_str} | unresolved_conflicts={conflicts}"
    )


def upsert_semantic_entity(conn: sqlite3.Connection, profile: dict[str, Any]) -> bool:
    """Upsert org profile projection into brain.db entities."""

    canonical = profile["organization_name"].strip().lower()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, mention_count
        FROM entities
        WHERE type = 'organization' AND lower(canonical_name) = ?
        LIMIT 1
        """,
        (canonical,),
    )
    existing = cursor.fetchone()

    metadata = {
        "projection_type": "org_profile_backfill",
        "org_id": profile["org_id"],
        "confidence_score": profile.get("confidence_score", 0.0),
        "signal_counts": profile.get("signal_counts", {}),
        "unresolved_conflicts": len(profile.get("unresolved_conflicts", [])),
        "summary": summarize_projection(profile),
        "updated_at": profile.get("updated_at"),
    }

    now = utc_now_iso()
    if existing:
        entity_id, mention_count = existing
        cursor.execute(
            """
            UPDATE entities
            SET name = ?,
                canonical_name = ?,
                last_seen_at = ?,
                last_activated_at = ?,
                mention_count = ?,
                metadata = ?
            WHERE id = ?
            """,
            (
                profile["organization_name"],
                profile["organization_name"],
                now,
                now,
                int(mention_count or 0) + 1,
                json.dumps(metadata, ensure_ascii=True),
                entity_id,
            ),
        )
        return True

    entity_id = stable_id("orgmem", profile["org_id"], profile["organization_name"]) 
    cursor.execute(
        """
        INSERT INTO entities (
            id, name, type, canonical_name, first_seen_at, last_seen_at,
            mention_count, source_block_id, metadata, subtype, last_activated_at
        ) VALUES (?, ?, 'organization', ?, ?, ?, 1, NULL, ?, 'org_profile_projection', ?)
        """,
        (
            entity_id,
            profile["organization_name"],
            profile["organization_name"],
            now,
            now,
            json.dumps(metadata, ensure_ascii=True),
            now,
        ),
    )
    return True


def atomic_write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically and verify it is parseable."""

    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True)
    tmp.write_text(data + "\n", encoding="utf-8")
    try:
        _ = json.loads(tmp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"State verification failed for {tmp}: {exc}") from exc
    tmp.replace(path)


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    """Append rows to JSONL file and verify line count increase."""

    if not rows:
        return 0
    before = 0
    if path.exists():
        before = sum(1 for _ in path.open("r", encoding="utf-8"))

    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")

    after = sum(1 for _ in path.open("r", encoding="utf-8"))
    expected = before + len(rows)
    if after != expected:
        raise RuntimeError(
            f"State verification failed for {path}: expected {expected} lines, found {after}"
        )
    return len(rows)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""

    parser = argparse.ArgumentParser(description="Org profile enrichment backfill")
    parser.add_argument("--meetings-root", default="/home/workspace/Personal/Meetings")
    parser.add_argument("--canonical-path", default="/home/workspace/N5/data/org_profiles_canonical.json")
    parser.add_argument("--deltas-path", default="/home/workspace/N5/data/org_profile_deltas.jsonl")
    parser.add_argument("--merge-audit-path", default="/home/workspace/N5/data/org_profile_merge_audit.jsonl")
    parser.add_argument(
        "--semantic-projection-path",
        default="/home/workspace/N5/data/org_profile_semantic_projection.jsonl",
    )
    parser.add_argument(
        "--validation-report",
        default="/home/workspace/N5/builds/relationship-intelligence-os/artifacts/org-profile-backfill-validation-report.json",
    )
    parser.add_argument("--brain-db", default="/home/workspace/N5/cognition/brain.db")
    parser.add_argument("--batch-size", type=int, default=150)
    parser.add_argument("--batch-index", type=int, default=0)
    parser.add_argument("--max-meetings", type=int, default=0)
    parser.add_argument("--project-semantic-memory", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Fail if any meeting parse errors occur")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    """Main execution path with explicit error handling and exit codes."""

    parser = build_arg_parser()
    args = parser.parse_args()

    meetings_root = Path(args.meetings_root)
    canonical_path = Path(args.canonical_path)
    deltas_path = Path(args.deltas_path)
    merge_audit_path = Path(args.merge_audit_path)
    projection_path = Path(args.semantic_projection_path)
    validation_report = Path(args.validation_report)

    stats = {
        "started_at": utc_now_iso(),
        "mode": "dry_run" if args.dry_run else "apply",
        "meetings_discovered": 0,
        "meetings_in_batch": 0,
        "meetings_with_orgs": 0,
        "orgs_unique": 0,
        "deltas_extracted": 0,
        "deltas_by_type": {},
        "merge_outcomes": Counter(),
        "errors": [],
        "unresolved_conflicts": 0,
        "semantic_entities_upserted": 0,
        "batch": {
            "batch_size": args.batch_size,
            "batch_index": args.batch_index,
        },
    }

    try:
        if args.batch_size <= 0:
            raise ValueError("--batch-size must be > 0")
        if args.batch_index < 0:
            raise ValueError("--batch-index must be >= 0")

        meeting_dirs = iter_meeting_dirs(meetings_root)
        stats["meetings_discovered"] = len(meeting_dirs)

        start = args.batch_index * args.batch_size
        end = start + args.batch_size
        selected = meeting_dirs[start:end]
        if args.max_meetings > 0:
            selected = selected[: args.max_meetings]

        stats["meetings_in_batch"] = len(selected)
        log("INFO", f"Discovered {len(meeting_dirs)} meeting dirs; processing batch slice [{start}:{end})")

        profiles = load_canonical_profiles(canonical_path)
        existing_delta_ids = load_existing_jsonl_ids(deltas_path, "delta_id")

        delta_rows_to_append: list[dict[str, Any]] = []
        merge_rows_to_append: list[dict[str, Any]] = []
        projection_rows_to_append: list[dict[str, Any]] = []

        touched_org_ids: set[str] = set()
        unique_orgs_seen: set[str] = set()

        for meeting_dir in selected:
            try:
                orgs = extract_organizations(meeting_dir)
                if not orgs:
                    continue

                stats["meetings_with_orgs"] += 1
                meeting_id = infer_meeting_id(meeting_dir)

                for org_name in sorted(orgs):
                    unique_orgs_seen.add(org_name)
                    org_id = stable_id("org", org_name.lower())
                    profile = ensure_profile(org_id, org_name, profiles)

                    for block_type, prefix in BLOCK_FILE_PREFIXES.items():
                        for block_file in sorted(meeting_dir.glob(f"{prefix}*.md")):
                            deltas = extract_deltas_from_block(
                                org_name=org_name,
                                org_id=org_id,
                                meeting_id=meeting_id,
                                meeting_dir=meeting_dir,
                                block_file=block_file,
                                block_type=block_type,
                            )

                            for delta in deltas:
                                if delta.delta_id in existing_delta_ids:
                                    continue

                                outcome = merge_delta_into_profile(delta, profile, merge_rows_to_append)
                                stats["merge_outcomes"][outcome] += 1
                                if outcome != "duplicate_skipped":
                                    delta_rows_to_append.append(delta.as_dict())
                                    existing_delta_ids.add(delta.delta_id)
                                    touched_org_ids.add(org_id)
                                    stats["deltas_extracted"] += 1

                
            except (ValueError, OSError, json.JSONDecodeError) as exc:
                err = f"{meeting_dir}: {exc}"
                stats["errors"].append(err)
                log("ERROR", err)
                if args.strict:
                    raise

        stats["orgs_unique"] = len(unique_orgs_seen)

        delta_type_counter = Counter(row["delta_type"] for row in delta_rows_to_append)
        stats["deltas_by_type"] = dict(sorted(delta_type_counter.items()))

        if not args.dry_run:
            canonical_path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(canonical_path, profiles)
            append_jsonl(deltas_path, delta_rows_to_append)
            append_jsonl(merge_audit_path, merge_rows_to_append)

            for org_id in sorted(touched_org_ids):
                profile = profiles[org_id]
                projection_row = {
                    "projection_id": stable_id("orgproj", org_id, profile.get("updated_at", "")),
                    "org_id": org_id,
                    "organization_name": profile["organization_name"],
                    "summary": summarize_projection(profile),
                    "confidence_score": profile.get("confidence_score", 0.0),
                    "updated_at": profile.get("updated_at"),
                    "provenance": {
                        "source": "org_profile_backfill",
                        "generated_at": utc_now_iso(),
                    },
                }
                projection_rows_to_append.append(projection_row)

            append_jsonl(projection_path, projection_rows_to_append)

            if args.project_semantic_memory and projection_rows_to_append:
                with sqlite3.connect(args.brain_db) as conn:
                    for org_id in sorted(touched_org_ids):
                        if upsert_semantic_entity(conn, profiles[org_id]):
                            stats["semantic_entities_upserted"] += 1
                    conn.commit()

            reloaded = load_canonical_profiles(canonical_path)
            for org_id in touched_org_ids:
                if org_id not in reloaded:
                    raise RuntimeError(f"State verification failed: missing org_id {org_id} after write")

        stats["unresolved_conflicts"] = sum(
            len(profile.get("unresolved_conflicts", []))
            for profile in profiles.values()
        )

        total_meetings = max(1, stats["meetings_in_batch"])
        stats["error_rate"] = round(len(stats["errors"]) / total_meetings, 4)
        stats["completed_at"] = utc_now_iso()

        validation_report.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(validation_report, stats)

        log(
            "INFO",
            (
                f"Batch complete: meetings={stats['meetings_in_batch']}, orgs={stats['orgs_unique']}, "
                f"deltas={stats['deltas_extracted']}, conflicts={stats['unresolved_conflicts']}, "
                f"errors={len(stats['errors'])}, dry_run={args.dry_run}"
            ),
        )

        if args.strict and stats["errors"]:
            return 1
        return 0

    except (RuntimeError, ValueError, sqlite3.Error) as exc:
        log("ERROR", f"Backfill failed: {exc}")
        try:
            failure_payload = {
                "started_at": stats.get("started_at"),
                "failed_at": utc_now_iso(),
                "error": str(exc),
                "partial_stats": stats,
            }
            validation_report.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(validation_report, failure_payload)
        except OSError:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
