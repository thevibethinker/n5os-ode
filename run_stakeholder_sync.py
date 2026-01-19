import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add N5/scripts to path
sys.path.append('/home/workspace/N5/scripts')

from auto_create_stakeholder_profiles import process_calendar_events, create_stakeholder_profile_auto, is_external_email

def run_sync(events_data):
    print("=== Auto-Create Stakeholder Profiles (Zo Orchestrated) ===")
    
    # Process events to extract new external stakeholders
    new_stakeholders = process_calendar_events(events_data)
    
    if not new_stakeholders:
        print("✓ No new external stakeholders found in upcoming meetings.")
        return
    
    print(f"Found {len(new_stakeholders)} new external stakeholders.")
    
    profiles_created = []
    
    for stakeholder in new_stakeholders:
        email = stakeholder['email']
        name = stakeholder['name']
        
        # Double check external
        if not is_external_email(email):
            continue
            
        print(f"Creating profile for: {name} ({email})...")
        try:
            # create_stakeholder_profile_auto handles history fetch, LLM analysis, and DB tracking
            profile_path = create_stakeholder_profile_auto(
                email=email,
                name=name,
                calendar_event=stakeholder
            )
            profiles_created.append(str(profile_path))
        except Exception as e:
            print(f"Error creating profile for {email}: {e}")
            
    print("\n=== Summary ===")
    print(f"Profiles created: {len(profiles_created)}")
    for p in profiles_created:
        print(f" - {p}")

if __name__ == "__main__":
    # Load events from the saved file
    events_file = '/home/.z/workspaces/con_Jl6HP8ZHQEaKY5ig/app_responses/google_calendar~~3ause_app_google_calendar_core.txt'
    
    # We need to extract the JSON list from the file content
    with open(events_file, 'r') as f:
        content = f.read()
        
    # The file contains a mix of text and the actual response data
    # We look for the 'ret=[' part and extract it
    import re
    match = re.search(r'ret=(\[.*\]) stash_id', content, re.DOTALL)
    if match:
        events_json = match.group(1)
        # Note: The output might have single quotes instead of double quotes
        # We need to be careful with eval vs json.loads
        try:
            # The 'ret' part in the tool output is a Python list representation
            # We can use ast.literal_eval safely if it's not strictly JSON
            import ast
            events = ast.literal_eval(events_json)
            run_sync(events)
        except Exception as e:
            print(f"Failed to parse events: {e}")
    else:
        print("Could not find events list in response file.")
