#!/usr/bin/env python3
"""
Centralized telemetry for Pulse v2.
Auto-enriches events with persona, model, conversation context.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

WORKSPACE = Path("/home/workspace")
PULSE_DIR = WORKSPACE / "N5" / "pulse"
CONFIG_PATH = WORKSPACE / "Skills" / "pulse" / "config" / "pulse_v2_config.json"
TELEMETRY_PATH = PULSE_DIR / "telemetry.jsonl"


def load_config() -> dict:
    """Load Pulse config with defaults."""
    defaults = {
        "default_build_model": "anthropic:claude-opus-4-5-20251101"
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                return {**defaults, **config}
        except:
            pass
    return defaults


def log_event(
    event_type: str,  # error, confusion, decision, requirement, preference
    data: dict,
    persona_id: str = None,
    persona_name: str = None,
    model_name: str = None,
    build_slug: str = None,
    conversation_id: str = None,
    drop_id: str = None
) -> dict:
    """
    Log event with auto-enrichment.
    
    Auto-detects:
    - used_default_model: True if model matches config default
    - timestamp: UTC ISO format
    
    Args:
        event_type: Type of event (error, confusion, decision, requirement, preference)
        data: Event-specific data dictionary
        persona_id: Persona ID (UUID)
        persona_name: Persona name (human-readable)
        model_name: Model used (e.g., anthropic:claude-opus-4-5-20251101)
        build_slug: Build identifier
        conversation_id: Conversation ID
        drop_id: Drop ID (if event from a specific Drop)
    
    Returns:
        Event dictionary that was logged
    """
    config = load_config()
    default_model = config.get("default_build_model", "anthropic:claude-opus-4-5-20251101")
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type,
        "data": data,
        "context": {
            "persona_id": persona_id,
            "persona_name": persona_name,
            "model_name": model_name,
            "used_default_model": model_name == default_model if model_name else None,
            "build_slug": build_slug,
            "conversation_id": conversation_id,
            "drop_id": drop_id
        }
    }
    
    # Append to JSONL
    TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TELEMETRY_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")
    
    return event


def query_events(
    event_type: str = None,
    build_slug: str = None,
    drop_id: str = None,
    persona_name: str = None,
    since: str = None,
    limit: int = None
) -> list:
    """
    Query telemetry events by filters.
    
    Args:
        event_type: Filter by event type
        build_slug: Filter by build slug
        drop_id: Filter by drop ID
        persona_name: Filter by persona name
        since: ISO timestamp to filter from (inclusive)
        limit: Max number of results
    
    Returns:
        List of matching events (reverse chronological)
    """
    if not TELEMETRY_PATH.exists():
        return []
    
    events = []
    with open(TELEMETRY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                events.append(event)
            except:
                continue
    
    # Filter
    filtered = events
    if event_type:
        filtered = [e for e in filtered if e.get("event_type") == event_type]
    if build_slug:
        filtered = [e for e in filtered if e.get("context", {}).get("build_slug") == build_slug]
    if drop_id:
        filtered = [e for e in filtered if e.get("context", {}).get("drop_id") == drop_id]
    if persona_name:
        filtered = [e for e in filtered if e.get("context", {}).get("persona_name") == persona_name]
    if since:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        filtered = [e for e in filtered if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) >= since_dt]
    
    # Sort reverse chronological
    filtered.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Limit
    if limit:
        filtered = filtered[:limit]
    
    return filtered


def get_event_stats(build_slug: str = None) -> dict:
    """
    Get statistics about telemetry events.
    
    Args:
        build_slug: Optional build slug to filter
    
    Returns:
        Dict with event counts by type, most recent, etc.
    """
    events = query_events(build_slug=build_slug)
    
    if not events:
        return {"total": 0, "by_type": {}, "by_persona": {}, "by_build": {}}
    
    by_type = {}
    by_persona = {}
    by_build = {}
    
    for e in events:
        etype = e.get("event_type", "unknown")
        persona = e.get("context", {}).get("persona_name", "unknown")
        build = e.get("context", {}).get("build_slug", "unknown")
        
        by_type[etype] = by_type.get(etype, 0) + 1
        by_persona[persona] = by_persona.get(persona, 0) + 1
        by_build[build] = by_build.get(build, 0) + 1
    
    return {
        "total": len(events),
        "by_type": by_type,
        "by_persona": by_persona,
        "by_build": by_build,
        "most_recent": events[0]["timestamp"] if events else None,
        "oldest": events[-1]["timestamp"] if events else None
    }


def export_build_telemetry(build_slug: str, output_path: Path = None) -> str:
    """
    Export all telemetry for a build to a file.
    
    Args:
        build_slug: Build slug to export
        output_path: Optional output path (defaults to builds/<slug>/telemetry.json)
    
    Returns:
        Path to exported file
    """
    events = query_events(build_slug=build_slug)
    
    if not output_path:
        output_path = WORKSPACE / "N5" / "builds" / build_slug / "telemetry.json"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "build_slug": build_slug,
            "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "total_events": len(events),
            "events": events
        }, f, indent=2)
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Pulse Telemetry Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log an error
  python3 N5/pulse/telemetry_manager.py log error \\
    --data '{"message": "Drop D1.1 failed validation"}' \\
    --persona-id 567cc602 --persona-name Builder \\
    --model anthropic:claude-opus-4-5-20251101 \\
    --build-slug my-build

  # Log a requirement
  python3 N5/pulse/telemetry_manager.py log requirement \\
    --data '{"text": "I want all plans reviewed before building"}' \\
    --persona-name Operator --build-slug my-build

  # Query events
  python3 N5/pulse/telemetry_manager.py query --build-slug my-build --limit 10

  # Get stats
  python3 N5/pulse/telemetry_manager.py stats --build-slug my-build

  # Export build telemetry
  python3 N5/pulse/telemetry_manager.py export my-build
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # log
    log_parser = subparsers.add_parser("log", help="Log a telemetry event")
    log_parser.add_argument("event_type", help="Event type: error, confusion, decision, requirement, preference")
    log_parser.add_argument("--data", required=True, help="Event data as JSON string")
    log_parser.add_argument("--persona-id", help="Persona ID (UUID)")
    log_parser.add_argument("--persona-name", help="Persona name")
    log_parser.add_argument("--model", help="Model used")
    log_parser.add_argument("--build-slug", help="Build slug")
    log_parser.add_argument("--conversation-id", help="Conversation ID")
    log_parser.add_argument("--drop-id", help="Drop ID")
    
    # query
    query_parser = subparsers.add_parser("query", help="Query telemetry events")
    query_parser.add_argument("--event-type", help="Filter by event type")
    query_parser.add_argument("--build-slug", help="Filter by build slug")
    query_parser.add_argument("--drop-id", help="Filter by drop ID")
    query_parser.add_argument("--persona-name", help="Filter by persona name")
    query_parser.add_argument("--since", help="ISO timestamp to filter from")
    query_parser.add_argument("--limit", type=int, help="Max results")
    
    # stats
    stats_parser = subparsers.add_parser("stats", help="Get telemetry statistics")
    stats_parser.add_argument("--build-slug", help="Filter by build slug")
    
    # export
    export_parser = subparsers.add_parser("export", help="Export build telemetry to file")
    export_parser.add_argument("build_slug", help="Build slug to export")
    export_parser.add_argument("--output", help="Optional output path")
    
    args = parser.parse_args()
    
    if args.command == "log":
        try:
            data = json.loads(args.data)
        except:
            print(f"Error: --data must be valid JSON")
            return
        
        event = log_event(
            event_type=args.event_type,
            data=data,
            persona_id=args.persona_id,
            persona_name=args.persona_name,
            model_name=args.model,
            build_slug=args.build_slug,
            conversation_id=args.conversation_id,
            drop_id=args.drop_id
        )
        
        print(f"Logged {args.event_type} event at {event['timestamp']}")
        if args.build_slug:
            print(f"Build: {args.build_slug}")
        if args.persona_name:
            print(f"Persona: {args.persona_name}")
    
    elif args.command == "query":
        events = query_events(
            event_type=args.event_type,
            build_slug=args.build_slug,
            drop_id=args.drop_id,
            persona_name=args.persona_name,
            since=args.since,
            limit=args.limit
        )
        
        if not events:
            print("No events found")
        else:
            for e in events:
                print(f"[{e['timestamp']}] {e['event_type']}")
                if e.get("context", {}).get("persona_name"):
                    print(f"  Persona: {e['context']['persona_name']}")
                if e.get("context", {}).get("build_slug"):
                    print(f"  Build: {e['context']['build_slug']}")
                print(f"  Data: {json.dumps(e['data'], indent=2)[:200]}")
                print()
    
    elif args.command == "stats":
        stats = get_event_stats(build_slug=args.build_slug)
        print(f"Total Events: {stats['total']}")
        
        if stats.get("by_type"):
            print("\nBy Type:")
            for etype, count in sorted(stats["by_type"].items(), key=lambda x: -x[1]):
                print(f"  {etype}: {count}")
        
        if stats.get("by_persona"):
            print("\nBy Persona:")
            for persona, count in sorted(stats["by_persona"].items(), key=lambda x: -x[1]):
                print(f"  {persona}: {count}")
        
        if stats.get("by_build"):
            print("\nBy Build:")
            for build, count in sorted(stats["by_build"].items(), key=lambda x: -x[1]):
                print(f"  {build}: {count}")
        
        print(f"\nTime Range:")
        print(f"  Most Recent: {stats.get('most_recent', 'N/A')}")
        print(f"  Oldest: {stats.get('oldest', 'N/A')}")
    
    elif args.command == "export":
        output = export_build_telemetry(args.build_slug, Path(args.output) if args.output else None)
        print(f"Exported {args.build_slug} telemetry to {output}")


if __name__ == "__main__":
    main()
