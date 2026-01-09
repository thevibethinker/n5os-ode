import sqlite3
import os
import datetime
import json
import logging
import hashlib
import re
import time
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
import sys

# Add N5 lib to path for imports
sys.path.insert(0, '/home/workspace')
from N5.lib.paths import BRAIN_DB, BRAIN_HNSW_INDEX

# Try importing OpenAI, handle failure gracefully
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Try importing sentence_transformers for local fallback
try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False

# BM25 for hybrid search
try:
    from rank_bm25 import BM25Okapi
    HAS_BM25 = True
except ImportError:
    HAS_BM25 = False

# Cross-encoder for reranking
try:
    from sentence_transformers import CrossEncoder
    HAS_CROSS_ENCODER = True
except ImportError:
    HAS_CROSS_ENCODER = False

# ANN Index support (HNSW)
try:
    import hnswlib
    HAS_HNSWLIB = True
except ImportError:
    HAS_HNSWLIB = False

ANN_INDEX_PATH = str(BRAIN_HNSW_INDEX)

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("n5_memory_client")


class N5MemoryClient:
    def __init__(self, db_path: str = str(BRAIN_DB)):
        self.db_path = db_path
        self._conn = None
        self.provider = os.getenv("N5_EMBEDDING_PROVIDER", "local") # 'local' or 'openai'
        self.openai_model = os.getenv("N5_OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
        self.local_model_name = "all-MiniLM-L6-v2"
        
        # Named semantic retrieval profiles (thin config in code; can be externalized later)
        # Paths are absolute and match canonical domains referenced in persona/routing docs.
        self.profiles = {
            "system-architecture": {
                "path_prefixes": [
                    "/home/workspace/Documents/System/",
                    "/home/workspace/N5/docs/",
                    "/home/workspace/Knowledge/architectural/",
                ]
            },
            "content-library": {
                "path_prefixes": [
                    "/home/workspace/Knowledge/content-library/",
                ]
            },
            "meetings": {
                "path_prefixes": [
                    "/home/workspace/Personal/Meetings/",
                    "/home/workspace/N5/digests/",
                ]
            },
            "crm": {
                "path_prefixes": [
                    "/home/workspace/Personal/Knowledge/CRM/individuals/",  # Canonical profiles
                    "/home/workspace/Personal/Knowledge/CRM/",              # CRM root (orgs, views)
                ]
            },
            "voice-guides": {
                "path_prefixes": [
                    "/home/workspace/N5/prefs/communication/",
                ]
            },
            "wellness": {
                "path_prefixes": [
                    "/home/workspace/Personal/Health/",
                    "/home/workspace/Personal/Health/WorkoutTracker/",
                    "/home/workspace/Personal/Health/protocols/",
                    "/home/workspace/Personal/Health/stack/",
                ]
            },
            "capabilities": {
                "path_prefixes": [
                    "/home/workspace/N5/capabilities/",
                    "/home/workspace/Prompts/",
                ]
            },
        }
        
        self.openai_client = None
        self.local_model = None
        self.cross_encoder = None
        
        # Rate limiting for OpenAI
        self._last_embedding_time = 0
        self._min_embedding_interval = 0.1  # 100ms between calls (10/sec max)
        
        # ANN Index state
        self.use_vector_index = os.getenv("USE_VECTOR_INDEX", "true").lower() == "true"
        self.ann_index = None
        self.ann_block_ids = []  # Ordered list mapping index position → block_id
        
        self._init_provider()
        self._init_db()
        self._init_reranker()
        
        # Load ANN index after DB is initialized
        if self.use_vector_index:
            self._load_ann_index()

    def _init_provider(self):
        # Check for API Key in secret file if not in Env
        key_path = "/home/workspace/N5/config/secrets/openai.key"
        if not os.getenv("OPENAI_API_KEY") and os.path.exists(key_path):
            with open(key_path, 'r') as f:
                os.environ["OPENAI_API_KEY"] = f.read().strip()
                self.provider = "openai" # Force switch if key found
        
        if self.provider == "openai":
            if not HAS_OPENAI:
                LOG.error("OpenAI provider requested but 'openai' package not installed.")
                self.provider = "local"
            elif not os.getenv("OPENAI_API_KEY"):
                LOG.error("OpenAI provider requested but OPENAI_API_KEY not set.")
                self.provider = "local"
            else:
                self.openai_client = OpenAI()
                LOG.info(f"Using OpenAI Embeddings: {self.openai_model}")
                return

        if self.provider == "local":
            if not HAS_SBERT:
                raise ImportError("sentence-transformers not installed for local embeddings.")
            self.local_model = SentenceTransformer(self.local_model_name)
            LOG.info(f"Using Local Embeddings: {self.local_model_name}")

    def _init_db(self):
        self._conn = sqlite3.connect(self.db_path)
        # Ensure schema exists (idempotent)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                hash TEXT,
                last_indexed_at DATETIME,
                content_date DATETIME
            )
        """)
        self._conn.execute("""
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
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                block_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                FOREIGN KEY(block_id) REFERENCES blocks(id) ON DELETE CASCADE
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                resource_id TEXT, 
                tag TEXT, 
                PRIMARY KEY (resource_id, tag), 
                FOREIGN KEY(resource_id) REFERENCES resources(id) ON DELETE CASCADE
            )
        """)
        self._conn.commit()

    def _init_reranker(self):
        """Initialize cross-encoder for reranking if available."""
        if HAS_CROSS_ENCODER:
            try:
                self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                LOG.info("Reranker initialized: cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                LOG.warning(f"Could not load cross-encoder: {e}")
                self.cross_encoder = None

    def _load_ann_index(self, check_freshness: bool = True) -> bool:
        """Load the pre-built HNSW index if available.

        Args:
            check_freshness: If True, check index freshness and log warnings
        """
        if not HAS_HNSWLIB:
            LOG.warning("hnswlib not installed, falling back to brute-force")
            return False

        index_path = ANN_INDEX_PATH
        mapping_path = ANN_INDEX_PATH + ".ids"

        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            LOG.info("ANN index not found, will use brute-force search")
            return False

        try:
            # Load block_id mapping
            with open(mapping_path, 'r') as f:
                self.ann_block_ids = json.load(f)

            # Detect dimension from first vector in DB
            cursor = self._get_db().cursor()
            cursor.execute("SELECT embedding FROM vectors LIMIT 1")
            row = cursor.fetchone()
            if not row:
                return False
            dim = len(np.frombuffer(row[0], dtype=np.float32))

            # Load index
            self.ann_index = hnswlib.Index(space='cosine', dim=dim)
            self.ann_index.load_index(index_path)
            self.ann_index.set_ef(100)  # Search accuracy parameter
            LOG.info(f"ANN index loaded: {len(self.ann_block_ids)} vectors, dim={dim}")

            # Check freshness if requested
            if check_freshness:
                freshness = self.check_index_freshness()
                if freshness and freshness.get('needs_rebuild'):
                    LOG.warning(f"ANN index is stale: {freshness.get('drift_pct', 0):.1f}% drift "
                               f"({freshness.get('missing_count', 0)} missing, "
                               f"{freshness.get('orphan_count', 0)} orphan)")

            return True
        except Exception as e:
            LOG.warning(f"Failed to load ANN index: {e}")
            self.ann_index = None
            self.ann_block_ids = []
            return False

    def check_index_freshness(self) -> Optional[Dict[str, Any]]:
        """Check if ANN index is fresh compared to database.

        Returns:
            Dict with freshness metrics:
            - index_count: Number of vectors in index
            - db_count: Number of vectors in database
            - missing_count: Vectors in DB but not in index
            - orphan_count: Vectors in index but not in DB
            - drift_pct: Percentage of vectors that are mismatched
            - index_mtime: When index file was last modified
            - latest_indexed: Latest last_indexed_at from resources
            - needs_rebuild: True if drift exceeds threshold (5%)
            - stale_reason: Human-readable reason if stale
        """
        if not self.ann_block_ids:
            return None

        index_path = ANN_INDEX_PATH
        if not os.path.exists(index_path):
            return None

        try:
            cursor = self._get_db().cursor()

            # Get DB vector count and block_ids
            cursor.execute("SELECT block_id FROM vectors")
            db_block_ids = set(row[0] for row in cursor.fetchall())

            # Get latest indexed timestamp
            cursor.execute("SELECT MAX(last_indexed_at) FROM resources")
            row = cursor.fetchone()
            latest_indexed = row[0] if row else None

            # Compare with index
            index_block_ids = set(self.ann_block_ids)
            missing = db_block_ids - index_block_ids  # In DB but not in index
            orphans = index_block_ids - db_block_ids  # In index but not in DB

            index_count = len(index_block_ids)
            db_count = len(db_block_ids)
            total = max(index_count, db_count, 1)
            drift_pct = (len(missing) + len(orphans)) / total * 100

            # Get index file mtime
            index_mtime = os.path.getmtime(index_path)
            from datetime import datetime
            index_mtime_str = datetime.fromtimestamp(index_mtime).isoformat()

            # Determine if rebuild is needed (>5% drift threshold)
            needs_rebuild = drift_pct > 5.0
            stale_reason = None
            if needs_rebuild:
                reasons = []
                if missing:
                    reasons.append(f"{len(missing)} new vectors not in index")
                if orphans:
                    reasons.append(f"{len(orphans)} deleted vectors still in index")
                stale_reason = "; ".join(reasons)

            return {
                'index_count': index_count,
                'db_count': db_count,
                'missing_count': len(missing),
                'orphan_count': len(orphans),
                'drift_pct': drift_pct,
                'index_mtime': index_mtime_str,
                'latest_indexed': latest_indexed,
                'needs_rebuild': needs_rebuild,
                'stale_reason': stale_reason
            }
        except Exception as e:
            LOG.warning(f"Failed to check index freshness: {e}")
            return None

    def ensure_index_fresh(self, drift_threshold: float = 5.0, auto_rebuild: bool = True) -> Dict[str, Any]:
        """Ensure ANN index is fresh, optionally rebuilding if stale.

        Args:
            drift_threshold: Percentage drift that triggers rebuild (default: 5%)
            auto_rebuild: If True, automatically rebuild when stale

        Returns:
            Dict with:
            - fresh: True if index is fresh (or was rebuilt)
            - rebuilt: True if index was rebuilt
            - freshness: Freshness check results
        """
        result = {
            'fresh': True,
            'rebuilt': False,
            'freshness': None
        }

        # Check freshness
        freshness = self.check_index_freshness()
        result['freshness'] = freshness

        if freshness is None:
            # No index exists
            if auto_rebuild:
                LOG.info("No ANN index found, building...")
                if self.rebuild_ann_index():
                    result['rebuilt'] = True
                    result['freshness'] = self.check_index_freshness()
                else:
                    result['fresh'] = False
            else:
                result['fresh'] = False
            return result

        # Check if stale
        if freshness.get('drift_pct', 0) > drift_threshold:
            result['fresh'] = False
            if auto_rebuild:
                LOG.info(f"ANN index stale ({freshness['drift_pct']:.1f}% drift), rebuilding...")
                if self.rebuild_ann_index():
                    result['rebuilt'] = True
                    result['fresh'] = True
                    result['freshness'] = self.check_index_freshness()

        return result

    def _search_ann(self, query_vec: np.ndarray, k: int = 100) -> List[Tuple[str, float]]:
        """Search ANN index, return list of (block_id, similarity)."""
        if self.ann_index is None or not self.ann_block_ids:
            return []
        
        try:
            # hnswlib returns (labels, distances) where labels are indices
            labels, distances = self.ann_index.knn_query(query_vec.reshape(1, -1), k=min(k, len(self.ann_block_ids)))
            
            results = []
            for idx, dist in zip(labels[0], distances[0]):
                if idx < len(self.ann_block_ids):
                    block_id = self.ann_block_ids[idx]
                    # Convert cosine distance to similarity: sim = 1 - dist
                    similarity = 1.0 - dist
                    results.append((block_id, similarity))
            return results
        except Exception as e:
            LOG.warning(f"ANN search failed: {e}")
            return []

    def rebuild_ann_index(self, ef_construction: int = 200, M: int = 16) -> bool:
        """Rebuild the HNSW index from all vectors in database."""
        if not HAS_HNSWLIB:
            LOG.error("hnswlib not installed")
            return False
        
        cursor = self._get_db().cursor()
        cursor.execute("SELECT block_id, embedding FROM vectors")
        rows = cursor.fetchall()
        
        if not rows:
            LOG.warning("No vectors to index")
            return False
        
        # Detect dimension
        dim = len(np.frombuffer(rows[0][1], dtype=np.float32))
        
        # Build index
        index = hnswlib.Index(space='cosine', dim=dim)
        index.init_index(max_elements=len(rows), ef_construction=ef_construction, M=M)
        
        block_ids = []
        vectors = []
        for block_id, emb_blob in rows:
            block_ids.append(block_id)
            vectors.append(np.frombuffer(emb_blob, dtype=np.float32))
        
        vectors_array = np.array(vectors, dtype=np.float32)
        index.add_items(vectors_array, list(range(len(block_ids))))
        
        # Save index and mapping
        index.save_index(ANN_INDEX_PATH)
        with open(ANN_INDEX_PATH + ".ids", 'w') as f:
            json.dump(block_ids, f)
        
        LOG.info(f"ANN index rebuilt: {len(block_ids)} vectors, dim={dim}")
        
        # Reload into memory
        self._load_ann_index()
        return True

    def _get_db(self) -> sqlite3.Connection:
        """Return the database connection (for direct access when needed)."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn

    def get_embedding(self, text: str) -> bytes:
        text = text.replace("\n", " ")
        if self.provider == "openai":
            # Rate limiting
            elapsed = time.time() - self._last_embedding_time
            if elapsed < self._min_embedding_interval:
                time.sleep(self._min_embedding_interval - elapsed)
            
            try:
                response = self.openai_client.embeddings.create(
                    input=[text],
                    model=self.openai_model
                )
                self._last_embedding_time = time.time()
                vec = response.data[0].embedding
                return np.array(vec, dtype=np.float32).tobytes()
            except Exception as e:
                LOG.error(f"OpenAI Embedding Error: {e}")
                # Back off on rate limit errors
                if "rate" in str(e).lower():
                    time.sleep(5)
                raise e
        else:
            vec = self.local_model.encode(text)
            return np.array(vec, dtype=np.float32).tobytes()

    def extract_content_date(self, file_path: str) -> Optional[str]:
        """Extract content_date from YAML frontmatter or filename date patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000)  # Read first 2KB for frontmatter
            
            # Check for YAML frontmatter
            if content.startswith('---'):
                end_idx = content.find('---', 3)
                if end_idx > 3:
                    frontmatter = content[3:end_idx]
                    # Look for created: or date: field
                    for line in frontmatter.splitlines():
                        if line.strip().startswith(('created:', 'date:')):
                            date_val = line.split(':', 1)[1].strip()
                            # Validate ISO date format
                            if re.match(r'\d{4}-\d{2}-\d{2}', date_val):
                                return date_val[:10]  # Return YYYY-MM-DD
            
            # Fallback: extract from filename (e.g., 2025-10-15_meeting-name.md)
            basename = os.path.basename(file_path)
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', basename)
            if date_match:
                return date_match.group(1)
                
        except Exception as e:
            LOG.debug(f"Could not extract date from {file_path}: {e}")
        return None

    def store_resource(self, path: str, file_hash: str, content_date: Optional[str] = None) -> str:
        """Store or update a resource entry, returning its ID."""
        resource_id = hashlib.md5(path.encode('utf-8')).hexdigest()
        cursor = self._get_db().cursor()
        cursor.execute("""
            INSERT INTO resources (id, path, hash, last_indexed_at, content_date)
            VALUES (?, ?, ?, datetime('now'), ?)
            ON CONFLICT(id) DO UPDATE SET
                hash=excluded.hash,
                last_indexed_at=excluded.last_indexed_at,
                content_date=coalesce(excluded.content_date, content_date)
        """, (resource_id, path, file_hash, content_date))
        self._get_db().commit()
        return resource_id

    def delete_resource_blocks(self, resource_id: str) -> None:
        """Delete all blocks (and their vectors via CASCADE) for a resource."""
        cursor = self._get_db().cursor()
        # Delete vectors first (if no CASCADE)
        cursor.execute("DELETE FROM vectors WHERE block_id IN (SELECT id FROM blocks WHERE resource_id = ?)", (resource_id,))
        cursor.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
        self._get_db().commit()

    def add_block(self, resource_id: str, content: str, block_type: str = "paragraph",
                  start_line: int = 0, end_line: int = 0, content_date: Optional[str] = None) -> str:
        """Add a block with its embedding vector."""
        # Generate unique block ID
        block_hash = hashlib.md5(f"{resource_id}:{start_line}:{content[:50]}".encode()).hexdigest()
        block_id = f"{resource_id}_{block_hash[:8]}"
        
        # Get embedding
        embedding_blob = self.get_embedding(content)
        
        cursor = self._get_db().cursor()
        cursor.execute("""
            INSERT INTO blocks (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (block_id, resource_id, block_type, content, start_line, end_line, len(content)//4, content_date))
        
        cursor.execute("""
            INSERT INTO vectors (block_id, embedding)
            VALUES (?, ?)
        """, (block_id, embedding_blob))
        
        self._get_db().commit()
        return block_id

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer for BM25 - lowercase and split on non-alphanumeric."""
        return re.findall(r'\w+', text.lower())

    def _compute_bm25_scores(self, query: str, documents: List[Dict]) -> Dict[str, float]:
        """Compute BM25 scores for documents given a query."""
        if not HAS_BM25 or not documents:
            return {}
        
        # Tokenize all documents
        tokenized_docs = [self._tokenize(doc['content']) for doc in documents]
        tokenized_query = self._tokenize(query)
        
        if not tokenized_query:
            return {}
        
        bm25 = BM25Okapi(tokenized_docs)
        scores = bm25.get_scores(tokenized_query)
        
        # Normalize BM25 scores to [0, 1] range
        max_score = max(scores) if max(scores) > 0 else 1
        return {doc['block_id']: score / max_score for doc, score in zip(documents, scores)}

    def search(self, query: str, limit: int = 10, tag_filter: Optional[str] = None,
               recency_weight: float = 0.2, use_hybrid: bool = True,
               semantic_weight: float = 0.7, bm25_weight: float = 0.3,
               use_reranker: bool = False, rerank_top_k: int = 50,
               metadata_filters: Optional[Dict[str, Any]] = None,
               _query_embedding: Optional[bytes] = None) -> List[Dict]:
        """
        Semantic search with optional hybrid BM25 and reranking.

        Args:
            query: Search query string
            limit: Number of results to return
            tag_filter: Filter by tag (legacy support)
            recency_weight: Weight for recency boosting (0-1)
            use_hybrid: Enable BM25 + semantic hybrid search
            semantic_weight: Weight for semantic similarity in hybrid mode
            bm25_weight: Weight for BM25 scores in hybrid mode
            use_reranker: Enable cross-encoder reranking
            rerank_top_k: Number of candidates to rerank
            metadata_filters: Dict of metadata filters {field: value or (op, value)}
                Supported fields: path, block_type, content_date
                Operators: eq, ne, gt, lt, gte, lte, contains, startswith
            _query_embedding: Pre-computed query embedding (internal use for batching)
        """
        # Use pre-computed embedding if provided, otherwise compute
        query_embedding = _query_embedding if _query_embedding is not None else self.get_embedding(query)
        query_vec = np.frombuffer(query_embedding, dtype=np.float32)
        
        cursor = self._get_db().cursor()
        raw_results = []
        
        # === ANN INDEX FAST PATH ===
        # Use HNSW index if available and enabled, with no tag filter (tag filter requires brute-force join)
        if self.use_vector_index and self.ann_index is not None and not tag_filter:
            ann_k = max(limit * 5, rerank_top_k * 2) if use_reranker else limit * 3
            ann_results = self._search_ann(query_vec, k=ann_k)
            
            if ann_results:
                block_ids = [r[0] for r in ann_results]
                sim_map = {r[0]: r[1] for r in ann_results}
                
                placeholders = ','.join('?' * len(block_ids))
                cursor.execute(f"""
                    SELECT b.id, b.content, b.block_type, r.path, b.content_date, b.start_line, b.end_line
                    FROM blocks b
                    JOIN resources r ON b.resource_id = r.id
                    WHERE b.id IN ({placeholders})
                """, block_ids)
                
                for row in cursor.fetchall():
                    block_id, content, block_type, path, content_date, start_line, end_line = row
                    
                    # Apply metadata filters in Python (post-filter)
                    if metadata_filters:
                        skip = False
                        for field, value in metadata_filters.items():
                            if field == 'path':
                                if isinstance(value, tuple) and len(value) == 2:
                                    op, val = value
                                    if op == 'startswith' and not path.startswith(val):
                                        skip = True
                                    elif op == 'contains' and val not in path:
                                        skip = True
                                elif path != value:
                                    skip = True
                            elif field == 'block_type':
                                if block_type != value:
                                    skip = True
                            elif field == 'content_date':
                                if isinstance(value, tuple) and len(value) == 2:
                                    op, val = value
                                    if op == 'gt' and not (content_date and content_date > val):
                                        skip = True
                                    elif op == 'lt' and not (content_date and content_date < val):
                                        skip = True
                                elif content_date != value:
                                    skip = True
                        if skip:
                            continue
                    
                    raw_results.append({
                        'block_id': block_id,
                        'content': content,
                        'block_type': block_type,
                        'path': path,
                        'content_date': content_date,
                        'start_line': int(start_line or 0),
                        'end_line': int(end_line or 0),
                        'lines': [int(start_line or 0), int(end_line or 0)],
                        'similarity': sim_map.get(block_id, 0.0)
                    })
        
        # === BRUTE-FORCE FALLBACK ===
        # Use when ANN index not available, disabled, or tag_filter specified
        if not raw_results:
            sql_parts = ["""
                SELECT b.id, b.content, b.block_type, r.path, b.content_date, b.start_line, b.end_line, v.embedding
                FROM blocks b
                JOIN resources r ON b.resource_id = r.id
                JOIN vectors v ON b.id = v.block_id
            """]
            
            conditions = []
            params = []
            
            # Tag filter (legacy)
            if tag_filter:
                sql_parts[0] = sql_parts[0].replace("JOIN vectors", "JOIN tags t ON r.id = t.resource_id\nJOIN vectors")
                conditions.append("t.tag = ?")
                params.append(tag_filter)
            
            # Metadata filters
            if metadata_filters:
                for field, value in metadata_filters.items():
                    col_map = {
                        'path': 'r.path',
                        'block_type': 'b.block_type', 
                        'content_date': 'b.content_date'
                    }
                    if field not in col_map:
                        continue
                    col = col_map[field]
                    
                    if isinstance(value, tuple) and len(value) == 2:
                        op, val = value
                        op_map = {
                            'eq': '=', 'ne': '!=', 'gt': '>', 'lt': '<',
                            'gte': '>=', 'lte': '<=',
                            'contains': 'LIKE', 'startswith': 'LIKE'
                        }
                        if op in op_map:
                            if op == 'contains':
                                val = f'%{val}%'
                            elif op == 'startswith':
                                val = f'{val}%'
                            conditions.append(f"{col} {op_map[op]} ?")
                            params.append(val)
                    else:
                        conditions.append(f"{col} = ?")
                        params.append(value)
            
            if conditions:
                sql_parts.append("WHERE " + " AND ".join(conditions))
            
            cursor.execute(" ".join(sql_parts), params)
            
            for row in cursor.fetchall():
                block_id, content, block_type, path, content_date, start_line, end_line, emb_blob = row
                stored_vec = np.frombuffer(emb_blob, dtype=np.float32)
                
                # Cosine similarity
                similarity = np.dot(query_vec, stored_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(stored_vec) + 1e-9)
                
                raw_results.append({
                    'block_id': block_id,
                    'content': content,
                    'block_type': block_type,
                    'path': path,
                    'content_date': content_date,
                    'start_line': int(start_line or 0),
                    'end_line': int(end_line or 0),
                    'lines': [int(start_line or 0), int(end_line or 0)],
                    'similarity': float(similarity)
                })
        
        # Compute BM25 scores for hybrid search - OPTIMIZED: only for top-K candidates
        # Computing BM25 for all results is O(n) tokenization; limit to top semantic matches
        bm25_scores = {}
        if use_hybrid and HAS_BM25 and raw_results:
            # Sort by semantic similarity first, take top candidates for BM25
            bm25_candidate_count = max(limit * 3, rerank_top_k) if use_reranker else limit * 3
            sorted_by_similarity = sorted(raw_results, key=lambda x: x['similarity'], reverse=True)
            bm25_candidates = sorted_by_similarity[:bm25_candidate_count]
            bm25_scores = self._compute_bm25_scores(query, bm25_candidates)

        # Combine scores
        results = []
        for r in raw_results:
            semantic_score = r['similarity']
            bm25_score = bm25_scores.get(r['block_id'], 0.0) if use_hybrid else 0.0
            
            if use_hybrid:
                combined = semantic_weight * semantic_score + bm25_weight * bm25_score
            else:
                combined = semantic_score
            
            # Apply recency boost
            recency_score = 0.0
            if r['content_date'] and recency_weight > 0:
                try:
                    date_obj = datetime.datetime.fromisoformat(r['content_date'][:10])
                    days_old = (datetime.datetime.now() - date_obj).days
                    recency_score = max(0, 1 - (days_old / 365)) * recency_weight
                except:
                    pass
            
            final_score = combined + recency_score
            results.append({
                **r,
                'bm25_score': bm25_score,
                'score': float(final_score)
            })
        
        # Sort by combined score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Reranking with cross-encoder
        if use_reranker and self.cross_encoder and results:
            top_candidates = results[:rerank_top_k]
            pairs = [(query, r['content']) for r in top_candidates]
            
            try:
                rerank_scores = self.cross_encoder.predict(pairs)
                for i, score in enumerate(rerank_scores):
                    top_candidates[i]['rerank_score'] = float(score)
                    top_candidates[i]['score'] = float(score)  # Replace with rerank score
                
                top_candidates.sort(key=lambda x: x['score'], reverse=True)
                results = top_candidates + results[rerank_top_k:]
            except Exception as e:
                LOG.warning(f"Reranking failed: {e}")
        
        return results[:limit]

    def search_profile(self, profile: str, query: str, limit: int = 10, **kwargs) -> List[Dict]:
        """Search using a named retrieval profile.

        Profiles are thin semantic filters over paths/tags that group related
        domains (e.g., system-architecture, meetings, crm, content-library).

        This is a convenience wrapper over `search` that applies path-prefix
        filters and merges results across prefixes, preserving scoring.

        OPTIMIZATION: Computes query embedding once and reuses across all
        path prefix searches, avoiding redundant embedding API calls.
        """
        profile_def = self.profiles.get(profile)
        if not profile_def:
            raise ValueError(f"Unknown profile: {profile}")

        path_prefixes: List[str] = profile_def.get("path_prefixes", [])
        if not path_prefixes:
            # Fall back to generic search if misconfigured
            return self.search(query, limit=limit, **kwargs)

        # OPTIMIZATION: Compute embedding once for all prefix searches
        query_embedding = self.get_embedding(query)

        all_results: List[Dict[str, Any]] = []
        seen: set[str] = set()

        for prefix in path_prefixes:
            mf = dict(kwargs.get("metadata_filters") or {})
            # Path filter uses startswith operator to scope results
            mf["path"] = ("startswith", prefix)
            prefix_results = self.search(
                query=query,
                limit=limit,
                metadata_filters=mf,
                _query_embedding=query_embedding,  # Reuse pre-computed embedding
                **{k: v for k, v in kwargs.items() if k != "metadata_filters"}
            )
            for r in prefix_results:
                bid = r.get("block_id")
                if bid and bid not in seen:
                    seen.add(bid)
                    all_results.append(r)

        # Global sort by score and trim
        all_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return all_results[:limit]

    def index_file(self, file_path: str, content: str, content_date: Optional[str] = None):
        """Full re-index of a file: update resource, delete old blocks, insert new blocks."""
        # 1. Update Resource
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        resource_id = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        
        cursor = self._conn.cursor()
        
        # First delete any existing resource with this path (handles both id and path uniqueness)
        cursor.execute("DELETE FROM resources WHERE path = ? OR id = ?", (file_path, resource_id))
        
        # Then insert fresh
        cursor.execute("""
            INSERT INTO resources (id, path, hash, last_indexed_at, content_date)
            VALUES (?, ?, ?, datetime('now'), ?)
        """, (resource_id, file_path, file_hash, content_date))
        
        # 2. Clear old blocks AND vectors explicitly (CASCADE may not work)
        cursor.execute("DELETE FROM vectors WHERE block_id IN (SELECT id FROM blocks WHERE resource_id = ?)", (resource_id,))
        cursor.execute("DELETE FROM blocks WHERE resource_id = ?", (resource_id,))
        
        # 3. Chunk & Embed
        chunks = self._chunk_content(content)
        
        for i, chunk in enumerate(chunks):
            block_id = f"{resource_id}_{i}"
            # Delete any orphan vectors with this block_id
            cursor.execute("DELETE FROM vectors WHERE block_id = ?", (block_id,))
            embedding_blob = self.get_embedding(chunk['text'])
            
            cursor.execute("""
                INSERT INTO blocks (id, resource_id, block_type, content, start_line, end_line, token_count, content_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (block_id, resource_id, 'text', chunk['text'], chunk['start'], chunk['end'], len(chunk['text'])//4, content_date))
            
            cursor.execute("""
                INSERT INTO vectors (block_id, embedding)
                VALUES (?, ?)
            """, (block_id, embedding_blob))
            
        self._conn.commit()
        LOG.info(f"Indexed {file_path}: {len(chunks)} blocks")

    def tag_resource(self, file_path: str, tag: str):
        resource_id = hashlib.md5(file_path.encode('utf-8')).hexdigest()
        try:
            self._conn.execute("INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)", (resource_id, tag))
            self._conn.commit()
        except Exception as e:
            LOG.error(f"Tagging error: {e}")

    def _chunk_content_markdown(self, content: str, max_chunk_size: int = 1500, 
                                 min_chunk_size: int = 200, overlap: int = 100) -> List[Dict]:
        """
        Markdown-aware chunker that respects document structure.
        
        Respects:
        - Headers (splits before headers)
        - Code blocks (keeps together)
        - Bullet lists (keeps related items together)
        - Paragraphs
        """
        chunks = []
        lines = content.split('\n')
        
        current_chunk_lines = []
        current_chunk_size = 0
        start_line = 1
        in_code_block = False
        code_block_start = 0
        
        def flush_chunk(end_idx: int):
            nonlocal current_chunk_lines, current_chunk_size, start_line
            if current_chunk_lines:
                text = '\n'.join(current_chunk_lines)
                if len(text.strip()) >= min_chunk_size // 2:  # Don't discard very short meaningful chunks
                    chunks.append({
                        'text': text,
                        'start': start_line,
                        'end': end_idx,
                        'type': 'text'
                    })
            current_chunk_lines = []
            current_chunk_size = 0
        
        for i, line in enumerate(lines, 1):
            line_len = len(line)
            
            # Track code blocks
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block - flush current if we're at capacity
                    if current_chunk_size > max_chunk_size * 0.7:
                        flush_chunk(i - 1)
                        start_line = i
                    in_code_block = True
                    code_block_start = i
                else:
                    # Ending code block - keep it together
                    in_code_block = False
                current_chunk_lines.append(line)
                current_chunk_size += line_len
                continue
            
            # Inside code block - don't split
            if in_code_block:
                current_chunk_lines.append(line)
                current_chunk_size += line_len
                continue
            
            # Header detection - potential split point
            is_header = re.match(r'^#{1,6}\s', line)
            
            # Should we split before this line?
            should_split = False
            
            if is_header and current_chunk_size > min_chunk_size:
                # Split before headers (unless chunk is too small)
                should_split = True
            elif current_chunk_size + line_len > max_chunk_size:
                # Chunk too large - find a good break point
                if is_header:
                    should_split = True
                elif line.strip() == '':
                    # Paragraph break
                    should_split = True
                elif not line.strip().startswith(('-', '*', '1.', '•')):
                    # Not a list item continuation
                    should_split = True
            
            if should_split and current_chunk_lines:
                flush_chunk(i - 1)
                start_line = i
            
            current_chunk_lines.append(line)
            current_chunk_size += line_len
        
        # Flush remaining
        flush_chunk(len(lines))
        
        return chunks

    def _chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """
        Smart chunker - uses markdown-aware chunking for markdown files,
        falls back to simple line-based chunking otherwise.
        """
        # Detect if content is markdown-like
        has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
        has_code_blocks = '```' in content
        has_bullets = bool(re.search(r'^[\s]*[-*•]\s', content, re.MULTILINE))
        
        if has_headers or has_code_blocks or has_bullets:
            return self._chunk_content_markdown(content, max_chunk_size=chunk_size * 1.5,
                                                 min_chunk_size=chunk_size // 5)
        
        # Fallback: simple line-based chunking
        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_len = 0
        start_line = 1
        
        for i, line in enumerate(lines):
            line_len = len(line)
            if current_len + line_len > chunk_size and current_chunk:
                # Flush
                text = "\n".join(current_chunk)
                chunks.append({
                    'text': text,
                    'start': start_line,
                    'end': start_line + len(current_chunk) - 1
                })
                current_chunk = []
                current_len = 0
                start_line = i + 1
            
            current_chunk.append(line)
            current_len += line_len
            
        if current_chunk:
            text = "\n".join(current_chunk)
            chunks.append({
                'text': text,
                'start': start_line,
                'end': len(lines)
            })
            
        return chunks

    def needs_indexing(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        cursor = self._conn.cursor()
        cursor.execute("SELECT hash FROM resources WHERE path = ?", (file_path,))
        row = cursor.fetchone()
        
        if row and row[0] == current_hash:
            return False
        return True















