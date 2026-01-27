#!/usr/bin/env python3
"""
Seeded judgment evaluator for Pulse v2.
Determines if an interview has enough information to proceed to planning.
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime, timezone

INTERVIEWS_DIR = Path(__file__).parent / "interviews"
CONFIG_PATH = Path(__file__).parent.parent / "Skills" / "pulse" / "config" / "pulse_v2_config.json"
QUEUE_PATH = Path(__file__).parent / "task_queue.json"


def now_utc() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_config() -> dict:
    """Load Pulse v2 configuration."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {"interview": {"seeded_threshold": 0.8}}


def load_task(task_id: str) -> dict | None:
    """Load task from queue by ID or slug."""
    if not QUEUE_PATH.exists():
        return None

    queue = json.loads(QUEUE_PATH.read_text())
    for task in queue.get("tasks", []):
        if task["id"] == task_id or task.get("slug", "") == task_id:
            return task
    return None


def load_fragments(task_id: str) -> list:
    """Load all fragments for a task."""
    fragments_path = INTERVIEWS_DIR / task_id / "fragments.jsonl"

    if not fragments_path.exists():
        return []

    fragments = []
    with open(fragments_path) as f:
        for line in f:
            if line.strip():
                fragments.append(json.loads(line))
    return fragments


JUDGMENT_PROMPT = """You are evaluating whether an interview has gathered enough information to create a detailed execution plan.

Task: {task_title}
Task Type: {task_type}
Original Request: {original_message}

Interview Responses Collected:
{fragments_text}

Evaluate:
1. Do we have enough information to create a detailed execution plan?
2. What critical information is still missing?
3. How confident are you (0.0-1.0) that we can proceed?

Consider:
- For CONTENT tasks: Do we know the audience, tone, key points, constraints?
- For RESEARCH tasks: Do we know the scope, depth, deliverable format, deadline?
- For CODE_BUILD tasks: Do we know the requirements, constraints, success criteria?
- For ANALYSIS tasks: Do we know the data sources, questions to answer, format?

Respond with JSON:
{{
  "seeded": true/false,
  "confidence": 0.0-1.0,
  "missing": ["list", "of", "gaps"],
  "summary": "Brief summary of what we know",
  "reasoning": "Why seeded or not seeded"
}}"""


