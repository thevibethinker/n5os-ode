#!/usr/bin/env python3
"""
verify.py — Post-promotion verification suite for Skills.

Runs comprehensive checks to validate a promoted skill is fully
self-contained and functional.

Usage:
    python3 Skills/build-promote/scripts/verify.py check <skill-slug>
    python3 Skills/build-promote/scripts/verify.py check <skill-slug> --fix
    python3 Skills/build-promote/scripts/verify.py check <skill-slug> --verbose
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/home/workspace")
BUILDS_DIR = WORKSPACE / "N5" / "builds"
SKILLS_DIR = WORKSPACE / "Skills"

CHECK_NAMES = [
    "stale_paths",
    "script_health",
    "import_health",
    "skill_md",
    "state_accessibility",
    "protection_markers",
    "build_residuals",
    "bytecode_cleanup",
]


def _is_string_literal_ref(line: str) -> bool:
    """Check if N5/builds/ appears inside a string literal on this line."""
    stripped = line.strip()
    # Detect N5/builds/ inside any quoting: single, double, or triple-quoted
    if '"N5/builds/' in stripped or "'N5/builds/" in stripped:
        return True
    # Triple-quoted single-line docstrings: """...N5/builds/..."""
    if ('"""' in stripped or "'''" in stripped) and "N5/builds/" in stripped:
        return True
    # String containing N5/builds/ with any prefix inside quotes (e.g. "`N5/builds/")
    if ('N5/builds/' in stripped and
            (stripped.count('"') >= 2 or stripped.count("'") >= 2)):
        return True
    return False


