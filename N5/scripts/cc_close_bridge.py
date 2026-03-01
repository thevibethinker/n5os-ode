#!/usr/bin/env python3
"""
Claude Code → Zo Close Bridge

Creates a synthetic Zo-compatible workspace so the close pipeline
(Skills/thread-close, drop-close, build-close) can run from Claude Code sessions.

Problem: Claude Code sessions don't have a Zo conversation ID or
/home/.z/workspaces/<convo_id>/SESSION_STATE.md. The close scripts
depend on that structure to detect context, tier, and gather artifacts.

Solution: This bridge creates a temporary workspace with a proper
SESSION_STATE.md, optionally symlinks artifacts, then returns a
synthetic convo_id that the normal close pipeline can use.

Usage:
  # Minimal — creates workspace, returns convo_id for close scripts
  python3 N5/scripts/cc_close_bridge.py init \
    --type build \
    --focus "The Vibe Pill site migration" \
    --tier 3

  # With artifacts (symlinked into synthetic workspace for tier detection)
  python3 N5/scripts/cc_close_bridge.py init \
    --type build \
    --focus "Hotline webhook refactor" \
    --artifacts Sites/thevibepill/src/App.tsx Skills/zo-hotline/scripts/webhook.ts

  # With build context (routes to build-close)
  python3 N5/scripts/cc_close_bridge.py init \
    --type build \
    --focus "Career Coaching Hotline" \
    --build-slug career-coaching-hotline

  # Check if running in Claude Code
  python3 N5/scripts/cc_close_bridge.py detect

  # Clean up old synthetic workspaces
  python3 N5/scripts/cc_close_bridge.py cleanup --older-than 7
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


WORKSPACE_BASE = Path("/home/.z/workspaces")
CC_PREFIX = "cc_"


def is_claude_code() -> bool:
    return os.environ.get("CLAUDECODE") == "1"


def generate_cc_convo_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{CC_PREFIX}{ts}"


def create_session_state(
    convo_id: str,
    conv_type: str = "discussion",
    mode: str = "standalone",
    focus: str = "Claude Code session",
    objective: str = None,
    tier_override: int = None,
    build_slug: str = None,
    drop_id: str = None,
    parent_topic: str = None,
) -> Path:
    """Create a SESSION_STATE.md in the synthetic workspace."""
    workspace = WORKSPACE_BASE / convo_id
    workspace.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)

    # Build frontmatter
    fm_lines = [
        "---",
        f"conversation_id: {convo_id}",
        f"type: {conv_type}",
        f"mode: {mode}",
        f"status: active",
        f"created: {now.isoformat()}",
        f"last_updated: {now.isoformat()}",
        f"source: claude_code",
    ]

    if build_slug:
        fm_lines.append(f"build_slug: {build_slug}")
    if drop_id:
        fm_lines.append(f"drop_id: {drop_id}")
        fm_lines.append(f"worker_id: W{drop_id}")
    if parent_topic:
        fm_lines.append(f"parent_topic: {parent_topic}")
    if tier_override:
        fm_lines.append(f"tier_override: {tier_override}")

    fm_lines.append("---")

    # Build content
    parts = ["\n".join(fm_lines), ""]

    if build_slug and drop_id:
        parts.extend([
            "## Build Context",
            "",
            f"- **Build:** {build_slug}",
            f"- **Worker:** {drop_id}",
            f"- **Parent Topic:** {parent_topic or build_slug}",
            "",
        ])

    parts.extend([
        "## Metadata",
        "",
        f"- **Type:** {conv_type.title()}",
        f"- **Mode:** {mode}",
        f"- **Focus:** {focus}",
        f"- **Objective:** {objective or focus}",
        "",
        "## Progress",
        "",
        "- **Overall:** 100%",
        "- **Current Phase:** Close",
        "- **Next Actions:** Thread close",
        "",
        "## Covered",
        "",
        f"- {focus}",
        "- Work performed in Claude Code session",
        "",
    ])

    state_path = workspace / "SESSION_STATE.md"
    state_path.write_text("\n".join(parts))
    return state_path


def link_artifacts(convo_id: str, artifact_paths: list) -> int:
    """Symlink or copy artifact files into the synthetic workspace.

    This lets detect_tier() count artifacts correctly.
    Returns the number of artifacts linked.
    """
    workspace = WORKSPACE_BASE / convo_id
    linked = 0

    for path_str in artifact_paths:
        source = Path(path_str)
        if not source.is_absolute():
            source = Path("/home/workspace") / source

        if not source.exists():
            print(f"  WARN: artifact not found: {source}", file=sys.stderr)
            continue

        target = workspace / source.name
        if target.exists():
            # Avoid collision — append counter
            stem = source.stem
            suffix = source.suffix
            i = 2
            while target.exists():
                target = workspace / f"{stem}_{i}{suffix}"
                i += 1

        try:
            target.symlink_to(source)
            linked += 1
        except OSError:
            # Fallback: copy instead of symlink
            shutil.copy2(source, target)
            linked += 1

    return linked


def cmd_init(args):
    """Create synthetic workspace and return convo_id."""
    convo_id = args.convo_id or generate_cc_convo_id()

    # Determine mode from context
    mode = "standalone"
    if args.build_slug and args.drop_id:
        mode = "worker"
    elif args.build_slug:
        mode = "standalone"  # build-close context but not a worker

    state_path = create_session_state(
        convo_id=convo_id,
        conv_type=args.type,
        mode=mode,
        focus=args.focus,
        objective=args.objective,
        tier_override=args.tier,
        build_slug=args.build_slug,
        drop_id=args.drop_id,
        parent_topic=args.parent_topic,
    )

    # Link artifacts if provided
    artifact_count = 0
    if args.artifacts:
        artifact_count = link_artifacts(convo_id, args.artifacts)

    # If tier override requested, also create placeholder files to
    # ensure detect_tier() returns the right value when it counts files
    if args.tier and args.tier > 1 and artifact_count < 3:
        workspace = WORKSPACE_BASE / convo_id
        needed = 3 if args.tier == 2 else 10
        for i in range(artifact_count, needed):
            placeholder = workspace / f"_cc_artifact_{i}.md"
            placeholder.write_text(f"# Claude Code artifact placeholder {i}\n")

    result = {
        "convo_id": convo_id,
        "workspace": str(WORKSPACE_BASE / convo_id),
        "session_state": str(state_path),
        "artifacts_linked": artifact_count,
        "tier_override": args.tier,
        "source": "claude_code",
    }

    # Print the convo_id prominently for the LLM to capture
    print(f"CC_CONVO_ID={convo_id}")
    print(json.dumps(result, indent=2))
    return 0


def cmd_detect(args):
    """Check if running in Claude Code."""
    if is_claude_code():
        print("CLAUDE_CODE=true")
        print("Bridge required for close operations.")
        return 0
    else:
        print("CLAUDE_CODE=false")
        print("Native Zo environment — bridge not needed.")
        return 0


def cmd_cleanup(args):
    """Remove old synthetic workspaces."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.older_than)
    removed = 0

    for workspace in WORKSPACE_BASE.iterdir():
        if not workspace.name.startswith(CC_PREFIX):
            continue
        if not workspace.is_dir():
            continue

        # Parse timestamp from name
        try:
            ts_str = workspace.name[len(CC_PREFIX):]
            ws_time = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").replace(
                tzinfo=timezone.utc
            )
            if ws_time < cutoff:
                shutil.rmtree(workspace)
                print(f"  Removed: {workspace.name}")
                removed += 1
        except (ValueError, OSError) as e:
            print(f"  SKIP: {workspace.name} ({e})", file=sys.stderr)

    print(f"\nCleaned up {removed} old synthetic workspace(s).")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code → Zo Close Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init --type build --focus "Site migration" --tier 3
  %(prog)s init --type research --focus "Market analysis"
  %(prog)s init --type build --focus "Hotline" --build-slug career-coaching-hotline
  %(prog)s detect
  %(prog)s cleanup --older-than 7
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Create synthetic workspace")
    p_init.add_argument(
        "--type",
        default="discussion",
        choices=["build", "research", "discussion", "planning", "debug"],
        help="Conversation type",
    )
    p_init.add_argument("--focus", required=True, help="What the session was about")
    p_init.add_argument("--objective", help="Session objective (defaults to focus)")
    p_init.add_argument(
        "--tier", type=int, choices=[1, 2, 3], help="Force close tier"
    )
    p_init.add_argument("--convo-id", help="Custom convo ID (auto-generated if omitted)")
    p_init.add_argument(
        "--artifacts",
        nargs="*",
        help="File paths to link into synthetic workspace",
    )
    p_init.add_argument("--build-slug", help="Build slug (triggers build-close routing)")
    p_init.add_argument("--drop-id", help="Drop ID (triggers drop-close routing)")
    p_init.add_argument("--parent-topic", help="Parent topic for worker context")

    # detect
    subparsers.add_parser("detect", help="Check if running in Claude Code")

    # cleanup
    p_cleanup = subparsers.add_parser("cleanup", help="Remove old synthetic workspaces")
    p_cleanup.add_argument(
        "--older-than", type=int, default=7, help="Days threshold (default: 7)"
    )

    args = parser.parse_args()

    if args.command == "init":
        return cmd_init(args)
    elif args.command == "detect":
        return cmd_detect(args)
    elif args.command == "cleanup":
        return cmd_cleanup(args)


if __name__ == "__main__":
    sys.exit(main())
