#!/usr/bin/env python3
"""
Multi-Layer Dependency Parser for N5OS

Scans the workspace and extracts typed dependency relationships across six layers:
1. Python imports (AST-based)
2. Subprocess/os.system calls (AST-based)
3. Config references (commands.jsonl, YAML, JSON configs)
4. Prompt references (.prompt.md files)
5. Skill wiring (SKILL.md files)
6. Pulse meta.json (build orchestration references)

Returns raw edges only — graph construction is handled by graph_builder.py (D1.2).
"""

import ast
import json
import os
import re
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

EXCLUDE_PATTERNS = [
    "logs/", ".backups/", ".EXPUNGED/",
    "node_modules/", "state/", "Trash/",
    "__pycache__/", "completions/", ".git/",
    "venv/", ".venv/", "dist/",
    "Temp/", "zoputer-substrate/", "Build Exports/",
]

PYTHON_SCAN_ROOTS = ["N5", "Skills", "Integrations"]
PROMPT_SCAN_ROOTS = ["Prompts", "N5", "Skills"]
ROOT_LEVEL_PROMPTS = ["BOOTLOADER.prompt.md", "WALKTHROUGH.prompt.md"]

SCRIPT_PATH_RE = re.compile(
    r'(?:python3?\s+)?(?:/home/workspace/)?'
    r'((?:N5|Skills|Prompts|Integrations)/[\w/.+-]+\.py)\b'
)

FILE_REF_RE = re.compile(
    r'(?:/home/workspace/)?'
    r'((?:N5|Skills|Prompts|Integrations|Knowledge|Personal)/[\w/.+-]+\.\w+)\b'
)

SUBPROCESS_FUNCS = {
    'subprocess.run', 'subprocess.call', 'subprocess.check_call',
    'subprocess.check_output', 'subprocess.Popen',
    'os.system', 'os.popen',
}


def _should_exclude(rel_path: str) -> bool:
    for pattern in EXCLUDE_PATTERNS:
        if f"/{pattern}" in f"/{rel_path}/" or rel_path.startswith(pattern):
            return True
    return False


def _make_edge(
    source: str,
    target: str,
    edge_type: str,
    source_type: str,
    target_type: str,
    line: Optional[int],
    confidence: str,
    detail: str,
) -> dict:
    return {
        "source": source,
        "target": target,
        "type": edge_type,
        "source_type": source_type,
        "target_type": target_type,
        "line": line,
        "confidence": confidence,
        "detail": detail,
    }


def _resolve_import_to_path(module_name: str, root: str) -> Optional[str]:
    parts = module_name.split(".")
    candidate = os.path.join(*parts) + ".py"
    if os.path.isfile(os.path.join(root, candidate)):
        return candidate
    pkg_init = os.path.join(*parts, "__init__.py")
    if os.path.isfile(os.path.join(root, pkg_init)):
        return pkg_init
    return None


def _classify_file(rel_path: str) -> str:
    if rel_path.endswith(".prompt.md"):
        return "PROMPT"
    if "SKILL.md" in rel_path:
        return "SKILL"
    if rel_path.endswith(".py"):
        return "SCRIPT"
    if rel_path.startswith("N5/config/") or rel_path.endswith((".json", ".jsonl", ".yaml", ".yml")):
        return "CONFIG"
    return "CONFIG"


def _extract_string_from_node(node: ast.expr) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _get_func_name(node: ast.Call) -> Optional[str]:
    if isinstance(node.func, ast.Attribute):
        if isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
        if isinstance(node.func.value, ast.Attribute) and isinstance(node.func.value.value, ast.Name):
            return f"{node.func.value.value.id}.{node.func.value.attr}.{node.func.attr}"
    elif isinstance(node.func, ast.Name):
        return node.func.id
    return None


def parse_python_imports(filepath: str, rel_path: str, root: str) -> list[dict]:
    edges = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=filepath)
    except (SyntaxError, ValueError) as e:
        logger.warning("Skipping %s: parse error: %s", rel_path, e)
        return edges

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            target = _resolve_import_to_path(node.module, root)
            if target and target != rel_path:
                names = [alias.name for alias in node.names]
                detail = f"imports {', '.join(names[:3])}" + ("..." if len(names) > 3 else "")
                edges.append(_make_edge(
                    source=rel_path, target=target, edge_type="IMPORTS",
                    source_type="SCRIPT", target_type="SCRIPT",
                    line=node.lineno, confidence="high", detail=detail,
                ))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                target = _resolve_import_to_path(alias.name, root)
                if target and target != rel_path:
                    edges.append(_make_edge(
                        source=rel_path, target=target, edge_type="IMPORTS",
                        source_type="SCRIPT", target_type="SCRIPT",
                        line=node.lineno, confidence="high",
                        detail=f"imports {alias.name}",
                    ))
    return edges


