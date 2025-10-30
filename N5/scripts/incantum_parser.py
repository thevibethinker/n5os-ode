#!/usr/bin/env python3
"""
Incantum Helper - Registry Loading and Pattern Logging
Simple utilities for the incantum system - parsing is done by the LLM directly.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Paths
N5_ROOT = Path("/home/workspace/N5")
COMMANDS_REGISTRY = N5_ROOT / "config/recipes.jsonl"
SHORTCUTS_FILE = N5_ROOT / "config/incantum_shortcuts.json"
PATTERNS_FILE = N5_ROOT / "logs/incantum_patterns.jsonl"


def load_commands_registry() -> Dict[str, dict]:
    """Load command registry from recipes.jsonl."""
    commands = {}
    
    if not COMMANDS_REGISTRY.exists():
        logger.error(f"Commands registry not found: {COMMANDS_REGISTRY}")
        return commands
    
    with open(COMMANDS_REGISTRY) as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    cmd = json.loads(line)
                    if "command" in cmd:
                        commands[cmd["command"]] = cmd
                    else:
                        logger.warning(f"Line {line_num}: Missing 'command' field, skipping")
                except json.JSONDecodeError as e:
                    logger.warning(f"Line {line_num}: Malformed JSON: {e}")
    
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
    query_lower = query.lower()
    
    with open(PATTERNS_FILE) as f:
        for line in f:
            if line.strip():
                pattern = json.loads(line)
                # Simple substring match - LLM can do better semantic matching
                if query_lower in pattern["natural_language"].lower():
                    patterns.append(pattern)
    
    # Return most recent matches
    patterns.sort(key=lambda p: p["timestamp"], reverse=True)
    return patterns[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Incantum helper utilities"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Load registry
    load_parser = subparsers.add_parser('load-registry', help='Load commands registry')
    load_parser.add_argument('--format', choices=['json', 'list'], default='json',
                            help='Output format')
    
    # Load shortcuts
    shortcuts_parser = subparsers.add_parser('load-shortcuts', help='Load user shortcuts')
    
    # Log pattern
    log_parser = subparsers.add_parser('log', help='Log a successful pattern')
    log_parser.add_argument('natural_language', help='Natural language instruction')
    log_parser.add_argument('--commands', required=True, help='Commands as JSON array')
    log_parser.add_argument('--context', type=json.loads, help='Context as JSON')
    log_parser.add_argument('--feedback', help='User feedback')
    log_parser.add_argument('--failed', action='store_true', help='Mark as failed attempt')
    
    # Search patterns
    search_parser = subparsers.add_parser('search', help='Search historical patterns')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    args = parser.parse_args()
    
    if args.command == 'load-registry':
        commands = load_commands_registry()
        if args.format == 'json':
            print(json.dumps(commands, indent=2))
        else:
            for cmd_name in sorted(commands.keys()):
                cmd = commands[cmd_name]
                desc = cmd.get('description', 'No description')
                print(f"{cmd_name}: {desc}")
        return 0
    
    elif args.command == 'load-shortcuts':
        shortcuts = load_shortcuts()
        print(json.dumps(shortcuts, indent=2))
        return 0
    
    elif args.command == 'log':
        commands = json.loads(args.commands)
        log_pattern(
            args.natural_language,
            commands,
            args.context,
            success=not args.failed,
            user_feedback=args.feedback
        )
        print("✓ Pattern logged")
        return 0
    
    elif args.command == 'search':
        patterns = search_patterns(args.query, args.limit)
        print(json.dumps(patterns, indent=2))
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
