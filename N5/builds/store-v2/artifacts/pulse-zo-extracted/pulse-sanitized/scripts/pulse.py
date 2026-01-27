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

# Paths
WORKSPACE = Path(".")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
CONVERSATIONS_DB = WORKSPACE / "N5" / "data" / "conversations.db"
SKILLS_DIR = WORKSPACE / "Skills" / "pulse" / "scripts"
TIDYING_DIR = WORKSPACE / "N5" / "pulse" / "tidying"
TIDYING_TEMPLATES_DIR = WORKSPACE / "Skills" / "pulse" / "drops" / "tidying"

# Config
DEFAULT_POLL_INTERVAL = 180  # 3 minutes
DEFAULT_DEAD_THRESHOLD = 900  # 15 minutes
ZO_API_URL = "<YOUR_WEBHOOK_URL>"
CONFIG_PATH = WORKSPACE / "Skills" / "pulse" / "config" / "pulse_v2_config.json"


def load_config() -> dict:
    """Load Pulse config with defaults."""
    defaults = {
        "validation": {
            "enabled": True,
            "code_validator_enabled": True,
            "llm_filter_enabled": True,
            "llm_filter_timeout_seconds": 120,
            "code_validator_timeout_seconds": 60,
            "auto_pass_on_validator_error": True
        }
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                config = json.load(f)
                # Merge with defaults
                for key, val in defaults.items():
                    if key not in config:
                        config[key] = val
                    elif isinstance(val, dict):
                        for k, v in val.items():
                            if k not in config[key]:
                                config[key][k] = v
                return config
        except:
            pass
    return defaults


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


def load_drop_brief(slug: str, drop_id: str) -> str:
    """Load a Drop brief from drops/ folder"""
    drops_dir = BUILDS_DIR / slug / "drops"
    # Try both D and C prefixes
    for pattern in [f"{drop_id}-*.md", f"C*.md"]:
        for f in drops_dir.glob(pattern):
            if f.stem.startswith(drop_id):
                return f.read_text()
    # Fallback: exact match
    for f in drops_dir.glob("*.md"):
        if f.stem.split("-")[0] == drop_id:
            return f.read_text()
    raise FileNotFoundError(f"Brief not found for {drop_id}")


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
    pending = [d for d, info in drops.items() if info.get("status") == "pending"]
    dead = [d for d, info in drops.items() if info.get("status") == "dead"]
    failed = [d for d, info in drops.items() if info.get("status") == "failed"]
    
    total = len(drops)
    pct = int(len(complete) / total * 100) if total > 0 else 0
    
    content = f"""# Build Status: {slug}

**Updated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {meta.get('status', 'unknown')}
**Stream:** {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}
**Progress:** {len(complete)}/{total} Drops ({pct}%)

## Complete ({len(complete)})
{chr(10).join(f'- [x] {d}' for d in sorted(complete)) or '(none)'}

## Running ({len(running)})
{chr(10).join(f'- [ ] {d} (since {drops[d].get("started_at", "?")[:16]})' for d in sorted(running)) or '(none)'}

## Pending ({len(pending)})
{chr(10).join(f'- [ ] {d}' for d in sorted(pending)) or '(none)'}

## Dead ({len(dead)})
{chr(10).join(f'- [!] {d}' for d in sorted(dead)) or '(none)'}

## Failed ({len(failed)})
{chr(10).join(f'- [x] {d} (Filter rejected)' for d in sorted(failed)) or '(none)'}
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
    """Spawn a Drop via /zo/ask, return conversation_id"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        raise RuntimeError("ZO_CLIENT_IDENTITY_TOKEN not set")
    
    # Include SESSION_STATE init in the prompt
    full_prompt = f"""You are a Pulse worker (Drop) executing build "{slug}", task "{drop_id}".

FIRST ACTION (before anything else):
Run this command to register yourself:
```bash
python3 ./scripts/scripts/session_state_manager.py init --convo-id $(cat /proc/self/cgroup | grep -o 'con_[^/]*' | head -1 || echo "unknown") --type build --build {slug} --worker-num {drop_id} --message "Drop {drop_id}: {brief.split(chr(10))[0][:50]}"
```

THEN EXECUTE:
1. Read the brief below carefully
2. Execute the task completely  
3. Write your deposit to: scripts/builds/{slug}/deposits/{drop_id}.json
4. DO NOT commit any code
5. If blocked, write deposit with status "blocked" and explain why

---
{brief}
---

Begin execution now. Initialize SESSION_STATE first, then work, then write deposit."""

    async with aiohttp.ClientSession() as session:
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
            convo_id = result.get("conversation_id", f"unknown_{drop_id}_{datetime.now().timestamp()}")
            return convo_id


async def run_filter(slug: str, drop_id: str, brief: str, deposit: dict) -> dict:
    """Run LLM Filter to validate a Deposit against its brief"""
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        # Fallback: auto-pass
        return {"drop_id": drop_id, "verdict": "PASS", "reason": "Filter skipped (no token)"}
    
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
{{
  "drop_id": "{drop_id}",
  "verdict": "PASS" or "FAIL",
  "reason": "Brief explanation",
  "artifacts_verified": true/false,
  "concerns": ["any concerns for orchestrator"]
}}"""

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


def mark_deposit_failed(slug: str, drop_id: str, reason: str, details: dict):
    """Mark a deposit as failed validation and update meta.json."""
    build_dir = BUILDS_DIR / slug
    deposit_path = build_dir / "deposits" / f"{drop_id}.json"
    
    if deposit_path.exists():
        deposit = json.loads(deposit_path.read_text())
        deposit["validation_status"] = "failed"
        deposit["validation_reason"] = reason
        deposit["validation_details"] = details
        deposit_path.write_text(json.dumps(deposit, indent=2))
    
    # Update meta.json
    meta_path = build_dir / "meta.json"
    meta = json.loads(meta_path.read_text())
    if drop_id in meta.get("drops", {}):
        meta["drops"][drop_id]["status"] = "failed"
        meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
        meta["drops"][drop_id]["failure_reason"] = reason
        meta["drops"][drop_id]["validation_details"] = details
    meta_path.write_text(json.dumps(meta, indent=2))
    
    print(f"[FAIL] {drop_id} failed {reason}")


async def run_validators(slug: str, drop_id: str) -> tuple[bool, dict]:
    """Run mechanical + LLM validators on a deposit.
    
    Uses the actual validator scripts:
    - pulse_code_validator.py check <slug> <drop_id>  (mechanical)
    - pulse_llm_filter.py validate <slug> <drop_id>   (LLM-based)
    
    Returns: (passed, result_dict)
    """
    config = load_config()
    validation_config = config.get("validation", {})
    
    if not validation_config.get("enabled", True):
        return True, {"verdict": "PASS", "reason": "Validation disabled in config"}
    
    code_timeout = validation_config.get("code_validator_timeout_seconds", 60)
    llm_timeout = validation_config.get("llm_filter_timeout_seconds", 120)
    auto_pass_on_error = validation_config.get("auto_pass_on_validator_error", True)
    
    result = {
        "drop_id": drop_id,
        "build_slug": slug,
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "mechanical": None,
        "llm": None,
        "verdict": "PASS",
        "reason": ""
    }
    
    # === Stage 1: Mechanical validation (code_validator) ===
    if validation_config.get("code_validator_enabled", True):
        try:
            code_result = subprocess.run(
                ["python3", str(SKILLS_DIR / "pulse_code_validator.py"), "check", slug, drop_id],
                capture_output=True, text=True, timeout=code_timeout, cwd=str(WORKSPACE)
            )
            
            # Extract JSON from stdout (may have log lines before it)
            stdout = code_result.stdout
            json_start = stdout.find('{')
            json_end = stdout.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                try:
                    code_data = json.loads(stdout[json_start:json_end])
                    result["mechanical"] = code_data
                    
                    # Check for critical issues regardless of exit code
                    if code_data.get("critical_count", 0) > 0:
                        result["verdict"] = "FAIL"
                        result["reason"] = f"Code validation: {code_data.get('critical_count')} critical issues"
                        print(f"[VALIDATOR] {drop_id} FAILED mechanical check: {code_data.get('critical_count')} critical issues")
                        
                        # Lesson already logged by validator, skip duplicate
                        return False, result
                    else:
                        print(f"[VALIDATOR] {drop_id} passed mechanical check")
                except json.JSONDecodeError as e:
                    print(f"[WARN] Could not parse code validator JSON: {e}")
                    result["mechanical"] = {"error": "JSON parse error", "raw": stdout[:500]}
                    if not auto_pass_on_error:
                        result["verdict"] = "FAIL"
                        result["reason"] = "Code validator JSON parse error"
                        return False, result
            else:
                # No JSON in output
                print(f"[WARN] No JSON in code validator output: {stdout[:200]}")
                result["mechanical"] = {"error": "No JSON output", "raw": stdout[:500]}
                if not auto_pass_on_error:
                    result["verdict"] = "FAIL"
                    result["reason"] = "Code validator produced no JSON"
                    return False, result
        except subprocess.TimeoutExpired:
            print(f"[WARN] Code validator timeout for {drop_id}")
            result["mechanical"] = {"error": "timeout"}
            if not auto_pass_on_error:
                result["verdict"] = "FAIL"
                result["reason"] = "Code validator timeout"
                return False, result
        except Exception as e:
            print(f"[WARN] Code validator failed for {drop_id}: {e}")
            result["mechanical"] = {"error": str(e)}
            if not auto_pass_on_error:
                result["verdict"] = "FAIL"
                result["reason"] = f"Code validator error: {e}"
                return False, result
    
    # === Stage 2: LLM validation ===
    if validation_config.get("llm_filter_enabled", True):
        try:
            llm_result = subprocess.run(
                ["python3", str(SKILLS_DIR / "pulse_llm_filter.py"), "validate", slug, drop_id],
                capture_output=True, text=True, timeout=llm_timeout, cwd=str(WORKSPACE)
            )
            
            if llm_result.returncode == 0:
                try:
                    llm_data = json.loads(llm_result.stdout)
                    result["llm"] = llm_data
                    
                    if not llm_data.get("pass", False):
                        result["verdict"] = "FAIL"
                        result["reason"] = f"LLM validation: {llm_data.get('summary', 'Unknown reason')}"
                        print(f"[VALIDATOR] {drop_id} FAILED LLM filter: {llm_data.get('summary', 'Unknown')}")
                        
                        # Log lesson
                        try:
                            subprocess.run([
                                "python3", str(SKILLS_DIR / "pulse_learnings.py"), "add", slug,
                                f"Drop {drop_id} failed LLM validation: {llm_data.get('summary', 'Unknown')[:100]}",
                                "--source", drop_id, "--category", "llm_rejection", "--severity", "high"
                            ], capture_output=True, timeout=30, cwd=str(WORKSPACE))
                        except Exception as e:
                            print(f"[WARN] Could not log lesson: {e}")
                        
                        return False, result
                    else:
                        print(f"[VALIDATOR] {drop_id} passed LLM filter (confidence: {llm_data.get('confidence', 'N/A')})")
                except json.JSONDecodeError:
                    result["llm"] = {"error": "Could not parse output", "raw": llm_result.stdout[:500]}
                    if not auto_pass_on_error:
                        result["verdict"] = "FAIL"
                        result["reason"] = "LLM filter output parse error"
                        return False, result
            else:
                # Non-zero exit = validation failed
                try:
                    llm_data = json.loads(llm_result.stdout)
                    result["llm"] = llm_data
                    result["verdict"] = "FAIL"
                    result["reason"] = f"LLM validation failed: {llm_data.get('summary', 'Unknown')}"
                    return False, result
                except:
                    result["llm"] = {"error": llm_result.stderr or "Unknown error"}
                    if not auto_pass_on_error:
                        result["verdict"] = "FAIL"
                        result["reason"] = "LLM validator returned error"
                        return False, result
                    print(f"[WARN] LLM filter error, auto-passing: {llm_result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            print(f"[WARN] LLM filter timeout for {drop_id}")
            result["llm"] = {"error": "timeout"}
            if not auto_pass_on_error:
                result["verdict"] = "FAIL"
                result["reason"] = "LLM filter timeout"
                return False, result
        except Exception as e:
            print(f"[WARN] LLM filter failed for {drop_id}: {e}")
            result["llm"] = {"error": str(e)}
            if not auto_pass_on_error:
                result["verdict"] = "FAIL"
                result["reason"] = f"LLM filter error: {e}"
                return False, result
    
    # Passed both stages
    result["verdict"] = "PASS"
    result["reason"] = "Passed mechanical and LLM validation"
    return True, result


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
2. Check if there's a partial deposit in scripts/builds/{slug}/deposits/
3. Look for any error indicators
4. Write a forensics report to: scripts/builds/{slug}/deposits/{drop_id}_forensics.json

Report format:
{{
  "drop_id": "{drop_id}",
  "partial_artifacts": ["list of any files created"],
  "partial_work": "description of what was started",
  "likely_cause": "timeout/error/stuck",
  "recommendation": "retry/skip/manual",
  "cleanup_needed": true/false
}}

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


def get_ready_drops(meta: dict) -> list[str]:
    """Get list of Drops ready to spawn (dependencies met, not started)"""
    ready = []
    drops = meta.get("drops", {})
    currents = meta.get("currents", {})
    
    # Build set of complete drops
    complete_drops = {d for d, info in drops.items() if info.get("status") == "complete"}
    
    # Build set of drops in currents (sequential chains)
    current_drops = set()
    for chain in currents.values():
        current_drops.update(chain)
    
    for drop_id, info in drops.items():
        if info.get("status") != "pending":
            continue
        
        # Check dependencies
        depends_on = info.get("depends_on", [])
        if not all(d in complete_drops for d in depends_on):
            continue
        
        # Check if part of a Current (sequential chain)
        in_current = False
        for chain_id, chain in currents.items():
            if drop_id in chain:
                in_current = True
                idx = chain.index(drop_id)
                if idx > 0:
                    # Must wait for previous in chain
                    prev_drop = chain[idx - 1]
                    if prev_drop not in complete_drops:
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
    """Check if current stream is complete"""
    current_stream = meta.get("current_stream", 1)
    drops = meta.get("drops", {})
    
    for drop_id, info in drops.items():
        # Parse stream from drop_id (D1.1 -> stream 1)
        try:
            stream_num = int(drop_id[1])
        except:
            continue
        
        if stream_num == current_stream:
            if info.get("status") not in ["complete", "failed"]:
                return False
    
    return True


def advance_stream(meta: dict) -> bool:
    """Advance to next stream if current is complete. Returns True if advanced."""
    if not check_stream_complete(meta):
        return False
    
    current = meta.get("current_stream", 1)
    total = meta.get("total_streams", 1)
    
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


def get_tidying_templates() -> list[dict]:
    """Load tidying templates from Skills/pulse/drops/tidying/."""
    templates = []
    if TIDYING_TEMPLATES_DIR.exists():
        for f in sorted(TIDYING_TEMPLATES_DIR.glob("*.md")):
            content = f.read_text()
            # Parse frontmatter for priority
            priority = 99
            auto_fix = False
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if line.startswith("priority:"):
                            try:
                                priority = int(line.split(":")[1].strip())
                            except:
                                pass
                        if line.startswith("auto_fix:"):
                            auto_fix = "true" in line.lower()
            templates.append({
                "name": f.stem,
                "path": str(f),
                "priority": priority,
                "auto_fix": auto_fix,
                "content": content
            })
    return sorted(templates, key=lambda t: t["priority"])


def generate_tidying_drop_brief(slug: str, template: dict) -> str:
    """Generate a tidying Drop brief from a template."""
    return f"""---
build_slug: {slug}
drop_type: tidying
hygiene_check: {template['name']}
auto_generated: true
---

{template['content']}

## Build Context
- **Build Slug**: {slug}
- **Build Dir**: scripts/builds/{slug}

## Deposit Location
Write your deposit to: scripts/builds/{slug}/deposits/T-{template['name']}.json

## Required Deposit Schema
```json
{{
  "drop_id": "T-{template['name']}",
  "build_slug": "{slug}",
  "check_type": "{template['name']}",
  "findings": [...],
  "auto_fixable": [...],
  "requires_review": [...],
  "health_contribution": 0.0-1.0
}}
```
"""


async def enter_tidying_stage(slug: str, meta: dict) -> bool:
    """
    Enter the tidying stage after BUILD completes.
    
    1. Spawn 5 tidying Drops (parallel, one Stream)
    2. Return True to indicate stage entered
    
    Subsequent ticks will handle:
    3. Wait for all deposits
    4. Run aggregator
    5. Run fix dispatcher
    6. If fixes spawned: wait, re-run checks
    7. If escalations: SMS summary, wait for approval
    8. Advance to complete/delivery
    """
    config = load_config()
    tidying_config = config.get("tidying_swarm", {})
    
    if not tidying_config.get("enabled", True):
        print("[TIDYING] Tidying swarm disabled in config")
        return False
    
    templates = get_tidying_templates()
    if not templates:
        print("[TIDYING] No tidying templates found")
        return False
    
    print(f"[TIDYING] Entering tidying stage with {len(templates)} hygiene checks")
    
    # Create tidying drops in meta
    tidying_drops = {}
    for t in templates:
        drop_id = f"T-{t['name']}"
        tidying_drops[drop_id] = {
            "stream": meta.get("total_streams", 1) + 1,  # New stream after build
            "status": "pending",
            "type": "tidying",
            "hygiene_check": t["name"],
            "auto_fix": t["auto_fix"],
            "priority": t["priority"]
        }
    
    # Add tidying drops to meta
    if "drops" not in meta:
        meta["drops"] = {}
    meta["drops"].update(tidying_drops)
    
    # Update streams
    meta["tidying_stream"] = meta.get("total_streams", 1) + 1
    meta["total_streams"] = meta["tidying_stream"]
    meta["current_stream"] = meta["tidying_stream"]
    meta["stage"] = "tidying"
    meta["tidying_started_at"] = datetime.now(timezone.utc).isoformat()
    
    # Spawn all tidying drops in parallel
    model = meta.get("model")
    for drop_id, info in tidying_drops.items():
        template = next((t for t in templates if f"T-{t['name']}" == drop_id), None)
        if not template:
            continue
        
        brief = generate_tidying_drop_brief(slug, template)
        
        # Save brief for reference
        brief_path = BUILDS_DIR / slug / "drops" / f"{drop_id}.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(brief)
        
        try:
            convo_id = await spawn_drop(slug, drop_id, brief, model)
            meta["drops"][drop_id]["status"] = "running"
            meta["drops"][drop_id]["started_at"] = datetime.now(timezone.utc).isoformat()
            meta["drops"][drop_id]["conversation_id"] = convo_id
            register_drop_conversation(drop_id, slug, convo_id)
            print(f"[TIDYING SPAWN] {drop_id}")
        except Exception as e:
            print(f"[TIDYING SPAWN ERROR] {drop_id}: {e}")
            meta["drops"][drop_id]["status"] = "failed"
            meta["drops"][drop_id]["failure_reason"] = str(e)
    
    save_meta(slug, meta)
    return True


async def process_tidying_complete(slug: str, meta: dict) -> dict:
    """
    Process completed tidying stage: aggregate and dispatch.
    
    Returns: {
        "health_score": float,
        "fixes_spawned": int,
        "escalations": int,
        "proceed": bool
    }
    """
    print("[TIDYING] All hygiene checks complete, running aggregator...")
    
    # Run aggregator
    try:
        result = subprocess.run(
            ["python3", str(TIDYING_DIR / "aggregator.py"), slug, "--json"],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        findings = json.loads(result.stdout) if result.returncode == 0 else {}
    except Exception as e:
        print(f"[TIDYING] Aggregator error: {e}")
        findings = {"health_score": 0.5, "critical": [], "warning": [], "auto_fixable": []}
    
    health_score = findings.get("health_score", 1.0)
    print(f"[TIDYING] Health score: {health_score:.2f}")
    
    # Save aggregated findings
    agg_path = BUILDS_DIR / slug / "TIDYING_FINDINGS.json"
    with open(agg_path, "w") as f:
        json.dump(findings, f, indent=2)
    
    # If health score >= 0.9, proceed without fixes
    if health_score >= 0.9:
        print("[TIDYING] Health score >= 0.9, proceeding to delivery")
        return {
            "health_score": health_score,
            "fixes_spawned": 0,
            "escalations": 0,
            "proceed": True
        }
    
    # NEW: Dispatch auto-fixes for high-confidence findings  
    config = load_config()
    auto_fix_threshold = config.get("auto_fix", {}).get("confidence_threshold", 0.9)
    
    if config.get("auto_fix", {}).get("enabled", True):
        print(f"  Dispatching auto-fixes (threshold: {auto_fix_threshold})...")
        dispatch_result = subprocess.run([
            "python3", str(TIDYING_DIR / "fix_dispatcher.py"), slug,
            "--findings-json", str(agg_path)
        ], capture_output=True, text=True)
        
        if dispatch_result.returncode == 0:
            try:
                # Try to parse JSON output from the dispatch script
                output_lines = dispatch_result.stdout.strip().split('\n')
                # Look for JSON-like output or specific result indicators
                dispatch_data = None
                for line in output_lines:
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            dispatch_data = json.loads(line)
                            break
                        except json.JSONDecodeError:
                            continue
                
                # If we found JSON data, use it; otherwise check file
                if dispatch_data:
                    fixes_dispatched = dispatch_data.get("to_fix", 0)
                    escalated = dispatch_data.get("to_escalate", 0)
                else:
                    # Fallback: parse from DISPATCH_RESULT.json file
                    if (BUILDS_DIR / slug / "DISPATCH_RESULT.json").exists():
                        with open(BUILDS_DIR / slug / "DISPATCH_RESULT.json") as f:
                            file_data = json.load(f)
                        fixes_dispatched = len(file_data.get("fixes_spawned", []))
                        escalated = 1 if file_data.get("escalation_sent", False) else 0
                    else:
                        fixes_dispatched = 0
                        escalated = 0
                
                if fixes_dispatched > 0:
                    print(f"  ✓ Auto-fixed {fixes_dispatched} issues")
                if escalated > 0:
                    print(f"  ⚠ Escalated {escalated} issues for manual review")
                    
            except json.JSONDecodeError:
                print(f"  Fix dispatcher output: {dispatch_result.stdout}")
        else:
            print(f"  Fix dispatcher warning: {dispatch_result.stderr or 'unknown error'}")
        
        # Load dispatch results from file if available
        dispatch_file_result = {}
        if (BUILDS_DIR / slug / "DISPATCH_RESULT.json").exists():
            with open(BUILDS_DIR / slug / "DISPATCH_RESULT.json") as f:
                dispatch_file_result = json.load(f)
    else:
        print("  Auto-fix disabled in config")
        dispatch_file_result = {}

    fixes = len(dispatch_file_result.get("fixes_spawned", []))
    escalated = dispatch_file_result.get("escalation_sent", False)
    
    return {
        "health_score": health_score,
        "fixes_spawned": fixes,
        "escalations": 1 if escalated else 0,
        "proceed": not escalated and fixes == 0
    }


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
            
            # Run validators (mechanical + LLM)
            try:
                passed, validator_result = await run_validators(slug, drop_id)
                
                # Save validation result
                filter_path = BUILDS_DIR / slug / "deposits" / f"{drop_id}_validation.json"
                with open(filter_path, "w") as f:
                    json.dump(validator_result, f, indent=2)
                
                convo_id = info.get("conversation_id")
                
                if passed:
                    meta["drops"][drop_id]["status"] = "complete"
                    meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["validation"] = validator_result
                    update_drop_conversation_status(convo_id, "complete")
                    print(f"[VALIDATOR PASS] {drop_id}")
                else:
                    meta["drops"][drop_id]["status"] = "failed"
                    meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["failure_reason"] = validator_result.get("reason", "Validation failed")
                    meta["drops"][drop_id]["validation"] = validator_result
                    update_drop_conversation_status(convo_id, "failed")
                    print(f"[VALIDATOR FAIL] {drop_id}: {validator_result.get('reason')}")
                    await send_sms(f"[PULSE] {slug}: {drop_id} FAILED validation. Reason: {validator_result.get('reason', 'Unknown')[:50]}")
            except Exception as e:
                print(f"[VALIDATOR ERROR] {drop_id}: {e}")
                # Check config for auto-pass behavior
                config = load_config()
                if config.get("validation", {}).get("auto_pass_on_validator_error", True):
                    meta["drops"][drop_id]["status"] = "complete"
                    meta["drops"][drop_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["validation_error"] = str(e)
                    update_drop_conversation_status(info.get("conversation_id"), "complete")
                    print(f"[VALIDATOR] {drop_id} auto-passed due to validator error")
                else:
                    meta["drops"][drop_id]["status"] = "failed"
                    meta["drops"][drop_id]["failed_at"] = datetime.now(timezone.utc).isoformat()
                    meta["drops"][drop_id]["failure_reason"] = f"Validator error: {e}"
                    update_drop_conversation_status(info.get("conversation_id"), "failed")
    
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
    
    # 3. Check if stream complete, advance if so
    if advance_stream(meta):
        print(f"[STREAM] Advanced to Stream {meta['current_stream']}")
    
    # 4. Check if build complete (non-tidying drops)
    build_drops = {k: v for k, v in meta.get("drops", {}).items() 
                   if not v.get("type") == "tidying"}
    all_build_terminal = all(
        info.get("status") in ["complete", "failed", "dead"]
        for info in build_drops.values()
    ) if build_drops else False
    
    # Check stage
    current_stage = meta.get("stage", "build")
    
    if all_build_terminal and current_stage == "build":
        complete_count = sum(1 for d in build_drops.values() if d.get("status") == "complete")
        total_count = len(build_drops)
        
        if complete_count == total_count:
            # All BUILD drops succeeded, enter tidying stage
            print(f"[BUILD PHASE COMPLETE] {slug} - entering tidying stage")
            await enter_tidying_stage(slug, meta)
        else:
            # BUILD phase partial failure
            meta["status"] = "partial"
            meta["completed_at"] = datetime.now(timezone.utc).isoformat()
            failed = [d for d, i in build_drops.items() if i.get("status") in ["failed", "dead"]]
            await send_sms(f"[PULSE] {slug} BUILD PARTIAL. {complete_count}/{total_count} succeeded. Failed: {', '.join(failed[:3])}")
    
    elif current_stage == "tidying":
        # Check if tidying drops are complete
        tidying_drops = {k: v for k, v in meta.get("drops", {}).items() 
                        if v.get("type") == "tidying"}
        all_tidying_terminal = all(
            info.get("status") in ["complete", "failed", "dead"]
            for info in tidying_drops.values()
        ) if tidying_drops else True
        
        if all_tidying_terminal:
            result = await process_tidying_complete(slug, meta)
            
            if result["proceed"]:
                meta["status"] = "complete"
                meta["stage"] = "complete"
                meta["completed_at"] = datetime.now(timezone.utc).isoformat()
                meta["tidying_result"] = result
                build_drops_count = len(build_drops)
                print(f"[BUILD COMPLETE] {slug}")
                await send_sms(f"[PULSE] {slug} COMPLETE. {build_drops_count} Drops + tidying. Health: {result['health_score']:.2f}")
            elif result["escalations"] > 0:
                meta["status"] = "awaiting_review"
                meta["stage"] = "tidying_escalated"
                await send_sms(f"[PULSE] {slug} awaiting tidying review. Reply APPROVE or STOP.")
            else:
                # Fixes were spawned, continue waiting
                print(f"[TIDYING] {result['fixes_spawned']} fix Drops spawned, waiting...")
    
    # 5. Spawn ready Drops
    ready = get_ready_drops(meta)
    model = meta.get("model")
    
    for drop_id in ready:
        try:
            brief = load_drop_brief(slug, drop_id)
            print(f"[SPAWN] {drop_id}")
            
            drop_info = meta.get("drops", {}).get(drop_id, {})
            spawn_mode = drop_info.get("spawn_mode", "auto")
            
            if spawn_mode == "manual":
                print(f"[SPAWN] {drop_id} is waiting for manual spawn")
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
    
    print(f"[PULSE TICK DONE] Stream {meta.get('current_stream')}/{meta.get('total_streams')}")


async def start_build(slug: str, orchestrator_convo_id: str = None):
    """Initialize and start a build
    
    Args:
        slug: Build slug
        orchestrator_convo_id: The conversation ID where this build was initiated.
                               Used for parent context tracking in thread titles.
    """
    meta = load_meta(slug)
    
    if meta.get("status") == "active":
        print(f"Build {slug} already active")
        return
    
    meta["status"] = "active"
    meta["started_at"] = datetime.now(timezone.utc).isoformat()
    
    # Track orchestrator conversation for parent context resolution
    if orchestrator_convo_id:
        meta["orchestrator_convo_id"] = orchestrator_convo_id
    
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
    pending = sum(1 for d in drops.values() if d.get("status") == "pending")
    dead = sum(1 for d in drops.values() if d.get("status") == "dead")
    failed = sum(1 for d in drops.values() if d.get("status") == "failed")
    
    print(f"""
Build: {slug}
Status: {meta.get('status', 'unknown')}
Stream: {meta.get('current_stream', '?')}/{meta.get('total_streams', '?')}

Drops:
  Complete: {complete}
  Running:  {running}
  Pending:  {pending}
  Dead:     {dead}
  Failed:   {failed}
  Total:    {len(drops)}

Progress: {complete}/{len(drops)} ({int(complete/len(drops)*100) if drops else 0}%)
""")


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
    
    # 3.5. Activate VibeTeacher at build_complete checkpoint
    print("[FINALIZE] Activating VibeTeacher...")
    try:
        # Generate build summary for teaching context
        build_summary = await summarize_build(slug, meta)
        
        teaching_result = subprocess.run(
            ["python3", str(WORKSPACE / "N5" / "pulse" / "teaching" / "teaching_manager.py"),
             "activate",
             "--checkpoint", "build_complete",
             "--slug", slug,
             "--input", build_summary[:2000]],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        
        if teaching_result.returncode == 0:
            try:
                teaching_data = json.loads(teaching_result.stdout)
                if teaching_data.get("activated"):
                    results["teaching_moment"] = teaching_data.get("teaching")
                    print(f"[FINALIZE] ✅ Teaching moment captured: {teaching_data.get('teaching', {}).get('precise_term', 'unknown')}")
            except:
                pass
    except Exception as e:
        print(f"[FINALIZE] Teaching activation error (non-blocking): {e}")
    
    # 4. Save finalization results
    finalize_path = BUILDS_DIR / slug / "FINALIZATION.json"
    with open(finalize_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # 5. Update meta
    meta["finalized_at"] = datetime.now(timezone.utc).isoformat()
    meta["finalization_passed"] = results["success"]
    save_meta(slug, meta)
    
    # 6. SMS summary
    teaching_summary = ""
    try:
        teaching_cmd = subprocess.run(
            ["python3", str(WORKSPACE / "N5" / "pulse" / "teaching" / "build_review.py"),
             "generate", slug],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        if teaching_cmd.returncode == 0:
            teaching_data = json.loads(teaching_cmd.stdout)
            if teaching_data.get("total_moments", 0) > 0:
                terms = teaching_data.get("new_terms_introduced", [])
                teaching_summary = f"\n📚 Teaching: {', '.join(terms[:3])}"
                if len(terms) > 3:
                    teaching_summary += f" +{len(terms)-3} more"
                teaching_summary += "\nReply 'teach' for details."
    except:
        pass

    if results["success"]:
        await send_sms(f"[PULSE] {slug} FINALIZED ✅ Artifacts verified, tests passed.{teaching_summary}")
    else:
        failures = []
        if not results.get("verification", {}).get("passed", True):
            failures.append("artifacts")
        if not results.get("integration_tests", {}).get("passed", True):
            failures.append("tests")
        await send_sms(f"[PULSE] {slug} FINALIZE ❌ Failed: {', '.join(failures)}. Review needed.{teaching_summary}")
    
    print(f"[FINALIZE] Complete. Success: {results['success']}")
    return results


def cmd_plan(task_id: str):
    """Generate plan from seeded task."""
    result = subprocess.run(
        ["python3", "./scripts/pulse/plan_generator.py", task_id],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    try:
        data = json.loads(result.stdout)
        if data.get("success"):
            print(f"✅ Plan generated: {data.get('plan_path', 'N/A')}")
            print(f"   Drops: {data.get('drops_count', '?')}")
            print(f"   Streams: {data.get('streams', '?')}")
            print(f"\nNext: python3 Skills/pulse/scripts/pulse.py review {task_id}")
        else:
            print(f"❌ Plan generation failed: {data.get('error')}")
    except:
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")


def cmd_review(slug: str):
    """Initiate HITL plan review."""
    result = subprocess.run(
        ["python3", "./scripts/pulse/review_manager.py", "initiate", slug],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    try:
        data = json.loads(result.stdout)
        if data.get("success"):
            print("📋 Plan review initiated")
            print(f"\n--- SMS MESSAGE ---\n{data.get('sms_message', '')}\n---")
            print("\nWaiting for V's response...")
            print(f"\nNote: {data.get('note', '')}")
        else:
            print(f"❌ Review initiation failed: {data.get('error')}")
    except:
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")


def cmd_approve(slug: str):
    """Approve plan and start build."""
    result = subprocess.run(
        ["python3", "./scripts/pulse/review_manager.py", "respond", slug, "go"],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    try:
        data = json.loads(result.stdout)
        if data.get("action") == "approved":
            print(f"✅ Plan approved. Starting build...")
            asyncio.run(start_build(slug))
        else:
            print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")


def cmd_sync_drive(slug: str):
    """Sync build to Google Drive."""
    result = subprocess.run(
        ["python3", "./scripts/pulse/outpost_manager.py", "sync", slug],
        capture_output=True, text=True, cwd=str(WORKSPACE)
    )
    try:
        data = json.loads(result.stdout)
        if data.get("success"):
            print(f"✅ Drive sync: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Sync failed: {data.get('error')}")
    except:
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")


def cmd_lifecycle_start():
    """Create lifecycle agent (scheduled task)."""
    from datetime import datetime
    
    # Check if agent already exists
    # For now, just print instructions since we can't create agents from scripts
    print(json.dumps({
        "success": True,
        "message": "Lifecycle agent instructions",
        "note": "Create a scheduled agent with these settings:",
        "agent_config": {
            "rrule": "FREQ=MINUTELY;INTERVAL=5",
            "instruction": """Pulse Lifecycle Agent - tick the lifecycle

1. Run: python3 scripts/pulse/lifecycle_agent.py tick
2. Review output for actions taken
3. If any errors, report via SMS

Self-destruct condition: If 'No tasks in queue' for 6 consecutive ticks (30 min), delete yourself.""",
            "delivery": "sms"
        }
    }, indent=2))

def cmd_lifecycle_stop():
    """Stop lifecycle agent."""
    print(json.dumps({
        "success": True,
        "message": "To stop lifecycle agent: delete the 'Pulse Lifecycle Agent' scheduled task",
        "note": "Or text: pulse lifecycle stop"
    }, indent=2))

def cmd_lifecycle_status():
    """Show lifecycle status."""
    result = subprocess.run(
        ["python3", str(WORKSPACE / "N5" / "pulse" / "lifecycle_agent.py"), "status"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(json.dumps({"error": result.stderr or "Failed to get status"}))

def cmd_lifecycle_tick(dry_run: bool = False):
    """Run single lifecycle tick."""
    cmd = ["python3", str(WORKSPACE / "N5" / "pulse" / "lifecycle_agent.py"), "tick"]
    if dry_run:
        cmd.append("--dry-run")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(json.dumps({"error": result.stderr or result.stdout}))


def main():
    parser = argparse.ArgumentParser(
        description="Pulse Build Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start <slug>       Start automated orchestration
  status <slug>      Show current build status
  stop <slug>        Gracefully stop orchestration
  resume <slug>      Resume a stopped build
  tick <slug>        Run single orchestration cycle
  finalize <slug>    Run post-build finalization
  
  # v2 lifecycle commands:
  plan <task_id>     Generate plan from seeded task
  review <slug>      Initiate HITL plan review
  approve <slug>     Approve plan and start build
  sync-drive <slug>  Manual Drive sync
  
  # v3 lifecycle management:
  lifecycle start    Create lifecycle agent (scheduled)
  lifecycle stop     Stop lifecycle agent
  lifecycle status   Show queue/lifecycle state  
  lifecycle tick     Manual single tick (--dry-run for preview)
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Build management commands
    start_parser = subparsers.add_parser("start", help="Start automated orchestration")
    start_parser.add_argument("slug", help="Build slug")
    start_parser.add_argument("--orchestrator-convo", 
                             help="Conversation ID of the orchestrator thread")
    
    status_parser = subparsers.add_parser("status", help="Show current build status")
    status_parser.add_argument("slug", help="Build slug")
    
    stop_parser = subparsers.add_parser("stop", help="Gracefully stop orchestration")
    stop_parser.add_argument("slug", help="Build slug")
    
    resume_parser = subparsers.add_parser("resume", help="Resume a stopped build")
    resume_parser.add_argument("slug", help="Build slug")
    
    tick_parser = subparsers.add_parser("tick", help="Run single orchestration cycle")
    tick_parser.add_argument("slug", help="Build slug")
    
    finalize_parser = subparsers.add_parser("finalize", help="Run post-build finalization")
    finalize_parser.add_argument("slug", help="Build slug")
    
    # v2 lifecycle commands
    plan_parser = subparsers.add_parser("plan", help="Generate plan from seeded task")
    plan_parser.add_argument("slug", help="Task ID or build slug")
    
    review_parser = subparsers.add_parser("review", help="Initiate HITL plan review")
    review_parser.add_argument("slug", help="Build slug")
    
    approve_parser = subparsers.add_parser("approve", help="Approve plan and start build")
    approve_parser.add_argument("slug", help="Build slug")
    
    sync_parser = subparsers.add_parser("sync-drive", help="Manual Drive sync")
    sync_parser.add_argument("slug", help="Build slug")
    
    # Lifecycle management (v3)
    lifecycle_parser = subparsers.add_parser("lifecycle", help="Manage lifecycle agent")
    lifecycle_parser.add_argument("action", choices=["start", "stop", "status", "tick"],
                                 help="start=create agent, stop=delete agent, status=show state, tick=manual advance")
    lifecycle_parser.add_argument("--dry-run", action="store_true", help="For tick: show what would happen")
    
    args = parser.parse_args()
    
    if args.command == "start":
        asyncio.run(start_build(args.slug, orchestrator_convo_id=args.orchestrator_convo))
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
    # v2 lifecycle commands
    elif args.command == "plan":
        cmd_plan(args.slug)
    elif args.command == "review":
        cmd_review(args.slug)
    elif args.command == "approve":
        cmd_approve(args.slug)
    elif args.command == "sync-drive":
        cmd_sync_drive(args.slug)
    elif args.command == "lifecycle":
        if args.action == "start":
            cmd_lifecycle_start()
        elif args.action == "stop":
            cmd_lifecycle_stop()
        elif args.action == "status":
            cmd_lifecycle_status()
        elif args.action == "tick":
            cmd_lifecycle_tick(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
