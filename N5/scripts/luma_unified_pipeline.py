#!/usr/bin/env python3
"""
Luma Unified Pipeline - Single entry point for all event operations.

Consolidates the fragmented events system into one orchestrated pipeline:
1. Ingest: Scrape lu.ma/nyc + parse newsletter emails + sync personal Luma
2. Score: Score all unscored events
3. Export: Export to luma_candidates.json for site
4. Digest: Generate digest via luma_digest.py
5. Email: Flag digest ready for email delivery (agent handles actual send)

Usage:
    python3 luma_unified_pipeline.py                    # Full pipeline
    python3 luma_unified_pipeline.py --steps ingest,score
    python3 luma_unified_pipeline.py --dry-run --verbose
    python3 luma_unified_pipeline.py --steps digest --email-ready
"""

import argparse
import json
import logging
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Use centralized paths
from N5.lib.paths import N5_SCRIPTS_DIR, N5_DATA_DIR, N5_DIGESTS_DIR

SCRIPTS_DIR = N5_SCRIPTS_DIR
DATA_DIR = N5_DATA_DIR
DIGESTS_DIR = N5_DIGESTS_DIR
DB_PATH = DATA_DIR / "luma_events.db"
CANDIDATES_FILE = DATA_DIR / "luma_candidates.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

ALL_STEPS = ["ingest", "score", "export", "digest", "email"]


class PipelineResult:
    def __init__(self):
        self.success = True
        self.steps_completed = []
        self.stats = {
            "events_ingested": 0,
            "events_scored": 0,
            "events_exported": 0,
            "digest_generated": False,
            "email_ready": False
        }
        self.errors = []
        self.digest_content = None
        self.digest_path = None
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "success": self.success and len(self.errors) == 0,
            "steps_completed": self.steps_completed,
            "stats": self.stats,
            "errors": self.errors,
            "digest_path": str(self.digest_path) if self.digest_path else None,
            "timestamp": self.timestamp
        }


def run_script(script_name: str, args: list = None, capture_output: bool = True) -> tuple[int, str, str]:
    """Run a Python script and return (returncode, stdout, stderr)."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return 1, "", f"Script not found: {script_path}"
    
    cmd = ["python3", str(script_path)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=300)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Script timed out after 300s: {script_name}"
    except Exception as e:
        return 1, "", str(e)


def step_ingest(result: PipelineResult, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Ingest events from multiple sources:
    - luma_scraper.py: Scrape lu.ma/nyc
    - luma_email_discovery.py: Parse Gmail for event links
    """
    logger.info("=" * 50)
    logger.info("STEP: INGEST - Discovering events from all sources")
    logger.info("=" * 50)
    
    total_ingested = 0
    
    # 1. Run scraper
    logger.info("Running luma_scraper.py...")
    if dry_run:
        logger.info("[DRY RUN] Would scrape lu.ma/nyc")
    else:
        returncode, stdout, stderr = run_script("luma_scraper.py", ["--nyc"])
        if returncode != 0:
            error_msg = f"Scraper failed: {stderr}"
            logger.warning(error_msg)
            result.errors.append(error_msg)
        else:
            if verbose:
                logger.info(f"Scraper output: {stdout[:500]}...")
            # Parse output for count if available
            if "events" in stdout.lower():
                logger.info(f"Scraper completed: {stdout.strip().split(chr(10))[-1]}")
    
    # 2. Run email discovery (this needs agent context, so we just check if it can run)
    logger.info("Checking luma_email_discovery.py...")
    if dry_run:
        logger.info("[DRY RUN] Would parse Gmail for event links")
    else:
        # Email discovery typically needs to be run by agent with Gmail access
        # Here we just verify the script exists and log the need for agent invocation
        if (SCRIPTS_DIR / "luma_email_discovery.py").exists():
            logger.info("Email discovery script available - invoke via agent for Gmail access")
        else:
            logger.warning("luma_email_discovery.py not found")
    
    # 3. Count new events in DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'new' OR status IS NULL")
        new_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM events")
        total_count = cursor.fetchone()[0]
        conn.close()
        
        total_ingested = new_count
        logger.info(f"Events in DB: {total_count} total, {new_count} unprocessed")
    except Exception as e:
        result.errors.append(f"DB query failed: {e}")
        logger.error(f"Failed to query DB: {e}")
    
    result.stats["events_ingested"] = total_ingested
    result.steps_completed.append("ingest")
    logger.info(f"INGEST complete: {total_ingested} events available for scoring")
    return True


