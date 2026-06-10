#!/usr/bin/env python3
"""
Graph Builder for N5OS Dependency Graph.

Consumes edge dicts from parsers.scan_workspace(), builds a NetworkX DiGraph
with typed nodes and edges, and persists to JSON with file hashes for lazy
invalidation.

Edge dict contract (from D1.1 parsers.py):
{
    "source": "N5/scripts/crm_cli.py",
    "target": "N5/scripts/db_paths.py",
    "edge_type": "IMPORTS",          # IMPORTS | CALLS_SUBPROCESS | CONFIG_REF | PROMPT_REF | SKILL_REF
    "line": 7,                       # source line number
    "confidence": "high",            # high | medium | low
    "detail": "imports get_db_connection"
}
"""

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx

WORKSPACE = "/home/workspace"
DATA_DIR = Path(__file__).parent.parent / "data"
GRAPH_PATH = DATA_DIR / "graph.json"

NODE_TYPE_MAP = {
    ".py": "SCRIPT",
    ".md": "PROMPT",
    ".jsonl": "CONFIG",
    ".json": "CONFIG",
    ".yaml": "CONFIG",
    ".yml": "CONFIG",
    ".ts": "SCRIPT",
    ".sh": "SCRIPT",
}

SKILL_DIR_MARKER = "Skills/"
PROMPT_SUFFIX = ".prompt.md"


def classify_node_type(path: str) -> str:
    if path.endswith(PROMPT_SUFFIX):
        return "PROMPT"
    if "/SKILL.md" in path:
        return "SKILL"
    ext = Path(path).suffix
    return NODE_TYPE_MAP.get(ext, "CONFIG")


def derive_domain(path: str) -> str:
    parts = Path(path).parts
    if len(parts) == 0:
        return "unknown"

    if parts[0] == "Skills" and len(parts) >= 2:
        return f"skill-{parts[1]}"
    if parts[0] == "N5":
        if len(parts) >= 3 and parts[1] == "scripts":
            subdir = parts[2]
            if Path(path).suffix:
                return "n5-core"
            return subdir
        if len(parts) >= 3 and parts[1] == "scripts" and not Path(parts[2]).suffix:
            return parts[2]
        if parts[1] == "config":
            return "config"
        if parts[1] == "commands":
            return "commands"
        return f"n5-{parts[1]}" if len(parts) >= 2 else "n5"
    if parts[0] == "Prompts":
        return "prompts"
    if parts[0] == "Sites":
        return f"site-{parts[1]}" if len(parts) >= 2 else "sites"
    return parts[0].lower()


def _rederive_domain(path: str) -> str:
    parts = Path(path).parts
    if len(parts) == 0:
        return "unknown"
    if parts[0] == "Skills" and len(parts) >= 2:
        return f"skill-{parts[1]}"
    if parts[0] == "N5":
        if len(parts) >= 3 and parts[1] == "scripts":
            child = parts[2]
            if not Path(child).suffix:
                return child
            return "n5-core"
        if len(parts) >= 2 and parts[1] == "config":
            return "config"
        return f"n5-{parts[1]}" if len(parts) >= 2 else "n5"
    if parts[0] == "Prompts":
        return "prompts"
    if parts[0] == "Sites" and len(parts) >= 2:
        return f"site-{parts[1]}"
    return parts[0].lower()


derive_domain = _rederive_domain


def file_sha256(path: str) -> str:
    full = os.path.join(WORKSPACE, path)
    try:
        with open(full, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]
    except (OSError, IOError):
        return "missing"


def build_graph(edges: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()
    all_nodes = set()
    for e in edges:
        all_nodes.add(e["source"])
        all_nodes.add(e["target"])

    # Build a type hint map from edges (parser knows best)
    type_hints = {}
    for e in edges:
        if e.get("source_type"):
            type_hints[e["source"]] = e["source_type"]
        if e.get("target_type"):
            type_hints[e["target"]] = e["target_type"]

    for node_path in all_nodes:
        G.add_node(
            node_path,
            node_type=type_hints.get(node_path, classify_node_type(node_path)),
            domain=derive_domain(node_path),
            sha256=file_sha256(node_path),
            label=Path(node_path).name,
        )

    for e in edges:
        G.add_edge(
            e["source"],
            e["target"],
            edge_type=e.get("edge_type") or e.get("type", "IMPORTS"),
            line=e.get("line", 0),
            confidence=e.get("confidence", "medium"),
            detail=e.get("detail", ""),
        )

    return G


def graph_to_dict(G: nx.DiGraph, duration: float) -> dict:
    nodes = []
    for nid, attrs in G.nodes(data=True):
        nodes.append({"id": nid, **attrs})

    edges = []
    for src, tgt, attrs in G.edges(data=True):
        edges.append({"source": src, "target": tgt, **attrs})

    return {
        "metadata": {
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "index_duration_seconds": round(duration, 2),
        },
        "nodes": nodes,
        "edges": edges,
    }


def save_graph(G: nx.DiGraph, duration: float, path: Path | None = None) -> dict:
    path = path or GRAPH_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data = graph_to_dict(G, duration)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return data


def load_graph(path: Path | None = None) -> nx.DiGraph | None:
    path = path or GRAPH_PATH
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)

    G = nx.DiGraph()
    for n in data["nodes"]:
        nid = n.pop("id")
        G.add_node(nid, **n)
    for e in data["edges"]:
        src = e.pop("source")
        tgt = e.pop("target")
        G.add_edge(src, tgt, **e)
    return G


def load_graph_metadata(path: Path | None = None) -> dict | None:
    path = path or GRAPH_PATH
    if not path.exists():
        return None
    with open(path) as f:
        data = json.load(f)
    return data.get("metadata", {})


def export_cytoscape(G: nx.DiGraph, output_path: Path) -> None:
    elements = []
    for nid, attrs in G.nodes(data=True):
        elements.append({
            "group": "nodes",
            "data": {"id": nid, **attrs},
        })
    for src, tgt, attrs in G.edges(data=True):
        elements.append({
            "group": "edges",
            "data": {
                "id": f"{src}→{tgt}",
                "source": src,
                "target": tgt,
                **attrs,
            },
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"elements": elements}, f, indent=2)


def index(scan_fn=None) -> tuple[nx.DiGraph, dict]:
    t0 = time.time()

    if scan_fn is None:
        try:
            from parsers import scan_workspace
            scan_fn = scan_workspace
        except ImportError:
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent))
                from parsers import scan_workspace
                scan_fn = scan_workspace
            except ImportError:
                raise RuntimeError(
                    "parsers.py not found. Run D1.1 first, or provide a scan function."
                )

    edges = scan_fn()
    G = build_graph(edges)
    duration = time.time() - t0
    data = save_graph(G, duration)
    return G, data
