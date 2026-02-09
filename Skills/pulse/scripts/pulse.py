#!/usr/bin/env python3
"""
Pulse: Automated Build Orchestration System

Commands:
  start <slug>     - Begin automated orchestration
  status <slug>    - Show current build status
  stop <slug>      - Gracefully stop orchestration
  resume <slug>    - Resume a stopped build
  tick <slug>      - Run single orchestration cycle (for scheduled tasks)
  finalize <slug>  - Run post-build finalization (safety, tests, learnings)
"""

import argparse
import asyncio
import aiohttp
import json
import os
import sys
import sqlite3
import subprocess
import fcntl
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from pulse_common import PATHS, WORKSPACE, parse_drop_id, sort_wave_keys, get_drop_stream_order

# Paths
# WORKSPACE = Path("/home/workspace")  # Now imported from pulse_common
BUILDS_DIR = PATHS.BUILDS
CONVERSATIONS_DB = PATHS.WORKSPACE / "N5" / "data" / "conversations.db"
SKILLS_DIR = PATHS.SCRIPTS

# Config
DEFAULT_POLL_INTERVAL = 180  # 3 minutes
DEFAULT_DEAD_THRESHOLD = 900  # 15 minutes
DEFAULT_SPAWN_TIMEOUT = 300  # 5 minutes for API call to return
ZO_API_URL = "https://api.zo.computer/zo/ask"


def claim_task(slug: str, drop_id: str) -> dict | None:
    """Atomically claim a task from the pool."""
    meta_path = BUILDS_DIR / slug / "meta.json"
    
    if not meta_path.exists():
        return None
    
    with open(meta_path, "r+") as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            meta = json.load(f)
            pool = meta.get("task_pool", {})
            
            if not pool.get("enabled"):
                return None
            
            # Find first pending task
            for task in pool.get("tasks", []):
                if task["status"] == "pending":
                    task["status"] = "claimed"
                    task["claimed_by"] = drop_id
                    task["claimed_at"] = datetime.now(timezone.utc).isoformat()
                    
                    # Write back
                    f.seek(0)
                    f.truncate()
                    json.dump(meta, f, indent=2)
                    
                    return task
            
            return None  # Pool exhausted
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def update_task_status(slug: str, task_id: str, status: str, drop_id: str = None) -> bool:
    """Update a task's status in the pool."""
    meta_path = BUILDS_DIR / slug / "meta.json"
    
    if not meta_path.exists():
        return False
    
    with open(meta_path, "r+") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            meta = json.load(f)
            pool = meta.get("task_pool", {})
            
            if not pool.get("enabled"):
                return False
            
            # Find and update task
            for task in pool.get("tasks", []):
                if task["id"] == task_id:
                    old_status = task["status"]
                    task["status"] = status
                    if status in ("complete", "failed"):
                        task["completed_at"] = datetime.now(timezone.utc).isoformat()
                        if drop_id:
                            task["completed_by"] = drop_id
                    
                    # Write back
                    f.seek(0)
                    f.truncate()
                    json.dump(meta, f, indent=2)
                    
                    print(f"[TASK_POOL] Task {task_id}: {old_status} → {status}")
                    return True
            
            return False
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def get_pool_status(meta: dict) -> dict:
    """Get task pool status summary for STATUS.md."""
    pool = meta.get("task_pool", {})
    if not pool.get("enabled"):
        return None
    
    tasks = pool.get("tasks", [])
    status_counts = {
        "pending": 0,
        "claimed": 0,
        "complete": 0,
        "failed": 0
    }
    
    active_claims = []
    
    for task in tasks:
        status = task["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if status == "claimed":
            claimed_at = task.get("claimed_at")
            claimed_by = task.get("claimed_by", "unknown")
            duration = ""
            if claimed_at:
                try:
                    claimed_time = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
                    duration_min = int((datetime.now(timezone.utc) - claimed_time).total_seconds() / 60)
                    duration = f"({duration_min} min)"
                except:
                    pass
            
            active_claims.append(f"- {claimed_by} → {task['id']} {duration}")
    
    return {
        "counts": status_counts,
        "active_claims": active_claims,
        "total": len(tasks)
    }


def inject_pool_claim_instructions(brief_content: str, slug: str, drop_id: str = "UNKNOWN") -> str:
    """Inject task pool claiming instructions for pool workers."""
    pool_instructions = f"""

## Task Pool Worker Instructions

You are pool worker **{drop_id}**. Your execution pattern:

1. **Claim a task** by running:
```bash
python3 -c "
import sys; sys.path.insert(0, '/home/workspace/Skills/pulse/scripts')
from pulse import claim_task
task = claim_task('{slug}', '{drop_id}')
if task:
    print(f'CLAIMED: {{task[\"id\"]}}')
    print(f'TYPE: {{task.get(\"type\", \"unknown\")}}')
    print(f'TARGET: {{task.get(\"target\", \"unknown\")}}')
else:
    print('POOL_EXHAUSTED')
"
```

2. **Execute the claimed task** according to its type and target
3. **Mark complete** when done by running:
```bash
python3 -c "
import sys; sys.path.insert(0, '/home/workspace/Skills/pulse/scripts')
from pulse import update_task_status
update_task_status('{slug}', 'TASK_ID_HERE', 'complete', '{drop_id}')
"
```
4. **Repeat**: Claim another task until pool is exhausted (POOL_EXHAUSTED)
5. **Deposit summary**: Write deposit with summary of ALL completed tasks

## On Pool Exhaustion

When claiming returns POOL_EXHAUSTED, write your final deposit summarizing all work completed.

"""
    
    # Insert after brief frontmatter or at beginning of content
    lines = brief_content.split('\n')
    insert_idx = 0
    
    # Skip frontmatter if present
    if lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                insert_idx = i + 1
                break
    
    lines.insert(insert_idx, pool_instructions)
    return '\n'.join(lines)


def load_meta(slug: str) -> dict:
    """Load build meta.json"""
    meta_path = BUILDS_DIR / slug / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Build not found: {slug}")
    with open(meta_path) as f:
        return json.load(f)


def save_meta(slug: str, meta: dict):
    """Save build meta.json"""
    meta_path = BUILDS_DIR / slug / "meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)


def find_drop_brief_path(slug: str, drop_id: str) -> Path:
    """Find the file path for a Drop brief in the build's drops/ folder."""
    drops_dir = BUILDS_DIR / slug / "drops"

    # Try both D and C prefixes
    for pattern in [f"{drop_id}-*.md", f"C*.md"]:
        for f in drops_dir.glob(pattern):
            if f.stem.startswith(drop_id):
                return f

    # Fallback: exact match
    for f in drops_dir.glob("*.md"):
        if f.stem.split("-")[0] == drop_id:
            return f

    raise FileNotFoundError(f"Brief not found for {drop_id}")


def ensure_launcher(slug: str, drop_id: str) -> Path:
    """Create/update a manual-launcher markdown file for a Drop and return its path."""
    brief_path = find_drop_brief_path(slug, drop_id)
    launchers_dir = BUILDS_DIR / slug / "launchers"
    launchers_dir.mkdir(parents=True, exist_ok=True)

    launcher_path = launchers_dir / f"{drop_id}.md"

    today = datetime.now(timezone.utc).date().isoformat()
    content = f"""---
created: {today}
last_edited: {today}
version: 1.0
provenance: pulse:{slug}
---

# Launcher: {slug} / {drop_id}

## Paste into a new thread

```text
Load and execute: file 'N5/builds/{slug}/drops/{brief_path.name}'

When complete, write deposit to:
file 'N5/builds/{slug}/deposits/{drop_id}.json'
```

## After you finish

- Confirm the deposit exists at the path above.
- Then run:
  - `python3 Skills/pulse/scripts/pulse.py tick {slug}`
  - (or wait for the Sentinel to tick)
"""

    launcher_path.write_text(content)
    return launcher_path


def load_drop_brief(slug: str, drop_id: str) -> str:
    """Load a Drop brief from drops/ folder"""
    return find_drop_brief_path(slug, drop_id).read_text()


def get_deposit(slug: str, drop_id: str) -> Optional[dict]:
    """Get a Drop's deposit if it exists"""
    deposit_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}.json"
    if deposit_path.exists():
        with open(deposit_path) as f:
            return json.load(f)
    return None


