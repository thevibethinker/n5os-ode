#!/usr/bin/env python3
"""
Meeting Ingestion - Process Script

Canonical processor for future meetings. Gated meetings now flow only through
S-shape generation.

Usage:
    python3 process.py [meeting_path] [--dry-run]
"""

import sys
import json
import os
import logging
from pathlib import Path
from datetime import datetime, UTC

# --- D1 sys.path injection for paths.py ---
from pathlib import Path as _D1Path
sys.path.insert(0, str(_D1Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

_WORKSPACE = Path(__file__).resolve().parent.parent.parent.parent
from paths import ACTIVE_DIR as INBOX  # noqa: E402


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _read_manifest(manifest_path: Path) -> dict:
    return json.loads(manifest_path.read_text())


def _write_manifest(manifest_path: Path, manifest: dict) -> None:
    manifest_path.write_text(json.dumps(manifest, indent=2))


def _append_status(manifest: dict, status: str) -> None:
    history = manifest.setdefault("status_history", [])
    if history and history[-1].get("status") == status:
        return
    history.append({"status": status, "at": _timestamp()})


def _set_processed_status(manifest: dict) -> None:
    manifest["status"] = "processed"
    manifest.setdefault("timestamps", {})["processed_at"] = _timestamp()
    _append_status(manifest, "processed")


def _mark_closeout_error(manifest_path: Path, phase: str, error: str) -> None:
    manifest = _read_manifest(manifest_path)
    closeout = manifest.setdefault("closeout", {})
    closeout[phase] = {
        "success": False,
        "error": error,
        "at": _timestamp(),
    }
    _write_manifest(manifest_path, manifest)


def _run_complete_closeout(meeting_path: Path, manifest_path: Path) -> tuple[Path, dict]:
    from memory_router import route_meeting_memory
    from title_normalizer import normalize_title
    from archive import archive_meeting_path

    manifest = _read_manifest(manifest_path)
    closeout = manifest.setdefault("closeout", {})

    if closeout.get("archival", {}).get("success"):
        logger.info("  Closeout already completed; skipping duplicate archive")
        return meeting_path, {
            "memory_routing": closeout.get("memory_routing", {}),
            "title_normalization": closeout.get("title_normalization", {}),
            "archival": closeout.get("archival", {}),
            "skipped": "already_closed",
        }

    extraction_at = _timestamp()
    closeout["extraction"] = {
        "success": True,
        "completed_at": extraction_at,
        "method": "trigger_wisdom_extraction",
    }
    _write_manifest(manifest_path, manifest)

    memory_result = route_meeting_memory(meeting_path)
    # Router writes its own manifest section; re-read to pick it up
    manifest = _read_manifest(manifest_path)
    closeout = manifest.setdefault("closeout", {})

    if not memory_result.get("success"):
        logger.warning("  Memory routing failed; skipping rename/archive")
        return meeting_path, {
            "memory_routing": closeout.get("memory_routing", {}),
            "archival_skipped": "memory_routing_failed",
        }

    title_result = normalize_title(meeting_path, dry_run=False, rename=False)
    updated_path = meeting_path
    if title_result.get("folder_renamed") and title_result.get("new_folder_name"):
        updated_path = meeting_path.parent / title_result["new_folder_name"]
        manifest_path = updated_path / "manifest.json"

    manifest = _read_manifest(manifest_path)
    closeout = manifest.setdefault("closeout", {})
    closeout["title_normalization"] = {
        "success": not bool(title_result.get("error")),
        "new_title": title_result.get("new_title"),
        "folder_renamed": bool(title_result.get("folder_renamed")),
        "new_folder_name": title_result.get("new_folder_name"),
        "locked_name": title_result.get("locked_name"),
        "rename_skipped": title_result.get("rename_skipped"),
        "error": title_result.get("error"),
    }
    _write_manifest(manifest_path, manifest)

    archive_result = archive_meeting_path(updated_path, dry_run=False)
    archive_manifest_path = Path(archive_result.get("archived_path", updated_path)) / "manifest.json" if archive_result.get("success") else manifest_path

    if archive_result.get("success"):
        archived_manifest = _read_manifest(archive_manifest_path)
        archived_closeout = archived_manifest.setdefault("closeout", {})
        archived_closeout["archival"] = {
            "success": True,
            "archived_path": archive_result.get("archived_path") or archive_result.get("to"),
            "week": archive_result.get("week"),
            "subfolder": archive_result.get("subfolder"),
            "merged": bool(archive_result.get("merged")),
        }
        _write_manifest(archive_manifest_path, archived_manifest)
    else:
        _mark_closeout_error(manifest_path, "archival", archive_result.get("error", "archive_failed"))

    return Path(archive_result.get("archived_path", updated_path)), {
        "memory_routing": memory_result,
        "title_normalization": title_result,
        "archival": archive_result,
    }


def resolve_generic_speakers(transcript: str, manifest: dict) -> tuple[str, dict]:
    """Use LLM to resolve generic speaker labels (Speaker 1, Speaker 2) to real names.

    Returns (resolved_transcript, speaker_mapping).
    If no generic speakers found, returns the original transcript unchanged.
    """
    import re as _re

    # Check for generic speaker patterns
    generic_pattern = _re.compile(r'^(Speaker\s*\d+)\s*:', _re.MULTILINE)
    generic_matches = generic_pattern.findall(transcript)

    if len(set(generic_matches)) < 2:
        return transcript, {}

    # Collect known participant names from manifest
    participants_raw = manifest.get("participants", {})
    known_names = []
    if isinstance(participants_raw, dict):
        for p in participants_raw.get("identified", []):
            if isinstance(p, dict) and p.get("name"):
                known_names.append(p["name"])
        for p in participants_raw.get("unidentified", []):
            if isinstance(p, dict) and p.get("name"):
                known_names.append(p["name"])
            elif isinstance(p, str):
                known_names.append(p)
    elif isinstance(participants_raw, list):
        for p in participants_raw:
            if isinstance(p, dict) and p.get("name"):
                known_names.append(p["name"])
            elif isinstance(p, str):
                known_names.append(p)

    if not known_names:
        # No participant data to resolve against
        return transcript, {}

    unique_generics = sorted(set(generic_matches))
    logger.info(f"  Resolving {len(unique_generics)} generic speakers via LLM: {unique_generics}")
    logger.info(f"  Known participants: {known_names}")

    # Take a sample of the transcript for each speaker to help identification
    speaker_samples = {}
    for label in unique_generics:
        pattern = _re.compile(r'^' + _re.escape(label) + r':\s*(.+)', _re.MULTILINE)
        lines = pattern.findall(transcript)
        speaker_samples[label] = lines[:5]  # First 5 utterances

    samples_text = ""
    for label, lines in speaker_samples.items():
        samples_text += f"\n{label}:\n"
        for line in lines:
            samples_text += f"  - \"{line[:150]}\"\n"

    prompt = f"""Map generic speaker labels to real participant names based on transcript content.

Known participants for this meeting: {', '.join(known_names)}

Generic speakers found in transcript with sample utterances:
{samples_text}

Rules:
- The primary user / host may appear as "V" or another host label in the transcript
- Match speakers to known participants based on content clues (introducing themselves, being addressed by name, topic expertise, speaking patterns)
- If a speaker cannot be confidently matched, keep the generic label
- Return ONLY a JSON object mapping generic labels to real names

Example: {{"Speaker 1": "V", "Speaker 2": "Manav Kothari"}}

Respond with ONLY the JSON mapping."""

    try:
        result = call_zo_api(prompt)
        # Parse the mapping
        clean = result.strip()
        if clean.startswith('```'):
            lines = clean.split('\n')
            clean = '\n'.join(l for l in lines if not l.startswith('```'))

        mapping = json.loads(clean)

        if not isinstance(mapping, dict) or not mapping:
            return transcript, {}

        # Apply the mapping to the transcript
        resolved = transcript
        for generic_label, real_name in mapping.items():
            if real_name and real_name != generic_label:
                resolved = resolved.replace(f"{generic_label}:", f"{real_name}:")

        logger.info(f"  Speaker resolution: {mapping}")
        return resolved, mapping

    except Exception as e:
        logger.warning(f"  Speaker resolution failed (non-fatal): {e}")
        return transcript, {}


def trigger_wisdom_extraction(meeting_path: Path):
    """Post-processing hook: extract position/wisdom candidates from idea-system blocks.

    Scans for B32 (worldview), B36 (strategic), B37 (frameworks), B38 (narrative)
    and runs the extractor on each found block file.
    """
    import subprocess

    WISDOM_BLOCKS = {
        "B32": "THOUGHT_PROVOKING_IDEAS",
        "B36": "STRATEGIC_MARKET_INSIGHTS",
        "B37": "FRAMEWORKS_MENTAL_MODELS",
        "B38": "NARRATIVE_FRAMES",
    }

    env = os.environ.copy()
    env["PYTHONPATH"] = str(_WORKSPACE)
    extractor = str(_WORKSPACE / "N5" / "scripts" / "b32_position_extractor.py")

    for block_code, block_suffix in WISDOM_BLOCKS.items():
        # Match files like B36_STRATEGIC_MARKET_INSIGHTS.md
        candidates = list(meeting_path.glob(f"{block_code}*.md"))
        if not candidates:
            continue

        for block_file in candidates:
            logger.info(f"  Triggering {block_code} extraction: {block_file.name}")
            try:
                result = subprocess.run(
                    ["python3", extractor, "extract", str(block_file), "--auto-promote"],
                    capture_output=True, text=True, timeout=120, env=env
                )
                if result.returncode == 0:
                    logger.info(f"  ✓ {block_code} positions extracted")
                else:
                    logger.warning(f"  {block_code} extraction returned {result.returncode}: {result.stderr[:200]}")
            except Exception as e:
                logger.warning(f"  {block_code} extraction failed (non-fatal): {e}")


def resolve_meeting_type(manifest: dict) -> str:
    """Resolve canonical meeting type across v3/legacy/enrichment fields."""
    crm_type = (manifest.get("crm_enrichment", {}) or {}).get("classification")
    if isinstance(crm_type, str) and crm_type.lower() in {"internal", "external"}:
        return crm_type.lower()

    nested_type = (manifest.get("meeting", {}) or {}).get("type")
    if isinstance(nested_type, str) and nested_type.lower() in {"internal", "external"}:
        return nested_type.lower()

    legacy_type = manifest.get("meeting_type")
    if isinstance(legacy_type, str) and legacy_type.lower() in {"internal", "external"}:
        return legacy_type.lower()

    return "external"
def process_meeting(meeting_path: Path, dry_run: bool = False) -> dict:
    """Process a single meeting folder through canonical S-shape generation only."""
    logger.info(f"Processing: {meeting_path.name}")

    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        return {"error": "no manifest.json - run stage first", "path": str(meeting_path)}

    manifest = _read_manifest(manifest_path)
    closeout_result = None

    if manifest.get("closeout", {}).get("archival", {}).get("success"):
        logger.info("  Already archived/closed, skipping")
        return {"status": "already_closed", "path": str(meeting_path)}

    if manifest.get("status") == "complete":
        logger.info(f"  Already complete, skipping")
        return {"status": "already_complete", "path": str(meeting_path)}

    transcript_file = meeting_path / manifest.get("transcript_file", "transcript.md")
    if not transcript_file.exists():
        for pattern in ["*.md", "*.txt"]:
            files = list(meeting_path.glob(pattern))
            if files:
                transcript_file = files[0]
                break

    if not transcript_file.exists():
        return {"error": "no transcript found", "path": str(meeting_path)}

    transcript = transcript_file.read_text()
    if len(transcript.strip()) < 100:
        return {"error": f"transcript too short ({len(transcript)} chars)", "path": str(meeting_path)}

    # LLM-based speaker resolution: map "Speaker 1", "Speaker 2" to real names
    transcript, speaker_mapping = resolve_generic_speakers(transcript, manifest)
    if speaker_mapping:
        manifest["speaker_resolution"] = {
            "mapping": speaker_mapping,
            "resolved_at": _timestamp(),
            "method": "llm"
        }
        _write_manifest(manifest_path, manifest)

    from run_shapes import generate_shapes
    logger.info("  Selection method: shape_router_v1")
    if dry_run:
        shape_preview = generate_shapes(meeting_path, manifest, transcript, dry_run=True)
        return {
            "dry_run": True,
            "path": str(meeting_path),
            "shapes": shape_preview.get("shape_codes", []),
            "selection_metadata": shape_preview.get("selection", {}),
        }

    shape_result = generate_shapes(meeting_path, manifest, transcript, dry_run=False)
    result = {
        "path": str(meeting_path),
        "shapes_generated": shape_result.get("shapes_generated", []),
        "shapes_failed": shape_result.get("shapes_failed", []),
        "selection_metadata": shape_result.get("selection_metadata", {}),
    }

    manifest = _read_manifest(manifest_path)
    closeout_result = None
    if manifest.get("status") == "processed":
        meeting_path, closeout_result = _run_complete_closeout(meeting_path, manifest_path)
        manifest_path = meeting_path / "manifest.json"
    elif manifest.get("status") == "partial":
        partial_manifest = _read_manifest(manifest_path)
        partial_manifest.setdefault("closeout", {})["archival"] = {
            "success": False,
            "skipped": "partial_meeting",
            "at": _timestamp(),
        }
        _write_manifest(manifest_path, partial_manifest)

    logger.info(f"  Complete: {len(result['shapes_generated'])} generated, {len(result['shapes_failed'])} failed")
    if closeout_result:
        result["closeout"] = closeout_result
    result["path"] = str(meeting_path)
    return result


def process_queue(batch_size: int = 5, dry_run: bool = False) -> dict:
    """Process all staged meetings in queue through canonical S-shape generation."""
    logger.info(f"Processing queue (batch_size={batch_size})")

    if not INBOX.exists():
        return {"error": "inbox not found"}

    candidates = []
    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith(('.', '_')):
            continue

        manifest_path = folder / "manifest.json"
        if not manifest_path.exists():
            continue

        try:
            manifest = json.loads(manifest_path.read_text())
            status = manifest.get("status")
            if status in ["staged", "processing"]:
                candidates.append(folder)
        except Exception:
            continue

    logger.info(f"Found {len(candidates)} meetings ready for processing")

    results = {
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "meetings": []
    }

    for folder in candidates[:batch_size]:
        try:
            result = process_meeting(folder, dry_run=dry_run)
            results["meetings"].append(result)
            results["processed"] += 1

            if result.get("shapes_failed"):
                results["failed"] += 1
            else:
                results["succeeded"] += 1

        except Exception as e:
            logger.error(f"Error processing {folder.name}: {e}")
            results["meetings"].append({"path": str(folder), "error": str(e)})
            results["processed"] += 1
            results["failed"] += 1

    logger.info(f"Queue complete: {results['succeeded']}/{results['processed']} succeeded")
    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process meeting transcripts with canonical S-shape generation")
    parser.add_argument("meeting_path", nargs="?", help="Specific meeting folder")
    parser.add_argument("--batch-size", type=int, default=5, help="Max meetings from queue")
    parser.add_argument("--dry-run", action="store_true", help="Preview without processing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
        if not meeting_path.exists():
            print(f"Error: Path not found: {meeting_path}")
            return 1
        results = process_meeting(meeting_path, dry_run=args.dry_run)
    else:
        results = process_queue(batch_size=args.batch_size, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if "meetings" in results:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Queue Processing:")
            print(f"  Processed: {results['processed']}")
            print(f"  Succeeded: {results['succeeded']}")
            print(f"  Failed:    {results['failed']}")

            for m in results.get("meetings", []):
                meta = m.get("selection_metadata", {})
                method = meta.get("method", "unknown")
                print(f"\n  {m.get('path', 'unknown').split('/')[-1]}:")
                print(f"    Method: {method}")
                if meta.get("recipe"):
                    print(f"    Recipe: {meta['recipe']}")
                if m.get("shapes"):
                    print(f"    Shapes: {', '.join(m['shapes'])}")
        else:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Meeting Processed:")
            print(f"  Path: {results.get('path')}")

            meta = results.get("selection_metadata", {})
            if meta:
                print(f"  Selection Method: {meta.get('method', 'unknown')}")
                if meta.get("recipe"):
                    print(f"  Recipe: {meta['recipe']}")
                if meta.get("reasoning"):
                    print(f"  Selection Reasoning:")
                    for shape, reason in meta["reasoning"].items():
                        print(f"    {shape}: {reason}")

            if results.get('shapes_generated'):
                print(f"  Shapes Generated: {len(results['shapes_generated'])}")
            if results.get('shapes'):
                print(f"  Shapes to Generate: {', '.join(results['shapes'])}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
