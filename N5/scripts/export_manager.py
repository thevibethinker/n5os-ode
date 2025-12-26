#!/usr/bin/env python3
import argparse
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


BASE_DIR = Path(__file__).resolve().parents[2]  # /home/workspace
EXPORTS_DIR = BASE_DIR / "Exports"


@dataclass
class ExportItem:
    label: str
    source_path: Path
    exported_name: str


def slugify(value: str) -> str:
    """Simple slugifier for folder names."""
    import re

    value = value.strip().lower()
    # Replace non-alphanumeric with dashes
    value = re.sub(r"[^a-z0-9]+", "-", value)
    # Remove leading/trailing dashes
    value = value.strip("-")
    return value or "export"


def parse_item_arg(arg: str) -> ExportItem:
    """Parse --item strings of the form 'source::exported_name::label'.

    - source is required
    - exported_name defaults to basename(source)
    - label defaults to exported_name
    """
    parts = arg.split("::")
    if len(parts) == 0 or not parts[0].strip():
        raise ValueError(f"Invalid --item value (missing source): {arg!r}")

    source = Path(parts[0].strip())
    exported_name = parts[1].strip() if len(parts) > 1 and parts[1].strip() else source.name
    label = parts[2].strip() if len(parts) > 2 and parts[2].strip() else exported_name

    # Normalize to workspace-rooted path if relative
    if not source.is_absolute():
        source = BASE_DIR / source

    return ExportItem(label=label, source_path=source, exported_name=exported_name)


def ensure_source_files_exist(items: List[ExportItem]) -> None:
    missing = [str(item.source_path) for item in items if not item.source_path.exists()]
    if missing:
        msg = "The following source files do not exist and cannot be exported:\n" + "\n".join(missing)
        raise FileNotFoundError(msg)


def build_batch_name(slug: str) -> str:
    now = datetime.now()
    ts = now.strftime("%Y%m%d_%H%M%S")
    s = slugify(slug)
    return f"{ts}_{s}" if s else ts


def write_metadata_yaml(
    batch_dir: Path,
    export_id: str,
    created_at: str,
    conversation_id: Optional[str],
    requested_by: Optional[str],
    recipient: Optional[str],
    purpose: str,
    notes: Optional[str],
    items: List[ExportItem],
) -> None:
    """Write a simple YAML metadata file without external deps."""
    lines: List[str] = []
    lines.append(f"export_id: {export_id}")
    lines.append(f"created_at: {created_at}")
    if conversation_id:
        lines.append(f"conversation_id: {conversation_id}")
    if requested_by:
        lines.append(f"requested_by: {requested_by}")
    if recipient:
        lines.append(f"recipient: {recipient}")
    lines.append(f"purpose: {purpose}")
    if notes:
        lines.append(f"notes: {notes}")
    lines.append("items:")
    for item in items:
        lines.append("  - label: " + str(item.label))
        lines.append("    source_path: " + str(item.source_path))
        lines.append("    exported_name: " + str(item.exported_name))

    (batch_dir / "metadata.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_manifest_md(
    batch_dir: Path,
    export_id: str,
    created_at: datetime,
    conversation_id: Optional[str],
    requested_by: Optional[str],
    recipient: Optional[str],
    purpose: str,
    notes: Optional[str],
    items: List[ExportItem],
) -> None:
    """Write a human-readable MANIFEST.md with required YAML frontmatter."""
    created_date = created_at.date().isoformat()
    frontmatter = [
        "---",
        f"created: {created_date}",
        f"last_edited: {created_date}",
        "version: 1.0",
        "---",
        "",
    ]

    body_lines: List[str] = []
    body_lines.append(f"# Export Manifest — {export_id}")
    body_lines.append("")
    body_lines.append(f"**Created at:** {created_at.isoformat()}")
    if conversation_id:
        body_lines.append(f"**Conversation ID:** {conversation_id}")
    if requested_by:
        body_lines.append(f"**Requested by:** {requested_by}")
    if recipient:
        body_lines.append(f"**Intended recipient:** {recipient}")
    body_lines.append(f"**Purpose:** {purpose}")
    if notes:
        body_lines.append("")
        body_lines.append(f"**Notes:** {notes}")

    body_lines.append("")
    body_lines.append("## Contents")
    body_lines.append("")
    for item in items:
        rel_name = item.exported_name
        body_lines.append(f"- **{item.label}:** `{rel_name}` (from `{item.source_path}`)")

    (batch_dir / "MANIFEST.md").write_text("\n".join(frontmatter + body_lines) + "\n", encoding="utf-8")


def create_batch(
    slug: str,
    purpose: str,
    items_raw: List[str],
    conversation_id: Optional[str] = None,
    requested_by: Optional[str] = None,
    recipient: Optional[str] = None,
    notes: Optional[str] = None,
) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    created_at_dt = datetime.now()
    export_id = build_batch_name(slug or purpose)
    batch_dir = EXPORTS_DIR / export_id
    batch_dir.mkdir(parents=False, exist_ok=False)

    items = [parse_item_arg(arg) for arg in items_raw]
    ensure_source_files_exist(items)

    # Copy files into batch dir (copy-only; never move)
    for item in items:
        dest = batch_dir / item.exported_name
        shutil.copy2(item.source_path, dest)

    # Write metadata + manifest
    created_at_iso = created_at_dt.isoformat()
    write_metadata_yaml(
        batch_dir=batch_dir,
        export_id=export_id,
        created_at=created_at_iso,
        conversation_id=conversation_id,
        requested_by=requested_by,
        recipient=recipient,
        purpose=purpose,
        notes=notes,
        items=items,
    )
    write_manifest_md(
        batch_dir=batch_dir,
        export_id=export_id,
        created_at=created_at_dt,
        conversation_id=conversation_id,
        requested_by=requested_by,
        recipient=recipient,
        purpose=purpose,
        notes=notes,
        items=items,
    )

    return batch_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage outbound export batches under Exports/.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-batch", help="Create a new export batch folder.")
    create_parser.add_argument("--slug", required=False, default="", help="Short theme/purpose slug for the batch name.")
    create_parser.add_argument("--purpose", required=True, help="Human-readable purpose/description of this export.")
    create_parser.add_argument("--conversation-id", required=False, help="Originating conversation ID, if any.")
    create_parser.add_argument("--requested-by", required=False, help="Who requested this export (e.g. 'V').")
    create_parser.add_argument("--recipient", required=False, help="Intended recipient (for metadata only, not naming).")
    create_parser.add_argument("--notes", required=False, help="Optional freeform notes about this export.")
    create_parser.add_argument(
        "--item",
        action="append",
        required=True,
        help="Item to export: 'source::exported_name::label'. exported_name and label are optional.",
    )

    args = parser.parse_args()

    if args.command == "create-batch":
        try:
            batch_dir = create_batch(
                slug=args.slug,
                purpose=args.purpose,
                items_raw=args.item,
                conversation_id=getattr(args, "conversation_id", None),
                requested_by=getattr(args, "requested_by", None),
                recipient=getattr(args, "recipient", None),
                notes=getattr(args, "notes", None),
            )
        except Exception as e:
            # Print error to stderr and exit non-zero
            import sys

            print(f"ERROR: {e}", file=sys.stderr)
            raise SystemExit(1)

        # Print absolute path of created batch dir for callers
        print(str(batch_dir.resolve()))


if __name__ == "__main__":
    main()

