#!/usr/bin/env python3
"""Meeting Block Generation [MG-2] orchestrator"""

import asyncio
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

BASE_DIR = Path("/home/workspace")
MEETINGS_DIR = BASE_DIR / "Personal" / "Meetings"
PROCESSING_LOG = MEETINGS_DIR / "PROCESSING_LOG.jsonl"
QUARANTINE_DIR = MEETINGS_DIR / "_quarantine"
PROMPTS_DIR = BASE_DIR / "Prompts" / "Blocks"
ZO_TOKEN = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")

PLACEHOLDER_PATTERNS = [
    "this is a test transcript",
    "test transcript for mg",
    "meeting content here",
    "sample meeting content",
    "placeholder"
]
NAME_GUARD_KEYWORDS = ["test", "sample", "simulated", "demo", "raw-meeting"]
GUARD_MIN_SIZE_BYTES = 500

BLOCK_DEFINITIONS = [
    {"filename": "B00_ZO_TAKE_HEED.jsonl", "prompt_key": "B00", "format": "jsonl"},
    {"filename": "B01_DETAILED_RECAP.md", "prompt_key": "B01", "format": "markdown"},
    {"filename": "B03_STAKEHOLDER_INTELLIGENCE.md", "prompt_key": "B31", "format": "markdown"},
    {"filename": "B03_DECISIONS.md", "prompt_key": "B03", "format": "markdown"},
    {"filename": "B05_ACTION_ITEMS.md", "prompt_key": "B05", "format": "markdown"},
    {"filename": "B06_BUSINESS_CONTEXT.md", "prompt_key": "B06", "format": "markdown"},
    {"filename": "B07_TONE_AND_CONTEXT.md", "prompt_key": "B07", "format": "markdown"},
    {"filename": "B14_BLURBS_REQUESTED.md", "prompt_key": "B14", "format": "markdown"},
    {"filename": "B21_KEY_MOMENTS.md", "prompt_key": "B21", "format": "markdown"},
    {"filename": "B25_DELIVERABLES.md", "prompt_key": "B25", "format": "markdown"},
    {"filename": "B26_MEETING_METADATA.md", "prompt_key": "B26", "format": "markdown"},
    {"filename": "B32_THOUGHT_PROVOKING_IDEAS.md", "prompt_key": "B32", "format": "markdown"},
    {"filename": "B35_LINGUISTIC_PRIMITIVES.jsonl", "prompt_key": "B35", "format": "jsonl"},
]

if not ZO_TOKEN:
    raise SystemExit("Missing ZO_CLIENT_IDENTITY_TOKEN environment variable")


def ensure_directories():
    MEETINGS_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSING_LOG.parent.mkdir(parents=True, exist_ok=True)


def iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_meeting_folders() -> list[Path]:
    matches = []
    for root, dirs, _ in os.walk(MEETINGS_DIR):
        # skip quarantined folders entirely
        if "_quarantine" in root.split(os.sep):
            continue
        # prune hidden/system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for dirname in dirs:
            if "[M]" in dirname:
                matches.append(Path(root) / dirname)
    matches.sort()
    return matches


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def should_process(manifest: dict) -> bool:
    blocks = manifest.get("blocks_generated", {})
    brief = blocks.get("brief")
    stakeholder = blocks.get("stakeholder_intelligence")
    if brief:
        return False
    if stakeholder:
        return False
    return True


def guard_reason(meeting_path: Path, transcript: str) -> tuple[str | None, Path | None]:
    name_lower = meeting_path.name.lower()
    for keyword in NAME_GUARD_KEYWORDS:
        if keyword in name_lower:
            target = QUARANTINE_DIR / f"{meeting_path.name}_mg2_guard_failed"
            suffix = 1
            while target.exists():
                target = QUARANTINE_DIR / f"{meeting_path.name}_mg2_guard_failed_{suffix:02d}"
                suffix += 1
            shutil.move(meeting_path, target)
            return f"Folder name contains quarantine pattern: '{keyword}'", target
    content_lower = transcript.lower()
    if len(transcript.encode("utf-8")) < GUARD_MIN_SIZE_BYTES:
        return f"Stub transcript ({len(transcript.encode('utf-8'))} bytes, <{GUARD_MIN_SIZE_BYTES} bytes)", None
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern in content_lower:
            return f"Placeholder phrase detected ('{pattern}')", None
    return None, None


