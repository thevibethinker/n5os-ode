#!/usr/bin/env python3
"""
Meeting Ingestion Skill - Unified CLI v3

Single entry point for all meeting ingestion operations with v3 pipeline support.

Usage:
    # v3 Pipeline Commands (recommended)
    python3 meeting_cli.py ingest <path> [--dry-run]
    python3 meeting_cli.py identify <meeting> [--dry-run] 
    python3 meeting_cli.py gate <meeting> [--dry-run]
    python3 meeting_cli.py process <meeting> [--dry-run]
    python3 meeting_cli.py tick [--dry-run]

    # Legacy Commands (v2 compatibility) 
    python3 meeting_cli.py stage [--dry-run]
    python3 meeting_cli.py archive [--execute]
    python3 meeting_cli.py status
    python3 meeting_cli.py fix
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from paths import ACTIVE_DIR as INBOX  # noqa: E402
MEETINGS = Path("/home/workspace/Personal/Meetings")


def _source_type_and_id(manifest: dict) -> tuple[str, str]:
    """Normalize source metadata across v2/v3 manifest formats."""
    source = manifest.get("source") or {}
    if not isinstance(source, dict):
        return "", ""

    source_type = str(source.get("type") or source.get("format") or "").lower().strip()
    if not source_type:
        adapter = str(source.get("adapter", "")).lower()
        if "fathom" in adapter:
            source_type = "fathom"
        elif "fireflies" in adapter:
            source_type = "fireflies"

    if "fathom" in source_type:
        source_type = "fathom"
    elif "fireflies" in source_type:
        source_type = "fireflies"

    source_id = str(
        source.get("source_id")
        or source.get("recording_id")
        or source.get("transcript_id")
        or ""
    ).strip()
    return source_type, source_id


# === v3 Pipeline Commands ===

def cmd_ingest(args):
    """Ingest raw transcript into v3 manifest (raw → ingested)."""
    from ingest import TranscriptIngestor
    
    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path not found: {path}")
        return 1
    
    try:
        ingestor = TranscriptIngestor()
        
        if path.is_file():
            result = ingestor.ingest_file(str(path), dry_run=args.dry_run)
        else:
            result = ingestor.ingest_folder(str(path), dry_run=args.dry_run)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = result.get('status', 'unknown')
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Ingest: {status}")
            if result.get('meeting_folder'):
                print(f"  Meeting folder: {result['meeting_folder']}")
            if result.get('meeting_id'):
                print(f"  Meeting ID: {result['meeting_id']}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
        
        return 0
        
    except Exception as e:
        print(f"Error running ingest: {e}")
        return 1


def cmd_identify(args):
    """Run calendar triangulation + CRM enrichment for a meeting."""
    from calendar_match import match_meeting_to_calendar
    from crm_enricher import CRMEnricher
    
    meeting_path = Path(args.meeting)
    if not meeting_path.exists() or not meeting_path.is_dir():
        print(f"Error: Meeting folder not found: {meeting_path}")
        return 1
    
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: manifest.json not found in {meeting_path}")
        return 1
    
    try:
        results = {}
        
        # Step 1: Calendar matching
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Running calendar triangulation...")
        if not args.dry_run:
            manifest_data = json.loads(manifest_path.read_text())
            cal_result = match_meeting_to_calendar(manifest_data)
            if cal_result:
                results['calendar'] = cal_result
                print(f"  Calendar match: {cal_result.get('confidence', 'N/A')} confidence")
            else:
                results['calendar'] = {"event_id": None, "confidence": 0.0, "method": "none", "attendee_emails": []}
                print("  Calendar match: no match (0.0 confidence)")
        
        # Step 2: CRM enrichment  
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Running CRM enrichment...")
        if not args.dry_run:
            crm = CRMEnricher()
            crm_result = crm.enrich_meeting(str(meeting_path))
            results['crm'] = crm_result
            classification = crm_result.get('classification', 'unknown')
            print(f"  Meeting classification: {classification}")
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}✅ Identification complete")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def cmd_gate(args):
    """Run quality gate validation for a meeting."""
    from quality_gate import QualityGate
    
    meeting_path = Path(args.meeting)
    if not meeting_path.exists() or not meeting_path.is_dir():
        print(f"Error: Meeting folder not found: {meeting_path}")
        return 1
    
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: manifest.json not found in {meeting_path}")
        return 1
    
    try:
        if args.dry_run:
            print(f"[DRY RUN] Would run quality gate on {meeting_path}")
            return 0
        
        # Find transcript file
        transcript_path = None
        for fname in ["transcript.md", "transcript.txt"]:
            candidate = meeting_path / fname
            if candidate.exists():
                transcript_path = candidate
                break
        
        # Run quality gate
        gate = QualityGate()
        result = gate.execute(manifest_path, transcript_path)
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            passed = result.get('passed', False)
            score = result.get('score', 0.0)
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"\nQuality Gate: {status} (Score: {score:.2f})")
            
            if not passed:
                failed_checks = [check['name'] for check in result.get('checks', []) 
                               if not check.get('passed', False)]
                if failed_checks:
                    print(f"  Failed checks: {', '.join(failed_checks)}")
                
                if result.get('hitl_escalations'):
                    print(f"  ⚠️  {len(result['hitl_escalations'])} escalation(s) to HITL queue")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


def cmd_tick(args):
    """Process meetings in the queue through the full pipeline.

    With --auto-process: runs identify → gate → shape generation automatically.
    Without --auto-process: stops before shape generation (manual mode).
    """
    auto_process = getattr(args, 'auto_process', False)
    batch_size = getattr(args, 'batch_size', 10)
    target = getattr(args, 'target', None)
    skip_raw_intake = getattr(args, 'skip_raw_intake', False)

    try:
        results = {"processed": 0, "succeeded": 0, "failed": 0, "meetings": []}

        # If targeting a specific meeting, skip pre-step and queue scan
        if target:
            target_path = INBOX / target
            if not target_path.exists():
                print(f"Target meeting not found: {target}")
                return 1
            manifest_path = target_path / "manifest.json"
            if not manifest_path.exists():
                print(f"No manifest.json in {target}")
                return 1
            manifest = json.loads(manifest_path.read_text())
            status = manifest.get("status", "")
            if status not in ["ingested", "identified", "gated", "routed"]:
                print(f"Meeting {target} is at status '{status}', not processable")
                return 0
            meetings_to_process = [(target_path, status)]
            batch = meetings_to_process
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing target: {target} (status: {status})")
            if auto_process:
                print("  Mode: --auto-process (full pipeline including shape generation)")
            # Falls through to the main processing loop below.
        else:
            meetings_to_process = None  # Signal to do the normal scan

        # Pre-step: Ingest any raw transcript files sitting in Inbox root
        if meetings_to_process is None and not skip_raw_intake:
            if INBOX.exists():
                raw_files = [
                    f for f in INBOX.iterdir()
                    if f.is_file() and f.suffix in [".md", ".txt", ".jsonl"] and not f.name.startswith(".")
                ]
                if raw_files:
                    print(f"Found {len(raw_files)} raw transcript file(s) in Active queue root")
                    from ingest import TranscriptIngestor
                    ingestor = TranscriptIngestor()
                    for raw_file in raw_files:
                        try:
                            if args.dry_run:
                                print(f"  [DRY RUN] Would ingest: {raw_file.name}")
                            else:
                                result = ingestor.ingest_file(str(raw_file), dry_run=False)
                                ing_status = result.get('status', 'unknown')
                                target_path = result.get('folder_path') or result.get('existing_path') or 'unknown'
                                if ing_status in {'completed', 'duplicate_skipped', 'rejected'} and raw_file.exists():
                                    try:
                                        raw_file.unlink()
                                    except Exception as unlink_error:
                                        print(f"  ⚠️  Ingest succeeded but could not remove raw file {raw_file.name}: {unlink_error}")
                                print(f"  Ingested {raw_file.name} → {target_path} ({ing_status})")
                        except Exception as e:
                            print(f"  ❌ Failed to ingest {raw_file.name}: {e}")

        # Find meetings that need processing
        meetings_to_process = []

        if INBOX.exists():
            for item in INBOX.iterdir():
                if item.is_dir() and not item.name.startswith(('.', '_')):
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        try:
                            manifest = json.loads(manifest_path.read_text())
                            status = manifest.get("status", "")
                            review_status = manifest.get("review_status")
                            if status in ["ingested", "identified", "gated", "routed"] and review_status != "needs_review":
                                meetings_to_process.append((item, status))
                        except:
                            continue

        # D6: LIFO sort — newest first
        def _lifo_key(pair):
            item, _st = pair
            created_at = None
            mp = item / "manifest.json"
            if mp.exists():
                try:
                    created_at = json.loads(mp.read_text()).get("created_at")
                except Exception:
                    pass
            if created_at:
                return (str(created_at), item.name)
            print(f"[lifo-sort] fallback to mtime for {item.name} (no created_at)", file=sys.stderr)
            return (datetime.fromtimestamp(item.stat().st_mtime, tz=timezone.utc).isoformat(), item.name)
        meetings_to_process.sort(key=_lifo_key, reverse=True)

        if not meetings_to_process:
            print("No drainable meetings in queue ready for processing")
            return 0

        # Limit to batch size
        batch = meetings_to_process[:batch_size]
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(batch)}/{len(meetings_to_process)} meetings (batch_size={batch_size})")
        if auto_process:
            print("  Mode: --auto-process (full pipeline including shape generation)")

        for meeting_path, current_status in batch:
            print(f"\n--- {meeting_path.name} ---")
            print(f"  Current status: {current_status}")

            if args.dry_run:
                steps = []
                if current_status in ("ingested", "routed"):
                    steps = ["identify", "gate"]
                elif current_status == "identified":
                    steps = ["gate"]
                if auto_process:
                    steps.append("process (shape generation)")
                print(f"  Would run: {' → '.join(steps)}")
                results["processed"] += 1
                results["meetings"].append({"meeting": meeting_path.name, "status": "dry_run", "steps": steps})
                continue

            success = True
            meeting_result = {"meeting": meeting_path.name}

            # Step 1: Identify (if needed)
            if current_status in ("ingested", "routed"):
                print("  Running identification...")
                try:
                    from calendar_match import match_meeting_to_calendar
                    from crm_enricherer import CRMEnricher
                    manifest_data = json.loads((meeting_path / "manifest.json").read_text())
                    cal_result = match_meeting_to_calendar(manifest_data)
                    if not cal_result:
                        cal_result = {"event_id": None, "confidence": 0.0, "method": "none", "attendee_emails": []}
                    manifest_data["calendar_match"] = {k: cal_result.get(k) for k in ["event_id", "confidence", "method"] if k in cal_result}
                    (meeting_path / "manifest.json").write_text(json.dumps(manifest_data, indent=2))
                    crm = CRMEnricher()
                    crm.enrich_meeting(str(meeting_path))
                    print("    ✅ Identification complete")
                except Exception as e:
                    print(f"    ❌ Identification failed: {e}")
                    success = False

                # Step 1b: Title normalization (reads transcript to improve title + extract speakers)
                if success:
                    print("  Running title normalization...")
                    try:
                        from title_normalizer import normalize_title
                        title_result = normalize_title(meeting_path, dry_run=False, rename=True)
                        if "error" not in title_result:
                            old_t = title_result.get("original_title", "?")
                            new_t = title_result.get("new_title", "?")
                            speakers = title_result.get("speakers", [])
                            new_p = title_result.get("new_participants", 0)
                            print(f"    ✅ Title: '{old_t}' → '{new_t}'")
                            if speakers:
                                print(f"    ✅ Speakers: {', '.join(speakers)}")
                            if new_p > 0:
                                print(f"    ✅ {new_p} new participant(s) added")
                            # Update meeting_path if folder was renamed
                            if title_result.get("folder_renamed") and title_result.get("new_folder_name"):
                                meeting_path = meeting_path.parent / title_result["new_folder_name"]
                                print(f"    ✅ Folder renamed → {title_result['new_folder_name']}")
                        else:
                            print(f"    ⚠️  Title normalization skipped: {title_result['error']}")
                    except Exception as e:
                        print(f"    ⚠️  Title normalization failed (non-fatal): {e}")

                # Step 1c: Org classification
                if success:
                    print("  Running org classification...")
                    try:
                        from org_classifier import classify_and_update
                        org_result = classify_and_update(meeting_path)
                        if "error" not in org_result:
                            print(f"    ✅ Org: {org_result['org']} (confidence: {org_result['confidence']})")
                        else:
                            print(f"    ⚠️  Org classification skipped: {org_result['error']}")
                    except Exception as e:
                        print(f"    ⚠️  Org classification failed (non-fatal): {e}")

                # Update manifest status to identified
                if success:
                    try:
                        mf = json.loads((meeting_path / "manifest.json").read_text())
                        existing_status = mf.get("status")
                        processed_at = (mf.get("timestamps", {}) or {}).get("processed_at")
                        if processed_at or existing_status in {"gated", "processed", "partial", "failed", "archived", "completed", "complete"}:
                            print(f"    ⚠️  Leaving status as {existing_status or 'unknown'} (already progressed)")
                            current_status = existing_status or current_status
                        elif existing_status in {"ingested", "routed"}:
                            mf["status"] = "identified"
                            mf.setdefault("timestamps", {})["identified_at"] = datetime.now(timezone.utc).isoformat()
                            mf.setdefault("status_history", []).append({
                                "status": "identified",
                                "at": datetime.now(timezone.utc).isoformat(),
                            })
                            (meeting_path / "manifest.json").write_text(json.dumps(mf, indent=2))
                            current_status = "identified"
                        elif existing_status == "identified":
                            current_status = "identified"
                        else:
                            current_status = existing_status or current_status
                    except Exception as e:
                        print(f"    ⚠️  Status update failed: {e}")

            # Step 2: Quality gate (advisory — records score but doesn't block pipeline)
            if success and current_status in ["ingested", "identified"]:
                print("  Running quality gate...")
                try:
                    from quality_gate import QualityGate
                    transcript_path = None
                    for fname in ["transcript.md", "transcript.txt", "transcript.json"]:
                        candidate = meeting_path / fname
                        if candidate.exists():
                            transcript_path = candidate
                            break

                    mf_path = meeting_path / "manifest.json"
                    gate = QualityGate()
                    gate_result = gate.execute(mf_path, transcript_path)
                    score = gate_result.get('score', 0)
                    if gate_result.get('passed', False):
                        print(f"    ✅ Quality gate passed (score: {score:.2f})")
                    else:
                        hitl_count = len(gate_result.get('hitl_escalations', []))
                        print(f"    ⚠️  Quality gate flagged issues (score: {score:.2f}, {hitl_count} HITL items)")
                        print(f"    ℹ️  Continuing pipeline — HITL items queued for review")
                except Exception as e:
                    print(f"    ⚠️  Quality gate error (non-fatal): {e}")

            # Step 3: Shape generation (only with --auto-process)
            if success and auto_process:
                print("  Running shape generation...")
                try:
                    from process import process_meeting
                    proc_result = process_meeting(meeting_path, dry_run=False)
                    proc_status = proc_result.get('status', 'unknown')
                    shapes_gen = proc_result.get('shapes_generated', [])
                    shapes_failed = proc_result.get("shapes_failed", [])

                    if proc_result.get("error"):
                        print(f"    ❌ Shape generation failed: {proc_result['error']}")
                        success = False
                        meeting_result["process_error"] = proc_result["error"]
                    elif proc_status == "already_complete":
                        print("    ✅ Already complete (no new shapes needed)")
                        meeting_result["shapes_generated"] = []
                    elif proc_status in {"failed", "partial"} or shapes_failed:
                        print(f"    ❌ Shape generation incomplete (status={proc_status}, failed={len(shapes_failed)})")
                        success = False
                        meeting_result["shapes_generated"] = shapes_gen
                        meeting_result["shapes_failed"] = shapes_failed
                    else:
                        print(f"    ✅ Shapes generated: {len(shapes_gen)}")
                        for shape in shapes_gen:
                            print(f"      - {shape}")
                        meeting_result["shapes_generated"] = shapes_gen
                except Exception as e:
                    print(f"    ❌ Shape generation failed: {e}")
                    success = False
            elif success and not auto_process:
                print("  ⚠️  Shape processing requires --auto-process or manual run")
                print(f"    Use: meeting_cli.py process {meeting_path}")

            results["processed"] += 1
            if success:
                results["succeeded"] += 1
                meeting_result["status"] = "success"
            else:
                results["failed"] += 1
                meeting_result["status"] = "failed"
            results["meetings"].append(meeting_result)

        if not args.dry_run:
            print(f"\n{'=' * 40}")
            print(f"Tick complete: {results['succeeded']}/{results['processed']} succeeded, {results['failed']} failed")

        if getattr(args, 'json', False):
            print(json.dumps(results, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        return 1

    if not args.dry_run and results.get("failed", 0) > 0:
        return 1
    return 0


def cmd_process_all(args):
    """Process all queued meetings in parallel.

    Scans Inbox for meetings at ingested/identified/gated status,
    spawns parallel subprocesses to process each through the full pipeline.
    """
    import subprocess
    import time

    parallel = getattr(args, 'parallel', 3)
    do_archive = not getattr(args, 'no_archive', False)

    # Find all processable meetings
    meetings = []
    if INBOX.exists():
        for item in sorted(INBOX.iterdir()):
            if item.is_dir() and not item.name.startswith(('.', '_')):
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text())
                        status = manifest.get("status", "")
                        if status in ["ingested", "identified", "gated"]:
                            meetings.append((item.name, status))
                    except:
                        continue

    if not meetings:
        print("No meetings in queue ready for processing")
        return 0

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Found {len(meetings)} meetings to process")
    print(f"  Parallel workers: {parallel}")
    print(f"  Archive after: {'yes' if do_archive else 'no'}")
    print()

    for name, status in meetings:
        print(f"  {name:60s} [{status}]")

    if args.dry_run:
        print(f"\n[DRY RUN] Would process {len(meetings)} meetings with {parallel} parallel workers")
        return 0

    print(f"\nStarting processing...")
    cli_path = str(Path(__file__).resolve())

    active = {}  # pid -> (process, meeting_name, log_path)
    completed = []
    failed = []
    queue = list(meetings)

    while queue or active:
        # Launch new processes up to parallel limit
        while queue and len(active) < parallel:
            meeting_name, status = queue.pop(0)
            log_path = f"/dev/shm/meeting-process-{meeting_name}.log"

            cmd = [
                sys.executable, cli_path,
                "tick", "--auto-process", "--target", meeting_name,
            ]

            log_file = open(log_path, "w")
            proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
            active[proc.pid] = (proc, meeting_name, log_path, log_file)
            print(f"  ▶ Started: {meeting_name} (pid {proc.pid})")

        # Poll for completed processes
        done_pids = []
        for pid, (proc, name, log_path, log_file) in active.items():
            ret = proc.poll()
            if ret is not None:
                log_file.close()
                done_pids.append(pid)
                if ret == 0:
                    completed.append(name)
                    print(f"  ✅ Done: {name}")
                else:
                    failed.append(name)
                    # Read last few lines of log for error context
                    try:
                        with open(log_path) as f:
                            lines = f.readlines()
                            tail = ''.join(lines[-3:]).strip()
                    except:
                        tail = "(no log)"
                    print(f"  ❌ Failed: {name} (exit {ret})")
                    print(f"     {tail}")

        for pid in done_pids:
            del active[pid]

        if active:
            time.sleep(2)  # Poll every 2 seconds

    # Summary
    print(f"\n{'=' * 50}")
    print(f"Process-all complete:")
    print(f"  Completed: {len(completed)}")
    print(f"  Failed:    {len(failed)}")
    if failed:
        print(f"  Failed meetings:")
        for name in failed:
            print(f"    - {name}")

    # Archive completed meetings
    if do_archive and completed:
        print(f"\nArchiving {len(completed)} completed meetings...")
        try:
            from archive import archive_all
            archive_result = archive_all(dry_run=False)
            archived = len(archive_result.get('archived', []))
            print(f"  Archived: {archived}")
        except Exception as e:
            print(f"  ❌ Archive failed: {e}")

    if getattr(args, 'json', False):
        print(json.dumps({
            "completed": completed,
            "failed": failed,
            "total": len(meetings),
        }, indent=2))

    return 0 if not failed else 1


def cmd_process_batch(args):
    """LIFO batch processor — processes newest meetings first.

    Designed for gradual backfill: picks the N most recent unprocessed meetings,
    checks metadata quality, and processes them through the full pipeline.
    Pauses and alerts if a meeting has low metadata quality.
    """
    batch_size = getattr(args, 'batch_size', 3)
    alert_on_low_quality = not getattr(args, 'no_quality_gate', False)

    # Find all processable meetings
    meetings = []
    if INBOX.exists():
        for item in INBOX.iterdir():
            if item.is_dir() and not item.name.startswith(('.', '_')):
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text())
                        status = manifest.get("status", "")
                        if status in ["ingested", "identified", "gated"]:
                            meetings.append((item, status, manifest))
                    except:
                        continue

    if not meetings:
        print("No meetings in queue ready for processing")
        print(json.dumps({"processed": 0, "remaining": 0, "paused": False}))
        return 0

    # LIFO sort: newest first (by folder date prefix, then mtime)
    def sort_key(entry):
        folder_name = entry[0].name
        # Extract date from folder name (YYYY-MM-DD prefix)
        date_part = folder_name[:10] if len(folder_name) >= 10 else ""
        try:
            return datetime.strptime(date_part, "%Y-%m-%d")
        except ValueError:
            return datetime.min

    meetings.sort(key=sort_key, reverse=True)  # newest first

    batch = meetings[:batch_size]
    remaining = len(meetings) - len(batch)

    print(f"{'[DRY RUN] ' if args.dry_run else ''}LIFO Batch: {len(batch)}/{len(meetings)} meetings (newest first)")
    print(f"  Remaining after this batch: {remaining}")
    print()

    results = {
        "processed": 0,
        "succeeded": 0,
        "failed": 0,
        "skipped_low_quality": 0,
        "remaining": remaining,
        "paused": False,
        "meetings": [],
    }

    for meeting_path, current_status, manifest in batch:
        meeting_name = meeting_path.name
        print(f"--- {meeting_name} ---")
        print(f"  Status: {current_status}")

        # Metadata quality check
        if alert_on_low_quality:
            meta_quality = manifest.get("metadata_quality")
            # For backfilled manifests missing metadata_quality, apply a cheap
            # transcript-length sanity gate to avoid repeated expensive failures.
            if meta_quality is None:
                transcript_path = None
                for fname in ("transcript.md", "transcript.txt", "transcript.json"):
                    candidate = meeting_path / fname
                    if candidate.exists():
                        transcript_path = candidate
                        break
                if transcript_path is not None:
                    text = transcript_path.read_text(errors="ignore").strip()
                    if len(text) < 100:
                        quality_score = 0.0
                        flags = [f"Transcript too short ({len(text)} chars)"]
                        print(f"  ⚠️  LOW METADATA QUALITY (score: {quality_score:.2f})")
                        for flag in flags:
                            print(f"    - {flag}")
                        print("  ⏸️  Skipping — transcript quality is too low for reliable shape generation")
                        print("    Fix: re-import full transcript, then retry")
                        results["skipped_low_quality"] += 1
                        results["paused"] = True
                        results["meetings"].append({
                            "meeting": meeting_name,
                            "status": "skipped_low_quality",
                            "quality_score": quality_score,
                            "flags": flags,
                        })
                        continue
            elif meta_quality.get("overall_score", 1.0) < 0.5 or (
                not meta_quality.get("has_speaker_labels", True)
                and not meta_quality.get("has_participant_context", True)
            ):
                quality_score = meta_quality.get("overall_score", 0.0)
                flags = meta_quality.get("flags", [])
                print(f"  ⚠️  LOW METADATA QUALITY (score: {quality_score:.2f})")
                if flags:
                    for flag in flags:
                        print(f"    - {flag}")
                print(f"  ⏸️  Skipping — needs manual review or metadata enrichment")
                print(f"    Fix: provide participant names or use meeting_cli.py ingest with metadata")
                results["skipped_low_quality"] += 1
                results["paused"] = True
                results["meetings"].append({
                    "meeting": meeting_name,
                    "status": "skipped_low_quality",
                    "quality_score": quality_score,
                    "flags": flags,
                })
                continue

        if args.dry_run:
            print(f"  Would process through full pipeline")
            results["processed"] += 1
            results["meetings"].append({"meeting": meeting_name, "status": "dry_run"})
            continue

        # Process through tick with auto-process
        try:
            # Create a mock args object for cmd_tick
            class TickArgs:
                dry_run = False
                auto_process = True
                batch_size = 1
                target = meeting_name
                json = False

            tick_result = cmd_tick(TickArgs())
            if tick_result == 0:
                results["succeeded"] += 1
                results["meetings"].append({"meeting": meeting_name, "status": "success"})
            else:
                results["failed"] += 1
                results["meetings"].append({"meeting": meeting_name, "status": "failed"})
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results["failed"] += 1
            results["meetings"].append({"meeting": meeting_name, "status": "error", "error": str(e)})

        results["processed"] += 1

    print(f"\n{'=' * 40}")
    print(f"Batch complete: {results['succeeded']}/{results['processed']} succeeded, {results['failed']} failed")
    if results["skipped_low_quality"]:
        print(f"  ⚠️  {results['skipped_low_quality']} skipped (low metadata quality)")
    print(f"  Remaining in queue: {results['remaining']}")

    if getattr(args, 'json_output', False):
        print(json.dumps(results, indent=2))

    if results["failed"] > 0 or results["paused"]:
        return 1
    return 0


# === Legacy Commands (v2 compatibility) ===

def cmd_stage(args):
    """[LEGACY] Stage raw transcripts into meeting folders."""
    from stage import stage_all
    
    results = stage_all(dry_run=args.dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}[LEGACY] Staging Results:")
        print(f"  Staged:  {len(results.get('staged', []))}") 
        print(f"  Skipped: {len(results.get('skipped', []))}") 
        print(f"  Errors:  {len(results.get('errors', []))}")
        
        fix = results.get('fix_result', {})
        if fix.get('orphaned_files', 0) > 0:
            print(f"\n  Orphaned files moved: {fix['orphaned_files']}")
    
    return 0


def cmd_process(args):
    """Process staged meetings to generate canonical S-shape artifacts."""
    from process import process_meeting, process_queue

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
        else:
            status = results.get('status', 'processed')
            print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Meeting: {status}")
            generated = results.get('shapes_generated', [])
            if generated:
                print(f"  Shapes generated: {len(generated)}")
                for shape in generated:
                    print(f"    - {shape}")
    
    return 0


def cmd_archive(args):
    """[LEGACY] Archive completed meetings to weekly folders.""" 
    from archive import archive_all
    
    dry_run = not args.execute
    results = archive_all(dry_run=dry_run)
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    return 0


def cmd_status(args):
    """Show current ingestion status with v3 manifest support."""
    # v3 status counting
    v3_ingested = 0
    v3_identified = 0 
    v3_gated = 0
    v3_complete = 0
    
    # Legacy status counting
    staged = 0
    processing = 0
    complete = 0
    raw_files = 0
    
    if INBOX.exists():
        for item in INBOX.iterdir():
            if item.name.startswith((".", "_")):
                continue
            
            if item.is_file() and item.suffix in [".md", ".txt"]:
                raw_files += 1
                continue
            
            if item.is_dir():
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    try:
                        manifest = json.loads(manifest_path.read_text())
                        status = manifest.get("status", "unknown")
                        schema_version = str(
                            manifest.get("schema_version")
                            or manifest.get("manifest_version")
                            or ""
                        ).lower()
                        is_v3 = (
                            schema_version.startswith("v3")
                            or schema_version.startswith("3")
                            or status in {"ingested", "identified", "gated"}
                        )
                        
                        if is_v3:
                            # v3 status
                            if status == "ingested":
                                v3_ingested += 1
                            elif status == "identified":
                                v3_identified += 1
                            elif status == "gated":
                                v3_gated += 1 
                            elif status == "complete":
                                v3_complete += 1
                        else:
                            # Legacy status
                            if status == "staged":
                                staged += 1
                            elif status == "processing":
                                processing += 1
                            elif status == "complete":
                                complete += 1
                    except Exception as e:
                        logger.debug(f"Skipping {folder.name}: {e}")
    
    week_folders = 0
    archived_meetings = 0
    from paths import iter_archived_meetings
    seen_weeks = set()
    for meeting in iter_archived_meetings():
        archived_meetings += 1
        seen_weeks.add(meeting.parent)
    week_folders = len(seen_weeks)
    
    status = {
        "inbox": {
            "raw_files": raw_files,
            "v3_pipeline": {
                "ingested": v3_ingested,
                "identified": v3_identified, 
                "gated": v3_gated,
                "complete": v3_complete,
                "total": v3_ingested + v3_identified + v3_gated + v3_complete
            },
            "legacy_pipeline": {
                "staged": staged,
                "processing": processing,
                "complete": complete,
                "total": staged + processing + complete
            }
        },
        "archive": {
            "week_folders": week_folders,
            "meetings": archived_meetings
        }
    }
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("\nMeeting Ingestion Status")
        print("=" * 40)
        print("\nActive queue:")
        print(f"  Raw files (need ingestion):    {raw_files}")
        
        print(f"\n  v3 Pipeline:")
        print(f"    Ingested (need identify):     {v3_ingested}")
        print(f"    Identified (need gate):       {v3_identified}")
        print(f"    Gated (need process):         {v3_gated}")
        print(f"    Complete (need archive):      {v3_complete}")
        print(f"    Total v3:                     {status['inbox']['v3_pipeline']['total']}")
        
        print(f"\n  Legacy Pipeline:")
        print(f"    Staged (ready to process):    {staged}")
        print(f"    Processing:                   {processing}")
        print(f"    Complete (ready to archive):  {complete}")
        print(f"    Total legacy:                 {status['inbox']['legacy_pipeline']['total']}")
        
        print(f"\nArchive:")
        print(f"  Week folders:                   {week_folders}")
        print(f"  Archived meetings:              {archived_meetings}")
    
    return 0


def cmd_dedup_audit(args):
    """Scan Active + archive for likely duplicate meetings.

    Groups folders by (date_prefix, stable 2+ word title signature). Reports any
    group with >1 member. Read-only — makes no changes.
    """
    import re
    from collections import defaultdict
    from paths import ACTIVE_DIR, iter_archived_meetings

    def title_words(name: str) -> frozenset[str]:
        rest = name[11:] if len(name) > 10 and name[10] == "_" else name
        return frozenset(
            w for w in re.sub(r"[^a-z0-9\s]", " ", rest.lower().replace("-", " ")).split()
            if len(w) >= 3
        )

    groups: dict[tuple, list[dict]] = defaultdict(list)

    def consider(folder, location):
        if not folder.is_dir() or folder.name.startswith('.'):
            return
        date_prefix = folder.name[:10] if len(folder.name) >= 10 else ""
        if not date_prefix or date_prefix[4] != "-":
            return
        words = title_words(folder.name)
        if len(words) < 2:
            return
        key = (date_prefix, words)
        groups[key].append({"name": folder.name, "location": location, "path": str(folder)})

    if ACTIVE_DIR.exists():
        for f in ACTIVE_DIR.iterdir():
            consider(f, "Active")
    for f in iter_archived_meetings():
        consider(f, "archive")

    dupes = {k: v for k, v in groups.items() if len(v) > 1}

    if args.json:
        report = {
            "total_groups_scanned": len(groups),
            "duplicate_groups": len(dupes),
            "groups": [
                {"date": k[0], "signature": sorted(k[1]), "members": v}
                for k, v in dupes.items()
            ],
        }
        print(json.dumps(report, indent=2))
        return 0

    print(f"\nDedup audit")
    print(f"  Scanned groups:   {len(groups)}")
    print(f"  Duplicate groups: {len(dupes)}")
    if not dupes:
        print("  ✅ No duplicates found.")
        return 0
    for (date, sig), members in sorted(dupes.items()):
        print(f"\n  {date} [{', '.join(sorted(sig))[:80]}]")
        for m in members:
            print(f"    - [{m['location']}] {m['name']}")
    return 1 if dupes else 0



def cmd_list(args):
    """D7: list meetings by manifest.review_status.

    Default: show everything in Active/ with review_status=needs_review.
    """
    import json as _json
    if not INBOX.exists():
        print("[]"); return 0
    rows = []
    for folder in sorted(INBOX.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        mp = folder / "manifest.json"
        if not mp.exists():
            continue
        try:
            m = _json.loads(mp.read_text())
        except Exception:
            continue
        status = m.get("status", "")
        rs = m.get("review_status", "")
        if getattr(args, "needs_review", False) and rs != "needs_review":
            continue
        rows.append({
            "meeting_id": m.get("meeting_id") or folder.name,
            "status": status,
            "review_status": rs,
            "reason": m.get("review", {}).get("last_reason"),
            "folder": str(folder),
        })
    if getattr(args, "json", False):
        print(_json.dumps(rows, indent=2))
    else:
        if not rows:
            print("(no matching meetings)")
        for r in rows:
            print(f"  {r['meeting_id']:60s} status={r['status']:12s} review={r['review_status']} {('reason=' + r['reason']) if r['reason'] else ''}")
    return 0


def cmd_fix(args):
    """[LEGACY] Fix malformed meetings in Active queue."""
    from stage import fix_inbox_mess, stage_all
    
    print("\n=== [LEGACY] Fixing Active queue ===\n")
    
    print("Step 1: Quarantine orphaned files...")
    fix_result = fix_inbox_mess(dry_run=args.dry_run)
    print(f"  Orphaned files: {fix_result.get('orphaned_files', 0)}")
    
    print("\nStep 2: Stage any raw files...")
    stage_result = stage_all(dry_run=args.dry_run)
    print(f"  Staged: {len(stage_result.get('staged', []))}")
    print(f"  Errors: {len(stage_result.get('errors', []))}")
    
    if args.json:
        print(json.dumps({"fix": fix_result, "stage": stage_result}, indent=2))
    
    return 0


def cmd_check(args):
    """All-points intake check — scan all meeting intake sources."""
    from intake_checker import run_full_check

    report = run_full_check(verbose=args.verbose, json_output=args.json)
    if args.json:
        print(json.dumps(report, indent=2))
    return 0


def cmd_backfill(args):
    """Pull historical meetings from Fathom/Fireflies by date range."""
    from backfill import run_backfill

    from_dt = datetime.strptime(args.from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(args.to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)

    result = run_backfill(
        source=args.source,
        from_date=from_dt,
        to_date=to_dt,
        dry_run=args.dry_run,
        limit=args.limit,
        json_output=args.json,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    return 0 if result.get("errors") == 0 else 1


def cmd_closeout_backfill(args):
    """Run safe closeout-only backfill for already-complete Active queue meetings."""
    from closeout_backfill import cmd_run
    return cmd_run(args)


def cmd_refill(args):
    """Re-fetch transcripts for meetings with empty/short content.

    Scans Inbox for meetings from a given source whose transcript is below
    a character threshold, then re-fetches the transcript from the API
    and rewrites transcript.md using the fixed converter.
    """
    import requests
    from backfill import _fathom_to_markdown, _fireflies_to_markdown, get_api_key

    threshold = args.min_chars
    source_filter = args.source
    dry_run = args.dry_run

    candidates = []
    for meeting_dir in sorted(INBOX.iterdir()):
        if not meeting_dir.is_dir():
            continue
        manifest_path = meeting_dir / "manifest.json"
        transcript_path = meeting_dir / "transcript.md"
        if not manifest_path.exists():
            continue

        manifest = json.loads(manifest_path.read_text())
        source_type, rec_id = _source_type_and_id(manifest)

        if source_filter and source_filter != source_type:
            continue

        t_size = transcript_path.stat().st_size if transcript_path.exists() else 0
        if t_size >= threshold:
            continue

        if not source_type or not rec_id:
            continue

        candidates.append({
            "dir": meeting_dir,
            "manifest": manifest,
            "source_type": source_type,
            "rec_id": rec_id,
            "current_size": t_size,
        })

    print(f"Found {len(candidates)} meetings with transcript < {threshold} chars")
    if not candidates:
        return 0

    if dry_run:
        for c in candidates:
            print(f"  Would refill: {c['dir'].name} ({c['source_type']}, {c['current_size']} chars)")
        print(f"\nRun without --dry-run to re-fetch {len(candidates)} transcript(s)")
        return 0

    fathom_key = get_api_key("FATHOM_API_KEY")
    fireflies_key = get_api_key("FIREFLIES_API_KEY")

    import time as _time

    refilled = 0
    errors = []
    for c in candidates:
        rec_id = c["rec_id"]
        meeting_dir = c["dir"]
        print(f"  Refilling {meeting_dir.name} (id={rec_id})...", end=" ")

        try:
            if c["source_type"] == "fathom":
                if not fathom_key:
                    print("SKIP (no FATHOM_API_KEY)")
                    continue
                base = "https://api.fathom.ai/external/v1"
                headers = {"X-Api-Key": fathom_key}

                # Fetch transcript with rate-limit retry
                for attempt in range(3):
                    t_resp = requests.get(f"{base}/recordings/{rec_id}/transcript", headers=headers, timeout=15)
                    if t_resp.status_code == 429:
                        wait = 2 ** (attempt + 1)
                        print(f"rate-limited, waiting {wait}s...", end=" ")
                        _time.sleep(wait)
                        continue
                    break

                if t_resp.status_code != 200:
                    print(f"FAIL (API {t_resp.status_code})")
                    errors.append(f"{meeting_dir.name}: API {t_resp.status_code}")
                    continue

                transcript_data = t_resp.json()
                full = {"transcript": transcript_data}
                full["title"] = c["manifest"].get("source", {}).get("original_title", "Untitled")
                md = _fathom_to_markdown(full)

                # Throttle to avoid hitting rate limits
                _time.sleep(0.5)

            elif c["source_type"] == "fireflies":
                if not fireflies_key:
                    print("SKIP (no FIREFLIES_API_KEY)")
                    continue
                ff_headers = {"Authorization": f"Bearer {fireflies_key}", "Content-Type": "application/json"}
                detail_query = f'''{{ transcript(id: "{rec_id}") {{
                    id title date duration participants
                    sentences {{ index text raw_text start_time end_time speaker_name speaker_id }}
                    summary {{ keywords action_items overview }}
                }} }}'''
                resp = requests.post(
                    "https://api.fireflies.ai/graphql",
                    headers=ff_headers,
                    json={"query": detail_query},
                    timeout=30,
                )
                resp.raise_for_status()
                full = resp.json().get("data", {}).get("transcript")
                if not full:
                    print("FAIL (no transcript data)")
                    errors.append(f"{meeting_dir.name}: empty response")
                    continue
                md = _fireflies_to_markdown(full)
            else:
                print(f"SKIP (unknown source: {c['source_type']})")
                continue

            if len(md) < threshold:
                print(f"SKIP (refetched but still short: {len(md)} chars)")
                continue

            (meeting_dir / "transcript.md").write_text(md)
            refilled += 1
            print(f"OK ({len(md)} chars)")

        except Exception as e:
            print(f"ERROR ({e})")
            errors.append(f"{meeting_dir.name}: {e}")

    print(f"\nRefilled: {refilled}/{len(candidates)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors[:10]:
            print(f"  - {e}")
    return 0 if not errors else 1


def cmd_drive_import(args):
    """Import transcripts from Google Drive External Transcripts folders."""
    from drive_import import scan_drive_folders, pull_from_drive

    if args.scan:
        result = scan_drive_folders(json_output=args.json)
    else:
        result = pull_from_drive(dry_run=args.dry_run, json_output=args.json)

    if args.json:
        print(json.dumps(result, indent=2))
    return 0


def cmd_pull(args):
    """[LEGACY] Pull transcripts from Google Drive."""
    from pull import pull_transcripts
    
    results = pull_transcripts(dry_run=args.dry_run, batch_size=args.batch_size)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}[LEGACY] Pull Results:")
        print(f"  Ingested: {len(results.get('ingested', []))}")
        print(f"  Skipped:  {len(results.get('skipped', []))}")
        print(f"  Errors:   {len(results.get('errors', []))}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Meeting Ingestion CLI v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
v3 Pipeline Workflow (Recommended):
    1. meeting_cli.py ingest <path>        # Ingest transcripts → v3 manifests
    2. meeting_cli.py identify <meeting>   # Calendar + CRM enrichment  
    3. meeting_cli.py gate <meeting>       # Quality validation
    4. meeting_cli.py process <meeting>    # Generate canonical meeting shapes
    5. meeting_cli.py archive --execute    # Move to weekly folders
    
    OR: meeting_cli.py tick                # Process next in queue

Intake Management:
    meeting_cli.py check                  # All-points intake scan
    meeting_cli.py backfill --source all --from 2026-02-01 --to 2026-03-10
    meeting_cli.py drive-import --scan    # Check Drive folders for new files
    meeting_cli.py drive-import --pull    # Pull new files from Drive

Legacy Workflow (v2 Compatibility):
    1. meeting_cli.py pull                 # Download from Google Drive
    2. meeting_cli.py stage                # Wrap raw files in folders
    3. meeting_cli.py process              # Generate canonical meeting shapes  
    4. meeting_cli.py archive --execute    # Move to weekly folders

Examples:
    # v3 Commands
    meeting_cli.py status                              # Check both pipelines
    meeting_cli.py ingest ./transcript.md --dry-run   # Ingest single file
    meeting_cli.py ingest ./inbox/ --dry-run          # Ingest folder
    meeting_cli.py identify ./meeting-2026-01-01_Test --dry-run
    meeting_cli.py gate ./meeting-2026-01-01_Test --dry-run  
    meeting_cli.py tick --dry-run                      # Process next in queue
    
    # Legacy Commands
    meeting_cli.py stage --dry-run                     # Preview staging
    meeting_cli.py process --batch-size 3              # Process 3 meetings
    meeting_cli.py process ./meeting-folder            # Process specific meeting
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # === v3 Pipeline Commands ===
    
    # Ingest
    ingest_parser = subparsers.add_parser("ingest", help="[v3] Ingest transcripts into v3 meeting folders")
    ingest_parser.add_argument("path", help="File or folder to ingest")
    ingest_parser.add_argument("--dry-run", action="store_true")
    ingest_parser.add_argument("--json", action="store_true")
    
    # Identify
    identify_parser = subparsers.add_parser("identify", help="[v3] Run calendar + CRM enrichment") 
    identify_parser.add_argument("meeting", help="Meeting folder path")
    identify_parser.add_argument("--dry-run", action="store_true")
    identify_parser.add_argument("--json", action="store_true")
    
    # Gate
    gate_parser = subparsers.add_parser("gate", help="[v3] Run quality gate validation")
    gate_parser.add_argument("meeting", help="Meeting folder path") 
    gate_parser.add_argument("--dry-run", action="store_true")
    gate_parser.add_argument("--json", action="store_true")
    
    # Tick
    tick_parser = subparsers.add_parser("tick", help="[v3] Process next meeting in queue")
    tick_parser.add_argument("--dry-run", action="store_true")
    tick_parser.add_argument("--auto-process", action="store_true", help="Continue through shape generation (for automation)")
    tick_parser.add_argument("--batch-size", type=int, default=10, help="Number of meetings to process per tick")
    tick_parser.add_argument("--target", type=str, help="Process a specific meeting folder name (skip queue scan)")
    tick_parser.add_argument("--skip-raw-intake", action="store_true", help="Do not ingest raw files from Active/ root before processing queued folders")
    tick_parser.add_argument("--json", action="store_true")

    # Process-all
    process_all_parser = subparsers.add_parser("process-all", help="[v3] Process all queued meetings (parallel)")
    process_all_parser.add_argument("--dry-run", action="store_true")
    process_all_parser.add_argument("--parallel", type=int, default=3, help="Max concurrent meetings to process (default: 3)")
    process_all_parser.add_argument("--archive", action="store_true", default=True, help="Archive completed meetings after processing")
    process_all_parser.add_argument("--no-archive", action="store_true", help="Skip archiving after processing")
    process_all_parser.add_argument("--json", action="store_true")
    
    # LIFO Batch Processor
    batch_parser = subparsers.add_parser("process-batch", help="[v3] LIFO batch processor — newest meetings first")
    batch_parser.add_argument("--batch-size", type=int, default=3, help="Meetings per batch (default: 3)")
    batch_parser.add_argument("--dry-run", action="store_true")
    batch_parser.add_argument("--no-quality-gate", action="store_true", help="Skip metadata quality check")
    batch_parser.add_argument("--json", dest="json_output", action="store_true")

    # === Intake Management Commands ===

    # Check (all-points intake scan)
    check_parser = subparsers.add_parser("check", help="All-points intake check across all sources")
    check_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed listings")
    check_parser.add_argument("--json", action="store_true")

    # Backfill (Fathom/Fireflies historical pull)
    backfill_parser = subparsers.add_parser("backfill", help="Pull historical meetings from Fathom/Fireflies")
    backfill_parser.add_argument("--source", required=True, choices=["fathom", "fireflies", "all"],
                                 help="Source to backfill from")
    backfill_parser.add_argument("--from", dest="from_date", required=True,
                                 help="Start date (YYYY-MM-DD)")
    backfill_parser.add_argument("--to", dest="to_date", required=True,
                                 help="End date (YYYY-MM-DD)")
    backfill_parser.add_argument("--dry-run", action="store_true")
    backfill_parser.add_argument("--limit", type=int, default=100,
                                 help="Max recordings per source (default: 100)")
    backfill_parser.add_argument("--json", action="store_true")

    closeout_backfill_parser = subparsers.add_parser(
        "closeout-backfill",
        help="Run safe closeout-only backfill for already-complete Active queue meetings"
    )
    closeout_backfill_parser.add_argument("--limit", type=int, default=None)
    closeout_backfill_parser.add_argument("--dry-run", action="store_true")

    # Refill (re-fetch empty transcripts)
    refill_parser = subparsers.add_parser("refill", help="Re-fetch transcripts for meetings with empty/short content")
    refill_parser.add_argument("--source", choices=["fathom", "fireflies"],
                                help="Only refill from this source (default: all)")
    refill_parser.add_argument("--min-chars", type=int, default=200,
                                help="Transcript char threshold (default: 200)")
    refill_parser.add_argument("--dry-run", action="store_true")

    # Drive Import (External Transcripts folders)
    drive_parser = subparsers.add_parser("drive-import", help="Import from Google Drive External Transcripts")
    drive_group = drive_parser.add_mutually_exclusive_group(required=True)
    drive_group.add_argument("--scan", action="store_true", help="Scan Drive folders for new files")
    drive_group.add_argument("--pull", action="store_true", help="Pull new files into Inbox")
    drive_parser.add_argument("--dry-run", action="store_true")
    drive_parser.add_argument("--json", action="store_true")

    # === Legacy Commands ===

    # Pull
    pull_parser = subparsers.add_parser("pull", help="[LEGACY] Download from Google Drive")
    pull_parser.add_argument("--dry-run", action="store_true")
    pull_parser.add_argument("--batch-size", type=int, default=5)
    pull_parser.add_argument("--json", action="store_true")
    
    # Stage
    stage_parser = subparsers.add_parser("stage", help="[LEGACY] Stage raw transcripts")
    stage_parser.add_argument("--dry-run", action="store_true")
    stage_parser.add_argument("--json", action="store_true")
    
    # Process (enhanced to work with both v2 and v3)
    process_parser = subparsers.add_parser(
        "process",
        help="Generate canonical S-shapes"
    )
    process_parser.add_argument("meeting_path", nargs="?")
    process_parser.add_argument("--batch-size", type=int, default=5)
    process_parser.add_argument("--dry-run", action="store_true")
    process_parser.add_argument("--json", action="store_true")
    
    # Archive
    archive_parser = subparsers.add_parser("archive", help="[LEGACY] Move to weekly folders")
    archive_parser.add_argument("--dry-run", action="store_true", default=True)
    archive_parser.add_argument("--execute", action="store_true")
    archive_parser.add_argument("--json", action="store_true")

    # List (D7: review queue view)
    list_parser = subparsers.add_parser("list", help="List meetings; filter by review_status")
    list_parser.add_argument("--needs-review", action="store_true", help="Only show review_status=needs_review")
    list_parser.add_argument("--json", action="store_true")

    # Status (enhanced for v3 support)
    status_parser = subparsers.add_parser("status", help="Show ingestion status")
    status_parser.add_argument("--json", action="store_true")

    # Fix
    fix_parser = subparsers.add_parser("fix", help="[LEGACY] Fix malformed active queue")
    fix_parser.add_argument("--dry-run", action="store_true")
    fix_parser.add_argument("--json", action="store_true")

    # Dedup audit
    dedup_parser = subparsers.add_parser("dedup-audit", help="Scan Active + archive for duplicate meetings")
    dedup_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    handlers = {
        # v3 Pipeline Commands
        "ingest": cmd_ingest,
        "identify": cmd_identify,
        "gate": cmd_gate,
        "tick": cmd_tick,
        "process-all": cmd_process_all,
        "process-batch": cmd_process_batch,

        # Intake Management
        "check": cmd_check,
        "backfill": cmd_backfill,
        "refill": cmd_refill,
        "drive-import": cmd_drive_import,
        "closeout-backfill": cmd_closeout_backfill,
        "dedup-audit": cmd_dedup_audit,
        "list": cmd_list,

        # Legacy Commands
        "pull": cmd_pull,
        "stage": cmd_stage,
        "process": cmd_process,
        "archive": cmd_archive,
        "status": cmd_status,
        "fix": cmd_fix,
    }
    
    handler = handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
