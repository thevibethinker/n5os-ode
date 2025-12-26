#!/usr/bin/env python3
"""Smoke test for capability_registry_update.

This does NOT run automatically. When executed manually, it:
- Writes a temporary spec for a test capability under N5/capabilities/internal/
- Invokes capability_registry_update.apply_capability_update() directly
- Prints whether the capability file and index entry exist

It leaves the test capability in place so you can inspect the result.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from capability_registry_update import apply_capability_update, CAP_ROOT, INDEX_PATH


def main() -> None:
    workspace_root = Path("/home/workspace")
    n5_root = workspace_root / "N5"

    spec = {
        "capability_update": {
            "capability_id": "test-capability-registry-update",
            "name": "TEST – Capability Registry Update Helper",
            "category": "internal",
            "status": "experimental",
            "confidence": "low",
            "tags": ["test", "registry"],
            "entry_points": [],
            "description": "Test-only capability used to validate capability_registry_update mechanics.",
            "change_type": "new",
        }
    }

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.safe_dump(spec, f)
        spec_path = Path(f.name)

    print(f"Using spec file: {spec_path}")

    apply_capability_update(spec_path)

    cap_file = CAP_ROOT / "internal" / "test-capability-registry-update.md"
    print(f"Capability file exists: {cap_file.exists()} ({cap_file})")

    idx_lines = INDEX_PATH.read_text(encoding="utf-8").splitlines()
    marker = "N5/capabilities/internal/test-capability-registry-update.md"
    in_index = any(marker in line for line in idx_lines)
    print(f"Index entry present: {in_index} (marker: {marker})")

    print("Smoke test complete. Inspect the test capability and index entry manually.")


if __name__ == "__main__":  # pragma: no cover
    main()

