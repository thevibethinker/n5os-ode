import argparse

#!/usr/bin/env python3
"""
N5 OS Config Merge Utility

Merges configuration layers with precedence: Task > Project > Workflow > Global.
Rules:
- Scalars: last-wins (highest precedence).
- Maps: deep-merge.
- Lists: union for {tags, excludes}; replace otherwise.
- Sticky safety: dry_run and require_auth stay True if set in any layer.

Returns merged dict and explain string.
"""

from typing import Dict, List, Tuple, Any, Union


def merge_configs(layers: List[Tuple[str, Dict[str, Any]]]) -> Tuple[Dict[str, Any], str]:
    """
    Merge config layers.

    Args:
        layers: List of (name, config_dict) tuples in order: global, workflow, project, task.

    Returns:
        (merged_config, explain_string)
    """
    merged = {}
    sources = {}  # key -> source or list for union
    sticky_keys = {'dry_run', 'require_auth'}
    sticky_set = {k: False for k in sticky_keys}

    for name, layer in layers:
        for key, value in layer.items():
            if key in sticky_keys:
                if value is True:
                    if not sticky_set[key]:
                        sticky_set[key] = True
                        merged[key] = True
                        sources[key] = f"{name}(sticky)"
                elif not sticky_set[key]:
                    merged[key] = value
                    sources[key] = name
            else:
                if isinstance(value, dict):
                    # deep merge
                    if key not in merged:
                        merged[key] = {}
                    elif not isinstance(merged[key], dict):
                        merged[key] = {}
                    _deep_merge(merged[key], value)
                    if key not in sources:
                        sources[key] = name
                    # For deep, keep top level source
                elif isinstance(value, list):
                    if key in ('tags', 'excludes'):
                        # union
                        if key not in merged:
                            merged[key] = []
                        elif not isinstance(merged[key], list):
                            merged[key] = []
                        existing = set(merged[key])
                        new = set(value)
                        merged[key] = list(existing | new)
                        merged[key].sort()
                        if key not in sources:
                            sources[key] = [name]
                        elif isinstance(sources[key], list):
                            if name not in sources[key]:
                                sources[key].append(name)
                        else:
                            if sources[key] != name:
                                sources[key] = [sources[key], name]
                    else:
                        merged[key] = value[:]
                        sources[key] = name
                else:
                    merged[key] = value
                    sources[key] = name

    # Build explain
    explain_parts = []
    for key in sorted(sources.keys()):
        src = sources[key]
        if isinstance(src, list):
            explain_parts.append(f"{key}=union({','.join(sorted(src))})")
        else:
            explain_parts.append(f"{key}={src}")
    explain = "Config → " + "; ".join(explain_parts) + "."
    return merged, explain


def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]):
    """Deep merge source into target."""
    for k, v in source.items():
        if isinstance(v, dict) and k in target and isinstance(target[k], dict):
            _deep_merge(target[k], v)
        else:
            target[k] = v


# Test cases
def run_tests():
    test_cases = [
        # Basic scalar override
        {
            "layers": [
                ("global", {"output_dir": "global_dir", "tone": "neutral"}),
                ("workflow", {"tone": "formal"}),
                ("project", {}),
                ("task", {"output_dir": "task_dir"})
            ],
            "expected_merged": {"output_dir": "task_dir", "tone": "formal"},
            "expected_explain": "Config → output_dir=task; tone=workflow."
        },
        # Sticky dry_run
        {
            "layers": [
                ("global", {"dry_run": True}),
                ("workflow", {}),
                ("project", {"dry_run": False}),
                ("task", {})
            ],
            "expected_merged": {"dry_run": True},
            "expected_explain": "Config → dry_run=global(sticky)."
        },
        # Union tags
        {
            "layers": [
                ("global", {"tags": ["global1", "shared"]}),
                ("workflow", {}),
                ("project", {"tags": ["project1", "shared"]}),
                ("task", {})
            ],
            "expected_merged": {"tags": ["global1", "project1", "shared"]},
            "expected_explain": "Config → tags=union(global,project)."
        },
        # Deep merge maps
        {
            "layers": [
                ("global", {"writing": {"style": "concise"}}),
                ("workflow", {"writing": {"tone": "professional"}}),
                ("project", {}),
                ("task", {})
            ],
            "expected_merged": {"writing": {"style": "concise", "tone": "professional"}},
            "expected_explain": "Config → writing=global."
        },
        # Empty layers
        {
            "layers": [
                ("global", {}),
                ("workflow", {}),
                ("project", {}),
                ("task", {"key": "value"})
            ],
            "expected_merged": {"key": "value"},
            "expected_explain": "Config → key=task."
        }
    ]

    for i, case in enumerate(test_cases):
        merged, explain = merge_configs(case["layers"])
        if merged == case["expected_merged"] and explain == case["expected_explain"]:
            print(f"Test {i+1}: PASS")
        else:
            print(f"Test {i+1}: FAIL")
            print(f"  Merged: {merged}")
            print(f"  Expected: {case['expected_merged']}")
            print(f"  Explain: {explain}")
            print(f"  Expected: {case['expected_explain']}")


if __name__ == "__main__":
    run_tests()