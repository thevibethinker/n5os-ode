#!/usr/bin/env python3
"""
loop_runner.py - Core Ralph concept: run AI agent in a loop until specs are met.

Each iteration starts with FRESH context (not accumulated). Progress persists
in files and git, not in the agent's memory.

Usage:
    # Dry run (default) - shows plan
    python3 N5/scripts/loop_runner.py --prompt task.md --build-slug my-build

    # Actually execute
    python3 N5/scripts/loop_runner.py --prompt task.md --build-slug my-build --execute

    # With iteration limit
    python3 N5/scripts/loop_runner.py --prompt task.md --max-iterations 5 --execute

    # Force past 20 iterations (dangerous)
    python3 N5/scripts/loop_runner.py --prompt task.md --max-iterations 50 --force --execute
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Default safety limits
DEFAULT_MAX_ITERATIONS = 10
HARD_LIMIT_ITERATIONS = 20  # Requires --force to exceed


def get_prompt_hash(content: str) -> str:
    """Generate short hash of prompt content for tracking."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def call_zo_ask(prompt: str) -> dict:
    """Call the /zo/ask API with the given prompt."""
    import requests
    
    token = os.environ.get("ZO_CLIENT_IDENTITY_TOKEN")
    if not token:
        return {
            "success": False,
            "error": "ZO_CLIENT_IDENTITY_TOKEN not set",
            "output": None
        }
    
    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": token,
                "content-type": "application/json"
            },
            json={"input": prompt},
            timeout=300  # 5 minute timeout per iteration
        )
        response.raise_for_status()
        result = response.json()
        return {
            "success": True,
            "output": result.get("output", ""),
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output": None
        }


def run_backpressure(build_slug: str) -> dict:
    """
    Run backpressure validation.
    Returns dict with: status (PASS/WARN/FAIL), details, checks
    """
    script_path = Path("N5/scripts/backpressure.py")
    
    if not script_path.exists():
        # Stub: return PASS if script doesn't exist yet
        return {
            "status": "PASS",
            "details": "backpressure.py not found - using stub (PASS)",
            "checks": [],
            "stub": True
        }
    
    try:
        result = subprocess.run(
            ["python3", str(script_path), build_slug, "--json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "status": "PASS",
                    "details": result.stdout.strip() or "No output",
                    "checks": []
                }
        else:
            return {
                "status": "FAIL",
                "details": result.stderr.strip() or result.stdout.strip(),
                "checks": []
            }
    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "details": "Backpressure check timed out",
            "checks": []
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Error running backpressure: {e}",
            "checks": []
        }


def run_struggle_detector(build_slug: str, history_file: Optional[Path] = None) -> dict:
    """
    Run struggle detection.
    Returns dict with: status (HEALTHY/STRUGGLING/STUCK), details, signals
    """
    script_path = Path("N5/scripts/struggle_detector.py")
    
    if not script_path.exists():
        # Stub: return HEALTHY if script doesn't exist yet
        return {
            "status": "HEALTHY",
            "details": "struggle_detector.py not found - using stub (HEALTHY)",
            "signals": [],
            "stub": True
        }
    
    try:
        cmd = ["python3", str(script_path), build_slug, "--json"]
        if history_file and history_file.exists():
            cmd.extend(["--history", str(history_file)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "status": "HEALTHY",
                    "details": result.stdout.strip() or "No output",
                    "signals": []
                }
        else:
            # Non-zero exit might indicate STUCK
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "status": "WARN",
                    "details": result.stderr.strip() or result.stdout.strip(),
                    "signals": []
                }
    except subprocess.TimeoutExpired:
        return {
            "status": "WARN",
            "details": "Struggle detection timed out",
            "signals": []
        }
    except Exception as e:
        return {
            "status": "WARN",
            "details": f"Error running struggle detector: {e}",
            "signals": []
        }


def load_prompt(prompt_path: Path) -> str:
    """Load prompt from file."""
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text()


