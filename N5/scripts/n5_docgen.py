#!/usr/bin/env python3
"""
N5 Docgen - Unified documentation generator
Version: 3.0.0 (migrated to executables.db)
Modes: --recipes (catalog), --lists (MD views), --scheduled (wrapper), --all
"""
import json, sys, re, argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from executable_manager import list_executables, Executable

from datetime import datetime, timezone
import subprocess
from n5_lists_content_extractor import extract_content_for_item

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Import safety layer
# from n5_safety import execute_with_safety, load_command_spec  # Legacy, not needed

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
RECIPES_FILE = ROOT / "data" / "executables.db"
COMMANDS_DIR = ROOT / "commands"
COMMANDS_MD = ROOT / "commands.md"
PREFS_MD = ROOT / "prefs.md"
LISTS_DIR = ROOT / "lists"
LISTS_INDEX = LISTS_DIR / "index.jsonl"

MAX_INDEX = 20

# ============================================================================
# COMMANDS MODE (original docgen functionality)
# ============================================================================

def load_schema(p: Path):
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def read_jsonl(p: Path):
    items = []
    if not p.exists():
        return items
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            ln = line.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSON on line {i} of {p}: {e}")
    return items

def read_executables_as_jsonl():
    """Load executables from DB and convert to JSONL-compatible format"""
    executables = list_executables()
    items = []
    for exe in executables:
        item = {
            "id": exe.id,
            "command": exe.name,
            "name": exe.name,
            "description": exe.description or "",
            "category": exe.category or "",
            "type": exe.type,
            "file": exe.file_path,
            "version": exe.version,
            "tags": exe.tags or []
        }
        items.append(item)
    return items

