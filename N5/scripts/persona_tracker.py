#!/usr/bin/env python3
"""
Persona Time Tracker
Tracks how long each persona has been active in a conversation.
Alerts when a specialist persona has been active too long without returning to Operator.

Usage:
    python3 persona_tracker.py start <persona_id> --convo <convo_id>
    python3 persona_tracker.py check --convo <convo_id>
    python3 persona_tracker.py end <persona_id> --convo <convo_id>
    python3 persona_tracker.py status --convo <convo_id>
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

WORKSPACE_BASE = Path("/home/.z/workspaces")

# Thresholds (in exchanges/turns)
EXCHANGE_WARNING_THRESHOLD = 5  # Warn after 5 exchanges in specialist mode
EXCHANGE_ALERT_THRESHOLD = 8   # Strong alert after 8 exchanges

# Operator doesn't count for tracking
OPERATOR_ID = "90a7486f-46f9-41c9-a98c-21931fa5c5f6"

PERSONA_NAMES = {
    "90a7486f-46f9-41c9-a98c-21931fa5c5f6": "Operator",
    "39309f92-3f9e-448e-81e2-f23eef5c873c": "Strategist",
    "567cc602-060b-4251-91e7-40be591b9bc3": "Builder",
    "88d70597-80f3-4b3e-90c1-da2c99da7f1f": "Teacher",
    "5cbe0dd8-9bfb-4cff-b2da-23112572a6b8": "Writer",
    "17def82c-ca82-4c03-9c98-4994e79f785a": "Debugger",
    "74e0a70d-398a-4337-bcab-3e5a3a9d805c": "Architect",
    "d0f04503-3ab4-447f-ba24-e02611993d90": "Researcher",
    "76cccdcd-2709-490a-84a3-ca67c9852a82": "Level Upper",
    "9790ca46-ae01-4ad5-b2eb-a5e72aeb22e7": "Coach",
    "1bb66f53-9e2a-4152-9b18-75c2ee2c25a3": "Librarian",
    "c545cc7a-ccbf-47ff-8c50-cb61b3c2eae3": "Trainer",
    "f25038f1-114c-4f77-8bd2-40f1ed07182d": "Nutritionist",
}


def get_tracker_path(convo_id: str) -> Path:
    """Get path to the persona tracker file for a conversation."""
    return WORKSPACE_BASE / convo_id / "PERSONA_TRACKER.json"


def load_tracker(convo_id: str) -> dict:
    """Load or initialize the tracker for a conversation."""
    path = get_tracker_path(convo_id)
    if path.exists():
        return json.loads(path.read_text())
    return {
        "conversation_id": convo_id,
        "current_persona": None,
        "current_persona_started": None,
        "exchange_count": 0,
        "history": [],
        "warnings_issued": []
    }


def save_tracker(convo_id: str, tracker: dict):
    """Save the tracker state."""
    path = get_tracker_path(convo_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tracker, indent=2, default=str))


def start_persona(convo_id: str, persona_id: str):
    """Record that a persona has become active."""
    tracker = load_tracker(convo_id)
    now = datetime.now(timezone.utc).isoformat()
    
    # If switching from another persona, record the end
    if tracker["current_persona"] and tracker["current_persona"] != persona_id:
        tracker["history"].append({
            "persona_id": tracker["current_persona"],
            "persona_name": PERSONA_NAMES.get(tracker["current_persona"], "Unknown"),
            "started": tracker["current_persona_started"],
            "ended": now,
            "exchanges": tracker["exchange_count"]
        })
    
    # Start tracking new persona
    tracker["current_persona"] = persona_id
    tracker["current_persona_started"] = now
    tracker["exchange_count"] = 0
    
    save_tracker(convo_id, tracker)
    
    persona_name = PERSONA_NAMES.get(persona_id, persona_id[:8])
    print(f"✓ Started tracking: {persona_name}")
    
    if persona_id == OPERATOR_ID:
        print("  (Operator - no time limits)")
    else:
        print(f"  Warning threshold: {EXCHANGE_WARNING_THRESHOLD} exchanges")


def increment_exchange(convo_id: str) -> dict:
    """
    Increment the exchange counter and return warnings if thresholds exceeded.
    Call this at the start of each AI response.
    """
    tracker = load_tracker(convo_id)
    
    if not tracker["current_persona"]:
        return {"status": "no_persona_tracked"}
    
    # Don't track Operator exchanges
    if tracker["current_persona"] == OPERATOR_ID:
        return {"status": "operator_active", "message": "Operator active - no limits"}
    
    tracker["exchange_count"] += 1
    count = tracker["exchange_count"]
    persona_name = PERSONA_NAMES.get(tracker["current_persona"], "Unknown")
    
    result = {
        "status": "ok",
        "persona": persona_name,
        "persona_id": tracker["current_persona"],
        "exchange_count": count
    }
    
    # Check thresholds
    if count >= EXCHANGE_ALERT_THRESHOLD:
        result["status"] = "alert"
        result["message"] = (
            f"⚠️ ALERT: {persona_name} has been active for {count} exchanges. "
            f"Consider returning to Operator: set_active_persona(\"{OPERATOR_ID}\")"
        )
        tracker["warnings_issued"].append({
            "type": "alert",
            "exchange": count,
            "time": datetime.now(timezone.utc).isoformat()
        })
    elif count >= EXCHANGE_WARNING_THRESHOLD:
        result["status"] = "warning"
        result["message"] = (
            f"⏰ WARNING: {persona_name} has been active for {count} exchanges. "
            f"Is the task complete? Should you return to Operator?"
        )
        # Only add warning once per session
        if not any(w["type"] == "warning" for w in tracker["warnings_issued"]):
            tracker["warnings_issued"].append({
                "type": "warning",
                "exchange": count,
                "time": datetime.now(timezone.utc).isoformat()
            })
    
    save_tracker(convo_id, tracker)
    return result


def check_status(convo_id: str) -> dict:
    """Check current persona tracking status."""
    tracker = load_tracker(convo_id)
    
    if not tracker["current_persona"]:
        return {"status": "no_persona_tracked", "message": "No persona currently tracked"}
    
    persona_name = PERSONA_NAMES.get(tracker["current_persona"], "Unknown")
    count = tracker["exchange_count"]
    
    result = {
        "current_persona": persona_name,
        "persona_id": tracker["current_persona"],
        "exchange_count": count,
        "started": tracker["current_persona_started"],
        "is_operator": tracker["current_persona"] == OPERATOR_ID,
        "history_count": len(tracker["history"])
    }
    
    if not result["is_operator"]:
        if count >= EXCHANGE_ALERT_THRESHOLD:
            result["status"] = "overdue"
        elif count >= EXCHANGE_WARNING_THRESHOLD:
            result["status"] = "warning"
        else:
            result["status"] = "ok"
    else:
        result["status"] = "operator"
    
    return result


def end_persona(convo_id: str, persona_id: str):
    """Record that a persona session has ended (returning to Operator)."""
    tracker = load_tracker(convo_id)
    now = datetime.now(timezone.utc).isoformat()
    
    if tracker["current_persona"]:
        tracker["history"].append({
            "persona_id": tracker["current_persona"],
            "persona_name": PERSONA_NAMES.get(tracker["current_persona"], "Unknown"),
            "started": tracker["current_persona_started"],
            "ended": now,
            "exchanges": tracker["exchange_count"]
        })
    
    # Reset tracking
    tracker["current_persona"] = OPERATOR_ID
    tracker["current_persona_started"] = now
    tracker["exchange_count"] = 0
    tracker["warnings_issued"] = []
    
    save_tracker(convo_id, tracker)
    print(f"✓ Returned to Operator. Tracking reset.")


def show_status(convo_id: str):
    """Display current tracking status."""
    status = check_status(convo_id)
    
    print("=" * 50)
    print("PERSONA TRACKER STATUS")
    print("=" * 50)
    
    if status.get("status") == "no_persona_tracked":
        print("No persona currently tracked for this conversation.")
        return
    
    print(f"Current Persona: {status['current_persona']}")
    print(f"Persona ID: {status['persona_id'][:8]}...")
    print(f"Exchanges: {status['exchange_count']}")
    print(f"Started: {status['started']}")
    print(f"Status: {status['status'].upper()}")
    
    if status['status'] == "warning":
        print(f"\n⏰ WARNING: Consider returning to Operator soon")
    elif status['status'] == "overdue":
        print(f"\n⚠️ ALERT: Specialist persona active too long!")
        print(f"   Return to Operator: set_active_persona(\"{OPERATOR_ID}\")")
    
    if status['history_count'] > 0:
        print(f"\nPrevious personas this conversation: {status['history_count']}")


def main():
    parser = argparse.ArgumentParser(description="Track persona duration in conversations")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Start tracking a persona")
    start_parser.add_argument("persona_id", help="Persona ID to track")
    start_parser.add_argument("--convo", required=True, help="Conversation ID")
    
    # check command
    check_parser = subparsers.add_parser("check", help="Check current status")
    check_parser.add_argument("--convo", required=True, help="Conversation ID")
    check_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # increment command
    inc_parser = subparsers.add_parser("increment", help="Increment exchange counter")
    inc_parser.add_argument("--convo", required=True, help="Conversation ID")
    inc_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # end command
    end_parser = subparsers.add_parser("end", help="End persona tracking (return to Operator)")
    end_parser.add_argument("persona_id", nargs="?", help="Persona ID that ended")
    end_parser.add_argument("--convo", required=True, help="Conversation ID")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show detailed status")
    status_parser.add_argument("--convo", required=True, help="Conversation ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "start":
        start_persona(args.convo, args.persona_id)
    elif args.command == "check":
        result = check_status(args.convo)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            show_status(args.convo)
    elif args.command == "increment":
        result = increment_exchange(args.convo)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("message"):
                print(result["message"])
            else:
                print(f"Exchange {result.get('exchange_count', '?')} for {result.get('persona', 'unknown')}")
    elif args.command == "end":
        end_persona(args.convo, args.persona_id)
    elif args.command == "status":
        show_status(args.convo)


if __name__ == "__main__":
    main()

