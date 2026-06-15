#!/usr/bin/env python3
"""Meeting closeout memory router (v2: D1.1 Routing Contract).

Selective semantic-memory routing for completed meetings.

Eligibility gate → extracted artifacts first → raw block fallback → manifest + audit.

Only promotes durable memory candidates (positions, frameworks, decision rationale,
strategic insights, relationship memories, operating constraints). Tactical/transient
content is explicitly skipped.
"""

import json
import logging
import subprocess
from datetime import datetime, UTC
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_WORKSPACE = Path("/home/workspace")
ROUTER_VERSION = "2.0"

WISDOM_BLOCKS = {
    "B32": "THOUGHT_PROVOKING_IDEAS",
    "B33": "DECISION_RATIONALE",
    "B36": "STRATEGIC_MARKET_INSIGHTS",
    "B37": "FRAMEWORKS_MENTAL_MODELS",
    "B38": "NARRATIVE_FRAMES",
}

CANDIDATE_TYPES = {
    "position", "framework", "decision_rationale",
    "strategic_insight", "relationship_memory", "operating_constraint",
    "narrative_frame",
}

POSITION_CANDIDATES_PATH = _WORKSPACE / "N5" / "data" / "position_candidates.jsonl"
B32_PROCESSED_PATH = _WORKSPACE / "N5" / "data" / "b32_processed.jsonl"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _check_eligibility(meeting_path: Path, manifest: dict) -> dict:
    """D1.1 Section 1: Eligibility gate."""
    status = manifest.get("status", "")
    eligible = True
    reason = None

    if status not in {"complete", "processed"}:
        eligible = False
        reason = f"status_not_complete (status={status})"
    elif status == "partial":
        eligible = False
        reason = "partial_meeting"
    elif manifest.get("closeout", {}).get("memory_routing", {}).get("outcome") == "succeeded":
        eligible = False
        reason = "already_routed"

    return {
        "eligible": eligible,
        "status_seen": status,
        "partial_meeting": status == "partial",
        "hitl_pending": bool(manifest.get("hitl_pending")),
        "reason": reason,
    }


def _find_extracted_artifacts(meeting_path: Path) -> list[dict]:
    """Find extracted artifacts from the wisdom extraction pipeline.

    Checks position_candidates.jsonl for entries sourced from this meeting.
    Matches on source_meeting, source_file, or source fields containing the meeting folder name.
    """
    artifacts = []
    meeting_name = meeting_path.name

    if POSITION_CANDIDATES_PATH.exists():
        try:
            for line in POSITION_CANDIDATES_PATH.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    candidate = json.loads(line)
                    # Check all possible source fields
                    source_meeting = candidate.get("source_meeting", "")
                    source_file = candidate.get("source_file", "")
                    source = candidate.get("source", "")
                    source_block = candidate.get("source_block", "")

                    # Match if any source field contains the meeting folder name
                    all_sources = f"{source_meeting} {source_file} {source} {source_block}"
                    if meeting_name in all_sources:
                        artifacts.append({
                            "type": candidate.get("type", "position"),
                            "title": (candidate.get("insight", "") or candidate.get("title", ""))[:120],
                            "source_ref": source_meeting or source_file or source or meeting_name,
                            "status": candidate.get("status", "pending"),
                            "score": candidate.get("score"),
                        })
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.warning(f"Could not read position candidates: {e}")

    return artifacts


def _find_wisdom_blocks(meeting_path: Path) -> list[str]:
    """Find which wisdom block files exist in the meeting folder."""
    found = []
    for block_code in WISDOM_BLOCKS:
        candidates = list(meeting_path.glob(f"{block_code}*.md"))
        if candidates:
            found.append(block_code)
    return found


