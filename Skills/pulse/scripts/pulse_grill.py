#!/usr/bin/env python3
"""
Pre-build Grill Gate for Pulse.

The gate inspects build artifacts and local architecture surfaces, then emits
questions only for decisions that cannot be resolved from the workspace.
"""

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pulse_common import PATHS, load_meta


def read_text(path: Path, limit: int = 12000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(errors="replace")
    return text[:limit]


def run_command(args: list[str]) -> str:
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=90, cwd=str(PATHS.WORKSPACE))
    except Exception as exc:
        return f"ERROR: {exc}"
    output = (proc.stdout or "") + (proc.stderr or "")
    return re.sub(r"\x1b\[[0-9;]*m", "", output).strip()


def extract_path_mentions(text: str) -> list[str]:
    found = set()
    pathish = r"(?:Skills|N5|Sites|Documents|Research|Personal|Knowledge|Projects|Integrations|Prompts)/[A-Za-z0-9._/@+=:,%-]+"
    for value in re.findall(r"file '(" + pathish + r")'", text):
        found.add(value.rstrip(".,;:"))
    for value in re.findall(r"`(" + pathish + r")`", text):
        found.add(value.rstrip(".,;:"))
    for value in re.findall(pathish, text):
        if len(value) <= 240:
            found.add(value.rstrip(".,;:"))
    return sorted(found)


def build_context(slug: str) -> dict[str, Any]:
    build_dir = PATHS.build(slug)
    plan = read_text(build_dir / "PLAN.md")
    meta = load_meta(slug) or {}
    drop_files = sorted((build_dir / "drops").glob("*.md")) if (build_dir / "drops").exists() else []
    drops = [{"name": path.name, "text": read_text(path, 4000)} for path in drop_files]
    combined = "\n".join([plan, json.dumps(meta), *[item["text"] for item in drops]])
    paths = extract_path_mentions(combined)
    existing = []
    missing = []
    future_optional = []
    for value in paths[:80]:
        path = PATHS.WORKSPACE / value
        if path.exists():
            existing.append(value)
        elif _is_future_optional_path(combined, value):
            future_optional.append(value)
        else:
            missing.append(value)
    return {
        "slug": slug,
        "build_dir": str(build_dir),
        "plan_present": bool(plan),
        "meta_present": bool(meta),
        "drop_count": len(drop_files),
        "drop_files": [path.name for path in drop_files],
        "mentioned_paths_existing": existing,
        "mentioned_paths_missing": missing,
        "mentioned_paths_future_optional": future_optional,
        "meta": meta,
        "plan_excerpt": plan[:4000],
    }


def _is_future_optional_path(text: str, path: str) -> bool:
    index = text.find(path)
    if index < 0:
        return False
    window = text[max(0, index - 240): index + len(path) + 240].lower()
    future_markers = (
        "if the proof is useful",
        "decide whether to promote",
        "promotion decision",
        "future",
        "optional",
        "later",
    )
    return any(marker in window for marker in future_markers)


def has_unresolved_open_questions(plan_text: str) -> bool:
    if "{{" in plan_text or re.search(r"\bTODO\b", plan_text):
        return True

    match = re.search(
        r"^##\s+Open Questions\s*$([\s\S]*?)(?=^##\s+|\Z)",
        plan_text,
        re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return False

    section = match.group(1)
    for line in section.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]\s+\[\s\]", stripped):
            return True
        if stripped.upper().startswith(("TODO", "TBD")):
            return True
    return False


