#!/usr/bin/env python3
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import hashlib
import argparse
import fcntl

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

# Import safety layer
from n5_safety import execute_with_safety, load_command_spec

"""N5 Index Rebuild Script

Rebuilds the N5 index from scratch, scanning all files and regenerating MD view.
"""

ROOT = Path(__file__).resolve().parents[1]
INDEX_FILE = ROOT / "index.jsonl"
INDEX_MD = ROOT / "index.md"
COMMANDS_FILE = ROOT / "commands.jsonl"
SCHEMAS = ROOT / "schemas"

EXCLUDE_PATTERNS = [
    ".git",
    "node_modules",
    "__pycache__",
    ".DS_Store",
    "*.pyc",
    "*.log",
    "*.tmp",
    "runtime/runs",  # exclude run records
    "exports",  # maybe exclude exports
]

def should_exclude(path: Path, relative: str) -> bool:
    """Check if path should be excluded."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in relative:
            return True
        if path.match(pattern):
            return True
    return False

def get_file_kind(path: Path) -> str:
    """Determine file kind."""
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "doc"
    elif suffix in [".jsonl", ".json"] or ".sheet.json" in str(path):
        return "sheet"
    elif suffix in [".py", ".js", ".sh", ".ts"]:
        return "code"
    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".mp4", ".avi"]:
        return "media"
    elif "service" in str(path) or suffix in [".service", ".yaml", ".yml"]:
        return "service"
    else:
        # check if text
        try:
            with path.open("rb") as f:
                data = f.read(1024)
                if b'\0' in data:
                    return "media"  # binary
                else:
                    return "note"
        except:
            return "note"

def get_file_hash(path: Path) -> str:
    """Get file hash for change detection."""
    hash_md5 = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_entrypoints():
    """Get entrypoints from commands.jsonl."""
    entrypoints = set()
    if not COMMANDS_FILE.exists():
        return entrypoints
    with COMMANDS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            ln = line.strip()
            if not ln:
                continue
            cmd = json.loads(ln)
            name = cmd.get("name")
            if name:
                script_name = name.replace("-", "_")
                entrypoints.add(f"scripts/n5_{script_name}.py")
                # also add aliases if any
                for alias in cmd.get("aliases", []):
                    alias_script = alias.replace("-", "_")
                    entrypoints.add(f"scripts/n5_{alias_script}.py")
    return entrypoints

def scan_file(path: Path, relative: str):
    """Scan a single file and return index entry."""
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    size = stat.st_size
    kind = get_file_kind(path)
    file_hash = get_file_hash(path)
    
    # summary: extract from file content
    summary = ""
    if kind == "doc" and path.suffix == ".md":
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        summary = line[2:]
                        break
        except:
            pass
    elif kind == "code":
        if path.suffix == ".py":
            # Look for module docstring
            try:
                with path.open("r", encoding="utf-8") as f:
                    content = f.read()
                    # Find triple-quoted string after imports
                    import_end = content.find("\n\n")
                    if import_end != -1:
                        after_imports = content[import_end:]
                        # Find first """
                        start = after_imports.find('"""')
                        if start != -1:
                            end = after_imports.find('"""', start + 3)
                            if end != -1:
                                summary = after_imports[start + 3:end].strip().split('\n')[0]
            except:
                pass
        else:
            # For other code, look for first comment
            try:
                with path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#") and not line.startswith("#!"):
                            summary = line[1:].strip()
                            break
            except:
                pass
    if not summary:
        summary = path.name
    
    # tags: infer from path
    tags = []
    if "knowledge" in relative:
        tags.append("knowledge")
    if "lists" in relative:
        tags.append("lists")
    if "scripts" in relative:
        tags.append("scripts")
    if "commands" in relative:
        tags.append("commands")
    
    entrypoints = get_entrypoints()
    is_entrypoint = relative in entrypoints
    
    entry = {
        "path": relative,
        "kind": kind,
        "tags": tags,
        "summary": summary[:220],  # max 220
        "mtime": mtime,
        "size": size,
        "is_entrypoint": is_entrypoint,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "hash": file_hash
    }
    
    if is_entrypoint:
        entry["entrypoints"] = [relative]
    
    return entry