def clean_response(raw: str) -> str:
    text = raw.strip()
    for fence in ("```jsonl", "```json", "```markdown", "```md", "```"):
        if text.startswith(fence):
            text = text[len(fence) :].strip()
            break
    if text.endswith("```"):
        text = text[: -3].strip()
    return text


def build_prompt(block: dict, transcript: str, metadata: str, manifest: dict) -> str:
    prompt_path = PROMPTS_DIR / f"Generate_{block['prompt_key']}.prompt.md"
    prompt_template = prompt_path.read_text() if prompt_path.exists() else ""
    parts = [prompt_template.strip(), "", "TRANSCRIPT:", transcript.strip()]
    if metadata:
        parts.extend(["", "METADATA:", metadata.strip()])
    if manifest:
        parts.extend(["", "MANIFEST:", json.dumps(manifest, indent=2)])
    parts.append("")
    parts.append(f"Generate {block['filename']} now.")
    return "\n".join(parts)


async def call_zo(session: aiohttp.ClientSession, prompt: str) -> str:
    payload = {"input": prompt}
    async with session.post("https://api.zo.computer/zo/ask", json=payload) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"LLM responded {resp.status}: {body}")
        data = await resp.json()
        return data.get("output", "") or ""


def parse_b00_entries(b00_path: Path) -> list[dict]:
    if not b00_path.exists():
        return []
    entries = []
    for line in b00_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def summarize_zth_entries(entries: list[dict]) -> tuple[list[dict], dict]:
    summary = []
    processed = {"count": 0, "auto_executed": [], "queued": [], "directives_applied": []}
    for entry in entries:
        entry_id = entry.get("id")
        if not entry_id or entry_id.startswith("ZTH-REJECTED"):
            continue
        policy = (entry.get("execution_policy") or "").lower()
        task_type = entry.get("task_type", "unknown")
        if policy == "auto_execute":
            status = "executed"
            processed["auto_executed"].append(entry_id)
        elif policy == "queue":
            status = "queued"
            processed["queued"].append(entry_id)
        elif policy == "inline":
            status = "applied"
            processed["directives_applied"].append(entry_id)
        else:
            status = policy or "unknown"
        summary.append({"id": entry_id, "type": task_type, "status": status})
        processed["count"] += 1
    return summary, processed


