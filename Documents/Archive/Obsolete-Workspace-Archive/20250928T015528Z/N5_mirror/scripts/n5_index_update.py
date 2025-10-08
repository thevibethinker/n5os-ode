#!/usr/bin/env python3
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import hashlib
import mimetypes
import fcntl

try:
    from jsonschema import Draft202012Validator
except Exception as e:
    print("ERROR: jsonschema not installed. Install with: pip install jsonschema", file=sys.stderr)
    sys.exit(1)

"""N5 Index Update Script

Incremental indexer for N5 OS that updates the index with changed files.
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

def load_existing_index() -> dict:
    """Load existing index as dict of path -> entry."""
    index = {}
    if not INDEX_FILE.exists():
        return index
    with INDEX_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            ln = line.strip()
            if not ln:
                continue
            entry = json.loads(ln)
            index[entry["path"]] = entry
    return index

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

def scan_file(path: Path, relative: str, existing_entry=None):
    """Scan a single file and return index entry."""
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    size = stat.st_size
    kind = get_file_kind(path)
    file_hash = get_file_hash(path)
    
    # check if changed
    if existing_entry and existing_entry.get("hash") == file_hash and existing_entry.get("mtime") == mtime:
        return existing_entry  # no change
    
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

def update_index():
    """Incremental update of index."""
    # Acquire lock on index file
    lock_file = INDEX_FILE.with_suffix('.lock')
    with lock_file.open('w') as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            existing = load_existing_index()
            updated = []
            removed = []
            
            # scan all files
            all_files = set()
            for path in ROOT.rglob("*"):
                if path.is_file():
                    relative = str(path.relative_to(ROOT))
                    if should_exclude(path, relative):
                        continue
                    all_files.add(relative)
                    entry = scan_file(path, relative, existing.get(relative))
                    if entry != existing.get(relative):
                        updated.append(entry)
            
            # find removed
            for rel in existing:
                if rel not in all_files:
                    removed.append(rel)
            
            # write new index
            new_index = {}
            for rel, entry in existing.items():
                if rel not in removed:
                    new_index[rel] = entry
            
            for entry in updated:
                new_index[entry["path"]] = entry
            
            with INDEX_FILE.open("w", encoding="utf-8") as f:
                for entry in sorted(new_index.values(), key=lambda x: x["path"]):
                    json.dump(entry, f, ensure_ascii=False)
                    f.write("\n")
            
            return len(updated), len(removed)
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
            lock_file.unlink(missing_ok=True)

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
            sys.executable, str(ROOT / "scripts" / "n5_run_record.py"), "index-update"
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
    inputs = {}
    layers_used = ["pathlib", "json", "hashlib", "datetime", "jsonschema"]
    artifacts = [str(INDEX_FILE)]
    errors = []
    status = "success"
    
    try:
        updated, removed = update_index()
        print(f"Index update complete. Updated: {updated}, Removed: {removed}")
        
    except Exception as e:
        errors.append(str(e))
        status = "error"
        raise
    
    finally:
        run_file = record_run(inputs, layers_used, status, artifacts, errors)
        if run_file:
            print(f"Run recorded: {run_file}")

if __name__ == "__main__":
    main()