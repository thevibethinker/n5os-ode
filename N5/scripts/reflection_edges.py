#!/usr/bin/env python3
"""
Reflection Edges CLI

Manage edges (connections) between reflections, positions, knowledge articles,
and other content in V's knowledge graph.

Usage:
    python3 N5/scripts/reflection_edges.py add --from SOURCE --to TARGET ...
    python3 N5/scripts/reflection_edges.py from SOURCE_ID
    python3 N5/scripts/reflection_edges.py to TARGET_ID
    python3 N5/scripts/reflection_edges.py type EDGE_TYPE
    python3 N5/scripts/reflection_edges.py stats
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# Constants
EDGES_FILE = Path(__file__).parent.parent / "data" / "reflection_edges.jsonl"
VALID_EDGE_TYPES = {"EXTENDS", "CONTRADICTS", "SUPPORTS", "REFINES", "ENABLES"}
VALID_NODE_TYPES = {"reflection", "position", "knowledge", "meeting"}
VALID_CONFIDENCE = {"high", "medium", "low"}


def load_edges() -> list[dict]:
    """Load all edges from JSONL file, skipping comments."""
    edges = []
    if not EDGES_FILE.exists():
        return edges

    with open(EDGES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    edges.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return edges


def generate_edge_id() -> str:
    """Generate a unique edge ID based on timestamp and counter."""
    today = datetime.now().strftime("%Y%m%d")
    edges = load_edges()

    # Find existing edges from today
    today_edges = [e for e in edges if e.get("id", "").startswith(f"edge_{today}_")]
    counter = len(today_edges) + 1

    return f"edge_{today}_{counter:03d}"


def add_edge(args) -> None:
    """Add a new edge to the JSONL file."""
    # Validate inputs
    if args.edge_type not in VALID_EDGE_TYPES:
        print(f"Error: Invalid edge type '{args.edge_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(VALID_EDGE_TYPES))}", file=sys.stderr)
        sys.exit(1)

    if args.from_type not in VALID_NODE_TYPES:
        print(f"Error: Invalid from_type '{args.from_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(VALID_NODE_TYPES))}", file=sys.stderr)
        sys.exit(1)

    if args.to_type not in VALID_NODE_TYPES:
        print(f"Error: Invalid to_type '{args.to_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(VALID_NODE_TYPES))}", file=sys.stderr)
        sys.exit(1)

    if args.confidence not in VALID_CONFIDENCE:
        print(f"Error: Invalid confidence '{args.confidence}'", file=sys.stderr)
        print(f"Valid values: {', '.join(sorted(VALID_CONFIDENCE))}", file=sys.stderr)
        sys.exit(1)

    edge = {
        "id": generate_edge_id(),
        "from": args.source,
        "from_type": args.from_type,
        "to": args.to,
        "to_type": args.to_type,
        "edge_type": args.edge_type,
        "evidence": args.evidence,
        "confidence": args.confidence,
        "created": datetime.now().isoformat() + "Z",
        "created_by": args.created_by or "manual"
    }

    # Append to file
    with open(EDGES_FILE, "a") as f:
        f.write(json.dumps(edge) + "\n")

    if args.json:
        print(json.dumps(edge, indent=2))
    else:
        print(f"Created edge: {edge['id']}")
        print(f"  {edge['from']} --[{edge['edge_type']}]--> {edge['to']}")


def find_from(args) -> None:
    """Find all edges FROM a given source."""
    edges = load_edges()
    matches = [e for e in edges if e.get("from") == args.source_id]

    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        if not matches:
            print(f"No edges found from '{args.source_id}'")
            return

        print(f"Edges from '{args.source_id}':")
        for edge in matches:
            print(f"  --[{edge['edge_type']}]--> {edge['to']} ({edge['to_type']})")
            if edge.get('evidence'):
                print(f"     Evidence: {edge['evidence'][:80]}...")


def find_to(args) -> None:
    """Find all edges TO a given target."""
    edges = load_edges()
    matches = [e for e in edges if e.get("to") == args.target_id]

    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        if not matches:
            print(f"No edges found to '{args.target_id}'")
            return

        print(f"Edges to '{args.target_id}':")
        for edge in matches:
            print(f"  {edge['from']} ({edge['from_type']}) --[{edge['edge_type']}]-->")
            if edge.get('evidence'):
                print(f"     Evidence: {edge['evidence'][:80]}...")


def find_type(args) -> None:
    """Find all edges of a given type."""
    edge_type = args.edge_type.upper()

    if edge_type not in VALID_EDGE_TYPES:
        print(f"Error: Invalid edge type '{edge_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(VALID_EDGE_TYPES))}", file=sys.stderr)
        sys.exit(1)

    edges = load_edges()
    matches = [e for e in edges if e.get("edge_type") == edge_type]

    if args.json:
        print(json.dumps(matches, indent=2))
    else:
        if not matches:
            print(f"No edges of type '{edge_type}'")
            return

        print(f"Edges of type '{edge_type}' ({len(matches)} found):")
        for edge in matches:
            print(f"  {edge['from']} --> {edge['to']}")


def show_stats(args) -> None:
    """Show statistics about the edge graph."""
    edges = load_edges()

    if not edges:
        print("No edges found.")
        return

    # Compute statistics
    edge_type_counts = Counter(e.get("edge_type") for e in edges)
    from_type_counts = Counter(e.get("from_type") for e in edges)
    to_type_counts = Counter(e.get("to_type") for e in edges)
    confidence_counts = Counter(e.get("confidence") for e in edges)

    # Find super-connectors (nodes with many connections)
    from_counts = Counter(e.get("from") for e in edges)
    to_counts = Counter(e.get("to") for e in edges)
    all_node_counts = from_counts + to_counts
    super_connectors = [(node, count) for node, count in all_node_counts.most_common(5) if count >= 2]

    if args.json:
        stats = {
            "total_edges": len(edges),
            "by_edge_type": dict(edge_type_counts),
            "by_from_type": dict(from_type_counts),
            "by_to_type": dict(to_type_counts),
            "by_confidence": dict(confidence_counts),
            "super_connectors": [{"node": n, "connections": c} for n, c in super_connectors]
        }
        print(json.dumps(stats, indent=2))
    else:
        print(f"Edge Statistics")
        print(f"===============")
        print(f"Total edges: {len(edges)}")
        print()
        print("By edge type:")
        for edge_type, count in sorted(edge_type_counts.items()):
            print(f"  {edge_type}: {count}")
        print()
        print("By source type:")
        for node_type, count in sorted(from_type_counts.items()):
            print(f"  {node_type}: {count}")
        print()
        print("By target type:")
        for node_type, count in sorted(to_type_counts.items()):
            print(f"  {node_type}: {count}")
        print()
        print("By confidence:")
        for conf, count in sorted(confidence_counts.items()):
            print(f"  {conf}: {count}")

        if super_connectors:
            print()
            print("Super-connectors (2+ connections):")
            for node, count in super_connectors:
                print(f"  {node}: {count} connections")


def main():
    parser = argparse.ArgumentParser(
        description="Manage reflection edges (connections between content)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a new edge
  %(prog)s add --from "2026-01-09_recruiter-game-plan" --from-type reflection \\
               --to "candidate-ownership" --to-type position \\
               --edge-type EXTENDS --evidence "Quote here" --confidence high

  # Find edges FROM a source
  %(prog)s from "2026-01-09_recruiter-game-plan"

  # Find edges TO a target
  %(prog)s to "candidate-ownership"

  # Find all edges of a type
  %(prog)s type EXTENDS

  # Show statistics
  %(prog)s stats
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new edge")
    add_parser.add_argument("--from", dest="source", required=True, help="Source node ID")
    add_parser.add_argument("--from-type", dest="from_type", required=True,
                           choices=sorted(VALID_NODE_TYPES), help="Source node type")
    add_parser.add_argument("--to", required=True, help="Target node ID")
    add_parser.add_argument("--to-type", dest="to_type", required=True,
                           choices=sorted(VALID_NODE_TYPES), help="Target node type")
    add_parser.add_argument("--edge-type", dest="edge_type", required=True,
                           choices=sorted(VALID_EDGE_TYPES), help="Type of connection")
    add_parser.add_argument("--evidence", required=True, help="Evidence for the connection")
    add_parser.add_argument("--confidence", required=True,
                           choices=sorted(VALID_CONFIDENCE), help="Confidence level")
    add_parser.add_argument("--created-by", dest="created_by", help="Creator (default: manual)")
    add_parser.add_argument("--json", action="store_true", help="Output as JSON")
    add_parser.set_defaults(func=add_edge)

    # From command
    from_parser = subparsers.add_parser("from", help="Find edges FROM a source")
    from_parser.add_argument("source_id", help="Source node ID to search for")
    from_parser.add_argument("--json", action="store_true", help="Output as JSON")
    from_parser.set_defaults(func=find_from)

    # To command
    to_parser = subparsers.add_parser("to", help="Find edges TO a target")
    to_parser.add_argument("target_id", help="Target node ID to search for")
    to_parser.add_argument("--json", action="store_true", help="Output as JSON")
    to_parser.set_defaults(func=find_to)

    # Type command
    type_parser = subparsers.add_parser("type", help="Find edges of a specific type")
    type_parser.add_argument("edge_type", help="Edge type to search for")
    type_parser.add_argument("--json", action="store_true", help="Output as JSON")
    type_parser.set_defaults(func=find_type)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show edge statistics")
    stats_parser.add_argument("--json", action="store_true", help="Output as JSON")
    stats_parser.set_defaults(func=show_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
