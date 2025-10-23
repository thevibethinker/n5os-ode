#!/usr/bin/env python3
"""
N5 Social Post Manager - CLI for social media content tracking
Part of N5 OS - Social Media Content Management System

Usage:
    n5_social_post.py add <file> --platform <platform> [--status <status>]
    n5_social_post.py status <post_id> <new_status> [--url <url>] [--notes <notes>]
    n5_social_post.py list [--platform <platform>] [--status <status>] [--limit <n>]
    n5_social_post.py stats
    n5_social_post.py verify [<post_id>]
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# Add N5 scripts to path
sys.path.insert(0, str(Path(__file__).parent))

import social_post_lib as spl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def cmd_add(args) -> int:
    """Add new post to library"""
    try:
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            logger.error("File is empty")
            return 1
        
        post = spl.add_post(
            content=content,
            platform=args.platform,
            status=args.status,
            title=args.title,
            slug=args.slug,
            source=args.source,
            conversation_id=args.conversation_id,
            tags=args.tags.split(',') if args.tags else None,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            logger.info(f"[DRY RUN] Post record:")
            logger.info(f"  ID: {post['id']}")
            logger.info(f"  Title: {post['title']}")
            logger.info(f"  Slug: {post['slug']}")
            logger.info(f"  File: {post['file_path']}")
        else:
            logger.info(f"✓ Added post: {post['id']}")
            logger.info(f"  Title: {post['title']}")
            logger.info(f"  Platform: {post['platform']}")
            logger.info(f"  Status: {post['status']}")
            logger.info(f"  File: {post['file_path']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error adding post: {e}", exc_info=True)
        return 1


def cmd_status(args) -> int:
    """Update post status"""
    try:
        post = spl.update_post_status(
            post_id=args.post_id,
            new_status=args.new_status,
            published_url=args.url,
            review_notes=args.notes,
            dry_run=args.dry_run
        )
        
        if not args.dry_run:
            logger.info(f"✓ Updated: {post['id']}")
            logger.info(f"  Status: {post['status']}")
            logger.info(f"  File: {post['file_path']}")
            if post.get('published_url'):
                logger.info(f"  URL: {post['published_url']}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error updating status: {e}", exc_info=True)
        return 1


def cmd_list(args) -> int:
    """List posts with filters"""
    try:
        posts = spl.list_posts(
            platform=args.platform,
            status=args.status,
            limit=args.limit
        )
        
        if not posts:
            logger.info("No posts found")
            return 0
        
        logger.info(f"Found {len(posts)} post(s):\n")
        
        for post in posts:
            print(f"ID: {post['id']}")
            print(f"  Title: {post['title']}")
            print(f"  Platform: {post['platform']}")
            print(f"  Status: {post['status']}")
            print(f"  Created: {post['created'][:10]}")
            print(f"  Words: {post['word_count']}")
            print(f"  File: {post['file_path']}")
            if post.get('published_url'):
                print(f"  URL: {post['published_url']}")
            if post.get('tags'):
                print(f"  Tags: {', '.join(post['tags'])}")
            print()
        
        return 0
    
    except Exception as e:
        logger.error(f"Error listing posts: {e}", exc_info=True)
        return 1


def cmd_stats(args) -> int:
    """Show summary statistics"""
    try:
        stats = spl.get_stats()
        
        print(f"Total Posts: {stats['total']}\n")
        
        print("By Status:")
        for status, count in sorted(stats['by_status'].items()):
            print(f"  {status}: {count}")
        
        print("\nBy Platform:")
        for platform, count in sorted(stats['by_platform'].items()):
            print(f"  {platform}: {count}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return 1


def cmd_verify(args) -> int:
    """Verify post files"""
    try:
        if args.post_id:
            post = spl.find_post_by_id(args.post_id)
            if not post:
                logger.error(f"Post not found: {args.post_id}")
                return 1
            posts = [post]
        else:
            posts = spl.load_registry()
        
        success_count = 0
        failure_count = 0
        
        for post in posts:
            if spl.verify_post_file(post):
                success_count += 1
                logger.info(f"✓ Verified: {post['id']} - {post['title']}")
            else:
                failure_count += 1
        
        logger.info(f"\nVerification complete: {success_count} OK, {failure_count} failed")
        
        return 0 if failure_count == 0 else 1
    
    except Exception as e:
        logger.error(f"Error verifying: {e}", exc_info=True)
        return 1


def cmd_health(args) -> int:
    """Run system health check"""
    try:
        print("\n" + "="*70)
        print("SOCIAL POSTS SYSTEM HEALTH CHECK")
        print("="*70 + "\n")
        
        # Check registry
        print(f"Registry: {spl.REGISTRY_PATH}")
        registry_exists = spl.REGISTRY_PATH.exists()
        print(f"  Exists: {'✓' if registry_exists else '✗'}")
        
        if not registry_exists:
            print(f"\n✗ Registry not found\n")
            return 1
        
        # Load posts
        try:
            posts = spl.load_registry()
            print(f"  Readable: ✓")
            print()
        except Exception as e:
            print(f"  Readable: ✗ ({e})")
            print()
            return 1
        
        # Get stats
        stats = spl.get_stats()
        
        status = "healthy" if stats['total'] > 0 else "empty"
        print(f"Status: {status.upper()}")
        print(f"Total Posts: {stats['total']}")
        print()
        
        if stats['by_platform']:
            print("Posts by Platform:")
            for platform, count in stats['by_platform'].items():
                print(f"  {platform}: {count}")
            print()
        
        if stats['by_status']:
            print("Posts by Status:")
            for status_name, count in stats['by_status'].items():
                print(f"  {status_name}: {count}")
            print()
        
        # Verify files
        missing_files = []
        empty_files = []
        
        for post in posts:
            file_verified = spl.verify_post_file(post)
            if not file_verified:
                file_path = spl.WORKSPACE / post['file_path']
                if not file_path.exists():
                    missing_files.append(post['id'])
                elif file_path.stat().st_size == 0:
                    empty_files.append(post['id'])
        
        if missing_files:
            print(f"⚠ Missing Files: {len(missing_files)}")
            if args.verbose:
                for post_id in missing_files:
                    print(f"  - {post_id}")
            print()
        
        if empty_files:
            print(f"⚠ Empty Files: {len(empty_files)}")
            if args.verbose:
                for post_id in empty_files:
                    print(f"  - {post_id}")
            print()
        
        return 0 if not (missing_files or empty_files) else 1
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


def cmd_import(args) -> int:
    """Batch import posts from directory"""
    try:
        base = Path(args.dir).expanduser().resolve()
        if not base.exists() or not base.is_dir():
            logger.error(f"Directory not found: {base}")
            return 1
        
        pattern = args.pattern
        files = sorted(base.glob(pattern))
        
        if not files:
            logger.info(f"No files matched pattern: {pattern}")
            return 0
        
        logger.info(f"Found {len(files)} file(s) to import")
        
        imported_count = 0
        for file_path in files:
            try:
                logger.info(f"Processing: {file_path.name}")
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    logger.warning(f"Skipping empty file: {file_path.name}")
                    continue
                
                # Import using add_post
                post = spl.add_post(
                    content=content,
                    platform=args.platform,
                    status=args.status,
                    source='imported',
                    dry_run=args.dry_run
                )
                
                if not args.dry_run and post:
                    logger.info(f"✓ Imported: {post['id']} - {post['title']}")
                    imported_count += 1
            
            except Exception as e:
                logger.error(f"Error importing {file_path.name}: {e}")
                continue
        
        logger.info(f"Import complete: {imported_count}/{len(files)} file(s) imported")
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="N5 Social Post Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add new post')
    add_parser.add_argument('file', help='Path to post file')
    add_parser.add_argument('--platform', required=True, choices=spl.VALID_PLATFORMS)
    add_parser.add_argument('--status', default='draft', choices=spl.VALID_STATUSES)
    add_parser.add_argument('--title', help='Custom title')
    add_parser.add_argument('--slug', help='Custom slug')
    add_parser.add_argument('--source', default='manual', help='Source (manual, generated, imported)')
    add_parser.add_argument('--conversation-id', help='Conversation ID where post was created')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Update post status')
    status_parser.add_argument('post_id', help='Post ID')
    status_parser.add_argument('new_status', choices=spl.VALID_STATUSES)
    status_parser.add_argument('--url', help='Published URL (for submitted status)')
    status_parser.add_argument('--notes', help='Review notes')
    status_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List posts')
    list_parser.add_argument('--platform', choices=spl.VALID_PLATFORMS)
    list_parser.add_argument('--status', choices=spl.VALID_STATUSES)
    list_parser.add_argument('--limit', type=int, help='Maximum number of posts to show')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show summary statistics')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify post files')
    verify_parser.add_argument('post_id', nargs='?', help='Specific post ID (optional)')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Run system health check')
    health_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed information')
    
    # Import command (batch import from directory)
    import_parser = subparsers.add_parser('import', help='Batch import posts from directory')
    import_parser.add_argument('--dir', required=True, help='Directory containing post files')
    import_parser.add_argument('--platform', required=True, choices=spl.VALID_PLATFORMS)
    import_parser.add_argument('--status', default='draft', choices=spl.VALID_STATUSES)
    import_parser.add_argument('--pattern', default='*-post-draft.md', help='File pattern to match')
    import_parser.add_argument('--dry-run', action='store_true', help='Preview without importing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'add': cmd_add,
        'status': cmd_status,
        'list': cmd_list,
        'stats': cmd_stats,
        'verify': cmd_verify,
        'health': cmd_health,
        'import': cmd_import,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
