#!/usr/bin/env python3
"""
Luma Orchestrator - The "Brain" of the Luma Automation.
1. Discovery (via browser_runner)
2. Storage (via luma_db)
3. Mechanical Scoring (via luma_scorer)
4. Candidate Export (for Agent LLM)
"""
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

# Add N5/scripts to path to allow imports
sys.path.append(str(Path(__file__).parent))

import luma_db
import luma_scorer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("luma_orchestrator")

N5_ROOT = Path("/home/workspace/N5")
RUNNER_PATH = N5_ROOT / "scripts" / "browser_runner.py"
JOB_FILE = N5_ROOT / "data" / "luma_job.json"
RESULT_FILE = N5_ROOT / "data" / "luma_result.json"
CANDIDATES_FILE = N5_ROOT / "data" / "luma_candidates.json"

TARGET_CITIES = ["sf", "nyc"]  # Configurable

def run_discovery(city: str):
    """Run browser_runner for a city."""
    logger.info(f"Running discovery for {city}...")
    
    # Create job file
    job = {
        "task": "luma_list_city_events",
        "params": {"city": city}
    }
    JOB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOB_FILE, "w") as f:
        json.dump(job, f)
        
    # Run script
    try:
        subprocess.run(
            [sys.executable, str(RUNNER_PATH), "--job-file", str(JOB_FILE), "--output", str(RESULT_FILE)],
            check=True,
            capture_output=True
        )
        
        # Load result
        with open(RESULT_FILE) as f:
            data = json.load(f)
            
        return data.get("result", [])
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Discovery failed for {city}: {e.stderr.decode()}")
        return []
    except Exception as e:
        logger.exception(f"Unexpected error in discovery: {e}")
        return []

def main():
    luma_db.init_db()
    
    total_new = 0
    
    # 0. Email Ingestion (Allowlist)
    EMAIL_FILE = N5_ROOT / "data" / "pending_emails.json"
    DISCOVERY_SCRIPT = N5_ROOT / "scripts" / "luma_email_discovery.py"
    
    if EMAIL_FILE.exists():
        logger.info("Found pending emails, running email discovery...")
        try:
            # Run the discovery script
            subprocess.run(
                [sys.executable, str(DISCOVERY_SCRIPT), "--email-file", str(EMAIL_FILE)],
                check=True
            )
            # Remove file after successful processing to prevent re-runs
            EMAIL_FILE.unlink()
            logger.info("Email processing complete. Removed pending file.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Email discovery failed: {e}")
        except Exception as e:
            logger.error(f"Error during email processing: {e}")

    # 1. Discovery
    for city in TARGET_CITIES:
        events = run_discovery(city)
        if not events:
            continue
            
        # Transform for DB (browser_runner returns simple dicts, need ID)
        db_events = []
        for ev in events:
            # Generate ID from URL slug if possible, else random
            # URL is like https://lu.ma/slug?k=c
            try:
                slug = ev["url"].split("lu.ma/")[-1].split("?")[0]
                ev["id"] = slug
                ev["city"] = city
                db_events.append(ev)
            except:
                continue
                
        # 2. Storage
        stats = luma_db.save_events(db_events)
        logger.info(f"Saved {city}: {stats}")
        total_new += stats["inserted"]

    # 2.5 Smart Detector (Tier 2) - Catch events from non-allowlisted sources
    DETECTED_FILE = N5_ROOT / "data" / "tier2_emails.json"
    DETECTOR_SCRIPT = N5_ROOT / "scripts" / "smart_event_detector.py"
    
    if DETECTED_FILE.exists():
        logger.info("Found Tier 2 detected emails, processing...")
        try:
            subprocess.run(
                [sys.executable, str(DETECTOR_SCRIPT), "--email-file", str(DETECTED_FILE)],
                check=True
            )
            DETECTED_FILE.unlink()
            logger.info("Tier 2 detection complete.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Smart detector failed: {e}")
        except Exception as e:
            logger.error(f"Error during Tier 2 processing: {e}")

    # 3. Mechanical Scoring
    scored = luma_scorer.score_all_pending()
    logger.info(f"Scored {len(scored)} pending events")
    
    # 4. Candidate Export
    # Get top 20 candidates across all cities
    top_events = luma_scorer.get_top_recommendations(limit=20)
    
    with open(CANDIDATES_FILE, "w") as f:
        json.dump(top_events, f, indent=2)
        
    logger.info(f"Exported {len(top_events)} candidates to {CANDIDATES_FILE}")
    print(f"Luma Orchestration Complete. {total_new} new events found. {len(top_events)} candidates ready for Agent review.")

if __name__ == "__main__":
    main()




