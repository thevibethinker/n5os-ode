#!/usr/bin/env python3
"""
Migration script: Re-embed all blocks from brain.db to brain_v2.db
Migrates from all-MiniLM-L6-v2 (384-dim) to text-embedding-3-large (3072-dim)

Features:
- Checkpoint every 500 blocks
- Resume capability from checkpoint
- Rate limiting with backoff
- Progress logging
- Cost estimation and tracking
"""

import sqlite3
import os
import sys
import time
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

# Add N5 lib to path
sys.path.insert(0, '/home/workspace')
from N5.lib.paths import BRAIN_DB

# Check for OpenAI
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("ERROR: OpenAI package not installed. Run: pip install openai")
    sys.exit(1)

# Configuration
SOURCE_DB = str(BRAIN_DB)
TARGET_DB = SOURCE_DB.replace("brain.db", "brain_v2.db")
CHECKPOINT_FILE = "/home/workspace/N5/cognition/migration_checkpoint.json"
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIM = 3072
BATCH_SIZE = 100  # Process in batches for efficiency
CHECKPOINT_INTERVAL = 500  # Save checkpoint every N blocks
RATE_LIMIT_DELAY = 0.12  # ~8 requests per second (OpenAI free tier limit)
MAX_RETRIES = 5
BASE_BACKOFF = 2.0

# Cost estimation (as of 2026-01)
# text-embedding-3-large: $0.13 per 1M tokens
COST_PER_1M_TOKENS = 0.13

# Setup logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/workspace/N5/cognition/migration.log')
    ]
)
LOG = logging.getLogger("migrate_embeddings")


