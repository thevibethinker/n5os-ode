#!/usr/bin/env python3
"""
N5 Preference Loader Utility

Loads preferences based on context, respecting the precedence hierarchy.

Supports caching for improved performance when preferences are loaded
repeatedly (e.g., by multiple scripts in a session).
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:
    print("PyYAML not installed. Install it with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# Add workspace to path for N5 lib imports
sys.path.insert(0, '/home/workspace')

# Try to import caching (optional - falls back to direct loading)
try:
    from N5.lib.cache import (
        get_cached_hub,
        get_cached_preferences,
        get_cache_stats,
        clear_all_caches
    )
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False

# Paths
WORKSPACE = Path("/home/workspace")
ROOT = Path(__file__).resolve().parents[1]
HUB_FILE = ROOT / "config" / "user_preferences.yaml"


def load_hub(use_cache: bool = True) -> Dict[str, Any]:
    """Load the preferences hub file.

    Args:
        use_cache: Use cached version if available (default: True)
    """
    if use_cache and HAS_CACHE:
        hub = get_cached_hub()
        if hub is not None:
            return hub

    # Fall back to direct loading
    if not HUB_FILE.exists():
        print(f"Error: Hub file not found: {HUB_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(HUB_FILE, "r") as f:
        return yaml.safe_load(f)


def load_overrides(hub: Dict[str, Any]) -> Dict[str, Any]:
    """Load user overrides if specified."""
    overrides_path = hub.get("overrides_file")
    if not overrides_path:
        return {}

    overrides_file = WORKSPACE / overrides_path
    if not overrides_file.exists():
        return {}

    with open(overrides_file, "r") as f:
        return yaml.safe_load(f) or {}


def get_modules_for_context(hub: Dict[str, Any], context: str) -> List[str]:
    """Get list of module names to load for a given context."""
    contexts = hub.get("contexts", {})

    if context not in contexts:
        print(f"Warning: Unknown context '{context}'. Available: {list(contexts.keys())}", file=sys.stderr)
        return []

    ctx_config = contexts[context]
    load_spec = ctx_config.get("load", [])

    if load_spec == "all":
        # Load all non-deprecated modules
        return [
            name for name, config in hub.get("modules", {}).items()
            if not config.get("deprecated", False)
        ]

    return load_spec


def get_always_loaded_modules(hub: Dict[str, Any]) -> List[str]:
    """Get modules that should always be loaded."""
    always = []
    for name, config in hub.get("modules", {}).items():
        if config.get("load") == "always" and not config.get("deprecated", False):
            always.append(name)
    return always


def load_module_content(module_path: str) -> Optional[str]:
    """Load content of a module file."""
    full_path = WORKSPACE / module_path
    if not full_path.exists():
        return None

    with open(full_path, "r") as f:
        return f.read()


def resolve_preferences(hub: Dict[str, Any], context: str, include_content: bool = False,
                        use_cache: bool = True) -> Dict[str, Any]:
    """
    Resolve preferences for a given context.

    Args:
        hub: Loaded hub configuration (ignored if use_cache=True and cache available)
        context: Context name
        include_content: Include module file contents
        use_cache: Use cached resolution if available (default: True)

    Returns:
        Dict with:
        - core: Core preferences
        - modules: List of module configs to load
        - overrides: User overrides
        - content: Dict of module_name -> file content (if include_content=True)
    """
    # Try cached resolution first
    if use_cache and HAS_CACHE:
        return get_cached_preferences(context, include_content)
    result = {
        "context": context,
        "core": hub.get("core", {}),
        "precedence": hub.get("precedence", []),
        "modules": [],
        "overrides": {},
        "content": {}
    }

    # Get always-loaded modules
    always_modules = get_always_loaded_modules(hub)

    # Get context-specific modules
    context_modules = get_modules_for_context(hub, context) if context else []

    # Combine and dedupe
    all_module_names = list(dict.fromkeys(always_modules + context_modules))

    # Build module list with full config
    modules_config = hub.get("modules", {})
    for name in all_module_names:
        if name in modules_config:
            module = modules_config[name].copy()
            module["name"] = name
            result["modules"].append(module)

            if include_content:
                content = load_module_content(module["path"])
                if content:
                    result["content"][name] = content

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    result["modules"].sort(key=lambda m: priority_order.get(m.get("priority", "low"), 3))

    # Load overrides
    result["overrides"] = load_overrides(hub)

    return result


def list_contexts(hub: Dict[str, Any]) -> None:
    """Print available contexts."""
    contexts = hub.get("contexts", {})
    print("\nAvailable contexts:\n")
    for name, config in contexts.items():
        desc = config.get("description", "No description")
        load_count = len(config.get("load", [])) if isinstance(config.get("load"), list) else "all"
        print(f"  {name:20} ({load_count} modules)")
        print(f"    {desc}\n")


def list_modules(hub: Dict[str, Any]) -> None:
    """Print all registered modules."""
    modules = hub.get("modules", {})
    print("\nRegistered modules:\n")

    # Group by priority
    by_priority = {"critical": [], "high": [], "medium": [], "low": []}
    for name, config in modules.items():
        priority = config.get("priority", "low")
        by_priority[priority].append((name, config))

    for priority in ["critical", "high", "medium", "low"]:
        if by_priority[priority]:
            print(f"[{priority.upper()}]")
            for name, config in by_priority[priority]:
                status = " (deprecated)" if config.get("deprecated") else ""
                load = config.get("load", [])
                load_str = "always" if load == "always" else f"{len(load)} contexts"
                print(f"  {name:30} {load_str:15}{status}")
                print(f"    {config.get('description', 'No description')}")
            print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N5 Preference Loader",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Load command
    load_parser = subparsers.add_parser("load", help="Load preferences for a context")
    load_parser.add_argument("context", help="Context name (e.g., system_ops, content_generation)")
    load_parser.add_argument("--content", action="store_true", help="Include module file contents")
    load_parser.add_argument("--json", action="store_true", help="Output as JSON")
    load_parser.add_argument("--no-cache", action="store_true", help="Bypass cache, load fresh")

    # List contexts command
    subparsers.add_parser("contexts", help="List available contexts")

    # List modules command
    subparsers.add_parser("modules", help="List all registered modules")

    # Validate command
    subparsers.add_parser("validate", help="Validate hub file structure")

    # Cache stats command
    cache_parser = subparsers.add_parser("cache", help="Show or manage preference cache")
    cache_parser.add_argument("--clear", action="store_true", help="Clear all caches")

    args = parser.parse_args()

    # Handle cache command first (doesn't need hub)
    if args.command == "cache":
        if not HAS_CACHE:
            print("Caching not available (N5.lib.cache not installed)")
            return 1

        if args.clear:
            clear_all_caches()
            print("All caches cleared.")
            return 0

        stats = get_cache_stats()
        print("\nCache Statistics:\n")
        print(f"YAML Cache:")
        print(f"  Entries: {stats['yaml_cache']['entries']}/{stats['yaml_cache']['max_size']}")
        print(f"  Hit rate: {stats['yaml_cache']['hit_rate']}")
        print(f"  Hits: {stats['yaml_cache']['hits']}, Misses: {stats['yaml_cache']['misses']}")
        print(f"\nJSON Cache:")
        print(f"  Entries: {stats['json_cache']['entries']}/{stats['json_cache']['max_size']}")
        print(f"  Hit rate: {stats['json_cache']['hit_rate']}")
        print(f"\nPreferences Cache:")
        print(f"  Cached contexts: {stats['preferences_cache']['entries']}")
        if stats['preferences_cache']['contexts']:
            for ctx in stats['preferences_cache']['contexts']:
                print(f"    - {ctx}")
        print()
        return 0

    # Determine if caching should be used
    use_cache = not getattr(args, 'no_cache', False)

    hub = load_hub(use_cache=use_cache)

    if args.command == "contexts":
        list_contexts(hub)
        return 0

    elif args.command == "modules":
        list_modules(hub)
        return 0

    elif args.command == "validate":
        print("Validating hub file...")

        # Check required sections
        required = ["version", "precedence", "core", "modules", "contexts"]
        missing = [r for r in required if r not in hub]
        if missing:
            print(f"Missing required sections: {missing}")
            return 1

        # Check module paths exist
        modules = hub.get("modules", {})
        missing_paths = []
        for name, config in modules.items():
            path = WORKSPACE / config.get("path", "")
            if not path.exists():
                missing_paths.append((name, config.get("path")))

        if missing_paths:
            print(f"\nWarning: {len(missing_paths)} module paths not found:")
            for name, path in missing_paths[:10]:
                print(f"  {name}: {path}")
            if len(missing_paths) > 10:
                print(f"  ... and {len(missing_paths) - 10} more")

        # Check context references
        context_errors = []
        for ctx_name, ctx_config in hub.get("contexts", {}).items():
            load_list = ctx_config.get("load", [])
            if isinstance(load_list, list):
                for mod_name in load_list:
                    if mod_name not in modules:
                        context_errors.append((ctx_name, mod_name))

        if context_errors:
            print(f"\nWarning: {len(context_errors)} unknown modules in contexts:")
            for ctx_name, mod_name in context_errors:
                print(f"  context '{ctx_name}' references unknown module '{mod_name}'")

        print(f"\nHub version: {hub.get('version')}")
        print(f"Modules: {len(modules)}")
        print(f"Contexts: {len(hub.get('contexts', {}))}")
        print("\nValidation complete!")
        return 0

    elif args.command == "load":
        result = resolve_preferences(hub, args.context, include_content=args.content,
                                     use_cache=use_cache)

        if args.json:
            # Don't include full content in JSON output unless requested
            if not args.content:
                result.pop("content", None)
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"\nContext: {result['context']}")
            print(f"Core: timezone={result['core'].get('timezone', {}).get('display')}, military_time={result['core'].get('military_time')}")
            print(f"\nModules to load ({len(result['modules'])}):")
            for mod in result["modules"]:
                print(f"  [{mod['priority']:8}] {mod['name']:30} {mod['path']}")

            if result["overrides"]:
                print(f"\nOverrides applied: {list(result['overrides'].keys())}")

        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
