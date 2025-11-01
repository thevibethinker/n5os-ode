#!/usr/bin/env python3
"""
Incantum Helper - Registry Loading and Pattern Logging
Simple utilities for the incantum system - parsing is done by the LLM directly.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from executable_manager import list_executables, search_executables, Executable

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
SHORTCUTS_FILE = N5_ROOT / "config/incantum_shortcuts.json"
PATTERNS_FILE = N5_ROOT / "logs/incantum_patterns.jsonl"


def load_commands_registry() -> Dict[str, Executable]:
    """Load command registry from executables.db using executable_manager."""
    executables = list_executables()
    
    # Convert to dict keyed by name for backward compatibility
    commands = {exe.name: exe for exe in executables}
    
    logger.info(f"Loaded {len(commands)} commands from registry")
    return commands


def load_shortcuts() -> Dict[str, List[str]]:
    """Load user-defined shortcuts."""
    if not SHORTCUTS_FILE.exists():
        logger.info("No shortcuts file found, returning empty dict")
        return {}
    
    with open(SHORTCUTS_FILE) as f:
        shortcuts = json.load(f)
    
    logger.info(f"Loaded {len(shortcuts)} shortcuts")
    return shortcuts


def log_pattern(
    natural_language: str,
    commands: List[Dict],
    context: Optional[Dict] = None,
    success: bool = True,
    user_feedback: Optional[str] = None
) -> None:
    """
    Log a successful (or failed) pattern for future reference.
    
    Args:
        natural_language: The original NL instruction
        commands: List of commands that were executed (format: [{"name": "cmd", "args": {...}}])
        context: Optional context dict
        success: Whether the execution succeeded
        user_feedback: Optional feedback from user
    """
    PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    pattern = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "natural_language": natural_language,
        "commands": commands,
        "context": context or {},
        "success": success,
        "user_feedback": user_feedback
    }
    
    with open(PATTERNS_FILE, "a") as f:
        f.write(json.dumps(pattern) + "\n")
    
    logger.info(f"Logged pattern: '{natural_language}' → {len(commands)} command(s)")


def search_patterns(query: str, limit: int = 10) -> List[Dict]:
    """Search historical patterns for similar instructions."""
    if not PATTERNS_FILE.exists():
        return []
    
    patterns = []
    with open(PATTERNS_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    patterns.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    
    # Simple substring matching (could be improved with fuzzy matching)
    query_lower = query.lower()
    matching = [
        p for p in patterns
        if query_lower in p.get("natural_language", "").lower()
    ]
    
    # Return most recent matches
    return sorted(matching, key=lambda p: p.get("timestamp", ""), reverse=True)[:limit]


def main():
    """CLI for testing incantum helper functions."""
    parser = argparse.ArgumentParser(description="Incantum Helper Utilities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Load registry
    load_parser = subparsers.add_parser("load", help="Load and display commands registry")
    
    # Search patterns
    search_parser = subparsers.add_parser("search", help="Search historical patterns")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    
    # Log pattern
    log_parser = subparsers.add_parser("log", help="Log a new pattern")
    log_parser.add_argument("natural_language", help="Natural language instruction")
    log_parser.add_argument("--commands", required=True, help="JSON array of commands")
    log_parser.add_argument("--success", action="store_true", default=True)
    log_parser.add_argument("--feedback", help="User feedback")
    
    args = parser.parse_args()
    
    if args.command == "load":
        commands = load_commands_registry()
        print(f"Loaded {len(commands)} commands:")
        for name, exe in list(commands.items())[:10]:
            print(f"  - {name}: {exe.description or 'No description'}")
        if len(commands) > 10:
            print(f"  ... and {len(commands) - 10} more")
    
    elif args.command == "search":
        results = search_patterns(args.query, args.limit)
        print(f"Found {len(results)} matching patterns:")
        for p in results:
            print(f"\n  NL: {p['natural_language']}")
            print(f"  Commands: {[c.get('name') for c in p.get('commands', [])]}")
            print(f"  Timestamp: {p.get('timestamp')}")
            print(f"  Success: {p.get('success')}")
    
    elif args.command == "log":
        try:
            commands = json.loads(args.commands)
            log_pattern(
                args.natural_language,
                commands,
                success=args.success,
                user_feedback=args.feedback
            )
            print("✓ Pattern logged successfully")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for commands: {e}", file=sys.stderr)
            return 1
    
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
