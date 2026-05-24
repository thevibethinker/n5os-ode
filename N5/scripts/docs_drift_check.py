#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


FILE_MENTION_RE = re.compile(r"`?file '([^']+)'`?")
PATHISH_RE = re.compile(r"\b(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:md|py|json|yaml|yml|sh|ts|tsx|js|jsx)\b")


@dataclass
class MissingRef:
    source: str
    line: int
    reference: str
    resolved_path: str
    reason: str


def iter_markdown_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.md"):
        if "/Trash/" in str(p):
            continue
        yield p


def resolve_reference(root: Path, ref: str) -> Path:
    if ref.startswith("/"):
        return Path(ref)
    return root / ref


def extract_refs(line: str, include_pathish: bool) -> List[str]:
    refs: List[str] = []
    seen = set()
    for ref in FILE_MENTION_RE.findall(line):
        if ref.startswith(("http://", "https://", "www.")):
            continue
        if any(token in ref for token in ("path/to/", "<", ">", "{{", "}}")):
            continue
        if ref not in seen:
            refs.append(ref)
            seen.add(ref)
    if include_pathish:
        for ref in PATHISH_RE.findall(line):
            if ref.startswith(("http://", "https://", "www.")):
                continue
            if any(token in ref for token in ("path/to/", "<", ">", "{{", "}}")):
                continue
            if ref not in seen:
                refs.append(ref)
                seen.add(ref)
    return refs


def check_references(root: Path, files: Iterable[Path], include_pathish: bool) -> List[MissingRef]:
    missing: List[MissingRef] = []
    for md in files:
        try:
            lines = md.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, start=1):
            for ref in extract_refs(line, include_pathish):
                resolved = resolve_reference(root, ref)
                if not resolved.exists():
                    missing.append(
                        MissingRef(
                            source=str(md.relative_to(root)),
                            line=i,
                            reference=ref,
                            resolved_path=str(resolved),
                            reason="missing_path",
                        )
                    )
    return missing


def check_deprecation_mismatches(root: Path) -> List[dict]:
    issues: List[dict] = []

    close_spec = root / "N5/prefs/operations/conversation-end-v5.md"
    if close_spec.exists():
        text = close_spec.read_text(encoding="utf-8", errors="ignore")
        if "deprecated" in text and "Prompts/Close Conversation.prompt.md" in text:
            issues.append(
                {
                    "file": "N5/prefs/operations/conversation-end-v5.md",
                    "type": "deprecation_conflict",
                    "message": "Close prompt marked deprecated while still referenced as active.",
                }
            )

    claude = root / "CLAUDE.md"
    build_orchestrator_ref = "Documents/System/Build-Orchestrator-System.md"
    if claude.exists():
        text = claude.read_text(encoding="utf-8", errors="ignore")
        if build_orchestrator_ref in text and not (root / build_orchestrator_ref).exists():
            issues.append(
                {
                    "file": "CLAUDE.md",
                    "type": "broken_reference",
                    "message": f"Referenced path does not exist: {build_orchestrator_ref}",
                }
            )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check docs for reference drift and deprecation mismatches.")
    parser.add_argument("--root", default="/home/workspace", help="Workspace root to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--report", help="Optional path to write full JSON report.")
    parser.add_argument(
        "--include-pathish",
        action="store_true",
        help="Also scan generic path-like strings (noisier, broader coverage).",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = list(iter_markdown_files(root))
    missing_refs = check_references(root, files, args.include_pathish)
    mismatch_issues = check_deprecation_mismatches(root)

    payload = {
        "root": str(root),
        "markdown_files_scanned": len(files),
        "missing_reference_count": len(missing_refs),
        "deprecation_mismatch_count": len(mismatch_issues),
        "missing_references": [m.__dict__ for m in missing_refs],
        "deprecation_mismatches": mismatch_issues,
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Docs drift check root: {root}")
        print(f"Markdown files scanned: {len(files)}")
        print(f"Missing references: {len(missing_refs)}")
        print(f"Deprecation mismatches: {len(mismatch_issues)}")
        for issue in mismatch_issues[:20]:
            print(f"- {issue['file']}: {issue['type']} | {issue['message']}")
        for miss in missing_refs[:20]:
            print(f"- {miss.source}:{miss.line} -> {miss.reference} (missing)")

    return 1 if missing_refs or mismatch_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
