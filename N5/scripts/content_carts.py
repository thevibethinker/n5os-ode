#!/usr/bin/env python3
"""
Content Carts Helper Functions
Part of: ycb-content-layer build (D1.2)

Content Carts are temporary (or persistent) collections of entries for synthesis workflows.
Think of them like shopping carts for knowledge.
"""

import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import os
import json


def get_db_path() -> str:
    """Get the path to the content library database."""
    return "/home/workspace/N5/data/content_library.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with foreign key enforcement."""
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn


def create_cart(name: str, description: Optional[str] = None) -> str:
    """
    Create a new content cart.
    
    Args:
        name: Name of the cart
        description: Optional description
        
    Returns:
        cart_id: The ID of the created cart
    """
    cart_id = str(uuid.uuid4())
    
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO content_carts (id, name, description)
            VALUES (?, ?, ?)
        """, (cart_id, name, description))
        conn.commit()
    
    return cart_id


def add_to_cart(cart_id: str, item_id: str, notes: Optional[str] = None) -> bool:
    """
    Add an item to a cart.
    
    Args:
        cart_id: ID of the cart
        item_id: ID of the item to add
        notes: Optional notes about why this item is in the cart
        
    Returns:
        True if added successfully, False if already in cart or error
    """
    try:
        with get_connection() as conn:
            # Get the next order index for this cart
            cursor = conn.execute("""
                SELECT COALESCE(MAX(order_index), 0) + 1 as next_order
                FROM cart_items 
                WHERE cart_id = ?
            """, (cart_id,))
            next_order = cursor.fetchone()["next_order"]
            
            # Generate unique ID for cart_item
            cart_item_id = str(uuid.uuid4())
            
            conn.execute("""
                INSERT INTO cart_items (id, cart_id, item_id, notes, order_index)
                VALUES (?, ?, ?, ?, ?)
            """, (cart_item_id, cart_id, item_id, notes, next_order))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # Item already in cart or cart/item doesn't exist
        return False


def remove_from_cart(cart_id: str, item_id: str) -> bool:
    """
    Remove an item from a cart.
    
    Args:
        cart_id: ID of the cart
        item_id: ID of the item to remove
        
    Returns:
        True if removed successfully, False if not found
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            DELETE FROM cart_items 
            WHERE cart_id = ? AND item_id = ?
        """, (cart_id, item_id))
        conn.commit()
        return cursor.rowcount > 0


def get_cart(cart_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a cart with all its items.
    
    Args:
        cart_id: ID of the cart
        
    Returns:
        Dictionary with cart info and items, or None if not found
    """
    with get_connection() as conn:
        # Get cart info
        cursor = conn.execute("""
            SELECT * FROM content_carts WHERE id = ?
        """, (cart_id,))
        cart_row = cursor.fetchone()
        
        if not cart_row:
            return None
        
        cart = dict(cart_row)
        
        # Get cart items with full item details
        cursor = conn.execute("""
            SELECT 
                ci.id as cart_item_id,
                ci.added_at,
                ci.notes,
                ci.order_index,
                i.*
            FROM cart_items ci
            JOIN items i ON ci.item_id = i.id
            WHERE ci.cart_id = ?
            ORDER BY ci.order_index ASC, ci.added_at ASC
        """, (cart_id,))
        
        items = [dict(row) for row in cursor.fetchall()]
        cart["items"] = items
        cart["item_count"] = len(items)
        
        return cart


def list_carts(include_archived: bool = False) -> List[Dict[str, Any]]:
    """
    List all carts with basic info and item counts.
    
    Args:
        include_archived: Whether to include archived carts
        
    Returns:
        List of cart dictionaries with item counts
    """
    status_filter = "WHERE status IN ('active')" if not include_archived else "WHERE status != 'deleted'"
    
    with get_connection() as conn:
        cursor = conn.execute(f"""
            SELECT 
                cc.*,
                COUNT(ci.id) as item_count
            FROM content_carts cc
            LEFT JOIN cart_items ci ON cc.id = ci.cart_id
            {status_filter}
            GROUP BY cc.id
            ORDER BY cc.updated_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]


def archive_cart(cart_id: str) -> bool:
    """
    Archive a cart (mark as archived, don't delete).
    
    Args:
        cart_id: ID of the cart to archive
        
    Returns:
        True if archived successfully, False if not found
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE content_carts 
            SET status = 'archived'
            WHERE id = ? AND status = 'active'
        """, (cart_id,))
        conn.commit()
        return cursor.rowcount > 0


def reorder_cart_item(cart_id: str, item_id: str, new_order: int) -> bool:
    """
    Change the order of an item within a cart.
    
    Args:
        cart_id: ID of the cart
        item_id: ID of the item to reorder
        new_order: New order index
        
    Returns:
        True if reordered successfully
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE cart_items 
            SET order_index = ?
            WHERE cart_id = ? AND item_id = ?
        """, (new_order, cart_id, item_id))
        conn.commit()
        return cursor.rowcount > 0


def get_cart_summary(cart_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a quick summary of a cart without full item details.
    
    Args:
        cart_id: ID of the cart
        
    Returns:
        Dictionary with cart summary or None if not found
    """
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT 
                cc.*,
                COUNT(ci.id) as item_count,
                GROUP_CONCAT(DISTINCT i.content_type) as item_types
            FROM content_carts cc
            LEFT JOIN cart_items ci ON cc.id = ci.cart_id
            LEFT JOIN items i ON ci.item_id = i.id
            WHERE cc.id = ?
            GROUP BY cc.id
        """, (cart_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None


# Command-line interface for testing
if __name__ == "__main__":
    import sys
    
    def test_operations():
        """Test all cart operations with sample data."""
        print("Testing Content Carts operations...")
        
        # Test 1: Create cart
        print("\n1. Creating test cart...")
        cart_id = create_cart("Test Research Cart", "Testing the cart functionality")
        print(f"   Created cart: {cart_id}")
        
        # Test 2: List carts
        print("\n2. Listing carts...")
        carts = list_carts()
        print(f"   Found {len(carts)} carts")
        for cart in carts:
            print(f"   - {cart['name']}: {cart['item_count']} items")
        
        # Test 3: Add items (need to check if any items exist first)
        with get_connection() as conn:
            cursor = conn.execute("SELECT id, title FROM items LIMIT 3")
            sample_items = cursor.fetchall()
        
        if sample_items:
            print(f"\n3. Adding {len(sample_items)} items to cart...")
            for i, item in enumerate(sample_items):
                success = add_to_cart(cart_id, item["id"], f"Test note {i+1}")
                print(f"   Added '{item['title']}': {success}")
        else:
            print("\n3. No items found in database to add to cart")
        
        # Test 4: Get cart with items
        print("\n4. Retrieving cart with items...")
        cart_with_items = get_cart(cart_id)
        if cart_with_items:
            print(f"   Cart '{cart_with_items['name']}' has {len(cart_with_items['items'])} items:")
            for item in cart_with_items['items']:
                print(f"   - {item['title']} (notes: {item['notes']})")
        
        # Test 5: Archive cart
        print("\n5. Archiving cart...")
        archived = archive_cart(cart_id)
        print(f"   Archived: {archived}")
        
        print("\n✓ All tests completed successfully!")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_operations()
    else:
        print("Content Carts Helper Functions")
        print("Usage: python content_carts.py test")