#!/usr/bin/env python3
"""
Build Dashboard - Consolidated view of build health.

Shows: build status, worker progress, backpressure results, struggle status.

Usage:
    python3 N5/scripts/build_dashboard.py <slug>
    python3 N5/scripts/build_dashboard.py <slug> --json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/home/workspace")
from N5.lib.paths import N5_BUILDS_DIR, N5_SCRIPTS_DIR


def run_script(cmd: list, capture_json: bool = True) -> dict | None:
    """Run a script and optionally parse JSON output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        if capture_json and result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw_output": result.stdout, "exit_code": result.returncode}
        return {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "exit_code": -1}
    except FileNotFoundError:
        return {"error": "script not found", "exit_code": -1}
    except Exception as e:
        return {"error": str(e), "exit_code": -1}


def load_meta(build_path: Path) -> dict:
    """Load build meta.json."""
    meta_file = build_path / "meta.json"
    if meta_file.exists():
        try:
            return json.loads(meta_file.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def load_plan(build_path: Path) -> dict:
    """Parse PLAN.md for worker list."""
    plan_file = build_path / "PLAN.md"
    workers = []
    
    if plan_file.exists():
        content = plan_file.read_text()
        # Look for worker references in the plan
        import re
        # Match patterns like "W1.1", "W1.2", etc.
        worker_ids = set(re.findall(r'\bW\d+\.\d+\b', content))
        for wid in sorted(worker_ids):
            workers.append({"id": wid, "from_plan": True})
    
    return {"workers": workers}


def load_workers(build_path: Path) -> list:
    """Load worker status from workers/ and completions/ directories."""
    workers = []
    workers_dir = build_path / "workers"
    completions_dir = build_path / "completions"
    
    # Get worker briefs
    if workers_dir.exists():
        for brief in sorted(workers_dir.glob("W*.md")):
            # Extract worker ID from filename (e.g., W1.1_task.md -> W1.1)
            name = brief.stem
            parts = name.split("_")
            worker_id = parts[0] if parts else name
            
            # Extract title from first heading
            content = brief.read_text()
            title = name
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            
            workers.append({
                "id": worker_id,
                "title": title,
                "brief": str(brief),
                "status": "pending"
            })
    
    # Check completions
    if completions_dir.exists():
        for comp_file in completions_dir.glob("*.json"):
            try:
                comp = json.loads(comp_file.read_text())
                worker_id = comp.get("worker_id", comp_file.stem)
                
                # Update matching worker
                for w in workers:
                    if w["id"] == worker_id:
                        w["status"] = comp.get("status", "complete")
                        w["completion"] = comp
                        break
                else:
                    # Worker not in briefs, add from completion
                    workers.append({
                        "id": worker_id,
                        "title": comp.get("title", worker_id),
                        "status": comp.get("status", "complete"),
                        "completion": comp
                    })
            except (json.JSONDecodeError, KeyError):
                continue
    
    # Sort by worker ID (W1.1, W1.2, W2.1, etc.)
    def sort_key(w):
        parts = w["id"].replace("W", "").split(".")
        try:
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except (ValueError, IndexError):
            return (999, 0)
    
    return sorted(workers, key=sort_key)


def get_backpressure(slug: str) -> dict:
    """Run backpressure and get results."""
    script = N5_SCRIPTS_DIR / "backpressure.py"
    if not script.exists():
        return {"status": "SKIP", "message": "backpressure.py not found", "stub": True}
    
    result = run_script(["python3", str(script), slug, "--json"])
    
    if result and "error" not in result:
        return result
    
    return {"status": "ERROR", "message": result.get("error", "unknown"), "stub": True}


def get_struggle_status(slug: str) -> dict:
    """Run struggle detector and get results."""
    script = N5_SCRIPTS_DIR / "struggle_detector.py"
    if not script.exists():
        return {"status": "SKIP", "message": "struggle_detector.py not found", "stub": True}
    
    result = run_script(["python3", str(script), "--build-slug", slug, "--json"])
    
    if result and "error" not in result:
        return result
    
    return {"status": "ERROR", "message": result.get("error", "unknown"), "stub": True}


def build_dashboard_data(slug: str) -> dict:
    """Collect all dashboard data."""
    build_path = N5_BUILDS_DIR / slug
    
    if not build_path.exists():
        return {"error": f"Build not found: {slug}", "path": str(build_path)}
    
    meta = load_meta(build_path)
    workers = load_workers(build_path)
    backpressure = get_backpressure(slug)
    struggle = get_struggle_status(slug)
    
    # Calculate summary stats
    total_workers = len(workers)
    complete_workers = sum(1 for w in workers if w.get("status") == "complete")
    
    # Determine overall status
    if meta.get("status") == "complete":
        overall_status = "COMPLETE"
    elif complete_workers == total_workers and total_workers > 0:
        overall_status = "READY_TO_CLOSE"
    elif complete_workers > 0:
        overall_status = "IN_PROGRESS"
    else:
        overall_status = "NOT_STARTED"
    
    return {
        "slug": slug,
        "path": str(build_path),
        "status": overall_status,
        "meta": meta,
        "workers": workers,
        "worker_summary": {
            "complete": complete_workers,
            "total": total_workers,
            "pct": round(complete_workers / total_workers * 100) if total_workers > 0 else 0
        },
        "backpressure": backpressure,
        "struggle": struggle,
        "timestamp": datetime.now().isoformat()
    }


def format_status_icon(status: str) -> str:
    """Get icon for status."""
    icons = {
        "complete": "✓",
        "in_progress": "⏳",
        "pending": "○",
        "waiting": "○",
        "PASS": "✓",
        "WARN": "⚠",
        "FAIL": "✗",
        "SKIP": "○",
        "HEALTHY": "✓",
        "STRUGGLING": "⚠",
        "STUCK": "✗",
        "ERROR": "?",
    }
    return icons.get(status, "?")


def render_box(title: str, lines: list[str], width: int = 56) -> list[str]:
    """Render a box section."""
    output = []
    output.append(f"├{'─' * width}┤")
    output.append(f"│  {title.upper():<{width-4}}  │")
    for line in lines:
        # Truncate if too long
        if len(line) > width - 4:
            line = line[:width-7] + "..."
        output.append(f"│  {line:<{width-4}}  │")
    return output


def render_dashboard(data: dict) -> str:
    """Render terminal dashboard."""
    if "error" in data:
        return f"Error: {data['error']}"
    
    width = 56
    lines = []
    
    # Header
    lines.append(f"╭{'─' * width}╮")
    lines.append(f"│  BUILD: {data['slug']:<{width-11}}  │")
    
    status = data['status']
    summary = data['worker_summary']
    status_line = f"Status: {status} ({summary['complete']}/{summary['total']} workers complete)"
    lines.append(f"│  {status_line:<{width-4}}  │")
    
    # Workers section
    worker_lines = []
    workers = data.get("workers", [])
    for i, w in enumerate(workers):
        prefix = "├─" if i < len(workers) - 1 else "└─"
        icon = format_status_icon(w.get("status", "pending"))
        status_str = w.get("status", "pending").title()
        title = w.get("title", w["id"])
        # Truncate title if needed
        max_title = width - 25
        if len(title) > max_title:
            title = title[:max_title-3] + "..."
        worker_lines.append(f"{prefix} {w['id']} {title} {icon} {status_str}")
    
    if not worker_lines:
        worker_lines.append("No workers found")
    
    lines.extend(render_box("WORKERS", worker_lines, width))
    
    # Backpressure section
    bp = data.get("backpressure", {})
    bp_lines = []
    
    if bp.get("stub"):
        bp_lines.append(f"⚠ Stub mode: {bp.get('message', 'no details')}")
    else:
        validators = bp.get("validators", [])
        # Handle both list format (from backpressure.py) and dict format
        if isinstance(validators, list):
            for info in validators:
                name = info.get("name", "?")
                status = info.get("status", "?")
                msg = info.get("details", info.get("message", ""))
                icon = format_status_icon(status)
                bp_lines.append(f"├─ {name:<8} {icon} {status} ({msg})" if msg else f"├─ {name:<8} {icon} {status}")
        elif isinstance(validators, dict):
            for name, info in validators.items():
                if isinstance(info, dict):
                    status = info.get("status", "?")
                    msg = info.get("message", "")
                    icon = format_status_icon(status)
                    bp_lines.append(f"├─ {name:<8} {icon} {status} ({msg})" if msg else f"├─ {name:<8} {icon} {status}")
        
        overall = bp.get("overall_status", bp.get("status", "?"))
        bp_lines.append(f"Overall: {overall}")
    
    if not bp_lines:
        bp_lines.append(f"Status: {bp.get('status', bp.get('overall_status', 'unknown'))}")
    
    lines.extend(render_box("BACKPRESSURE", bp_lines, width))
    
    # Struggle section
    struggle = data.get("struggle", {})
    struggle_lines = []
    
    if struggle.get("stub"):
        struggle_lines.append(f"⚠ Stub mode: {struggle.get('message', 'no details')}")
    else:
        status = struggle.get("status", struggle.get("overall_status", "unknown"))
        struggle_lines.append(f"Status: {status}")
        
        patterns = struggle.get("patterns_detected", struggle.get("patterns", []))
        if patterns:
            for p in patterns[:3]:  # Limit to 3
                if isinstance(p, dict):
                    struggle_lines.append(f"  • {p.get('name', p.get('pattern', '?'))}: {p.get('severity', '')}")
                else:
                    struggle_lines.append(f"  • {p}")
        else:
            struggle_lines.append("No patterns detected")
    
    lines.extend(render_box("STRUGGLE", struggle_lines, width))
    
    # Footer
    lines.append(f"╰{'─' * width}╯")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Build Dashboard - Consolidated build health view",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 N5/scripts/build_dashboard.py ralph-learnings
    python3 N5/scripts/build_dashboard.py my-build --json

Shows:
    - Build status and worker progress
    - Backpressure validation results
    - Struggle detection status
        """
    )
    parser.add_argument("slug", help="Build slug to display")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    data = build_dashboard_data(args.slug)
    
    if args.json:
        print(json.dumps(data, indent=2, default=str))
    else:
        print(render_dashboard(data))
    
    # Exit code based on overall health
    if "error" in data:
        sys.exit(2)
    
    bp_status = data.get("backpressure", {}).get("overall_status", 
                data.get("backpressure", {}).get("status", "PASS"))
    struggle_status = data.get("struggle", {}).get("status", 
                     data.get("struggle", {}).get("overall_status", "HEALTHY"))
    
    if bp_status == "FAIL" or struggle_status == "STUCK":
        sys.exit(2)
    elif bp_status == "WARN" or struggle_status == "STRUGGLING":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
