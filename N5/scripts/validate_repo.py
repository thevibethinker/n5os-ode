#!/usr/bin/env python3
"""
Validate n5OS-Ode repo for completeness and consistency.

Usage:
  python3 scripts/validate_repo.py [--verbose] [--scope broad|pr]
"""
import sys
import re
from pathlib import Path
import py_compile
import argparse


PR_PYTHON_PATHS = (
    "N5/lib",
    "N5/scripts",
    "Skills/pulse/scripts",
)

PR_MARKDOWN_PATHS = (
    "README.md",
    "CHANGELOG.md",
    "AGENTS.md",
    "N5/HARNESS_CONTRACT.md",
    "N5/SESSION_STATE_POLICY.md",
    "Skills/pulse/SKILL.md",
)


def rel_path(path, root):
    return str(path.relative_to(root)).replace("\\", "/")


def is_top_level_script(path, root):
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    return len(rel.parts) == 3 and rel.parts[0] == "N5" and rel.parts[1] == "scripts"


def iter_pr_python_files(root):
    seen = set()
    for prefix in PR_PYTHON_PATHS:
        base = root / prefix
        if not base.exists():
            continue
        if prefix == "N5/scripts":
            candidates = sorted(p for p in base.glob("*.py") if p.is_file())
        else:
            candidates = sorted(p for p in base.rglob("*.py") if p.is_file())
        for path in candidates:
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            yield path


def iter_pr_markdown_files(root):
    for rel in PR_MARKDOWN_PATHS:
        path = root / rel
        if path.exists() and path.is_file():
            yield path

def main():
    parser = argparse.ArgumentParser(description="Validate n5OS-Ode repository")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--scope",
        choices=("broad", "pr"),
        default="broad",
        help="Validation scope. Use 'pr' for CI PR gates and 'broad' for repository drift audits.",
    )
    args = parser.parse_args()
    
    # Script is at N5/scripts/, repo root is 2 levels up
    root = Path(__file__).resolve().parent.parent.parent
    errors = []
    warnings = []
    
    if args.scope == "pr":
        py_files = list(iter_pr_python_files(root))
        md_files = list(iter_pr_markdown_files(root))
    else:
        py_files = sorted(root.rglob("*.py"))
        md_files = list(root.rglob("*.md")) + list(root.rglob("*.prompt.md"))

    # 1. Check Python syntax
    for pf in py_files:
        try:
            py_compile.compile(str(pf), doraise=True)
        except Exception as e:
            errors.append(f"Python syntax: {pf}: {e}")
    
    # 2. Check for file references in markdown/prompts
    file_ref_re = re.compile(r"`file '([^']+)'`")
    # Build set of relative paths from root
    existing = {str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*') if p.is_file()}
    
    RUNTIME_PATH_PREFIXES = {
        'Personal/', 'Documents/', 'Knowledge/', 'Records/',
        'N5/builds/', 'N5/schemas/', 'N5/learnings/', 'N5/config/pulse_control',
        'Skills/pulse-interview/',
    }
    
    for md_file in md_files:
        try:
            txt = md_file.read_text(errors="ignore")
        except Exception:
            continue
        
        for m in file_ref_re.finditer(txt):
            ref = m.group(1)
            if ref.startswith('/'):
                continue
            ref_norm = ref.lstrip('./')
            if '<' in ref_norm or ref_norm == '...':
                continue
            if ref_norm.startswith('path/to/'):
                continue
            if ref_norm.endswith('/'):
                continue
            if any(ref_norm.startswith(p) for p in RUNTIME_PATH_PREFIXES):
                continue
            if ref_norm not in existing:
                warnings.append(f"Missing file ref: {md_file.relative_to(root)}: {ref}")
    
    # 3. Check markdown links
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for md_file in md_files:
        if md_file.suffix != ".md":
            continue
        try:
            txt = md_file.read_text(errors="ignore")
        except Exception:
            continue
        
        for m in link_re.finditer(txt):
            url = m.group(1).strip()
            if url.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            url = url.split('#', 1)[0]
            if not url:
                continue
            
            try:
                target = (md_file.parent / url).resolve()
                rel = str(target.relative_to(root)).replace('\\', '/')
            except ValueError:
                continue
            
            if rel not in existing:
                warnings.append(f"Missing link target: {md_file.relative_to(root)}: {url}")
    
    # 4. Check for PROJECT_REPO placeholder (skip self to avoid false positive)
    placeholder_pattern = "PROJECT" + "_REPO"  # Split to avoid self-match
    placeholder_files = py_files if args.scope == "pr" else root.rglob("*.py")
    for pf in placeholder_files:
        if pf.name == "validate_repo.py":
            continue  # Skip self
        try:
            txt = pf.read_text(errors="ignore")
        except Exception:
            continue
        if placeholder_pattern in txt:
            warnings.append(f"Placeholder {placeholder_pattern} found in: {pf.relative_to(root)}")
    
    # Report
    warnings = list(dict.fromkeys(warnings))
    
    print("=" * 70)
    print("n5OS-Ode Repository Validation")
    print("=" * 70)
    print(f"Scope: {args.scope}")
    print()
    
    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
        print()
    
    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")
        print()
    
    if not errors and not warnings:
        print("✅ All checks passed!")
        print()
    
    py_count = len(py_files)
    md_count = len(md_files)
    print(f"📊 Summary:")
    print(f"  Python files: {py_count}")
    print(f"  Markdown files: {md_count}")
    print()
    
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())