def step_score(result: PipelineResult, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Score all unscored events using luma_scorer.py.
    """
    logger.info("=" * 50)
    logger.info("STEP: SCORE - Scoring events")
    logger.info("=" * 50)
    
    if dry_run:
        logger.info("[DRY RUN] Would score unscored events")
        result.steps_completed.append("score")
        return True
    
    # Count unscored events
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events WHERE score IS NULL")
        unscored_count = cursor.fetchone()[0]
        conn.close()
        
        if unscored_count == 0:
            logger.info("No unscored events found - all events already scored")
            result.steps_completed.append("score")
            return True
        
        logger.info(f"Found {unscored_count} unscored events")
    except Exception as e:
        result.errors.append(f"Failed to count unscored: {e}")
        return False
    
    # Run scorer
    logger.info("Running luma_scorer.py...")
    returncode, stdout, stderr = run_script("luma_scorer.py", ["--score-all"])
    
    if returncode != 0:
        # Try alternative invocation
        returncode, stdout, stderr = run_script("luma_scorer.py")
    
    if verbose:
        logger.info(f"Scorer output: {stdout}")
    
    # Count scored events after
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events WHERE score IS NOT NULL")
        scored_count = cursor.fetchone()[0]
        conn.close()
        
        result.stats["events_scored"] = scored_count
        logger.info(f"Total scored events: {scored_count}")
    except Exception as e:
        result.errors.append(f"Failed to count scored: {e}")
    
    result.steps_completed.append("score")
    return True


def step_export(result: PipelineResult, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Export all future events to luma_candidates.json for the calendar site.
    """
    logger.info("=" * 50)
    logger.info("STEP: EXPORT - Exporting events to JSON")
    logger.info("=" * 50)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would export to {CANDIDATES_FILE}")
        result.steps_completed.append("export")
        return True
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get future events with scores
        cursor.execute("""
            SELECT * FROM events 
            WHERE (event_date >= ? OR event_date IS NULL)
            AND (status IS NULL OR status NOT IN ('rejected', 'past'))
            ORDER BY event_date ASC, score DESC
        """, (today,))
        
        events = []
        for row in cursor.fetchall():
            event = dict(row)
            events.append({
                "id": event.get("id"),
                "url": event.get("url"),
                "title": event.get("title"),
                "description": event.get("description", ""),
                "event_date": event.get("event_date"),
                "event_time": event.get("event_time"),
                "venue_name": event.get("venue_name", ""),
                "venue_address": event.get("venue_address", ""),
                "location": event.get("location", ""),
                "organizer_name": event.get("organizer_name", ""),
                "organizers": event.get("organizers", ""),
                "city": event.get("city", "nyc"),
                "price": event.get("price", ""),
                "attendee_count": event.get("attendee_count", 0),
                "cover_image_url": event.get("cover_image_url", ""),
                "source": "luma",
                "invitation_status": event.get("invitation_status", "public"),
                "score": event.get("score"),  # Include score!
                "status": event.get("status")
            })
        
        conn.close()
        
        # Write to JSON
        CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CANDIDATES_FILE, "w") as f:
            json.dump(events, f, indent=2)
        
        result.stats["events_exported"] = len(events)
        logger.info(f"Exported {len(events)} events to {CANDIDATES_FILE}")
        
    except Exception as e:
        error_msg = f"Export failed: {e}"
        result.errors.append(error_msg)
        logger.error(error_msg)
        return False
    
    result.steps_completed.append("export")
    return True


def step_digest(result: PipelineResult, dry_run: bool = False, verbose: bool = False, 
                days_ahead: int = 7, top_n: int = 5) -> bool:
    """
    Generate digest using luma_digest.py.
    """
    logger.info("=" * 50)
    logger.info("STEP: DIGEST - Generating event digest")
    logger.info("=" * 50)
    
    if dry_run:
        logger.info("[DRY RUN] Would generate digest")
        result.steps_completed.append("digest")
        return True
    
    # Try to import and use luma_digest directly
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        import luma_digest
        
        digest_result = luma_digest.generate_digest(
            days_ahead=days_ahead,
            top_n=top_n,
            output_format="markdown"
        )
        
        if digest_result and digest_result.get("digest_text"):
            # Save digest to file
            today = datetime.now().strftime("%Y-%m-%d")
            digest_path = DIGESTS_DIR / f"events-digest-{today}.md"
            DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(digest_path, "w") as f:
                f.write(digest_result["digest_text"])
            
            result.digest_content = digest_result["digest_text"]
            result.digest_path = digest_path
            result.stats["digest_generated"] = True
            
            logger.info(f"Digest saved to {digest_path}")
            if verbose:
                logger.info(f"Digest preview:\n{digest_result['digest_text'][:500]}...")
        else:
            logger.warning("Digest generation returned empty result")
            
    except ImportError as e:
        logger.warning(f"Could not import luma_digest: {e}")
        # Fall back to subprocess
        returncode, stdout, stderr = run_script("luma_digest.py", 
            ["--days", str(days_ahead), "--top", str(top_n), "--format", "markdown"])
        
        if returncode == 0 and stdout:
            today = datetime.now().strftime("%Y-%m-%d")
            digest_path = DIGESTS_DIR / f"events-digest-{today}.md"
            DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(digest_path, "w") as f:
                f.write(stdout)
            
            result.digest_content = stdout
            result.digest_path = digest_path
            result.stats["digest_generated"] = True
            logger.info(f"Digest saved to {digest_path}")
        else:
            result.errors.append(f"Digest generation failed: {stderr}")
            logger.error(f"Digest failed: {stderr}")
            
    except Exception as e:
        result.errors.append(f"Digest error: {e}")
        logger.error(f"Digest error: {e}")
    
    result.steps_completed.append("digest")
    return True


