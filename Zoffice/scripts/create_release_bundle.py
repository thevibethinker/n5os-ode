#!/usr/bin/env python3
"""Create a versioned release bundle for manual substrate pull."""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

EXCLUDES = {
    "__pycache__",
    ".git",
    "office.db-wal",
    "office.db-shm",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(root: Path, version: str, out_dir: Path) -> dict:
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDES for part in p.parts):
            continue
        rel = p.relative_to(root)
        if rel.parts[:2] == ("releases", version):
            continue
        files.append({
            "path": str(rel),
            "size": p.stat().st_size,
            "sha256": sha256_file(p),
        })

    return {
        "product": "Zoffice",
        "release_version": version,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "files": files,
        "acceptance_gate": "zoputer reports 100% integrity rebuild",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Zoffice release bundle")
    parser.add_argument("--version", default="v2.0.0-rc1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path("/home/workspace/Zoffice")
    release_dir = root / "releases" / args.version
    bundle_path = release_dir / f"zoffice-{args.version}.tar.gz"
    manifest_path = release_dir / "bundle-manifest.json"

    manifest = build_manifest(root, args.version, release_dir)

    if args.dry_run:
        print(json.dumps({"release_dir": str(release_dir), "file_count": manifest["file_count"]}, indent=2))
        return

    release_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with tarfile.open(bundle_path, "w:gz") as tar:
        tar.add(root, arcname="Zoffice", filter=lambda i: None if any(part in EXCLUDES for part in Path(i.name).parts) else i)

    checksum = sha256_file(bundle_path)
    (release_dir / "bundle.sha256").write_text(f"{checksum}  {bundle_path.name}\n", encoding="utf-8")

    print(json.dumps({
        "release_dir": str(release_dir),
        "bundle": str(bundle_path),
        "bundle_sha256": checksum,
        "manifest": str(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
