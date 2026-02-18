#!/usr/bin/env python3
"""Generate a knowledge index for the Zo Hotline knowledge base.

Creates Knowledge/zo-hotline/00-knowledge-index.md — a lightweight lookup table
listing every knowledge section with concept keys and 1-line summaries.
Used by Zoseph's explainConcept tool to know what it has before fetching.

Usage:
    python3 N5/scripts/generate_zo_knowledge_index.py [--dry-run]
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

KNOWLEDGE_BASE = Path("/home/workspace/Knowledge/zo-hotline")
OUTPUT_PATH = KNOWLEDGE_BASE / "00-knowledge-index.md"

SKIP_FILES = {"00-knowledge-index.md", "quick-wins-by-level.md"}
SKIP_DIRS = {"__pycache__", ".git"}


def extract_summary(filepath: Path) -> str:
    """Extract a 1-line summary from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
        lines = text.strip().split("\n")

        in_frontmatter = False
        content_lines = []
        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                continue
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            content_lines.append(stripped)
            if len(content_lines) >= 2:
                break

        if content_lines:
            summary = content_lines[0]
            if len(summary) > 120:
                summary = summary[:117] + "..."
            return summary
        return "(no summary available)"
    except Exception as e:
        return f"(error reading: {e})"


def scan_knowledge_base() -> list[dict]:
    """Walk the knowledge base and build an index of all content."""
    entries = []

    for root, dirs, files in os.walk(KNOWLEDGE_BASE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel_root = Path(root).relative_to(KNOWLEDGE_BASE)

        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            if fname in SKIP_FILES:
                continue

            filepath = Path(root) / fname
            rel_path = rel_root / fname

            stem = fname.replace(".md", "")
            concept_key = stem.lower().replace("_", "-").replace(" ", "-")
            if concept_key.startswith(("00-", "10-", "20-", "30-", "40-", "50-", "60-", "70-", "80-", "90-", "95-", "96-", "97-")):
                parts = concept_key.split("-", 1)
                if len(parts) > 1:
                    concept_key = parts[1]

            section = str(rel_root) if str(rel_root) != "." else "root"
            summary = extract_summary(filepath)

            entries.append({
                "concept_key": concept_key,
                "file": str(rel_path),
                "section": section,
                "summary": summary,
            })

    return entries


def generate_index_content(entries: list[dict]) -> str:
    """Generate the markdown index content."""
    now = datetime.now(tz=__import__("datetime").timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "---",
        f"created: {now}",
        f"last_edited: {now}",
        "version: 1.0",
        "provenance: generate_zo_knowledge_index.py",
        "---",
        "",
        "# Zo Hotline Knowledge Index",
        "",
        "Auto-generated lookup table for Zoseph's `explainConcept` tool.",
        "Lists every knowledge file with concept key and 1-line summary.",
        "",
        "| concept-key | file | section | summary |",
        "|---|---|---|---|",
    ]

    for entry in entries:
        escaped_summary = entry["summary"].replace("|", "\\|")
        lines.append(
            f"| {entry['concept_key']} | {entry['file']} | {entry['section']} | {escaped_summary} |"
        )

    lines.append("")
    lines.append(f"**Total entries:** {len(entries)}")
    lines.append(f"**Generated:** {now}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Zo Hotline knowledge index")
    parser.add_argument("--dry-run", action="store_true", help="Print output without writing")
    args = parser.parse_args()

    if not KNOWLEDGE_BASE.exists():
        print(f"ERROR: Knowledge base not found: {KNOWLEDGE_BASE}", file=sys.stderr)
        return 1

    print(f"[{datetime.now(tz=__import__("datetime").timezone.utc).isoformat()}] Scanning {KNOWLEDGE_BASE}...")
    entries = scan_knowledge_base()
    print(f"  Found {len(entries)} knowledge entries")

    content = generate_index_content(entries)

    if args.dry_run:
        print("\n--- DRY RUN OUTPUT ---")
        print(content)
        print(f"\nWould write to: {OUTPUT_PATH}")
        return 0

    OUTPUT_PATH.write_text(content, encoding="utf-8")
    print(f"[{datetime.now(tz=__import__("datetime").timezone.utc).isoformat()}] Written: {OUTPUT_PATH}")

    verify = OUTPUT_PATH.read_text(encoding="utf-8")
    line_count = len(verify.strip().split("\n"))
    print(f"  Verified: {line_count} lines written")

    return 0


if __name__ == "__main__":
    sys.exit(main())