def check_stale_paths(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 1: Stale path references to N5/builds/."""
    result = {"name": "stale_paths", "status": "pass", "details": "", "failures": []}
    stale_refs = []

    for ext in ("*.py", "*.ts", "*.js", "*.md", "*.json"):
        for f in skill_dir.rglob(ext):
            if "__pycache__" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8", errors="replace")
                is_skill_md = f.name == "SKILL.md"
                is_script = f.suffix in (".py", ".ts", ".js")
                in_docstring = False
                for i, line in enumerate(content.split("\n"), 1):
                    # Track triple-quote docstring blocks in Python
                    if is_script and f.suffix == ".py":
                        tq_count = line.count('"""') + line.count("'''")
                        if tq_count % 2 == 1:
                            in_docstring = not in_docstring
                    if "N5/builds/" in line:
                        stripped = line.strip()
                        # Skip provenance metadata in SKILL.md
                        if is_skill_md and any(
                            marker in stripped.lower()
                            for marker in ("promoted_from:", "build origin", "promoted from build")
                        ):
                            continue
                        # Skip template strings (contain {build}, {slug}, etc.)
                        if "{build}" in line or "{slug}" in line:
                            continue
                        # Skip string literals in scripts (detection logic, not operational paths)
                        if is_script and _is_string_literal_ref(line):
                            continue
                        # Skip comments and docstrings in scripts
                        if is_script and (stripped.startswith("#") or in_docstring):
                            continue
                        # In markdown files, skip descriptive text and inline code refs
                        # Only flag lines that look like config (variable assignments, path definitions)
                        if f.suffix == ".md":
                            # Skip if N5/builds/ is in backticks (documentation reference)
                            if "`N5/builds/" in stripped:
                                continue
                            # Skip general prose — only flag lines with assignment-like patterns
                            if not any(p in stripped for p in ("= ", "=\t", "DIR ", "PATH ")):
                                continue
                        stale_refs.append(f"{f.relative_to(skill_dir)}:{i}: {stripped[:100]}")
            except (IOError, UnicodeDecodeError):
                pass

    if stale_refs:
        result["status"] = "fail"
        result["details"] = f"{len(stale_refs)} stale reference(s) found"
        result["failures"] = stale_refs
    else:
        result["details"] = "0 stale references found"

    return result


def check_script_health(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 2: Run --help on all scripts."""
    result = {"name": "script_health", "status": "pass", "details": "", "failures": []}
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        result["status"] = "skip"
        result["details"] = "No scripts/ directory"
        return result

    py_scripts = sorted(scripts_dir.glob("*.py"))
    if not py_scripts:
        result["status"] = "skip"
        result["details"] = "No Python scripts found"
        return result

    passed = 0
    failed = 0
    for script in py_scripts:
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True, text=True, timeout=10,
                cwd=str(WORKSPACE),
            )
            if proc.returncode == 0:
                passed += 1
            else:
                failed += 1
                err = proc.stderr.strip()[:200] if proc.stderr else "exit code " + str(proc.returncode)
                result["failures"].append(f"{script.name}: {err}")
        except subprocess.TimeoutExpired:
            failed += 1
            result["failures"].append(f"{script.name}: timeout (10s)")
        except Exception as e:
            failed += 1
            result["failures"].append(f"{script.name}: {str(e)[:100]}")

    total = passed + failed
    if failed > 0:
        result["status"] = "fail"
        result["details"] = f"{passed}/{total} scripts OK, {failed} failed"
    else:
        result["details"] = f"{passed}/{total} scripts OK"

    # Clean up pycache created by running --help (avoid false positive in bytecode check)
    for pycache in scripts_dir.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)

    return result


def check_import_health(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 3: Scan for sys.path hacks referencing build paths."""
    result = {"name": "import_health", "status": "pass", "details": "", "failures": []}
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        result["status"] = "skip"
        result["details"] = "No scripts/ directory"
        return result

    offending = []
    for script in sorted(scripts_dir.glob("*.py")):
        try:
            content = script.read_text(encoding="utf-8")
            lines = content.split("\n")
            dirty = False
            clean_lines = []
            for i, line in enumerate(lines, 1):
                if ("sys.path.insert" in line or "sys.path.append" in line) and "N5/builds/" in line:
                    # Skip lines where these appear inside string literals (detection logic)
                    stripped = line.strip()
                    if stripped.startswith("#") or _is_string_literal_ref(line):
                        clean_lines.append(line)
                        continue
                    offending.append(f"{script.name}:{i}: {stripped}")
                    dirty = True
                    if not fix:
                        clean_lines.append(line)
                else:
                    clean_lines.append(line)

            if fix and dirty:
                script.write_text("\n".join(clean_lines), encoding="utf-8")
        except (IOError, UnicodeDecodeError):
            pass

    if offending:
        if fix:
            result["status"] = "fixed"
            result["details"] = f"Removed {len(offending)} build-path import(s)"
        else:
            result["status"] = "fail"
            result["details"] = f"{len(offending)} build-path import(s) found"
        result["failures"] = offending
    else:
        result["details"] = "No build-path imports found"

    return result


def check_skill_md(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 4: SKILL.md exists and documents all scripts."""
    result = {"name": "skill_md", "status": "pass", "details": "", "failures": []}
    skill_md_path = skill_dir / "SKILL.md"

    if not skill_md_path.exists():
        result["status"] = "fail"
        result["details"] = "SKILL.md not found"
        return result

    content = skill_md_path.read_text(encoding="utf-8")

    # Check frontmatter
    missing_fields = []
    if "name:" not in content[:500]:
        missing_fields.append("name")
    if "description:" not in content[:500]:
        missing_fields.append("description")

    if missing_fields:
        result["failures"].append(f"Missing frontmatter fields: {', '.join(missing_fields)}")

    # Check script documentation
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        scripts = [f.name for f in sorted(scripts_dir.glob("*.py"))]
        undocumented = [s for s in scripts if s not in content]
        if undocumented:
            result["failures"].append(f"Undocumented scripts: {', '.join(undocumented)}")

    if result["failures"]:
        result["status"] = "fail"
        result["details"] = "; ".join(result["failures"])
    else:
        scripts_count = len(list(scripts_dir.glob("*.py"))) if scripts_dir.exists() else 0
        result["details"] = f"SKILL.md present, {scripts_count} scripts documented"

    return result


def check_state_accessibility(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 5: State directory is referenced and readable."""
    result = {"name": "state_accessibility", "status": "pass", "details": "", "failures": []}
    state_dir = skill_dir / "state"

    if not state_dir.exists():
        result["status"] = "skip"
        result["details"] = "No state/ directory (stateless skill)"
        return result

    # Check if any script references state/
    scripts_dir = skill_dir / "scripts"
    referenced = False
    if scripts_dir.exists():
        for script in scripts_dir.glob("*.py"):
            try:
                content = script.read_text(encoding="utf-8")
                if "state" in content and ("state/" in content or "state\"" in content or "state'" in content):
                    referenced = True
                    break
            except (IOError, UnicodeDecodeError):
                pass

    if not referenced:
        # Also check SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if "state/" in content:
                referenced = True

    # Check readability
    readable = False
    try:
        files = list(state_dir.rglob("*"))
        readable = True
    except PermissionError:
        pass

    if not referenced:
        result["status"] = "warn"
        result["details"] = "State directory exists but no script references it"
    elif not readable:
        result["status"] = "fail"
        result["details"] = "State directory not readable"
    else:
        file_count = sum(1 for f in state_dir.rglob("*") if f.is_file())
        result["details"] = f"State directory referenced and readable ({file_count} files)"

    return result


def check_protection_markers(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 6: .n5protected in state/ directory."""
    result = {"name": "protection_markers", "status": "pass", "details": "", "failures": []}
    state_dir = skill_dir / "state"

    if not state_dir.exists():
        result["status"] = "skip"
        result["details"] = "No state/ directory"
        return result

    n5p = state_dir / ".n5protected"
    if not n5p.exists():
        if fix:
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            n5p.write_text(
                f"Protected: runtime state for {skill_dir.name}\n"
                f"Date: {today}\n"
            )
            result["status"] = "fixed"
            result["details"] = "Created .n5protected in state/"
        else:
            result["status"] = "fail"
            result["details"] = "Missing .n5protected in state/ directory"
    else:
        result["details"] = ".n5protected present"

    return result


def check_build_residuals(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 7: Source build only contains scaffolding."""
    result = {"name": "build_residuals", "status": "pass", "details": "", "failures": []}

    # Try to find source build
    skill_md_path = skill_dir / "SKILL.md"
    source_build = None

    if skill_md_path.exists():
        content = skill_md_path.read_text(encoding="utf-8")
        # Look for promoted_from in frontmatter
        for line in content.split("\n"):
            if "promoted_from:" in line:
                source_build = line.split("promoted_from:")[-1].strip().strip('"').strip("'")
                break

    if not source_build:
        # Try matching by slug
        build_dir = BUILDS_DIR / skill_dir.name
        if build_dir.exists():
            source_build = skill_dir.name

    if not source_build:
        result["status"] = "skip"
        result["details"] = "No matching build folder found"
        return result

    build_dir = BUILDS_DIR / source_build
    if not build_dir.exists():
        result["status"] = "skip"
        result["details"] = f"Build folder not found: {source_build}"
        return result

    # Check for operational files still in build
    scaffolding_names = {
        "meta.json", "PLAN.md", "STATUS.md", "BUILD.md",
        "BUILD_LESSONS.json", "FINALIZATION.json", ".n5protected",
    }
    scaffolding_dirs = {"workers", "completions", "deposits", "drops"}

    operational = []
    for f in build_dir.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(build_dir)
        parts = rel.parts

        # Skip scaffolding
        if rel.name in scaffolding_names:
            continue
        if parts and parts[0] in scaffolding_dirs:
            continue

        operational.append(str(rel))

    if operational:
        result["status"] = "warn"
        result["details"] = f"{len(operational)} operational file(s) still in build folder"
        result["failures"] = operational[:20]  # Cap at 20
    else:
        result["details"] = "Only scaffolding remains in build folder"

    return result


def check_bytecode_cleanup(skill_dir: Path, fix: bool = False, verbose: bool = False) -> dict:
    """Check 8: No stale __pycache__."""
    result = {"name": "bytecode_cleanup", "status": "pass", "details": "", "failures": []}

    pycache_dirs = list(skill_dir.rglob("__pycache__"))

    if pycache_dirs:
        if fix:
            for d in pycache_dirs:
                shutil.rmtree(d)
            result["status"] = "fixed"
            result["details"] = f"Deleted {len(pycache_dirs)} __pycache__ directory(ies)"
        else:
            result["status"] = "fail"
            result["details"] = f"{len(pycache_dirs)} __pycache__ directory(ies) found"
            result["failures"] = [str(d.relative_to(skill_dir)) for d in pycache_dirs]
    else:
        result["details"] = "No stale bytecode"

    return result


def cmd_check(args):
    """Run all verification checks."""
    slug = args.slug
    skill_dir = SKILLS_DIR / slug

    if not skill_dir.exists():
        print(f"Skill not found: {skill_dir}", file=sys.stderr)
        return 1

    checks = [
        check_stale_paths,
        check_script_health,
        check_import_health,
        check_skill_md,
        check_state_accessibility,
        check_protection_markers,
        check_build_residuals,
        check_bytecode_cleanup,
    ]

    results = []
    for check_fn in checks:
        r = check_fn(skill_dir, fix=args.fix, verbose=args.verbose)
        results.append(r)

    # Output
    passed = sum(1 for r in results if r["status"] in ("pass", "skip", "fixed"))
    failed = sum(1 for r in results if r["status"] == "fail")
    warned = sum(1 for r in results if r["status"] == "warn")

    if args.json:
        output = {
            "skill_slug": slug,
            "checks": results,
            "passed": passed,
            "failed": failed,
            "warned": warned,
            "overall": "pass" if failed == 0 else "fail",
        }
        json.dump(output, sys.stdout, indent=2)
    else:
        print(f"\n{'='*50}", file=sys.stderr)
        print(f"  Verification: Skills/{slug}/", file=sys.stderr)
        print(f"{'='*50}", file=sys.stderr)
        print(file=sys.stderr)

        for r in results:
            icon = {
                "pass": "\u2713", "fail": "\u2717", "skip": "-",
                "warn": "!", "fixed": "\u2713*",
            }.get(r["status"], "?")
            status_label = r["status"].upper()
            name_display = r["name"].replace("_", " ").title()
            print(f"  [{icon}] {name_display} — {status_label} ({r['details']})", file=sys.stderr)

            if (args.verbose or r["status"] in ("fail", "warn")) and r.get("failures"):
                for f in r["failures"][:10]:
                    print(f"      → {f}", file=sys.stderr)

        print(file=sys.stderr)
        total = len(results)
        print(f"  Result: {passed}/{total} PASSED", file=sys.stderr, end="")
        if failed:
            print(f", {failed} FAILED", file=sys.stderr, end="")
        if warned:
            print(f", {warned} WARNED", file=sys.stderr, end="")
        print(file=sys.stderr)

    return 0 if failed == 0 else 1


def main():
    parser = argparse.ArgumentParser(
        description="Verify a promoted skill is self-contained and functional.",
    )
    subparsers = parser.add_subparsers(dest="command")

    p_check = subparsers.add_parser("check", help="Run verification checks")
    p_check.add_argument("slug", help="Skill slug to verify")
    p_check.add_argument("--fix", action="store_true", help="Auto-fix simple issues")
    p_check.add_argument("--verbose", "-v", action="store_true", help="Show details for all checks")
    p_check.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "check": cmd_check,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
