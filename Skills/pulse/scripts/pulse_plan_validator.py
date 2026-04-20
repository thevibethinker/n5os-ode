#!/usr/bin/env python3
"""
Pulse Plan Validator

Validates that a build plan is complete before allowing build start.
Based on Theo's lesson: Plans are context vehicles, not spec documents.
An unfilled plan means the model will guess — and guessing compounds errors.

Usage:
    python3 pulse_plan_validator.py <slug>
    python3 pulse_plan_validator.py <slug> --fix  # Interactive mode to fill placeholders

Exit codes:
    0 = Plan is valid
    1 = Plan has issues (unfilled placeholders, missing sections)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

def resolve_workspace_root() -> Path:
    for key in ("ZO_WORKSPACE", "N5OS_WORKSPACE"):
        value = os.environ.get(key)
        if value:
            return Path(value).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


WORKSPACE_ROOT = resolve_workspace_root()
BUILDS_DIR = WORKSPACE_ROOT / "N5" / "builds"

# Regex patterns for design/frontend keywords (word-boundary matched to avoid
# false positives like "ui" matching "acquisition" or "page" matching "homepage")
DESIGN_KEYWORD_PATTERN = re.compile(
    r'\b(?:'
    r'ui|ux|design|layout|styling|css|tailwind|'
    r'frontend|front-end|webpage|component|homepage|'
    r'aesthetic|visual|responsive|typography|'
    r'theme|dark mode|light mode|animation|landing page'
    r')\b',
    re.IGNORECASE,
)

# Patterns that indicate unfilled template content
PLACEHOLDER_PATTERNS = [
    r'\{\{[A-Z_]+\}\}',           # {{PLACEHOLDER}}
    r'\[\[.+?\]\]',               # [[placeholder]]
    r'<[A-Z_]+>',                 # <PLACEHOLDER> (but not HTML tags)
    r'TODO:?\s',                  # TODO or TODO:
    r'FIXME:?\s',                 # FIXME
    r'XXX',                       # XXX marker
]

# Required sections in a valid plan
REQUIRED_SECTIONS = [
    "Objective",
    "Open Questions",
    "Phase 1",  # At least one phase
    "Success Criteria",
]

# Sections that should have content (not just headers)
CONTENT_REQUIRED = [
    "Objective",
    "Success Criteria",
]


def extract_frontmatter(content: str) -> str:
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    return match.group(1) if match else ""


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf'^{re.escape(key)}:\s*(.+)$', frontmatter, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def frontmatter_has_key(frontmatter: str, key: str) -> bool:
    return bool(re.search(rf'^{re.escape(key)}:\s*', frontmatter, re.MULTILINE))


def check_drop_scenarios(slug: str) -> list[str]:
    """Check that Drop briefs have a ## Scenarios section.
    
    Returns list of warnings for briefs missing scenarios.
    """
    drops_dir = BUILDS_DIR / slug / "drops"
    if not drops_dir.exists():
        return []
    
    warnings = []
    for brief_path in sorted(drops_dir.glob("*.md")):
        content = brief_path.read_text()
        # Skip checkpoint briefs (C*.md)
        if brief_path.stem.startswith("C"):
            continue
        # Check for Scenarios section
        has_scenarios = re.search(r'^#{1,3}\s+Scenarios', content, re.MULTILINE)
        if not has_scenarios:
            warnings.append(f"Drop brief {brief_path.name} missing ## Scenarios section")
        else:
            # Check that scenarios have actual Given/When/Then content (not just template)
            scenario_entries = re.findall(r'^S\d+:', content, re.MULTILINE)
            template_markers = re.findall(r'<.*?descriptive name.*?>', content)
            if scenario_entries and len(scenario_entries) == len(template_markers):
                warnings.append(f"Drop brief {brief_path.name} has Scenarios section but all entries are still template placeholders")
    
    return warnings


def check_design_context(slug: str) -> list[str]:
    """Check if a build with design/frontend Drops has .impeccable.md design context.

    Soft integration with /teach-impeccable skill:
    - Scans Drop titles and briefs for design/frontend keywords
    - If design work detected, looks for .impeccable.md in referenced Sites/ dirs
    - Returns recommendations (not blockers) if design context is missing

    Returns list of recommendation strings.
    """
    build_dir = BUILDS_DIR / slug
    meta_path = build_dir / "meta.json"
    plan_path = build_dir / "PLAN.md"
    drops_dir = build_dir / "drops"

    recommendations = []

    # --- Collect all content and detect design work in one pass ---
    has_design_work = False
    all_content = ""
    meta = {}

    # Read meta.json (used for drop titles + target_project)
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text())
            for drop_info in meta.get("drops", {}).values():
                title = drop_info.get("title", "").lower()
                if DESIGN_KEYWORD_PATTERN.search(title):
                    has_design_work = True
                    break
        except (json.JSONDecodeError, KeyError):
            pass

    # Read PLAN.md
    if plan_path.exists():
        plan_content = plan_path.read_text()
        all_content += plan_content
        if not has_design_work:
            if DESIGN_KEYWORD_PATTERN.search(plan_content):
                has_design_work = True

    # Always read Drop briefs into all_content (needed for Sites/ path discovery)
    if drops_dir.exists():
        for brief_path in drops_dir.glob("*.md"):
            brief_content = brief_path.read_text()
            all_content += brief_content
            if not has_design_work:
                if DESIGN_KEYWORD_PATTERN.search(brief_content):
                    has_design_work = True

    if not has_design_work:
        return []

    # --- Find referenced project directories ---
    sites_refs = set()

    # Look for Sites/ path references in all collected content
    sites_pattern = r'Sites/([a-zA-Z0-9_-]+)'
    for match in re.finditer(sites_pattern, all_content):
        site_slug = match.group(1)
        site_path = WORKSPACE_ROOT / "Sites" / site_slug
        if site_path.exists():
            sites_refs.add(site_path)

    # Check for explicit target_project in meta.json
    target = meta.get("target_project")
    if target:
        target_path = WORKSPACE_ROOT / target
        if target_path.exists():
            sites_refs.add(target_path)

    if not sites_refs:
        # No specific project dir found — still recommend if design work detected
        recommendations.append(
            "Design/frontend work detected but no .impeccable.md found. "
            "Consider running /teach-impeccable on the target project to establish "
            "persistent design guidelines before briefing design Drops."
        )
        return recommendations

    # --- Check for .impeccable.md in referenced project dirs ---
    found_impeccable = []
    missing_impeccable = []

    for project_dir in sites_refs:
        impeccable_path = project_dir / ".impeccable.md"
        if impeccable_path.exists():
            found_impeccable.append(project_dir.name)
        else:
            missing_impeccable.append(project_dir.name)

    if missing_impeccable and not found_impeccable:
        dirs_str = ", ".join(missing_impeccable)
        recommendations.append(
            f"Design/frontend work detected but no .impeccable.md in: {dirs_str}. "
            f"Consider running /teach-impeccable to establish design guidelines "
            f"(brand personality, aesthetic direction, design principles) before "
            f"briefing design Drops."
        )
    elif found_impeccable:
        dirs_str = ", ".join(found_impeccable)
        recommendations.append(
            f"✅ Design context found (.impeccable.md) in: {dirs_str}. "
            f"Inject into design Drop briefs for consistent aesthetic guidance."
        )

    # --- Check for Stitch visual references ---
    context_dir = build_dir / "context"
    design_drop_ids = []
    if meta:
        for drop_id, drop_info in meta.get("drops", {}).items():
            title = drop_info.get("title", "")
            # Check title first
            if DESIGN_KEYWORD_PATTERN.search(title):
                design_drop_ids.append(drop_id)
                continue
            # Also check brief content for this Drop
            if drops_dir.exists():
                for bp in drops_dir.glob("*.md"):
                    if bp.stem.startswith(drop_id):
                        if DESIGN_KEYWORD_PATTERN.search(bp.read_text()):
                            design_drop_ids.append(drop_id)
                        break

    if design_drop_ids and found_impeccable:
        refs_found = 0
        refs_missing = 0
        for drop_id in design_drop_ids:
            ref_png = context_dir / f"{drop_id}-reference.png"
            ref_json = context_dir / f"{drop_id}-reference.json"
            if ref_png.exists() or ref_json.exists():
                refs_found += 1
            else:
                refs_missing += 1

        if refs_missing > 0 and refs_found == 0:
            recommendations.append(
                f"No Stitch visual references found for {len(design_drop_ids)} design Drop(s). "
                f"Consider running: python3 Skills/pulse/scripts/stitch_brief.py generate {slug}"
            )
        elif refs_found > 0 and refs_missing > 0:
            recommendations.append(
                f"Stitch references: {refs_found}/{len(design_drop_ids)} design Drops covered. "
                f"Generate remaining: python3 Skills/pulse/scripts/stitch_brief.py generate {slug}"
            )
        elif refs_found == len(design_drop_ids):
            recommendations.append(
                f"✅ Stitch visual references found for all {refs_found} design Drop(s)."
            )

    return recommendations


def check_spec_completeness(slug: str) -> list[str]:
    """Check that auto-spawn Drops have full spec completeness.
    
    Returns list of warnings for Drops with spawn_mode=auto but spec_completeness != full.
    """
    drops_dir = BUILDS_DIR / slug / "drops"
    if not drops_dir.exists():
        return []
    
    warnings = []
    for brief_path in sorted(drops_dir.glob("*.md")):
        content = brief_path.read_text()
        if brief_path.stem.startswith("C"):
            continue
        
        # Parse frontmatter
        spawn_mode = "auto"  # default
        spec_completeness = "full"  # default
        
        spawn_match = re.search(r'^spawn_mode:\s*(\S+)', content, re.MULTILINE)
        if spawn_match:
            spawn_mode = spawn_match.group(1).strip()
        
        spec_match = re.search(r'^spec_completeness:\s*(\S+)', content, re.MULTILINE)
        if spec_match:
            spec_completeness = spec_match.group(1).strip()
        
        if spawn_mode == "auto" and spec_completeness in ("partial", "ambiguous"):
            warnings.append(
                f"Drop brief {brief_path.name}: spawn_mode=auto but spec_completeness={spec_completeness} "
                f"(auto-spawn requires full spec — switch to manual or complete the spec)"
            )
    
    return warnings


def check_drop_contracts(slug: str) -> list[str]:
    """Warn when new-style code/debug Drops omit explicit runtime contracts."""
    drops_dir = BUILDS_DIR / slug / "drops"
    if not drops_dir.exists():
        return []

    warnings = []
    for brief_path in sorted(drops_dir.glob("*.md")):
        if brief_path.stem.startswith("C"):
            continue

        content = brief_path.read_text()
        frontmatter = extract_frontmatter(content)
        if not frontmatter:
            warnings.append(f"Drop brief {brief_path.name} missing YAML frontmatter")
            continue

        drop_type = frontmatter_value(frontmatter, "drop_type")
        if not drop_type:
            warnings.append(
                f"Drop brief {brief_path.name} missing drop_type "
                f"(expected one of: code, debug, checkpoint, research, docs, learning)"
            )
            continue

        if drop_type == "code":
            if not frontmatter_has_key(frontmatter, "quality_contract"):
                warnings.append(
                    f"Drop brief {brief_path.name} is drop_type=code but missing quality_contract"
                )
                continue
            if not re.search(r'^\s+check_cmd:\s*.+$', frontmatter, re.MULTILINE):
                warnings.append(
                    f"Drop brief {brief_path.name} quality_contract missing check_cmd"
                )

        if drop_type == "debug":
            if not frontmatter_has_key(frontmatter, "debug_contract"):
                warnings.append(
                    f"Drop brief {brief_path.name} is drop_type=debug but missing debug_contract"
                )
                continue
            for required_key in ("target", "symptom"):
                if not re.search(rf'^\s+{required_key}:\s*.+$', frontmatter, re.MULTILINE):
                    warnings.append(
                        f"Drop brief {brief_path.name} debug_contract missing {required_key}"
                    )

    return warnings


def find_placeholders(content: str) -> list[tuple[int, str, str]]:
    """Find unfilled placeholders in content.
    
    Returns: [(line_number, placeholder, context)]
    """
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Skip if it's in a code block showing the template itself
                if '```' in line or 'template' in line.lower():
                    continue
                # Skip HTML-like tags that are legitimate
                if pattern == r'<[A-Z_]+>' and match.group() in ['<URL>', '<ISO>']:
                    continue
                issues.append((i, match.group(), line.strip()[:60]))
    
    return issues


def check_required_sections(content: str) -> list[str]:
    """Check that required sections exist.
    
    Looks for both section headers (## Objective) and inline bold format (**Objective:**)
    """
    missing = []
    for section in REQUIRED_SECTIONS:
        # Look for markdown headers with the section name
        header_pattern = rf'^#+\s*.*{re.escape(section)}.*$'
        # Also look for bold inline format: **Objective:** followed by content
        inline_pattern = rf'\*\*{re.escape(section)}:\*\*\s*\S'
        
        has_header = re.search(header_pattern, content, re.MULTILINE | re.IGNORECASE)
        has_inline = re.search(inline_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        if not has_header and not has_inline:
            missing.append(section)
    return missing


def check_section_content(content: str) -> list[str]:
    """Check that key sections have actual content, not just headers."""
    empty_sections = []
    
    for section in CONTENT_REQUIRED:
        # Find the section header
        pattern = rf'^(#+)\s*.*{re.escape(section)}.*$'
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        if not match:
            continue
        
        # Get the header level
        header_level = len(match.group(1))
        start = match.end()
        
        # Find the next section of same or higher level
        next_section = re.search(rf'^#{{{1},{header_level}}}\s', content[start:], re.MULTILINE)
        if next_section:
            section_content = content[start:start + next_section.start()]
        else:
            section_content = content[start:]
        
        # Check if there's actual content (not just whitespace and placeholders)
        cleaned = re.sub(r'\{\{[^}]+\}\}', '', section_content)
        cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
        cleaned = cleaned.strip()
        
        if len(cleaned) < 20:  # Less than 20 chars of real content
            empty_sections.append(section)
    
    return empty_sections


def validate_plan(slug: str) -> dict:
    """Validate a build plan.
    
    Returns: {
        "valid": bool,
        "placeholders": [(line, placeholder, context)],
        "missing_sections": [str],
        "empty_sections": [str],
        "warnings": [str]
    }
    """
    plan_path = BUILDS_DIR / slug / "PLAN.md"
    
    if not plan_path.exists():
        return {
            "valid": False,
            "error": f"Plan not found: {plan_path}",
            "placeholders": [],
            "missing_sections": [],
            "empty_sections": [],
            "warnings": []
        }
    
    content = plan_path.read_text()
    
    placeholders = find_placeholders(content)
    missing_sections = check_required_sections(content)
    empty_sections = check_section_content(content)
    
    warnings = []
    
    # Check if Open Questions has unchecked items
    if re.search(r'^\s*-\s*\[\s*\]', content, re.MULTILINE):
        open_questions = re.findall(r'^\s*-\s*\[\s*\]\s*(.+)$', content, re.MULTILINE)
        if open_questions:
            warnings.append(f"{len(open_questions)} open questions still unchecked")
    
    # Check plan age
    try:
        # Look for created date in frontmatter
        created_match = re.search(r'^created:\s*(\d{4}-\d{2}-\d{2})', content, re.MULTILINE)
        if created_match:
            created = datetime.strptime(created_match.group(1), '%Y-%m-%d')
            age_days = (datetime.now() - created).days
            if age_days > 14:
                warnings.append(f"Plan is {age_days} days old — may need refresh")
    except:
        pass
    
    # Check Drop briefs for scenarios
    scenario_warnings = check_drop_scenarios(slug)
    warnings.extend(scenario_warnings)
    
    # Check spec completeness vs spawn mode consistency
    spec_warnings = check_spec_completeness(slug)
    warnings.extend(spec_warnings)

    # Check explicit code/debug contracts
    contract_warnings = check_drop_contracts(slug)
    warnings.extend(contract_warnings)

    # Check for design context (.impeccable.md) — soft integration
    design_recommendations = check_design_context(slug)

    valid = (
        len(placeholders) == 0 and
        len(missing_sections) == 0 and
        len(empty_sections) == 0
    )

    return {
        "valid": valid,
        "placeholders": placeholders,
        "missing_sections": missing_sections,
        "empty_sections": empty_sections,
        "warnings": warnings,
        "design_recommendations": design_recommendations,
    }


def print_report(slug: str, result: dict):
    """Print validation report."""
    if result.get("error"):
        print(f"❌ {result['error']}")
        return
    
    print(f"\n{'='*60}")
    print(f"Plan Validation: {slug}")
    print(f"{'='*60}\n")
    
    if result["valid"]:
        print("✅ Plan is VALID — ready for build\n")
    else:
        print("❌ Plan has ISSUES — fix before starting build\n")
    
    if result["placeholders"]:
        print(f"📝 Unfilled Placeholders ({len(result['placeholders'])}):")
        for line, placeholder, context in result["placeholders"][:10]:
            print(f"   Line {line}: {placeholder}")
            print(f"      → {context}...")
        if len(result["placeholders"]) > 10:
            print(f"   ... and {len(result['placeholders']) - 10} more")
        print()
    
    if result["missing_sections"]:
        print(f"📋 Missing Required Sections:")
        for section in result["missing_sections"]:
            print(f"   - {section}")
        print()
    
    if result["empty_sections"]:
        print(f"📭 Empty Sections (need content):")
        for section in result["empty_sections"]:
            print(f"   - {section}")
        print()
    
    if result["warnings"]:
        print(f"⚠️  Warnings:")
        for warning in result["warnings"]:
            print(f"   - {warning}")
        print()
    
    if result.get("design_recommendations"):
        print(f"🎨 Design Context:")
        for rec in result["design_recommendations"]:
            print(f"   {rec}")
        print()

    if not result["valid"]:
        print("💡 Fix these issues before running: pulse start " + slug)
        print("   Or use: python3 pulse_plan_validator.py " + slug + " --fix")


def main():
    parser = argparse.ArgumentParser(description="Validate Pulse build plan")
    parser.add_argument("slug", help="Build slug")
    parser.add_argument("--fix", action="store_true", help="Interactive mode to fix placeholders")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only output exit code")
    
    args = parser.parse_args()
    
    result = validate_plan(args.slug)
    
    if args.json:
        import json
        # Convert tuples to lists for JSON
        result["placeholders"] = [list(p) for p in result["placeholders"]]
        print(json.dumps(result, indent=2))
    elif args.quiet:
        pass
    else:
        print_report(args.slug, result)
    
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
