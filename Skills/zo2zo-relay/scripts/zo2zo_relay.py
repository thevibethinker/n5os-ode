#!/usr/bin/env python3
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

WORKSPACE_ROOT = Path("/home/workspace")
SCRIPT_ROOT = WORKSPACE_ROOT / "Skills" / "zo2zo-relay"
ALLOWLIST_PATH = SCRIPT_ROOT / "config" / "allowlist.yaml"
SUBSTRATE_CLI = WORKSPACE_ROOT / "Skills" / "zo-substrate" / "scripts" / "substrate.py"
BUNDLE_CLI = WORKSPACE_ROOT / "Skills" / "consulting-api" / "scripts" / "bundle_manager.py"


@dataclass
class SubstrateConfig:
    identity: str
    partner: str
    repo: str
    branch: str
    clone_method: str


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=check,
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_yaml(path: Path) -> dict[str, Any]:
    if not yaml:
        raise RuntimeError("PyYAML not installed")
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {path}")
    return data


def load_substrate_config() -> SubstrateConfig:
    cfg_path = WORKSPACE_ROOT / "Skills" / "zo-substrate" / "config" / "substrate.yaml"
    cfg = load_yaml(cfg_path)
    return SubstrateConfig(
        identity=str((cfg.get("identity") or {}).get("name", "")).strip(),
        partner=str((cfg.get("partner") or {}).get("name", "")).strip(),
        repo=str((cfg.get("substrate") or {}).get("repo", "")).strip(),
        branch=str((cfg.get("substrate") or {}).get("branch", "main")).strip() or "main",
        clone_method=str((cfg.get("substrate") or {}).get("clone_method", "https")).strip() or "https",
    )


def repo_url(cfg: SubstrateConfig) -> str:
    if cfg.clone_method == "ssh":
        return f"git@github.com:{cfg.repo}.git"
    return f"https://github.com/{cfg.repo}.git"


def load_allowlist() -> list[str]:
    data = load_yaml(ALLOWLIST_PATH)
    roots = data.get("allowed_roots", [])
    if not isinstance(roots, list):
        raise ValueError("allowed_roots must be a list")
    cleaned = [str(r).strip().strip("/") for r in roots if str(r).strip()]
    if not cleaned:
        raise ValueError("allowlist has no roots")
    return cleaned


def parse_csv(arg: str) -> list[str]:
    return [s.strip() for s in arg.split(",") if s.strip()]


def resolve_workspace_path(raw: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = WORKSPACE_ROOT / candidate
    resolved = candidate.resolve()
    resolved.relative_to(WORKSPACE_ROOT)
    return resolved


def is_allowed(path: Path, allowed_roots: list[str]) -> bool:
    rel = path.relative_to(WORKSPACE_ROOT)
    rel_str = str(rel).replace("\\", "/")
    for root in allowed_roots:
        if rel_str == root or rel_str.startswith(root + "/"):
            return True
    return False


def validate_paths(paths: list[str], allowed_roots: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw in paths:
        p = resolve_workspace_path(raw)
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {p}")
        if not is_allowed(p, allowed_roots):
            raise PermissionError(f"Path outside allowlist: {p}")
        resolved.append(p)
    return resolved


def run_substrate(command: str, skills: str | None = None, dry_run: bool = False) -> int:
    cmd = ["python3", str(SUBSTRATE_CLI), command]
    if skills:
        cmd += ["--skills", skills]
    if dry_run:
        cmd += ["--dry-run"]
    proc = run(cmd, check=False)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode


def run_bundle(skill: str, target: str, dry_run: bool) -> int:
    out_dir = WORKSPACE_ROOT / "N5" / "data" / "zo2zo-relay" / "bundles"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bundle_path = out_dir / f"{skill}_{stamp}.tar.gz"

    create_cmd = [
        "python3",
        str(BUNDLE_CLI),
        "create",
        "--skill",
        skill,
        "--output",
        str(bundle_path),
    ]
    if dry_run:
        create_cmd.append("--dry-run")
    create_proc = run(create_cmd, check=False)
    if create_proc.stdout:
        print(create_proc.stdout.strip())
    if create_proc.returncode != 0:
        if create_proc.stderr:
            print(create_proc.stderr.strip(), file=sys.stderr)
        return create_proc.returncode

    if dry_run:
        return 0

    validate_proc = run(
        ["python3", str(BUNDLE_CLI), "validate", "--bundle", str(bundle_path)],
        check=False,
    )
    if validate_proc.stdout:
        print(validate_proc.stdout.strip())
    if validate_proc.returncode != 0:
        if validate_proc.stderr:
            print(validate_proc.stderr.strip(), file=sys.stderr)
        return validate_proc.returncode

    transmit_proc = run(
        [
            "python3",
            str(BUNDLE_CLI),
            "transmit",
            "--bundle",
            str(bundle_path),
            "--target",
            target,
        ],
        check=False,
    )
    if transmit_proc.stdout:
        print(transmit_proc.stdout.strip())
    if transmit_proc.stderr:
        print(transmit_proc.stderr.strip(), file=sys.stderr)
    return transmit_proc.returncode


def clone_repo(cfg: SubstrateConfig) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix=f"zo2zo-relay-{cfg.identity}-", dir="/tmp"))
    try:
        run(
            [
                "git",
                "clone",
                "--branch",
                cfg.branch,
                "--single-branch",
                repo_url(cfg),
                str(tmp),
            ]
        )
        return tmp
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise


