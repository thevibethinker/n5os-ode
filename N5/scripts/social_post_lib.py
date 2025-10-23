#!/usr/bin/env python3
"""
Social Post Library - Core functions for social media content tracking
Part of N5 OS - Social Media Content Management System

Manages social posts through lifecycle: draft → pending → submitted → archived
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Constants
WORKSPACE = Path("/home/workspace")
REGISTRY_PATH = WORKSPACE / "N5/data/social-posts.jsonl"
CONTENT_BASE = WORKSPACE / "Knowledge/personal-brand/social-content"
EMOJI_PREFIX = "🔗_"

VALID_PLATFORMS = ["linkedin", "twitter", "facebook", "instagram"]
VALID_STATUSES = ["draft", "pending", "submitted", "archived", "declined"]


def generate_post_id(content: str) -> str:
    """Generate unique post ID from content hash"""
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return f"post_{hash_obj.hexdigest()[:12]}"


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to URL-safe slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:max_length].strip('-')


def create_post_filename(platform: str, slug: str, timestamp: Optional[str] = None) -> str:
    """Generate standardized filename with emoji prefix"""
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    return f"{EMOJI_PREFIX}{timestamp}_{platform}_{slug}.md"


def extract_title_from_content(content: str) -> str:
    """Extract first line or first sentence as title"""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if not lines:
        return "Untitled Post"
    
    first_line = lines[0].lstrip('#').strip()
    
    # If first line is too long, take first sentence
    if len(first_line) > 80:
        sentences = re.split(r'[.!?]\s+', first_line)
        if sentences:
            return sentences[0][:80].strip()
    
    return first_line[:80].strip()


def load_registry() -> List[Dict[str, Any]]:
    """Load all posts from registry"""
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        REGISTRY_PATH.touch()
        return []
    
    posts = []
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                posts.append(json.loads(line))
    return posts


def save_post_to_registry(post: Dict[str, Any]) -> None:
    """Append post to registry (atomic append)"""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(post, ensure_ascii=False) + '\n')
    logger.info(f"✓ Added to registry: {post['id']}")


def update_registry(posts: List[Dict[str, Any]]) -> None:
    """Rewrite entire registry (for updates/deletes)"""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        for post in posts:
            f.write(json.dumps(post, ensure_ascii=False) + '\n')
    logger.info(f"✓ Updated registry: {len(posts)} posts")


def find_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
    """Find post in registry by ID"""
    posts = load_registry()
    for post in posts:
        if post['id'] == post_id:
            return post
    return None


def find_posts_by_status(status: str) -> List[Dict[str, Any]]:
    """Find all posts with given status"""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}. Must be one of {VALID_STATUSES}")
    
    posts = load_registry()
    return [p for p in posts if p['status'] == status]


def find_posts_by_platform(platform: str) -> List[Dict[str, Any]]:
    """Find all posts for given platform"""
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Invalid platform: {platform}. Must be one of {VALID_PLATFORMS}")
    
    posts = load_registry()
    return [p for p in posts if p['platform'] == platform]


def create_post_record(
    content: str,
    platform: str,
    status: str = "draft",
    title: Optional[str] = None,
    slug: Optional[str] = None,
    source: str = "manual",
    conversation_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Create new post record with metadata"""
    
    if platform not in VALID_PLATFORMS:
        raise ValueError(f"Invalid platform: {platform}")
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    
    now = datetime.now(timezone.utc).isoformat()
    post_id = generate_post_id(content)
    
    if not title:
        title = extract_title_from_content(content)
    
    if not slug:
        slug = slugify(title)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    filename = create_post_filename(platform, slug, timestamp)
    
    file_path = CONTENT_BASE / platform / status / filename
    
    record = {
        "id": post_id,
        "created": now,
        "updated": now,
        "platform": platform,
        "status": status,
        "title": title,
        "slug": slug,
        "file_path": str(file_path.relative_to(WORKSPACE)),
        "word_count": len(content.split()),
        "character_count": len(content),
        "tags": tags or [],
        "scheduled_date": None,
        "published_date": None,
        "published_url": None,
        "source": source,
        "conversation_id": conversation_id,
        "review_notes": "",
        "version": 1
    }
    
    return record


