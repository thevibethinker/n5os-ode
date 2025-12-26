#!/usr/bin/env python3

"""CLI entrypoint for the Zo Tutor Kit.

Initial focus:
- `init`: create local config and key material
- `status`: show current tutor configuration
- `local-demo`: exercise sandbox + teaching package + forensics locally
- `export-package`: write a teaching package JSON file to share via email/files
- `import-package`: ingest a teaching package JSON file into a sandbox
- `student-plan`: print a structured implementation plan for a teaching package
- `invite`: generate an invite blob that can be emailed to another Zo
- `accept`: accept an invite blob file and register the peer locally
- `bridge-listen`: listen for a single bridge message on a TCP port
- `bridge-send-demo`: send a single demo teaching package over the bridge

Networking, sessions, and teaching flows will be layered on in later phases.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from zo_tutor_kit.sandbox_manager import ensure_session_sandbox
from zo_tutor_kit.logging_forensics import log_message
from zo_tutor_kit.tutor_protocol import (
    SessionMode,
    SessionStart,
    SessionScope,
    CapabilityPackage,
    KnowledgePackage,
    DataDropPackage,
)
from zo_tutor_kit.peers import load_peers, save_peers, get_peers_path
from zo_tutor_kit import bridge as tutor_bridge


CONFIG_FILENAME = "tutor_config.yaml"
PROTOCOL_VERSION = "0.1"
INVITE_BEGIN = "--- BEGIN ZO-TUTOR-INVITE ---"
INVITE_END = "--- END ZO-TUTOR-INVITE ---"


def get_repo_root() -> Path:
    return Path(__file__).resolve().parent


def get_config_path() -> Path:
    return get_repo_root() / CONFIG_FILENAME


def _read_local_zo_id() -> str:
    """Read the local zo_id from the tutor config file."""

    config_path = get_config_path()
    if not config_path.exists():
        raise RuntimeError("Tutor config not found. Run `tutor_cli.py init` first.")

    for line in config_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("zo_id:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("zo_id not found in tutor_config.yaml")


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize local tutor configuration.

    For now this just writes a minimal YAML stub if it does not exist.
    """

    config_path = get_config_path()
    if config_path.exists() and not args.force:
        print(f"Config already exists at {config_path}. Use --force to overwrite.")
        return

    zo_id = args.zo_id or input("Enter Zo ID (e.g. va.zo): ").strip()

    content = f"""zo_id: {zo_id}
config_version: 0.1
"""
    config_path.write_text(content, encoding="utf-8")
    print(f"Wrote tutor config to {config_path}")


def cmd_status(args: argparse.Namespace) -> None:  # noqa: ARG001
    """Show basic tutor kit status."""

    config_path = get_config_path()
    if not config_path.exists():
        print("Tutor config not found. Run `tutor_cli.py init` first.")
        return

    print(f"Tutor config found at {config_path}")
    print(config_path.read_text(encoding="utf-8"))

    peers_path = get_peers_path()
    if peers_path.exists():
        peers = load_peers()
        print(f"Peers registry at {peers_path}:")
        for zo_id, meta in peers.items():
            modes = ",".join(meta.get("allowed_modes", []))
            print(f"  - {zo_id} (modes: {modes})")
    else:
        print("No peers registry found yet.")


def _make_demo_package(mode: SessionMode):
    """Create a small synthetic teaching package payload for the given mode.

    This is intentionally demo-focused. In later phases we will replace
    this with real capability/knowledge/data extraction.
    """

    if mode == "capability":
        manifest = {
            "entrypoints": ["demo.meeting_scheduler.main"],
            "dependencies": ["python>=3.10", "zo-core"],
            "tests": [
                {
                    "name": "no_double_booking",
                    "description": "Ensure the scheduler never creates overlapping events for the same attendee.",
                    "kind": "unit",
                    "inputs": {"existing_events": ["09:00-10:00"], "new_event": "09:30-10:00"},
                    "expected": {"accepted": False},
                }
            ],
            "non_functional": {
                "latency_ms_p95": 500,
                "max_meetings_per_day": 100,
            },
        }
        return CapabilityPackage(
            name="demo_meeting_scheduler",
            version="0.1",
            description="Demo capability package for a simple meeting scheduler.",
            manifest=manifest,
        ).to_dict()

    if mode == "knowledge":
        return KnowledgePackage(
            topic="Tutor Protocol Overview",
            outline="Goals -> Constraints -> Flows -> Safety",
            body=(
                "This is a synthetic knowledge package summarizing the high-level "
                "design of the Tutor Protocol for demo purposes."
            ),
            learning_objectives=[
                "Understand the difference between capability, knowledge, and data modes.",
                "Be able to describe the time-bounded, sandboxed nature of sessions.",
            ],
            references=[
                "internal:rfc-tutor-protocol",
            ],
        ).to_dict()

    if mode == "data":
        return DataDropPackage(
            name="demo_dataset",
            schema={"fields": [
                {"name": "id", "type": "string"},
                {"name": "value", "type": "number"},
            ]},
            purpose="Demonstrate bounded data drop packaging.",
            preview_rows=3,
            record_count=100,
            sensitivity="low",
        ).to_dict()

    raise ValueError(f"Unsupported demo mode: {mode}")


