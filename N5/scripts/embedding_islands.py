#!/usr/bin/env python3
"""Embedding Islands Inventory + Quarantine + (Gated) Deletion.

Goal: make brain.db (N5/cognition/brain.db) the ONLY embedding/vector store.

This script is intentionally conservative:
- Default is dry-run.
- Quarantine moves require --execute.
- Permanent deletion is NOT performed by default; deletion requires:
  1) Quarantine already done
  2) Item age >= 7 days
  3) Explicit token via --approve

Outputs (deterministic, versionable):
- Inventory: N5/data/embedding_islands_inventory.json
- Deletion manifest: N5/data/embedding_islands_deletion_manifest.json

Note: This script does *not* decide what is "valuable"; it inventories and
creates reversible plans. Migration into brain.db is handled by dedicated
migrators (e.g., migrate_positions_to_brain.py).
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKSPACE = Path("/home/workspace")
N5 = WORKSPACE / "N5"
DATA_DIR = N5 / "data"

BRAIN_DB = N5 / "cognition" / "brain.db"

INVENTORY_PATH = DATA_DIR / "embedding_islands_inventory.json"
DELETION_MANIFEST_PATH = DATA_DIR / "embedding_islands_deletion_manifest.json"

QUARANTINE_ROOT = N5 / "quarantine" / "embedding_islands"

DEFAULT_QUARANTINE_DAYS = 7


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _n5_protect_check(path: Path) -> dict:
    """Call the canonical protection checker. Returns parsed JSON if possible."""
    cmd = ["python3", str(WORKSPACE / "N5/scripts/n5_protect.py"), "check", str(path)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # n5_protect prints human text; we preserve it.
        return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e:
        return {"returncode": 2, "stdout": "", "stderr": str(e)}


@dataclass
class EmbeddingIsland:
    path: str
    kind: str  # e.g., sqlite-db, file
    reason: str
    size_bytes: int


def discover_islands() -> list[EmbeddingIsland]:
    """Discover known embedding islands.

    For now this is intentionally explicit (avoid noisy false positives).
    Extend as new islands are identified.
    """
    islands: list[EmbeddingIsland] = []

    # Positions DB contains an embedding column historically; embeddings now canonical in brain.db
    positions_db = N5 / "data" / "positions.db"
    if positions_db.exists() and positions_db != BRAIN_DB:
        islands.append(
            EmbeddingIsland(
                path=str(positions_db),
                kind="sqlite-db",
                reason="Historical embedding column in positions table (now migrated/unused)",
                size_bytes=positions_db.stat().st_size,
            )
        )

    # Legacy/duplicate memory client implementation (code-level island; no embeddings stored here)
    legacy_client = N5 / "lib" / "n5_memory_client.py"
    if legacy_client.exists():
        islands.append(
            EmbeddingIsland(
                path=str(legacy_client),
                kind="code",
                reason="Legacy memory client implementation; canonical is N5/cognition/n5_memory_client.py",
                size_bytes=legacy_client.stat().st_size,
            )
        )

    return islands


def cmd_inventory(_: argparse.Namespace) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    islands = discover_islands()
    payload = {
        "generated_at": _utc_now(),
        "brain_db": str(BRAIN_DB),
        "items": [asdict(i) for i in islands],
    }
    INVENTORY_PATH.write_text(json.dumps(payload, indent=2))
    print(str(INVENTORY_PATH))


def cmd_prepare(args: argparse.Namespace) -> None:
    if not INVENTORY_PATH.exists():
        raise SystemExit(f"Inventory missing: {INVENTORY_PATH}. Run inventory first.")

    inv = json.loads(INVENTORY_PATH.read_text())
    items = inv.get("items", [])

    manifest_items = []
    for item in items:
        p = Path(item["path"])
        if not p.exists():
            continue
        protect = _n5_protect_check(p)
        manifest_items.append(
            {
                **item,
                "sha256": _sha256(p) if p.is_file() else None,
                "protected_check": protect,
            }
        )

    payload = {
        "generated_at": _utc_now(),
        "quarantine_days": DEFAULT_QUARANTINE_DAYS,
        "items": manifest_items,
    }
    DELETION_MANIFEST_PATH.write_text(json.dumps(payload, indent=2))
    print(str(DELETION_MANIFEST_PATH))


def cmd_quarantine(args: argparse.Namespace) -> None:
    if not DELETION_MANIFEST_PATH.exists():
        raise SystemExit(f"Deletion manifest missing: {DELETION_MANIFEST_PATH}. Run prepare first.")

    manifest = json.loads(DELETION_MANIFEST_PATH.read_text())
    items = manifest.get("items", [])

    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = QUARANTINE_ROOT / ts

    planned = []
    for it in items:
        p = Path(it["path"])
        if not p.exists():
            continue

        planned.append({"from": str(p), "to": str(run_dir / p.name), "reason": it.get("reason")})

    if not args.execute:
        print(json.dumps({"mode": "dry-run", "planned": planned}, indent=2))
        return

    run_dir.mkdir(parents=True, exist_ok=True)

    # Execute moves
    moved = []
    for move in planned:
        src = Path(move["from"])
        dst = Path(move["to"])

        protect = _n5_protect_check(src)
        if protect.get("returncode") != 0:
            raise SystemExit(f"Refusing to quarantine protected path: {src}\n{protect.get('stdout')}\n{protect.get('stderr')}")

        shutil.move(str(src), str(dst))
        moved.append(move)

    (run_dir / "quarantine_manifest.json").write_text(
        json.dumps({"quarantined_at": _utc_now(), "items": moved}, indent=2)
    )
    print(str(run_dir))


def cmd_purge(args: argparse.Namespace) -> None:
    if not QUARANTINE_ROOT.exists():
        raise SystemExit(f"No quarantine root: {QUARANTINE_ROOT}")

    approve = args.approve or ""
    required_token = "I_APPROVE_PERMANENT_DELETION"
    if approve != required_token:
        raise SystemExit(
            f"Refusing to purge without explicit approval token.\n"
            f"Pass: --approve {required_token}"
        )

    cutoff = datetime.now(timezone.utc) - timedelta(days=DEFAULT_QUARANTINE_DAYS)

    candidates = []
    for run_dir in sorted(QUARANTINE_ROOT.glob("*")):
        if not run_dir.is_dir():
            continue
        try:
            dt = datetime.strptime(run_dir.name, "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if dt <= cutoff:
            candidates.append(run_dir)

    if not args.execute:
        print(json.dumps({"mode": "dry-run", "eligible_runs": [str(c) for c in candidates]}, indent=2))
        return

    for run_dir in candidates:
        shutil.rmtree(run_dir)

    print(json.dumps({"purged": [str(c) for c in candidates], "purged_at": _utc_now()}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_inv = sub.add_parser("inventory")
    p_inv.set_defaults(func=cmd_inventory)

    p_prep = sub.add_parser("prepare")
    p_prep.set_defaults(func=cmd_prepare)

    p_quar = sub.add_parser("quarantine")
    p_quar.add_argument("--execute", action="store_true")
    p_quar.set_defaults(func=cmd_quarantine)

    p_purge = sub.add_parser("purge")
    p_purge.add_argument("--approve", type=str, default="")
    p_purge.add_argument("--execute", action="store_true")
    p_purge.set_defaults(func=cmd_purge)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