class EmbeddingMigrator:
    def __init__(self):
        self.source_conn = sqlite3.connect(SOURCE_DB)
        self.target_conn = None
        self.openai_client = self._init_openai()
        self.checkpoint = self._load_checkpoint()
        
        # Statistics
        self.total_blocks = 0
        self.migrated_blocks = 0
        self.skipped_blocks = 0
        self.total_tokens = 0
        self.start_time = None
        self.last_rate_limit_time = 0
        
    def _init_openai(self) -> OpenAI:
        """Initialize OpenAI client with API key from env or secret file."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Check secret file if not in env
        if not api_key:
            key_path = "/home/workspace/N5/config/secrets/openai.key"
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    api_key = f.read().strip()
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment or secret file")
        
        return OpenAI(api_key=api_key)
    
    def _load_checkpoint(self) -> Dict:
        """Load checkpoint if exists."""
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        return {
            "migrated_blocks": [],
            "last_block_index": -1,
            "total_tokens": 0,
            "cost_estimate_usd": 0.0,
            "start_time": None,
            "last_updated": None
        }
    
    def _save_checkpoint(self):
        """Save current progress to checkpoint file."""
        checkpoint = {
            **self.checkpoint,
            "last_updated": datetime.now().isoformat(),
            "cost_estimate_usd": self._estimate_cost()
        }
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        LOG.info(f"Checkpoint saved: {len(self.checkpoint['migrated_blocks'])} blocks migrated")
    
    def _estimate_cost(self) -> float:
        """Estimate total cost based on tokens processed."""
        return (self.total_tokens / 1_000_000) * COST_PER_1M_TOKENS
    
    def _init_target_db(self):
        """Create target database with v2 schema."""
        self.target_conn = sqlite3.connect(TARGET_DB)
        
        # Create metadata table
        self.target_conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Create resources table
        self.target_conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                hash TEXT,
                last_indexed_at DATETIME,
                content_date DATETIME
            )
        """)
        
        # Create blocks table
        self.target_conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                block_type TEXT,
                content TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                token_count INTEGER,
                content_date DATETIME,
                FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
        """)
        
        # Create vectors table with embedding_dim column
        self.target_conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                block_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                embedding_dim INTEGER DEFAULT 3072,
                FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        """)
        
        self.target_conn.commit()
        LOG.info(f"Target database initialized: {TARGET_DB}")
    
    def _insert_metadata(self):
        """Insert migration metadata."""
        metadata = [
            ('embedding_model', EMBEDDING_MODEL),
            ('embedding_dim', str(EMBEDDING_DIM)),
            ('migrated_from', SOURCE_DB),
            ('migration_date', datetime.now().isoformat()),
            ('migration_duration_minutes', str((time.time() - self.start_time) / 60 if self.start_time else 0)),
            ('total_blocks_migrated', str(self.migrated_blocks)),
            ('total_tokens', str(self.total_tokens)),
            ('estimated_cost_usd', str(self._estimate_cost()))
        ]
        
        for key, value in metadata:
            self.target_conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )
        
        self.target_conn.commit()
        LOG.info("Migration metadata inserted")
    
    def _get_all_blocks_from_source(self) -> List[Dict]:
        """Fetch all blocks from source database."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT 
                b.id, b.resource_id, b.block_type, b.content, 
                b.start_line, b.end_line, b.token_count, b.content_date,
                r.path
            FROM blocks b
            JOIN resources r ON b.resource_id = r.id
            ORDER BY r.path, b.start_line
        """)
        
        blocks = []
        for row in cursor.fetchall():
            blocks.append({
                'id': row[0],
                'resource_id': row[1],
                'block_type': row[2],
                'content': row[3],
                'start_line': row[4],
                'end_line': row[5],
                'token_count': row[6],
                'content_date': row[7],
                'resource_path': row[8]
            })
        
        self.total_blocks = len(blocks)
        LOG.info(f"Found {self.total_blocks} blocks in source database")
        return blocks
    
    def _migrate_resources(self, resource_ids: set):
        """Migrate unique resources from source to target."""
        cursor = self.source_conn.cursor()
        cursor.execute("""
            SELECT id, path, hash, last_indexed_at, content_date
            FROM resources
            WHERE id IN ({})
        """.format(','.join(['?'] * len(resource_ids))), list(resource_ids))
        
        migrated = 0
        for row in cursor.fetchall():
            self.target_conn.execute("""
                INSERT OR REPLACE INTO resources (id, path, hash, last_indexed_at, content_date)
                VALUES (?, ?, ?, ?, ?)
            """, row)
            migrated += 1
        
        self.target_conn.commit()
        LOG.info(f"Migrated {migrated} resources")
    
    def _get_embedding_with_retry(self, text: str, retry_count: int = 0) -> Optional[List[float]]:
        """Get embedding from OpenAI with rate limiting and retry logic."""
        # Rate limiting
        now = time.time()
        elapsed = now - self.last_rate_limit_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self.last_rate_limit_time = time.time()
        
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            if retry_count < MAX_RETRIES:
                # Exponential backoff
                backoff = BASE_BACKOFF * (2 ** retry_count)
                LOG.warning(f"Error getting embedding (attempt {retry_count + 1}/{MAX_RETRIES}): {e}. Retrying in {backoff}s...")
                time.sleep(backoff)
                return self._get_embedding_with_retry(text, retry_count + 1)
            else:
                LOG.error(f"Failed to get embedding after {MAX_RETRIES} retries: {e}")
                return None
    
    def migrate(self):
        """Main migration process."""
        LOG.info("=" * 60)
        LOG.info("Starting embedding migration")
        LOG.info(f"Source: {SOURCE_DB}")
        LOG.info(f"Target: {TARGET_DB}")
        LOG.info(f"Model: {EMBEDDING_MODEL} ({EMBEDDING_DIM}-dim)")
        LOG.info("=" * 60)
        
        self.start_time = time.time()
        self.checkpoint['start_time'] = datetime.now().isoformat()
        
        # Initialize target DB
        self._init_target_db()
        
        # Get all blocks from source
        blocks = self._get_all_blocks_from_source()
        
        # Check if we're resuming
        if self.checkpoint['migrated_blocks']:
            LOG.info(f"Resuming from checkpoint: {len(self.checkpoint['migrated_blocks'])} blocks already migrated")
            start_index = self.checkpoint['last_block_index'] + 1
        else:
            start_index = 0
        
        # Track migrated resources
        migrated_resource_ids = set()
        
        # Process blocks
        for i in range(start_index, len(blocks)):
            block = blocks[i]
            block_id = block['id']
            
            # Skip if already migrated
            if block_id in self.checkpoint['migrated_blocks']:
                self.skipped_blocks += 1
                continue
            
            # Get new embedding
            content = block['content']
            embedding = self._get_embedding_with_retry(content)
            
            if embedding is None:
                LOG.error(f"Failed to embed block {block_id}, skipping")
                continue
            
            # Verify dimension
            if len(embedding) != EMBEDDING_DIM:
                LOG.error(f"Embedding dimension mismatch for block {block_id}: expected {EMBEDDING_DIM}, got {len(embedding)}")
                continue
            
            # Estimate tokens (approximate: 4 chars = 1 token)
            token_count = len(content) // 4
            self.total_tokens += token_count
            
            # Insert block
            self.target_conn.execute("""
                INSERT OR REPLACE INTO blocks (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                block['id'], block['resource_id'], block['block_type'],
                block['content'], block['start_line'], block['end_line'],
                token_count, block['content_date']
            ))
            
            # Insert vector
            embedding_blob = float_array_to_blob(embedding)
            self.target_conn.execute("""
                INSERT OR REPLACE INTO vectors (block_id, embedding, embedding_dim)
                VALUES (?, ?, ?)
            """, (block['id'], embedding_blob, EMBEDDING_DIM))
            
            # Track resource for migration
            migrated_resource_ids.add(block['resource_id'])
            
            # Update checkpoint tracking
            self.checkpoint['migrated_blocks'].append(block_id)
            self.checkpoint['last_block_index'] = i
            self.migrated_blocks += 1
            
            # Progress logging and checkpointing
            if self.migrated_blocks % 100 == 0:
                elapsed = time.time() - self.start_time
                rate = self.migrated_blocks / elapsed if elapsed > 0 else 0
                eta_minutes = ((self.total_blocks - self.migrated_blocks) / rate / 60) if rate > 0 else 0
                cost = self._estimate_cost()
                
                LOG.info(f"Progress: {self.migrated_blocks}/{self.total_blocks} ({self.migrated_blocks/self.total_blocks*100:.1f}%) | "
                         f"Rate: {rate:.1f} blocks/sec | ETA: {eta_minutes:.1f} min | Cost: ${cost:.2f}")
            
            # Checkpoint
            if self.migrated_blocks % CHECKPOINT_INTERVAL == 0:
                self._save_checkpoint()
                self.target_conn.commit()
        
        # Migrate resources (unique set)
        self._migrate_resources(migrated_resource_ids)
        
        # Final commit
        self.target_conn.commit()
        
        # Insert metadata
        self._insert_metadata()
        
        # Final checkpoint
        self._save_checkpoint()
        
        # Print summary
        elapsed_seconds = time.time() - self.start_time
        elapsed_minutes = elapsed_seconds / 60
        
        LOG.info("=" * 60)
        LOG.info("Migration Complete!")
        LOG.info(f"Total blocks: {self.total_blocks}")
        LOG.info(f"Migrated: {self.migrated_blocks}")
        LOG.info(f"Skipped (checkpoint): {self.skipped_blocks}")
        LOG.info(f"Total tokens: {self.total_tokens}")
        LOG.info(f"Estimated cost: ${self._estimate_cost():.2f}")
        LOG.info(f"Duration: {elapsed_minutes:.1f} minutes ({elapsed_seconds:.1f} seconds)")
        LOG.info(f"Average rate: {self.migrated_blocks/elapsed_seconds:.2f} blocks/second")
        LOG.info(f"Target database: {TARGET_DB}")
        LOG.info("=" * 60)


def float_array_to_blob(array: List[float]) -> bytes:
    """Convert float array to binary blob for SQLite storage."""
    import numpy as np
    return np.array(array, dtype=np.float32).tobytes()


def validate_migration():
    """Validate the migration results."""
    LOG.info("\nValidating migration...")
    
    # Check database exists
    if not os.path.exists(TARGET_DB):
        LOG.error("Target database does not exist!")
        return False
    
    # Connect to both databases
    source_conn = sqlite3.connect(SOURCE_DB)
    target_conn = sqlite3.connect(TARGET_DB)
    
    # Compare counts
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()
    
    # Resource count
    source_cursor.execute("SELECT COUNT(*) FROM resources")
    target_cursor.execute("SELECT COUNT(*) FROM resources")
    source_resources = source_cursor.fetchone()[0]
    target_resources = target_cursor.fetchone()[0]
    
    LOG.info(f"Resources: Source={source_resources}, Target={target_resources}")
    
    # Block count
    source_cursor.execute("SELECT COUNT(*) FROM blocks")
    target_cursor.execute("SELECT COUNT(*) FROM blocks")
    source_blocks = source_cursor.fetchone()[0]
    target_blocks = target_cursor.fetchone()[0]
    
    LOG.info(f"Blocks: Source={source_blocks}, Target={target_blocks}")
    
    # Vector count
    target_cursor.execute("SELECT COUNT(*) FROM vectors")
    target_vectors = target_cursor.fetchone()[0]
    
    LOG.info(f"Vectors: Target={target_vectors}")
    
    # Check embedding dimensions
    target_cursor.execute("SELECT embedding_dim, COUNT(*) FROM vectors GROUP BY embedding_dim")
    dim_results = target_cursor.fetchall()
    
    all_3072 = all(dim == EMBEDDING_DIM for dim, _ in dim_results)
    LOG.info(f"Vector dimensions: {dim_results}")
    LOG.info(f"All vectors 3072-dim: {all_3072}")
    
    # Check metadata
    target_cursor.execute("SELECT * FROM metadata")
    metadata = dict(target_cursor.fetchall())
    LOG.info(f"Metadata: {metadata}")
    
    # Sample search test
    LOG.info("\nRunning sample search test...")
    target_cursor.execute("""
        SELECT b.content, v.embedding
        FROM blocks b
        JOIN vectors v ON b.id = v.block_id
        LIMIT 10
    """)
    samples = target_cursor.fetchall()
    LOG.info(f"Sample search: Found {len(samples)} blocks with vectors")
    
    # Overall validation
    validation_pass = (
        target_resources == source_resources and
        target_blocks == source_blocks and
        target_vectors == target_blocks and
        all_3072 and
        len(metadata) > 0
    )
    
    if validation_pass:
        LOG.info("✓ Validation PASSED")
    else:
        LOG.error("✗ Validation FAILED")
    
    return validation_pass


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate embeddings from brain.db to brain_v2.db")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing migration")
    args = parser.parse_args()
    
    if args.validate_only:
        # Just validate
        success = validate_migration()
        sys.exit(0 if success else 1)
    
    # Run migration
    migrator = EmbeddingMigrator()
    migrator.migrate()
    
    # Validate
    success = validate_migration()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
