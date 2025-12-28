#!/usr/bin/env python3
"""
Acquisition Deal Tracking Agent - Daily Orchestrator

This script runs daily to:
1. Scan for new acquisition/partnership opportunities (semantic discovery)
2. Check tracked deals for new meetings to ingest
3. Sync meeting intelligence with context-awareness
4. Calculate momentum and deal health for all deals
5. Generate digest of changes

Designed to be run by Zo scheduled agent.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import from local modules
try:
    from airtable_config import WATCHED_ENTITIES, MEETINGS_DIR, TABLES
except ImportError:
    # Fallback if run directly
    WATCHED_ENTITIES = []
    MEETINGS_DIR = "/home/workspace/Personal/Meetings"
    TABLES = {
        "deals": "tblVvlBtY4QtmA7ss",
        "meeting_audit": "tbl2mFQSHP5bOIus4",
    }


def find_new_meetings_for_entity(entity: Dict[str, Any], already_processed: List[str]) -> List[Dict[str, Any]]:
    """Find meetings matching entity that haven't been processed yet."""
    meetings_root = Path(MEETINGS_DIR)
    matches = []
    
    # Search recent week folders
    for week_folder in sorted(meetings_root.glob("Week-of-*"), reverse=True)[:4]:
        for meeting_folder in week_folder.iterdir():
            if not meeting_folder.is_dir():
                continue
            
            folder_name = meeting_folder.name.lower()
            
            # Skip if already processed
            if meeting_folder.name in already_processed:
                continue
            
            # Check for entity alias matches
            for alias in entity["aliases"]:
                if alias.lower() in folder_name:
                    # Check for B01 file (indicates processed meeting)
                    b01_files = list(meeting_folder.glob("B01*.md"))
                    if b01_files:
                        matches.append({
                            "entity": entity["name"],
                            "meeting_folder": meeting_folder.name,
                            "meeting_path": str(meeting_folder),
                            "deal_record_id": entity["deal_record_id"],
                        })
                        break
    
    return matches


def main():
    parser = argparse.ArgumentParser(description="Daily acquisition deal tracking agent")
    parser.add_argument("--discovery-only", action="store_true", help="Only run discovery, skip sync")
    parser.add_argument("--sync-only", action="store_true", help="Only sync known entities, skip discovery")
    parser.add_argument("--json", action="store_true", help="Output as JSON for Zo processing")
    args = parser.parse_args()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "new_discoveries": [],
        "meetings_to_sync": [],
        "deal_health_updates": [],
        "summary": {
            "new_opportunities": 0,
            "meetings_found": 0,
            "deals_needing_attention": 0,
        }
    }
    
    # Step 1: Run Discovery Scanner (find NEW opportunities not in tracked entities)
    if not args.sync_only:
        logger.info("Step 1: Running semantic discovery scanner...")
        # Import and run discovery scanner
        try:
            import subprocess
            discovery_result = subprocess.run(
                ["python3", "N5/scripts/acquisition_discovery_scanner.py", "--weeks", "2", "--json"],
                capture_output=True,
                text=True,
                cwd="/home/workspace"
            )
            if discovery_result.returncode == 0:
                discovery_data = json.loads(discovery_result.stdout)
                results["new_discoveries"] = discovery_data.get("new_discoveries", [])[:5]  # Top 5
                results["summary"]["new_opportunities"] = len(results["new_discoveries"])
                logger.info(f"Found {len(results['new_discoveries'])} new opportunities")
        except Exception as e:
            logger.warning(f"Discovery scanner failed: {e}")
    
    # Step 2: Check tracked entities for new meetings
    if not args.discovery_only:
        logger.info("Step 2: Checking tracked entities for new meetings...")
        
        # Get already processed meetings from a simple cache file
        processed_cache = Path("/home/workspace/N5/data/processed_meetings.json")
        already_processed = []
        if processed_cache.exists():
            try:
                already_processed = json.loads(processed_cache.read_text())
            except:
                already_processed = []
        
        for entity in WATCHED_ENTITIES:
            new_meetings = find_new_meetings_for_entity(entity, already_processed)
            for meeting in new_meetings:
                results["meetings_to_sync"].append(meeting)
                logger.info(f"Found new meeting for {entity['name']}: {meeting['meeting_folder']}")
        
        results["summary"]["meetings_found"] = len(results["meetings_to_sync"])
    
    # Step 3: Calculate deal health for all deals (based on last meeting date)
    logger.info("Step 3: Calculating deal health...")
    today = datetime.now()
    
    for entity in WATCHED_ENTITIES:
        # Simple staleness check based on whether we found any recent meetings
        has_recent_meeting = any(
            m["entity"] == entity["name"] 
            for m in results["meetings_to_sync"]
        )
        
        # If no recent meeting and not in today's sync, flag as potentially stalling
        if not has_recent_meeting:
            results["deal_health_updates"].append({
                "deal_name": entity["name"],
                "deal_record_id": entity["deal_record_id"],
                "status": "CHECK_NEEDED",
                "reason": "No new meetings found in last 2 weeks",
            })
            results["summary"]["deals_needing_attention"] += 1
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "="*70)
        print("📊 ACQUISITION DEAL TRACKING - DAILY REPORT")
        print("="*70)
        print(f"Run time: {results['timestamp']}")
        
        if results["new_discoveries"]:
            print(f"\n🆕 NEW OPPORTUNITIES DISCOVERED: {len(results['new_discoveries'])}")
            for d in results["new_discoveries"]:
                print(f"   • [{d['date']}] {d['folder']} (score: {d['strategic_score']})")
        
        if results["meetings_to_sync"]:
            print(f"\n📥 MEETINGS TO SYNC: {len(results['meetings_to_sync'])}")
            for m in results["meetings_to_sync"]:
                print(f"   • {m['entity']}: {m['meeting_folder']}")
        
        if results["deal_health_updates"]:
            print(f"\n⚠️ DEALS NEEDING ATTENTION: {len(results['deal_health_updates'])}")
            for d in results["deal_health_updates"]:
                print(f"   • {d['deal_name']}: {d['reason']}")
        
        print("\n" + "="*70)
        print(f"Summary: {results['summary']['new_opportunities']} new opportunities, "
              f"{results['summary']['meetings_found']} meetings to sync, "
              f"{results['summary']['deals_needing_attention']} deals need attention")
        print("="*70)


if __name__ == "__main__":
    main()