def rebuild_index():
    """Rebuild index from scratch."""
    # Acquire lock on index file
    lock_file = INDEX_FILE.with_suffix('.lock')
    with lock_file.open('w') as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            entries = []
            
            for path in ROOT.rglob("*"):
                if path.is_file():
                    relative = str(path.relative_to(ROOT))
                    if should_exclude(path, relative):
                        continue
                    entry = scan_file(path, relative)
                    entries.append(entry)
            
            # write index
            with INDEX_FILE.open("w", encoding="utf-8") as f:
                for entry in sorted(entries, key=lambda x: x["path"]):
                    json.dump(entry, f, ensure_ascii=False)
                    f.write("\n")
            
            return len(entries)
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
            lock_file.unlink(missing_ok=True)

def regenerate_md():
    """Regenerate index.md from index.jsonl."""
    if not INDEX_FILE.exists():
        print("Index file not found, cannot regenerate MD.")
        return
    
    entries = []
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            ln = line.strip()
            if ln:
                entries.append(json.loads(ln))
    
    # group by kind
    grouped = {}
    for entry in entries:
        kind = entry["kind"]
        if kind not in grouped:
            grouped[kind] = []
        grouped[kind].append(entry)
    
    lines = ["# N5 OS Index\n\n", "Generated from index.jsonl. Do not edit by hand.\n\n"]
    
    for kind in ["doc", "sheet", "code", "note", "media", "service"]:
        if kind in grouped:
            lines.append(f"## {kind.capitalize()} Files\n\n")
            for entry in sorted(grouped[kind], key=lambda x: x["path"]):
                path = entry["path"]
                summary = entry["summary"]
                tags = ", ".join(entry.get("tags", []))
                ep = " (entrypoint)" if entry.get("is_entrypoint") else ""
                lines.append(f"- [{path}](./{path}) — {summary}{ep}\n")
                if tags:
                    lines.append(f"  - Tags: {tags}\n")
            lines.append("\n")
    
    # entrypoints section
    entrypoints = [e for e in entries if e.get("is_entrypoint")]
    if entrypoints:
        lines.append("## Entrypoints\n\n")
        for ep in sorted(entrypoints, key=lambda x: x["path"]):
            lines.append(f"- [{ep['path']}](./{ep['path']}) — {ep['summary']}\n")
        lines.append("\n")
    
    with INDEX_MD.open("w", encoding="utf-8") as f:
        f.write("".join(lines))

def validate_index():
    """Validate index against schema."""
    if not INDEX_FILE.exists():
        return
    schema_path = SCHEMAS / "index.schema.json"
    if not schema_path.exists():
        print("Warning: Index schema not found, skipping validation.")
        return
    with schema_path.open("r", encoding="utf-8") as f:
        schema = json.load(f)
    validator = Draft202012Validator(schema)
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            ln = line.strip()
            if not ln:
                continue
            try:
                entry = json.loads(ln)
                errors = list(validator.iter_errors(entry))
                if errors:
                    print(f"Validation error on line {i}: {errors}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON on line {i}: {e}")

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
            sys.executable, str(ROOT / "scripts" / "n5_run_record.py"), "index-rebuild"
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
    parser = argparse.ArgumentParser(description="Rebuild N5 index from scratch")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    args = parser.parse_args()

    # Load command spec for safety checks
    command_spec = load_command_spec("index-rebuild")

    def execute_index_rebuild(args):
        inputs = {}
        layers_used = ["pathlib", "json", "hashlib", "datetime", "jsonschema"]
        artifacts = [str(INDEX_FILE), str(INDEX_MD)]
        errors = []
        status = "success"

        try:
            count = rebuild_index()
            print(f"Index rebuild complete. Scanned {count} files.")

            regenerate_md()
            print("MD view regenerated.")

            validate_index()

        except Exception as e:
            errors.append(str(e))
            status = "error"
            raise

        finally:
            run_file = record_run(inputs, layers_used, status, artifacts, errors)
            if run_file:
                print(f"Run recorded: {run_file}")

    # Execute with safety layer
    result = execute_with_safety(command_spec, args, execute_index_rebuild)
    return result

if __name__ == "__main__":
    main()