def copy_payload(paths: list[Path], transfer_dir: Path) -> list[str]:
    payload_dir = transfer_dir / "payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for src in paths:
        rel = src.relative_to(WORKSPACE_ROOT)
        dst = payload_dir / rel
        if src.is_dir():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied.append(str(rel))
    return copied


def git_commit_push(repo_dir: Path, cfg: SubstrateConfig, message: str, dry_run: bool) -> None:
    run(["git", "config", "user.email", f"{cfg.identity}@zo.computer"], cwd=repo_dir)
    run(["git", "config", "user.name", cfg.identity], cwd=repo_dir)
    run(["git", "add", "-A"], cwd=repo_dir)
    status = run(["git", "status", "--porcelain"], cwd=repo_dir)
    if not status.stdout.strip():
        print("No changes to commit.")
        return
    if dry_run:
        print("Dry run: skipping commit/push.")
        return
    run(["git", "commit", "-m", message], cwd=repo_dir)
    run(["git", "push", "origin", cfg.branch], cwd=repo_dir)


def cmd_check(_: argparse.Namespace) -> int:
    cfg = load_substrate_config()
    allowed = load_allowlist()
    print("zo2zo-relay check")
    print(f"identity={cfg.identity} partner={cfg.partner} repo={cfg.repo} branch={cfg.branch}")
    print(f"allowlist_roots={','.join(allowed)}")
    proc = run(["python3", str(SUBSTRATE_CLI), "setup", "check"], check=False)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        print(proc.stderr.strip(), file=sys.stderr)
    return proc.returncode


def cmd_send_skill(args: argparse.Namespace) -> int:
    return run_substrate("push", skills=args.skills, dry_run=args.dry_run)


def cmd_recv_skill(args: argparse.Namespace) -> int:
    return run_substrate("pull", skills=args.skills, dry_run=args.dry_run)


def cmd_bundle_skill(args: argparse.Namespace) -> int:
    return run_bundle(args.skill, args.target, args.dry_run)


