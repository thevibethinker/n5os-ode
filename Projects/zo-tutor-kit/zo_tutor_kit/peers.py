"""Peer registry utilities for the Zo Tutor Kit.

Phase 5A focuses on file-based peer registration via invite/accept
flows, without any live networking.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


PEERS_FILENAME = "peers.json"


def _get_repo_root() -> Path:
    # zo_tutor_kit/peers.py -> repo root is parent of this package
    return Path(__file__).resolve().parent.parent


def get_peers_path() -> Path:
    """Return the path to the peers registry JSON file."""

    return _get_repo_root() / PEERS_FILENAME


def load_peers() -> Dict[str, Any]:
    """Load the peers registry from disk.

    Returns an empty dict if the registry does not yet exist or is
    unreadable for any reason.
    """

    path = get_peers_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_peers(peers: Dict[str, Any]) -> None:
    """Persist the peers registry to disk as JSON."""

    path = get_peers_path()
    path.write_text(json.dumps(peers, indent=2, sort_keys=True), encoding="utf-8")

