#!/usr/bin/env python3
"""Shared config loader for meeting-ingestion runtime.

Fail-closed by design for identity/org config:
- `config/me.yaml` must exist
- `config/orgs.yaml` must exist

Public export can ship only the `.template` files; live runtime must provide the
real configs locally.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
ME_CONFIG_PATH = CONFIG_DIR / "me.yaml"
ORGS_CONFIG_PATH = CONFIG_DIR / "orgs.yaml"
ME_TEMPLATE_PATH = CONFIG_DIR / "me.yaml.template"
ORGS_TEMPLATE_PATH = CONFIG_DIR / "orgs.yaml.template"


class ConfigMissingError(RuntimeError):
    pass


class ConfigInvalidError(RuntimeError):
    pass


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        template = None
        if path == ME_CONFIG_PATH:
            template = ME_TEMPLATE_PATH
        elif path == ORGS_CONFIG_PATH:
            template = ORGS_TEMPLATE_PATH
        hint = f" Create from template: {template.name}" if template and template.exists() else ""
        raise ConfigMissingError(f"Required config missing: {path}{hint}")
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ConfigInvalidError(f"Config must be a mapping: {path}")
    return data


@lru_cache(maxsize=1)
def load_me_config() -> Dict[str, Any]:
    data = _load_yaml(ME_CONFIG_PATH)
    identity = data.get("identity")
    if not isinstance(identity, dict):
        raise ConfigInvalidError(f"Missing identity section in {ME_CONFIG_PATH}")
    for key in ["canonical_short_name", "email_addresses", "exact_names", "unique_tokens"]:
        if key not in identity:
            raise ConfigInvalidError(f"Missing identity.{key} in {ME_CONFIG_PATH}")
    return data


@lru_cache(maxsize=1)
def load_orgs_config() -> Dict[str, Any]:
    data = _load_yaml(ORGS_CONFIG_PATH)
    for key in ["org_classification", "internal_identity", "staging"]:
        if key not in data:
            raise ConfigInvalidError(f"Missing {key} in {ORGS_CONFIG_PATH}")
    return data


__all__ = [
    "CONFIG_DIR",
    "ME_CONFIG_PATH",
    "ORGS_CONFIG_PATH",
    "ME_TEMPLATE_PATH",
    "ORGS_TEMPLATE_PATH",
    "ConfigMissingError",
    "ConfigInvalidError",
    "load_me_config",
    "load_orgs_config",
]