def parse_python_subprocess(filepath: str, rel_path: str, root: str) -> list[dict]:
    edges = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=filepath)
    except (SyntaxError, ValueError):
        return edges

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = _get_func_name(node)
        if not func_name or func_name not in SUBPROCESS_FUNCS:
            continue

        strings = []
        for arg in node.args:
            if isinstance(arg, ast.List):
                for elt in arg.elts:
                    s = _extract_string_from_node(elt)
                    if s:
                        strings.append(s)
            else:
                s = _extract_string_from_node(arg)
                if s:
                    strings.append(s)
        for kw in node.keywords:
            s = _extract_string_from_node(kw.value)
            if s:
                strings.append(s)

        combined = " ".join(strings)
        for match in SCRIPT_PATH_RE.finditer(combined):
            target = match.group(1)
            if os.path.isfile(os.path.join(root, target)):
                edges.append(_make_edge(
                    source=rel_path, target=target, edge_type="CALLS_SUBPROCESS",
                    source_type="SCRIPT", target_type="SCRIPT",
                    line=node.lineno, confidence="high",
                    detail=f"subprocess via {func_name}",
                ))
    return edges


def parse_python_string_refs(filepath: str, rel_path: str, root: str) -> list[dict]:
    edges = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source_code = f.read()
        tree = ast.parse(source_code, filename=filepath)
    except (SyntaxError, ValueError):
        return edges

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value
            if "/home/workspace/" in val:
                val = val.replace("/home/workspace/", "")
            m = SCRIPT_PATH_RE.search(val)
            if m:
                target = m.group(1)
                if target != rel_path and os.path.isfile(os.path.join(root, target)):
                    edges.append(_make_edge(
                        source=rel_path, target=target, edge_type="CALLS_SUBPROCESS",
                        source_type="SCRIPT", target_type="SCRIPT",
                        line=getattr(node, "lineno", None), confidence="medium",
                        detail=f"string reference to {target}",
                    ))
    return edges


