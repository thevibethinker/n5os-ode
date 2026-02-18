#!/usr/bin/env python3
"""
Meeting Ingestion Skill - Unified CLI v3

Single entry point for all meeting ingestion operations with v3 pipeline support.

Usage:
    # v3 Pipeline Commands (recommended)
    python3 meeting_cli.py ingest <path> [--dry-run]
    python3 meeting_cli.py identify <meeting> [--dry-run] 
    python3 meeting_cli.py gate <meeting> [--dry-run]
    python3 meeting_cli.py process <meeting> [--blocks B01,B05] [--dry-run]
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

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
MEETINGS = Path("/home/workspace/Personal/Meetings")


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
            results['calendar'] = cal_result
            print(f"  Calendar match: {cal_result.get('confidence', 'N/A')} confidence")
        
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

    With --auto-process: runs identify → gate → block generation automatically.
    Without --auto-process: stops before block generation (manual mode).
    """
    auto_process = getattr(args, 'auto_process', False)
    batch_size = getattr(args, 'batch_size', 1)
    target = getattr(args, 'target', None)

    try:
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
            if status not in ["ingested", "identified", "gated"]:
                print(f"Meeting {target} is at status '{status}', not processable")
                return 0
            meetings_to_process = [(target_path, status)]
            batch = meetings_to_process
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing target: {target} (status: {status})")
            if auto_process:
                print("  Mode: --auto-process (full pipeline including block generation)")
            # Skip to processing loop
            results = {"processed": 0, "succeeded": 0, "failed": 0, "meetings": []}
            # (falls through to the main processing loop below)
        else:
            meetings_to_process = None  # Signal to do the normal scan

        # Pre-step: Ingest any raw transcript files sitting in Inbox root
        if meetings_to_process is None:
            if INBOX.exists():
                raw_files = [
                    f for f in INBOX.iterdir()
                    if f.is_file() and f.suffix in [".md", ".txt", ".jsonl"] and not f.name.startswith(".")
                ]
                if raw_files:
                    print(f"Found {len(raw_files)} raw transcript file(s) in Inbox root")
                    from ingest import TranscriptIngestor
                    ingestor = TranscriptIngestor()
                    for raw_file in raw_files:
                        try:
                            if args.dry_run:
                                print(f"  [DRY RUN] Would ingest: {raw_file.name}")
                            else:
                                result = ingestor.ingest_file(str(raw_file), dry_run=False)
                                ing_status = result.get('status', 'unknown')
                                print(f"  Ingested {raw_file.name} → {result.get('meeting_folder', 'unknown')} ({ing_status})")
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
                                if status in ["ingested", "identified", "gated"]:
                                    meetings_to_process.append((item, status))
                            except:
                                continue

            if not meetings_to_process:
                print("No meetings in queue ready for processing")
                return 0

            # Sort by creation time (oldest first)
            meetings_to_process.sort(key=lambda x: x[0].stat().st_mtime)

            # Limit to batch size
            batch = meetings_to_process[:batch_size]
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(batch)}/{len(meetings_to_process)} meetings (batch_size={batch_size})")
            if auto_process:
                print("  Mode: --auto-process (full pipeline including block generation)")

            results = {"processed": 0, "succeeded": 0, "failed": 0, "meetings": []}

        for meeting_path, current_status in batch:
            print(f"\n--- {meeting_path.name} ---")
            print(f"  Current status: {current_status}")

            if args.dry_run:
                steps = []
                if current_status == "ingested":
                    steps = ["identify", "gate"]
                elif current_status == "identified":
                    steps = ["gate"]
                if auto_process:
                    steps.append("process (block generation)")
                print(f"  Would run: {' → '.join(steps)}")
                results["meetings"].append({"meeting": meeting_path.name, "status": "dry_run", "steps": steps})
                continue

            success = True
            meeting_result = {"meeting": meeting_path.name}

            # Step 1: Identify (if needed)
            if current_status == "ingested":
                print("  Running identification...")
                try:
                    from calendar_match import match_meeting_to_calendar
                    from crm_enricher import CRMEnricher
                    manifest_data = json.loads((meeting_path / "manifest.json").read_text())
                    match_meeting_to_calendar(manifest_data)
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

                # Update manifest status to identified
                if success:
                    try:
                        mf = json.loads((meeting_path / "manifest.json").read_text())
                        mf["status"] = "identified"
                        mf.setdefault("timestamps", {})["identified_at"] = datetime.now(timezone.utc).isoformat()
                        mf.setdefault("status_history", []).append({
                            "status": "identified",
                            "at": datetime.now(timezone.utc).isoformat(),
                        })
                        (meeting_path / "manifest.json").write_text(json.dumps(mf, indent=2))
                        current_status = "identified"
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

            # Step 3: Block generation (only with --auto-process)
            if success and auto_process:
                print("  Running block generation...")
                try:
                    from process import process_meeting
                    proc_result = process_meeting(meeting_path, dry_run=False)
                    proc_status = proc_result.get('status', 'unknown')
                    blocks_gen = proc_result.get('blocks_generated', [])
                    print(f"    ✅ Blocks generated: {len(blocks_gen)}")
                    for b in blocks_gen:
                        print(f"      - {b}")
                    meeting_result["blocks_generated"] = blocks_gen
                except Exception as e:
                    print(f"    ❌ Block generation failed: {e}")
                    success = False
            elif success and not auto_process:
                print("  ⚠️  Block processing requires --auto-process or manual run")
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
    """Process staged meetings to generate intelligence blocks."""
    from process import process_meeting, process_queue
    
    blocks = None
    if args.blocks:
        blocks = [b.strip().upper() for b in args.blocks.split(",")]
    
    if args.meeting_path:
        meeting_path = Path(args.meeting_path)
        if not meeting_path.exists():
            print(f"Error: Path not found: {meeting_path}")
            return 1
        results = process_meeting(meeting_path, blocks=blocks, dry_run=args.dry_run)
    else:
        results = process_queue(batch_size=args.batch_size, blocks=blocks, dry_run=args.dry_run)
    
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
            if results.get('blocks_generated'):
                print(f"  Blocks generated: {len(results['blocks_generated'])}")
                for b in results['blocks_generated']:
                    print(f"    - {b}")
    
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
                        schema_version = manifest.get("schema_version", "v2")
                        
                        if schema_version == "v3":
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
                    except:
                        pass
    
    week_folders = 0
    archived_meetings = 0
    if MEETINGS.exists():
        for folder in MEETINGS.iterdir():
            if folder.is_dir() and folder.name.startswith("Week-of-"):
                week_folders += 1
                for meeting in folder.iterdir():
                    if meeting.is_dir():
                        archived_meetings += 1
    
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
        print("\nInbox:")
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


