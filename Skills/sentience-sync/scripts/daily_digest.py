#!/usr/bin/env python3
"""
Daily digest: pull all Sentience memories for a given period,
categorize into buckets using the relevance rubric, score priority,
and output a structured summary.
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict
from zoneinfo import ZoneInfo

import requests
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from state import atomic_write
from pii import strip_pii

API_URL = "https://audiosummarizer-production.up.railway.app/v1/memories"
API_KEY = os.environ.get("SENTIENCE_API_KEY")
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
RUBRIC_FILE = DATA_DIR / "relevance_rubric.yaml"
DIGESTS_DIR = DATA_DIR / "digests"
PT = ZoneInfo("America/Los_Angeles")

ZO_CONTENT_MARKERS = ["[Zo Journal:", "[Zo Learning:", "[V's Framework", "[External Insight", "[Communication Style:", "[Building Principle:", "[Zo's Self-Model:"]


def load_rubric() -> dict:
    try:
        return yaml.safe_load(RUBRIC_FILE.read_text())
    except Exception as e:
        print(f"ERROR loading rubric from {RUBRIC_FILE}: {e}", file=sys.stderr)
        sys.exit(1)


def pull_memories(start: str, end: str) -> list[dict]:
    resp = requests.get(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        params={"start": start, "end": end},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json().get("memories", [])


def is_zo_originated(memory: dict) -> bool:
    if memory.get("source") == "api":
        return True
    content = memory.get("content") or ""
    return any(marker in content for marker in ZO_CONTENT_MARKERS)


def parse_screenshot(content_str) -> dict | None:
    if isinstance(content_str, dict):
        return content_str
    try:
        return json.loads(content_str)
    except (json.JSONDecodeError, TypeError):
        return None


def classify_memory(memory: dict, rubric: dict) -> tuple[str, str, float]:
    """Returns (bucket, priority, confidence)."""
    content = memory.get("content") or ""
    source = memory.get("source", "")
    content_lower = content.casefold()

    parsed = None
    if source == "Sentience Desktop App":
        parsed = parse_screenshot(content)
        if parsed:
            sig = parsed.get("significance_score", 0)
            if sig < 0.3:
                return ("other", "SKIP", 0.0)
            cat = parsed.get("category", "")
            if cat in ("System", "Lock Screen"):
                return ("other", "SKIP", 0.0)
            searchable = " ".join([
                parsed.get("appName", ""),
                parsed.get("title", ""),
                parsed.get("summary", ""),
                " ".join(parsed.get("facts", {}).get("people", [])),
                " ".join(parsed.get("facts", {}).get("companies", [])),
            ])
            content_lower = searchable.casefold()

    bucket = "other"
    best_score = 0
    second_score = 0

    for bucket_name, config in rubric.get("buckets", {}).items():
        if bucket_name == "other":
            continue
        signals = config.get("signals", {})
        score = 0

        if parsed:
            app_name = (parsed.get("appName") or "").casefold()
            for sig_app in signals.get("apps", []):
                if sig_app.casefold() in app_name:
                    score += 3

        for kw in signals.get("keywords", []):
            if kw.casefold() in content_lower:
                score += 2

        for domain in signals.get("domains", []):
            if domain.casefold() in content_lower:
                score += 2

        if score > best_score:
            second_score = best_score
            best_score = score
            bucket = bucket_name
        elif score > second_score:
            second_score = score

    confidence = 1.0 if second_score == 0 else (best_score - second_score) / max(best_score, 1)

    # Priority scoring with phrase-level patterns and word boundaries
    priority = "LOW"

    high_patterns = [
        re.compile(r"\b(?:agreed to|committed to|i will|we will|i'll|we'll)\b", re.I),
        re.compile(r"\b(?:by|before)\s+(?:tomorrow|tonight|eod|eow|end of|next week|this week|monday|tuesday|wednesday|thursday|friday)\b", re.I),
        re.compile(r"\b(?:by|before)\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\b", re.I),
        re.compile(r"\bdeadline\b(?!\s*(?:not|no|without|free))", re.I),
        re.compile(r"\baction item\b", re.I),
        re.compile(r"\bscheduled\s+(?:a\s+)?meeting\b", re.I),
    ]
    medium_high_patterns = [
        re.compile(r"\b(?:first time meeting|nice to meet|just met)\b", re.I),
        re.compile(r"\bfollow[\s-]?up\s+(?:with|on|needed|required)\b", re.I),
        re.compile(r"\b(?:shipped|launched|deployed|published|released)\b", re.I),
        re.compile(r"\b(?:offer|accepted|rejected|approved|denied)\b", re.I),
    ]
    medium_patterns = [
        re.compile(r"\b(?:new idea|insight|hypothesis|framework)\b", re.I),
        re.compile(r"\bresearch(?:ing|ed)?\s+\w+", re.I),
        re.compile(r"\b(?:reviewed|gave feedback|commented on)\b", re.I),
    ]

    for pat in high_patterns:
        if pat.search(content_lower):
            priority = "HIGH"
            break
    if priority != "HIGH":
        for pat in medium_high_patterns:
            if pat.search(content_lower):
                priority = "MEDIUM_HIGH"
                break
    if priority not in ("HIGH", "MEDIUM_HIGH"):
        for pat in medium_patterns:
            if pat.search(content_lower):
                priority = "MEDIUM"
                break

    return (bucket, priority, confidence)


def format_memory(memory: dict, parsed_content: dict | None = None) -> dict:
    source = memory.get("source", "")
    content = memory.get("content") or ""
    ts = memory.get("timestamp", "")

    result = {
        "id": memory.get("id", ""),
        "timestamp": ts,
        "source": source,
    }

    if source == "Sentience Desktop App" and parsed_content:
        result["app"] = parsed_content.get("appName", "unknown")
        result["title"] = parsed_content.get("title", "")
        result["summary"] = parsed_content.get("summary", "")
        result["people"] = parsed_content.get("facts", {}).get("people", [])
        result["companies"] = parsed_content.get("facts", {}).get("companies", [])
        result["actions"] = parsed_content.get("facts", {}).get("actions", [])
    elif source == "Gmail":
        lines = content.split("\n")
        subject = ""
        sender = ""
        for line in lines[:10]:
            if line.startswith("Subject:"):
                subject = line.replace("Subject:", "").strip()
            if line.startswith("From:"):
                sender = re.sub(r'<[^>]+>', '', line.replace("From:", "")).strip()
        result["title"] = subject or content[:100]
        result["sender"] = sender
        result["summary"] = content[:300]
    elif source == "Google Calendar":
        result["title"] = content[:200]
        result["summary"] = content[:300]
    else:
        result["title"] = content[:100]
        result["summary"] = content[:300]

    for key in ("summary", "title", "sender"):
        if key in result:
            result[key] = strip_pii(str(result[key]))

    return result


def main():
    parser = argparse.ArgumentParser(description="Generate daily Sentience digest")
    parser.add_argument("--date", type=str, help="Date to digest (YYYY-MM-DD in PT)")
    parser.add_argument("--hours", type=float, default=18, help="Hours to look back (default: 18)")
    parser.add_argument("--output", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: SENTIENCE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    rubric = load_rubric()

    if args.date:
        day_pt = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=PT)
        start_dt = day_pt.replace(hour=6, minute=0, second=0)
        end_dt = day_pt.replace(hour=23, minute=59, second=59)
    else:
        end_dt = datetime.now(timezone.utc)
        start_dt = end_dt - timedelta(hours=args.hours)

    start_str = start_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"Pulling memories from {start_str} to {end_str}", file=sys.stderr)

    try:
        memories = pull_memories(start_str, end_str)
    except requests.RequestException as e:
        print(f"ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Total memories: {len(memories)}", file=sys.stderr)

    memories = [m for m in memories if not is_zo_originated(m)]

    categorized = defaultdict(lambda: {"HIGH": [], "MEDIUM_HIGH": [], "MEDIUM": [], "LOW": []})
    stats = defaultdict(int)
    uncertain = []
    skipped = 0

    for mem in memories:
        bucket, priority, confidence = classify_memory(mem, rubric)
        stats[bucket] += 1

        if priority == "SKIP":
            skipped += 1
            continue

        parsed = None
        if mem.get("source") == "Sentience Desktop App":
            parsed = parse_screenshot(mem.get("content") or "")

        formatted = format_memory(mem, parsed)
        formatted["bucket"] = bucket
        formatted["priority"] = priority
        formatted["confidence"] = round(confidence, 2)

        if confidence < 0.3 and bucket != "other":
            uncertain.append(formatted)

        categorized[bucket][priority].append(formatted)

    # Build output
    bucket_order = [k for k in rubric.get("buckets", {}).keys() if k != "other"] + ["other"]
    digest = {
        "period": {"start": start_str, "end": end_str},
        "stats": {
            "total_memories": len(memories),
            "skipped": skipped,
            "by_bucket": dict(stats),
        },
        "buckets": {},
        "uncertain": uncertain[:10],
    }

    for bucket_name in bucket_order:
        bucket_data = categorized.get(bucket_name, {})
        items = []
        for priority in ["HIGH", "MEDIUM_HIGH", "MEDIUM", "LOW"]:
            items.extend(bucket_data.get(priority, []))
        if items:
            digest["buckets"][bucket_name] = items

    if args.output == "json":
        print(json.dumps(digest, indent=2))
    else:
        print(format_markdown(digest))

    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = start_dt.strftime("%Y-%m-%d")
    digest_file = DIGESTS_DIR / f"{date_str}.json"
    atomic_write(digest_file, json.dumps(digest, indent=2))
    print(f"\nDigest saved to {digest_file}", file=sys.stderr)


def format_markdown(digest: dict) -> str:
    lines = [f"# Daily Activity Digest"]
    lines.append(f"**Period:** {digest['period']['start']} → {digest['period']['end']}")
    lines.append(f"**Total memories:** {digest['stats']['total_memories']} (skipped: {digest['stats'].get('skipped', 0)})")
    lines.append("")

    for bucket, items in digest.get("buckets", {}).items():
        lines.append(f"## {bucket.upper()}")
        lines.append("")
        for item in items:
            badge = f"[{item['priority']}]"
            conf = f"({item.get('confidence', '?')})" if item.get("confidence", 1.0) < 0.5 else ""
            title = item.get("title", "untitled")
            ts = item.get("timestamp", "")[:16]
            lines.append(f"- {badge} {conf} **{title}** ({ts})")
            if item.get("summary"):
                lines.append(f"  {item['summary'][:200]}")
        lines.append("")

    if digest.get("uncertain"):
        lines.append("## ⚠️ UNCERTAIN CLASSIFICATION")
        lines.append("")
        for item in digest["uncertain"]:
            lines.append(f"- [{item['bucket']}?] **{item.get('title', 'untitled')}** (confidence: {item.get('confidence', '?')})")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