def get_filter_result(slug: str, drop_id: str) -> Optional[dict]:
    """Get Filter judgment for a Drop if it exists"""
    filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_filter.json"
    if filter_path.exists():
        with open(filter_path) as f:
            return json.load(f)
    return None


def register_drop_conversation(drop_id: str, slug: str, convo_id: str):
    """Register a Drop's conversation in conversations.db"""
    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    # Check if conversations table has the columns we need
    cursor.execute("PRAGMA table_info(conversations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "build_slug" not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN build_slug TEXT")
    if "drop_id" not in columns:
        cursor.execute("ALTER TABLE conversations ADD COLUMN drop_id TEXT")
    
    # Insert or update
    cursor.execute("""
        INSERT INTO conversations (id, type, status, created_at, updated_at, build_slug, drop_id)
        VALUES (?, 'headless_worker', 'running', ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET build_slug=?, drop_id=?, updated_at=?
    """, (convo_id, now, now, slug, drop_id, slug, drop_id, now))
    
    conn.commit()
    conn.close()


def update_drop_conversation_status(convo_id: str, status: str):
    """Update a Drop conversation's status in conversations.db"""
    if not convo_id or convo_id.startswith("unknown_"):
        return
    conn = sqlite3.connect(CONVERSATIONS_DB)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute("""
        UPDATE conversations 
        SET status = ?, updated_at = ?, completed_at = ?
        WHERE id = ?
    """, (status, now, now if status == "complete" else None, convo_id))
    conn.commit()
    conn.close()


def update_status_md(slug: str, meta: dict):
    """Update STATUS.md with current progress"""
    status_path = BUILDS_DIR / slug / "STATUS.md"

    drops = meta.get("drops", {})
    complete = [d for d, info in drops.items() if info.get("status") == "complete"]
    running = [d for d, info in drops.items() if info.get("status") == "running"]
    awaiting_manual = [d for d, info in drops.items() if info.get("status") == "awaiting_manual"]
    pending = [d for d, info in drops.items() if info.get("status") == "pending"]
    superseded = [d for d, info in drops.items() if info.get("status") == "superseded"]
    dead = [d for d, info in drops.items() if info.get("status") == "dead"]
    failed = [d for d, info in drops.items() if info.get("status") == "failed"]

    total = len(drops)
    pct = int(len(complete) / total * 100) if total > 0 else 0

    if meta.get("waves"):
        gate_line = f"**Wave:** {meta.get('active_wave', '?')}"
    else:
        gate_line = f"**Legacy Stream Gate:** {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}"

    gate = meta.get("gate")
    gate_text = ""
    if isinstance(gate, dict) and gate.get("reason"):
        gate_text = f"\n**Gate:** {gate.get('type', 'gate')} — {gate.get('reason')}"

    awaiting_lines = "\n".join(
        f"- [ ] {d} → run: `python3 Skills/pulse/scripts/pulse.py launch {slug} {d}`"
        for d in sorted(awaiting_manual)
    )

    # Build superseded lines with superseded_by info
    superseded_lines = "\n".join(
        f"- [~] {d} (superseded by {drops[d].get('superseded_by', '?')})"
        for d in sorted(superseded)
    )

    # Add task pool status if enabled
    pool_status = get_pool_status(meta)
    pool_section = ""
    if pool_status:
        counts = pool_status["counts"]
        active_claims = pool_status["active_claims"]
        
        pool_section = f"""
## Task Pool
| Status | Count |
|--------|-------|
| Pending | {counts['pending']} |
| Claimed | {counts['claimed']} |
| Complete | {counts['complete']} |
| Failed | {counts['failed']} |

Active claims:
{chr(10).join(active_claims) if active_claims else '(none)'}

"""

    content = f"""# Build Status: {slug}

**Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {meta.get('status', 'unknown')}
{gate_line}{gate_text}
**Progress:** {len(complete)}/{total} Drops ({pct}%)
{pool_section}
## Awaiting Manual ({len(awaiting_manual)})
{awaiting_lines or '(none)'}

## Running ({len(running)})
{chr(10).join(f'- [ ] {d} (since {drops[d].get("started_at", "?")[:16]})' for d in sorted(running)) or '(none)'}

## Pending ({len(pending)})
{chr(10).join(f'- [ ] {d}' for d in sorted(pending)) or '(none)'}

## Superseded ({len(superseded)})
{superseded_lines or '(none)'}

## Complete ({len(complete)})
{chr(10).join(f'- [x] {d}' for d in sorted(complete)) or '(none)'}

## Dead ({len(dead)})
{chr(10).join(f'- [!] {d}' for d in sorted(dead)) or '(none)'}

## Failed ({len(failed)})
{chr(10).join(f'- [x] {d}' for d in sorted(failed)) or '(none)'}
"""

    status_path.write_text(content)