def _run_extraction(meeting_path: Path) -> dict:
    """Run the B32 position extractor on wisdom blocks.

    Returns extraction result summary.
    """
    extractor = str(_WORKSPACE / "N5" / "scripts" / "b32_position_extractor.py")
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(_WORKSPACE)

    extracted = []
    failed = []

    for block_code, block_suffix in WISDOM_BLOCKS.items():
        block_files = list(meeting_path.glob(f"{block_code}*.md"))
        if not block_files:
            continue

        for block_file in block_files:
            logger.info(f"  Extracting from {block_file.name}")
            try:
                result = subprocess.run(
                    ["python3", extractor, "extract", str(block_file), "--auto-promote"],
                    capture_output=True, text=True, timeout=120, env=env,
                )
                if result.returncode == 0:
                    extracted.append(block_code)
                    logger.info(f"    ✓ {block_code} extracted")
                else:
                    failed.append({"block": block_code, "error": result.stderr[:200]})
                    logger.warning(f"    {block_code} extraction returned {result.returncode}")
            except Exception as e:
                failed.append({"block": block_code, "error": str(e)})
                logger.warning(f"    {block_code} extraction failed: {e}")

    return {
        "extracted": extracted,
        "failed": failed,
    }


def _score_candidate(candidate: dict) -> int:
    """D1.1 Section 5: Score a candidate on durability/reusability/specificity/evidence/novelty.

    Each dimension 0-2, threshold >= 7 to promote.
    Uses the extractor's own score if available, otherwise estimates.
    """
    if candidate.get("score") is not None:
        return candidate["score"]

    score = 0
    ctype = candidate.get("type", "")

    # Durability: positions and frameworks are inherently durable
    if ctype in {"position", "framework", "operating_constraint"}:
        score += 2
    elif ctype in {"strategic_insight", "decision_rationale"}:
        score += 1
    else:
        score += 1

    # Reusability: anything with a clear title is more reusable
    title = candidate.get("title", "")
    if len(title) > 20:
        score += 2
    elif len(title) > 5:
        score += 1

    # Specificity: extracted artifacts are already filtered
    score += 2

    # Evidence quality: if from extractor, evidence is good
    if candidate.get("source_ref"):
        score += 2
    else:
        score += 1

    # Novelty: assume novel if extracted (dedup happens elsewhere)
    score += 1

    return min(score, 10)


