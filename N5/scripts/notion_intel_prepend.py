#!/usr/bin/env python3
"""
Notion Intel Append — Working workaround for adding deal intelligence to Notion pages.

## SOLUTION DISCOVERY (2026-01-18)

**Problem:** notion-update-page can't easily update rich_text properties programmatically
via Pipedream (requires UI property selector).

**Working Solution:** Use notion-append-block with markdownContents to add intel
directly to the page body. This is actually BETTER because:
1. Page body supports rich formatting (headers, bullets, bold)
2. Append works natively - no read-modify-write needed
3. Content is more visible in the page view

## Usage

1. Format intel for append:
   python3 N5/scripts/notion_intel_prepend.py format-markdown \
       --source-title "Meeting: Tope Awotona Sync" \
       --source-type "meeting" \
       --key-fact "Confirmed interest in partnership" \
       --key-fact "Budget approved by board"

2. Use output with use_app_notion:
   use_app_notion("notion-append-block", {
       "pageId": "<notion_page_id>",
       "blockTypes": ["markdownContents"],
       "markdownContents": ["<output from step 1>"]
   })

## Legacy Commands (for reference)

- `format`: Generate intel entry text
- `combine`: Combine new + existing (for property updates if ever needed)
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import List, Optional


def format_intel_entry(
    source_title: str,
    source_type: str,
    date: Optional[str] = None,
    stage_before: Optional[str] = None,
    stage_after: Optional[str] = None,
    key_facts: Optional[List[str]] = None,
    next_action: Optional[str] = None,
    next_action_date: Optional[str] = None,
) -> str:
    """Format a new intel entry for prepending to Notion field."""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        "---",
        f"## [{date}] {source_title}",
        f"**Source:** {source_type}",
    ]
    
    if stage_before and stage_after and stage_before != stage_after:
        lines.append(f"**Stage:** {stage_before} → {stage_after}")
    
    if key_facts:
        lines.append("")
        lines.append("**Key Intel:**")
        for fact in key_facts:
            lines.append(f"- {fact}")
    
    if next_action:
        lines.append("")
        if next_action_date:
            lines.append(f"**Next:** {next_action} (by {next_action_date})")
        else:
            lines.append(f"**Next:** {next_action}")
    
    return "\n".join(lines)


def format_markdown_for_append(
    source_title: str,
    source_type: str,
    date: Optional[str] = None,
    stage_before: Optional[str] = None,
    stage_after: Optional[str] = None,
    key_facts: Optional[List[str]] = None,
    next_action: Optional[str] = None,
    next_action_date: Optional[str] = None,
) -> str:
    """Format intel as markdown for notion-append-block.
    
    This formats content suitable for use with:
    use_app_notion("notion-append-block", {
        "pageId": "...",
        "blockTypes": ["markdownContents"],
        "markdownContents": [<this output>]
    })
    """
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"## [{date}] {source_title}",
        f"**Source:** {source_type}",
    ]
    
    if stage_before and stage_after and stage_before != stage_after:
        lines.append(f"**Stage:** {stage_before} → {stage_after}")
    
    if key_facts:
        lines.append("")
        lines.append("**Key Intel:**")
        for fact in key_facts:
            lines.append(f"- {fact}")
    
    if next_action:
        lines.append("")
        if next_action_date:
            lines.append(f"**Next:** {next_action} (by {next_action_date})")
        else:
            lines.append(f"**Next:** {next_action}")
    
    lines.append("")
    lines.append("---")
    
    return "\n".join(lines)


def combine_content(new_entry: str, existing: str) -> str:
    """Combine new entry with existing content (prepend with separator)."""
    existing = (existing or "").strip()
    new_entry = (new_entry or "").strip()
    
    if not existing:
        return new_entry
    
    if not new_entry:
        return existing
    
    return f"{new_entry}\n\n---\n[Previous content below]\n\n{existing}"


def extract_plain_text(rich_text_array: List[dict]) -> str:
    """Extract plain text from Notion rich_text array."""
    if not rich_text_array:
        return ""
    return "".join(item.get("plain_text", "") for item in rich_text_array)


def build_rich_text_payload(text: str) -> dict:
    """Build Notion rich_text property payload from plain text."""
    return {
        "rich_text": [
            {
                "type": "text",
                "text": {"content": text}
            }
        ]
    }


def cmd_format_markdown(args):
    """Format intel for notion-append-block (RECOMMENDED)."""
    entry = format_markdown_for_append(
        source_title=args.source_title,
        source_type=args.source_type,
        date=args.date,
        stage_before=args.stage_before,
        stage_after=args.stage_after,
        key_facts=args.key_fact or [],
        next_action=args.next_action,
        next_action_date=args.next_action_date,
    )
    
    if args.json:
        print(json.dumps({
            "markdown": entry,
            "notion_append_params": {
                "blockTypes": ["markdownContents"],
                "markdownContents": [entry]
            }
        }))
    else:
        print(entry)


def cmd_format(args):
    """Format a new intel entry (legacy - for property updates)."""
    entry = format_intel_entry(
        source_title=args.source_title,
        source_type=args.source_type,
        date=args.date,
        stage_before=args.stage_before,
        stage_after=args.stage_after,
        key_facts=args.key_fact or [],
        next_action=args.next_action,
        next_action_date=args.next_action_date,
    )
    
    if args.json:
        print(json.dumps({"entry": entry}))
    else:
        print(entry)


def cmd_combine(args):
    """Combine new entry with existing content."""
    new_entry = args.new_entry or ""
    existing = args.existing or ""
    
    # Handle JSON input for existing content (from Notion API response)
    if args.existing_json:
        try:
            data = json.loads(args.existing_json)
            if isinstance(data, list):
                existing = extract_plain_text(data)
            elif isinstance(data, dict) and "rich_text" in data:
                existing = extract_plain_text(data["rich_text"])
            else:
                existing = str(data)
        except json.JSONDecodeError:
            existing = args.existing_json
    
    combined = combine_content(new_entry, existing)
    
    if args.json:
        print(json.dumps({
            "combined": combined,
            "payload": build_rich_text_payload(combined)
        }))
    else:
        print(combined)


def cmd_payload(args):
    """Generate full update payload for notion-update-page."""
    # This generates the propertyValues format for use_app_notion
    payload = {
        "propertyIdOrName": args.field_name,
        "propertyValue": args.value
    }
    print(json.dumps([payload]))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Notion intel append helper")
    sub = p.add_subparsers(dest="command", required=True)
    
    # Format-markdown command (RECOMMENDED)
    sp = sub.add_parser("format-markdown", help="Format intel for notion-append-block (RECOMMENDED)")
    sp.add_argument("--source-title", required=True, help="e.g., 'Meeting: Tope Awotona Sync'")
    sp.add_argument("--source-type", required=True, help="e.g., 'meeting', 'email', 'sms'")
    sp.add_argument("--date", help="Override date (default: today)")
    sp.add_argument("--stage-before", help="Previous deal stage")
    sp.add_argument("--stage-after", help="New deal stage")
    sp.add_argument("--key-fact", action="append", help="Key fact (repeatable)")
    sp.add_argument("--next-action", help="Next action")
    sp.add_argument("--next-action-date", help="Next action deadline")
    sp.add_argument("--json", action="store_true", help="Output as JSON with notion params")
    sp.set_defaults(func=cmd_format_markdown)
    
    # Format command (legacy)
    sp = sub.add_parser("format", help="Format intel entry (legacy - for property updates)")
    sp.add_argument("--source-title", required=True, help="e.g., 'Meeting: Tope Awotona Sync'")
    sp.add_argument("--source-type", required=True, help="e.g., 'meeting', 'email', 'sms'")
    sp.add_argument("--date", help="Override date (default: today)")
    sp.add_argument("--stage-before", help="Previous deal stage")
    sp.add_argument("--stage-after", help="New deal stage")
    sp.add_argument("--key-fact", action="append", help="Key fact (repeatable)")
    sp.add_argument("--next-action", help="Next action")
    sp.add_argument("--next-action-date", help="Next action deadline")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.set_defaults(func=cmd_format)
    
    # Combine command (legacy)
    sp = sub.add_parser("combine", help="Combine new entry with existing (legacy)")
    sp.add_argument("--new-entry", required=True, help="New content to prepend")
    sp.add_argument("--existing", help="Existing content (plain text)")
    sp.add_argument("--existing-json", help="Existing content (Notion rich_text JSON)")
    sp.add_argument("--json", action="store_true", help="Output as JSON with payload")
    sp.set_defaults(func=cmd_combine)
    
    # Payload command
    sp = sub.add_parser("payload", help="Generate propertyValues payload")
    sp.add_argument("--field-name", required=True, help="Notion field name")
    sp.add_argument("--value", required=True, help="Value to set")
    sp.set_defaults(func=cmd_payload)
    
    return p


def main() -> int:
    args = build_parser().parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
