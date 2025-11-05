"""
Huey queue configuration for meeting ingestion pipeline
"""
from huey import SqliteHuey
from pathlib import Path

# Queue database location
QUEUE_DB = Path("/home/workspace/N5/data/huey_queue.db")
QUEUE_DB.parent.mkdir(parents=True, exist_ok=True)

# Create Huey instance
huey = SqliteHuey(
    name='meeting_ingestion',
    filename=str(QUEUE_DB),
    immediate=False,      # Async execution
    results=True,         # Store task results
    store_none=False,     # Don't store None results
    utc=False,            # Use local timezone
    immediate_use_memory=True  # For testing
)
