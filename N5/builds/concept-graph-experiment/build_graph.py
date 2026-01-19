#!/usr/bin/env python3
"""
Phase 2: Graph Data Transformation

Transforms extracted concepts and edges into a heterogeneous graph format
suitable for visualization.

Input:
- data/concepts.json
- data/thought_concept_edges.json
- positions_export.json (for thought metadata)

Output:
- data/concept_graph.json - Full graph with nodes and edges
"""

import json
from pathlib import Path
from collections import defaultdict

BUILD_DIR = Path(__file__).parent
DATA_DIR = BUILD_DIR / "data"
POSITIONS_EXPORT = Path("/home/workspace/N5/builds/position-system-overhaul/positions_export.json")

# Domain colors (matching the existing mind map)
DOMAIN_COLORS = {
    "hiring-market": "#f97316",    # Orange
    "worldview": "#8b5cf6",        # Purple
    "careerspan": "#22c55e",       # Green
    "ai-automation": "#3b82f6",    # Blue
    "epistemology": "#ec4899",     # Pink
    "founder": "#f59e0b",          # Amber
    "personal-foundations": "#14b8a6",  # Teal
    "education": "#06b6d4",        # Cyan
    "product-strategy": "#ef4444"  # Red
}

CONCEPT_COLOR = "#fbbf24"  # Gold/amber for concepts


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def build_heterogeneous_graph():
    """Build the heterogeneous graph with two node types."""
    
    # Load data
    concepts_data = load_json(DATA_DIR / "concepts.json")
    edges_data = load_json(DATA_DIR / "thought_concept_edges.json")
    positions = load_json(POSITIONS_EXPORT)
    
    # Build position lookup
    pos_lookup = {}
    for pos in positions:
        pos_id = pos.get("id")
        pos_lookup[pos_id] = pos
    
    # Build nodes
    nodes = []
    
    # Add concept nodes
    for concept in concepts_data["concepts"]:
        nodes.append({
            "id": f"c:{concept['id']}",
            "type": "concept",
            "label": concept["label"],
            "description": concept["description"],
            "thought_count": concept["thought_count"],
            "domains": concept["domains"],
            "color": CONCEPT_COLOR,
            "size": 20 + (concept["thought_count"] * 2)  # Size by connectivity
        })
    
    # Track which thoughts are connected
    connected_thoughts = set()
    for edge in edges_data["edges"]:
        connected_thoughts.add(edge["thought_id"])
    
    # Add thought nodes
    for pos in positions:
        pos_id = pos.get("id")
        domain = pos.get("domain", "unknown")
        
        nodes.append({
            "id": f"t:{pos_id}",
            "type": "thought",
            "label": pos.get("title", "")[:60],
            "full_title": pos.get("title", ""),
            "insight_preview": pos.get("insight_preview", ""),
            "domain": domain,
            "color": DOMAIN_COLORS.get(domain, "#6b7280"),
            "size": 8,
            "connected": pos_id in connected_thoughts
        })
    
    # Build edges (thought → concept)
    edges = []
    for edge in edges_data["edges"]:
        edges.append({
            "source": f"t:{edge['thought_id']}",
            "target": f"c:{edge['concept_id']}",
            "type": "embodies",
            "strength": edge["strength"]
        })
    
    # Compute statistics
    stats = compute_graph_stats(nodes, edges, concepts_data["concepts"])
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": stats,
        "domain_colors": DOMAIN_COLORS,
        "concept_color": CONCEPT_COLOR
    }


def compute_graph_stats(nodes: list, edges: list, concepts: list) -> dict:
    """Compute useful graph statistics."""
    
    thought_nodes = [n for n in nodes if n["type"] == "thought"]
    concept_nodes = [n for n in nodes if n["type"] == "concept"]
    connected_thoughts = [n for n in thought_nodes if n.get("connected", False)]
    
    # Find cross-domain bridges (concepts that span multiple domains)
    bridges = []
    for concept in concepts:
        if len(concept.get("domains", [])) >= 2:
            bridges.append({
                "concept": concept["label"],
                "domains": concept["domains"],
                "thought_count": concept["thought_count"]
            })
    bridges.sort(key=lambda x: -x["thought_count"])
    
    # Find most connected concepts
    concept_edge_counts = defaultdict(int)
    for edge in edges:
        if edge["target"].startswith("c:"):
            concept_edge_counts[edge["target"]] += 1
    
    top_concepts = sorted(
        [(cid.replace("c:", ""), count) for cid, count in concept_edge_counts.items()],
        key=lambda x: -x[1]
    )[:5]
    
    return {
        "total_thoughts": len(thought_nodes),
        "total_concepts": len(concept_nodes),
        "total_edges": len(edges),
        "connected_thoughts": len(connected_thoughts),
        "orphan_thoughts": len(thought_nodes) - len(connected_thoughts),
        "coverage_pct": round(len(connected_thoughts) / len(thought_nodes) * 100, 1),
        "avg_concepts_per_thought": round(len(edges) / len(thought_nodes), 1),
        "cross_domain_bridges": bridges[:5],
        "top_concepts": top_concepts
    }


def main():
    print("Building heterogeneous graph...")
    graph = build_heterogeneous_graph()
    
    print(f"\n=== Graph Structure ===")
    print(f"Thought nodes: {graph['stats']['total_thoughts']}")
    print(f"Concept nodes: {graph['stats']['total_concepts']}")
    print(f"Edges (thought→concept): {graph['stats']['total_edges']}")
    print(f"Coverage: {graph['stats']['coverage_pct']}%")
    
    print(f"\n=== Cross-Domain Bridges ===")
    for bridge in graph['stats']['cross_domain_bridges']:
        print(f"  {bridge['concept']}: {bridge['domains']} ({bridge['thought_count']} thoughts)")
    
    print(f"\n=== Top Concepts ===")
    for concept_id, count in graph['stats']['top_concepts']:
        print(f"  {concept_id}: {count} connections")
    
    # Write output
    output_path = DATA_DIR / "concept_graph.json"
    with open(output_path, "w") as f:
        json.dump(graph, f, indent=2)
    print(f"\nWrote {output_path}")
    
    # Validation
    print("\n=== Validation ===")
    thought_to_thought = [e for e in graph['edges'] if e['source'].startswith('t:') and e['target'].startswith('t:')]
    if thought_to_thought:
        print(f"❌ FAIL: Found {len(thought_to_thought)} direct thought→thought edges")
    else:
        print("✓ No direct thought→thought edges (all go through concepts)")
    
    orphans = graph['stats']['orphan_thoughts']
    if orphans > 0:
        print(f"⚠ {orphans} orphan thoughts (no concept connections)")
    else:
        print("✓ All thoughts connected to at least one concept")


if __name__ == "__main__":
    main()
