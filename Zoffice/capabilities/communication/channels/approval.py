"""
Communication — Approval Gate

Autonomy-aware approval system. Reads autonomy.yaml thresholds
and always_escalate/never_escalate lists to decide whether an action
can proceed automatically.
"""

from pathlib import Path

import yaml

_AUTONOMY_CONFIG_PATH = str(
    Path(__file__).resolve().parents[3] / "config" / "autonomy.yaml"
)


def _load_autonomy_config(config_path: str | None = None) -> dict:
    path = config_path or _AUTONOMY_CONFIG_PATH
    with open(path) as f:
        return yaml.safe_load(f)


def check_approval(
    action: str,
    confidence: float,
    employee: str,
    autonomy_config_path: str | None = None,
) -> dict:
    """
    Check whether an action is approved based on autonomy config.

    Args:
        action: The action being attempted (e.g. "send_email", "respond_to_inquiry").
        confidence: Confidence score 0.0-1.0.
        employee: Employee slug requesting the action.
        autonomy_config_path: Override path to autonomy.yaml.

    Returns:
        ApprovalResult dict with keys: decision, reason.
        decision is one of: auto_act, act_and_notify, escalate_to_parent, escalate_to_human
    """
    cfg = _load_autonomy_config(autonomy_config_path)

    always_escalate = cfg.get("always_escalate", [])
    never_escalate = cfg.get("never_escalate", [])
    thresholds = cfg.get("thresholds", {})

    # Check always_escalate list first
    if action in always_escalate:
        return {
            "decision": "escalate_to_human",
            "reason": f"Action '{action}' is in always_escalate list",
        }

    # Check never_escalate list
    if action in never_escalate:
        return {
            "decision": "auto_act",
            "reason": f"Action '{action}' is in never_escalate list",
        }

    # Compare against thresholds
    auto_act = thresholds.get("auto_act", 0.9)
    act_and_notify = thresholds.get("act_and_notify", 0.7)
    escalate_to_parent = thresholds.get("escalate_to_parent", 0.5)

    if confidence >= auto_act:
        return {
            "decision": "auto_act",
            "reason": f"Confidence {confidence} >= auto_act threshold {auto_act}",
        }
    elif confidence >= act_and_notify:
        return {
            "decision": "act_and_notify",
            "reason": f"Confidence {confidence} >= act_and_notify threshold {act_and_notify}",
        }
    elif confidence >= escalate_to_parent:
        return {
            "decision": "escalate_to_parent",
            "reason": f"Confidence {confidence} >= escalate_to_parent threshold {escalate_to_parent}",
        }
    else:
        return {
            "decision": "escalate_to_human",
            "reason": f"Confidence {confidence} below all thresholds",
        }
