#!/usr/bin/env python3
"""
Worker: worker_knowledge_bridge
Task: Append-only promotion to Knowledge Base
Input: SQLite database (Content Library), Knowledge Base system
Output: Promotion script + bridge table
Dependencies: worker_query (functional)
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

class KnowledgeBridge:
    def __init__(self):
        # Database paths
        self.content_lib_db = Path("/home/workspace/Personal/Content-Library/content-library.db")
        self.knowledge_base_db = Path("/home/workspace/Inbox/20251105-095007_Intelligence/blocks.db")
        
        # Initialize connections
        self.content_conn = None
        self.knowledge_conn = None
        
    def connect_databases(self):
        """Establish connections to both databases"""
        try:
            logger.info(f"Connecting to Content Library: {self.content_lib_db}")
            logger.info(f"Connecting to Knowledge Base: {self.knowledge_base_db}")
            self.content_conn = sqlite3.connect(self.content_lib_db)
            self.knowledge_conn = sqlite3.connect(self.knowledge_base_db)
        except Exception as e:
            logger.error(f"Failed to connect to databases: {e}")
            raise

    def create_bridge_table(self):
        """Create bridge table in Knowledge Base to track promotions"""
        logger.info("Creating bridge table in Knowledge Base")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS content_library_bridge (
            bridge_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL, -- 'content' or 'block'
            source_id TEXT NOT NULL,   -- content_id or block_id
            target_type TEXT NOT NULL, -- 'generation' or 'meeting'
            target_id TEXT,            -- generation_id or meeting identifier
            promotion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'promoted',
            metadata_json TEXT,        -- Additional metadata for tracking
            UNIQUE(source_type, source_id)
        );
        """
        
        try:
            cursor = self.knowledge_conn.cursor()
            cursor.execute(create_table_sql)
            self.knowledge_conn.commit()
            logger.info("✅ Bridge table created/exists in Knowledge Base")
        except Exception as e:
            logger.error(f"Failed to create bridge table: {e}")
            raise

    def get_unpromoted_content(self) -> List[Dict]:
        """Get content from Content Library that hasn't been promoted"""
        logger.info("Querying for unpromoted content")
        
        try:
            # First, get all promoted content IDs from Knowledge Base bridge
            promoted_ids = set()
            try:
                kb_cursor = self.knowledge_conn.cursor()
                kb_cursor.execute("SELECT source_id FROM content_library_bridge WHERE source_type = 'content'")
                promoted_ids = {row[0] for row in kb_cursor.fetchall()}
                logger.info(f"Found {len(promoted_ids)} already promoted content items")
            except Exception as e:
                logger.warning(f"Could not query bridge for promoted content: {e}")
            
            # Query all content from Content Library
            cursor = self.content_conn.cursor()
            query = """
            SELECT 
                c.id as content_id,
                c.notes as metadata_json,
                c.title,
                c.source_type as type,
                c.date_ingested as created_at
            FROM content c
            ORDER BY c.date_ingested ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            content_list = []
            for row in rows:
                content_id = row[0]
                if content_id not in promoted_ids:
                    content_list.append({
                        'content_id': content_id,
                        'metadata_json': row[1],
                        'title': row[2],
                        'type': row[3],
                        'created_at': row[4]
                    })
            
            logger.info(f"Found {len(content_list)} unpromoted content entries")
            return content_list
        except Exception as e:
            logger.error(f"Failed to query unpromoted content: {e}")
            return []

    def get_unpromoted_blocks(self) -> List[Dict]:
        """Get blocks from Content Library that haven't been promoted"""
        logger.info("Querying for unpromoted blocks")
        
        try:
            # First, get all promoted block IDs from Knowledge Base bridge
            promoted_ids = set()
            try:
                kb_cursor = self.knowledge_conn.cursor()
                kb_cursor.execute("SELECT source_id FROM content_library_bridge WHERE source_type = 'block'")
                promoted_ids = {row[0] for row in kb_cursor.fetchall()}
                logger.info(f"Found {len(promoted_ids)} already promoted blocks")
            except Exception as e:
                logger.warning(f"Could not query bridge for promoted blocks: {e}")
            
            # Query all blocks from Content Library
            cursor = self.content_conn.cursor()
            query = """
            SELECT 
                b.id as block_id,
                NULL as block_code,  -- Not available in this schema
                b.content_id,
                b.content as content_json,
                b.line_start as block_order,
                b.extracted_at as created_at
            FROM blocks b
            ORDER BY b.extracted_at ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            blocks_list = []
            for row in rows:
                block_id = row[0]
                if block_id not in promoted_ids:
                    blocks_list.append({
                        'block_id': block_id,
                        'block_code': row[1],  # Will be None
                        'content_id': row[2],
                        'content_json': row[3],
                        'block_order': row[4],
                        'created_at': row[5]
                    })
            
            logger.info(f"Found {len(blocks_list)} unpromoted blocks")
            return blocks_list
        except Exception as e:
            logger.error(f"Failed to query unpromoted blocks: {e}")
            return []

    def promote_content_to_meetings(self, content: List[Dict]) -> Dict[str, int]:
        """Promote content to Knowledge Base meeting structure"""
        logger.info(f"Promoting {len(content)} content entries to Knowledge Base")
        
        stats = {'promoted': 0, 'skipped': 0, 'errors': 0}
        
        try:
            for item in content:
                # Extract meeting metadata
                metadata = json.loads(item['metadata_json']) if item['metadata_json'] else {}
                
                # Insert into generation history as meeting context
                # Map content to meeting-style generation entries
                insert_sql = """
                INSERT INTO generation_history (
                    block_id,
                    meeting_id,
                    status,
                    input_context,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                """
                
                # Use a generic B00 block for meeting-level context
                # Meeting ID derived from content title
                meeting_id = f"meet_{item['content_id']}"
                status = "completed"
                input_context = json.dumps({
                    "title": item['title'],
                    "type": item['type'],
                    "metadata": metadata,
                    "promoted_from_content_library": True
                })
                
                cursor = self.knowledge_conn.cursor()
                cursor.execute(insert_sql, (
                    "B00",  # Generic meeting context block
                    meeting_id,
                    status,
                    input_context,
                    item['created_at']
                ))
                
                generation_id = cursor.lastrowid
                
                # Create bridge entry
                bridge_sql = """
                INSERT INTO content_library_bridge (
                    source_type,
                    source_id,
                    target_type,
                    target_id,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?)
                """
                
                cursor.execute(bridge_sql, (
                    "content",
                    item['content_id'],
                    "generation",
                    str(generation_id),
                    json.dumps({"meeting_id": meeting_id})
                ))
                
                stats['promoted'] += 1
                logger.info(f"Promoted content {item['content_id']} → generation {generation_id}")
            
            self.knowledge_conn.commit()
            return stats
        except Exception as e:
            logger.error(f"Error promoting content: {e}")
            stats['errors'] += 1
            self.knowledge_conn.rollback()
            return stats

    def promote_blocks_to_knowledge(self, blocks: List[Dict]) -> Dict[str, int]:
        """Promote blocks to Knowledge Base block structure"""
        logger.info(f"Promoting {len(blocks)} blocks to Knowledge Base")
        
        stats = {'promoted': 0, 'skipped': 0, 'errors': 0}
        
        try:
            for idx, block in enumerate(blocks):
                # Block content is plain text, not JSON
                block_content = block['content_json'] if block['content_json'] else ""
                
                # Insert into generation history as block generation
                sql = """
                INSERT INTO generation_history (
                    block_id,
                    meeting_id,
                    status,
                    input_context,
                    created_at
                ) VALUES (?, ?, ?, ?, ?)
                """
                
                # Link to meeting via content_id
                meeting_id = f"meet_{block['content_id']}"
                status = "completed"
                input_context = json.dumps({
                    "block_order": block['block_order'],
                    "content": block_content,
                    "promoted_from_content_library": True
                })
                
                cursor = self.knowledge_conn.cursor()
                
                # Use block_code if available, otherwise generate a pseudo-code
                if block['block_code']:
                    block_code = block['block_code']
                elif block['block_order'] is not None:
                    block_code = f"B{block['block_order']:02d}"
                else:
                    # Fallback for when both block_code and block_order are NULL
                    block_code = f"B{idx+1:02d}"
                
                cursor.execute(sql, (
                    block_code,
                    meeting_id,
                    status,
                    input_context,
                    block['created_at']
                ))
                
                generation_id = cursor.lastrowid
                
                # Create bridge entry
                bridge_sql = """
                INSERT INTO content_library_bridge (
                    source_type,
                    source_id,
                    target_type,
                    target_id,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?)
                """
                
                cursor.execute(bridge_sql, (
                    "block",
                    block['block_id'],
                    "generation",
                    str(generation_id),
                    json.dumps({
                        "block_code": block_code,
                        "meeting_id": meeting_id
                    })
                ))
                
                stats['promoted'] += 1
                logger.info(f"Promoted block {block['block_id']} → generation {generation_id}")
            
            self.knowledge_conn.commit()
            return stats
        except Exception as e:
            logger.error(f"Error promoting blocks: {e}")
            stats['errors'] += 1
            self.knowledge_conn.rollback()
            return stats

    def get_bridge_stats(self) -> Dict:
        """Get statistics about what's been promoted"""
        try:
            cursor = self.knowledge_conn.cursor()
            cursor.execute("""
                SELECT 
                    source_type,
                    COUNT(*) as count,
                    COUNT(DISTINCT source_id) as unique_sources,
                    MIN(promotion_date) as earliest,
                    MAX(promotion_date) as latest
                FROM content_library_bridge
                GROUP BY source_type
            """)
            
            stats = {
                'total_promoted': 0,
                'by_type': {}
            }
            for row in cursor.fetchall():
                source_type = row[0]
                count = row[1]
                unique_sources = row[2]
                earliest = row[3]
                latest = row[4]
                
                stats['by_type'][source_type] = {
                    'count': count,
                    'unique_sources': unique_sources,
                    'earliest': earliest,
                    'latest': latest
                }
                stats['total_promoted'] += count
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get bridge stats: {e}")
            return {'total_promoted': 0, 'by_type': {}}

    def close(self):
        """Close database connections"""
        if self.content_conn:
            self.content_conn.close()
        if self.knowledge_conn:
            self.knowledge_conn.close()
        logger.info("Database connections closed")

def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("Worker: worker_knowledge_bridge")
    logger.info("Task: Append-only promotion to Knowledge Base")
    logger.info("=" * 60)
    
    bridge = KnowledgeBridge()
    
    try:
        # Step 1: Connect to databases
        bridge.connect_databases()
        
        # Step 2: Create bridge table
        bridge.create_bridge_table()
        
        # Step 3: Check current stats
        current_stats = bridge.get_bridge_stats()
        logger.info("Current bridge statistics: %s", json.dumps(current_stats, indent=2))
        
        # Step 4: Get unpromoted content
        unpromoted_content = bridge.get_unpromoted_content()
        
        # Step 5: Promote content
        if unpromoted_content:
            content_stats = bridge.promote_content_to_meetings(unpromoted_content)
            logger.info("Content promotion stats: %s", json.dumps(content_stats, indent=2))
        else:
            content_stats = {'promoted': 0, 'skipped': 0, 'errors': 0}
            logger.info("No unpromoted content found")
        
        # Step 6: Get unpromoted blocks
        unpromoted_blocks = bridge.get_unpromoted_blocks()
        
        # Step 7: Promote blocks
        if unpromoted_blocks:
            block_stats = bridge.promote_blocks_to_knowledge(unpromoted_blocks)
            logger.info("Block promotion stats: %s", json.dumps(block_stats, indent=2))
        else:
            block_stats = {'promoted': 0, 'skipped': 0, 'errors': 0}
            logger.info("No unpromoted blocks found")
        
        # Step 8: Final statistics
        final_stats = bridge.get_bridge_stats()
        logger.info("Final bridge statistics: %s", json.dumps(final_stats, indent=2))
        
        # Summary
        logger.info("=" * 60)
        logger.info("PROMOTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Content promoted: {content_stats['promoted']}")
        logger.info(f"Blocks promoted: {block_stats['promoted']}")
        logger.info(f"Total bridge records: {final_stats['total_promoted']}")
        logger.info(f"Errors: {content_stats['errors'] + block_stats['errors']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error during promotion: {e}", exc_info=True)
        return 1
        
    finally:
        bridge.close()

if __name__ == '__main__':
    exit(main())






