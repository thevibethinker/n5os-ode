#!/usr/bin/env python3
"""
Org Classifier — Classifies meetings into configured org categories.

Classification uses participant names, meeting title, transcript content,
and calendar event data to determine the best-fit category from config.

Usage:
    python3 org_classifier.py <meeting-folder>
    python3 org_classifier.py <meeting-folder> --json
"""

import json
import sys
from pathlib import Path

from config_loader import load_orgs_config


def _classification_config() -> dict:
    return load_orgs_config()["org_classification"]


def _categories() -> dict:
    return _classification_config().get("categories", {})


def classify_org(manifest: dict, transcript_text: str = "") -> dict:
    """Classify meeting into configured org category."""
    title = (
        (manifest.get("meeting", {}) or {}).get("title", "")
        or manifest.get("source", {}).get("original_title", "")
        or ""
    ).lower()

    participants = []
    raw_participants = manifest.get("participants", [])
    if not raw_participants:
        raw_participants = (manifest.get("meeting", {}) or {}).get("participants", [])
    for p in raw_participants:
        if isinstance(p, dict):
            participants.append((p.get("name", "") or "").lower())
        elif isinstance(p, str):
            participants.append(p.lower())
    participants_str = " ".join(participants)

    calendar_title = ""
    cal = manifest.get("calendar_match", {})
    if cal and isinstance(cal, dict):
        calendar_title = (cal.get("event_title", "") or "").lower()

    searchable = f"{title} {participants_str} {calendar_title} {transcript_text[:3000].lower()}"
    manifest_blob = str(manifest).lower()

    categories = _categories()
    scores = {category: 0.0 for category in categories.keys()}
    matched = {category: [] for category in categories.keys()}

    for category, spec in categories.items():
        for signal in spec.get("signals", []) or []:
            signal_l = str(signal).lower()
            if signal_l and signal_l in searchable:
                scores[category] += 1.0
                matched[category].append(signal_l)
        for hint in spec.get("manifest_hints", []) or []:
            hint_l = str(hint).lower()
            if hint_l and hint_l in manifest_blob:
                scores[category] += 2.0
                matched[category].append(f"manifest:{hint_l}")

    default_category = _classification_config().get("default_category", "professional")
    if default_category not in scores:
        scores[default_category] = 0.0
        matched[default_category] = []

    best_org = max(scores, key=scores.get) if scores else default_category
    best_score = scores.get(best_org, 0.0)

    if best_score == 0:
        best_org = default_category
        confidence = 0.5
    else:
        total = sum(scores.values())
        confidence = min(1.0, best_score / max(total, 1.0))

    return {
        "org": best_org,
        "confidence": round(confidence, 2),
        "signals": matched.get(best_org, []),
        "scores": {k: round(v, 2) for k, v in scores.items()},
    }


def classify_and_update(meeting_path: Path) -> dict:
    """Classify a meeting and update its manifest with the org field."""
    manifest_path = meeting_path / "manifest.json"
    if not manifest_path.exists():
        return {"error": "manifest_missing"}

    manifest = json.loads(manifest_path.read_text())

    transcript_text = ""
    for fname in ("transcript.md", "transcript.txt"):
        tp = meeting_path / fname
        if tp.exists():
            transcript_text = tp.read_text(errors="ignore")
            break

    result = classify_org(manifest, transcript_text)

    manifest["org"] = result["org"]
    manifest["org_classification"] = {
        "org": result["org"],
        "confidence": result["confidence"],
        "signals": result["signals"],
        "classified_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2))

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Classify meeting org category")
    parser.add_argument("meeting", type=Path, help="Meeting folder path")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = classify_and_update(args.meeting)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Org: {result['org']} (confidence: {result['confidence']})")
            if result["signals"]:
                print(f"Signals: {', '.join(result['signals'])}")


if __name__ == "__main__":
    sys.exit(main() or 0)