def append_to_history(history_file: Path, entry: dict):
    """Append an entry to the loop history JSONL file."""
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def read_history(history_file: Path) -> list[dict]:
    """Read all entries from loop history."""
    if not history_file.exists():
        return []
    entries = []
    with open(history_file) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def run_loop(
    prompt_path: Path,
    build_slug: str,
    max_iterations: int,
    force: bool,
    execute: bool,
    verbose: bool = False
) -> dict:
    """
    Run the main loop.
    
    Returns dict with:
        - success: bool
        - iterations: int
        - final_status: str (COMPLETE/MAX_ITERATIONS/STUCK/ERROR)
        - history_file: str
    """
    # Setup paths
    build_dir = Path(f"N5/builds/{build_slug}")
    history_file = build_dir / "loop_history.jsonl"
    
    # Validate
    if max_iterations > HARD_LIMIT_ITERATIONS and not force:
        return {
            "success": False,
            "iterations": 0,
            "final_status": "ERROR",
            "error": f"Max iterations ({max_iterations}) exceeds hard limit ({HARD_LIMIT_ITERATIONS}). Use --force to override.",
            "history_file": str(history_file)
        }
    
    # Load prompt
    try:
        prompt_content = load_prompt(prompt_path)
        prompt_hash = get_prompt_hash(prompt_content)
    except FileNotFoundError as e:
        return {
            "success": False,
            "iterations": 0,
            "final_status": "ERROR",
            "error": str(e),
            "history_file": str(history_file)
        }
    
    # Dry run mode
    if not execute:
        print("=" * 60)
        print("DRY RUN MODE - No actual execution")
        print("=" * 60)
        print(f"\nPrompt file: {prompt_path}")
        print(f"Prompt hash: {prompt_hash}")
        print(f"Build slug: {build_slug}")
        print(f"Max iterations: {max_iterations}")
        print(f"Force mode: {force}")
        print(f"History file: {history_file}")
        print(f"\nPrompt preview (first 500 chars):")
        print("-" * 40)
        print(prompt_content[:500])
        if len(prompt_content) > 500:
            print(f"... ({len(prompt_content) - 500} more characters)")
        print("-" * 40)
        print("\nTo execute, add --execute flag")
        return {
            "success": True,
            "iterations": 0,
            "final_status": "DRY_RUN",
            "history_file": str(history_file)
        }
    
    # Execute mode
    print(f"Starting loop for build: {build_slug}")
    print(f"Prompt: {prompt_path} (hash: {prompt_hash})")
    print(f"Max iterations: {max_iterations}")
    print("-" * 40)
    
    iteration = 0
    final_status = "UNKNOWN"
    
    while iteration < max_iterations:
        iteration += 1
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        print(f"\n[Iteration {iteration}/{max_iterations}]")
        
        # Call /zo/ask with fresh context (re-read prompt each time)
        prompt_content = load_prompt(prompt_path)
        
        if verbose:
            print(f"  Calling /zo/ask...")
        
        zo_result = call_zo_ask(prompt_content)
        
        if not zo_result["success"]:
            print(f"  ❌ API call failed: {zo_result['error']}")
            entry = {
                "iteration": iteration,
                "timestamp": timestamp,
                "prompt_hash": prompt_hash,
                "api_success": False,
                "api_error": zo_result["error"],
                "backpressure": None,
                "struggle": None,
                "duration_sec": round(time.time() - start_time, 2)
            }
            append_to_history(history_file, entry)
            final_status = "ERROR"
            break
        
        if verbose:
            print(f"  ✓ API call succeeded")
            print(f"  Output preview: {zo_result['output'][:200]}...")
        
        # Run backpressure validation
        if verbose:
            print(f"  Running backpressure check...")
        backpressure = run_backpressure(build_slug)
        bp_status = backpressure.get("status", "UNKNOWN")
        print(f"  Backpressure: {bp_status}")
        
        # Run struggle detection
        if verbose:
            print(f"  Running struggle detection...")
        struggle = run_struggle_detector(build_slug, history_file)
        struggle_status = struggle.get("status", "UNKNOWN")
        print(f"  Struggle: {struggle_status}")
        
        duration = round(time.time() - start_time, 2)
        
        # Log to history
        entry = {
            "iteration": iteration,
            "timestamp": timestamp,
            "prompt_hash": prompt_hash,
            "api_success": True,
            "backpressure": backpressure,
            "struggle": struggle,
            "duration_sec": duration
        }
        append_to_history(history_file, entry)
        
        print(f"  Duration: {duration}s")
        
        # Check stop conditions
        if bp_status == "PASS" and struggle_status == "HEALTHY":
            print(f"\n✓ Loop complete! Backpressure passed, no struggle detected.")
            final_status = "COMPLETE"
            break
        
        if struggle_status == "STUCK":
            print(f"\n⚠ Loop stopped: Agent appears stuck.")
            final_status = "STUCK"
            break
        
        if bp_status == "FAIL":
            print(f"  → Backpressure failed, continuing...")
        
        if struggle_status == "STRUGGLING":
            print(f"  → Agent struggling, continuing with caution...")
    
    else:
        # Exhausted max iterations
        print(f"\n⚠ Max iterations ({max_iterations}) reached without completion.")
        final_status = "MAX_ITERATIONS"
    
    return {
        "success": final_status == "COMPLETE",
        "iterations": iteration,
        "final_status": final_status,
        "history_file": str(history_file)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Run AI agent in a loop until specifications are met.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - shows plan
  python3 N5/scripts/loop_runner.py --prompt task.md --build-slug my-build

  # Actually execute
  python3 N5/scripts/loop_runner.py --prompt task.md --build-slug my-build --execute

  # With iteration limit
  python3 N5/scripts/loop_runner.py --prompt task.md --max-iterations 5 --execute

  # Force past 20 iterations (dangerous)
  python3 N5/scripts/loop_runner.py --prompt task.md --max-iterations 50 --force --execute

Safety:
  - Default mode is dry-run (no execution)
  - Max 20 iterations before requiring --force
  - All iterations logged to loop_history.jsonl in build folder
        """
    )
    
    parser.add_argument(
        "--prompt", "-p",
        type=Path,
        required=True,
        help="Path to the prompt file (Markdown)"
    )
    
    parser.add_argument(
        "--build-slug", "-b",
        type=str,
        required=True,
        help="Build slug for organizing outputs and history"
    )
    
    parser.add_argument(
        "--max-iterations", "-m",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Maximum iterations (default: {DEFAULT_MAX_ITERATIONS}, hard limit: {HARD_LIMIT_ITERATIONS} without --force)"
    )
    
    parser.add_argument(
        "--execute", "-x",
        action="store_true",
        help="Actually execute (without this flag, runs in dry-run mode)"
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help=f"Allow exceeding {HARD_LIMIT_ITERATIONS} iterations (dangerous)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    result = run_loop(
        prompt_path=args.prompt,
        build_slug=args.build_slug,
        max_iterations=args.max_iterations,
        force=args.force,
        execute=args.execute,
        verbose=args.verbose
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["final_status"] != "DRY_RUN":
            print("\n" + "=" * 40)
            print(f"Final Status: {result['final_status']}")
            print(f"Iterations: {result['iterations']}")
            print(f"History: {result['history_file']}")
    
    # Exit code
    if result["success"] or result["final_status"] == "DRY_RUN":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
