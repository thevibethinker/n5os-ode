#!/usr/bin/env python3
"""
Plan generator for Pulse v2.
Transforms seeded interviews into execution plans.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
import subprocess

PULSE_DIR = Path(__file__).parent
BUILDS_DIR = Path("/home/workspace/N5/builds")

def run_cmd(cmd: list) -> dict:
    """Run a command and return parsed JSON output."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/workspace")
    try:
        return json.loads(result.stdout)
    except:
        return {"error": result.stderr or result.stdout}

def generate_plan(task_id: str) -> dict:
    """Generate execution plan from seeded interview."""
    
    # 1. Load task info from queue
    queue_path = PULSE_DIR / "task_queue.json"
    if not queue_path.exists():
        return {"error": "Task queue not found"}
    
    queue = json.loads(queue_path.read_text())
    task = None
    for t in queue.get("tasks", []):
        if t["id"] == task_id or t["slug"] == task_id:
            task = t
            break
    
    if not task:
        return {"error": "Task not found"}
    
    # 2. Load synthesis
    interviews_dir = PULSE_DIR / "interviews"
    synthesis_path = interviews_dir / task_id / "synthesis.json"
    if not synthesis_path.exists():
        # Try by slug
        synthesis_path = interviews_dir / task["slug"] / "synthesis.json"
    
    if not synthesis_path.exists():
        return {"error": "No synthesis found. Run interview_manager.py synthesize first."}
    
    synthesis = json.loads(synthesis_path.read_text())
    
    # 3. Decompose into plan using decomposer
    decomp_result = run_cmd([
        "python3", "N5/pulse/decomposer.py",
        task["title"],
        "--type", task["type"],
        "--synthesis", json.dumps(synthesis)
    ])
    
    if "error" in decomp_result:
        return decomp_result
    
    # 4. Create build folder
    slug = task["slug"]
    build_dir = BUILDS_DIR / slug
    build_dir.mkdir(parents=True, exist_ok=True)
    (build_dir / "drops").mkdir(exist_ok=True)
    (build_dir / "deposits").mkdir(exist_ok=True)
    (build_dir / "artifacts").mkdir(exist_ok=True)
    
    # 5. Generate meta.json
    config_path = Path("/home/workspace/Skills/pulse/config/pulse_v2_config.json")
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    default_model = config.get("default_build_model", "anthropic:claude-opus-4-5-20251101")
    
    meta = {
        "slug": slug,
        "title": task["title"],
        "build_type": task["type"],
        "task_id": task["id"],
        "status": "planning",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "model": default_model,
        "total_streams": decomp_result["streams"],
        "current_stream": 0,
        "drops": {},
        "interview_synthesis": synthesis
    }
    
    # Convert drops to meta format
    for drop in decomp_result["drops"]:
        meta["drops"][drop["id"]] = {
            "name": drop["name"],
            "stream": drop["stream"],
            "depends_on": drop["depends_on"],
            "spawn_mode": drop.get("spawn_mode", "auto"),
            "status": "pending"
        }
    
    (build_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    
    # 6. Generate PLAN.md
    plan_md = generate_plan_markdown(task, decomp_result, synthesis)
    (build_dir / "PLAN.md").write_text(plan_md)
    
    # 7. Generate drop briefs
    for drop in decomp_result["drops"]:
        brief = generate_drop_brief(slug, drop, task, synthesis, default_model)
        brief_path = build_dir / "drops" / f"{drop['id']}-{drop['name'].lower().replace(' ', '-')}.md"
        brief_path.write_text(brief)
    
    # 8. Update task status
    run_cmd(["python3", "N5/pulse/queue_manager.py", "advance", task_id, "planning"])
    
    return {
        "success": True,
        "build_dir": str(build_dir),
        "plan_path": str(build_dir / "PLAN.md"),
        "drops_count": len(decomp_result["drops"]),
        "streams": decomp_result["streams"]
    }

def generate_plan_markdown(task: dict, decomp: dict, synthesis: dict) -> str:
    """Generate PLAN.md content."""
    
    # Create drops table
    header = "| Stream | ID | Name | Depends On |"
    separator = "|--------|----|-----|------------|"
    rows = "\n".join([
        f"| {d['stream']} | {d['id']} | {d['name']} | {', '.join(d['depends_on']) or 'None'} |"
        for d in decomp["drops"]
    ])
    
    drops_table = f"{header}\n{separator}\n{rows}"
    
    criteria = "\n".join([f"- [ ] {c}" for c in decomp["success_criteria"]])
    
    # Get synthesis summary (first 1000 chars)
    synthesis_summary = synthesis.get("combined_text", "No synthesis available")[:1000]
    
    return f"""---
created: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
version: 1.0
type: build_plan
status: planning
task_id: {task['id']}
---

# {task['title']}

## Task Type
{task['type']}

---
---

## Interview Summary

{synthesis_summary}

---
---

## Success Criteria

{criteria}

---
---

## Execution Plan

### Streams Overview
- **Total Streams:** {decomp["streams"]}

### Drops

{drops_table}

---
---

*Generated by Pulse v2 Plan Generator*
"""

def generate_drop_brief(slug: str, drop: dict, task: dict, synthesis: dict, model: str) -> str:
    """Generate individual drop brief."""
    
    # Create deliverables list
    deliverables_list = "\n".join([f"- {d}" for d in drop["deliverables"]])
    
    # Get synthesis excerpt relevant to this drop
    synthesis_excerpt = synthesis.get("combined_text", "")[:500]
    
    return f"""---
drop_id: {drop['id']}
build_slug: {slug}
stream: {drop['stream']}
title: "{drop['name']}"
thread_title: "[{slug}] {drop['id']}: {drop['name']}"
depends_on: {json.dumps(drop['depends_on'])}
spawn_mode: {drop.get('spawn_mode', 'auto')}
model: {model}
---

# {drop['id']}: {drop['name']}

## Context

**Task:** {task['title']}
**Type:** {task['type']}
**Stream:** {drop['stream']}

## Description

{drop['description']}

## Deliverables

{deliverables_list}

## Dependencies

{', '.join(drop['depends_on']) if drop['depends_on'] else 'None'}

## Interview Context

{synthesis_excerpt}

---
---

*Generated by Pulse v2 Plan Generator*
"""

def main():
    parser = argparse.ArgumentParser(description="Pulse v2 Plan Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate plan from interview")
    gen_parser.add_argument("task_id", help="Task ID or slug")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        result = generate_plan(args.task_id)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