def cmd_local_demo(args: argparse.Namespace) -> None:
    """Run a fully local demo of sandbox + package + forensics logging.

    This does not talk to any remote Zo. It simply exercises the core
    building blocks so we can iterate safely.
    """

    mode: SessionMode = args.mode

    config_path = get_config_path()
    if not config_path.exists():
        print("Tutor config not found. Run `tutor_cli.py init` first.")
        return

    now = datetime.now(timezone.utc)
    session_id = f"local-demo-{mode}-{int(now.timestamp())}"

    # Simulate a session start
    start = SessionStart(
        session_id=session_id,
        peer_zo_id="local",  # no real peer yet
        mode=mode,
        ttl_seconds=600,
        created_at=now,
    )
    scope = SessionScope(
        session_id=session_id,
        description=f"Local demo session for mode={mode}",
        mode=mode,
    )

    sandbox_path = ensure_session_sandbox(session_id)
    sandbox_path.mkdir(parents=True, exist_ok=True)

    package_dict = _make_demo_package(mode)
    package_path = sandbox_path / "teaching_package.json"
    package_bytes = json.dumps(
        {
            "protocol_version": PROTOCOL_VERSION,
            "session_start": {
                "session_id": start.session_id,
                "peer_zo_id": start.peer_zo_id,
                "mode": start.mode,
                "ttl_seconds": start.ttl_seconds,
                "created_at": start.created_at.isoformat(),
            },
            "session_scope": {
                "session_id": scope.session_id,
                "description": scope.description,
                "mode": scope.mode,
            },
            "package": package_dict,
        },
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    package_path.write_bytes(package_bytes)

    sha256 = hashlib.sha256(package_bytes).hexdigest()
    log_message(
        session_id=session_id,
        direction="outbound",
        message_type="LOCAL_DEMO_PACKAGE",
        payload=package_bytes,
        payload_sha256=sha256,
    )

    print(f"Created local demo session: {session_id}")
    print(f"Sandbox path: {sandbox_path}")
    print(f"Teaching package: {package_path}")
    print("A synthetic log entry was recorded in the tutor_sessions log root.")


def cmd_export_package(args: argparse.Namespace) -> None:
    """Export a teaching package to a JSON file for offline sharing.

    For now this uses the same synthetic demo packages as `local-demo`.
    In later phases, this will pull from real capabilities/knowledge/data.
    """

    mode: SessionMode = args.mode

    config_path = get_config_path()
    if not config_path.exists():
        print("Tutor config not found. Run `tutor_cli.py init` first.")
        return

    package_dict = _make_demo_package(mode)
    wrapper = {
        "protocol_version": PROTOCOL_VERSION,
        "mode": mode,
        "package": package_dict,
    }

    out_path = Path(args.out) if args.out else Path(f"tutor_package_{mode}.json")
    out_path = out_path.expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_bytes = json.dumps(wrapper, indent=2, sort_keys=True).encode("utf-8")
    out_path.write_bytes(out_bytes)

    print(f"Wrote {mode} teaching package to {out_path}")


def cmd_import_package(args: argparse.Namespace) -> None:
    """Import a teaching package JSON file into a fresh sandbox.

    This simulates the Student side receiving a package via email or
    file transfer. It does not yet perform full validation or run tests.
    """

    in_path = Path(args.file).expanduser().resolve()
    if not in_path.exists():
        print(f"Package file not found: {in_path}")
        return

    raw_bytes = in_path.read_bytes()
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse JSON from {in_path}: {exc}")
        return

    mode_value = data.get("mode") or (data.get("package") or {}).get("type")
    if mode_value not in ("capability", "knowledge", "data"):
        print(f"Unrecognized or missing mode in package: {mode_value}")
        return

    mode: SessionMode = mode_value  # type: ignore[assignment]
    package_dict = data.get("package") or {}

    # Round-trip through the dataclasses to validate shape a bit.
    if mode == "capability":
        pkg = CapabilityPackage.from_dict(package_dict)
        package_out = pkg.to_dict()
    elif mode == "knowledge":
        pkg = KnowledgePackage.from_dict(package_dict)
        package_out = pkg.to_dict()
    else:  # mode == "data"
        pkg = DataDropPackage.from_dict(package_dict)
        package_out = pkg.to_dict()

    now = datetime.now(timezone.utc)
    session_id = f"import-demo-{mode}-{int(now.timestamp())}"
    sandbox_path = ensure_session_sandbox(session_id)
    sandbox_path.mkdir(parents=True, exist_ok=True)

    teaching_path = sandbox_path / "teaching_package_imported.json"
    teaching_bytes = json.dumps(
        {
            "protocol_version": data.get("protocol_version", PROTOCOL_VERSION),
            "imported_from": str(in_path),
            "mode": mode,
            "package": package_out,
        },
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    teaching_path.write_bytes(teaching_bytes)

    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    log_message(
        session_id=session_id,
        direction="inbound",
        message_type="IMPORTED_PACKAGE_RAW",
        payload=raw_bytes,
        payload_sha256=sha256,
    )

    print(f"Imported {mode} teaching package from {in_path}")
    print(f"Created sandbox session: {session_id}")
    print(f"Sandbox path: {sandbox_path}")
    print(f"Imported teaching package copy: {teaching_path}")
    print("A synthetic inbound log entry was recorded in the tutor_sessions log root.")


def cmd_student_plan(args: argparse.Namespace) -> None:
    """Print a structured implementation plan for a teaching package.

    This simulates the "Student persona" reading a package and outlining
    how it would approach implementation and safety checks, without
    making any changes to the workspace.
    """

    in_path = Path(args.file).expanduser().resolve()
    if not in_path.exists():
        print(f"Package file not found: {in_path}")
        return

    raw_bytes = in_path.read_bytes()
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse JSON from {in_path}: {exc}")
        return

    mode_value = data.get("mode") or (data.get("package") or {}).get("type")
    if mode_value not in ("capability", "knowledge", "data"):
        print(f"Unrecognized or missing mode in package: {mode_value}")
        return

    mode: SessionMode = mode_value  # type: ignore[assignment]
    package_dict = data.get("package") or {}

    print(f"=== Student plan for mode={mode} ===")

    if mode == "capability":
        pkg = CapabilityPackage.from_dict(package_dict)
        manifest = pkg.manifest
        entrypoints = manifest.get("entrypoints", [])
        dependencies = manifest.get("dependencies", [])
        tests = manifest.get("tests", [])
        non_func = manifest.get("non_functional", {})

        print(f"Capability: {pkg.name} (v{pkg.version})")
        print(f"Description: {pkg.description}\n")

        print("Entrypoints:")
        for ep in entrypoints or ["<none specified>"]:
            print(f"  - {ep}")

        print("\nDependencies:")
        for dep in dependencies or ["<none specified>"]:
            print(f"  - {dep}")

        print("\nTests:")
        if not tests:
            print("  - <none specified>")
        else:
            for t in tests:
                print(f"  - {t.get('name', '<unnamed>')} [{t.get('kind', 'unspecified')}]: {t.get('description', '')}")

        print("\nNon-functional expectations:")
        if not non_func:
            print("  - <none specified>")
        else:
            for k, v in non_func.items():
                print(f"  - {k}: {v}")

        print("\nSuggested implementation steps:")
        print("  1. Create a fresh tutor sandbox and module skeleton for the capability.")
        print("  2. Wire the declared entrypoints to the new module, keeping changes localized.")
        print("  3. Implement the described behavior, prioritizing tests listed above.")
        print("  4. Run tests in the sandbox and iterate until all pass.")
        print("  5. Only then propose promoting changes from sandbox to main workspace.")

        print("\nSafety checklist:")
        print("  - Keep all writes inside the tutor sandbox until human review.")
        print("  - Do not touch secrets or service credentials while implementing.")
        print("  - Verify that behavior aligns with declared non-functional constraints.")

    elif mode == "knowledge":
        pkg = KnowledgePackage.from_dict(package_dict)

        print(f"Topic: {pkg.topic}")
        print(f"Outline: {pkg.outline}\n")

        print("Learning objectives:")
        if not pkg.learning_objectives:
            print("  - <none specified>")
        else:
            for obj in pkg.learning_objectives:
                print(f"  - {obj}")

        print("\nReferences:")
        if not pkg.references:
            print("  - <none specified>")
        else:
            for ref in pkg.references:
                print(f"  - {ref}")

        print("\nSuggested integration steps:")
        print("  1. Store this knowledge package in a dedicated knowledge vault or notes area.")
        print("  2. Link it to any related capabilities or prompts on this Zo.")
        print("  3. Use it as contextual material when implementing related capabilities.")

    else:  # mode == "data"
        pkg = DataDropPackage.from_dict(package_dict)

        print(f"Dataset: {pkg.name}")
        print(f"Purpose: {pkg.purpose}")
        print(f"Schema: {pkg.schema}")
        print(f"Preview rows (hint): {pkg.preview_rows}")
        print(f"Record count (approx): {pkg.record_count}")
        print(f"Sensitivity: {pkg.sensitivity}\n")

        print("Suggested handling steps:")
        print("  1. Store the raw data in a dedicated data directory with clear naming.")
        print("  2. Apply access controls appropriate to the declared sensitivity level.")
        print("  3. Build small, capability-specific views of the data rather than passing the full dataset everywhere.")

        print("\nSafety checklist:")
        print("  - Confirm that sensitivity metadata matches the actual contents.")
        print("  - Avoid copying data into logs or error messages.")
        print("  - Consider anonymization or aggregation before sharing onward.")


def cmd_invite(args: argparse.Namespace) -> None:
    """Generate an invite blob that can be emailed to another Zo.

    This does not perform any networking; it only prints or writes a
    structured blob containing JSON, which the peer can later accept
    using the `accept` command.
    """

    try:
        local_zo_id = _read_local_zo_id()
    except Exception as exc:  # noqa: BLE001
        print(str(exc))
        return

    raw_modes: List[str] = [m.strip() for m in (args.modes or "").split(",") if m.strip()]
    if not raw_modes:
        raw_modes = ["capability", "knowledge", "data"]

    allowed_values = {"capability", "knowledge", "data"}
    for m in raw_modes:
        if m not in allowed_values:
            print(f"Invalid mode in --modes: {m}")
            return

    invite = {
        "protocol_version": PROTOCOL_VERSION,
        "from_zo_id": local_zo_id,
        "to_zo_id": args.peer_id,
        "allowed_modes": raw_modes,
        "issued_at": datetime.now(timezone.utc).isoformat(),
    }

    invite_json = json.dumps(invite, indent=2, sort_keys=True)
    blob = f"{INVITE_BEGIN}\n{invite_json}\n{INVITE_END}\n"

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.write_text(blob, encoding="utf-8")
        print(f"Wrote invite for peer {args.peer_id} to {out_path}")
    else:
        print(blob)


def _extract_invite_json(text: str) -> str:
    """Extract the JSON section from an invite blob or raw JSON text."""

    if INVITE_BEGIN in text and INVITE_END in text:
        lines = text.splitlines()
        in_block = False
        json_lines: List[str] = []
        for line in lines:
            if line.strip() == INVITE_BEGIN:
                in_block = True
                continue
            if line.strip() == INVITE_END:
                break
            if in_block:
                json_lines.append(line)
        return "\n".join(json_lines).strip()
    return text.strip()


def cmd_accept(args: argparse.Namespace) -> None:
    """Accept an invite blob file and register the peer locally.

    The file can contain either:
    - a full invite blob with BEGIN/END markers, or
    - raw JSON for the invite payload.
    """

    in_path = Path(args.file).expanduser().resolve()
    if not in_path.exists():
        print(f"Invite file not found: {in_path}")
        return

    text = in_path.read_text(encoding="utf-8")
    json_text = _extract_invite_json(text)
    try:
        invite = json.loads(json_text)
    except json.JSONDecodeError as exc:
        print(f"Failed to parse invite JSON: {exc}")
        return

    if invite.get("protocol_version") != PROTOCOL_VERSION:
        print(
            f"Warning: invite protocol_version={invite.get('protocol_version')} "
            f"does not match local PROTOCOL_VERSION={PROTOCOL_VERSION}"
        )

    from_zo_id = invite.get("from_zo_id")
    if not from_zo_id:
        print("Invite is missing from_zo_id")
        return

    allowed_modes = invite.get("allowed_modes") or []
    peers = load_peers()
    peers[from_zo_id] = {
        "zo_id": from_zo_id,
        "last_invite": invite,
        "allowed_modes": allowed_modes,
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    save_peers(peers)

    print(f"Registered peer {from_zo_id} with modes: {', '.join(allowed_modes) or '<none>'}")
    print(f"Peers registry path: {get_peers_path()}")


def cmd_bridge_listen(args: argparse.Namespace) -> None:
    """Listen for a single bridge message on the given host/port."""

    host = args.host
    port = int(args.port)
    asyncio.run(tutor_bridge.listen_once(host=host, port=port))


def cmd_bridge_send_demo(args: argparse.Namespace) -> None:
    """Send a single demo teaching package over the bridge.

    This uses the same synthetic packages as `local-demo` and
    `export-package`, wrapped in a minimal Tutor Protocol envelope.
    """

    mode: SessionMode = args.mode
    package_dict = _make_demo_package(mode)

    host = args.host
    port = int(args.port)
    ttl_seconds = int(args.ttl)

    asyncio.run(
        tutor_bridge.send_demo_package(
            host=host,
            port=port,
            mode=mode,
            ttl_seconds=ttl_seconds,
            package=package_dict,
            protocol_version=PROTOCOL_VERSION,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Zo Tutor Kit CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init", help="Initialize local tutor configuration")
    p_init.add_argument("--zo-id", help="Logical Zo identifier, e.g. va.zo")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing config if present")
    p_init.set_defaults(func=cmd_init)

    p_status = subparsers.add_parser("status", help="Show tutor configuration status")
    p_status.set_defaults(func=cmd_status)

    p_demo = subparsers.add_parser("local-demo", help="Run a local demo session (no networking)")
    p_demo.add_argument(
        "--mode",
        choices=["capability", "knowledge", "data"],
        default="capability",
        help="Which teaching mode to exercise.",
    )
    p_demo.set_defaults(func=cmd_local_demo)

    p_export = subparsers.add_parser(
        "export-package",
        help="Export a teaching package JSON file for offline sharing",
    )
    p_export.add_argument(
        "--mode",
        choices=["capability", "knowledge", "data"],
        default="capability",
        help="Which teaching mode to export.",
    )
    p_export.add_argument(
        "--out",
        help="Output path for the JSON package file (defaults to tutor_package_<mode>.json in CWD)",
    )
    p_export.set_defaults(func=cmd_export_package)

    p_import = subparsers.add_parser(
        "import-package",
        help="Import a teaching package JSON file into a sandbox",
    )
    p_import.add_argument(
        "file",
        help="Path to the JSON teaching package file received from another Zo.",
    )
    p_import.set_defaults(func=cmd_import_package)

    p_plan = subparsers.add_parser(
        "student-plan",
        help="Print a structured implementation plan for a teaching package",
    )
    p_plan.add_argument(
        "file",
        help="Path to the JSON teaching package file to analyze.",
    )
    p_plan.set_defaults(func=cmd_student_plan)

    p_invite = subparsers.add_parser(
        "invite",
        help="Generate an invite blob that can be emailed to another Zo",
    )
    p_invite.add_argument(
        "--peer-id",
        required=True,
        help="Target Zo identifier (e.g. other.zo)",
    )
    p_invite.add_argument(
        "--modes",
        help="Comma-separated list of allowed modes (default: capability,knowledge,data)",
    )
    p_invite.add_argument(
        "--out",
        help="Optional output file for the invite blob (otherwise prints to stdout)",
    )
    p_invite.set_defaults(func=cmd_invite)

    p_accept = subparsers.add_parser(
        "accept",
        help="Accept an invite blob file and register the peer locally",
    )
    p_accept.add_argument(
        "file",
        help="Path to the invite blob file (with or without BEGIN/END markers)",
    )
    p_accept.set_defaults(func=cmd_accept)

    p_bridge_listen = subparsers.add_parser(
        "bridge-listen",
        help="Listen for a single bridge message on a TCP port",
    )
    p_bridge_listen.add_argument("--host", default="0.0.0.0", help="Host/interface to bind (default: 0.0.0.0)")
    p_bridge_listen.add_argument("--port", default=62001, type=int, help="Port to listen on (default: 62001)")
    p_bridge_listen.set_defaults(func=cmd_bridge_listen)

    p_bridge_send = subparsers.add_parser(
        "bridge-send-demo",
        help="Send a single demo teaching package over the bridge",
    )
    p_bridge_send.add_argument("--host", default="127.0.0.1", help="Bridge host to connect to (default: 127.0.0.1)")
    p_bridge_send.add_argument("--port", default=62001, type=int, help="Bridge port to connect to (default: 62001)")
    p_bridge_send.add_argument(
        "--mode",
        choices=["capability", "knowledge", "data"],
        default="capability",
        help="Which teaching mode to send as a demo payload.",
    )
    p_bridge_send.add_argument(
        "--ttl",
        type=int,
        default=600,
        help="TTL in seconds to embed in the demo session metadata (default: 600)",
    )
    p_bridge_send.set_defaults(func=cmd_bridge_send_demo)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        raise SystemExit(1)
    func(args)


if __name__ == "__main__":
    main()