def cmd_send_paths(args: argparse.Namespace) -> int:
    cfg = load_substrate_config()
    allowed = load_allowlist()
    requested = parse_csv(args.paths)
    if not requested:
        raise ValueError("No paths provided")
    paths = validate_paths(requested, allowed)
    transfer_id = args.transfer_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    tmp = clone_repo(cfg)
    try:
        drop_root = tmp / "RelayDrops" / cfg.identity / transfer_id
        copied = copy_payload(paths, drop_root)
        metadata = {
            "transfer_id": transfer_id,
            "sender": cfg.identity,
            "partner": cfg.partner,
            "created_at": now_iso(),
            "paths": copied,
            "note": args.note or "",
        }
        (drop_root / "transfer.json").write_text(json.dumps(metadata, indent=2))
        print(json.dumps(metadata, indent=2))
        git_commit_push(
            tmp,
            cfg,
            f"relay {cfg.identity} transfer {transfer_id}",
            args.dry_run,
        )
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def cmd_list_drops(args: argparse.Namespace) -> int:
    cfg = load_substrate_config()
    tmp = clone_repo(cfg)
    try:
        root = tmp / "RelayDrops"
        if not root.exists():
            print("[]")
            return 0
        sender_filter = args.sender
        rows: list[dict[str, Any]] = []
        senders = [d for d in root.iterdir() if d.is_dir()]
        for sender_dir in sorted(senders):
            sender = sender_dir.name
            if sender_filter and sender != sender_filter:
                continue
            for transfer_dir in sorted([d for d in sender_dir.iterdir() if d.is_dir()]):
                meta = transfer_dir / "transfer.json"
                if not meta.exists():
                    continue
                data = json.loads(meta.read_text())
                rows.append(data)
        print(json.dumps(rows, indent=2))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cmd_pull_paths(args: argparse.Namespace) -> int:
    cfg = load_substrate_config()
    tmp = clone_repo(cfg)
    try:
        sender = args.sender or cfg.partner
        sender_root = tmp / "RelayDrops" / sender
        if not sender_root.exists():
            raise FileNotFoundError(f"No drops from sender: {sender}")
        if args.transfer_id:
            transfer_dir = sender_root / args.transfer_id
        else:
            candidates = sorted([d for d in sender_root.iterdir() if d.is_dir()])
            if not candidates:
                raise FileNotFoundError(f"No transfers for sender: {sender}")
            transfer_dir = candidates[-1]

        payload_dir = transfer_dir / "payload"
        meta_path = transfer_dir / "transfer.json"
        if not payload_dir.exists() or not meta_path.exists():
            raise FileNotFoundError(f"Incomplete transfer at {transfer_dir}")

        dest = Path(args.dest).resolve()
        dest.mkdir(parents=True, exist_ok=True)

        for item in payload_dir.rglob("*"):
            rel = item.relative_to(payload_dir)
            target = dest / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists() and not args.overwrite:
                    continue
                shutil.copy2(item, target)

        print(meta_path.read_text())
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manual Zo2Zo relay commands")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Verify substrate and allowlist config")

    send_skill = sub.add_parser("send-skill", help="Push skills through zo-substrate")
    send_skill.add_argument("--skills", help="Comma-separated skill slugs")
    send_skill.add_argument("--dry-run", action="store_true")

    recv_skill = sub.add_parser("recv-skill", help="Pull skills through zo-substrate")
    recv_skill.add_argument("--skills", help="Comma-separated skill slugs")
    recv_skill.add_argument("--dry-run", action="store_true")

    bundle_skill = sub.add_parser("bundle-skill", help="Create+validate+transmit skill bundle")
    bundle_skill.add_argument("--skill", required=True)
    bundle_skill.add_argument("--target", default="zoputer")
    bundle_skill.add_argument("--dry-run", action="store_true")

    send_paths = sub.add_parser("send-paths", help="Send allowlisted workspace paths via substrate repo")
    send_paths.add_argument("--paths", required=True, help="Comma-separated paths, relative or absolute")
    send_paths.add_argument("--transfer-id", help="Optional explicit transfer id")
    send_paths.add_argument("--note", help="Optional transfer note")
    send_paths.add_argument("--dry-run", action="store_true")

    list_drops = sub.add_parser("list-drops", help="List path-transfer drops in substrate")
    list_drops.add_argument("--sender", help="Filter by sender name")

    pull_paths = sub.add_parser("pull-paths", help="Pull transferred paths into local destination")
    pull_paths.add_argument("--sender", help="Sender name (default: partner)")
    pull_paths.add_argument("--transfer-id", help="Specific transfer id (default: latest)")
    pull_paths.add_argument("--dest", default="/home/workspace/N5/data/zo2zo-relay/inbox")
    pull_paths.add_argument("--overwrite", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    handlers = {
        "check": cmd_check,
        "send-skill": cmd_send_skill,
        "recv-skill": cmd_recv_skill,
        "bundle-skill": cmd_bundle_skill,
        "send-paths": cmd_send_paths,
        "list-drops": cmd_list_drops,
        "pull-paths": cmd_pull_paths,
    }
    try:
        return handlers[args.command](args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
