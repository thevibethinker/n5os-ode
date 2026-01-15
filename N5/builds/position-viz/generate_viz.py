#!/usr/bin/env python3
"""
Knowledge Graph Visualizer for Position System
Uses PyVis to create an interactive HTML visualization.
"""
import json
from pyvis.network import Network
from pathlib import Path

# Color palette for domains
DOMAIN_COLORS = {
    "hiring-market": "#FF6B6B",
    "epistemology": "#4ECDC4",
    "worldview": "#45B7D1",
    "personal-foundations": "#96CEB4",
    "strategy": "#FFEAA7",
    "careerspan": "#DDA0DD",
    "ai": "#98D8C8",
    "entrepreneurship": "#F7DC6F",
    "relationships": "#BB8FCE",
    "unknown": "#95A5A6"
}

# Color for relationship types
RELATIONSHIP_COLORS = {
    "supports": "#2ECC71",
    "supported_by": "#27AE60",
    "extends": "#3498DB",
    "extended_by": "#2980B9",
    "implies": "#9B59B6",
    "implied_by": "#8E44AD",
    "prerequisite": "#E74C3C",
    "enables": "#1ABC9C",
    "belongs_to": "#BDC3C7",
    "related_to": "#7F8C8D"
}

def load_triples(filepath):
    with open(filepath) as f:
        return json.load(f)

def build_graph(triples, include_domain_nodes=True):
    net = Network(
        height="900px",
        width="100%",
        bgcolor="#1a1a2e",
        font_color="white",
        directed=True,
        select_menu=True,
        filter_menu=True
    )
    
    net.barnes_hut(
        gravity=-3000,
        central_gravity=0.3,
        spring_length=150,
        spring_strength=0.001,
        damping=0.09
    )
    
    nodes_added = set()
    domain_for_node = {}
    
    # First pass: collect domain info for each node
    for t in triples:
        if t["predicate"] == "belongs_to":
            domain_for_node[t["subject"]] = t["object"].strip("[]").lower()
    
    # Second pass: add nodes and edges
    for t in triples:
        subject = t["subject"]
        obj = t["object"]
        predicate = t["predicate"]
        
        # Skip domain membership edges if we're not including domain nodes
        if predicate == "belongs_to" and not include_domain_nodes:
            continue
        
        # Add subject node
        if subject not in nodes_added:
            domain = domain_for_node.get(subject, "unknown")
            color = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["unknown"])
            net.add_node(
                subject,
                label=subject,
                color=color,
                size=25,
                title=f"Domain: {domain}",
                font={"size": 12}
            )
            nodes_added.add(subject)
        
        # Add object node
        if obj not in nodes_added:
            # Check if it's a domain node
            if obj.startswith("[") and obj.endswith("]"):
                domain_name = obj.strip("[]").lower()
                color = DOMAIN_COLORS.get(domain_name, "#666666")
                net.add_node(
                    obj,
                    label=obj,
                    color=color,
                    size=40,
                    shape="box",
                    title=f"Domain: {domain_name}",
                    font={"size": 14, "bold": True}
                )
            else:
                domain = domain_for_node.get(obj, "unknown")
                color = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["unknown"])
                net.add_node(
                    obj,
                    label=obj,
                    color=color,
                    size=25,
                    title=f"Domain: {domain}",
                    font={"size": 12}
                )
            nodes_added.add(obj)
        
        # Add edge
        edge_color = RELATIONSHIP_COLORS.get(predicate, "#555555")
        edge_width = 1 if predicate == "belongs_to" else 2
        net.add_edge(
            subject,
            obj,
            label=predicate,
            color=edge_color,
            width=edge_width,
            title=predicate,
            arrows="to"
        )
    
    return net

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="positions_triples.json")
    parser.add_argument("--output", default="positions_graph.html")
    parser.add_argument("--no-domains", action="store_true", help="Hide domain cluster nodes")
    args = parser.parse_args()
    
    triples = load_triples(args.input)
    print(f"Loaded {len(triples)} triples")
    
    net = build_graph(triples, include_domain_nodes=not args.no_domains)
    
    # Save
    net.save_graph(args.output)
    print(f"Saved visualization to {args.output}")
    print(f"Open in browser: file://{Path(args.output).absolute()}")

if __name__ == "__main__":
    main()

