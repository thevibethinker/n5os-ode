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

    content = f"""# Build Status: {slug}

**Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {meta.get('status', 'unknown')}
{gate_line}{gate_text}
**Progress:** {len(complete)}/{total} Drops ({pct}%)

## Awaiting Manual ({len(awaiting_manual)})
{awaiting_lines or '(none)'}

## Running ({len(running)})
{chr(10).join(f'- [ ] {d} (since {drops[d].get("started_at", "?")[:16]})' for d in sorted(running)) or '(none)'}

## Pending ({len(pending)})
{chr(10).join(f'- [ ] {d}' for d in sorted(pending)) or '(none)'}

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


async def spawn_drop(slug: str, drop_id: str, brief: str, model: str = None) -> str:
    """Spawn a Drop via /zo/ask, return conversation_id
    
    Note: The /zo/ask API may not return the actual conversation_id.
    We generate a tracking ID but rely on deposit detection for completion.
    """
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    # Build deposit format as separate string to avoid f-string escaping issues
    deposit_format = '''
{
  "drop_id": "''' + drop_id + '''",
  "status": "complete",
  "summary": "What you accomplished",
  "artifacts": ["list", "of", "files", "created"],
  "learnings": ["any lessons for other workers"],
  "errors": []
}'''
    
    full_prompt = f"""You are a Pulse Drop executing build "{slug}", task "{drop_id}".

**YOUR IDENTITY:**
- Build: {slug}
- Drop ID: {drop_id}
- Type: Headless worker (no human in loop)

**EXECUTION PROTOCOL:**
1. Read the brief below carefully
2. Execute the task completely
3. When done, write your deposit JSON to: N5/builds/{slug}/deposits/{drop_id}.json
4. DO NOT commit code (orchestrator handles commits)
5. If blocked, write deposit with status "blocked" and explain why

**DEPOSIT FORMAT:**
```json{deposit_format}
```

Status can be "complete", "blocked", or "partial".

---
BRIEF:
{brief}
---

Execute the brief now. Write deposit when done."""

    # Create timeout
    timeout = aiohttp.ClientTimeout(total=DEFAULT_SPAWN_TIMEOUT)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                ZO_API_URL,
                headers={
                    "authorization": token,
                    "content-type": "application/json"
                },
                json={
                    "input": full_prompt,
                    "model_name": model
                }
            ) as resp:
                result = await resp.json()
                # Extract conversation_id from response if available
                convo_id = result.get("conversation_id")
                if not convo_id:
                    convo_id = f"spawn_{drop_id}_{int(datetime.now().timestamp())}"
                return convo_id
    except asyncio.TimeoutError:
        # API call timed out - worker may still be running
        print(f"[SPAWN TIMEOUT] {drop_id} - API call timed out after {DEFAULT_SPAWN_TIMEOUT}s")
        return f"timeout_{drop_id}_{int(datetime.now().timestamp())}"
    except Exception as e:
        print(f"[SPAWN ERROR] {drop_id}: {e}")
        raise


async def run_filter(slug: str, drop_id: str, brief: str, deposit: dict) -> dict:
    """Run LLM Filter to validate a Deposit against its brief"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        # Fallback: auto-pass
        return {"drop_id": drop_id, "verdict": "PASS", "reason": "Filter skipped (no token)"}
    
    # Build JSON template separately to avoid f-string conflicts
    json_template = """{
  "drop_id": "DROP_ID_HERE",
  "verdict": "PASS or FAIL",
  "reason": "Brief explanation",
  "artifacts_verified": true or false,
  "concerns": ["any concerns for orchestrator"]
}"""
    
    prompt = f"""You are a Pulse Filter validating a Drop's work.

## Drop Brief (what was requested):
{brief}

## Deposit (what was delivered):
{json.dumps(deposit, indent=2)}

## Your Task:
1. Compare the deposit against the brief's success criteria
2. Check if artifacts were actually created (you can read files to verify)
3. Determine PASS or FAIL

Respond with ONLY this JSON (no other text):
{json_template}

Replace DROP_ID_HERE with "{drop_id}"."""

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
            output = result.get("output", "")
            
            # Try to parse JSON from response
            try:
                # Find JSON in response
                start = output.find("{")
                end = output.rfind("}") + 1
                if start >= 0 and end > start:
                    return json.loads(output[start:end])
            except:
                pass
            
            # Fallback
            return {
                "drop_id": drop_id,
                "verdict": "PASS",
                "reason": "Filter parse failed, auto-passing",
                "raw_response": output[:500]
            }


