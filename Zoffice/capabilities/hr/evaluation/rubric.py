"""
HR — Evaluation Rubric

Scenario-based employee evaluation framework.
Layer 1: placeholder scores. Layer 2: LLM-based evaluation.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml


def _load_scenarios(scenarios_path: str | None = None) -> list[dict]:
    if scenarios_path is None:
        scenarios_path = str(Path(__file__).resolve().parent / "scenarios.yaml")
    with open(scenarios_path) as f:
        data = yaml.safe_load(f)
    return data.get("scenarios", [])


def evaluate_scenario(
    employee: str,
    scenario_name: str,
    scenarios_path: str | None = None,
) -> dict:
    """
    Evaluate an employee against a single scenario.

    Layer 1: Returns placeholder score (0.7) with scenario structure.

    Returns:
        EvalResult dict: scenario_name, employee, score, strengths, improvements, timestamp
    """
    scenarios = _load_scenarios(scenarios_path)
    scenario = None
    for s in scenarios:
        if s["name"] == scenario_name:
            scenario = s
            break

    if scenario is None:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    # Layer 1: placeholder evaluation
    return {
        "scenario_name": scenario_name,
        "employee": employee,
        "score": 0.7,  # Placeholder — Layer 2 uses LLM evaluation
        "strengths": [f"Handles '{scenario_name}' scenario structure"],
        "improvements": ["Pending real LLM evaluation in Layer 2"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input": scenario.get("input"),
        "expected_behavior": scenario.get("expected_behavior"),
    }


def run_full_evaluation(
    employee: str,
    scenarios_path: str | None = None,
) -> list[dict]:
    """Run all applicable scenarios for an employee."""
    scenarios = _load_scenarios(scenarios_path)
    results = []
    for s in scenarios:
        applicable = s.get("applicable_to", [])
        if not applicable or employee in applicable:
            results.append(evaluate_scenario(employee, s["name"], scenarios_path))
    return results


def save_evaluation(eval_results: list[dict], employee: str) -> str:
    """Save evaluation results to the evaluations table in office.db."""
    eval_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    overall = sum(r["score"] for r in eval_results) / len(eval_results) if eval_results else 0.0
    strengths = "; ".join(s for r in eval_results for s in r.get("strengths", []))
    improvements = "; ".join(s for r in eval_results for s in r.get("improvements", []))

    try:
        from Zoffice.capabilities.memory.db_helpers import get_db
        conn = get_db()
        conn.execute(
            """INSERT INTO evaluations (id, employee, evaluated_at, scenario_scores,
                                        overall_score, strengths, improvements, evaluator)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [eval_id, employee, now,
             json.dumps([{"name": r["scenario_name"], "score": r["score"]} for r in eval_results]),
             overall, strengths, improvements, "rubric-v1"],
        )
    except Exception:
        pass

    # Audit log
    try:
        from Zoffice.capabilities.security.audit.writer import log_audit
        log_audit(
            capability="hr",
            employee=employee,
            action="evaluation_saved",
            metadata={"eval_id": eval_id, "overall_score": overall, "scenario_count": len(eval_results)},
        )
    except Exception:
        pass

    return eval_id
