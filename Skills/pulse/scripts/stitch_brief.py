#!/usr/bin/env python3
"""
Stitch Brief Generator for Pulse Builds

Generates visual reference mockups for design-related Drops using Google Stitch.
Reads .impeccable.md design context and Drop briefs, composes Stitch prompts,
and saves screenshots as visual references in the build's context/ directory.

Usage:
    python3 Skills/pulse/scripts/stitch_brief.py generate <slug> [--drop <drop_id>] [--device DESKTOP] [--dry-run]
    python3 Skills/pulse/scripts/stitch_brief.py check <slug>
    python3 Skills/pulse/scripts/stitch_brief.py list <slug>

Commands:
    generate  Generate Stitch reference mockups for design Drops
    check     Check which design Drops have/lack visual references
    list      List existing Stitch references for a build

Requires:
    - STITCH_API_KEY environment variable
    - bun + @google/stitch-sdk installed in Skills/google-stitch/scripts/
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

BUILDS_DIR = Path("/home/workspace/N5/builds")
WORKSPACE_ROOT = Path("/home/workspace")
STITCH_SCRIPT = Path("/home/workspace/Skills/google-stitch/scripts/stitch.ts")

DESIGN_KEYWORD_PATTERN = re.compile(
    r'\b(?:'
    r'ui|ux|design|layout|styling|css|tailwind|'
    r'frontend|front-end|webpage|component|homepage|'
    r'aesthetic|visual|responsive|typography|'
    r'theme|dark mode|light mode|animation|landing page'
    r')\b',
    re.IGNORECASE,
)


def find_impeccable(slug: str) -> Path | None:
    """Find .impeccable.md for a build by scanning plan/briefs for Sites/ references."""
    build_dir = BUILDS_DIR / slug
    all_content = ""

    plan_path = build_dir / "PLAN.md"
    if plan_path.exists():
        all_content += plan_path.read_text()

    drops_dir = build_dir / "drops"
    if drops_dir.exists():
        for brief in drops_dir.glob("*.md"):
            all_content += brief.read_text()

    # Check meta.json for target_project
    meta_path = build_dir / "meta.json"
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            target = meta.get("target_project")
            if target:
                imp = WORKSPACE_ROOT / target / ".impeccable.md"
                if imp.exists():
                    return imp
        except (json.JSONDecodeError, KeyError):
            pass

    # Scan for Sites/ references
    for match in re.finditer(r'Sites/([a-zA-Z0-9_-]+)', all_content):
        site_slug = match.group(1)
        imp = WORKSPACE_ROOT / "Sites" / site_slug / ".impeccable.md"
        if imp.exists():
            return imp

    # Check build dir itself
    imp = build_dir / ".impeccable.md"
    if imp.exists():
        return imp

    return None


def get_design_drops(slug: str) -> list[dict]:
    """Get Drops that involve design/frontend work."""
    build_dir = BUILDS_DIR / slug
    meta_path = build_dir / "meta.json"
    drops_dir = build_dir / "drops"

    if not meta_path.exists():
        return []

    meta = json.loads(meta_path.read_text())
    design_drops = []

    for drop_id, drop_info in meta.get("drops", {}).items():
        title = drop_info.get("title", "")
        brief_content = ""

        # Find the brief file
        if drops_dir.exists():
            for brief_path in drops_dir.glob("*.md"):
                if brief_path.stem.startswith(drop_id):
                    brief_content = brief_path.read_text()
                    break

        # Check if design-related
        is_design = bool(
            DESIGN_KEYWORD_PATTERN.search(title) or
            DESIGN_KEYWORD_PATTERN.search(brief_content)
        )

        if is_design:
            # Extract the objective from the brief
            objective = title
            obj_match = re.search(
                r'(?:^#+\s*Objective\s*\n)(.*?)(?=\n#|\Z)',
                brief_content,
                re.MULTILINE | re.DOTALL,
            )
            if obj_match:
                objective = obj_match.group(1).strip()[:500]

            design_drops.append({
                "drop_id": drop_id,
                "title": title,
                "objective": objective,
                "status": drop_info.get("status", "pending"),
            })

    return design_drops


def compose_stitch_prompt(drop: dict, impeccable_content: str) -> str:
    """Compose a Stitch prompt from Drop brief + .impeccable.md design context."""
    # Extract key design directives from .impeccable.md
    sections = {}
    current_section = None
    for line in impeccable_content.split("\n"):
        header_match = re.match(r'^##\s+(.+)', line)
        if header_match:
            current_section = header_match.group(1).strip()
            sections[current_section] = ""
        elif current_section:
            sections[current_section] += line + "\n"

    aesthetic = sections.get("Aesthetic Direction", "").strip()
    colors = sections.get("Color System", "").strip()
    typography = sections.get("Typography", "").strip()
    principles = sections.get("Design Principles", "").strip()

    # Build a focused prompt for Stitch
    prompt_parts = [
        f"Design a web page: {drop['title']}.",
        f"\nPage purpose: {drop['objective']}",
    ]

    if aesthetic:
        # Extract just the key visual direction, not full markdown
        aesthetic_lines = [
            l.strip("- *").strip()
            for l in aesthetic.split("\n")
            if l.strip() and not l.startswith("**Anti") and not l.startswith("- Dark")
            and not l.startswith("- \"Hacker") and not l.startswith("- Generic")
            and not l.startswith("- Overly") and not l.startswith("- Busy")
        ][:6]
        prompt_parts.append(f"\nVisual style: {' '.join(aesthetic_lines)}")

    if colors:
        color_lines = [
            l.strip("- *").strip()
            for l in colors.split("\n")
            if l.strip() and not l.startswith("**No")
        ][:5]
        prompt_parts.append(f"\nColors: {' '.join(color_lines)}")

    if typography:
        typo_lines = [
            l.strip("- *").strip()
            for l in typography.split("\n")
            if l.strip()
        ][:4]
        prompt_parts.append(f"\nTypography: {' '.join(typo_lines)}")

    prompt = " ".join(prompt_parts)

    # Stitch works best with prompts under ~1000 chars
    if len(prompt) > 1000:
        prompt = prompt[:997] + "..."

    return prompt


def run_stitch_command(args: list[str], cwd: str | None = None) -> dict | None:
    """Run stitch.ts CLI and return parsed JSON output."""
    cmd = ["bun", str(STITCH_SCRIPT)] + args
    env = os.environ.copy()

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=cwd or str(STITCH_SCRIPT.parent),
        env=env,
    )

    if result.returncode != 0:
        print(f"  Stitch error: {result.stderr.strip()}", file=sys.stderr)
        return None

    # Try to parse JSON from output
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"raw_output": result.stdout}


def download_screenshot(url: str, output_path: Path) -> bool:
    """Download a screenshot from a URL."""
    try:
        import urllib.request
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, str(output_path))
        return True
    except Exception as e:
        print(f"  Failed to download screenshot: {e}", file=sys.stderr)
        return False


def cmd_generate(slug: str, drop_filter: str | None, device: str, dry_run: bool):
    """Generate Stitch reference mockups for design Drops."""
    build_dir = BUILDS_DIR / slug
    context_dir = build_dir / "context"

    if not build_dir.exists():
        print(f"Build not found: {slug}")
        sys.exit(1)

    # Find .impeccable.md
    impeccable_path = find_impeccable(slug)
    if not impeccable_path:
        print(f"No .impeccable.md found for build '{slug}'.")
        print("Run /teach-impeccable on the target project first.")
        sys.exit(1)

    impeccable_content = impeccable_path.read_text()
    print(f"Design context: {impeccable_path}")

    # Get design drops
    design_drops = get_design_drops(slug)
    if drop_filter:
        design_drops = [d for d in design_drops if d["drop_id"] == drop_filter]

    if not design_drops:
        print("No design-related Drops found.")
        return

    print(f"Found {len(design_drops)} design Drop(s):\n")

    if dry_run:
        for drop in design_drops:
            prompt = compose_stitch_prompt(drop, impeccable_content)
            print(f"  {drop['drop_id']}: {drop['title']}")
            print(f"  Status: {drop['status']}")
            print(f"  Prompt ({len(prompt)} chars):")
            print(f"    {prompt[:200]}...")
            ref_path = context_dir / f"{drop['drop_id']}-reference.png"
            print(f"  Would save to: {ref_path}")
            print()
        print("(dry-run — no API calls made)")
        return

    # Check for STITCH_API_KEY
    if not os.environ.get("STITCH_API_KEY"):
        print("STITCH_API_KEY not set. Add it in Settings > Advanced.")
        sys.exit(1)

    # Create or get project
    project_id = None
    meta_path = build_dir / "meta.json"
    meta = json.loads(meta_path.read_text())

    stitch_project_id = meta.get("stitch_project_id")
    if stitch_project_id:
        project_id = stitch_project_id
        print(f"Using existing Stitch project: {project_id}")
    else:
        print(f"Creating Stitch project for build '{slug}'...")
        result = run_stitch_command(["create", f"Pulse: {slug}"])
        if result and "raw_output" in result:
            # Parse "Created project: <id>" from output
            match = re.search(r'Created project:\s*(\S+)', result["raw_output"])
            if match:
                project_id = match.group(1)

        if not project_id:
            print("Failed to create Stitch project.")
            sys.exit(1)

        # Save project ID to meta.json
        meta["stitch_project_id"] = project_id
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"Created Stitch project: {project_id}")

    # Create design system from .impeccable.md
    print("Setting up design system from .impeccable.md...")
    design_system_prompt = compose_stitch_prompt(
        {"title": "Design system", "objective": "Overall design language"},
        impeccable_content,
    )
    run_stitch_command([
        "call", "create_design_system",
        json.dumps({"projectId": project_id, "prompt": design_system_prompt}),
    ])

    # Generate for each Drop
    context_dir.mkdir(parents=True, exist_ok=True)
    generated = 0

    for drop in design_drops:
        ref_path = context_dir / f"{drop['drop_id']}-reference.png"
        print(f"\n  Generating: {drop['drop_id']} — {drop['title']}")

        prompt = compose_stitch_prompt(drop, impeccable_content)
        print(f"  Prompt: {prompt[:120]}...")

        # Generate screen
        gen_args = ["generate", project_id, prompt]
        if device != "AGNOSTIC":
            gen_args.extend(["--device", device])

        result = run_stitch_command(gen_args)
        if not result:
            print(f"  Failed to generate screen for {drop['drop_id']}")
            continue

        # Extract screenshot URL from response
        screenshot_url = None
        if isinstance(result, dict):
            for comp in result.get("outputComponents", []):
                for screen in comp.get("design", {}).get("screens", []):
                    url = screen.get("screenshot", {}).get("downloadUrl")
                    if url:
                        screenshot_url = url
                        break

        if screenshot_url:
            if download_screenshot(screenshot_url, ref_path):
                print(f"  Saved: {ref_path}")
                generated += 1
            else:
                print(f"  Screenshot download failed")
        else:
            # Save raw JSON as fallback
            fallback = context_dir / f"{drop['drop_id']}-reference.json"
            fallback.write_text(json.dumps(result, indent=2))
            print(f"  No screenshot URL found. Saved raw response: {fallback}")

    print(f"\n{'='*50}")
    print(f"Generated {generated}/{len(design_drops)} reference mockups.")
    if generated > 0:
        print(f"References saved to: {context_dir}/")


def cmd_check(slug: str):
    """Check which design Drops have/lack visual references."""
    build_dir = BUILDS_DIR / slug
    context_dir = build_dir / "context"

    design_drops = get_design_drops(slug)
    if not design_drops:
        print(f"No design-related Drops in build '{slug}'.")
        return

    impeccable_path = find_impeccable(slug)

    print(f"Build: {slug}")
    print(f"Design context (.impeccable.md): {'✅ ' + str(impeccable_path) if impeccable_path else '❌ Missing'}")
    print(f"Design Drops: {len(design_drops)}\n")

    has_refs = 0
    missing_refs = 0

    for drop in design_drops:
        ref_png = context_dir / f"{drop['drop_id']}-reference.png"
        ref_json = context_dir / f"{drop['drop_id']}-reference.json"
        has_ref = ref_png.exists() or ref_json.exists()

        status_icon = "✅" if has_ref else "⬜"
        if has_ref:
            has_refs += 1
        else:
            missing_refs += 1

        print(f"  {status_icon} {drop['drop_id']}: {drop['title']} ({drop['status']})")

    print(f"\nStitch references: {has_refs}/{len(design_drops)}")
    if missing_refs > 0 and impeccable_path:
        print(f"Run: python3 Skills/pulse/scripts/stitch_brief.py generate {slug}")


def cmd_list(slug: str):
    """List existing Stitch references for a build."""
    context_dir = BUILDS_DIR / slug / "context"
    if not context_dir.exists():
        print(f"No context directory for build '{slug}'.")
        return

    refs = sorted(context_dir.glob("*-reference.*"))
    if not refs:
        print("No Stitch references found.")
        return

    print(f"Stitch references for '{slug}':\n")
    for ref in refs:
        size_kb = ref.stat().st_size / 1024
        print(f"  {ref.name} ({size_kb:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(description="Stitch Brief Generator for Pulse")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate Stitch reference mockups")
    gen.add_argument("slug", help="Build slug")
    gen.add_argument("--drop", help="Generate for a specific Drop ID only")
    gen.add_argument("--device", default="DESKTOP", help="Device type (default: DESKTOP)")
    gen.add_argument("--dry-run", action="store_true", help="Preview prompts without calling API")

    chk = sub.add_parser("check", help="Check Stitch reference status")
    chk.add_argument("slug", help="Build slug")

    lst = sub.add_parser("list", help="List existing references")
    lst.add_argument("slug", help="Build slug")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args.slug, args.drop, args.device, args.dry_run)
    elif args.command == "check":
        cmd_check(args.slug)
    elif args.command == "list":
        cmd_list(args.slug)


if __name__ == "__main__":
    main()
