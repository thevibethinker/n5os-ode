#!/usr/bin/env python3
"""
Push curated, PII-filtered memories to Sentience API.
Collects from: Zo journal, Zo learnings, B32 thought-provoking ideas, N5 prefs.
Uses push ledger for idempotency — safe to run multiple times.
"""

import os
import re
import json
import sys
import time
import glob
import argparse
import hashlib
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from state import PushLedger
from pii import clean

API_URL = "https://audiosummarizer-production.up.railway.app/v1/memories"
API_KEY = os.environ.get("SENTIENCE_API_KEY")

if not API_KEY:
    print("ERROR: SENTIENCE_API_KEY not set", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def content_key(source: str, content: str) -> str:
    h = hashlib.sha256(content.encode()).hexdigest()[:12]
    return f"{source}::{h}"


def push_memory(content: str, source_label: str) -> dict | None:
    if not content or len(content.strip()) < 50:
        return None
    try:
        r = requests.post(API_URL, headers=HEADERS, json={"content": content}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  ERROR pushing ({source_label}): {e}")
        return None


def read_safe(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def collect_memories() -> list[dict]:
    memories = []

    # 1. Zo Journal
    print("=== Collecting Zo Journal ===")
    journal_dir = Path("/home/workspace/Zo/journal")
    if journal_dir.exists():
        for f in sorted(journal_dir.glob("*.md")):
            if "heartbeat-agentcommune" in f.name:
                continue
            text = clean(read_safe(f))
            if len(text) > 100:
                memories.append({
                    "content": f"[Zo Journal: {f.stem}]\n\n{text}",
                    "source": f"zo-journal/{f.name}",
                })
                print(f"  Added: {f.name} ({len(text)} chars)")
    else:
        print("  WARN: Zo/journal dir not found")

    # 2. Zo Learnings
    print("\n=== Collecting Zo Learnings ===")
    learnings_dir = Path("/home/workspace/Zo/learnings")
    if learnings_dir.exists():
        for f in sorted(learnings_dir.glob("*.md")):
            text = clean(read_safe(f))
            if len(text) > 100:
                memories.append({
                    "content": f"[Zo Learning: {f.stem}]\n\n{text}",
                    "source": f"zo-learnings/{f.name}",
                })
                print(f"  Added: {f.name} ({len(text)} chars)")

    # 3. B32 Thought-Provoking Ideas
    print("\n=== Collecting B32 Ideas ===")
    b32_pattern = os.environ.get(
        "SENTIENCE_B32_GLOB",
        "/home/workspace/Records/Meetings/*/B32_THOUGHT_PROVOKING_IDEAS.md",
    )
    b32_files = sorted(glob.glob(b32_pattern))
    for fpath in b32_files:
        text = read_safe(Path(fpath))
        meeting_dir = Path(fpath).parent.name
        chunks = re.split(r'(?=^### )', text, flags=re.MULTILINE)
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk.startswith("### "):
                continue
            is_v = bool(re.search(r'Classification.*?V_POSITION|Classification.*?V_HYPOTHESIS', chunk))
            is_ext = bool(re.search(r'Classification.*?EXTERNAL_WISDOM', chunk))
            if is_v or is_ext:
                cleaned = clean(chunk)
                cleaned = re.sub(r'\*\*Speaker\*\*:.*\n', '', cleaned)
                if len(cleaned) > 100:
                    label = "V's Framework" if is_v else "External Insight"
                    memories.append({
                        "content": f"[{label} — from meeting {meeting_dir}]\n\n{cleaned}",
                        "source": f"meeting-b32/{meeting_dir}/{hashlib.md5(chunk[:100].encode()).hexdigest()[:8]}",
                    })

    # 4. N5 Communication Prefs
    print("\n=== Collecting N5 Prefs ===")
    n5_comm_files = [
        "/home/workspace/N5/prefs/communication/style-guide.md",
        "/home/workspace/N5/prefs/communication/nuances.md",
        "/home/workspace/N5/prefs/communication/general-preferences.md",
        "/home/workspace/N5/prefs/communication/x-voice/X_VOICE_FINGERPRINT.md",
        "/home/workspace/N5/prefs/communication/style-guides/hedging-antipatterns.md",
        "/home/workspace/N5/prefs/communication/style-guides/directness-calibration.md",
        "/home/workspace/N5/prefs/communication/style-guides/succinctness-pairs.md",
    ]
    for fpath in n5_comm_files:
        p = Path(fpath)
        if p.exists():
            text = clean(read_safe(p))
            if len(text) > 100:
                memories.append({
                    "content": f"[Communication Style: {p.stem}]\n\n{text}",
                    "source": f"n5-prefs/{p.name}",
                })
                print(f"  Added: {p.name} ({len(text)} chars)")

    # 5. Principles
    print("\n=== Collecting Principles ===")
    principles_dir = Path("/home/workspace/N5/prefs/principles")
    for fname in ["P01_human_readable_first.yaml", "P15_complete_before_claiming.yaml",
                   "P16_accuracy_over_sophistication.yaml", "P32_simple_over_easy.yaml",
                   "P27_nemawashi_mode.yaml", "decision_matrix.md", "watts_principles.md"]:
        p = principles_dir / fname
        if p.exists():
            text = clean(read_safe(p))
            if len(text) > 50:
                memories.append({
                    "content": f"[Building Principle: {p.stem}]\n\n{text}",
                    "source": f"n5-principles/{p.name}",
                })
                print(f"  Added: {p.name} ({len(text)} chars)")

    # 6. SOUL.md
    print("\n=== Collecting Zo SOUL ===")
    soul = Path("/home/workspace/Zo/SOUL.md")
    if soul.exists():
        text = clean(read_safe(soul))
        if len(text) > 100:
            memories.append({
                "content": f"[Zo's Self-Model: How V and Zo work together]\n\n{text}",
                "source": "zo/SOUL.md",
            })
            print(f"  Added: SOUL.md ({len(text)} chars)")

    return memories


def main():
    parser = argparse.ArgumentParser(description="Push curated memories to Sentience")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be pushed")
    args = parser.parse_args()

    ledger = PushLedger()
    memories = collect_memories()

    if not memories:
        print("No memories collected; exiting.")
        return

    new = []
    for m in memories:
        key = content_key(m["source"], m["content"])
        if ledger.is_pushed(key):
            continue
        m["_key"] = key
        new.append(m)

    print(f"\n{'='*60}")
    print(f"Total collected: {len(memories)}")
    print(f"Already pushed: {len(memories) - len(new)}")
    print(f"New to push: {len(new)}")

    if not new:
        print("Nothing new to push.")
        return

    if args.dry_run:
        for m in new:
            print(f"  [DRY] {m['source']} ({len(m['content'])} chars)")
        return

    print(f"\nPushing {len(new)} memories...")
    success = 0
    failed = 0
    for i, mem in enumerate(new):
        result = push_memory(mem["content"], mem["source"])
        if result:
            success += 1
            ledger.mark_pushed(mem["_key"], result.get("id", "?"))
            print(f"  [{i+1}/{len(new)}] ✓ {mem['source'][:50]} → {result.get('id')}")
        else:
            failed += 1
            print(f"  [{i+1}/{len(new)}] ✗ FAILED: {mem['source'][:50]}")
        time.sleep(0.3)

    ledger.save()
    print(f"\n{'='*60}")
    print(f"DONE: {success} pushed, {failed} failed, {len(new)} total")
    print(f"Ledger entries: {ledger.count()}")


if __name__ == "__main__":
    main()