def spawn_zth_workers(meeting_path: Path) -> dict | None:
    result = subprocess.run(
        ["python3", "N5/scripts/zth_spawn_worker.py", "--meeting-folder", str(meeting_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {
            "exit_code": result.returncode,
            "stderr": result.stderr.strip(),
            "stdout": result.stdout.strip(),
        }
    return None


def log_processing(entry: dict) -> None:
    PROCESSING_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSING_LOG, "a") as log:
        log.write(json.dumps(entry) + "\n")


def update_manifest(manifest: dict, zth_summary: list[dict], zth_processed: dict) -> dict:
    manifest.setdefault("blocks_generated", {})
    manifest["blocks_generated"]["stakeholder_intelligence"] = True
    manifest["blocks_generated"]["brief"] = True
    manifest["blocks_generated"]["transcript_processed"] = True
    manifest["status"] = "intelligence_generated"
    manifest["last_updated_by"] = "MG-2_Prompt"
    manifest["last_updated_at"] = iso_timestamp()
    manifest["zo_take_heed_count"] = zth_processed.get("count", 0)
    manifest["zo_take_heed_summary"] = zth_summary
    manifest["zo_take_heed_processed"] = zth_processed
    return manifest


async def process_meeting(
    session: aiohttp.ClientSession, meeting_path: Path, summary: dict
) -> None:
    meeting_name = meeting_path.name
    manifest_path = meeting_path / "manifest.json"
    manifest = load_json(manifest_path)
    needs_processing = should_process(manifest)
    if not needs_processing:
        return
    transcript_path = meeting_path / "transcript.jsonl"
    if not transcript_path.exists():
        log_processing(
            {
                "timestamp": iso_timestamp(),
                "stage": "MG-2",
                "meeting_id": meeting_name,
                "status": "mg2_failed",
                "reason": "Missing transcript.jsonl",
                "source": "Meeting Block Generation [MG-2]",
            }
        )
        summary["failed"].append((meeting_name, ["missing transcript.jsonl"]))
        return
    transcript = transcript_path.read_text()
    guard_msg, new_location = guard_reason(meeting_path, transcript)
    if guard_msg:
        entry = {
            "timestamp": iso_timestamp(),
            "stage": "MG-2",
            "meeting_id": meeting_name,
            "status": "mg2_skipped_guard",
            "reason": guard_msg,
            "source": "Meeting Block Generation [MG-2]",
        }
        if new_location:
            entry["location"] = str(new_location)
        log_processing(entry)
        summary["guard_skipped"].append((meeting_name, guard_msg))
        return
    metadata_path = meeting_path / "metadata.json"
    metadata = metadata_path.read_text() if metadata_path.exists() else ""
    missing_blocks = []
    for block in BLOCK_DEFINITIONS:
        dest = meeting_path / block["filename"]
        if dest.exists():
            continue
        missing_blocks.append(block)
    if not missing_blocks:
        return
    generated = []
    errors = []
    for block in missing_blocks:
        prompt = build_prompt(block, transcript, metadata, manifest)
        try:
            raw = await call_zo(session, prompt)
            content = clean_response(raw)
            dest_path = meeting_path / block["filename"]
            dest_path.write_text(content.strip() + ("\n" if content and not content.endswith("\n") else ""))
            generated.append(block["filename"])
            print(f"Generated {block['filename']} for {meeting_name}")
        except Exception as exc:
            errors.append(f"{block['filename']}: {exc}")
    b00_entries = parse_b00_entries(meeting_path / "B00_ZO_TAKE_HEED.jsonl")
    zth_summary, zth_processed = summarize_zth_entries(b00_entries)
    spawn_error = None
    if b00_entries:
        spawn_error = spawn_zth_workers(meeting_path)
        if spawn_error:
            errors.append(f"zth_spawn_worker failure: {spawn_error['stderr']}")
    manifest = update_manifest(manifest, zth_summary, zth_processed)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    log_entry = {
        "timestamp": iso_timestamp(),
        "stage": "MG-2",
        "meeting_id": meeting_name,
        "status": "mg2_completed" if not errors else "mg2_failed",
        "blocks_generated": generated,
        "zo_take_heed_processed": zth_processed,
        "source": "Meeting Block Generation [MG-2]",
    }
    if errors:
        log_entry["errors"] = errors
    log_processing(log_entry)
    if errors:
        summary["failed"].append((meeting_name, errors))
    else:
        summary["completed"].append((meeting_name, generated))


async def main():
    ensure_directories()
    meetings = find_meeting_folders()
    summary = {"completed": [], "guard_skipped": [], "failed": []}
    headers = {"authorization": ZO_TOKEN, "content-type": "application/json"}
    async with aiohttp.ClientSession(headers=headers) as session:
        for meeting in meetings:
            await process_meeting(session, meeting, summary)
    print("\nMG-2 Run Summary:")
    print(f"- Meetings completed: {len(summary['completed'])}")
    print(f"- Meetings skipped by guard rails: {len(summary['guard_skipped'])}")
    if summary["guard_skipped"]:
        for name, reason in summary["guard_skipped"]:
            print(f"  • {name}: {reason}")
    print(f"- Meetings that failed: {len(summary['failed'])}")
    if summary["failed"]:
        for name, errs in summary["failed"]:
            print(f"  • {name}: {errs}")


if __name__ == "__main__":
    asyncio.run(main())