def validate_commands(cmds, schema):
    v = Draft202012Validator(schema)
    names = set()
    for i, cmd in enumerate(cmds, 1):
        errors = sorted(v.iter_errors(cmd), key=lambda e: e.path)
        if errors:
            msgs = [f"- {'.'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in errors]
            raise SystemExit("Schema validation failed for commands.jsonl:\n" + "\n".join(msgs))
        name = cmd.get("name")
        if not name:
            raise SystemExit(f"Command at index {i} missing name")
        if name in names:
            raise SystemExit(f"Duplicate command name: {name}")
        names.add(name)
    return True

def md_escape(s: str) -> str:
    return s.replace("|", "\\|")

def render_commands_table(cmds):
    headers = ["Name", "Version", "Workflow", "Summary", "Side Effects", "Permissions"]
    out = ["# N5 Command Catalog\n", "Generated from commands.jsonl. Do not edit by hand.\n\n"]
    out.append("| " + " | ".join(headers) + " |\n")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |\n")
    for c in sorted(cmds, key=lambda x: x.get("name")):
        name = c.get("name", "")
        version = c.get("version", "")
        workflow = c.get("workflow", "")
        summary = md_escape(c.get("summary", ""))
        se = ", ".join(c.get("side_effects", []) or [])
        perms = ", ".join(c.get("permissions_required", []) or [])
        link = f"[`{name}`](./{name}.md)"
        out.append(f"| {link} | {version} | {workflow} | {summary} | {md_escape(se)} | {md_escape(perms)} |\n")
    return "".join(out)

def render_command_detail(c):
    name = c["name"]
    lines = [f"# `{name}`\\n\\n", f"Version: {c.get('version','')}\\n\\n", f"Summary: {c.get('summary','')}\\n\\n"]
    if c.get("aliases"):
        lines.append(f"Aliases: {', '.join(c['aliases'])}\\n\\n")
    if c.get("workflow"):
        lines.append(f"Workflow: {c['workflow']}\\n\\n")
    if c.get("tags"):
        lines.append(f"Tags: {', '.join(c['tags'])}\\n\\n")
    if c.get("inputs"):
        lines.append("## Inputs\\n")
        for inp in c["inputs"]:
            req = " (required)" if inp.get("required") else ""
            desc = f" — {inp.get('description','')}" if inp.get('description') else ""
            default = f" [default: {inp.get('default')}]" if 'default' in inp else ""
            lines.append(f"- {inp['name']} : {inp['type']}{req}{default}{desc}\\n")
        lines.append("\\n")
    if c.get("outputs"):
        lines.append("## Outputs\\n")
        for o in c["outputs"]:
            fmt = f" ({o.get('format')})" if o.get('format') else ""
            desc = f" — {o.get('description','')}" if o.get('description') else ""
            lines.append(f"- {o['name']} : {o['type']}{fmt}{desc}\\n")
        lines.append("\\n")
    if c.get("uses"):
        lines.append("## Uses\\n")
        if c["uses"].get("modules"):
            module_links = []
            for mod in c["uses"]["modules"]:
                module_links.append(f"[`{mod}`](../modules/{mod}.md)")
            lines.append(f"- **Modules**: {', '.join(module_links)}\\n")
        if c["uses"].get("commands"):
            cmd_links = []
            for cmd in c["uses"]["commands"]:
                cmd_links.append(f"[`{cmd}`](../commands/{cmd}.md)")
            lines.append(f"- **Commands**: {', '.join(cmd_links)}\\n")
        lines.append("\\n")
    if c.get("steps"):
        lines.append("## Steps\\n")
        for s in c["steps"]:
            with_map = ", ".join(f"{k}={v}" for k, v in (s.get("with") or {}).items())
            lines.append(f"- {s['ref']} {with_map}\\n")
        lines.append("\\n")
    if c.get("side_effects"):
        lines.append("## Side Effects\\n- " + "\\n- ".join(c["side_effects"]) + "\\n\\n")
    if c.get("permissions_required"):
        lines.append("## Permissions Required\\n- " + "\\n- ".join(c["permissions_required"]) + "\\n\\n")
    if c.get("examples"):
        lines.append("## Examples\\n")
        for ex in c["examples"]:
            lines.append(f"- {ex}\\n")
        lines.append("\\n")
    if c.get("failure_modes"):
        lines.append("## Failure Modes\\n- " + "\\n- ".join(c["failure_modes"]) + "\\n\\n")
    
    # Add Related Components section
    lines.append("## Related Components\\n\\n")
    
    # Add links to related commands based on workflow and tags
    workflow = c.get("workflow", "")
    tags = c.get("tags", [])
    
    related_commands = []
    if workflow == "lists":
        related_commands = ["lists-create", "lists-add", "lists-set", "lists-find", "lists-export", "lists-promote", "docgen"]
    elif workflow == "knowledge":
        related_commands = ["knowledge-add", "knowledge-find"]
    elif workflow == "ops":
        related_commands = ["docgen", "index-update", "index-rebuild", "digest-runs"]
    elif workflow == "misc":
        related_commands = ["flow-run"]
    
    # Remove self from related commands
    if name in related_commands:
        related_commands.remove(name)
    
    if related_commands:
        cmd_links = [f"[`{cmd}`](../commands/{cmd}.md)" for cmd in related_commands[:5]]  # Limit to 5
        lines.append(f"**Related Commands**: {', '.join(cmd_links)}\\n\\n")
    
    # Add knowledge links based on tags
    knowledge_links = []
    if "lists" in tags:
        knowledge_links.append("[List Management](../knowledge/list-management.md)")
    if "knowledge" in tags:
        knowledge_links.append("[Knowledge Base](../knowledge/knowledge-base.md)")
    if "index" in tags:
        knowledge_links.append("[System Architecture](../knowledge/system-architecture.md)")
    
    if knowledge_links:
        lines.append(f"**Knowledge Areas**: {', '.join(knowledge_links)}\\n\\n")
    
    # Add examples link
    lines.append(f"**Examples**: See [Examples Library](../examples/) for usage patterns\\n\\n")
    
    return "".join(lines)

def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    old = None
    if path.exists():
        old = path.read_text(encoding="utf-8")
    if old != content:
        path.write_text(content, encoding="utf-8")

def update_prefs_command_index(cmds):
    if not PREFS_MD.exists():
        return
    lines = PREFS_MD.read_text(encoding="utf-8").splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## command index"):
            start = i
            break
    top = sorted(cmds, key=lambda c: c.get("name"))[:MAX_INDEX]
    section = [lines[start] if start is not None else "## Command Index (top)"]
    section.append("")
    for c in top:
        section.append(f"- `{c['name']}` — {c.get('summary','')} (see ./commands/{c['name']}.md)")
    section.append("")
    # find next header
    if start is None:
        # append
        new_content = "\n".join(lines + [""] + section + [""])
    else:
        end = len(lines)
        for j in range(start + 1, len(lines)):
            if re.match(r"^## ", lines[j]):
                end = j
                break
        new_content = "\n".join(lines[:start] + section + lines[end:])
    write(PREFS_MD, new_content)

def generate_commands_catalog(dry_run=False):
    """Generate command catalog from commands.jsonl"""
    artifacts = []
    
    schema = load_schema(SCHEMAS / "commands.schema.json")
    cmds = read_executables_as_jsonl()
    if not cmds:
        print("No commands in commands.jsonl; nothing to generate.")
        return artifacts

    validate_commands(cmds, schema)

    if dry_run:
        print(f"[DRY RUN] Would generate {COMMANDS_MD} and {len(cmds)} detail files")
        return artifacts

    # write catalog
    catalog = render_commands_table(cmds)
    write(COMMANDS_MD, catalog)
    artifacts.append(str(COMMANDS_MD))

    # write details
    for c in cmds:
        detail = render_command_detail(c)
        write(COMMANDS_DIR / f"{c['name']}.md", detail)
        artifacts.append(str(COMMANDS_DIR / f"{c['name']}.md"))

    # update prefs index
    update_prefs_command_index(cmds)
    artifacts.append(str(PREFS_MD))

    print(f"✓ Commands catalog complete: {COMMANDS_MD} and {len(cmds)} detail files")
    
    return artifacts

# ============================================================================
# LISTS MODE (original lists-docgen functionality)
# ============================================================================

def md_escape_lists(s: str) -> str:
    """MD escape for lists mode"""
    return s.replace("|", "\\|").replace("\n", " ").replace("\r", "")

def render_list_md(title, items):
    """Render list items as markdown"""
    lines = [f"# {title}\n\n<!-- Generated MD view of JSONL -->\n\n"]
    if not items:
        lines.append("No items.\n\n")
        return "".join(lines)

    # Group by status
    groups = {}
    for item in items:
        status = item.get("status", "open")
        groups.setdefault(status, []).append(item)

    for status in ["open", "pinned", "done", "archived"]:
        if status not in groups:
            continue
        lines.append(f"## {status.title()}\n\n")
        for item in sorted(groups[status], key=lambda x: x.get("created_at", "")):
            lines.append(f"### {md_escape_lists(item['title'])}\n\n")
            lines.append(f"**ID:** {item['id']}\n\n")
            lines.append(f"**Created:** {item.get('created_at', 'N/A')}\n\n")
            if item.get("updated_at") and item["updated_at"] != item.get("created_at"):
                lines.append(f"**Updated:** {item['updated_at']}\n\n")
            if item.get("priority"):
                lines.append(f"**Priority:** {item['priority']}\n\n")
            if item.get("tags"):
                lines.append(f"**Tags:** {', '.join(item['tags'])}\n\n")
            if item.get("project"):
                lines.append(f"**Project:** {item['project']}\n\n")
            if item.get("due"):
                lines.append(f"**Due:** {item['due']}\n\n")
            if item.get("body"):
                lines.append(f"**Body:**\n\n{item['body']}\n\n")
            if extract_content_for_item is not None and item.get("links"):
                lines.append("### 📄 Linked Content\n\n")
                content = extract_content_for_item(item, ROOT.parent)
                if content:
                    lines.append(content)
                else:
                    lines.append("No content available for this item.\n\n")

            if item.get("notes"):
                lines.append(f"**Notes:** {item['notes']}\n\n")
            lines.append("---\n\n")
        lines.append("\n")

    return "".join(lines)

def generate_lists_views(list_slug=None, dry_run=False):
    """Generate MD views for lists from JSONL"""
    artifacts = []
    
    registry = read_jsonl(LISTS_INDEX)
    if not registry:
        print("No lists in registry.")
        return artifacts

    lists_to_process = registry
    if list_slug:
        lists_to_process = [r for r in registry if r.get("slug") == list_slug]
        if not lists_to_process:
            raise SystemExit(f"List '{list_slug}' not found")

    for reg in lists_to_process:
        slug = reg["slug"]
        title = reg["title"]
        jsonl_file = LISTS_DIR / f"{slug}.jsonl"
        md_file = LISTS_DIR / f"{slug}.md"

        items = read_jsonl(jsonl_file)
        md_content = render_list_md(title, items)

        if dry_run:
            print(f"[DRY RUN] Would generate MD for '{slug}': {md_file}")
        else:
            md_file.parent.mkdir(parents=True, exist_ok=True)
            md_file.write_text(md_content, encoding="utf-8")
            artifacts.append(str(md_file))
            print(f"✓ Generated MD for '{slug}': {md_file}")

    return artifacts

# ============================================================================
# SCHEDULED MODE (wrapper functionality)
# ============================================================================

def run_with_scheduling_wrapper(mode_args):
    """Run docgen through the scheduling wrapper"""
    wrapper_script = ROOT / "scripts" / "n5_schedule_wrapper.py"
    if not wrapper_script.exists():
        raise SystemExit(f"Scheduling wrapper not found: {wrapper_script}")

    # Build command: wrapper + docgen + mode args
    command = [sys.executable, str(wrapper_script), "docgen"] + mode_args

    print(f"Running docgen with scheduling wrapper...")
    result = subprocess.run(command, capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)

    return result.returncode

# ============================================================================
# RUN RECORDING
# ============================================================================

def record_run(inputs, layers_used, status="success", artifacts=None, errors=None):
    """Record the run using the run recorder script."""
    config = {
        "inputs": inputs,
        "layers_used": layers_used,
        "status": status,
        "artifacts": artifacts or [],
        "errors": errors or []
    }

    try:
        result = subprocess.run([
            sys.executable, str(ROOT / "scripts" / "n5_run_record.py"), "docgen"
        ], input=json.dumps(config), text=True, capture_output=True)

        if result.returncode == 0:
            run_file = result.stdout.strip()
            return run_file
        else:
            print(f"Warning: Run recording failed: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Warning: Failed to record run: {e}", file=sys.stderr)
        return None

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="N5 Docgen - Unified documentation generator",
        epilog="Examples:\n"
               "  docgen --commands              Generate command catalog\n"
               "  docgen --lists                 Generate all list MD views\n"
               "  docgen --lists --list ideas    Generate single list\n"
               "  docgen --all                   Generate everything\n"
               "  docgen --scheduled --commands  Run with scheduling wrapper\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Mode selection
    parser.add_argument("--commands", action="store_true", help="Generate command catalog (commands.jsonl → catalog)")
    parser.add_argument("--lists", action="store_true", help="Generate list MD views (JSONL → MD)")
    parser.add_argument("--all", action="store_true", help="Generate everything (commands + lists)")
    parser.add_argument("--scheduled", action="store_true", help="Run with scheduling wrapper (retry/lock/timezone)")
    
    # Options
    parser.add_argument("--list", metavar="SLUG", help="Specific list slug (for --lists mode)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--use-wrapper", action="store_true", help="Deprecated: use --scheduled instead")

    args = parser.parse_args()

    # Handle deprecated --use-wrapper flag
    if args.use_wrapper:
        print("Warning: --use-wrapper is deprecated, use --scheduled instead", file=sys.stderr)
        args.scheduled = True

    # Default to --commands if no mode specified
    if not (args.commands or args.lists or args.all or args.scheduled):
        args.commands = True

    # Handle --all mode
    if args.all:
        args.commands = True
        args.lists = True

    # Handle --scheduled mode: re-invoke through wrapper
    if args.scheduled:
        # Build mode args to pass through wrapper
        mode_args = []
        if args.commands:
            mode_args.append("--commands")
        if args.lists:
            mode_args.append("--lists")
        if args.list:
            mode_args.extend(["--list", args.list])
        if args.dry_run:
            mode_args.append("--dry-run")
        
        return run_with_scheduling_wrapper(mode_args)

    # Load command spec for safety checks
    # command_spec = load_command_spec("docgen")  # Legacy

    def execute_docgen(args):
        inputs = {
            "commands": args.commands,
            "lists": args.lists,
            "list_slug": args.list,
            "dry_run": args.dry_run
        }
        layers_used = ["jsonschema", "pathlib", "datetime"]
        artifacts = []
        errors = []
        status = "success"

        try:
            # Execute commands mode
            if args.commands:
                print(f"[MODE: commands] Generating command catalog...")
                cmd_artifacts = generate_commands_catalog(dry_run=args.dry_run)
                artifacts.extend(cmd_artifacts)

            # Execute lists mode
            if args.lists:
                print(f"[MODE: lists] Generating list MD views...")
                list_artifacts = generate_lists_views(list_slug=args.list, dry_run=args.dry_run)
                artifacts.extend(list_artifacts)

            if not args.dry_run:
                print(f"\n✓ Docgen complete: {len(artifacts)} files updated")
            else:
                print(f"\n[DRY RUN] Would update {len(artifacts)} files")

        except Exception as e:
            errors.append(str(e))
            status = "error"
            raise

        finally:
            # Record the run
            if not args.dry_run:
                run_file = record_run(inputs, layers_used, status, artifacts, errors)
                if run_file:
                    print(f"Run recorded: {run_file}")

    # Execute with safety layer
    # result = execute_with_safety(command_spec, args, execute_docgen)  # Legacy
    execute_docgen(args)
    return 0
    return result

if __name__ == "__main__":
    main()