def analyze(slug: str) -> dict[str, Any]:
    context = build_context(slug)
    unresolved = []
    auto_answers = []

    if not context["plan_present"]:
        unresolved.append({
            "question": "Where is the canonical PLAN.md for this build?",
            "recommendation": "Create `N5/builds/<slug>/PLAN.md` before starting Pulse.",
            "reason": "The grill gate cannot verify intent or success criteria without a plan.",
        })
    else:
        auto_answers.append({
            "question": "Is there a plan artifact?",
            "answer": "Yes. `PLAN.md` exists.",
            "evidence": "N5/builds/<slug>/PLAN.md",
        })

    if not context["meta_present"]:
        unresolved.append({
            "question": "Where is the canonical meta.json for this build?",
            "recommendation": "Create `N5/builds/<slug>/meta.json` with registered drops before start.",
            "reason": "Pulse cannot compute waves, statuses, or spawn modes without meta.json.",
        })
    else:
        auto_answers.append({
            "question": "Is there build metadata?",
            "answer": "Yes. `meta.json` exists.",
            "evidence": f"{len(context['meta'].get('drops', {}))} drops registered",
        })

    if context["drop_count"] == 0:
        unresolved.append({
            "question": "Which Drop briefs should Pulse execute?",
            "recommendation": "Create explicit brief files under `drops/` before start.",
            "reason": "Workers need scoped task packets; otherwise they infer work from the plan.",
        })
    else:
        auto_answers.append({
            "question": "Are Drop briefs present?",
            "answer": f"Yes. Found {context['drop_count']} brief(s).",
            "evidence": ", ".join(context["drop_files"][:8]),
        })

    if context["mentioned_paths_missing"]:
        unresolved.append({
            "question": "Should missing referenced paths be created, corrected, or removed from the plan?",
            "recommendation": "Fix path drift before spawning workers; do not let Drops guess replacement paths.",
            "reason": "Missing paths create divergent worker assumptions.",
            "evidence": context["mentioned_paths_missing"][:12],
        })
    elif context["mentioned_paths_existing"]:
        auto_answers.append({
            "question": "Did referenced workspace paths resolve?",
            "answer": "Referenced paths checked by the gate resolve.",
            "evidence": context["mentioned_paths_existing"][:12],
        })

    if context["mentioned_paths_future_optional"]:
        auto_answers.append({
            "question": "Were future-only path mentions distinguished from start blockers?",
            "answer": "Yes. Missing paths mentioned only as future promotion options are not blocking start.",
            "evidence": context["mentioned_paths_future_optional"][:12],
        })

    plan_lower = context["plan_excerpt"].lower()
    if "success criteria" not in plan_lower and "acceptance" not in plan_lower:
        unresolved.append({
            "question": "What concrete success criteria should Drops optimize for?",
            "recommendation": "Add measurable success criteria or acceptance tests to the plan.",
            "reason": "Workers need objective completion checks, not just task descriptions.",
        })

    if has_unresolved_open_questions(context["plan_excerpt"]):
        unresolved.append({
            "question": "Which open questions must be resolved before auto-spawn?",
            "recommendation": "Resolve authority, priority, and irreversible scope questions centrally; leave only execution details to Drops.",
            "reason": "Pulse workers should not make product or authority decisions independently.",
        })

    graph_review = ""
    if any(path.startswith(("Skills/", "N5/", "Prompts/", "Integrations/")) for path in context["mentioned_paths_existing"]):
        graph_review = run_command(["python3", "Skills/codebase-graph/scripts/query.py", "review", "Skills/pulse/scripts/pulse.py"])
        auto_answers.append({
            "question": "Was shared-code graph risk checked?",
            "answer": "Graph review was attempted for Pulse's command router.",
            "evidence": graph_review[:1000],
        })

    result = {
        "slug": slug,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "grill-gate",
        "auto_answers": auto_answers,
        "unresolved_questions": unresolved,
        "recommendation": "do_not_start" if unresolved else "start_allowed_after_contract_checks",
        "context": {
            "drop_count": context["drop_count"],
            "mentioned_paths_existing": context["mentioned_paths_existing"][:20],
            "mentioned_paths_missing": context["mentioned_paths_missing"][:20],
            "mentioned_paths_future_optional": context["mentioned_paths_future_optional"][:20],
            "graph_review_excerpt": graph_review[:1200],
        },
    }
    return result


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Grill Gate: {result['slug']}",
        "",
        f"Generated: `{result['generated_at']}`",
        f"Recommendation: `{result['recommendation']}`",
        "",
        "## Auto-Answered From Workspace",
        "",
    ]
    if not result["auto_answers"]:
        lines.append("- None")
    for item in result["auto_answers"]:
        lines.append(f"- **{item['question']}** {item['answer']}")
        if item.get("evidence"):
            lines.append(f"  - Evidence: {item['evidence']}")
    lines.extend(["", "## Questions For Orchestrator", ""])
    if not result["unresolved_questions"]:
        lines.append("- None")
    for idx, item in enumerate(result["unresolved_questions"], start=1):
        lines.append(f"{idx}. **{item['question']}**")
        lines.append(f"   - Recommendation: {item['recommendation']}")
        lines.append(f"   - Reason: {item['reason']}")
        if item.get("evidence"):
            evidence = item["evidence"]
            if isinstance(evidence, list):
                evidence = ", ".join(f"`{x}`" for x in evidence)
            lines.append(f"   - Evidence: {evidence}")
    return "\n".join(lines) + "\n"


def write_report(slug: str, result: dict[str, Any]) -> Path:
    artifacts = PATHS.build_artifacts(slug)
    artifacts.mkdir(parents=True, exist_ok=True)
    path = artifacts / "GRILL_GATE.md"
    today = datetime.now(timezone.utc).date().isoformat()
    body = render_markdown(result)
    path.write_text(
        "---\n"
        f"created: {today}\n"
        f"last_edited: {today}\n"
        "version: 1.0\n"
        f"provenance: pulse:{slug}\n"
        "---\n\n"
        + body
    )
    (artifacts / "grill_gate.json").write_text(json.dumps(result, indent=2))
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Pulse pre-build Grill Gate")
    parser.add_argument("slug")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write report to build artifacts")
    args = parser.parse_args()

    result = analyze(args.slug)
    if args.write:
        path = write_report(args.slug, result)
        print(f"Report: {path}")
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_markdown(result))
    return 0 if result["recommendation"] != "do_not_start" else 2


if __name__ == "__main__":
    raise SystemExit(main())