def step_email(result: PipelineResult, dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Flag digest as ready for email delivery.
    The actual email send is done by the calling agent using send_email_to_user.
    """
    logger.info("=" * 50)
    logger.info("STEP: EMAIL - Preparing for delivery")
    logger.info("=" * 50)
    
    if not result.digest_content:
        logger.warning("No digest content available for email")
        result.steps_completed.append("email")
        return True
    
    if dry_run:
        logger.info("[DRY RUN] Would flag digest ready for email")
        result.steps_completed.append("email")
        return True
    
    result.stats["email_ready"] = True
    logger.info("Digest ready for email delivery")
    logger.info("Agent should call send_email_to_user with digest content")
    
    if verbose and result.digest_path:
        logger.info(f"Digest file: {result.digest_path}")
    
    result.steps_completed.append("email")
    return True


def run_pipeline(
    steps: list = None,
    dry_run: bool = False,
    verbose: bool = False,
    days_ahead: int = 7,
    top_n: int = 5
) -> dict:
    """
    Run the unified events pipeline.
    
    Args:
        steps: List of steps to run. Defaults to all steps.
        dry_run: If True, don't make any changes.
        verbose: If True, show detailed output.
        days_ahead: Days to look ahead for digest.
        top_n: Number of top events in digest.
    
    Returns:
        Pipeline result as dict.
    """
    if steps is None:
        steps = ALL_STEPS.copy()
    
    # Validate steps
    invalid_steps = [s for s in steps if s not in ALL_STEPS]
    if invalid_steps:
        return {
            "success": False,
            "error": f"Invalid steps: {invalid_steps}. Valid: {ALL_STEPS}"
        }
    
    result = PipelineResult()
    
    logger.info("=" * 60)
    logger.info("LUMA UNIFIED PIPELINE")
    logger.info(f"Steps: {steps}")
    logger.info(f"Dry run: {dry_run}")
    logger.info("=" * 60)
    
    step_functions = {
        "ingest": step_ingest,
        "score": step_score,
        "export": step_export,
        "digest": lambda r, d, v: step_digest(r, d, v, days_ahead, top_n),
        "email": step_email
    }
    
    for step in steps:
        if step in step_functions:
            try:
                step_functions[step](result, dry_run, verbose)
            except Exception as e:
                error_msg = f"Step {step} failed with exception: {e}"
                result.errors.append(error_msg)
                logger.error(error_msg)
                # Continue with other steps
    
    # Summary
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"Steps completed: {result.steps_completed}")
    logger.info(f"Stats: {json.dumps(result.stats, indent=2)}")
    if result.errors:
        logger.warning(f"Errors: {result.errors}")
    logger.info("=" * 60)
    
    return result.to_dict()


def main():
    parser = argparse.ArgumentParser(
        description="Luma Unified Pipeline - Single entry point for event operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 luma_unified_pipeline.py                     # Full pipeline
    python3 luma_unified_pipeline.py --steps ingest,score
    python3 luma_unified_pipeline.py --dry-run --verbose
    python3 luma_unified_pipeline.py --steps digest --days 14 --top 10
        """
    )
    
    parser.add_argument(
        "--steps",
        type=str,
        default=",".join(ALL_STEPS),
        help=f"Comma-separated list of steps to run. Options: {ALL_STEPS}"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't make any changes, just show what would happen"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days ahead for digest (default: 7)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top events in digest (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    result = run_pipeline(
        steps=steps,
        dry_run=args.dry_run,
        verbose=args.verbose,
        days_ahead=args.days,
        top_n=args.top
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()