async def send_sms(message: str):
    """Send SMS via Zo's send_sms_to_user (calls back to Zo)"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        print(f"[SMS SKIPPED - no token] {message}")
        return
    
    prompt = f"Send this SMS to V immediately, no commentary: {message}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            result = await resp.json()
            print(f"[SMS SENT] {message}")
            return result


def collect_broadcasts(slug: str) -> list[dict]:
    """Collect all broadcasts from completed deposits."""
    broadcasts = []
    deposits_dir = BUILDS_DIR / slug / "deposits"
    
    if not deposits_dir.exists():
        return broadcasts
    
    for deposit_path in deposits_dir.glob("*.json"):
        # Skip filter results
        if "_filter" in deposit_path.name:
            continue
        
        try:
            with open(deposit_path) as f:
                deposit = json.load(f)
            
            # Check if deposit has broadcast field
            if deposit.get("broadcast"):
                broadcasts.append({
                    "drop_id": deposit.get("drop_id", deposit_path.stem),
                    "broadcast": deposit["broadcast"],
                    "timestamp": deposit.get("timestamp")
                })
        except (json.JSONDecodeError, IOError) as e:
            print(f"[BROADCAST] Warning: Could not read {deposit_path.name}: {e}")
    
    return broadcasts


def inject_broadcasts(brief_content: str, broadcasts: list[dict]) -> str:
    """Inject broadcasts section into brief before spawning."""
    if not broadcasts:
        return brief_content
    
    # Create broadcasts section
    section = "\n\n## Broadcasts from Prior Drops\n\n"
    section += "These findings were shared by earlier Drops in this build:\n\n"
    
    for b in broadcasts:
        section += f"- **{b['drop_id']}:** {b['broadcast']}\n"
    
    # Insert before common section markers or at end
    for marker in ["## Requirements", "## Context", "## Files to Read"]:
        if marker in brief_content:
            return brief_content.replace(marker, section + marker, 1)
    
    # If no markers found, append at end
    return brief_content + section


async def spawn_drop(slug: str, drop_id: str, brief: str, model: str = None) -> str:
    """Spawn a Drop via /zo/ask, return conversation_id
    
    Note: The /zo/ask API may not return the actual conversation_id.
    We generate a tracking ID but rely on deposit detection for completion.
    """
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    # Collect and inject broadcasts from prior Drops
    broadcasts = collect_broadcasts(slug)
    brief_with_broadcasts = inject_broadcasts(brief, broadcasts)
    
    # Check if this is a pool worker and inject pool instructions
    meta = load_meta(slug)
    pool = meta.get("task_pool", {})
    drops = meta.get("drops", {})
    drop_info = drops.get(drop_id, {})
    
    if pool.get("enabled") and drop_id in pool.get("worker_drops", []):
        print(f"[POOL] Injecting pool claim instructions for {drop_id}")
        brief_with_broadcasts = inject_pool_claim_instructions(brief_with_broadcasts, slug, drop_id)
    
    # Build deposit format as separate string to avoid f-string escaping issues
    deposit_format = '''{\n  \"drop_id\": \"''' + drop_id + '''\",\n  \"status\": \"complete\",\n  \"summary\": \"What you accomplished\",\n  \"artifacts\": [\"list\", \"of\", \"files\", \"created\"],\n  \"learnings\": [\"any lessons for other workers\"],\n  \"errors\": []\n}'''
    
    full_prompt = f"""You are a Pulse Drop executing build \"{slug}\", task \"{drop_id}\".

**YOUR IDENTITY:**
- Build: {slug}
- Drop ID: {drop_id}
- Type: Headless worker (no human in loop)

**EXECUTION PROTOCOL:**
1. Read the brief below carefully
2. Execute the task completely
3. When done, write your deposit JSON to: N5/builds/{slug}/deposits/{drop_id}.json
4. DO NOT commit code (orchestrator handles commits)
5. If blocked, write deposit with status \"blocked\" and explain why

**DEPOSIT FORMAT:**
{deposit_format}

Status can be \"complete\", \"blocked\", or \"partial\".

