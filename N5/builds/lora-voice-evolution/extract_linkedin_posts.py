#!/usr/bin/env python3
"""
Extract LinkedIn Posts from Multiple Sources
Part of the lora-voice-evolution build (Drop D1.1)
"""

import json
import sqlite3
import duckdb
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime


class LinkedInPostExtractor:
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.seen_texts: Set[str] = set()  # For deduplication
        self.posts: List[Dict] = []
        self.stats = {
            "duckdb_shares": 0,
            "voice_library_v2": 0,
            "content_library": 0,
            "paragraph_chunks": 0,
            "duplicates_removed": 0,
            "final_count": 0
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for deduplication comparison"""
        # Fix escaped newlines from DuckDB
        text = text.replace('\\"\\n\\"', '\n').replace('\\n', '\n')
        # Clean up extra quotes
        text = text.replace('""', '"')
        # Strip whitespace
        return text.strip()
    
    def get_dedup_key(self, text: str) -> str:
        """Get first 100 chars for deduplication"""
        normalized = self.normalize_text(text)
        return normalized[:100].lower().strip()
    
    def add_post(self, source: str, text: str, timestamp: str = None, metadata: Dict = None) -> bool:
        """Add a post if not duplicate and meets criteria"""
        normalized_text = self.normalize_text(text)
        
        # Filter out short posts
        if len(normalized_text) < 50:
            return False
        
        # Check for duplicates
        dedup_key = self.get_dedup_key(normalized_text)
        if dedup_key in self.seen_texts:
            self.stats["duplicates_removed"] += 1
            return False
        
        self.seen_texts.add(dedup_key)
        
        # Generate ID
        post_id = f"linkedin_post_{len(self.posts) + 1:03d}"
        
        # Create post record
        post = {
            "id": post_id,
            "source": source,
            "platform": "linkedin",
            "content_type": "post",
            "text": normalized_text,
            "char_count": len(normalized_text),
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        
        self.posts.append(post)
        self.stats[source] += 1
        return True
    
    def extract_from_duckdb(self, db_path: str):
        """Extract from DuckDB shares table"""
        print(f"Extracting from DuckDB: {db_path}")
        
        conn = duckdb.connect(db_path, read_only=True)
        
        query = """
        SELECT shared_at, share_commentary, shared_url, media_url, visibility
        FROM shares 
        WHERE share_commentary IS NOT NULL 
        AND LENGTH(share_commentary) > 50
        ORDER BY shared_at DESC
        """
        
        results = conn.execute(query).fetchall()
        
        for row in results:
            shared_at, commentary, shared_url, media_url, visibility = row
            
            # Convert timestamp to string
            timestamp_str = shared_at.strftime("%Y-%m-%dT%H:%M:%S") if shared_at else None
            
            metadata = {
                "shared_url": shared_url,
                "has_media": bool(media_url),
                "visibility": visibility,
                "originality_score": None
            }
            
            self.add_post("duckdb_shares", commentary, timestamp_str, metadata)
        
        conn.close()
        print(f"Processed {len(results)} records from DuckDB shares")
    
    def extract_from_voice_library_v2(self, jsonl_path: str):
        """Extract from voice-library-v2 corpus"""
        print(f"Extracting from voice-library-v2: {jsonl_path}")
        
        with open(jsonl_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                # Look for long-form content that might be posts
                # Most are comments, but longer ones could be post-like
                text = data.get("text", "")
                char_count = data.get("char_count", 0)
                
                # Focus on longer content that might be original posts
                if char_count > 300:  # Longer content more likely to be posts
                    timestamp = data.get("timestamp")
                    context_url = data.get("context_url")
                    
                    metadata = {
                        "source_id": data.get("id"),
                        "context_url": context_url,
                        "original_type": data.get("type", "unknown"),
                        "originality_score": None
                    }
                    
                    self.add_post("voice_library_v2", text, timestamp, metadata)
        
        print(f"Processed voice-library-v2 corpus")
    
    def extract_from_content_library(self, directory: str):
        """Extract from content library markdown files"""
        print(f"Extracting from content library: {directory}")
        
        dir_path = Path(directory)
        
        for md_file in dir_path.glob("*.md"):
            try:
                with open(md_file, 'r') as f:
                    content = f.read()
                
                # Split frontmatter and body
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter_text = parts[1]
                        body = parts[2].strip()
                        
                        # Parse some basic frontmatter
                        created_match = re.search(r'created:\s*(\S+)', frontmatter_text)
                        originality_match = re.search(r'originality_score:\s*(\d+)', frontmatter_text)
                        
                        timestamp = None
                        if created_match:
                            try:
                                timestamp = datetime.strptime(created_match.group(1), "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00")
                            except:
                                pass
                        
                        metadata = {
                            "source_file": str(md_file),
                            "originality_score": int(originality_match.group(1)) if originality_match else None
                        }
                        
                        # Extract just the main content, skip the markdown title
                        if body.startswith("# "):
                            lines = body.split("\n", 1)
                            if len(lines) > 1:
                                body = lines[1].strip()
                        
                        self.add_post("content_library", body, timestamp, metadata)
                        
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
        
        print(f"Processed content library files")
    
    def extract_from_paragraph_chunks(self, jsonl_path: str):
        """Extract from paragraph chunks"""
        print(f"Extracting from paragraph chunks: {jsonl_path}")
        
        with open(jsonl_path, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                text = data.get("text", "")
                position = data.get("position", "")
                post_type = data.get("post_type", "")
                char_count = data.get("char_count", 0)
                
                # Focus on opening paragraphs which are more complete
                if position == "opening" and char_count > 200:
                    metadata = {
                        "source_id": data.get("id"),
                        "post_type": post_type,
                        "position": position,
                        "source_post_id": data.get("source_post_id"),
                        "originality_score": None
                    }
                    
                    self.add_post("paragraph_chunks", text, None, metadata)
        
        print(f"Processed paragraph chunks")
    
    def save_posts(self):
        """Save all posts to JSONL file"""
        self.stats["final_count"] = len(self.posts)
        
        print(f"\nWriting {self.stats['final_count']} posts to {self.output_path}")
        
        with open(self.output_path, 'w') as f:
            for post in self.posts:
                f.write(json.dumps(post, ensure_ascii=False) + "\n")
    
    def print_stats(self):
        """Print extraction statistics"""
        print(f"\n{'='*50}")
        print("EXTRACTION STATISTICS")
        print(f"{'='*50}")
        print(f"DuckDB shares:     {self.stats['duckdb_shares']:4d}")
        print(f"Voice library v2:  {self.stats['voice_library_v2']:4d}")
        print(f"Content library:   {self.stats['content_library']:4d}")
        print(f"Paragraph chunks:  {self.stats['paragraph_chunks']:4d}")
        print(f"Duplicates removed: {self.stats['duplicates_removed']:4d}")
        print(f"{'='*50}")
        print(f"FINAL COUNT:       {self.stats['final_count']:4d}")
        print(f"{'='*50}")
        
        # Quality analysis
        if self.posts:
            char_counts = [p["char_count"] for p in self.posts]
            avg_length = sum(char_counts) / len(char_counts)
            print(f"Average post length: {avg_length:.0f} characters")
            print(f"Shortest post: {min(char_counts)} characters")
            print(f"Longest post: {max(char_counts)} characters")
            
            # Source breakdown
            print(f"\nSource Quality Ranking:")
            print(f"1. content_library ({self.stats['content_library']}) - Curated, high quality")
            print(f"2. duckdb_shares ({self.stats['duckdb_shares']}) - Raw but complete")
            print(f"3. paragraph_chunks ({self.stats['paragraph_chunks']}) - Structured segments")
            print(f"4. voice_library_v2 ({self.stats['voice_library_v2']}) - Mixed quality")


def main():
    """Main extraction function"""
    print("=== LinkedIn Posts Extraction (Drop D1.1) ===")
    
    output_path = "N5/builds/lora-voice-evolution/artifacts/linkedin_posts_raw.jsonl"
    extractor = LinkedInPostExtractor(output_path)
    
    # Data source paths
    duckdb_path = "/home/workspace/Datasets/linkedin-full-pre-jan-10/data.duckdb"
    voice_lib_path = "/home/workspace/N5/builds/voice-library-v2/linkedin_corpus.jsonl"
    content_lib_path = "/home/workspace/Knowledge/content-library/social-posts/linkedin"
    paragraph_chunks_path = "/home/workspace/Knowledge/voice-library/paragraph-chunks.jsonl"
    
    # Extract from all sources
    if os.path.exists(duckdb_path):
        extractor.extract_from_duckdb(duckdb_path)
    else:
        print(f"Warning: DuckDB not found at {duckdb_path}")
    
    if os.path.exists(voice_lib_path):
        extractor.extract_from_voice_library_v2(voice_lib_path)
    else:
        print(f"Warning: Voice library v2 not found at {voice_lib_path}")
    
    if os.path.exists(content_lib_path):
        extractor.extract_from_content_library(content_lib_path)
    else:
        print(f"Warning: Content library not found at {content_lib_path}")
    
    if os.path.exists(paragraph_chunks_path):
        extractor.extract_from_paragraph_chunks(paragraph_chunks_path)
    else:
        print(f"Warning: Paragraph chunks not found at {paragraph_chunks_path}")
    
    # Save and report
    extractor.save_posts()
    extractor.print_stats()
    
    return extractor.stats


if __name__ == "__main__":
    stats = main()
    
    # Create broadcast message
    broadcast_msg = f"LinkedIn posts dataset has {stats['final_count']} entries. Highest quality source is content_library (curated). DuckDB shares has raw unformatted text with escaped newlines — handle \\\"\\n\\\" as actual newlines."
    
    print(f"\nBROADCAST: {broadcast_msg}")