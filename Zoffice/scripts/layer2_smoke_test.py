#!/usr/bin/env python3
"""Layer 2 smoke checks for local config/state integrity."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_yaml(path: Path) -> dict:
    with path.open() as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML mapping: {path}")
    return data


def main() -> None:
    root = Path("/home/workspace/Zoffice")
    manifest = json.loads((root / "MANIFEST.json").read_text())
    integration = load_yaml(root / "config" / "integration.yaml")
    security = load_yaml(root / "config" / "security.yaml")
    zo2zo = load_yaml(root / "capabilities" / "zo2zo" / "config.yaml")

    assert manifest["version"] == "v2.0.0-rc1"
    assert manifest["layer"] == 2

    for k in ["voice", "email", "scheduling", "zo2zo", "webhooks", "publishing"]:
        assert integration["integrations"][k]["status"] == "active", f"integration {k} not active"

    trusted = security["security"]["trust"]["trusted_instances"]
    assert "va.zo.computer" in trusted
    assert zo2zo["parent_instance"] == "va.zo.computer"

    contract = root / "contracts" / "mutual-acceptance-v2.0.0-rc1.json"
    assert contract.exists(), "acceptance contract missing"

    print(json.dumps({
        "status": "pass",
        "version": manifest["version"],
        "layer": manifest["layer"],
        "trusted_instances": trusted,
        "contract": str(contract),
    }, indent=2))


if __name__ == "__main__":
    main()