def cmd_fix(args):
    """[LEGACY] Fix malformed meetings in Inbox."""
    from stage import fix_inbox_mess, stage_all
    
    print("\n=== [LEGACY] Fixing Inbox ===\n")
    
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
    4. meeting_cli.py process <meeting>    # Generate intelligence blocks
    5. meeting_cli.py archive --execute    # Move to weekly folders
    
    OR: meeting_cli.py tick                # Auto-process next in queue

Legacy Workflow (v2 Compatibility):
    1. meeting_cli.py pull                 # Download from Google Drive
    2. meeting_cli.py stage                # Wrap raw files in folders
    3. meeting_cli.py process              # Generate intelligence blocks  
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
    tick_parser.add_argument("--auto-process", action="store_true", help="Continue through block generation (for automation)")
    tick_parser.add_argument("--batch-size", type=int, default=1, help="Number of meetings to process per tick")
    tick_parser.add_argument("--target", type=str, help="Process a specific meeting folder name (skip queue scan)")
    tick_parser.add_argument("--json", action="store_true")

    # Process-all
    process_all_parser = subparsers.add_parser("process-all", help="[v3] Process all queued meetings (parallel)")
    process_all_parser.add_argument("--dry-run", action="store_true")
    process_all_parser.add_argument("--parallel", type=int, default=3, help="Max concurrent meetings to process (default: 3)")
    process_all_parser.add_argument("--archive", action="store_true", default=True, help="Archive completed meetings after processing")
    process_all_parser.add_argument("--no-archive", action="store_true", help="Skip archiving after processing")
    process_all_parser.add_argument("--json", action="store_true")
    
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
    process_parser = subparsers.add_parser("process", help="Generate intelligence blocks")
    process_parser.add_argument("meeting_path", nargs="?")
    process_parser.add_argument("--blocks", type=str)
    process_parser.add_argument("--batch-size", type=int, default=5)
    process_parser.add_argument("--dry-run", action="store_true")
    process_parser.add_argument("--json", action="store_true")
    
    # Archive
    archive_parser = subparsers.add_parser("archive", help="[LEGACY] Move to weekly folders")
    archive_parser.add_argument("--dry-run", action="store_true", default=True)
    archive_parser.add_argument("--execute", action="store_true")
    archive_parser.add_argument("--json", action="store_true")
    
    # Status (enhanced for v3 support)
    status_parser = subparsers.add_parser("status", help="Show ingestion status")
    status_parser.add_argument("--json", action="store_true")
    
    # Fix
    fix_parser = subparsers.add_parser("fix", help="[LEGACY] Fix malformed inbox")
    fix_parser.add_argument("--dry-run", action="store_true")
    fix_parser.add_argument("--json", action="store_true")
    
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