#!/usr/bin/env python3
"""
PageIndex Store — Document tree indexing and storage for N5 Brain.

Wraps the PageIndex library to:
1. Generate hierarchical tree structures from documents
2. Store trees in brain.db (page_trees + page_nodes tables)
3. Provide retrieval interfaces for the query router

Usage:
    from N5.cognition.pageindex.pageindex_store import PageIndexStore
    
    store = PageIndexStore()
    tree = store.index_document("/path/to/doc.pdf")
    store.store_tree(resource_id, tree)
    nodes = store.search_nodes("AISS framework", limit=5)
"""

import json
import hashlib
import logging
import sqlite3
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

LOG = logging.getLogger("pageindex_store")

BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")
PAGEINDEX_LIB = Path("/home/workspace/N5/cognition/pageindex/lib")
PAGEINDEX_VERSION = "1.0"


@dataclass
class PageNode:
    """A node in the document tree."""
    id: str
    resource_id: str
    title: str
    summary: str
    start_page: Optional[int]
    end_page: Optional[int]
    depth: int
    parent_node_id: Optional[str]
    node_index: str


@dataclass 
class PageTree:
    """Full document tree structure."""
    id: str  # resource_id
    doc_name: str
    tree_json: str
    summary: str
    node_count: int
    indexed_at: str
    pageindex_version: str