def parse_config_commands_jsonl(root: str) -> list[dict]:
    edges = []
    commands_path = os.path.join(root, "N5/config/commands.jsonl")
    if not os.path.isfile(commands_path):
        return edges

    rel_source = "N5/config/commands.jsonl"
    try:
        with open(commands_path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                file_path = entry.get("file_path") or entry.get("file")
                if file_path and os.path.isfile(os.path.join(root, file_path)):
                    target_type = _classify_file(file_path)
                    cmd_name = entry.get("id") or entry.get("name", "unknown")
                    edges.append(_make_edge(
                        source=rel_source, target=file_path, edge_type="CONFIG_REF",
                        source_type="CONFIG", target_type=target_type,
                        line=lineno, confidence="high",
                        detail=f"command '{cmd_name}' references {file_path}",
                    ))
    except Exception as e:
        logger.warning("Error parsing commands.jsonl: %s", e)
    return edges


def parse_config_files(root: str) -> list[dict]:
    edges = []
    config_dir = os.path.join(root, "N5/config")
    if not os.path.isdir(config_dir):
        return edges

    for fname in os.listdir(config_dir):
        fpath = os.path.join(config_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if fname == "commands.jsonl":
            continue

        rel_source = f"N5/config/{fname}"
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        seen = set()
        for match in SCRIPT_PATH_RE.finditer(content):
            target = match.group(1)
            if target in seen:
                continue
            seen.add(target)
            if os.path.isfile(os.path.join(root, target)):
                edges.append(_make_edge(
                    source=rel_source, target=target, edge_type="CONFIG_REF",
                    source_type="CONFIG", target_type=_classify_file(target),
                    line=None, confidence="medium",
                    detail=f"config references {target}",
                ))
    return edges


def parse_prompt_files(root: str) -> list[dict]:
    edges = []
    prompt_files: list[tuple[str, str]] = []

    for rel_root in PROMPT_SCAN_ROOTS:
        abs_root = os.path.join(root, rel_root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [d for d in dirnames if not _should_exclude(
                os.path.relpath(os.path.join(dirpath, d), root)
            )]
            for fname in filenames:
                if not fname.endswith(".prompt.md"):
                    continue
                fpath = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(fpath, root)
                if _should_exclude(rel_path):
                    continue
                prompt_files.append((fpath, rel_path))

    for fname in ROOT_LEVEL_PROMPTS:
        fpath = os.path.join(root, fname)
        if os.path.isfile(fpath):
            prompt_files.append((fpath, fname))

    seen_prompt_paths = set()
    for fpath, rel_path in prompt_files:
        if rel_path in seen_prompt_paths:
            continue
        seen_prompt_paths.add(rel_path)

        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        seen = set()
        for match in SCRIPT_PATH_RE.finditer(content):
            target = match.group(1)
            if target in seen:
                continue
            seen.add(target)
            if os.path.isfile(os.path.join(root, target)):
                edges.append(_make_edge(
                    source=rel_path, target=target, edge_type="PROMPT_REF",
                    source_type="PROMPT", target_type=_classify_file(target),
                    line=None, confidence="medium",
                    detail=f"prompt references {target}",
                ))
    return edges


def parse_skill_files(root: str) -> list[dict]:
    edges = []
    skills_dir = os.path.join(root, "Skills")
    if not os.path.isdir(skills_dir):
        return edges

    for dirpath, dirnames, filenames in os.walk(skills_dir):
        dirnames[:] = [d for d in dirnames if not _should_exclude(
            os.path.relpath(os.path.join(dirpath, d), root)
        )]
        for fname in filenames:
            if fname != "SKILL.md":
                continue
            fpath = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(fpath, root)
            if _should_exclude(rel_path):
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            seen = set()
            for match in FILE_REF_RE.finditer(content):
                target = match.group(1)
                if target in seen or target == rel_path:
                    continue
                seen.add(target)
                if target.endswith(".py") and os.path.isfile(os.path.join(root, target)):
                    edges.append(_make_edge(
                        source=rel_path, target=target, edge_type="SKILL_REF",
                        source_type="SKILL", target_type="SCRIPT",
                        line=None, confidence="medium",
                        detail=f"SKILL.md references {target}",
                    ))
    return edges


def parse_pulse_meta(root: str) -> list[dict]:
    edges = []
    builds_dir = os.path.join(root, "N5/builds")
    if not os.path.isdir(builds_dir):
        return edges

    for build_name in os.listdir(builds_dir):
        meta_path = os.path.join(builds_dir, build_name, "meta.json")
        if not os.path.isfile(meta_path):
            continue

        rel_source = f"N5/builds/{build_name}/meta.json"
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Skipping %s: %s", meta_path, e)
            continue

        drops = meta.get("drops", {})
        if not isinstance(drops, dict):
            continue
        for drop_id, drop_data in drops.items():
            if not isinstance(drop_data, dict):
                continue
            drop_str = json.dumps(drop_data)
            for match in SCRIPT_PATH_RE.finditer(drop_str):
                target = match.group(1)
                if os.path.isfile(os.path.join(root, target)):
                    edges.append(_make_edge(
                        source=rel_source, target=target, edge_type="PULSE_PLANNED",
                        source_type="CONFIG", target_type="SCRIPT",
                        line=None, confidence="medium",
                        detail=f"Pulse drop {drop_id} references {target}",
                    ))

        drops_dir = os.path.join(builds_dir, build_name, "drops")
        if os.path.isdir(drops_dir):
            for fname in os.listdir(drops_dir):
                if not fname.endswith(".md"):
                    continue
                brief_path = os.path.join(drops_dir, fname)
                rel_brief = f"N5/builds/{build_name}/drops/{fname}"
                try:
                    with open(brief_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception:
                    continue
                seen = set()
                for match in SCRIPT_PATH_RE.finditer(content):
                    target = match.group(1)
                    if target in seen:
                        continue
                    seen.add(target)
                    if os.path.isfile(os.path.join(root, target)):
                        edges.append(_make_edge(
                            source=rel_brief, target=target, edge_type="PULSE_PLANNED",
                            source_type="CONFIG", target_type="SCRIPT",
                            line=None, confidence="medium",
                            detail=f"drop brief references {target}",
                        ))
    return edges


def _collect_python_files(root: str) -> list[tuple[str, str]]:
    files = []
    for rel_root in PYTHON_SCAN_ROOTS:
        abs_root = os.path.join(root, rel_root)
        if not os.path.isdir(abs_root):
            continue
        for dirpath, dirnames, filenames in os.walk(abs_root):
            dirnames[:] = [d for d in dirnames if not _should_exclude(
                os.path.relpath(os.path.join(dirpath, d), root)
            )]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(fpath, root)
                if _should_exclude(rel_path):
                    continue
                files.append((fpath, rel_path))
    return files


def scan_workspace(root_path: str = "/home/workspace") -> list[dict]:
    """Scan N5OS workspace and return all detected dependency edges.

    Each edge is a dict:
    {
        "source": str,       # relative path from root
        "target": str,       # relative path from root
        "type": str,         # IMPORTS | CALLS_SUBPROCESS | CONFIG_REF | PROMPT_REF | SKILL_REF | PULSE_PLANNED | SHARED_STATE
        "source_type": str,  # SCRIPT | PROMPT | SKILL | COMMAND | CONFIG
        "target_type": str,  # SCRIPT | PROMPT | SKILL | COMMAND | CONFIG
        "line": int | None,  # source line number where detected
        "confidence": str,   # high | medium | low
        "detail": str        # human-readable description
    }
    """
    root = os.path.abspath(root_path)
    all_edges: list[dict] = []

    py_files = _collect_python_files(root)
    logger.info("Scanning %d Python files...", len(py_files))
    for fpath, rel_path in py_files:
        all_edges.extend(parse_python_imports(fpath, rel_path, root))
        all_edges.extend(parse_python_subprocess(fpath, rel_path, root))
        all_edges.extend(parse_python_string_refs(fpath, rel_path, root))

    logger.info("Scanning config files...")
    all_edges.extend(parse_config_commands_jsonl(root))
    all_edges.extend(parse_config_files(root))

    logger.info("Scanning prompt files...")
    all_edges.extend(parse_prompt_files(root))

    logger.info("Scanning SKILL.md files...")
    all_edges.extend(parse_skill_files(root))

    logger.info("Scanning Pulse build metadata...")
    all_edges.extend(parse_pulse_meta(root))

    # Deduplicate edges (same source+target+type)
    seen = set()
    unique_edges = []
    for edge in all_edges:
        key = (edge["source"], edge["target"], edge["type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)

    logger.info("Total unique edges: %d (from %d raw)", len(unique_edges), len(all_edges))
    return unique_edges


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    import argparse
    parser = argparse.ArgumentParser(description="N5OS Multi-Layer Dependency Parser")
    parser.add_argument("--root", default="/home/workspace", help="Workspace root path")
    parser.add_argument("--type", choices=[
        "IMPORTS", "CALLS_SUBPROCESS", "CONFIG_REF", "PROMPT_REF",
        "SKILL_REF", "PULSE_PLANNED", "SHARED_STATE"
    ], help="Filter by edge type")
    parser.add_argument("--source", help="Filter by source path substring")
    parser.add_argument("--target", help="Filter by target path substring")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be scanned without scanning")
    args = parser.parse_args()

    if args.dry_run:
        py_files = _collect_python_files(args.root)
        print(f"Would scan {len(py_files)} Python files")
        print(f"Would scan N5/config/ for config references")
        print(f"Would scan .prompt.md files for prompt references")
        print(f"Would scan Skills/*/SKILL.md for skill references")
        print(f"Would scan N5/builds/*/meta.json for Pulse references")
        sys.exit(0)

    edges = scan_workspace(args.root)

    if args.type:
        edges = [e for e in edges if e["type"] == args.type]
    if args.source:
        edges = [e for e in edges if args.source in e["source"]]
    if args.target:
        edges = [e for e in edges if args.target in e["target"]]

    if args.stats:
        from collections import Counter
        type_counts = Counter(e["type"] for e in edges)
        conf_counts = Counter(e["confidence"] for e in edges)
        print(f"\nTotal edges: {len(edges)}")
        print("\nBy type:")
        for t, c in type_counts.most_common():
            print(f"  {t}: {c}")
        print("\nBy confidence:")
        for conf, c in conf_counts.most_common():
            print(f"  {conf}: {c}")

        sources = set(e["source"] for e in edges)
        targets = set(e["target"] for e in edges)
        print(f"\nUnique sources: {len(sources)}")
        print(f"Unique targets: {len(targets)}")
        print(f"Unique nodes: {len(sources | targets)}")
    elif args.json:
        print(json.dumps(edges, indent=2))
    else:
        for e in edges:
            line_str = f":{e['line']}" if e['line'] else ""
            print(f"[{e['type']}] {e['source']}{line_str} -> {e['target']}  ({e['confidence']}) {e['detail']}")
