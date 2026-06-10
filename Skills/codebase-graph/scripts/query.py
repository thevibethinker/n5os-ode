#!/usr/bin/env python3
"""
CLI query interface for the N5OS dependency graph.

Usage:
    python query.py index              # Build/rebuild the graph
    python query.py review <node>      # Operational review summary for a node
    python query.py rdeps <node>       # Reverse dependencies (blast radius)
    python query.py deps <node>        # Forward dependencies
    python query.py orphans            # Scripts with zero inbound edges
    python query.py hubs [N]           # Top N most-connected nodes
    python query.py cluster <domain>   # Nodes in a domain/cluster
    python query.py path <from> <to>   # Shortest dependency path
    python query.py stats              # Graph summary statistics
    python query.py export-json        # Export for cytoscape.js visualization
    python query.py info <node>        # Details about a single node
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import networkx as nx

from graph_builder import (
    DATA_DIR,
    GRAPH_PATH,
    export_cytoscape,
    index as do_index,
    load_graph,
    load_graph_metadata,
)

# ANSI colors
C_BLUE = "\033[34m"
C_GREEN = "\033[32m"
C_PURPLE = "\033[35m"
C_ORANGE = "\033[33m"
C_GRAY = "\033[90m"
C_CYAN = "\033[36m"
C_WHITE = "\033[97m"
C_RED = "\033[31m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"

NODE_COLORS = {
    "SCRIPT": C_BLUE,
    "PROMPT": C_GREEN,
    "SKILL": C_PURPLE,
    "COMMAND": C_ORANGE,
    "CONFIG": C_GRAY,
}

EDGE_STYLE = {
    "IMPORTS": "──",
    "CALLS_SUBPROCESS": "──",
    "CONFIG_REF": "╌╌",
    "PROMPT_REF": "╌╌",
    "SKILL_REF": "╌╌",
    "PULSE_PLANNED": "╌╌",
}

COMMANDS_JSONL = "/home/workspace/N5/config/commands.jsonl"


def color_node(node_id: str, node_type: str = "") -> str:
    c = NODE_COLORS.get(node_type, C_WHITE)
    return f"{c}{node_id}{C_RESET}"


def color_edge_type(etype: str) -> str:
    style = EDGE_STYLE.get(etype, "──")
    return f"{C_DIM}{style} [{etype}]{C_RESET}"


def load_entry_points() -> set[str]:
    entries = set()
    if os.path.exists(COMMANDS_JSONL):
        with open(COMMANDS_JSONL) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    cmd = json.loads(line)
                    fp = cmd.get("file_path", "")
                    if fp:
                        entries.add(fp)
                except json.JSONDecodeError:
                    continue
    return entries


def fuzzy_match(G: nx.DiGraph, query: str) -> list[str]:
    nodes = list(G.nodes())
    exact = [n for n in nodes if n == query]
    if exact:
        return exact

    suffix = [n for n in nodes if n.endswith("/" + query) or n.endswith(query)]
    if suffix:
        return suffix

    contains = [n for n in nodes if query.lower() in n.lower()]
    if contains:
        return contains

    return []


def resolve_node(G: nx.DiGraph, query: str) -> str | None:
    matches = fuzzy_match(G, query)
    if len(matches) == 1:
        return matches[0]
    if len(matches) == 0:
        print(f"{C_RED}No node found matching '{query}'{C_RESET}")
        return None
    if len(matches) > 10:
        print(f"{C_ORANGE}Ambiguous: {len(matches)} nodes match '{query}'. Showing first 10:{C_RESET}")
        for m in matches[:10]:
            nt = G.nodes[m].get("node_type", "")
            print(f"  {color_node(m, nt)}")
        print(f"  {C_DIM}... and {len(matches) - 10} more{C_RESET}")
        return None
    print(f"{C_ORANGE}Ambiguous: {len(matches)} nodes match '{query}':{C_RESET}")
    for m in matches:
        nt = G.nodes[m].get("node_type", "")
        print(f"  {color_node(m, nt)}")
    return None


def require_graph() -> nx.DiGraph | None:
    G = load_graph()
    if G is None:
        print(f"{C_RED}No graph found. Run 'query.py index' first.{C_RESET}")
        return None
    return G


def reverse_dependency_depths(G: nx.DiGraph, node: str) -> dict[str, int]:
    visited = {node: 0}
    queue = [(node, 0)]

    while queue:
        current, depth = queue.pop(0)
        for pred in G.predecessors(current):
            if pred not in visited:
                visited[pred] = depth + 1
                queue.append((pred, depth + 1))

    visited.pop(node, None)
    return visited


def risk_label(total_reverse: int, direct_reverse: int, outbound: int, edge_types: set[str]) -> tuple[str, str]:
    if total_reverse >= 25 or direct_reverse >= 10 or len(edge_types) >= 3:
        return "HIGH", C_RED
    if total_reverse >= 8 or direct_reverse >= 4 or outbound >= 6:
        return "MEDIUM", C_ORANGE
    return "LOW", C_GREEN


def cmd_index(args):
    print(f"{C_CYAN}Indexing workspace...{C_RESET}")
    try:
        G, data = do_index()
    except RuntimeError as e:
        print(f"{C_RED}Error: {e}{C_RESET}")
        sys.exit(1)

    meta = data["metadata"]
    print(
        f"{C_GREEN}Indexed {meta['node_count']} nodes, "
        f"{meta['edge_count']} edges in "
        f"{meta['index_duration_seconds']}s{C_RESET}"
    )
    print(f"  Graph saved to {GRAPH_PATH}")


def cmd_rdeps(args):
    G = require_graph()
    if G is None:
        return

    node = resolve_node(G, args.node)
    if node is None:
        return

    visited = reverse_dependency_depths(G, node)

    if not visited:
        nt = G.nodes[node].get("node_type", "")
        print(f"No reverse dependencies for {color_node(node, nt)}")
        return

    by_depth = defaultdict(list)
    for dep, depth in visited.items():
        by_depth[depth].append(dep)

    total = len(visited)
    nt = G.nodes[node].get("node_type", "")
    print(f"\n{C_BOLD}Blast radius for {color_node(node, nt)}{C_BOLD} ({total} dependents):{C_RESET}\n")

    for depth in sorted(by_depth.keys()):
        deps = sorted(by_depth[depth])
        label = "direct" if depth == 1 else "transitive"
        print(f"  {C_BOLD}{depth}-hop ({label}):{C_RESET}")

        for i, dep in enumerate(deps):
            dep_nt = G.nodes[dep].get("node_type", "")
            is_last = i == len(deps) - 1
            prefix = "└──" if is_last else "├──"

            if depth == 1:
                edge_data = G.edges[dep, node]
                etype = edge_data.get("edge_type", "?")
                print(f"    {prefix} {color_node(dep, dep_nt)} {color_edge_type(etype)}")
            else:
                intermediaries = []
                for succ in G.successors(dep):
                    if succ in visited and visited[succ] == depth - 1:
                        edge_data = G.edges[dep, succ]
                        etype = edge_data.get("edge_type", "?")
                        intermediaries.append(f"{etype} → {Path(succ).name}")
                via = ", ".join(intermediaries[:3]) if intermediaries else ""
                via_str = f" {C_DIM}[{via}]{C_RESET}" if via else ""
                print(f"    {prefix} {color_node(dep, dep_nt)}{via_str}")
        print()


def cmd_deps(args):
    G = require_graph()
    if G is None:
        return

    node = resolve_node(G, args.node)
    if node is None:
        return

    successors = list(G.successors(node))
    if not successors:
        nt = G.nodes[node].get("node_type", "")
        print(f"No forward dependencies for {color_node(node, nt)}")
        return

    nt = G.nodes[node].get("node_type", "")
    print(f"\n{C_BOLD}Dependencies of {color_node(node, nt)}{C_BOLD} ({len(successors)}):{C_RESET}\n")

    for i, dep in enumerate(sorted(successors)):
        dep_nt = G.nodes[dep].get("node_type", "")
        edge_data = G.edges[node, dep]
        etype = edge_data.get("edge_type", "?")
        line = edge_data.get("line", 0)
        detail = edge_data.get("detail", "")
        is_last = i == len(successors) - 1
        prefix = "└──" if is_last else "├──"
        line_str = f" L{line}" if line else ""
        detail_str = f" {C_DIM}({detail}){C_RESET}" if detail else ""
        print(f"  {prefix} {color_node(dep, dep_nt)} {color_edge_type(etype)}{line_str}{detail_str}")
    print()


def cmd_orphans(args):
    G = require_graph()
    if G is None:
        return

    entry_points = load_entry_points()
    skill_scripts = set()
    for n in G.nodes():
        if "/SKILL.md" in n:
            skill_scripts.add(n)
        parts = Path(n).parts
        if len(parts) >= 2 and parts[0] == "Skills":
            if n.endswith("SKILL.md"):
                skill_scripts.add(n)

    orphans = []
    for n in G.nodes():
        if G.in_degree(n) == 0:
            if n in entry_points or n in skill_scripts:
                continue
            orphans.append(n)

    orphans.sort()
    print(f"\n{C_BOLD}Orphan nodes ({len(orphans)} with zero inbound edges):{C_RESET}\n")

    if not orphans:
        print(f"  {C_GREEN}No orphans found.{C_RESET}")
        return

    by_domain = defaultdict(list)
    for o in orphans:
        domain = G.nodes[o].get("domain", "unknown")
        by_domain[domain].append(o)

    for domain in sorted(by_domain.keys()):
        nodes = by_domain[domain]
        print(f"  {C_CYAN}{domain}/{C_RESET} ({len(nodes)})")
        for n in nodes[:20]:
            nt = G.nodes[n].get("node_type", "")
            out_deg = G.out_degree(n)
            out_str = f" → {out_deg} deps" if out_deg > 0 else ""
            print(f"    {color_node(n, nt)}{C_DIM}{out_str}{C_RESET}")
        if len(nodes) > 20:
            print(f"    {C_DIM}... and {len(nodes) - 20} more{C_RESET}")
    print()


def cmd_hubs(args):
    G = require_graph()
    if G is None:
        return

    n = args.count or 10
    degree_data = []
    for node in G.nodes():
        in_d = G.in_degree(node)
        out_d = G.out_degree(node)
        degree_data.append((node, in_d + out_d, in_d, out_d))

    degree_data.sort(key=lambda x: x[1], reverse=True)
    top = degree_data[:n]

    print(f"\n{C_BOLD}Top {n} hubs by total degree:{C_RESET}\n")
    print(f"  {'Rank':<6}{'Node':<55}{'Total':<8}{'In':<6}{'Out':<6}{'Type'}")
    print(f"  {'─'*6}{'─'*55}{'─'*8}{'─'*6}{'─'*6}{'─'*10}")

    for rank, (node, total, in_d, out_d) in enumerate(top, 1):
        nt = G.nodes[node].get("node_type", "")
        c = NODE_COLORS.get(nt, C_WHITE)
        short = node if len(node) <= 52 else "..." + node[-(52-3):]
        print(f"  {rank:<6}{c}{short:<55}{C_RESET}{total:<8}{in_d:<6}{out_d:<6}{nt}")
    print()


def cmd_cluster(args):
    G = require_graph()
    if G is None:
        return

    domains = sorted({attrs.get("domain", "unknown") for _, attrs in G.nodes(data=True)})
    query = args.domain.lower()
    matches = [d for d in domains if query == d.lower()]
    if not matches:
        matches = [d for d in domains if query in d.lower()]

    if not matches:
        print(f"{C_RED}No domain found matching '{args.domain}'{C_RESET}")
        return
    if len(matches) > 1:
        print(f"{C_ORANGE}Ambiguous domain '{args.domain}'. Matches:{C_RESET}")
        for domain in matches[:20]:
            print(f"  {C_CYAN}{domain}{C_RESET}")
        return

    domain = matches[0]
    nodes = sorted([n for n, attrs in G.nodes(data=True) if attrs.get("domain") == domain])
    print(f"\n{C_BOLD}Cluster {C_CYAN}{domain}{C_RESET}{C_BOLD} ({len(nodes)} nodes):{C_RESET}\n")

    edge_counts = defaultdict(int)
    for node in nodes:
        for _, _, attrs in G.in_edges(node, data=True):
            edge_counts[attrs.get("edge_type", "?")] += 1
        for _, _, attrs in G.out_edges(node, data=True):
            edge_counts[attrs.get("edge_type", "?")] += 1

    if edge_counts:
        print(f"  {C_BOLD}Edge mix:{C_RESET}")
        for etype, count in sorted(edge_counts.items(), key=lambda x: -x[1]):
            print(f"    {etype:<20} {count}")
        print()

    for node in nodes[:40]:
        attrs = G.nodes[node]
        nt = attrs.get("node_type", "")
        print(
            f"  {color_node(node, nt)}"
            f"{C_DIM} in={G.in_degree(node)} out={G.out_degree(node)}{C_RESET}"
        )
    if len(nodes) > 40:
        print(f"\n  {C_DIM}... and {len(nodes) - 40} more{C_RESET}")
    print()


def cmd_path(args):
    G = require_graph()
    if G is None:
        return

    src = resolve_node(G, args.source)
    if src is None:
        return
    tgt = resolve_node(G, args.target)
    if tgt is None:
        return

    try:
        path = nx.shortest_path(G, src, tgt)
    except nx.NetworkXNoPath:
        print(f"{C_RED}No path from {src} to {tgt}{C_RESET}")
        return
    except nx.NodeNotFound as e:
        print(f"{C_RED}{e}{C_RESET}")
        return

    print(f"\n{C_BOLD}Shortest path ({len(path)-1} hops):{C_RESET}\n")
    for i, node in enumerate(path):
        nt = G.nodes[node].get("node_type", "")
        if i == 0:
            print(f"  {color_node(node, nt)}")
        else:
            edge_data = G.edges[path[i-1], node]
            etype = edge_data.get("edge_type", "?")
            detail = edge_data.get("detail", "")
            detail_str = f" {C_DIM}({detail}){C_RESET}" if detail else ""
            print(f"  {color_edge_type(etype)} ↓")
            print(f"  {color_node(node, nt)}{detail_str}")
    print()


def cmd_stats(args):
    G = require_graph()
    if G is None:
        return

    meta = load_graph_metadata()

    print(f"\n{C_BOLD}Graph Statistics:{C_RESET}\n")
    if meta:
        print(f"  Indexed at:     {meta.get('indexed_at', '?')}")
        print(f"  Index duration: {meta.get('index_duration_seconds', '?')}s")
    print(f"  Nodes:          {G.number_of_nodes()}")
    print(f"  Edges:          {G.number_of_edges()}")

    type_counts = defaultdict(int)
    for _, attrs in G.nodes(data=True):
        type_counts[attrs.get("node_type", "?")] += 1
    print(f"\n  {C_BOLD}Node types:{C_RESET}")
    for nt, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        c = NODE_COLORS.get(nt, C_WHITE)
        print(f"    {c}{nt:<12}{C_RESET} {count}")

    edge_counts = defaultdict(int)
    for _, _, attrs in G.edges(data=True):
        edge_counts[attrs.get("edge_type", "?")] += 1
    print(f"\n  {C_BOLD}Edge types:{C_RESET}")
    for et, count in sorted(edge_counts.items(), key=lambda x: -x[1]):
        print(f"    {et:<20} {count}")

    domain_counts = defaultdict(int)
    for _, attrs in G.nodes(data=True):
        domain_counts[attrs.get("domain", "?")] += 1
    print(f"\n  {C_BOLD}Domains (top 15):{C_RESET}")
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"    {C_CYAN}{domain:<25}{C_RESET} {count}")

    components = list(nx.weakly_connected_components(G))
    print(f"\n  Connected components: {len(components)}")
    if components:
        largest = max(components, key=len)
        print(f"  Largest component:   {len(largest)} nodes ({100*len(largest)//G.number_of_nodes()}%)")

    isolated = [n for n in G.nodes() if G.degree(n) == 0]
    print(f"  Isolated nodes:      {len(isolated)}")
    print()


def cmd_export_json(args):
    G = require_graph()
    if G is None:
        return

    out = DATA_DIR / "viz-export.json"
    export_cytoscape(G, out)
    print(f"{C_GREEN}Exported {G.number_of_nodes()} nodes and {G.number_of_edges()} edges to {out}{C_RESET}")


def cmd_info(args):
    G = require_graph()
    if G is None:
        return

    node = resolve_node(G, args.node)
    if node is None:
        return

    attrs = G.nodes[node]
    nt = attrs.get("node_type", "?")

    print(f"\n{C_BOLD}Node: {color_node(node, nt)}{C_RESET}")
    print(f"  Type:   {nt}")
    print(f"  Domain: {attrs.get('domain', '?')}")
    print(f"  SHA256: {attrs.get('sha256', '?')}")

    in_edges = list(G.in_edges(node, data=True))
    out_edges = list(G.out_edges(node, data=True))

    print(f"\n  {C_BOLD}Inbound ({len(in_edges)}):{C_RESET}")
    for src, _, edata in sorted(in_edges, key=lambda x: x[0])[:20]:
        src_nt = G.nodes[src].get("node_type", "")
        etype = edata.get("edge_type", "?")
        print(f"    ← {color_node(src, src_nt)} {color_edge_type(etype)}")
    if len(in_edges) > 20:
        print(f"    {C_DIM}... and {len(in_edges) - 20} more{C_RESET}")

    print(f"\n  {C_BOLD}Outbound ({len(out_edges)}):{C_RESET}")
    for _, tgt, edata in sorted(out_edges, key=lambda x: x[1])[:20]:
        tgt_nt = G.nodes[tgt].get("node_type", "")
        etype = edata.get("edge_type", "?")
        line = edata.get("line", 0)
        line_str = f" L{line}" if line else ""
        print(f"    → {color_node(tgt, tgt_nt)} {color_edge_type(etype)}{line_str}")
    if len(out_edges) > 20:
        print(f"    {C_DIM}... and {len(out_edges) - 20} more{C_RESET}")
    print()


def cmd_review(args):
    G = require_graph()
    if G is None:
        return

    node = resolve_node(G, args.node)
    if node is None:
        return

    attrs = G.nodes[node]
    nt = attrs.get("node_type", "?")
    reverse_depths = reverse_dependency_depths(G, node)
    direct_reverse = sorted(dep for dep, depth in reverse_depths.items() if depth == 1)
    outbound = sorted(G.successors(node))
    inbound_edge_types = {edata.get("edge_type", "?") for _, _, edata in G.in_edges(node, data=True)}
    outbound_edge_types = {edata.get("edge_type", "?") for _, _, edata in G.out_edges(node, data=True)}
    label, color = risk_label(len(reverse_depths), len(direct_reverse), len(outbound), inbound_edge_types | outbound_edge_types)

    print(f"\n{C_BOLD}Review: {color_node(node, nt)}{C_RESET}")
    print(f"  Type:         {nt}")
    print(f"  Domain:       {attrs.get('domain', '?')}")
    print(f"  Blast radius: {len(direct_reverse)} direct, {len(reverse_depths)} total reverse dependents")
    print(f"  Depends on:   {len(outbound)} outbound dependencies")
    print(f"  Risk:         {color}{label}{C_RESET}")

    if inbound_edge_types:
        print(f"  Inbound mix:  {', '.join(sorted(inbound_edge_types))}")
    if outbound_edge_types:
        print(f"  Outbound mix: {', '.join(sorted(outbound_edge_types))}")

    print(f"\n  {C_BOLD}Direct dependents:{C_RESET}")
    if direct_reverse:
        for dep in direct_reverse[:12]:
            dep_nt = G.nodes[dep].get("node_type", "")
            etype = G.edges[dep, node].get("edge_type", "?")
            print(f"    ← {color_node(dep, dep_nt)} {color_edge_type(etype)}")
        if len(direct_reverse) > 12:
            print(f"    {C_DIM}... and {len(direct_reverse) - 12} more{C_RESET}")
    else:
        print(f"    {C_DIM}None{C_RESET}")

    print(f"\n  {C_BOLD}Immediate dependencies:{C_RESET}")
    if outbound:
        for dep in outbound[:12]:
            dep_nt = G.nodes[dep].get("node_type", "")
            etype = G.edges[node, dep].get("edge_type", "?")
            print(f"    → {color_node(dep, dep_nt)} {color_edge_type(etype)}")
        if len(outbound) > 12:
            print(f"    {C_DIM}... and {len(outbound) - 12} more{C_RESET}")
    else:
        print(f"    {C_DIM}None{C_RESET}")

    print(f"\n  {C_BOLD}Recommended next step:{C_RESET}")
    if label == "HIGH":
        print("    Stage the change, inspect top direct dependents, and avoid bundled edits.")
    elif label == "MEDIUM":
        print("    Review direct dependents before editing and keep scope tight.")
    else:
        print("    Proceed with a scoped change, but re-check if scope expands.")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="N5OS Dependency Graph — query interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    sub.add_parser("index", help="Build/rebuild the dependency graph")

    p_review = sub.add_parser("review", help="Operational dependency review for a node")
    p_review.add_argument("node", help="Node path or fuzzy name")

    p_rdeps = sub.add_parser("rdeps", help="Reverse dependencies (blast radius)")
    p_rdeps.add_argument("node", help="Node path or fuzzy name")

    p_deps = sub.add_parser("deps", help="Forward dependencies")
    p_deps.add_argument("node", help="Node path or fuzzy name")

    sub.add_parser("orphans", help="Find nodes with zero inbound edges")

    p_hubs = sub.add_parser("hubs", help="Top N most-connected nodes")
    p_hubs.add_argument("count", type=int, nargs="?", default=10, help="Number of hubs (default 10)")

    p_cluster = sub.add_parser("cluster", help="List nodes in a domain cluster")
    p_cluster.add_argument("domain", help="Domain name or substring")

    p_path = sub.add_parser("path", help="Shortest dependency path between two nodes")
    p_path.add_argument("source", help="Source node")
    p_path.add_argument("target", help="Target node")

    sub.add_parser("stats", help="Graph summary statistics")
    sub.add_parser("export-json", help="Export for cytoscape.js visualization")

    p_info = sub.add_parser("info", help="Details about a single node")
    p_info.add_argument("node", help="Node path or fuzzy name")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "index": cmd_index,
        "review": cmd_review,
        "rdeps": cmd_rdeps,
        "deps": cmd_deps,
        "orphans": cmd_orphans,
        "hubs": cmd_hubs,
        "cluster": cmd_cluster,
        "path": cmd_path,
        "stats": cmd_stats,
        "export-json": cmd_export_json,
        "info": cmd_info,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
