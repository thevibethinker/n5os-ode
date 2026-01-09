#!/usr/bin/env python3
"""
R-Block Memory Enricher
Queries N5 memory profiles for relevant context during reflection processing.

Usage:
    python3 r_block_memory_enricher.py "AI headhunters" "recruiter distribution"
    python3 r_block_memory_enricher.py --profiles knowledge positions "candidate ownership"
    python3 r_block_memory_enricher.py --json "market signal"
"""

import argparse
import json
import sys
from pathlib import Path

# Add N5/scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))
# Add N5/cognition for memory client
sys.path.insert(0, str(Path(__file__).parent.parent / "cognition"))

try:
    from n5_memory_client import N5MemoryClient
    HAS_MEMORY_CLIENT = True
except ImportError:
    HAS_MEMORY_CLIENT = False


def enrich(concepts: list[str], profiles: list[str] = None, limit: int = 5) -> dict:
    """
    Query memory profiles for concepts.
    
    Args:
        concepts: List of key concepts to search
        profiles: Profiles to query (default: knowledge, positions, meetings)
        limit: Max results per profile
    
    Returns:
        Dict with profile -> list of hits
    """
    if not HAS_MEMORY_CLIENT:
        return {"error": "n5_memory_client not available", "profiles": {}}
    
    profiles = profiles or ["knowledge", "positions", "meetings"]
    
    try:
        client = N5MemoryClient()
    except Exception as e:
        return {"error": f"Failed to initialize memory client: {e}", "profiles": {}}
    
    results = {"profiles": {}, "query": " ".join(concepts)}
    
    for profile in profiles:
        query = " ".join(concepts)
        try:
            hits = client.search_profile(profile, query, limit=limit)
            
            # Dedupe by ID and format results
            seen_ids = set()
            formatted_hits = []
            
            for h in hits:
                hit_id = h.get("id", h.get("path", str(h)[:50]))
                if hit_id in seen_ids:
                    continue
                seen_ids.add(hit_id)
                
                formatted_hits.append({
                    "id": hit_id,
                    "title": h.get("title", h.get("text", "")[:50]),
                    "score": round(h.get("score", 0), 3),
                    "snippet": h.get("text", "")[:200],
                    "path": h.get("path", None)
                })
            
            # Sort by score descending
            formatted_hits.sort(key=lambda x: x["score"], reverse=True)
            results["profiles"][profile] = formatted_hits
            
        except Exception as e:
            results["profiles"][profile] = {"error": str(e)}
    
    return results


def format_for_rix(results: dict) -> str:
    """
    Format results as markdown for RIX consumption.
    """
    lines = ["## Memory Context\n"]
    
    if "error" in results:
        lines.append(f"⚠️ {results['error']}\n")
        return "\n".join(lines)
    
    lines.append(f"**Query:** {results.get('query', 'N/A')}\n")
    
    for profile, hits in results.get("profiles", {}).items():
        lines.append(f"\n### {profile.title()}")
        
        if isinstance(hits, dict) and "error" in hits:
            lines.append(f"- ⚠️ Error: {hits['error']}")
            continue
        
        if not hits:
            lines.append("- No relevant hits")
            continue
        
        for h in hits[:5]:  # Top 5 per profile
            score = h.get("score", 0)
            title = h.get("title", "Untitled")
            snippet = h.get("snippet", "")[:100]
            lines.append(f"- **[{score:.2f}]** {title}")
            if snippet:
                lines.append(f"  > {snippet}...")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Query N5 memory profiles for reflection enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search across all default profiles
  python3 r_block_memory_enricher.py "AI headhunters" "recruiter"

  # Search specific profiles
  python3 r_block_memory_enricher.py --profiles knowledge positions "candidate ownership"

  # Output as JSON (for programmatic use)
  python3 r_block_memory_enricher.py --json "market signal"

  # Output as markdown (for RIX)
  python3 r_block_memory_enricher.py --markdown "strategic bet"
        """
    )
    parser.add_argument("concepts", nargs="+", help="Key concepts to search")
    parser.add_argument(
        "--profiles", 
        nargs="+", 
        default=["knowledge", "positions", "meetings"],
        help="Profiles to query (default: knowledge, positions, meetings)"
    )
    parser.add_argument("--limit", type=int, default=5, help="Max results per profile")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--markdown", action="store_true", help="Output as markdown for RIX")
    
    args = parser.parse_args()
    
    if not args.concepts:
        print("Error: At least one concept required", file=sys.stderr)
        sys.exit(1)
    
    results = enrich(args.concepts, args.profiles, args.limit)
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.markdown:
        print(format_for_rix(results))
    else:
        # Human-readable default
        if "error" in results:
            print(f"⚠️ {results['error']}")
        
        print(f"Query: {results.get('query', 'N/A')}\n")
        
        for profile, hits in results.get("profiles", {}).items():
            print(f"=== {profile.upper()} ===")
            
            if isinstance(hits, dict) and "error" in hits:
                print(f"  ⚠️ Error: {hits['error']}")
                continue
            
            if not hits:
                print("  No relevant hits")
                continue
            
            for h in hits:
                score = h.get("score", 0)
                title = h.get("title", "Untitled")
                print(f"  [{score:.2f}] {title}")
            print()


if __name__ == "__main__":
    main()


