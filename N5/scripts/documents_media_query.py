#!/usr/bin/env python3
"""
Documents & Media Query Interface - Search and retrieve registered items.
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(message)s")

DB_PATH = Path("/home/workspace/N5/data/documents_media.db")


def format_document(doc: tuple) -> Dict:
    """Format document tuple into dictionary."""
    return {
        'id': doc[0],
        'filepath': doc[1],
        'filename': doc[2],
        'file_type': doc[3],
        'size_bytes': doc[4],
        'created_date': doc[5],
        'modified_date': doc[6],
        'ingestion_date': doc[7],
        'processing_status': doc[8],
        'curation_score': doc[9],
        'tags': doc[10],
    }


def format_media(media: tuple) -> Dict:
    """Format media tuple into dictionary."""
    return {
        'id': media[0],
        'filepath': media[1],
        'filename': media[2],
        'media_type': media[3],
        'format': media[4],
        'duration_seconds': media[5],
        'transcript_path': media[6],
        'transcript_status': media[7],
        'created_date': media[8],
        'ingestion_date': media[9],
        'processing_status': media[10],
        'curation_score': media[11],
        'tags': media[12],
    }


def list_documents(conn: sqlite3.Connection, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """List documents with optional status filter."""
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT id, filepath, filename, file_type, size_bytes,
                   created_date, modified_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM documents
            WHERE processing_status = ?
            ORDER BY ingestion_date DESC
            LIMIT ?
        """, (status, limit))
    else:
        cursor.execute("""
            SELECT id, filepath, filename, file_type, size_bytes,
                   created_date, modified_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM documents
            ORDER BY ingestion_date DESC
            LIMIT ?
        """, (limit,))
    
    return [format_document(row) for row in cursor.fetchall()]