def add_post(
    content: str,
    platform: str,
    status: str = "draft",
    title: Optional[str] = None,
    slug: Optional[str] = None,
    source: str = "manual",
    conversation_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Add new post to library"""
    
    record = create_post_record(
        content=content,
        platform=platform,
        status=status,
        title=title,
        slug=slug,
        source=source,
        conversation_id=conversation_id,
        tags=tags
    )
    
    file_path = WORKSPACE / record['file_path']
    
    if dry_run:
        logger.info(f"[DRY RUN] Would create: {file_path}")
        logger.info(f"[DRY RUN] Would add to registry: {record['id']}")
        return record
    
    # Create file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"✓ Created: {file_path}")
    
    # Add to registry
    save_post_to_registry(record)
    
    return record


def update_post_status(
    post_id: str,
    new_status: str,
    published_url: Optional[str] = None,
    review_notes: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Update post status and move file to new folder"""
    
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}")
    
    posts = load_registry()
    post = None
    post_index = None
    
    for i, p in enumerate(posts):
        if p['id'] == post_id:
            post = p
            post_index = i
            break
    
    if not post:
        raise ValueError(f"Post not found: {post_id}")
    
    old_status = post['status']
    if old_status == new_status:
        logger.info(f"Post {post_id} already has status: {new_status}")
        return post
    
    # Update record
    post['status'] = new_status
    post['updated'] = datetime.now(timezone.utc).isoformat()
    
    if review_notes:
        post['review_notes'] = review_notes
    
    if new_status == "submitted" and published_url:
        post['published_url'] = published_url
        post['published_date'] = datetime.now(timezone.utc).isoformat()
    
    # Calculate new file path
    old_file_path = WORKSPACE / post['file_path']
    filename = old_file_path.name
    new_file_path = CONTENT_BASE / post['platform'] / new_status / filename
    
    if dry_run:
        logger.info(f"[DRY RUN] Would move: {old_file_path} → {new_file_path}")
        logger.info(f"[DRY RUN] Would update status: {old_status} → {new_status}")
        return post
    
    # Move file
    new_file_path.parent.mkdir(parents=True, exist_ok=True)
    if old_file_path.exists():
        old_file_path.rename(new_file_path)
        logger.info(f"✓ Moved: {old_file_path.name} → {new_status}/")
    else:
        logger.warning(f"⚠ File not found: {old_file_path}")
    
    # Update file path in record
    post['file_path'] = str(new_file_path.relative_to(WORKSPACE))
    
    # Update registry
    posts[post_index] = post
    update_registry(posts)
    
    logger.info(f"✓ Updated status: {post_id} ({old_status} → {new_status})")
    
    return post


def list_posts(
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """List posts with optional filters"""
    
    posts = load_registry()
    
    if platform:
        posts = [p for p in posts if p['platform'] == platform]
    
    if status:
        posts = [p for p in posts if p['status'] == status]
    
    # Sort by created date (newest first)
    posts.sort(key=lambda p: p['created'], reverse=True)
    
    if limit:
        posts = posts[:limit]
    
    return posts


def verify_post_file(post: Dict[str, Any]) -> bool:
    """Verify post file exists and matches metadata"""
    file_path = WORKSPACE / post['file_path']
    
    if not file_path.exists():
        logger.error(f"✗ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    word_count = len(content.split())
    char_count = len(content)
    
    # Allow 10% variance in counts
    if abs(word_count - post['word_count']) > post['word_count'] * 0.1:
        logger.warning(f"⚠ Word count mismatch: {post['id']}")
    
    if abs(char_count - post['character_count']) > post['character_count'] * 0.1:
        logger.warning(f"⚠ Character count mismatch: {post['id']}")
    
    return True


def get_stats() -> Dict[str, Any]:
    """Get summary statistics"""
    posts = load_registry()
    
    stats = {
        "total": len(posts),
        "by_status": {},
        "by_platform": {}
    }
    
    for post in posts:
        # Count by status
        status = post['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        # Count by platform
        platform = post['platform']
        stats['by_platform'][platform] = stats['by_platform'].get(platform, 0) + 1
    
    return stats
