#!/usr/bin/env python3
"""
N5OS Ode Export Pipeline — Sync designated live workspace files to the n5os-ode repo.

Usage:
  python3 Skills/ode-export/scripts/export.py --dry-run          # Preview changes
  python3 Skills/ode-export/scripts/export.py                    # Export changed files
  python3 Skills/ode-export/scripts/export.py --init             # First-time bulk sync
  python3 Skills/ode-export/scripts/export.py --diff             # Drift report only
  python3 Skills/ode-export/scripts/export.py --test             # Export + smoke test
  python3 Skills/ode-export/scripts/export.py --threshold 0      # Include trivial drifts
  python3 Skills/ode-export/scripts/export.py --force            # Ignore threshold
"""

import argparse
import datetime
import glob as globmod
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ode-export")

WORKSPACE = Path("/home/workspace")
SKILL_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SKILL_DIR / "ode_manifest.yaml"


def load_manifest() -> dict:
    """Load and validate the export manifest."""
    if not MANIFEST_PATH.exists():
        log.error(f"Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        manifest = yaml.safe_load(f)
    if not manifest.get("exports"):
        log.error("Manifest has no 'exports' section")
        sys.exit(1)
    return manifest


def resolve_file_list(manifest: dict) -> list[tuple[Path, Path]]:
    """Resolve manifest groups into (live_path, repo_relative_path) pairs."""
    pairs = []
    exports = manifest["exports"]
    for group_name, group in exports.items():
        source = group.get("source", "")
        live_dir = WORKSPACE / source if source else WORKSPACE

        if "files" in group:
            for f in group["files"]:
                live_path = live_dir / f
                repo_rel = Path(source) / f if source else Path(f)
                pairs.append((live_path, repo_rel))

        if "glob" in group:
            pattern = group["glob"]
            for match in sorted(live_dir.glob(pattern)):
                if match.is_file():
                    repo_rel = Path(source) / match.name if source else Path(match.name)
                    if (match, repo_rel) not in pairs:
                        pairs.append((match, repo_rel))

        if "extra" in group:
            for f in group["extra"]:
                live_path = live_dir / f
                repo_rel = Path(source) / f if source else Path(f)
                if (live_path, repo_rel) not in pairs:
                    pairs.append((live_path, repo_rel))

    return pairs


def file_hash(path: Path) -> Optional[str]:
    """SHA-256 hash of file contents."""
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_pii(content: str, patterns: list[str]) -> list[str]:
    """Check content for PII patterns. Returns list of matched patterns."""
    hits = []
    for pat in patterns:
        if re.search(pat, content, re.IGNORECASE):
            hits.append(pat)
    return hits


def sanitize_content(content: str, sanitize_patterns: dict[str, str]) -> str:
    """Apply sanitize patterns (find→replace) to content."""
    for pattern, replacement in sanitize_patterns.items():
        content = re.sub(pattern, replacement, content)
    return content


def compare_files(
    pairs: list[tuple[Path, Path]],
    repo_path: Path,
    threshold: int,
    force: bool,
) -> dict:
    """Compare live vs repo files. Returns categorized results."""
    results = {
        "changed": [],
        "trivial": [],
        "missing_live": [],
        "missing_repo": [],
        "identical": [],
    }

    for live_path, repo_rel in pairs:
        repo_file = repo_path / repo_rel

        if not live_path.exists():
            results["missing_live"].append((live_path, repo_rel))
            continue

        if not repo_file.exists():
            results["missing_repo"].append((live_path, repo_rel))
            continue

        live_h = file_hash(live_path)
        repo_h = file_hash(repo_file)

        if live_h == repo_h:
            results["identical"].append((live_path, repo_rel))
            continue

        try:
            live_size = len(live_path.read_text(errors="ignore"))
            repo_size = len(repo_file.read_text(errors="ignore"))
            delta = abs(live_size - repo_size)
        except Exception:
            delta = threshold + 1

        if delta < threshold and not force:
            results["trivial"].append((live_path, repo_rel, delta))
        else:
            results["changed"].append((live_path, repo_rel, delta))

    return results


def check_repo_managed_staleness(manifest: dict, repo_path: Path, days: int = 60) -> list[dict]:
    """Check repo-managed files for staleness."""
    stale = []
    cutoff = datetime.datetime.now().timestamp() - (days * 86400)
    repo_managed = manifest.get("repo_managed", [])

    for entry in repo_managed:
        path = repo_path / entry["path"]
        if path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    mtime = f.stat().st_mtime
                    if mtime < cutoff:
                        age_days = int((datetime.datetime.now().timestamp() - mtime) / 86400)
                        stale.append({
                            "path": str(f.relative_to(repo_path)),
                            "age_days": age_days,
                            "note": entry.get("note", ""),
                        })
        elif path.is_file():
            mtime = path.stat().st_mtime
            if mtime < cutoff:
                age_days = int((datetime.datetime.now().timestamp() - mtime) / 86400)
                stale.append({
                    "path": str(path.relative_to(repo_path)),
                    "age_days": age_days,
                    "note": entry.get("note", ""),
                })

    return stale


def run_pii_gate(pairs_to_sync: list[tuple[Path, Path]], pii_patterns: list[str]) -> tuple[list, list]:
    """Run PII gate on files about to be synced. Returns (clean, blocked)."""
    clean = []
    blocked = []

    for entry in pairs_to_sync:
        live_path = entry[0]
        repo_rel = entry[1]

        try:
            content = live_path.read_text(errors="ignore")
        except Exception:
            clean.append(entry)
            continue

        hits = check_pii(content, pii_patterns)
        if hits:
            blocked.append((live_path, repo_rel, hits))
        else:
            clean.append(entry)

    return clean, blocked


def do_export(clean_files: list, repo_path: Path, dry_run: bool, sanitize_patterns: dict[str, str] | None = None) -> int:
    """Copy clean files from live to repo. Returns count of files written."""
    count = 0
    for entry in clean_files:
        live_path = entry[0]
        repo_rel = entry[1]
        dest = repo_path / repo_rel

        if dry_run:
            log.info(f"  [DRY-RUN] Would copy {repo_rel}")
            count += 1
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        if sanitize_patterns:
            try:
                content = live_path.read_text(errors="ignore")
                content = sanitize_content(content, sanitize_patterns)
                dest.write_text(content)
            except Exception:
                shutil.copy2(str(live_path), str(dest))
        else:
            shutil.copy2(str(live_path), str(dest))

        count += 1
        log.info(f"  ✓ {repo_rel}")

    return count


def run_validate(repo_path: Path) -> bool:
    """Run validate_repo.py on the repo."""
    validator = repo_path / "N5" / "scripts" / "validate_repo.py"
    if not validator.exists():
        log.warning("validate_repo.py not found in repo, skipping validation")
        return True

    result = subprocess.run(
        [sys.executable, str(validator)],
        capture_output=True,
        text=True,
        cwd=str(repo_path),
    )
    if "All checks passed" in result.stdout:
        log.info("✅ Validation passed")
        return True
    else:
        log.warning(f"⚠ Validation issues:\n{result.stdout}")
        return False


def run_smoke_test(repo_path: Path) -> bool:
    """Run install.sh in a temp directory to verify it works."""
    with tempfile.TemporaryDirectory(prefix="ode-test-") as tmpdir:
        test_workspace = Path(tmpdir) / "workspace"
        test_workspace.mkdir()
        test_repo = test_workspace / "n5os-ode"

        shutil.copytree(str(repo_path), str(test_repo), ignore=shutil.ignore_patterns(".git"))

        install_sh = test_repo / "install.sh"
        if not install_sh.exists():
            log.warning("install.sh not found, skipping smoke test")
            return True

        result = subprocess.run(
            ["bash", str(install_sh)],
            capture_output=True,
            text=True,
            cwd=str(test_repo),
            env={**os.environ, "HOME": tmpdir, "WORKSPACE": str(test_workspace)},
        )

        if result.returncode == 0:
            installed_n5 = test_workspace / "N5"
            installed_skills = test_workspace / "Skills"
            bootloader = test_workspace / "BOOTLOADER.prompt.md"

            checks = [
                ("N5/ directory", installed_n5.is_dir()),
                ("Skills/ directory", installed_skills.is_dir()),
                ("BOOTLOADER.prompt.md", bootloader.exists()),
            ]

            all_pass = all(ok for _, ok in checks)
            for name, ok in checks:
                status = "✓" if ok else "✗"
                log.info(f"  {status} {name}")

            if all_pass:
                log.info("✅ Smoke test passed")
            else:
                log.warning("⚠ Smoke test: some checks failed")
            return all_pass
        else:
            log.error(f"✗ install.sh failed (exit {result.returncode})")
            log.error(f"  stderr: {result.stderr[:500]}")
            return False


def print_drift_report(results: dict, stale: list, blocked: list) -> None:
    """Print a formatted drift report."""
    print("\n" + "=" * 60)
    print("N5OS Ode Drift Report")
    print("=" * 60)

    if results["changed"]:
        print(f"\n📝 Changed ({len(results['changed'])} files):")
        for live, rel, delta in sorted(results["changed"], key=lambda x: -x[2]):
            print(f"  {rel} (+{delta} chars)")

    if results["missing_repo"]:
        print(f"\n🆕 New in live, missing from repo ({len(results['missing_repo'])} files):")
        for live, rel in results["missing_repo"]:
            print(f"  {rel}")

    if results["trivial"]:
        print(f"\n⏭ Trivial drift, skipped ({len(results['trivial'])} files):")
        for live, rel, delta in results["trivial"]:
            print(f"  {rel} ({delta} chars)")

    if results["missing_live"]:
        print(f"\n⚠ In manifest but missing from live ({len(results['missing_live'])} files):")
        for live, rel in results["missing_live"]:
            print(f"  {rel}")

    if blocked:
        print(f"\n🚫 PII blocked ({len(blocked)} files):")
        for live, rel, hits in blocked:
            print(f"  {rel} — matched: {', '.join(hits)}")

    if stale:
        print(f"\n🕐 Repo-managed files >60 days old ({len(stale)}):")
        for entry in sorted(stale, key=lambda x: -x["age_days"])[:10]:
            print(f"  {entry['path']} ({entry['age_days']}d)")

    print(f"\n📊 Summary:")
    print(f"  Identical: {len(results['identical'])}")
    print(f"  Changed: {len(results['changed'])}")
    print(f"  New: {len(results['missing_repo'])}")
    print(f"  Trivial (skipped): {len(results['trivial'])}")
    print(f"  Missing live: {len(results['missing_live'])}")
    if blocked:
        print(f"  PII blocked: {len(blocked)}")
    if stale:
        print(f"  Stale repo-managed: {len(stale)}")
    print()


def resolve_repo_managed_paths(manifest: dict) -> set[str]:
    """Collect all repo_managed paths to exclude from 'missing live' reporting."""
    managed = set()
    for entry in manifest.get("repo_managed", []):
        managed.add(entry["path"].rstrip("/"))
    return managed


def is_repo_managed(repo_rel: str, managed_paths: set[str]) -> bool:
    """Check if a repo-relative path is covered by repo_managed."""
    rel_str = str(repo_rel)
    for mp in managed_paths:
        if rel_str == mp or rel_str.startswith(mp + "/") or rel_str.startswith(mp):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="N5OS Ode Export Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--init", action="store_true", help="First-time bulk sync")
    parser.add_argument("--diff", action="store_true", help="Drift report only")
    parser.add_argument("--test", action="store_true", help="Post-export smoke test")
    parser.add_argument("--threshold", type=int, default=None, help="Skip files with <N chars drift")
    parser.add_argument("--force", action="store_true", help="Ignore threshold, sync all")
    parser.add_argument("--repo", type=str, default=None, help="Override repo path")
    args = parser.parse_args()

    manifest = load_manifest()
    settings = manifest.get("settings", {})

    repo_path = Path(args.repo) if args.repo else Path(settings.get("repo_path", "/tmp/n5os-ode"))
    threshold = args.threshold if args.threshold is not None else settings.get("threshold", 50)
    pii_patterns = settings.get("pii_patterns", [])

    if not repo_path.exists():
        log.info(f"Repo not found at {repo_path}, cloning...")
        remote = settings.get("repo_remote", "vrijenattawar/n5os-ode")
        branch = settings.get("default_branch", "main")
        result = subprocess.run(
            ["gh", "repo", "clone", remote, str(repo_path), "--", "-b", branch],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            log.error(f"Failed to clone: {result.stderr}")
            return 1

    pairs = resolve_file_list(manifest)
    log.info(f"Manifest resolved: {len(pairs)} files in scope")

    managed_paths = resolve_repo_managed_paths(manifest)
    pairs = [(lp, rr) for lp, rr in pairs if not is_repo_managed(str(rr), managed_paths)]
    log.info(f"After excluding repo-managed: {len(pairs)} files to check")

    results = compare_files(pairs, repo_path, threshold, args.force)

    stale = check_repo_managed_staleness(manifest, repo_path)

    to_sync = results["changed"] + results["missing_repo"]
    clean, blocked = run_pii_gate(to_sync, pii_patterns)

    if args.diff:
        print_drift_report(results, stale, blocked)
        return 0

    print_drift_report(results, stale, blocked)

    if not clean:
        log.info("Nothing to export.")
        return 0

    if blocked:
        log.warning(f"⚠ {len(blocked)} files blocked by PII gate — fix before export")

    sanitize_patterns = settings.get("sanitize_patterns", {})

    if args.dry_run:
        log.info(f"\n[DRY-RUN] Would export {len(clean)} files:")
        do_export(clean, repo_path, dry_run=True, sanitize_patterns=sanitize_patterns)
        return 0

    if args.init:
        log.info(f"\n[INIT] Bulk syncing {len(clean)} files...")
    else:
        log.info(f"\nExporting {len(clean)} files...")

    count = do_export(clean, repo_path, dry_run=False, sanitize_patterns=sanitize_patterns)
    log.info(f"\n✓ {count} files exported")

    valid = run_validate(repo_path)

    if args.test:
        smoke_ok = run_smoke_test(repo_path)
        if not smoke_ok:
            log.warning("⚠ Smoke test failed — review before committing")
            return 1

    if not valid:
        log.warning("⚠ Validation issues found — review before committing")

    log.info("\nNext steps:")
    log.info(f"  cd {repo_path}")
    log.info("  git diff --stat")
    log.info('  git add -A && git commit -m "chore: sync from live workspace"')
    log.info("  git push origin feature/ode-v2-upgrade")

    return 0


if __name__ == "__main__":
    sys.exit(main())