def list_media(conn: sqlite3.Connection, status: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """List media with optional status filter."""
    cursor = conn.cursor()
    
    if status:
        cursor.execute("""
            SELECT id, filepath, filename, media_type, format, duration_seconds,
                   transcript_path, transcript_status, created_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM media
            WHERE processing_status = ?
            ORDER BY ingestion_date DESC
            LIMIT ?
        """, (status, limit))
    else:
        cursor.execute("""
            SELECT id, filepath, filename, media_type, format, duration_seconds,
                   transcript_path, transcript_status, created_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM media
            ORDER BY ingestion_date DESC
            LIMIT ?
        """, (limit,))
    
    return [format_media(row) for row in cursor.fetchall()]


def search_by_filename(conn: sqlite3.Connection, query: str) -> Dict[str, List]:
    """Search documents and media by filename."""
    cursor = conn.cursor()
    
    # Search documents
    cursor.execute("""
        SELECT id, filepath, filename, file_type, size_bytes,
               created_date, modified_date, ingestion_date,
               processing_status, curation_score, tags
        FROM documents
        WHERE filename LIKE ?
        ORDER BY curation_score DESC, ingestion_date DESC
    """, (f"%{query}%",))
    documents = [format_document(row) for row in cursor.fetchall()]
    
    # Search media
    cursor.execute("""
        SELECT id, filepath, filename, media_type, format, duration_seconds,
               transcript_path, transcript_status, created_date, ingestion_date,
               processing_status, curation_score, tags
        FROM media
        WHERE filename LIKE ?
        ORDER BY curation_score DESC, ingestion_date DESC
    """, (f"%{query}%",))
    media = [format_media(row) for row in cursor.fetchall()]
    
    return {'documents': documents, 'media': media}


def search_by_tags(conn: sqlite3.Connection, tags: List[str]) -> Dict[str, List]:
    """Search documents and media by tags."""
    cursor = conn.cursor()
    
    documents = []
    media_results = []
    
    for tag in tags:
        # Search documents
        cursor.execute("""
            SELECT id, filepath, filename, file_type, size_bytes,
                   created_date, modified_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM documents
            WHERE tags LIKE ?
            ORDER BY curation_score DESC, ingestion_date DESC
        """, (f"%{tag}%",))
        documents.extend([format_document(row) for row in cursor.fetchall()])
        
        # Search media
        cursor.execute("""
            SELECT id, filepath, filename, media_type, format, duration_seconds,
                   transcript_path, transcript_status, created_date, ingestion_date,
                   processing_status, curation_score, tags
            FROM media
            WHERE tags LIKE ?
            ORDER BY curation_score DESC, ingestion_date DESC
        """, (f"%{tag}%",))
        media_results.extend([format_media(row) for row in cursor.fetchall()])
    
    # Deduplicate
    docs_dict = {d['id']: d for d in documents}
    media_dict = {m['id']: m for m in media_results}
    
    return {'documents': list(docs_dict.values()), 'media': list(media_dict.values())}


def get_stats(conn: sqlite3.Connection) -> Dict:
    """Get database statistics."""
    cursor = conn.cursor()
    
    # Document stats
    cursor.execute("SELECT COUNT(*), SUM(size_bytes) FROM documents")
    doc_count, doc_size = cursor.fetchone()
    
    cursor.execute("SELECT processing_status, COUNT(*) FROM documents GROUP BY processing_status")
    doc_status = dict(cursor.fetchall())
    
    # Media stats
    cursor.execute("SELECT COUNT(*), SUM(size_bytes) FROM media")
    media_count, media_size = cursor.fetchone()
    
    cursor.execute("SELECT processing_status, COUNT(*) FROM media GROUP BY processing_status")
    media_status = dict(cursor.fetchall())
    
    # Intelligence extracts
    cursor.execute("SELECT COUNT(*) FROM intelligence_extracts")
    intel_count = cursor.fetchone()[0]
    
    return {
        'documents': {
            'count': doc_count or 0,
            'total_size_bytes': doc_size or 0,
            'by_status': doc_status,
        },
        'media': {
            'count': media_count or 0,
            'total_size_bytes': media_size or 0,
            'by_status': media_status,
        },
        'intelligence_extracts': {
            'count': intel_count,
        }
    }


def print_results(results: Dict, output_format: str = 'text'):
    """Print query results in specified format."""
    if output_format == 'json':
        print(json.dumps(results, indent=2))
        return
    
    # Text format
    if 'documents' in results:
        docs = results['documents']
        print(f"\n=== Documents ({len(docs)}) ===")
        for doc in docs:
            print(f"  {doc['filename']}")
            print(f"    ID: {doc['id']}")
            print(f"    Type: {doc['file_type']}")
            print(f"    Status: {doc['processing_status']}")
            print(f"    Score: {doc['curation_score'] or 'N/A'}")
            print(f"    Path: {doc['filepath']}")
            print()
    
    if 'media' in results:
        media_items = results['media']
        print(f"\n=== Media ({len(media_items)}) ===")
        for media in media_items:
            print(f"  {media['filename']}")
            print(f"    ID: {media['id']}")
            print(f"    Type: {media['media_type']} ({media['format']})")
            print(f"    Status: {media['processing_status']}")
            print(f"    Transcript: {media['transcript_status']}")
            print(f"    Score: {media['curation_score'] or 'N/A'}")
            print(f"    Path: {media['filepath']}")
            print()


def main(
    list_docs: bool = False,
    list_media_files: bool = False,
    stats: bool = False,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    status: Optional[str] = None,
    output_format: str = 'text',
    limit: int = 50
) -> int:
    """Main query function."""
    try:
        if not DB_PATH.exists():
            logging.error(f"Database not found: {DB_PATH}")
            return 1
        
        conn = sqlite3.connect(DB_PATH)
        
        if stats:
            results = get_stats(conn)
            if output_format == 'json':
                print(json.dumps(results, indent=2))
            else:
                print("\n=== Documents & Media Statistics ===")
                print(f"\nDocuments: {results['documents']['count']}")
                print(f"  Size: {results['documents']['total_size_bytes']:,} bytes")
                print(f"  By status: {results['documents']['by_status']}")
                print(f"\nMedia: {results['media']['count']}")
                print(f"  Size: {results['media']['total_size_bytes']:,} bytes")
                print(f"  By status: {results['media']['by_status']}")
                print(f"\nIntelligence Extracts: {results['intelligence_extracts']['count']}")
        
        elif search:
            results = search_by_filename(conn, search)
            print_results(results, output_format)
        
        elif tags:
            tag_list = [t.strip() for t in tags.split(',')]
            results = search_by_tags(conn, tag_list)
            print_results(results, output_format)
        
        elif list_docs:
            documents = list_documents(conn, status, limit)
            print_results({'documents': documents}, output_format)
        
        elif list_media_files:
            media_items = list_media(conn, status, limit)
            print_results({'media': media_items}, output_format)
        
        else:
            logging.error("Must specify --list-docs, --list-media, --stats, --search, or --tags")
            return 1
        
        conn.close()
        return 0
        
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query documents and media registry"
    )
    parser.add_argument("--list-docs", action="store_true", help="List documents")
    parser.add_argument("--list-media", action="store_true", help="List media")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--search", type=str, help="Search by filename")
    parser.add_argument("--tags", type=str, help="Search by tags (comma-separated)")
    parser.add_argument("--status", type=str, help="Filter by status (pending/processed/curated/error)")
    parser.add_argument("--format", type=str, default="text", choices=["text", "json"], help="Output format")
    parser.add_argument("--limit", type=int, default=50, help="Limit results")
    
    args = parser.parse_args()
    exit(main(
        list_docs=args.list_docs,
        list_media_files=args.list_media,
        stats=args.stats,
        search=args.search,
        tags=args.tags,
        status=args.status,
        output_format=args.format,
        limit=args.limit
    ))
