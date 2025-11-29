"""
Content Library Search Module
Core search functionality for querying the SQLite database
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class ContentSearch:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "content-library.db"
        self.db_path = str(db_path)
    
    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def search_content(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Full-text search across content titles and notes
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT id, source_type, title, date_created, topics, tags, notes
                FROM content
                WHERE title LIKE ? OR notes LIKE ?
                ORDER BY date_created DESC
                LIMIT ?
            """
            search_term = f"%{query}%"
            cursor.execute(sql, (search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "source_type": row[1],
                    "title": row[2],
                    "date_created": row[3],
                    "topics": self._parse_json(row[4]),
                    "tags": self._parse_json(row[5]),
                    "notes": row[6]
                })
            return results
    
    def search_blocks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Full-text search across block content and context
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT b.id, b.content_id, b.block_code, b.block_type,
                       b.content, b.context, b.speaker, b.topics, b.tags,
                       c.title as content_title
                FROM blocks b
                LEFT JOIN content c ON b.content_id = c.id
                WHERE b.content LIKE ? OR b.context LIKE ?
                ORDER BY b.extracted_at DESC
                LIMIT ?
            """
            search_term = f"%{query}%"
            cursor.execute(sql, (search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content_id": row[1],
                    "block_code": row[2],
                    "block_type": row[3],
                    "content": row[4],
                    "context": row[5],
                    "speaker": row[6],
                    "topics": self._parse_json(row[7]),
                    "tags": self._parse_json(row[8]),
                    "content_title": row[9]
                })
            return results
    
    def filter_by_block_type(self, block_code: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Filter blocks by block code (B01, B08, B21, etc.)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT b.id, b.content_id, b.block_code, b.block_type,
                       b.content, b.context, b.speaker, b.topics, b.tags,
                       c.title as content_title, c.date_created
                FROM blocks b
                LEFT JOIN content c ON b.content_id = c.id
                WHERE b.block_code = ?
                ORDER BY c.date_created DESC
                LIMIT ?
            """
            cursor.execute(sql, (block_code, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content_id": row[1],
                    "block_code": row[2],
                    "block_type": row[3],
                    "content": row[4],
                    "context": row[5],
                    "speaker": row[6],
                    "topics": self._parse_json(row[7]),
                    "tags": self._parse_json(row[8]),
                    "content_title": row[9],
                    "date_created": row[10]
                })
            return results
    
    def filter_by_topic(self, topic: str, content_type: str = "both", limit: int = 100) -> Dict[str, List]:
        """
        Filter by topic name - returns both content and blocks
        content_type: "content", "blocks", or "both"
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            results = {"content": [], "blocks": []}
            
            if content_type in ["content", "both"]:
                sql = """
                    SELECT c.id, c.source_type, c.title, c.date_created,
                           c.topics, c.tags, c.notes
                    FROM content c
                    JOIN content_topics ct ON c.id = ct.content_id
                    JOIN topics t ON ct.topic_id = t.id
                    WHERE t.name = ?
                    ORDER BY c.date_created DESC
                    LIMIT ?
                """
                cursor.execute(sql, (topic, limit))
                
                for row in cursor.fetchall():
                    results["content"].append({
                        "id": row[0],
                        "source_type": row[1],
                        "title": row[2],
                        "date_created": row[3],
                        "topics": self._parse_json(row[4]),
                        "tags": self._parse_json(row[5]),
                        "notes": row[6]
                    })
            
            if content_type in ["blocks", "both"]:
                sql = """
                    SELECT b.id, b.content_id, b.block_code, b.block_type,
                           b.content, b.context, b.speaker, b.topics, b.tags,
                           c.title as content_title, c.date_created
                    FROM blocks b
                    JOIN block_topics bt ON b.id = bt.block_id
                    JOIN topics t ON bt.topic_id = t.id
                    LEFT JOIN content c ON b.content_id = c.id
                    WHERE t.name = ?
                    ORDER BY c.date_created DESC
                    LIMIT ?
                """
                cursor.execute(sql, (topic, limit))
                
                for row in cursor.fetchall():
                    results["blocks"].append({
                        "id": row[0],
                        "content_id": row[1],
                        "block_code": row[2],
                        "block_type": row[3],
                        "content": row[4],
                        "context": row[5],
                        "speaker": row[6],
                        "topics": self._parse_json(row[7]),
                        "tags": self._parse_json(row[8]),
                        "content_title": row[9],
                        "date_created": row[10]
                    })
            
            return results
    
    def get_recent_content(self, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recently added content (default: last 30 days)
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT id, source_type, title, date_created, date_ingested,
                       topics, tags, notes
                FROM content
                WHERE date_created >= date('now', '-{days} days')
                ORDER BY date_created DESC
                LIMIT {limit}
            """.format(days=days, limit=limit)
            
            cursor.execute(sql)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "source_type": row[1],
                    "title": row[2],
                    "date_created": row[3],
                    "date_ingested": row[4],
                    "topics": self._parse_json(row[5]),
                    "tags": self._parse_json(row[6]),
                    "notes": row[7]
                })
            return results
    
    def get_content_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Content count by type
            cursor.execute("""
                SELECT source_type, COUNT(*)
                FROM content
                GROUP BY source_type
            """)
            stats["content_by_type"] = dict(cursor.fetchall())
            
            # Total content
            cursor.execute("SELECT COUNT(*) FROM content")
            stats["total_content"] = cursor.fetchone()[0]
            
            # Total blocks
            cursor.execute("SELECT COUNT(*) FROM blocks")
            stats["total_blocks"] = cursor.fetchone()[0]
            
            # Blocks by type
            cursor.execute("""
                SELECT block_code, COUNT(*)
                FROM blocks
                GROUP BY block_code
                ORDER BY COUNT(*) DESC
            """)
            stats["blocks_by_code"] = dict(cursor.fetchall())
            
            # Topics
            cursor.execute("SELECT COUNT(*) FROM topics")
            stats["total_topics"] = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT name
                FROM topics
                ORDER BY name
            """)
            stats["topic_list"] = [row[0] for row in cursor.fetchall()]
            
            return stats
    
    def _parse_json(self, json_str: Optional[str]) -> List[str]:
        """
        Parse JSON array from database (handling NULL values)
        """
        if not json_str:
            return []
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return data
            return []
        except:
            return []


# Export convenient functions
_search_instance = None

def get_search() -> ContentSearch:
    global _search_instance
    if _search_instance is None:
        _search_instance = ContentSearch()
    return _search_instance

# Shortcut functions
def search_content(query: str, limit: int = 50):
    return get_search().search_content(query, limit)

def search_blocks(query: str, limit: int = 50):
    return get_search().search_blocks(query, limit)

def filter_by_block_type(block_code: str, limit: int = 100):
    return get_search().filter_by_block_type(block_code, limit)

def filter_by_topic(topic: str, content_type: str = "both", limit: int = 100):
    return get_search().filter_by_topic(topic, content_type, limit)

def get_stats():
    return get_search().get_content_stats()

