#!/usr/bin/env python3
"""n5 content CLI for the YCB Content Layer build.

Available commands:
  n5 content thread create ...
  n5 content thread show ...
  n5 content comment add ...
  n5 content cart create ...
  n5 content cart add ...
  n5 content cart remove ...
  n5 content cart list
  n5 content cart show ...
  n5 content cart archive ...
  n5 content cart summary ...
  n5 content cart reorder ...
  n5 content preprocess ...
  n5 content links ...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

# Allow helper modules to live in the scripts directory
sys.path.insert(0, str(Path(__file__).parent))

from content_carts import (
    add_to_cart,
    archive_cart,
    create_cart,
    get_cart,
    get_cart_summary,
    list_carts,
    reorder_cart_item,
    remove_from_cart,
)
from content_preprocessor import main as preprocessor_main
from content_threading import (
    add_comment,
    create_thread,
    get_item_links,
    get_item_threads,
    get_thread,
)
from semantic_links import SemanticLinkEngine


def _run_preprocessor(args: argparse.Namespace) -> int:
    sys.argv = ['content_preprocessor.py', 'process', str(args.file)]
    if args.stages != 'extract,clean,enrich,store':
        sys.argv.extend(['--stages', args.stages])
    if args.dry_run:
        sys.argv.append('--dry-run')
    if args.type:
        sys.argv.extend(['--type', args.type])
    if args.quiet:
        sys.argv.append('--quiet')
    return preprocessor_main()


def _handle_links(args: argparse.Namespace) -> int:
    engine = SemanticLinkEngine()

    if args.links_command == 'compute':
        result = engine.compute_links(
            item_id=args.item_id,
            threshold=args.threshold,
            max_links=args.max_links,
        )
        if result.get('error'):
            print(f"Error: {result['error']}")
            return 1
        print(f"Created {result['links_created']} links for {args.item_id}")
        return 0

    if args.links_command == 'compute-all':
        result = engine.compute_links(
            threshold=args.threshold,
            max_links=args.max_links,
        )
        print(f"Processed {result['items_processed']} items")
        print(f"Created {result['total_links_created']} total links")
        if result.get('errors'):
            print(f"Errors: {len(result['errors'])}")
            for error in result['errors'][:5]:
                print(f"  {error}")
        return 0

    if args.links_command == 'related':
        related = engine.get_related(
            args.item_id,
            min_strength=args.min_strength,
            limit=args.limit,
        )
        if not related:
            print(f"No related items for {args.item_id}")
            return 0
        print(f"Related items for {args.item_id}:\n")
        for item in related:
            print(f"[{item['strength']:.2f}] {item['link_type']}: {item['title']}")
        return 0

    if args.links_command == 'graph':
        graph = engine.get_link_graph(args.item_id, depth=args.depth)
        print(f"Link graph for {args.item_id} (depth {args.depth}):")
        print(f"Nodes: {len(graph['nodes'])}")
        print(f"Edges: {len(graph['edges'])}")
        for edge in graph['edges'][:10]:
            source = next((n for n in graph['nodes'] if n['id'] == edge['source']), None)
            target = next((n for n in graph['nodes'] if n['id'] == edge['target']), None)
            if source and target:
                print(f"  {source['title'][:30]} --[{edge['strength']:.2f}]--> {target['title'][:30]}")
        return 0

    print('Unknown links command')
    return 1


def _handle_thread(args: argparse.Namespace) -> int:
    if args.thread_command == 'create':
        thread_id = create_thread(args.item_id, args.title)
        print(f"Created thread {thread_id} for item {args.item_id}")
        return 0
    if args.thread_command == 'show':
        thread = get_thread(args.thread_id)
        if not thread:
            print(f"Thread {args.thread_id} not found")
            return 1
        print(f"Thread: {thread['title']} ({thread['id']})")
        print(f"Comments: {len(thread['comments'])}")
        return 0
    if args.thread_command == 'list':
        threads = get_item_threads(args.item_id)
        if not threads:
            print(f"No threads for item {args.item_id}")
            return 0
        for thread in threads:
            print(f"- {thread['title']} ({thread['id']}) - root {thread['root_item_id']}")
        return 0
    if args.thread_command == 'links':
        links = get_item_links(args.item_id)
        print(f"Links for {args.item_id}:")
        print("Outgoing:")
        for link in links['outgoing']:
            print(f"  [{link['strength']:.2f}] {link['link_type']} -> {link['target_title']}")
        print("Incoming:")
        for link in links['incoming']:
            print(f"  [{link['strength']:.2f}] {link['link_type']} from {link['source_title']}")
        return 0
    print('Unknown thread command')
    return 1


def _handle_comment(args: argparse.Namespace) -> int:
    if args.comment_command == 'add':
        comment_id = add_comment(
            args.thread_id,
            args.content,
            parent_comment_id=args.parent,
            comment_type=args.type,
            item_id=args.item_id,
        )
        print(f"Added comment {comment_id} to thread {args.thread_id}")
        return 0
    print('Unknown comment command')
    return 1


def _handle_cart(args: argparse.Namespace) -> int:
    if args.cart_command == 'create':
        cart_id = create_cart(args.name, description=args.description)
        print(f"Created cart {cart_id}")
        return 0
    if args.cart_command == 'add':
        success = add_to_cart(args.cart_id, args.item_id, notes=args.notes)
        print("Added." if success else "Item already present or error")
        return 0 if success else 1
    if args.cart_command == 'remove':
        removed = remove_from_cart(args.cart_id, args.item_id)
        print("Removed." if removed else "Item was not in cart")
        return 0 if removed else 1
    if args.cart_command == 'list':
        carts = list_carts(include_archived=args.include_archived)
        for cart in carts:
            print(f"- {cart['id']} {cart['name']} ({cart['item_count']} items)")
        return 0
    if args.cart_command == 'show':
        cart = get_cart(args.cart_id)
        if not cart:
            print(f"Cart {args.cart_id} not found")
            return 1
        print(f"Cart {cart['name']} ({cart['item_count']} items)")
        for item in cart['items']:
            print(f"  - {item['title']} (notes: {item['notes']})")
        return 0
    if args.cart_command == 'summary':
        summary = get_cart_summary(args.cart_id)
        if not summary:
            print(f"Cart {args.cart_id} not found")
            return 1
        print(f"Cart {summary['name']}: {summary['item_count']} items, types: {summary['item_types']}")
        return 0
    if args.cart_command == 'archive':
        archived = archive_cart(args.cart_id)
        print("Archived." if archived else "Cart not found or already archived")
        return 0 if archived else 1
    if args.cart_command == 'reorder':
        updated = reorder_cart_item(args.cart_id, args.item_id, args.position)
        print("Reordered." if updated else "Failed to reorder")
        return 0 if updated else 1
    print('Unknown cart command')
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='n5 content',
        description='CLI for managing content threads, carts, preprocessing, and semantic links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest='command')

    # Thread commands
    thread_parser = subparsers.add_parser('thread', help='Thread management commands')
    thread_sub = thread_parser.add_subparsers(dest='thread_command')
    thread_create = thread_sub.add_parser('create', help='Create a thread for an item')
    thread_create.add_argument('item_id')
    thread_create.add_argument('--title')
    thread_show = thread_sub.add_parser('show', help='Show thread details')
    thread_show.add_argument('thread_id')
    thread_list = thread_sub.add_parser('list', help='List threads for an item')
    thread_list.add_argument('item_id')
    thread_links = thread_sub.add_parser('links', help='Show links for an item')
    thread_links.add_argument('item_id')

    # Comment commands
    comment_parser = subparsers.add_parser('comment', help='Comment management commands')
    comment_sub = comment_parser.add_subparsers(dest='comment_command')
    comment_add = comment_sub.add_parser('add', help='Add a comment to a thread')
    comment_add.add_argument('thread_id')
    comment_add.add_argument('content')
    comment_add.add_argument('--parent')
    comment_add.add_argument('--type', default='note')
    comment_add.add_argument('--item-id')

    # Cart commands
    cart_parser = subparsers.add_parser('cart', help='Cart management commands')
    cart_sub = cart_parser.add_subparsers(dest='cart_command')
    cart_create = cart_sub.add_parser('create', help='Create a cart')
    cart_create.add_argument('name')
    cart_create.add_argument('--description')
    cart_add = cart_sub.add_parser('add', help='Add item to cart')
    cart_add.add_argument('cart_id')
    cart_add.add_argument('item_id')
    cart_add.add_argument('--notes')
    cart_remove = cart_sub.add_parser('remove', help='Remove item from cart')
    cart_remove.add_argument('cart_id')
    cart_remove.add_argument('item_id')
    cart_list = cart_sub.add_parser('list', help='List carts')
    cart_list.add_argument('--include-archived', action='store_true')
    cart_show = cart_sub.add_parser('show', help='Show cart contents')
    cart_show.add_argument('cart_id')
    cart_summary = cart_sub.add_parser('summary', help='Summary for a cart')
    cart_summary.add_argument('cart_id')
    cart_archive = cart_sub.add_parser('archive', help='Archive a cart')
    cart_archive.add_argument('cart_id')
    cart_reorder = cart_sub.add_parser('reorder', help='Reorder cart item')
    cart_reorder.add_argument('cart_id')
    cart_reorder.add_argument('item_id')
    cart_reorder.add_argument('position', type=int)

    # Preprocess command
    preprocess_parser = subparsers.add_parser('preprocess', help='Content preprocessor')
    preprocess_parser.add_argument('file', type=Path)
    preprocess_parser.add_argument('--stages', default='extract,clean,enrich,store')
    preprocess_parser.add_argument('--dry-run', action='store_true')
    preprocess_parser.add_argument('--type')
    preprocess_parser.add_argument('--quiet', action='store_true')

    # Links command (delegated to semantic links)
    links_parser = subparsers.add_parser('links', help='Semantic link operations')
    links_parser.add_argument('--threshold', type=float, default=0.75)
    links_parser.add_argument('--max-links', type=int, default=5)
    links_sub = links_parser.add_subparsers(dest='links_command')
    links_compute = links_sub.add_parser('compute', help='Compute links for an item')
    links_compute.add_argument('item_id')
    links_compute.add_argument('--threshold', type=float, default=0.75)
    links_compute.add_argument('--max-links', type=int, default=5)
    links_compute_all = links_sub.add_parser('compute-all', help='Compute links for all items')
    links_compute_all.add_argument('--threshold', type=float, default=0.75)
    links_compute_all.add_argument('--max-links', type=int, default=5)
    links_related = links_sub.add_parser('related', help='Show related items')
    links_related.add_argument('item_id')
    links_related.add_argument('--min-strength', type=float, default=0.7)
    links_related.add_argument('--limit', type=int, default=10)
    links_graph = links_sub.add_parser('graph', help='Show link graph')
    links_graph.add_argument('item_id')
    links_graph.add_argument('--depth', type=int, default=2)

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'thread':
        return _handle_thread(args)
    if args.command == 'comment':
        return _handle_comment(args)
    if args.command == 'cart':
        return _handle_cart(args)
    if args.command == 'preprocess':
        return _run_preprocessor(args)
    if args.command == 'links':
        return _handle_links(args)

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
