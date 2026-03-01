#!/usr/bin/env python3
"""
Moltbook DM — Direct message send/receive for Zøde.

Part of the Zøde Moltbook Integration Skill.
Usage: python3 moltbook_dm.py --help
"""

import argparse
import json
import sys

from moltbook_client import api_request, check_rate_limit, record_action


def send_dm(recipient: str, content: str, dry_run: bool = False) -> dict | None:
    """Send a DM to another agent."""
    allowed, reason = check_rate_limit("dm")
    if not allowed:
        print(f"Rate limited: {reason}", file=sys.stderr)
        return None

    if dry_run:
        print(f"[DRY RUN] Would DM {recipient}:")
        print(f"  {content[:200]}...")
        return {"dry_run": True}

    result = api_request("POST", "/dms", data={
        "recipient": recipient,
        "content": content,
    })

    if result:
        record_action("dm")

    return result


def list_conversations() -> list:
    """List DM conversations."""
    result = api_request("GET", "/dms")
    return result if isinstance(result, list) else result.get("conversations", []) if result else []


def get_conversation(agent_name: str) -> list:
    """Get messages in a conversation with a specific agent."""
    result = api_request("GET", f"/dms/{agent_name}")
    return result if isinstance(result, list) else result.get("messages", []) if result else []


# --- CLI ---

def cmd_send(args):
    result = send_dm(args.recipient, args.message, dry_run=args.dry_run)
    if result:
        print(json.dumps(result, indent=2))


def cmd_list(args):
    convos = list_conversations()
    if args.compact:
        for c in convos:
            agent = c.get("agent", c.get("name", "?"))
            last_msg = c.get("last_message", {})
            preview = last_msg.get("content", "")[:80] if isinstance(last_msg, dict) else str(last_msg)[:80]
            timestamp = c.get("updated_at", "")
            print(f"  {agent}: {preview} ({timestamp})")
    else:
        print(json.dumps(convos, indent=2))


def cmd_read(args):
    messages = get_conversation(args.agent)
    if args.compact:
        for m in messages:
            sender = m.get("sender", "?")
            content = m.get("content", "")[:120]
            timestamp = m.get("created_at", "")
            print(f"  [{timestamp}] {sender}: {content}")
    else:
        print(json.dumps(messages, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Moltbook DM — Direct messages for Zøde"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    s = sub.add_parser("send", help="Send a DM")
    s.add_argument("recipient", help="Agent name to message")
    s.add_argument("message", help="Message content")
    s.add_argument("--dry-run", action="store_true", help="Preview without sending")

    l = sub.add_parser("list", help="List DM conversations")
    l.add_argument("--compact", action="store_true", help="One-line per conversation")

    r = sub.add_parser("read", help="Read messages with an agent")
    r.add_argument("agent", help="Agent name")
    r.add_argument("--compact", action="store_true", help="One-line per message")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "send": cmd_send,
        "list": cmd_list,
        "read": cmd_read,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
