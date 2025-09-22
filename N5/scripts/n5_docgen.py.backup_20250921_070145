#!/usr/bin/env python3
import json, sys, re, argparse
from pathlib import Path
from datetime import datetime, timezone
import subprocess

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Import safety layer
from n5_safety import execute_with_safety, load_command_spec

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
COMMANDS_FILE = ROOT / "commands.jsonl"
COMMANDS_DIR = ROOT / "commands"
COMMANDS_MD = ROOT / "commands.md"
PREFS_MD = ROOT / "prefs.md"

MAX_INDEX = 20

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
        related_commands = ["lists-create", "lists-add", "lists-set", "lists-find", "lists-docgen", "lists-export", "lists-promote"]
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

def main():
    parser = argparse.ArgumentParser(description="Generate N5 command documentation")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--use-wrapper", action="store_true", help="Use scheduling wrapper (opt-in)")

    args = parser.parse_args()

    # Load command spec for safety checks
    command_spec = load_command_spec("docgen")

    def execute_docgen(args):
        # Inputs for run recording
        inputs = {}
        layers_used = ["jsonschema", "pathlib", "datetime"]
        artifacts = []
        errors = []
        status = "success"

        try:
            schema = load_schema(SCHEMAS / "commands.schema.json")
            cmds = read_jsonl(COMMANDS_FILE)
            if not cmds:
                print("No commands in commands.jsonl; nothing to generate.")
                return

            validate_commands(cmds, schema)

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

            print(f"Docgen complete. Wrote {COMMANDS_MD} and {len(cmds)} detail files.")

        except Exception as e:
            errors.append(str(e))
            status = "error"
            raise

        finally:
            # Record the run
            run_file = record_run(inputs, layers_used, status, artifacts, errors)
            if run_file:
                print(f"Run recorded: {run_file}")

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_docgen)
    return result

if __name__ == "__main__":
    main()