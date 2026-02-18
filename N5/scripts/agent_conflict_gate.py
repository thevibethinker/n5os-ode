#!/usr/bin/env python3
"""Agent Conflict Gate

Checks scheduled agents for duplication, stale agents, dense time windows, and shared delivery targets.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set

import requests

LOG_PATH = "/home/workspace/N5/logs/agent_conflict_gate.log"
API_KEY_ENV = "ZO_CLIENT_IDENTITY_TOKEN"


@dataclass
class Conflict:
    conflict_type: str
    agents: List[str]
    reason: str
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


class AgentConflictGateError(Exception):
    """Raised when the gate fails to load inventory or detect fatal errors."""


def fetch_agents() -> List[dict]:
    token = os.environ.get(API_KEY_ENV)
    if not token:
        raise AgentConflictGateError(f"Missing environment variable {API_KEY_ENV}")

    response = requests.post(
        "https://api.zo.computer/zo/ask",
        headers={
            "authorization": token,
            "content-type": "application/json",
        },
        json={
            "input": textwrap.dedent(
                """
                List all scheduled agents and return ONLY raw JSON array.
                Use list_agents tool and return the exact output, nothing else.
                """
            ).strip(),
            "output_format": {
                "type": "object",
                "properties": {
                    "agents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "instruction": {"type": "string"},
                                "active": {"type": "boolean"},
                                "next_run": {"type": "string"},
                                "result_delivery_method": {"type": "string"},
                                "delivery_target": {"type": "string"},
                                "delivery_address": {"type": "string"},
                            },
                            "required": ["id"],
                        },
                    }
                },
                "required": ["agents"],
            },
        },
        timeout=90,
    )
    response.raise_for_status()
    payload = response.json()
    output = payload.get("output", {})
    agents = output.get("agents")
    if not isinstance(agents, list):
        raise AgentConflictGateError("Unexpected response while fetching agents")
    return agents


def load_agents_from_file(path: str) -> List[dict]:
    with open(path, "r") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        agents = data.get("agents")
        if isinstance(agents, list):
            return agents
    raise AgentConflictGateError(f"Invalid JSON format in {path}")


def normalize_title(title: Optional[str]) -> str:
    return (title or "").strip().lower()


def safe_instruction(agent: dict) -> str:
    return (agent.get("instruction") or "")


def title_similarity(agent_a: dict, agent_b: dict) -> bool:
    return normalize_title(agent_a.get("title")) == normalize_title(agent_b.get("title"))


def instruction_overlap(agent_a: dict, agent_b: dict) -> bool:
    inst_a = safe_instruction(agent_a).strip()
    inst_b = safe_instruction(agent_b).strip()
    return bool(inst_a and inst_b and inst_a == inst_b)


def api_overlap(agent: dict, other: dict) -> Optional[str]:
    apis = ["fitbit", "gmail", "calendar", "drive"]
    hits = [api for api in apis if api in safe_instruction(agent).lower()]
    other_hits = [api for api in apis if api in safe_instruction(other).lower()]
    shared = set(hits) & set(other_hits)
    if shared:
        return ",".join(sorted(shared))
    return None


def extract_script_paths(agent: dict) -> Set[str]:
    inst = safe_instruction(agent)
    candidates: Set[str] = set()
    for token in inst.replace("`", "").split():
        if token.startswith("/home/") and any(token.endswith(ext) for ext in (".py", ".sh", ".ts", ".cmd")):
            candidates.add(token)
    return candidates


def commands_overlap(agent: dict, other: dict) -> bool:
    return bool(extract_script_paths(agent) & extract_script_paths(other))


def delivery_target(agent: dict) -> tuple[str, str]:
    method = agent.get("result_delivery_method") or "none"
    destination = agent.get("delivery_target") or agent.get("delivery_address") or ""
    return method, destination


def parse_timeslot(agent: dict) -> Optional[int]:
    next_run = agent.get("next_run")
    if not next_run:
        return None
    try:
        dt = datetime.fromisoformat(next_run.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt.hour


def build_conflicts(agents: List[dict]) -> List[Conflict]:
    conflicts: List[Conflict] = []
    delivery_groups: dict[str, List[dict]] = {}
    timeslot_counts: dict[int, List[str]] = {}

    for agent in agents:
        agent_id = agent.get("id")
        if not agent_id:
            continue

        if agent.get("active") and agent.get("next_run") is None:
            conflicts.append(
                Conflict(
                    conflict_type="stale_zombie",
                    agents=[agent_id],
                    reason="Active agent lacks next_run",
                    confidence=0.75,
                )
            )

        method, destination = delivery_target(agent)
        if method != "none" and destination:
            key = f"{method}:{destination}"
            delivery_groups.setdefault(key, []).append(agent)

        hour = parse_timeslot(agent)
        if hour is not None:
            timeslot_counts.setdefault(hour, []).append(agent_id)

    for target, group in delivery_groups.items():
        if len(group) > 1:
            conflicts.append(
                Conflict(
                    conflict_type="delivery_overlap",
                    agents=[agent.get("id") for agent in group if agent.get("id")],
                    reason=f"Shared delivery channel {target}",
                    confidence=0.55,
                )
            )

    for hour, agent_ids in timeslot_counts.items():
        if len(agent_ids) >= 3:
            conflicts.append(
                Conflict(
                    conflict_type="time_slot_density",
                    agents=agent_ids,
                    reason=f"{len(agent_ids)} agents scheduled in hour {hour}",
                    confidence=0.45,
                )
            )

    for idx, agent in enumerate(agents):
        for other in agents[idx + 1 :]:
            agent_id = agent.get("id")
            other_id = other.get("id")
            if not agent_id or not other_id:
                continue

            if title_similarity(agent, other):
                conflicts.append(
                    Conflict(
                        conflict_type="title_duplicate",
                        agents=[agent_id, other_id],
                        reason="Identical titles",
                        confidence=0.6,
                    )
                )

            if instruction_overlap(agent, other):
                conflicts.append(
                    Conflict(
                        conflict_type="instruction_overlap",
                        agents=[agent_id, other_id],
                        reason="Shared instruction text",
                        confidence=0.6,
                    )
                )

            shared = api_overlap(agent, other)
            if shared:
                conflicts.append(
                    Conflict(
                        conflict_type="api_dependency_overlap",
                        agents=[agent_id, other_id],
                        reason=f"Shared APIs: {shared}",
                        confidence=0.55,
                    )
                )

            if commands_overlap(agent, other):
                conflicts.append(
                    Conflict(
                        conflict_type="command_shared",
                        agents=[agent_id, other_id],
                        reason="Same scripts/commands referenced",
                        confidence=0.5,
                    )
                )

    return conflicts


def emit_output(conflicts: List[Conflict], summary: bool) -> None:
    payload = {"conflicts": [conflict.to_dict() for conflict in conflicts]}
    if summary:
        print("Agent Conflict Gate Summary:")
        if not conflicts:
            print("  No conflicts detected.")
        for conflict in payload["conflicts"]:
            print(f" - {conflict['conflict_type']}: {conflict['reason']}\n   Agents: {', '.join(conflict['agents'])}")
    print(json.dumps(payload, indent=2))


def append_log(exit_code: int, conflicts: List[Conflict]) -> None:
    prefix = f"{datetime.now(timezone.utc).isoformat()} | exit={exit_code}"
    if conflicts:
        types = ",".join({conflict.conflict_type for conflict in conflicts})
        entry = f"{prefix} | conflicts={len(conflicts)} | types={types}\n"
    else:
        entry = f"{prefix} | conflicts=0\n"
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as handle:
        handle.write(entry)
    if not Path(LOG_PATH).exists():
        raise AgentConflictGateError(f"Failed to write to log file: {LOG_PATH}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agent Conflict Gate (inventory + heuristics)")
    parser.add_argument("--dry-run", action="store_true", help="Report conflicts without blocking")
    parser.add_argument("--summary", action="store_true", help="Print human-friendly summary")
    parser.add_argument("--check-log", action="store_true", help="Append result to gate log")
    parser.add_argument("--force", action="store_true", help="Exit 0 even if conflicts exist")
    parser.add_argument("--agents-json", type=str, help="Read agents from a JSON file instead of live API")
    parser.add_argument("--save-snapshot", type=str, help="Fetch live agents and save to this JSON path")
    parser.add_argument("--no-cache", action="store_true", help="Ignored (kept for backward compatibility)")
    return parser.parse_args()


def save_agents_to_file(path: str, agents: List[dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as handle:
        json.dump(agents, handle, indent=2)


def main() -> int:
    args = parse_args()

    try:
        if args.agents_json:
            agents = load_agents_from_file(args.agents_json)
        else:
            agents = fetch_agents()

        if args.save_snapshot:
            save_agents_to_file(args.save_snapshot, agents)

        conflicts = build_conflicts(agents)
        emit_output(conflicts, args.summary)
        if args.check_log:
            append_log(exit_code=1 if conflicts else 0, conflicts=conflicts)

        if conflicts and not args.dry_run and not args.force:
            return 1
        return 0
    except AgentConflictGateError as exc:
        print(f"Conflict Gate Error: {exc}", file=sys.stderr)
        if args.check_log:
            append_log(exit_code=2, conflicts=[])
        return 2
    except Exception as exc:
        print(f"fatal: {exc}", file=sys.stderr)
        if args.check_log:
            append_log(exit_code=2, conflicts=[])
        return 2


if __name__ == "__main__":
    sys.exit(main())
