#!/usr/bin/env python3
"""
Meeting State Manager
Tracks processed calendar events to prevent duplicate research
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import pytz

STATE_FILE = Path("/home/workspace/Personal/Meetings/.processed.json")
TIMEZONE = pytz.timezone('America/New_York')


def _get_timestamp() -> str:
    """Get current timestamp in ET timezone"""
    return datetime.now(TIMEZONE).isoformat()


def _ensure_directory() -> None:
    """Ensure state file directory exists"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _initialize_state() -> dict:
    """Create initial state structure"""
    return {
        "last_poll": _get_timestamp(),
        "processed_events": {}
    }


def load_state() -> dict:
    """
    Load last poll state from .processed.json
    Returns: dict with 'last_poll' and 'processed_events'
    Creates file if doesn't exist
    """
    _ensure_directory()
    
    if not STATE_FILE.exists():
        state = _initialize_state()
        save_state(state)
        return state
    
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        
        # Validate structure
        if 'last_poll' not in state or 'processed_events' not in state:
            raise ValueError("Invalid state structure")
        
        return state
    
    except (json.JSONDecodeError, ValueError) as e:
        # File corrupted - create backup and reinitialize
        backup_path = STATE_FILE.with_suffix('.json.backup')
        if STATE_FILE.exists():
            shutil.copy2(STATE_FILE, backup_path)
            print(f"⚠️  Corrupted state file backed up to {backup_path}")
        
        state = _initialize_state()
        save_state(state)
        print(f"🔄 State file reinitialized")
        return state


def save_state(state: dict) -> None:
    """
    Save updated state to .processed.json
    Args:
        state: dict with 'last_poll' and 'processed_events'
    """
    _ensure_directory()
    
    # Atomic write: write to temp file, then rename
    temp_file = STATE_FILE.with_suffix('.json.tmp')
    
    try:
        with open(temp_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        # Atomic rename
        temp_file.replace(STATE_FILE)
        
    except Exception as e:
        # Clean up temp file if it exists
        if temp_file.exists():
            temp_file.unlink()
        raise e


def add_processed_event(event_id: str, event_data: dict) -> None:
    """
    Mark event as processed
    Args:
        event_id: Calendar event ID
        event_data: dict with title, priority, stakeholder_profiles, etc.
    """
    state = load_state()
    
    # Add processed timestamp if not provided
    if 'processed_at' not in event_data:
        event_data['processed_at'] = _get_timestamp()
    
    # Add to processed events
    state['processed_events'][event_id] = event_data
    
    # Update last poll time
    state['last_poll'] = _get_timestamp()
    
    save_state(state)
    print(f"✅ Event {event_id} marked as processed: {event_data.get('title', 'Unknown')}")


def is_event_processed(event_id: str) -> bool:
    """
    Check if event already processed
    Args:
        event_id: Calendar event ID
    Returns: True if already processed
    """
    state = load_state()
    return event_id in state['processed_events']


def get_processed_event(event_id: str) -> Optional[dict]:
    """
    Get details of a processed event
    Args:
        event_id: Calendar event ID
    Returns: Event data dict if found, None otherwise
    """
    state = load_state()
    return state['processed_events'].get(event_id)


def get_all_processed_events() -> dict:
    """
    Get all processed events
    Returns: dict of event_id -> event_data
    """
    state = load_state()
    return state['processed_events']


def update_last_poll() -> None:
    """Update last poll timestamp"""
    state = load_state()
    state['last_poll'] = _get_timestamp()
    save_state(state)


if __name__ == "__main__":
    # Quick test
    print("Testing meeting_state_manager...")
    
    # Test load/save
    state = load_state()
    print(f"✓ State loaded: {len(state['processed_events'])} events")
    
    # Test add event
    test_event_id = "test_event_123"
    if not is_event_processed(test_event_id):
        add_processed_event(test_event_id, {
            'title': 'Test Meeting',
            'priority': 'normal',
            'stakeholder_profiles': []
        })
    
    # Test check processed
    assert is_event_processed(test_event_id)
    print(f"✓ Event processing test passed")
    
    print("\n✅ All basic tests passed!")
