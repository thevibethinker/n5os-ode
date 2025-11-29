#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path("/home/workspace/Personal/Integrations/fillout").resolve()
FORM_INDEX_PATH = BASE_DIR / "form_index.json"


def load_index() -> dict:
    if not FORM_INDEX_PATH.exists():
        return {"forms": {}}
    with FORM_INDEX_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    index = load_index()
    forms = index.get("forms", {})

    if not forms:
        print("No forms found in form_index.json.")
        return

    print("Known Fillout forms (from form_index.json):")
    for form_id, entry in sorted(forms.items(), key=lambda kv: kv[0]):
        name = entry.get("formName") or "(no name recorded)"
        count = entry.get("submissionCount", 0)
        first_seen = entry.get("firstSeen")
        last_seen = entry.get("lastSeen")
        print(
            f"- formId={form_id}\n"
            f"    name: {name}\n"
            f"    submissions: {count}\n"
            f"    firstSeen: {first_seen}\n"
            f"    lastSeen: {last_seen}"
        )


if __name__ == "__main__":  # pragma: no cover
    main()