def judge_with_llm(task_title: str, task_type: str, original_message: str, fragments: list) -> dict:
    """Use LLM to judge if interview is seeded."""
    import requests

    fragments_text = "\n\n".join([
        f"[{f.get('channel', 'unknown')}] {f.get('content', '')}"
        for f in fragments
    ])

    prompt = JUDGMENT_PROMPT.format(
        task_title=task_title,
        task_type=task_type,
        original_message=original_message,
        fragments_text=fragments_text if fragments_text else "(No responses yet)"
    )

    try:
        response = requests.post(
            "https://api.zo.computer/zo/ask",
            headers={
                "authorization": os.environ.get("ZO_CLIENT_IDENTITY_TOKEN", ""),
                "content-type": "application/json"
            },
            json={
                "input": prompt,
                "output_format": {
                    "type": "object",
                    "properties": {
                        "seeded": {"type": "boolean"},
                        "confidence": {"type": "number"},
                        "missing": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["seeded", "confidence", "missing"]
                }
            },
            timeout=120
        )

        result = response.json()
        return result.get("output", {
            "seeded": False,
            "confidence": 0.0,
            "missing": ["evaluation_failed"],
            "reasoning": "Failed to get LLM response"
        })
    except Exception as e:
        return {
            "seeded": False,
            "confidence": 0.0,
            "missing": ["llm_error"],
            "reasoning": f"LLM error: {str(e)}"
        }


def judge_heuristic(fragments: list, task_type: str) -> dict:
    """Fast heuristic judgment (no API call)."""
    # Simple heuristic: need at least 2 fragments with substance
    substantive = [f for f in fragments if len(f.get("content", "")) > 20]

    if len(substantive) >= 3:
        return {
            "seeded": True,
            "confidence": 0.7,
            "missing": [],
            "summary": f"Collected {len(substantive)} substantive responses",
            "reasoning": "Heuristic: 3+ substantive fragments",
            "method": "heuristic"
        }
    elif len(substantive) >= 1:
        return {
            "seeded": False,
            "confidence": 0.4,
            "missing": ["more_context"],
            "summary": f"Only {len(substantive)} substantive response(s)",
            "reasoning": "Heuristic: need more detail",
            "method": "heuristic"
        }
    else:
        return {
            "seeded": False,
            "confidence": 0.1,
            "missing": ["any_substantive_input"],
            "summary": "No substantive responses yet",
            "reasoning": "Heuristic: no real content",
            "method": "heuristic"
        }


def judge(task_id: str, use_llm: bool = True) -> dict:
    """
    Judge if an interview is seeded (ready for planning).
    """
    # Load task info from queue
    task = load_task(task_id)

    if not task:
        return {
            "error": "Task not found",
            "seeded": False,
            "task_id": task_id
        }

    # Load fragments
    fragments = load_fragments(task_id)

    # Judge
    result = None
    if use_llm:
        result = judge_with_llm(
            task["title"],
            task["type"],
            task.get("intake_message", ""),
            fragments
        )
        result["method"] = "llm"
    else:
        result = judge_heuristic(fragments, task["type"])

    # Check against threshold
    config = load_config()
    threshold = config.get("interview", {}).get("seeded_threshold", 0.8)

    result["threshold"] = threshold
    result["passes_threshold"] = result.get("confidence", 0) >= threshold
    result["task_id"] = task_id
    result["task_title"] = task["title"]
    result["task_type"] = task["type"]
    result["fragment_count"] = len(fragments)
    result["judged_at"] = now_utc()

    return result


def judge_and_store(task_id: str, use_llm: bool = True) -> dict:
    """
    Judge interview and store result.
    Returns judgment dict and file path.
    """
    result = judge(task_id, use_llm=use_llm)

    # Store judgment result
    interview_dir = INTERVIEWS_DIR / task_id
    interview_dir.mkdir(parents=True, exist_ok=True)

    judgment_path = interview_dir / "seed_judgment.json"
    judgment_path.write_text(json.dumps(result, indent=2))

    result["stored_at"] = judgment_path.as_posix()
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Seeded Judgment Evaluator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Judge with heuristic (fast, no API call)
  python3 seeded_judge.py test-task --no-llm

  # Judge with LLM (detailed evaluation)
  python3 seeded_judge.py test-task

  # Judge and store result
  python3 seeded_judge.py test-task --store

  # Load existing judgment
  python3 seeded_judge.py test-task --load-only
"""
    )

    parser.add_argument("task_id", help="Task ID or slug")
    parser.add_argument("--no-llm", action="store_true",
                       help="Use heuristic only (no API call)")
    parser.add_argument("--store", action="store_true",
                       help="Store judgment result to interview dir")
    parser.add_argument("--load-only", action="store_true",
                       help="Load existing judgment without re-evaluating")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed output")

    args = parser.parse_args()

    # Load existing judgment if requested
    if args.load_only:
        judgment_path = INTERVIEWS_DIR / args.task_id / "seed_judgment.json"
        if judgment_path.exists():
            result = json.loads(judgment_path.read_text())
            print(json.dumps(result, indent=2 if args.verbose else None))
            return
        else:
            print(json.dumps({"error": "No stored judgment found"}, indent=2))
            return

    # Judge and optionally store
    if args.store:
        result = judge_and_store(args.task_id, use_llm=not args.no_llm)
    else:
        result = judge(args.task_id, use_llm=not args.no_llm)

    print(json.dumps(result, indent=2 if args.verbose else None))


if __name__ == "__main__":
    main()
