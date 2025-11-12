#!/usr/bin/env python3
"""
Meeting Pipeline Status Dashboard
Quick check on pipeline health and progress
"""
from pathlib import Path
from datetime import datetime

INBOX = Path("/home/workspace/Personal/Meetings/Inbox")
REQUESTS = Path("/home/workspace/N5/inbox/ai_requests")
MEETINGS = Path("/home/workspace/Personal/Meetings")

def main():
    # Count files
    inbox_count = len(list(INBOX.glob("*.transcript.md")))
    request_count = len(list(REQUESTS.glob("meeting_*.json")))
    meeting_folders = len([d for d in MEETINGS.iterdir() if d.is_dir() and "transcript" in d.name.lower()])
    
    print("=" * 60)
    print("📊 MEETING PIPELINE STATUS")
    print("=" * 60)
    print(f"\n📥 Inbox: {inbox_count} transcripts waiting")
    print(f"⏳ Queue: {request_count} AI requests pending")
    print(f"✅ Complete: {meeting_folders} meeting folders created")
    
    if inbox_count > 0:
        rate = 6  # 6 per hour (1 every 10 min)
        hours = inbox_count / rate
        print(f"\n⏱️  Processing rate: {rate}/hour")
        print(f"📅 Est. completion: ~{hours:.1f} hours")
    
    print("\n" + "=" * 60)
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S ET')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
