#!/usr/bin/env python3
"""Capability Registry updater.

Deterministic, CLI-friendly helper that applies a single capability update
(specified as YAML/JSON) to:

1. The appropriate capability markdown file under N5/capabilities/**
2. The N5/capabilities/index.md registry index

The LLM is responsible for SEMANTICS (the spec contents). This script is
responsible for MECHANICS (file creation/updating + index wiring).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import logging
import re
from pathlib import Path
from typing import Any, Dict

import yaml

WORKSPACE_ROOT = Path("/home/workspace").resolve()
N5_ROOT = WORKSPACE_ROOT / "N5"
CAP_ROOT = N5_ROOT / "capabilities"
INDEX_PATH = CAP_ROOT / "index.md"


CATEGORY_SUBDIR = {
    "integration": "integrations",
    "internal": "internal",
    # workflow-like things all map to workflows dir
    "workflow": "workflows",
    "orchestrator": "workflows",
    "agent": "workflows",
    "site": "workflows",
}


def _load_spec(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("Spec must be a mapping at top level")
    if "capability_update" in data and isinstance(data["capability_update"], dict):
        return data["capability_update"]
    return data


def _resolve_capability_paths(spec: Dict[str, Any]) -> tuple[str, Path, str]:
    cap_id = spec.get("capability_id")
    if not cap_id or not isinstance(cap_id, str):
        raise ValueError("capability_id is required and must be a string")

    category = spec.get("category")
    if category not in CATEGORY_SUBDIR:
        raise ValueError(
            f"category must be one of {sorted(CATEGORY_SUBDIR)}, got {category!r}"
        )

    subdir = CATEGORY_SUBDIR[category]
    cap_dir = CAP_ROOT / subdir
    cap_dir.mkdir(parents=True, exist_ok=True)
    cap_file = cap_dir / f"{cap_id}.md"

    # For index wiring: relative path from workspace root in file '...' syntax
    rel_path = f"N5/capabilities/{subdir}/{cap_id}.md"
    return cap_id, cap_file, rel_path


def _ensure_dates_and_defaults(spec: Dict[str, Any]) -> None:
    today = _dt.date.today().isoformat()
    if not spec.get("last_verified"):
        spec["last_verified"] = today
    if not spec.get("status"):
        spec["status"] = "active"
    if not spec.get("confidence"):
        spec["confidence"] = "medium"
    if not spec.get("owner"):
        spec["owner"] = "V"
    if "tags" not in spec or spec["tags"] is None:
        spec["tags"] = []


def _render_metadata_yaml(spec: Dict[str, Any]) -> str:
    # Order keys for readability
    ordered_keys = [
        "capability_id",
        "name",
        "category",
        "status",
        "confidence",
        "last_verified",
        "tags",
        "entry_points",
        "owner",
    ]
    ordered = {k: spec.get(k) for k in ordered_keys if k in spec}
    # Include any extra keys at the end
    for k, v in spec.items():
        if k not in ordered:
            ordered[k] = v
    return yaml.safe_dump(ordered, sort_keys=False).rstrip() + "\n"


def _create_new_capability_file(cap_file: Path, spec: Dict[str, Any]) -> None:
    name = spec.get("name") or spec.get("capability_id")
    description = (spec.get("description") or "").strip()
    today = _dt.date.today().isoformat()

    frontmatter = (
        "---\n"
        f"created: {today}\n"
        f"last_edited: {today}\n"
        "version: 1.0\n"
        "---\n\n"
    )

    meta_block = _render_metadata_yaml(spec)

    body_lines = [
        f"# {name}\n\n",
        "```yaml\n",
        "# Zone 2: Capability metadata (machine-readable)\n",
        meta_block,
        "```\n\n",
        "## What This Does\n\n",
    ]

    if description:
        body_lines.append(description + "\n\n")
    else:
        body_lines.append(
            "Brief overview (2–5 sentences) of what this capability does and why it exists.\n\n"
        )

    body_lines.extend(
        [
            "## How to Use It\n\n",
            "- How to trigger it (prompts, commands, UI entry points)\n",
            "- Typical usage patterns and workflows\n\n",
            "## Associated Files & Assets\n\n",
            "List key implementation and configuration files using `file '...'` syntax where helpful.\n\n",
            "## Workflow\n\n",
            "Describe the execution flow. Optionally include a mermaid diagram.\n\n",
            "```mermaid\n",
            "flowchart TD\n",
            "  A[Trigger] --> B[Step 1]\n",
            "  B --> C[Step 2]\n",
            "  C --> D[Outputs]\n",
            "```\n\n",
            "## Notes / Gotchas\n\n",
            "- Edge cases\n",
            "- Preconditions\n",
            "- Safety considerations\n",
        ]
    )

    cap_file.write_text(frontmatter + "".join(body_lines), encoding="utf-8")
    logging.info("Created new capability file: %s", cap_file)


def _update_existing_capability_file(cap_file: Path, spec: Dict[str, Any]) -> None:
    text = cap_file.read_text(encoding="utf-8")
    today = _dt.date.today().isoformat()

    # Update frontmatter last_edited
    def repl_front(match: re.Match[str]) -> str:
        front = match.group(0)
        if "last_edited:" in front:
            front = re.sub(r"last_edited:\s*.*", f"last_edited: {today}", front)
        else:
            front = front.rstrip() + f"\nlast_edited: {today}\n"
        return front

    text, n_front = re.subn(r"^---[\s\S]*?---\n", repl_front, text, count=1, flags=re.MULTILINE)
    if n_front == 0:
        logging.warning("No frontmatter found in %s; leaving created/last_edited as-is", cap_file)

    # Replace metadata yaml block inside ```yaml ... ```
    meta_yaml = _render_metadata_yaml(spec)

    def repl_meta(match: re.Match[str]) -> str:
        return "```yaml\n# Zone 2: Capability metadata (machine-readable)\n" + meta_yaml + "```\n"

    text, n_meta = re.subn(r"```yaml[\s\S]*?```", repl_meta, text, count=1)
    if n_meta == 0:
        logging.warning("No ```yaml metadata block found in %s; appending one at top", cap_file)
        insert_pos = text.find("\n\n## ")
        if insert_pos == -1:
            insert_pos = len(text)
        meta_block = (
            "```yaml\n# Zone 2: Capability metadata (machine-readable)\n" + meta_yaml + "```\n\n"
        )
        text = text[:insert_pos] + "\n" + meta_block + text[insert_pos:]

    cap_file.write_text(text, encoding="utf-8")
    logging.info("Updated capability file: %s", cap_file)


def _update_index(rel_path: str, name: str, description: str, category: str) -> None:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"index.md not found at {INDEX_PATH}")

    lines = INDEX_PATH.read_text(encoding="utf-8").splitlines()

    # Determine section header based on category
    if category == "integration":
        header = "### Integrations"
    elif category == "internal":
        header = "### Internal Systems"
    else:
        header = "### Workflows & Orchestrators"

    # Find section bounds
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == header)
    except StopIteration:
        raise RuntimeError(f"Section header {header!r} not found in index.md")

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("### ") and lines[i].strip() != header:
            end = i
            break

    bullet_pattern = re.compile(re.escape(rel_path))

    # Check if an entry already exists
    for i in range(start + 1, end):
        if bullet_pattern.search(lines[i]):
            # Existing bullet; keep it for now
            logging.info("Index entry already present for %s", rel_path)
            return

    # Append new bullet at end of section
    short_desc = description.strip().split(".\n")[0].strip()
    if not short_desc:
        short_desc = description.strip().split(". ")[0].strip()
    if not short_desc:
        short_desc = "Capability documented in registry."

    bullet = f"- {name} – file '{rel_path}' – {short_desc}"

    insert_at = end
    # Backtrack to keep blank-line separation if present
    while insert_at > start + 1 and lines[insert_at - 1].strip() == "":
        insert_at -= 1

    lines.insert(insert_at, bullet)
    INDEX_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logging.info("Added index entry under %s for %s", header, rel_path)


def apply_capability_update(spec_path: Path) -> None:
    spec = _load_spec(spec_path)
    _ensure_dates_and_defaults(spec)
    cap_id, cap_file, rel_path = _resolve_capability_paths(spec)

    change_type = spec.get("change_type") or "auto"
    exists = cap_file.exists()

    if change_type == "new" and exists:
        logging.warning("change_type=new but %s already exists; treating as update", cap_file)
        change_type = "update"
    elif change_type == "update" and not exists:
        logging.warning("change_type=update but %s does not exist; treating as new", cap_file)
        change_type = "new"
    elif change_type == "auto":
        change_type = "update" if exists else "new"

    description = (spec.get("description") or "").strip()
    name = spec.get("name") or cap_id
    category = spec.get("category")

    logging.info(
        "Applying capability update: id=%s, type=%s, file=%s", cap_id, change_type, cap_file
    )

    if change_type == "new":
        _create_new_capability_file(cap_file, spec)
    else:
        _update_existing_capability_file(cap_file, spec)

    _update_index(rel_path, name, description, category)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a capability registry update spec.")
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to YAML/JSON file containing capability_update spec.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(message)s",
    )

    spec_path = Path(args.spec).expanduser().resolve()
    if not spec_path.exists():
        raise SystemExit(f"Spec file not found: {spec_path}")

    try:
        apply_capability_update(spec_path)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to apply capability update: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":  # pragma: no cover
    main()