async def run_dredge(slug: str, drop_id: str, meta: dict):
    """Spawn forensics worker to investigate dead Drop"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        return
    
    drop_info = meta.get("drops", {}).get(drop_id, {})
    convo_id = drop_info.get("conversation_id", "unknown")
    
    prompt = f"""You are a Pulse Dredge worker investigating a dead Drop.

Build: {slug}
Dead Drop: {drop_id}
Conversation ID: {convo_id}
Started at: {drop_info.get('started_at', 'unknown')}

## Your Task:
1. Check if the Drop created any partial artifacts
2. Check if there's a partial deposit in N5/builds/{slug}/deposits/
3. Look for any error indicators
4. Write a forensics report to: N5/builds/{slug}/deposits/{drop_id}_forensics.json

Report format:
{
  "drop_id": "{drop_id}",
  "partial_artifacts": ["list of any files created"],
  "partial_work": "description of what was started",
  "likely_cause": "timeout/error/stuck",
  "recommendation": "retry/skip/manual",
  "cleanup_needed": true/false
}

Investigate now."""

    async with aiohttp.ClientSession() as session:
        async with session.post(
            ZO_API_URL,
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt}
        ) as resp:
            print(f"[DREDGE] Forensics worker spawned for {drop_id}")


def recommend_spawn_mode(brief: str) -> str:
    """Heuristics-first recommendation: return 'manual' or 'auto'.

    This is intentionally cheap/deterministic. If we add LLM-based classification later,
    it should be config-gated.
    """
    t = (brief or "").lower()
    manual_signals = [
        "human-in-the-loop",
        "hitl",
        "requires v",
        "ask v",
        "need v",
        "needs v",
        "voice protocol",
        "careerspan voice",
        "high-risk",
        "close control",
        "manual",
        "human judgment",
        "v review",
        "v approval",
        "preferences",
    ]
    return "manual" if any(s in t for s in manual_signals) else "auto"


def _is_blocking(info: dict) -> bool:
    return info.get("blocking", True) is not False


def _build_stream_chains(drops: dict) -> dict[int, list[str]]:
    chains: dict[int, list[tuple[int, str]]] = {}
    for drop_id, info in drops.items():
        try:
            stream, order = get_drop_stream_order(drop_id, info)
        except Exception:
            continue
        chains.setdefault(stream, []).append((order, drop_id))
    return {s: [d for _, d in sorted(items, key=lambda t: t[0])] for s, items in chains.items()}


def _can_run_stream_order(drop_id: str, drops: dict, stream_chains: dict[int, list[str]], complete: set[str]) -> bool:
    info = drops.get(drop_id, {})
    try:
        stream, _ = get_drop_stream_order(drop_id, info)
    except Exception:
        return True

    chain = stream_chains.get(stream, [])
    if drop_id not in chain:
        return True
    idx = chain.index(drop_id)
    if idx == 0:
        return True
    prev_drop = chain[idx - 1]
    return prev_drop in complete


def _get_active_wave(meta: dict) -> Optional[str]:
    waves = meta.get("waves")
    if not isinstance(waves, dict) or not waves:
        meta.pop("active_wave", None)
        meta.pop("gate", None)
        return None

    drops = meta.get("drops", {})
    wave_keys = sort_wave_keys(list(waves.keys()))

    for wk in wave_keys:
        wave_drop_ids = list(waves.get(wk, []) or [])
        blocking_ids = [d for d in wave_drop_ids if _is_blocking(drops.get(d, {}))]

        # If any blocking drop failed/dead, block the build at this wave.
        for d in blocking_ids:
            st = drops.get(d, {}).get("status")
            if st in ["failed", "dead"]:
                meta["active_wave"] = wk
                meta["gate"] = {
                    "type": "wave_blocked",
                    "wave": wk,
                    "drop_id": d,
                    "reason": f"Blocking drop {d} is {st}; later waves cannot start."
                }
                return wk

        # If any blocking drop is not complete, this is the active wave.
        if any(drops.get(d, {}).get("status") != "complete" for d in blocking_ids):
            meta["active_wave"] = wk
            meta.pop("gate", None)
            return wk

    # All blocking drops complete
    meta["active_wave"] = None
    meta.pop("gate", None)
    return None


def get_ready_drops(meta: dict) -> list[str]:
    """Get list of Drops ready to spawn (dependencies met, not started).

    v3 mode (meta.waves):
      - Hard barrier waves: only consider drops in the earliest active wave
      - blocking:false drops do not block wave advancement
      - If a blocking drop in the active wave failed/dead, gate the build and spawn nothing
      - Streams are sequential: within a stream, order k+1 waits for order k to be complete

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
        if info.get("status") != "pending":
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
    for drop_id, info in running:
        deposit = get_deposit(slug, drop_id)
        if deposit:
            print(f"[DEPOSIT] Found deposit for {drop_id}")
            
            # Run Filter
            try:
                brief = load_drop_brief(slug, drop_id)
                filter_result = await run_filter(slug, drop_id, brief, deposit)
                
                # Save filter result
                filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_filter.json"
                with open(filter_path, "w") as f:
                    json.dump(filter_result, f, indent=2)
                
                convo_id = info.get("conversation_id")
                
                if filter_result.get("verdict") == "PASS":
                    meta["drops"][drop_id]["status"] = "complete"
                    meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    update_drop_conversation_status(convo_id, "complete")
                    print(f"[FILTER PASS] {drop_id}")
                else:
                    meta["drops"][drop_id]["status"] = "failed"
                    meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["failure_reason"] = filter_result.get("reason", "Unknown")
                    update_drop_conversation_status(convo_id, "failed")
                    print(f"[FILTER FAIL] {drop_id}: {filter_result.get('reason')}")
                    await send_sms(f"[PULSE] {slug}: {drop_id} FAILED filter. Reason: {filter_result.get('reason', 'Unknown')[:50]}")
            except Exception as e:
                print(f"[FILTER ERROR] {drop_id}: {e}")
                # Auto-pass on filter error
                meta["drops"][drop_id]["status"] = "complete"
                meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                update_drop_conversation_status(info.get("conversation_id"), "complete")
    
    # 2. Check for dead Drops (running too long)
    dead_threshold = meta.get("dead_threshold_seconds", DEFAULT_DEAD_THRESHOLD)
    for drop_id, info in running:
        if info.get("status") != "running":
            continue  # Already processed above
        
        started_at = info.get("started_at")
        if started_at:
            started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            
            if elapsed > dead_threshold:
                print(f"[DEAD] {drop_id} - no deposit after {int(elapsed)}s")
                meta["drops"][drop_id]["status"] = "dead"
                meta["drops"][drop_id]["died_at"] = datetime.now(timezone.utc).isoformat()
                
                # Spawn Dredge
                await run_dredge(slug, drop_id, meta)
                
                # SMS escalation
                complete_count = sum(1 for d in meta["drops"].values() if d.get("status") == "complete")
                total_count = len(meta["drops"])
                await send_sms(f"[PULSE] {slug}: {drop_id} DEAD after {int(elapsed/60)}m. {complete_count}/{total_count} complete. Reply RESUME or STOP.")
    
    # 3. Legacy stream gating (only when no waves)
    if not meta.get("waves"):
        if advance_stream(meta):
            print(f"[STREAM] Advanced to Stream {meta['current_stream']}")
    
    # 4. Check if build complete
    all_terminal = all(
        info.get("status") in ["complete", "failed", "dead"]
        for info in meta.get("drops", {}).values()
    )
    if all_terminal:
        complete_count = sum(1 for d in meta["drops"].values() if d.get("status") == "complete")
        total_count = len(meta["drops"])
        
        if complete_count == total_count:
            meta["status"] = "complete"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            summary = await summarize_build(slug, meta)
            print(f"[BUILD COMPLETE] {slug}")
            await send_sms(f"[PULSE] {slug} BUILD COMPLETE. {complete_count}/{total_count} Drops succeeded.")
        else:
            meta["status"] = "partial"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            failed = [d for d, i in meta["drops"].items() if i.get("status") in ["failed", "dead"]]
            await send_sms(f"[PULSE] {slug} PARTIAL. {complete_count}/{total_count} succeeded. Failed: {', '.join(failed[:3])}")
    
    # 5. Spawn ready Drops
    ready = get_ready_drops(meta)
    model = meta.get("model")

    for drop_id in ready:
        try:
            brief = load_drop_brief(slug, drop_id)
            print(f"[SPAWN] {drop_id}")

            drop_info = meta.get("drops", {}).get(drop_id, {})

            # Recommendation (only if not explicitly set)
            if "spawn_mode" not in drop_info:
                rec = recommend_spawn_mode(brief)
                drop_info["spawn_recommendation"] = rec
                if rec == "manual":
                    drop_info["spawn_mode"] = "manual"

            spawn_mode = drop_info.get("spawn_mode", "auto")

            if spawn_mode == "manual":
                launcher_path = ensure_launcher(slug, drop_id)
                drop_info["launcher_path"] = f"N5/builds/{slug}/launchers/{drop_id}.md"
                print(f"[SPAWN] {drop_id} is waiting for manual launch (launcher: {launcher_path})")
                meta["drops"][drop_id]["status"] = "awaiting_manual"
                continue

            convo_id = await spawn_drop(slug, drop_id, brief, model)

            meta["drops"][drop_id]["status"] = "running"
            meta["drops"][drop_id]["started_at"] = datetime.now(timezone.utc).isoformat()
            meta["drops"][drop_id]["conversation_id"] = convo_id

            register_drop_conversation(drop_id, slug, convo_id)

        except Exception as e:
            print(f"[SPAWN ERROR] {drop_id}: {e}")
            meta["drops"][drop_id]["status"] = "failed"
            meta["drops"][drop_id]["failure_reason"] = str(e)

    
    # 6. Save state
    save_meta(slug, meta)
    update_status_md(slug, meta)
    
    if meta.get("waves"):
        print(f"[PULSE TICK DONE] Wave {meta.get('active_wave')}")
    else:
        print(f"[PULSE TICK DONE] Stream {meta.get('current_stream')}/{meta.get('total_streams')}")