---
BRIEF:
---
{brief_with_broadcasts}"""
    
    request_body = {"input": full_prompt}
    if model:
        request_body["model_name"] = model
    
    print(f"[SPAWN] Spawning Drop {drop_id} via /zo/ask...")
    
    start = datetime.now()
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_SPAWN_TIMEOUT)) as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json=request_body
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"API returned {resp.status}: {await resp.text()}")
            
            result = await resp.json()
            elapsed = datetime.now() - start
            
            # Generate tracking ID
            tracking_id = f"pulse_{slug}_{drop_id}_{int(start.timestamp())}"
            
            print(f"[SPAWN] Drop {drop_id} spawned (tracking: {tracking_id}, {elapsed.total_seconds():.1f}s)")
            return tracking_id


def start_build(slug: str):
    """Start a build"""
    meta = load_meta(slug)
    meta["status"] = "active"
    meta["started_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    update_status_md(slug, meta)
    print(f"[PULSE] Build {slug} started")


def stop_build(slug: str):
    """Stop a build"""
    meta = load_meta(slug)
    meta["status"] = "stopped"
    meta["stopped_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    update_status_md(slug, meta)
    print(f"[PULSE] Build {slug} stopped")


def resume_build(slug: str):
    """Resume a stopped build"""
    meta = load_meta(slug)
    if meta.get("status") != "stopped":
        print(f"[ERROR] Build {slug} is not stopped (current: {meta.get('status')})")
        return
    
    meta["status"] = "active"
    meta["resumed_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    update_status_md(slug, meta)
    print(f"[PULSE] Build {slug} resumed")


def _normalize_meta_for_waves(meta: dict) -> None:
    """Normalize legacy meta structure into waves structure in memory."""
    if meta.get("waves"):
        return  # Already using waves
    
    # Build waves from currents or drop stream/order
    waves = {}
    drops = meta.get("drops", {})
    
    if meta.get("currents"):
        # currents = {"chain1": ["D1.1", "D1.2"], "chain2": ["D2.1"]}
        wave_num = 1
        for chain_name, chain_drops in meta["currents"].items():
            for drop_id in chain_drops:
                wave_key = f"W{wave_num}"
                if wave_key not in waves:
                    waves[wave_key] = []
                waves[wave_key].append(drop_id)
            wave_num += 1
    else:
        # Group by stream number
        streams = {}
        for drop_id, info in drops.items():
            try:
                stream_num, order = get_drop_stream_order(drop_id, info)
                if stream_num not in streams:
                    streams[stream_num] = []
                streams[stream_num].append((order, drop_id))
            except Exception:
                # Fallback: put in stream 1
                if 1 not in streams:
                    streams[1] = []
                streams[1].append((1, drop_id))
        
        # Convert streams to waves
        for stream_num in sorted(streams.keys()):
            wave_key = f"W{stream_num}"
            waves[wave_key] = [drop_id for _, drop_id in sorted(streams[stream_num])]
    
    meta["waves"] = waves
    meta["active_wave"] = "W1"


def _get_active_wave(meta: dict) -> str | None:
    """Get the currently active wave."""
    waves = meta.get("waves", {})
    if not waves:
        return None
    
    active = meta.get("active_wave")
    if active and active in waves:
        return active
    
    # Default to first wave
    sorted_waves = sort_wave_keys(list(waves.keys()))
    return sorted_waves[0] if sorted_waves else None


def _can_advance_wave(meta: dict) -> bool:
    """Check if current wave is complete and can advance."""
    waves = meta.get("waves", {})
    active_wave = _get_active_wave(meta)
    
    if not active_wave or active_wave not in waves:
        return False
    
    drops = meta.get("drops", {})
    
    # Check if all blocking Drops in active wave are complete
    for drop_id in waves[active_wave]:
        info = drops.get(drop_id, {})
        if info.get("blocking", True):  # Default to blocking=True
            status = info.get("status", "pending")
            if status not in ("complete", "failed", "dead", "superseded"):
                return False
    
    return True


def _advance_wave(meta: dict) -> bool:
    """Advance to the next wave if possible. Returns True if advanced."""
    if not _can_advance_wave(meta):
        return False
    
    waves = meta.get("waves", {})
    active_wave = meta.get("active_wave")
    
    if not active_wave:
        return False
    
    sorted_waves = sort_wave_keys(list(waves.keys()))
    try:
        current_idx = sorted_waves.index(active_wave)
        if current_idx + 1 < len(sorted_waves):
            next_wave = sorted_waves[current_idx + 1]
            meta["active_wave"] = next_wave
            print(f"[WAVE] Advanced from {active_wave} to {next_wave}")
            return True
    except ValueError:
        pass
    
    return False


def _build_stream_chains(drops: dict) -> dict:
    """Build mapping of stream_num -> [(order, drop_id), ...]"""
    streams = {}
    for drop_id, info in drops.items():
        try:
            stream_num, order = get_drop_stream_order(drop_id, info)
            if stream_num not in streams:
                streams[stream_num] = []
            streams[stream_num].append((order, drop_id))
        except Exception:
            continue
    
    # Sort by order within each stream
    for stream_num in streams:
        streams[stream_num].sort()
    
    return streams


def _can_run_stream_order(drop_id: str, drops: dict, stream_chains: dict, complete: set) -> bool:
    """Check if Drop can run based on stream sequential ordering."""
    try:
        stream_num, order = get_drop_stream_order(drop_id, drops.get(drop_id, {}))
    except Exception:
        return True
    
    if stream_num not in stream_chains:
        return True
    
    chain = stream_chains[stream_num]
    
    for chain_order, chain_drop_id in chain:
        if chain_drop_id == drop_id:
            break
        if chain_order < order and chain_drop_id not in complete:
            return False
    
    return True


def check_build_complete(meta: dict) -> bool:
    """Check if all blocking Drops are complete"""
    drops = meta.get("drops", {})
    
    for drop_id, info in drops.items():
        # Skip non-blocking Drops
        if not info.get("blocking", True):
            continue
        
        status = info.get("status", "pending")
        if status not in ("complete", "failed", "dead", "superseded"):
            return False
    
    return True


def _check_pool_complete(meta: dict) -> bool:
    """Check if task pool is exhausted (no pending tasks)."""
    pool = meta.get("task_pool", {})
    if not pool.get("enabled"):
        return True  # No pool, consider complete
    
    tasks = pool.get("tasks", [])
    for task in tasks:
        if task["status"] == "pending":
            return False
    
    return True


def get_ready_drops(meta: dict) -> list[str]:
    """Get list of Drops ready to spawn.
    
    Rules:
    - waves mode: only drops in active wave, not blocked by dependencies or stream order
    - legacy mode: respects currents, stream sequencing as before
    
    In waves mode:
      - parallel: drops in same wave can run in parallel
      - sequential: within a stream, order k+1 waits for order k to be complete

    legacy mode (no meta.waves):
      - If current_stream is present, only consider drops in that stream
      - Preserve legacy currents sequencing if meta.currents exists
    """
    ready: list[str] = []
    drops = meta.get("drops", {})
    currents = meta.get("currents", {})

    complete = {d for d, info in drops.items() if info.get("status") == "complete"}
    stream_chains = _build_stream_chains(drops)

    allowed: set[str]
    if meta.get("waves"):
        active_wave = _get_active_wave(meta)
        if not active_wave:
            return []
        if isinstance(meta.get("gate"), dict) and meta["gate"].get("type") == "wave_blocked":
            return []
        allowed = set((meta.get("waves") or {}).get(active_wave, []) or [])
    elif meta.get("current_stream") is not None:
        allowed = set()
        try:
            cur = int(meta.get("current_stream"))
        except Exception:
            cur = None
        for drop_id, info in drops.items():
            try:
                stream, _ = get_drop_stream_order(drop_id, info)
            except Exception:
                continue
            if cur is None or stream == cur:
                allowed.add(drop_id)
    else:
        allowed = set(drops.keys())

    for drop_id in sorted(allowed):
        info = drops.get(drop_id, {})
        if info.get("status") not in ("pending",):
            continue

        # Dependencies
        depends_on = info.get("depends_on", [])
        if not all(d in complete for d in depends_on):
            continue

        # Legacy Currents (sequential chains)
        blocked_by_current = False
        for chain in currents.values():
            if drop_id in chain:
                idx = chain.index(drop_id)
                if idx > 0 and chain[idx - 1] not in complete:
                    blocked_by_current = True
                    break
        if blocked_by_current:
            continue

        # Stream sequential ordering
        if not _can_run_stream_order(drop_id, drops, stream_chains, complete):
            continue

        ready.append(drop_id)

    return ready


def get_running_drops(meta: dict) -> list[tuple[str, dict]]:
    """Get list of running Drops with their info"""
    return [
        (drop_id, info)
        for drop_id, info in meta.get("drops", {}).items()
        if info.get("status") == "running"
    ]


def check_stream_complete(meta: dict) -> bool:
    """Legacy: Check if current stream is complete (terminal in that stream)."""
    if meta.get("current_stream") is None:
        return False

    try:
        current_stream = int(meta.get("current_stream", 1))
    except Exception:
        current_stream = 1

    drops = meta.get("drops", {})

    for drop_id, info in drops.items():
        try:
            stream_num, _ = get_drop_stream_order(drop_id, info)
        except Exception:
            continue

        if stream_num == current_stream:
            if info.get("status") not in ["complete", "failed", "dead"]:
                return False

    return True


def advance_stream(meta: dict) -> bool:
    """Legacy: Advance to next stream if current is complete. Returns True if advanced."""
    if not check_stream_complete(meta):
        return False

    current = meta.get("current_stream", 1)
    total = meta.get("total_streams", 1)

    try:
        current = int(current)
    except Exception:
        current = 1
    try:
        total = int(total)
    except Exception:
        total = 1

    if current < total:
        meta["current_stream"] = current + 1
        return True

    return False


def check_first_wins(slug: str, meta: dict) -> bool:
    """Check if a hypothesis was confirmed and supersede others."""
    if not meta.get("first_wins"):
        return False
    
    hypothesis_group = meta.get("hypothesis_group") or list(meta.get("drops", {}).keys())
    
    # Find confirmed hypothesis
    winner = None
    for drop_id in hypothesis_group:
        deposit = get_deposit(slug, drop_id)
        if deposit and deposit.get("verdict") == "confirmed":
            winner = drop_id
            break
    
    if not winner:
        return False
    
    # Supersede others
    drops = meta.get("drops", {})
    superseded_count = 0
    for drop_id in hypothesis_group:
        if drop_id == winner:
            continue
        if drops.get(drop_id, {}).get("status") in ("pending", "running"):
            drops[drop_id]["status"] = "superseded"
            drops[drop_id]["superseded_by"] = winner
            drops[drop_id]["superseded_at"] = datetime.now(timezone.utc).isoformat()
            superseded_count += 1
            print(f"[FIRST_WINS] {drop_id} superseded by {winner}")
    
    if superseded_count > 0:
        save_meta(slug, meta)
        print(f"[FIRST_WINS] {superseded_count} Drops superseded by {winner}")
        return True
    
    return False


async def summarize_build(slug: str, meta: dict) -> str:
    """Generate completion summary"""
    deposits_dir = BUILDS_DIR / slug / "deposits"
    summaries = []
    
    for drop_id in sorted(meta.get("drops", {}).keys()):
        deposit = get_deposit(slug, drop_id)
        if deposit:
            summaries.append(f"**{drop_id}:** {deposit.get('summary', 'No summary')}")
    
    return "\n".join(summaries)


async def tick(slug: str):
    """Run one orchestration cycle"""
    print(f"\n[PULSE TICK] {slug} @ {datetime.now(timezone.utc).isoformat()}")
    
    meta = load_meta(slug)
    
    if meta.get("status") == "complete":
        print(f"[PULSE] Build {slug} already complete")
        return
    
    if meta.get("status") == "stopped":
        print(f"[PULSE] Build {slug} is stopped")
        return
    
    # 1. Check for new deposits from running Drops
    running = get_running_drops(meta)
    broadcasts_updated = False
    
    for drop_id, info in running:
        deposit = get_deposit(slug, drop_id)
        if deposit:
            print(f"[DEPOSIT] Found deposit for {drop_id}: {deposit.get('status', 'unknown')}")
            
            # Update Drop status based on deposit
            old_status = info.get("status", "unknown")
            new_status = deposit.get("status", "complete")
            
            # For pool workers, check if they completed tasks
            pool = meta.get("task_pool", {})
            if pool.get("enabled") and drop_id in pool.get("worker_drops", []):
                # Update completed tasks in pool
                completed_tasks = deposit.get("completed_tasks", [])
                for task_info in completed_tasks:
                    task_id = task_info.get("id")
                    task_status = task_info.get("status", "complete")
                    if task_id:
                        update_task_status(slug, task_id, task_status, drop_id)
            
            if new_status == "complete":
                info["status"] = "complete"
                info["completed_at"] = datetime.now(timezone.utc).isoformat()
                update_drop_conversation_status(info.get("conversation_id"), "complete")
            elif new_status == "blocked":
                info["status"] = "failed"
                info["failure_reason"] = deposit.get("summary", "Blocked")
                info["failed_at"] = datetime.now(timezone.utc).isoformat()
                update_drop_conversation_status(info.get("conversation_id"), "failed")
            elif new_status == "partial":
                info["status"] = "failed"
                info["failure_reason"] = "Partial completion"
                info["failed_at"] = datetime.now(timezone.utc).isoformat()
                update_drop_conversation_status(info.get("conversation_id"), "failed")
            
            print(f"[STATUS] {drop_id}: {old_status} → {info['status']}")
            broadcasts_updated = True
    
    # 2. Check for dead Drops (running too long)
    now = datetime.now(timezone.utc)
    for drop_id, info in running:
        if info.get("status") != "running":
            continue  # Skip if already processed above
        
        started_str = info.get("started_at")
        if not started_str:
            continue
        
        try:
            started = datetime.fromisoformat(started_str.replace("Z", "+00:00"))
            elapsed = now - started
            if elapsed.total_seconds() > DEFAULT_DEAD_THRESHOLD:
                print(f"[DEAD] {drop_id} has been running for {elapsed.total_seconds()/60:.0f} minutes")
                info["status"] = "dead"
                info["dead_at"] = now.isoformat()
                info["dead_reason"] = f"Running for {elapsed.total_seconds()/60:.0f} minutes"
                update_drop_conversation_status(info.get("conversation_id"), "failed")
                broadcasts_updated = True
        except ValueError:
            continue
    
    # 3. Check for first-wins supersession
    if check_first_wins(slug, meta):
        broadcasts_updated = True
    
    # 4. Normalize legacy meta to waves for processing
    _normalize_meta_for_waves(meta)
    
    # 5. Advance wave/stream if current is complete
    wave_advanced = False
    if meta.get("waves"):
        if _advance_wave(meta):
            wave_advanced = True
            broadcasts_updated = True
    else:
        if advance_stream(meta):
            wave_advanced = True
            broadcasts_updated = True
    
    # 6. Spawn ready Drops
    ready = get_ready_drops(meta)
    spawned = []
    
    for drop_id in ready:
        try:
            info = meta["drops"][drop_id]
            spawn_mode = info.get("spawn_mode", "auto")
            
            if spawn_mode == "manual":
                # Create launcher and mark as awaiting manual
                launcher_path = ensure_launcher(slug, drop_id)
                info["status"] = "awaiting_manual"
                info["launcher_created_at"] = datetime.now(timezone.utc).isoformat()
                print(f"[MANUAL] {drop_id} → launcher at {launcher_path}")
            else:
                # Auto spawn
                brief = load_drop_brief(slug, drop_id)
                model = meta.get("model")
                
                conversation_id = await spawn_drop(slug, drop_id, brief, model)
                
                info["status"] = "running"
                info["started_at"] = datetime.now(timezone.utc).isoformat()
                info["conversation_id"] = conversation_id
                
                register_drop_conversation(drop_id, slug, conversation_id)
                spawned.append(drop_id)
                
        except Exception as e:
            print(f"[ERROR] Failed to spawn {drop_id}: {e}")
            meta["drops"][drop_id]["status"] = "failed"
            meta["drops"][drop_id]["failure_reason"] = f"Spawn error: {e}"
            meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
    
    if spawned:
        print(f"[SPAWN] Spawned: {', '.join(spawned)}")
        broadcasts_updated = True
    
    # 7. Check if build is complete
    build_complete = check_build_complete(meta)
    pool_complete = _check_pool_complete(meta)
    
    if build_complete and pool_complete:
        if meta.get("status") != "complete":
            print(f"[COMPLETE] Build {slug} is complete!")
            meta["status"] = "complete"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Generate summary
            summary = await summarize_build(slug, meta)
            meta["summary"] = summary
            
            await send_sms(f"[PULSE] {slug} COMPLETE ✅")
            broadcasts_updated = True
    
    # 8. Save and update
    if broadcasts_updated:
        save_meta(slug, meta)
        update_status_md(slug, meta)
    
    print(f"[PULSE] Tick complete. Ready: {len(ready)}, Spawned: {len(spawned)}")


def show_status(slug: str):
    """Show build status"""
    meta = load_meta(slug)
    drops = meta.get("drops", {})

    complete = sum(1 for d in drops.values() if d.get("status") == "complete")
    running = sum(1 for d in drops.values() if d.get("status") == "running")
    awaiting_manual = sum(1 for d in drops.values() if d.get("status") == "awaiting_manual")
    pending = sum(1 for d in drops.values() if d.get("status") == "pending")
    superseded = sum(1 for d in drops.values() if d.get("status") == "superseded")
    dead = sum(1 for d in drops.values() if d.get("status") == "dead")
    failed = sum(1 for d in drops.values() if d.get("status") == "failed")

    gate = meta.get("gate")
    gate_line = ""
    if isinstance(gate, dict) and gate.get("reason"):
        gate_line = f"Gate: {gate.get('type', 'gate')} — {gate.get('reason')}\n"

    if meta.get("waves"):
        gate_scope = f"Wave: {meta.get('active_wave', '?')}\n"
    else:
        gate_scope = f"Legacy Stream Gate: {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}\n"

    # Add pool status if enabled
    pool_status = get_pool_status(meta)
    pool_text = ""
    if pool_status:
        counts = pool_status["counts"]
        pool_text = f"""
