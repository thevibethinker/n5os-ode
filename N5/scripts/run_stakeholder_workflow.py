import sys
import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Add N5/scripts to path
sys.path.insert(0, '/home/workspace/N5/scripts')

from auto_create_stakeholder_profiles import process_calendar_events, create_stakeholder_profile_auto

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main():
    # Load the events we fetched earlier
    events_file = Path('/home/workspace/N5/scripts/calendar_events.json')
    if not events_file.exists():
        logger.error("Calendar events file not found.")
        return

    with open(events_file, 'r') as f:
        events = json.load(f)

    logger.info(f"Processing {len(events)} calendar events...")
    new_stakeholders = process_calendar_events(events)

    if not new_stakeholders:
        logger.info("No new external stakeholders found.")
        return

    logger.info(f"Found {len(new_stakeholders)} new stakeholders. Creating profiles...")
    
    profiles_created = []
    for stakeholder in new_stakeholders:
        try:
            profile_path = create_stakeholder_profile_auto(
                email=stakeholder['email'],
                name=stakeholder['name'],
                calendar_event=stakeholder
            )
            profiles_created.append({
                'name': stakeholder['name'],
                'email': stakeholder['email'],
                'path': str(profile_path)
            })
        except Exception as e:
            logger.error(f"Failed to create profile for {stakeholder['email']}: {e}")

    # Output results for the AI to pick up
    print(json.dumps({
        'status': 'success',
        'profiles_created': profiles_created
    }))

if __name__ == "__main__":
    main()