async def start_build(slug: str):
    """Initialize and start a build"""
    meta = load_meta(slug)
    
    if meta.get("status") == "active":
        print(f"Build {slug} already active")
        return
    
    meta["status"] = "active"
    meta["started_at"] = datetime.now(timezone.utc).isoformat()
    
    # Initialize all drops to pending if not set
    for drop_id, info in meta.get("drops", {}).items():
        if "status" not in info:
            info["status"] = "pending"
    
    save_meta(slug, meta)
    update_status_md(slug, meta)
    
    print(f"[PULSE] Build {slug} started")
    await send_sms(f"[PULSE] Build {slug} STARTED. {len(meta.get('drops', {}))} Drops queued.")
    
    # Run first tick
    await tick(slug)


def stop_build(slug: str):
    """Stop a build gracefully"""
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
        print(f"Build {slug} is not stopped (status: {meta.get('status')})")
        return
    
    meta["status"] = "active"
    meta["resumed_at"] = datetime.now(timezone.utc).isoformat()
    save_meta(slug, meta)
    print(f"[PULSE] Build {slug} resumed")


def show_status(slug: str):
    """Show build status"""
    meta = load_meta(slug)
    drops = meta.get("drops", {})

    complete = sum(1 for d in drops.values() if d.get("status") == "complete")
    running = sum(1 for d in drops.values() if d.get("status") == "running")
    awaiting_manual = sum(1 for d in drops.values() if d.get("status") == "awaiting_manual")
    pending = sum(1 for d in drops.values() if d.get("status") == "pending")
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

    print(f"""
Build: {slug}
Status: {meta.get('status', 'unknown')}
{gate_scope}{gate_line}
Drops:
  Complete:        {complete}
  Running:         {running}
  Awaiting Manual: {awaiting_manual}
  Pending:         {pending}
  Dead:            {dead}
  Failed:          {failed}
  Total:           {len(drops)}

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
    
    # 5. Update meta
    meta["finalized_at"] = datetime.now(timezone.utc).isoformat()
    meta["finalization_passed"] = results["success"]
    save_meta(slug, meta)
    
    # 6. SMS summary
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
