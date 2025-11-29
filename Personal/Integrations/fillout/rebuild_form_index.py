#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path("/home/workspace/Personal/Integrations/fillout").resolve()
EVENTS_BASE_DIR = BASE_DIR / "events"
FORM_INDEX_PATH = BASE_DIR / "form_index.json"


def rebuild_index() -> Dict[str, Any]:
    index: Dict[str, Any] = {"forms": {}}
    forms = index["forms"]

    if not EVENTS_BASE_DIR.exists():
        return index

    for path in sorted(EVENTS_BASE_DIR.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                payload = event.get("payload", {})
                form_id = payload.get("formId")
                form_name = payload.get("formName")
                received_at = event.get("received_at")

                if not form_id:
                    continue

                entry = forms.get(form_id, {
                    "formId": form_id,
                    "formName": form_name,
                    "firstSeen": received_at,
                    "lastSeen": received_at,
                    "submissionCount": 0,
                })

                if form_name:
                    entry["formName"] = form_name

                if not entry.get("firstSeen"):
                    entry["firstSeen"] = received_at

                # Update lastSeen to the most recent timestamp seen
                if received_at and (
                    not entry.get("lastSeen")
                    or received_at > entry.get("lastSeen")
                ):
                    entry["lastSeen"] = received_at

                entry["submissionCount"] = int(entry.get("submissionCount", 0)) + 1
                forms[form_id] = entry

    return index


def main() -> None:
    index = rebuild_index()

    tmp = FORM_INDEX_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    tmp.replace(FORM_INDEX_PATH)

    print("Rebuilt form_index.json with forms:")
    for form_id, entry in index.get("forms", {}).items():
        print(
            f"- {form_id}: name={entry.get('formName')} "
            f"submissions={entry.get('submissionCount')} firstSeen={entry.get('firstSeen')} "
            f"lastSeen={entry.get('lastSeen')}"
        )


if __name__ == "__main__":  # pragma: no cover
    main()

