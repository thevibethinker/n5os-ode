"""
Content Library CLI Tool
Command-line interface for querying the Content Library database
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from search import (
    search_content, search_blocks, filter_by_block_type,
    filter_by_topic, get_stats
)


def format_json(data: Any) -> str:
    """Format data as pretty JSON"""
    return json.dumps(data, indent=2, default=str)


def print_content_results(results: List[Dict], verbose: bool = False):
    """Print content search results in readable format"""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} results:\n")
    print("=" * 80)
    
    for i, item in enumerate(results, 1):
        print(f"\n{i}. {item.get('title', 'Untitled')}")
        print(f"   ID: {item.get('id', 'N/A')}")
        print(f"   Type: {item.get('source_type', 'N/A')}")
        print(f"   Date: {item.get('date_created', 'N/A')}")
        
        topics = item.get('topics', [])
        if topics:
            print(f"   Topics: {', '.join(topics)}")
        
        tags = item.get('tags', [])
        if tags:
            print(f"   Tags: {', '.join(tags)}")
        
        if verbose and item.get('notes'):
            notes = item.get('notes', '')
            if len(notes) > 200:
                notes = notes[:200] + "..."
            print(f"   Notes: {notes}")
        
        if i < len(results):
            print("-" * 80)


def print_block_results(results: List[Dict], verbose: bool = False):
    """Print block search results in readable format"""
    if not results:
        print("No results found.")
        return
    
    print(f"\nFound {len(results)} blocks:\n")
    print("=" * 80)
    
    for i, block in enumerate(results, 1):
        print(f"\n{i}. {block.get('block_code', 'N/A')} - {block.get('block_type', 'N/A')}")
        print(f"   Source: {block.get('content_title', 'Unknown')}")
        print(f"   ID: {block.get('id', 'N/A')}")
        
        if block.get('speaker'):
            print(f"   Speaker: {block.get('speaker')}")
        
        topics = block.get('topics', [])
        if topics:
            print(f"   Topics: {', '.join(topics)}")
        
        content = block.get('content', '')
        if content:
            if verbose:
                print(f"\n   Content:\n   {content}")
            else:
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"   Content: {preview}")
        
        if i < len(results):
            print("-" * 80)


def print_topics(topic_list: List[str]):
    """Print available topics"""
    print("\nAvailable Topics:")
    print("=" * 40)
    for i, topic in enumerate(sorted(topic_list), 1):
        print(f"{i:2d}. {topic}")


def print_stats(stats: Dict):
    """Print database statistics"""
    print("\n📊 Content Library Statistics")
    print("=" * 50)
    
    print(f"\n📁 Total Content: {stats.get('total_content', 0)}")
    content_by_type = stats.get('content_by_type', {})
    if content_by_type:
        print("\nBy Type:")
        for content_type, count in content_by_type.items():
            print(f"   • {content_type}: {count}")
    
    print(f"\n🧱 Total Blocks: {stats.get('total_blocks', 0)}")
    blocks_by_code = stats.get('blocks_by_code', {})
    if blocks_by_code:
        print("\nBy Block Code:")
        for block_code, count in sorted(blocks_by_code.items()):
            print(f"   • {block_code}: {count}")
    
    print(f"\n🏷️  Total Topics: {stats.get('total_topics', 0)}")
    topic_list = stats.get('topic_list', [])
    if topic_list:
        print("   ", ", ".join(sorted(topic_list)[:10]))
        if len(topic_list) > 10:
            print(f"   ... and {len(topic_list) - 10} more")
    
    print()


def cmd_search(args):
    """Handle search command"""
    if args.type == "content":
        results = search_content(args.query, args.limit)
        print_content_results(results, args.verbose)
    elif args.type == "blocks":
        results = search_blocks(args.query, args.limit)
        print_block_results(results, args.verbose)
    elif args.type == "both":
        content_results = search_content(args.query, args.limit // 2)
        block_results = search_blocks(args.query, args.limit // 2)
        
        if content_results:
            print("📁 CONTENT RESULTS:")
            print_content_results(content_results, args.verbose)
            
        if block_results:
            if content_results:
                print("\n" + "=" * 80 + "\n")
            print("🧱 BLOCK RESULTS:")
            print_block_results(block_results, args.verbose)
    
    if args.format == "json":
        if args.type == "both":
            print("\n" + format_json({"content": content_results, "blocks": block_results}))
        elif args.type == "content":
            print(format_json(results))
        else:
            print(format_json(results))


def cmd_filter(args):
    """Handle filter command"""
    if args.block_type:
        results = filter_by_block_type(args.block_type, args.limit)
        print_block_results(results, args.verbose)
        
        if args.format == "json":
            print(format_json(results))
    
    elif args.topic:
        results = filter_by_topic(args.topic, args.content_type, args.limit)
        
        if args.content_type in ["content", "both"]:
            if results["content"]:
                print("📁 CONTENT RESULTS:")
                print_content_results(results["content"], args.verbose)
                print()
        
        if args.content_type in ["blocks", "both"]:
            if results["blocks"]:
                print("🧱 BLOCK RESULTS:")
                print_block_results(results["blocks"], args.verbose)
        
        if args.format == "json":
            print(format_json(results))


def cmd_topics(args):
    """Handle topics command"""
    stats = get_stats()
    topic_list = stats.get("topic_list", [])
    
    if args.list:
        print_topics(topic_list)
    
    if args.search:
        matches = [t for t in topic_list if args.search.lower() in t.lower()]
        if matches:
            print(f"\nTopics matching '{args.search}':")
            for topic in matches:
                count_data = filter_by_topic(topic, "both", 1)
                total = len(count_data.get("content", [])) + len(count_data.get("blocks", []))
                print(f"   • {topic} ({total} items)")
        else:
            print(f"No topics found matching '{args.search}'")


def cmd_stats(args):
    """Handle stats command"""
    stats = get_stats()
    print_stats(stats)
    
    if args.format == "json":
        print(format_json(stats))


def cmd_export(args):
    """Handle export command"""
    if not args.output:
        print("Error: --output is required for export command", file=sys.stderr)
        sys.exit(1)
    
    # Perform search/filter based on other arguments
    if hasattr(args, 'query') and args.query:
        if args.type == "content":
            results = search_content(args.query, args.limit)
        elif args.type == "blocks":
            results = search_blocks(args.query, args.limit)
        else:
            results = {
                "content": search_content(args.query, args.limit // 2),
                "blocks": search_blocks(args.query, args.limit // 2)
            }
    elif hasattr(args, 'block_type') and args.block_type:
        results = filter_by_block_type(args.block_type, args.limit)
    elif hasattr(args, 'topic') and args.topic:
        results = filter_by_topic(args.topic, args.content_type, args.limit)
    else:
        # Export everything
        stats = get_stats()
        # This is a simplified export - in practice you'd want pagination
        results = {"message": "Export all not implemented yet - use search/filter instead"}
        print("Note: Full export not implemented. Please use search or filter options.")
    
    if args.format == "json":
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Exported {len(results) if isinstance(results, list) else 'data'} to {args.output}")
    else:
        print("Only JSON export is currently supported. Use --format json")


def main():
    parser = argparse.ArgumentParser(
        description="Content Library Query Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search across all content and blocks
  python cli.py search "product strategy"
  
  # Search only in blocks
  python cli.py search --type blocks "customer"
  
  # Filter by block type
  python cli.py filter --block-type B08
  
  # Filter by topic
  python cli.py filter --topic advisory --content-type both
  
  # Get stats
  python cli.py stats
  
  # List all topics
  python cli.py topics --list
  
  # Export results to JSON
  python cli.py search --query "hiring" --format json --output results.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search content and blocks')
    search_parser.add_argument('query', help='Search query string')
    search_parser.add_argument('--type', choices=['content', 'blocks', 'both'], 
                               default='both', help='What to search')
    search_parser.add_argument('--limit', type=int, default=50, help='Maximum results')
    search_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Output format')
    search_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Show detailed output')
    search_parser.set_defaults(func=cmd_search)
    
    # Filter command
    filter_parser = subparsers.add_parser('filter', help='Filter by block type or topic')
    filter_group = filter_parser.add_mutually_exclusive_group(required=True)
    filter_group.add_argument('--block-type', help='Filter by block code (B01, B08, etc.)')
    filter_group.add_argument('--topic', help='Filter by topic name')
    filter_parser.add_argument('--content-type', choices=['content', 'blocks', 'both'],
                               default='both', help='Content type when filtering by topic')
    filter_parser.add_argument('--limit', type=int, default=100, help='Maximum results')
    filter_parser.add_argument('--format', choices=['text', 'json'], default='text',
                               help='Output format')
    filter_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Show detailed output')
    filter_parser.set_defaults(func=cmd_filter)
    
    # Topics command
    topics_parser = subparsers.add_parser('topics', help='List and search topics')
    topics_parser.add_argument('--list', action='store_true', help='List all topics')
    topics_parser.add_argument('--search', help='Search topics by name')
    topics_parser.set_defaults(func=cmd_topics)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    stats_parser.add_argument('--format', choices=['text', 'json'], default='text',
                              help='Output format')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export search results')
    export_parser.add_argument('--output', '-o', required=True, help='Output file path')
    export_parser.add_argument('--format', choices=['json'], default='json',
                               help='Export format')
    export_parser.add_argument('--limit', type=int, default=1000, help='Maximum items')
    
    # Export can use search or filter options
    export_subparsers = export_parser.add_subparsers()
    
    export_search = export_subparsers.add_parser('search')
    export_search.add_argument('query', help='Search query')
    export_search.add_argument('--type', choices=['content', 'blocks', 'both'], 
                               default='both')
    
    export_filter = export_subparsers.add_parser('filter')
    filter_group = export_filter.add_mutually_exclusive_group(required=True)
    filter_group.add_argument('--block-type', help='Block code')
    filter_group.add_argument('--topic', help='Topic name')
    export_filter.add_argument('--content-type', choices=['content', 'blocks', 'both'],
                               default='both')
    
    export_parser.set_defaults(func=cmd_export)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.format == 'json':
            print(format_json({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()