Task Pool:
  Pending: {counts['pending']}
  Claimed: {counts['claimed']}
  Complete: {counts['complete']}
  Failed: {counts['failed']}
"""

    print(f"""
Build: {slug}
Status: {meta.get('status', 'unknown')}
{gate_scope}{gate_line}
Drops:
  Complete:        {complete}
  Running:         {running}
  Awaiting Manual: {awaiting_manual}
  Pending:         {pending}
  Superseded:      {superseded}
  Dead:            {dead}
  Failed:          {failed}
  Total:           {len(drops)}
{pool_text}
Progress: {complete}/{len(drops)} ({int(complete/len(drops)*100) if drops else 0}%)
""")


def retry_drop(slug: str, drop_id: str, reason: str = None):
    """Reset a Drop to pending, archive old deposit, optionally appends retry reason to brief.
    
    Based on Theo's lesson: If output is bad, don't keep appending corrections.
    Revert and restart with corrected input. This gives the model a clean slate
    with better context rather than compounding errors.
    """
    meta = load_meta(slug)
    
    if drop_id not in meta.get("drops", {}):
        print(f"[ERROR] Drop {drop_id} not found in build {slug}")
        return
    
    drop_info = meta["drops"][drop_id]
    old_status = drop_info.get("status")
    
    # Archive old deposit if exists
    deposit_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}.json"
    if deposit_path.exists():
        archive_dir = BUILDS_DIR / slug / "deposits" / "archived"
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"{drop_id}_{timestamp}.json"
        deposit_path.rename(archive_path)
        print(f"[RETRY] Archived old deposit to {archive_path.name}")
    
    # Archive filter result if exists
    filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_filter.json"
    if filter_path.exists():
        archive_dir = BUILDS_DIR / slug / "deposits" / "archived"
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"{drop_id}_filter_{timestamp}.json"
        filter_path.rename(archive_path)
    
    # Reset Drop status
    drop_info["status"] = "pending"
    drop_info.pop("started_at", None)
    drop_info.pop("conversation_id", None)
    drop_info.pop("failure_reason", None)
    drop_info["retry_count"] = drop_info.get("retry_count", 0) + 1
    drop_info["last_retry"] = datetime.now(timezone.utc).isoformat()
    
    # Optionally update brief with retry reason
    if reason:
        try:
            brief_path = find_drop_brief_path(slug, drop_id)
            brief_content = brief_path.read_text()
            
            # Append retry context section
            retry_section = f"""

