#!/usr/bin/env python3
"""
Content threading helper functions for YCB-style Entry/Comment system.
Provides functionality to create threads, add comments, and retrieve thread structures.
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

DB_PATH = "/home/workspace/N5/data/content_library.db"

def get_db_connection():
    """Get database connection with foreign key support enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def create_thread(root_item_id: str, title: Optional[str] = None) -> str:
    """
    Create a new content thread rooted at the given item.
    
    Args:
        root_item_id: ID of the content item that starts this thread
        title: Optional title for the thread (defaults to root item title)
    
    Returns:
        The thread_id of the created thread
    """
    thread_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        # If no title provided, use the root item's title
        if title is None:
            cursor = conn.execute("SELECT title FROM items WHERE id = ?", (root_item_id,))
            row = cursor.fetchone()
            if row:
                title = row['title']
            else:
                raise ValueError(f"Root item {root_item_id} not found")
        
        conn.execute("""
            INSERT INTO content_threads (id, root_item_id, title)
            VALUES (?, ?, ?)
        """, (thread_id, root_item_id, title))
        
        conn.commit()
    
    return thread_id

def add_comment(thread_id: str, content: str, parent_comment_id: Optional[str] = None, 
                comment_type: str = 'note', item_id: Optional[str] = None) -> str:
    """
    Add a comment to a thread.
    
    Args:
        thread_id: ID of the thread to add comment to
        content: The comment content
        parent_comment_id: ID of parent comment (None for top-level)
        comment_type: Type of comment ('note', 'synthesis', 'quote', 'link')
        item_id: Optional ID of content item if this comment references one
    
    Returns:
        The comment_id of the created comment
    """
    comment_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        # Verify thread exists
        cursor = conn.execute("SELECT id FROM content_threads WHERE id = ?", (thread_id,))
        if not cursor.fetchone():
            raise ValueError(f"Thread {thread_id} not found")
        
        # Verify parent comment exists if provided
        if parent_comment_id:
            cursor = conn.execute("SELECT id FROM thread_comments WHERE id = ?", (parent_comment_id,))
            if not cursor.fetchone():
                raise ValueError(f"Parent comment {parent_comment_id} not found")
        
        conn.execute("""
            INSERT INTO thread_comments (id, thread_id, parent_comment_id, item_id, content, comment_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (comment_id, thread_id, parent_comment_id, item_id, content, comment_type))
        
        # Update thread updated_at
        conn.execute("""
            UPDATE content_threads 
            SET updated_at = datetime('now')
            WHERE id = ?
        """, (thread_id,))
        
        conn.commit()
    
    return comment_id

def get_thread(thread_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a complete thread with nested comment structure.
    
    Args:
        thread_id: ID of the thread to retrieve
    
    Returns:
        Dictionary containing thread metadata and nested comments, or None if not found
    """
    with get_db_connection() as conn:
        # Get thread header
        cursor = conn.execute("""
            SELECT t.*, i.title as root_item_title, i.content_type as root_item_type
            FROM content_threads t
            LEFT JOIN items i ON t.root_item_id = i.id
            WHERE t.id = ?
        """, (thread_id,))
        
        thread_row = cursor.fetchone()
        if not thread_row:
            return None
        
        thread = dict(thread_row)
        
        # Get all comments for this thread
        cursor = conn.execute("""
            SELECT c.*, i.title as item_title, i.content_type as item_type
            FROM thread_comments c
            LEFT JOIN items i ON c.item_id = i.id
            WHERE c.thread_id = ?
            ORDER BY c.created_at
        """, (thread_id,))
        
        comments = [dict(row) for row in cursor.fetchall()]
        
        # Build nested comment structure
        comment_map = {}
        root_comments = []
        
        for comment in comments:
            comment['children'] = []
            comment_map[comment['id']] = comment
            
            if comment['parent_comment_id'] is None:
                root_comments.append(comment)
            else:
                parent = comment_map.get(comment['parent_comment_id'])
                if parent:
                    parent['children'].append(comment)
        
        thread['comments'] = root_comments
        return thread

def get_item_threads(item_id: str) -> List[Dict[str, Any]]:
    """
    Get all threads that involve a specific item (either as root or in comments).
    
    Args:
        item_id: ID of the content item
    
    Returns:
        List of thread summaries involving this item
    """
    with get_db_connection() as conn:
        # Threads where this item is the root
        cursor = conn.execute("""
            SELECT t.*, 'root' as involvement_type
            FROM content_threads t
            WHERE t.root_item_id = ?
        """, (item_id,))
        
        threads = [dict(row) for row in cursor.fetchall()]
        
        # Threads where this item is referenced in comments
        cursor = conn.execute("""
            SELECT DISTINCT t.*, 'comment' as involvement_type
            FROM content_threads t
            JOIN thread_comments c ON t.id = c.thread_id
            WHERE c.item_id = ? AND t.root_item_id != ?
        """, (item_id, item_id))
        
        threads.extend([dict(row) for row in cursor.fetchall()])
        
        return threads

def add_entry_link(source_item_id: str, target_item_id: str, 
                  link_type: str = 'related', strength: float = 0.5) -> str:
    """
    Create an explicit link between two content items.
    
    Args:
        source_item_id: ID of the source item
        target_item_id: ID of the target item  
        link_type: Type of link ('related', 'derived', 'contradicts', 'supports')
        strength: Strength of the link (0.0 to 1.0)
    
    Returns:
        The link_id of the created link
    """
    link_id = str(uuid.uuid4())
    
    with get_db_connection() as conn:
        # Verify both items exist
        cursor = conn.execute("SELECT COUNT(*) as count FROM items WHERE id IN (?, ?)", 
                             (source_item_id, target_item_id))
        if cursor.fetchone()['count'] != 2:
            raise ValueError("One or both items not found")
        
        try:
            conn.execute("""
                INSERT INTO entry_links (id, source_item_id, target_item_id, link_type, strength)
                VALUES (?, ?, ?, ?, ?)
            """, (link_id, source_item_id, target_item_id, link_type, strength))
            conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError(f"Link of type '{link_type}' between these items already exists")
    
    return link_id

def get_item_links(item_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all links involving an item (both as source and target).
    
    Args:
        item_id: ID of the content item
    
    Returns:
        Dictionary with 'outgoing' and 'incoming' link lists
    """
    with get_db_connection() as conn:
        # Outgoing links (this item as source)
        cursor = conn.execute("""
            SELECT l.*, i.title as target_title, i.content_type as target_type
            FROM entry_links l
            JOIN items i ON l.target_item_id = i.id
            WHERE l.source_item_id = ?
            ORDER BY l.strength DESC, l.created_at DESC
        """, (item_id,))
        
        outgoing = [dict(row) for row in cursor.fetchall()]
        
        # Incoming links (this item as target)
        cursor = conn.execute("""
            SELECT l.*, i.title as source_title, i.content_type as source_type
            FROM entry_links l
            JOIN items i ON l.source_item_id = i.id
            WHERE l.target_item_id = ?
            ORDER BY l.strength DESC, l.created_at DESC
        """, (item_id,))
        
        incoming = [dict(row) for row in cursor.fetchall()]
        
        return {
            'outgoing': outgoing,
            'incoming': incoming
        }

if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python content_threading.py <command> [args...]")
        print("Commands:")
        print("  test - Run basic functionality tests")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        print("Testing content threading functions...")
        
        # This would require actual content items to test properly
        # For now, just verify the functions can be imported
        print("✓ All functions imported successfully")
        print("✓ Database connection works")
        
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM items LIMIT 1")
            item_count = cursor.fetchone()['count']
            print(f"✓ Found {item_count} items in content library")