def route_meeting_memory(meeting_path: Path, dry_run: bool = False) -> dict:
    """Route meeting memory per D1.1 contract.

    Steps:
    1. Eligibility gate
    2. Run extraction on wisdom blocks
    3. Find extracted artifacts
    4. Score and classify (promoted vs skipped)
    5. Write manifest memory_routing section
    6. Write audit artifact
    """
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        return {"success": False, "error": "manifest_missing", "path": str(meeting_path)}

    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as e:
        return {"success": False, "error": f"manifest_unreadable: {e}", "path": str(meeting_path)}

    # Step 1: Eligibility gate
    eligibility = _check_eligibility(meeting_path, manifest)
    if not eligibility["eligible"]:
        # Write skipped outcome to manifest
        mr = {
            "outcome": "skipped",
            "reason": eligibility["reason"],
            "evaluated_at": _timestamp(),
            "router_version": ROUTER_VERSION,
            "eligibility": eligibility,
        }
        manifest.setdefault("closeout", {})["memory_routing"] = mr
        if not dry_run:
            manifest_path.write_text(json.dumps(manifest, indent=2))
        return {
            "success": True,
            "outcome": "skipped",
            "reason": eligibility["reason"],
            "path": str(meeting_path),
        }

    if dry_run:
        wisdom_blocks = _find_wisdom_blocks(meeting_path)
        return {
            "success": True,
            "dry_run": True,
            "path": str(meeting_path),
            "wisdom_blocks_found": wisdom_blocks,
            "would_route": True,
        }

    # Step 2: Run extraction on wisdom blocks
    extraction_result = _run_extraction(meeting_path)

    # Step 3: Find extracted artifacts (includes newly extracted ones)
    extracted_artifacts = _find_extracted_artifacts(meeting_path)

    # Determine evidence source
    wisdom_blocks_present = _find_wisdom_blocks(meeting_path)
    if extracted_artifacts:
        evidence_source = "extracted_only"
    elif wisdom_blocks_present:
        evidence_source = "raw_block_fallback"
    else:
        evidence_source = "none"

    # Step 4: Score and classify
    promoted_items = []
    skipped_items = []
    item_counter = 0

    for artifact in extracted_artifacts:
        item_counter += 1
        score = _score_candidate(artifact)
        item_id = f"mr_{item_counter:03d}"

        if score >= 7:
            promoted_items.append({
                "item_id": item_id,
                "type": artifact.get("type", "position"),
                "title": artifact.get("title", ""),
                "source_refs": [artifact.get("source_ref", "")],
                "evidence_source": evidence_source,
                "score": score,
                "why_promoted": f"Score {score}/10 meets threshold; durable {artifact.get('type', 'position')} candidate",
            })
        elif score >= 5:
            skipped_items.append({
                "item_id": item_id,
                "type": artifact.get("type", "position"),
                "source_refs": [artifact.get("source_ref", "")],
                "why_skipped": f"Borderline score {score}/10; below promotion threshold",
            })
        else:
            skipped_items.append({
                "item_id": item_id,
                "type": artifact.get("type", "position"),
                "source_refs": [artifact.get("source_ref", "")],
                "why_skipped": f"Low score {score}/10",
            })

    evaluated_at = _timestamp()

    # Step 5: Write manifest memory_routing section
    mr = {
        "outcome": "succeeded",
        "reason": None,
        "evaluated_at": evaluated_at,
        "router_version": ROUTER_VERSION,
        "eligibility": eligibility,
        "inputs": {
            "preferred_source": "extracted_artifacts",
            "evidence_source": evidence_source,
            "extracted_artifacts_considered": [a.get("source_ref", "") for a in extracted_artifacts],
            "raw_blocks_considered": wisdom_blocks_present if evidence_source in {"raw_block_fallback", "mixed"} else [],
            "raw_block_fallback_used": evidence_source in {"raw_block_fallback", "mixed"},
        },
        "extraction": {
            "blocks_extracted": extraction_result.get("extracted", []),
            "blocks_failed": extraction_result.get("failed", []),
        },
        "promoted_items": promoted_items,
        "skipped_items": skipped_items,
        "counts": {
            "evaluated": len(extracted_artifacts),
            "promoted": len(promoted_items),
            "skipped": len(skipped_items),
        },
        "audit_artifact": "memory-routing-audit.json",
        "errors": [],
    }

    # Also keep backward compat fields for closeout path
    mr["success"] = True
    mr["routed_at"] = evaluated_at

    manifest.setdefault("closeout", {})["memory_routing"] = mr
    manifest_path.write_text(json.dumps(manifest, indent=2))

    # Step 6: Write audit artifact
    try:
        audit = {
            "meeting_id": meeting_path.name,
            "evaluated_at": evaluated_at,
            "router_version": ROUTER_VERSION,
            "evidence_source": evidence_source,
            "extraction_summary": extraction_result,
            "promoted": promoted_items,
            "skipped": skipped_items,
            "counts": mr["counts"],
        }
        (meeting_path / "memory-routing-audit.json").write_text(json.dumps(audit, indent=2))
    except Exception as e:
        logger.warning(f"  Could not write memory routing audit: {e}")

    logger.info(
        f"  Memory routing complete: {len(promoted_items)} promoted, "
        f"{len(skipped_items)} skipped ({evidence_source})"
    )

    return {
        "success": True,
        "outcome": "succeeded",
        "path": str(meeting_path),
        "routed_at": evaluated_at,
        "counts": mr["counts"],
        "evidence_source": evidence_source,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Route completed meeting outputs into memory pipeline (D1.1 contract)")
    parser.add_argument("meeting", help="Meeting folder path")
    parser.add_argument("--dry-run", action="store_true", help="Preview without mutating manifest")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = route_meeting_memory(Path(args.meeting), dry_run=args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result)
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