---

## ⚠️ Retry Context (Attempt {drop_info['retry_count'] + 1})

**Previous attempt failed because:** {reason}

**What to do differently:**
- Address the issue described above
- Review the archived deposit to understand what went wrong
- Follow the brief more carefully

"""
            # Insert before "## On Completion" if it exists, otherwise append
            if "## On Completion" in brief_content:
                brief_content = brief_content.replace("## On Completion", retry_section + "## On Completion")
            else:
                brief_content += retry_section
            
            brief_path.write_text(brief_content)
            print(f"[RETRY] Updated brief with retry context")
        except Exception as e:
            print(f"[RETRY] Warning: Could not update brief: {e}")
    
    save_meta(slug, meta)
    update_status_md(slug, meta)
    
    print(f"[RETRY] {drop_id} reset from '{old_status}' to 'pending' (attempt {drop_info['retry_count'] + 1})")
    print(f"[RETRY] Run 'pulse tick {slug}' or wait for Sentinel to re-spawn")


def validate_plan(slug: str):
    """Validate plan completeness before starting a build.
    
    Based on Theo's lesson: Plans are context vehicles. An incomplete plan
    means the model will guess, and guessing compounds errors across Drops.
    """
    validator_path = SKILLS_DIR / "pulse_plan_validator.py"
    
    if not validator_path.exists():
        print(f"[ERROR] Plan validator not found at {validator_path}")
        return
    
    result = subprocess.run(
        ["python3", str(validator_path), slug],
        capture_output=False,
        cwd=str(WORKSPACE)
    )
    
    if result.returncode == 0:
        print(f"\n✅ Plan validation passed. Safe to start build.")
    else:
        print(f"\n❌ Plan validation failed. Fix issues before starting build.")
        print(f"   Run: python3 {validator_path} {slug} --fix")


async def finalize_build(slug: str):
    """Run post-build finalization: safety checks, integration tests, harvest learnings"""
    print(f"\n[FINALIZE] {slug}")
    
    meta = load_meta(slug)
    results = {
        "slug": slug,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verification": None,
        "integration_tests": None,
        "learnings_harvested": 0,
        "success": True
    }
    
    # 1. Verify artifacts
    print("[FINALIZE] Verifying artifacts...")
    try:
        verify_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_safety.py"), "verify", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        results["verification"] = {
            "passed": verify_result.returncode == 0,
            "output": verify_result.stdout
        }
        if verify_result.returncode == 0:
            print("[FINALIZE] ✅ Artifact verification passed")
        else:
            print(f"[FINALIZE] ❌ Artifact verification failed")
            results["success"] = False
    except Exception as e:
        print(f"[FINALIZE] Verification error: {e}")
        results["verification"] = {"passed": False, "error": str(e)}
        results["success"] = False
    
    # 2. Run integration tests
    print("[FINALIZE] Running integration tests...")
    try:
        test_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_integration_test.py"), "run", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        results["integration_tests"] = {
            "passed": test_result.returncode == 0,
            "output": test_result.stdout
        }
        if test_result.returncode == 0:
            print("[FINALIZE] ✅ Integration tests passed")
        else:
            print(f"[FINALIZE] ❌ Integration tests failed")
            results["success"] = False
    except Exception as e:
        print(f"[FINALIZE] Test error: {e}")
        results["integration_tests"] = {"passed": False, "error": str(e)}
    
    # 3. Harvest learnings from deposits
    print("[FINALIZE] Harvesting learnings...")
    try:
        harvest_result = subprocess.run(
            ["python3", str(SKILLS_DIR / "pulse_learnings.py"), "harvest", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        # Parse harvested count from output
        output = harvest_result.stdout
        if "Harvested" in output:
            try:
                count = int(output.split("Harvested")[1].split()[0])
                results["learnings_harvested"] = count
            except:
                pass
        print(f"[FINALIZE] Harvested learnings from deposits")
    except Exception as e:
        print(f"[FINALIZE] Harvest error: {e}")
    
    # 4. Save finalization results
    finalize_path = BUILDS_DIR / slug / "FINALIZATION.json"
    with open(finalize_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # 5. Sync drop statuses from deposits
    deposits_dir = BUILDS_DIR / slug / "deposits"
    if deposits_dir.exists():
        for deposit_file in deposits_dir.glob("*.json"):
            try:
                with open(deposit_file) as f:
                    deposit = json.load(f)
                drop_id = deposit.get("drop_id")
                deposit_status = deposit.get("status")
                if drop_id and drop_id in meta.get("drops", {}):
                    current = meta["drops"][drop_id].get("status")
                    # Only update if deposit says complete and meta doesn't
                    if deposit_status == "complete" and current != "complete":
                        meta["drops"][drop_id]["status"] = "complete"
                        meta["drops"][drop_id]["completed_at"] = deposit.get("timestamp", datetime.now(timezone.utc).isoformat())
                        # Clean up failure fields if present
                        meta["drops"][drop_id].pop("failure_reason", None)
                        meta["drops"][drop_id].pop("failed_at", None)
                        print(f"[FINALIZE] Synced {drop_id} → complete from deposit")
            except Exception as e:
                print(f"[FINALIZE] Warning: Could not read deposit {deposit_file.name}: {e}")
    
    # 6. Update meta status
    meta["finalized_at"] = datetime.now(timezone.utc).isoformat()
    meta["finalization_passed"] = results["success"]
    if results["success"]:
        meta["status"] = "finalized"
    save_meta(slug, meta)
    
    # 7. SMS summary
    if results["success"]:
        await send_sms(f"[PULSE] {slug} FINALIZED ✅ Artifacts verified, tests passed.")
    else:
        failures = []
        if not results.get("verification", {}).get("passed", True):
            failures.append("artifacts")
        if not results.get("integration_tests", {}).get("passed", True):
            failures.append("tests")
        await send_sms(f"[PULSE] {slug} FINALIZE ❌ Failed: {', '.join(failures)}. Review needed.")
    
    print(f"[FINALIZE] Complete. Success: {results['success']}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Pulse Build Orchestration")
    subparsers = parser.add_subparsers(dest="command")
    
    start_parser = subparsers.add_parser("start", help="Begin automated orchestration")
    start_parser.add_argument("slug", help="Build slug")
    
    status_parser = subparsers.add_parser("status", help="Show current build status")
    status_parser.add_argument("slug", help="Build slug")
    
    stop_parser = subparsers.add_parser("stop", help="Gracefully stop orchestration")
    stop_parser.add_argument("slug", help="Build slug")
    
    resume_parser = subparsers.add_parser("resume", help="Resume a stopped build")
    resume_parser.add_argument("slug", help="Build slug")
    
    tick_parser = subparsers.add_parser("tick", help="Run single orchestration cycle (for scheduled tasks)")
    tick_parser.add_argument("slug", help="Build slug")
    
    finalize_parser = subparsers.add_parser("finalize", help="Run post-build finalization (safety, tests, learnings)")
    finalize_parser.add_argument("slug", help="Build slug")
    
    launch_parser = subparsers.add_parser("launch", help="Print launcher path and paste-prompt contents")
    launch_parser.add_argument("slug", help="Build slug")
    launch_parser.add_argument("drop_id", help="Drop ID")
    
    retry_parser = subparsers.add_parser("retry", help="Reset a failed/bad Drop and re-edit its brief")
    retry_parser.add_argument("slug", help="Build slug")
    retry_parser.add_argument("drop_id", help="Drop ID to retry")
    retry_parser.add_argument("--reason", "-r", help="Why the retry is needed (appended to brief)")
    
    validate_parser = subparsers.add_parser("validate", help="Validate plan completeness before start")
    validate_parser.add_argument("slug", help="Build slug")
    
    args = parser.parse_args()
    
    if args.command == "start":
        asyncio.run(start_build(args.slug))
    elif args.command == "status":
        show_status(args.slug)
    elif args.command == "stop":
        stop_build(args.slug)
    elif args.command == "resume":
        resume_build(args.slug)
    elif args.command == "tick":
        asyncio.run(tick(args.slug))
    elif args.command == "finalize":
        asyncio.run(finalize_build(args.slug))
    elif args.command == "launch":
        launcher_path = ensure_launcher(args.slug, args.drop_id)
        print(f"Launcher: {launcher_path}")
        print(launcher_path.read_text())
    elif args.command == "retry":
        retry_drop(args.slug, args.drop_id, args.reason)
    elif args.command == "validate":
        validate_plan(args.slug)


if __name__ == "__main__":
    main()