class PageIndexStore:
    """PageIndex storage and retrieval for N5 Brain."""
    
    def __init__(self, db_path: str = str(BRAIN_DB)):
        self.db_path = db_path
        self._conn = None
        self._ensure_schema()
    
    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _ensure_schema(self):
        """Create tables if they don't exist."""
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS page_trees (
                id TEXT PRIMARY KEY,
                doc_name TEXT NOT NULL,
                tree_json TEXT NOT NULL,
                summary TEXT,
                node_count INTEGER,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pageindex_version TEXT DEFAULT '1.0'
            );
            
            CREATE TABLE IF NOT EXISTS page_nodes (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                start_page INTEGER,
                end_page INTEGER,
                depth INTEGER,
                parent_node_id TEXT,
                node_index TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_page_trees_doc ON page_trees(doc_name);
            CREATE INDEX IF NOT EXISTS idx_page_nodes_resource ON page_nodes(resource_id);
            CREATE INDEX IF NOT EXISTS idx_page_nodes_title ON page_nodes(title);
        """)
        conn.commit()
    
    def index_document(self, filepath: str, model: str = "gpt-4o") -> Optional[Dict]:
        """
        Generate PageIndex tree structure for a document.
        
        Args:
            filepath: Path to PDF or markdown file
            model: OpenAI model to use for tree generation
            
        Returns:
            Tree structure dict or None if indexing failed
        """
        filepath = Path(filepath)
        if not filepath.exists():
            LOG.error(f"File not found: {filepath}")
            return None
        
        ext = filepath.suffix.lower()
        
        if ext == '.pdf':
            return self._index_pdf(filepath, model)
        elif ext in ['.md', '.markdown']:
            return self._index_markdown(filepath)
        else:
            LOG.warning(f"Unsupported file type: {ext}")
            return None
    
    def _index_pdf(self, filepath: Path, model: str) -> Optional[Dict]:
        """Index PDF using PageIndex library."""
        try:
            # Run PageIndex CLI
            result_dir = PAGEINDEX_LIB / "results"
            result_dir.mkdir(exist_ok=True)
            
            env = os.environ.copy()
            env["CHATGPT_API_KEY"] = os.environ.get("OPENAI_API_KEY", "")
            
            result = subprocess.run(
                ["python3", "run_pageindex.py", 
                 "--pdf_path", str(filepath),
                 "--model", model],
                cwd=str(PAGEINDEX_LIB),
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            
            if result.returncode != 0:
                LOG.error(f"PageIndex failed: {result.stderr}")
                return None
            
            # Find output file
            stem = filepath.stem
            output_file = result_dir / f"{stem}_structure.json"
            
            if not output_file.exists():
                LOG.error(f"PageIndex output not found: {output_file}")
                return None
            
            with open(output_file) as f:
                tree = json.load(f)
            
            # Clean up
            output_file.unlink()
            
            return tree
            
        except subprocess.TimeoutExpired:
            LOG.error(f"PageIndex timed out for {filepath}")
            return None
        except Exception as e:
            LOG.error(f"PageIndex error: {e}")
            return None
    
    def _index_markdown(self, filepath: Path) -> Optional[Dict]:
        """
        Generate tree structure from markdown headers.
        
        For markdown, we parse the header hierarchy directly
        rather than using the PDF-focused PageIndex.
        """
        try:
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            structure = []
            current_stack = []  # [(depth, node)]
            node_counter = [0]  # mutable counter
            
            def make_node(title: str, depth: int, start_line: int) -> Dict:
                node_counter[0] += 1
                return {
                    "title": title.strip(),
                    "start_index": start_line,
                    "end_index": None,  # filled in later
                    "depth": depth,
                    "node_index": f"{node_counter[0]:04d}",
                    "nodes": [],
                    "summary": ""
                }
            
            for i, line in enumerate(lines):
                if line.startswith('#'):
                    # Count header depth
                    depth = 0
                    for ch in line:
                        if ch == '#':
                            depth += 1
                        else:
                            break
                    
                    title = line[depth:].strip()
                    if not title:
                        continue
                    
                    node = make_node(title, depth, i + 1)
                    
                    # Close previous nodes at same or deeper depth
                    while current_stack and current_stack[-1][0] >= depth:
                        _, prev_node = current_stack.pop()
                        prev_node["end_index"] = i
                    
                    # Add as child of parent or root
                    if current_stack:
                        current_stack[-1][1]["nodes"].append(node)
                    else:
                        structure.append(node)
                    
                    current_stack.append((depth, node))
            
            # Close remaining nodes
            total_lines = len(lines)
            for _, node in current_stack:
                if node["end_index"] is None:
                    node["end_index"] = total_lines
            
            # Generate document summary from first paragraph
            summary = ""
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    summary = stripped[:500]
                    break
            
            return {
                "doc_name": filepath.name,
                "structure": structure,
                "summary": summary
            }
            
        except Exception as e:
            LOG.error(f"Markdown parsing error: {e}")
            return None
    
    def store_tree(self, resource_id: str, tree: Dict) -> bool:
        """
        Store a PageIndex tree in the database.
        
        Args:
            resource_id: ID from resources table (or content library)
            tree: Tree structure from index_document()
            
        Returns:
            True if stored successfully
        """
        try:
            conn = self._get_conn()
            
            doc_name = tree.get("doc_name", "unknown")
            summary = tree.get("summary", "")
            structure = tree.get("structure", [])
            
            # Count nodes
            def count_nodes(nodes: List) -> int:
                total = len(nodes)
                for node in nodes:
                    total += count_nodes(node.get("nodes", []))
                return total
            
            node_count = count_nodes(structure)
            
            # Store tree
            conn.execute("""
                INSERT OR REPLACE INTO page_trees 
                (id, doc_name, tree_json, summary, node_count, indexed_at, pageindex_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                resource_id,
                doc_name,
                json.dumps(tree),
                summary,
                node_count,
                datetime.now().isoformat(),
                PAGEINDEX_VERSION
            ))
            
            # Delete old nodes for this resource
            conn.execute("DELETE FROM page_nodes WHERE resource_id = ?", (resource_id,))
            
            # Store individual nodes
            def store_nodes(nodes: List, parent_id: Optional[str] = None, depth: int = 0):
                for node in nodes:
                    node_id = f"{resource_id}_{node.get('node_index', hashlib.md5(node['title'].encode()).hexdigest()[:8])}"
                    
                    conn.execute("""
                        INSERT INTO page_nodes
                        (id, resource_id, title, summary, start_page, end_page, depth, parent_node_id, node_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        node_id,
                        resource_id,
                        node.get("title", ""),
                        node.get("summary", ""),
                        node.get("start_index"),
                        node.get("end_index"),
                        depth,
                        parent_id,
                        node.get("node_index", "")
                    ))
                    
                    # Recurse into children
                    store_nodes(node.get("nodes", []), node_id, depth + 1)
            
            store_nodes(structure)
            conn.commit()
            
            LOG.info(f"Stored tree for {doc_name}: {node_count} nodes")
            return True
            
        except Exception as e:
            LOG.error(f"Failed to store tree: {e}")
            return False
    
    def get_tree(self, resource_id: str) -> Optional[Dict]:
        """Get stored tree for a resource."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT tree_json FROM page_trees WHERE id = ?",
            (resource_id,)
        ).fetchone()
        
        if row:
            return json.loads(row["tree_json"])
        return None
    
    def has_tree(self, resource_id: str) -> bool:
        """Check if a resource has a PageIndex tree."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT 1 FROM page_trees WHERE id = ?",
            (resource_id,)
        ).fetchone()
        return row is not None
    
    def search_nodes(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for nodes matching a query.
        
        Simple title/summary matching. For semantic search,
        use the PageIndex reasoner.
        """
        conn = self._get_conn()
        query_lower = f"%{query.lower()}%"
        
        rows = conn.execute("""
            SELECT n.*, t.doc_name
            FROM page_nodes n
            JOIN page_trees t ON n.resource_id = t.id
            WHERE LOWER(n.title) LIKE ? OR LOWER(n.summary) LIKE ?
            ORDER BY n.depth ASC
            LIMIT ?
        """, (query_lower, query_lower, limit)).fetchall()
        
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict:
        """Get statistics about indexed documents."""
        conn = self._get_conn()
        
        tree_count = conn.execute("SELECT COUNT(*) FROM page_trees").fetchone()[0]
        node_count = conn.execute("SELECT COUNT(*) FROM page_nodes").fetchone()[0]
        
        return {
            "tree_count": tree_count,
            "node_count": node_count,
            "pageindex_version": PAGEINDEX_VERSION
        }
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PageIndex Store CLI")
    parser.add_argument("command", choices=["index", "stats", "search", "check"])
    parser.add_argument("--file", help="File to index")
    parser.add_argument("--resource-id", help="Resource ID for storage")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    store = PageIndexStore()
    
    if args.command == "index":
        if not args.file:
            print("Error: --file required")
            exit(1)
        
        tree = store.index_document(args.file)
        if tree:
            resource_id = args.resource_id or hashlib.md5(args.file.encode()).hexdigest()
            store.store_tree(resource_id, tree)
            print(f"✓ Indexed {args.file}")
            print(f"  Nodes: {tree.get('structure', [])}")
        else:
            print(f"✗ Failed to index {args.file}")
            exit(1)
    
    elif args.command == "stats":
        stats = store.get_stats()
        print(f"PageIndex Stats:")
        print(f"  Trees: {stats['tree_count']}")
        print(f"  Nodes: {stats['node_count']}")
    
    elif args.command == "search":
        if not args.query:
            print("Error: --query required")
            exit(1)
        
        results = store.search_nodes(args.query, args.limit)
        for r in results:
            print(f"  [{r['doc_name']}] {r['title']} (depth={r['depth']})")
    
    elif args.command == "check":
        if not args.resource_id:
            print("Error: --resource-id required")
            exit(1)
        
        has = store.has_tree(args.resource_id)
        print(f"Has tree: {has}")
    
    store.close()
