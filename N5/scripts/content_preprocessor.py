#!/usr/bin/env python3
"""
Content Preprocessor Pipeline for YCB-style Content Layer

Multi-stage pipeline for content ingestion:
Raw Content → Extract → Clean → Enrich → Store

Usage:
    python3 N5/scripts/content_preprocessor.py process /path/to/article.html
    python3 N5/scripts/content_preprocessor.py process /path/to/article.html --stages extract,clean
    python3 N5/scripts/content_preprocessor.py process /path/to/article.html --dry-run

Part of Content Library v4 - YCB Content Layer.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import existing normalization functions from content_ingest
import sys
sys.path.insert(0, str(Path(__file__).parent))
from content_ingest import (
    DB_PATH, CANONICAL_ROOT, TYPE_DIRECTORIES,
    extract_with_trafilatura, heuristic_strip_boilerplate,
    parse_frontmatter, detect_content_type, generate_summary,
    find_companion_html, classify_ingest_mode
)

# API endpoint for LLM enrichment
ZO_ASK_ENDPOINT = "https://api.zo.computer/zo/ask"


class ContentPreprocessor:
    """Multi-stage content preprocessing pipeline."""
    
    def __init__(self, db_path: str = None):
        """Initialize preprocessor with database connection."""
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database exists and has required tables."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")
    
    def process(self, filepath: Path, options: Dict[str, Any] = None) -> str:
        """Run full pipeline on a file.
        
        Args:
            filepath: Path to the file to process
            options: Optional parameters for processing
        
        Returns:
            item_id: The ID of the created content item
        """
        options = options or {}
        stages = options.get('stages', ['extract', 'clean', 'enrich', 'store'])
        
        # Stage 1: Extract
        raw_content = self.extract(filepath) if 'extract' in stages else None
        
        # Stage 2: Clean
        if 'clean' in stages and raw_content:
            raw_content = self.clean(raw_content)
        
        # Stage 3: Enrich
        if 'enrich' in stages and raw_content:
            raw_content = self.enrich(raw_content, filepath)
        
        # Stage 4: Store
        if 'store' in stages and raw_content:
            item_id = self.store(raw_content, filepath, options)
            return item_id
        
        return None
    
    def extract(self, filepath: Path) -> Dict[str, Any]:
        """Stage 1: Extract content from source file.
        
        Returns:
            Dict containing extracted content and metadata
        """
        print(f"🔍 Extracting content from {filepath}")
        
        result = {
            'source_path': str(filepath),
            'extraction_method': None,
            'frontmatter': {},
            'body': '',
            'metadata': {}
        }
        
        try:
            # Read the source file
            if not filepath.exists():
                raise FileNotFoundError(f"Source file not found: {filepath}")
            
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            # Parse frontmatter for markdown files
            if filepath.suffix.lower() == '.md':
                frontmatter, body = parse_frontmatter(content)
                result['frontmatter'] = frontmatter
                result['body'] = body
                result['extraction_method'] = 'frontmatter'
            
            # Try trafilatura for HTML content (either direct HTML or companion file)
            html_content = None
            if filepath.suffix.lower() == '.html':
                html_content = content
                result['extraction_method'] = 'trafilatura_direct'
            else:
                # Look for companion HTML file
                companion_html = find_companion_html(filepath)
                if companion_html:
                    html_content = companion_html.read_text(encoding='utf-8', errors='ignore')
                    result['extraction_method'] = 'trafilatura_companion'
            
            if html_content:
                extracted = extract_with_trafilatura(Path('/tmp/temp.html'))
                # Write temp file for trafilatura
                temp_path = Path('/tmp/temp_extract.html')
                temp_path.write_text(html_content, encoding='utf-8')
                extracted = extract_with_trafilatura(temp_path)
                temp_path.unlink(missing_ok=True)
                
                if extracted['text']:
                    result['body'] = extracted['text']
                    # Merge extracted metadata
                    for key in ('title', 'author', 'date', 'description'):
                        if extracted.get(key):
                            result['metadata'][key] = extracted[key]
            
            # PDF extraction using pdfplumber
            if filepath.suffix.lower() == '.pdf':
                try:
                    import pdfplumber
                    with pdfplumber.open(filepath) as pdf:
                        text = ''
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + '\n'
                        result['body'] = text
                        result['extraction_method'] = 'pdfplumber'
                except ImportError:
                    print("Warning: pdfplumber not available for PDF extraction")
                    result['body'] = content
                    result['extraction_method'] = 'fallback'
            
            # Fallback: use content as-is
            if not result['body']:
                result['body'] = content
                result['extraction_method'] = result['extraction_method'] or 'raw'
                
        except Exception as e:
            print(f"Warning: Extraction failed: {e}")
            result['body'] = ''
            result['extraction_method'] = 'error'
            result['extraction_error'] = str(e)
        
        print(f"  ✓ Extracted {len(result['body'])} characters via {result['extraction_method']}")
        return result
    
    def clean(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Clean extracted content.
        
        Args:
            content: Content dict from extract stage
        
        Returns:
            Updated content dict with cleaned body
        """
        print(f"🧹 Cleaning content ({len(content['body'])} chars)")
        
        if not content['body']:
            return content
        
        # Apply heuristic boilerplate removal (skip for social posts)
        mode = content.get('mode', 'article')
        if mode != 'social':
            cleaned_body = heuristic_strip_boilerplate(content['body'])
        else:
            cleaned_body = content['body']
        
        # Additional cleaning steps
        cleaned_body = self._normalize_whitespace(cleaned_body)
        cleaned_body = self._remove_encoding_artifacts(cleaned_body)
        
        # Store original length for reference
        original_length = len(content['body'])
        content['body'] = cleaned_body
        content['cleaned_chars_removed'] = original_length - len(cleaned_body)
        
        print(f"  ✓ Removed {content['cleaned_chars_removed']} characters")
        return content
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace patterns."""
        if not text:
            return text
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines (more than 3 consecutive)
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        text = '\n'.join(line.rstrip() for line in lines)
        
        # Remove excessive spaces
        text = re.sub(r' {3,}', '  ', text)
        
        return text.strip()
    
    def _remove_encoding_artifacts(self, text: str) -> str:
        """Remove common encoding artifacts."""
        if not text:
            return text
        
        artifacts = [
            '\ufffd',  # Replacement character
            '\u00a0',  # Non-breaking space
            '\u200b',  # Zero-width space
            '\u2018', '\u2019',  # Smart single quotes
            '\u201c', '\u201d',  # Smart double quotes
            '\u2013', '\u2014',  # En dash, em dash
            '\u2026',  # Ellipsis
        ]
        
        replacements = [
            ' ',       # Replacement character -> space
            ' ',       # Non-breaking space -> regular space
            '',        # Zero-width space -> nothing
            "'", "'",  # Smart single quotes -> regular quotes
            '"', '"',  # Smart double quotes -> regular quotes
            '-', '--', # En dash, em dash -> hyphens
            '...',     # Ellipsis -> three dots
        ]
        
        for artifact, replacement in zip(artifacts, replacements):
            text = text.replace(artifact, replacement)
        
        return text
    
    def enrich(self, content: Dict[str, Any], filepath: Path) -> Dict[str, Any]:
        """Stage 3: Enrich with metadata and derived data.
        
        Args:
            content: Content dict from clean stage
            filepath: Original source file path
        
        Returns:
            Updated content dict with enriched metadata
        """
        print("🔬 Enriching content with metadata")
        
        if not content['body']:
            return content
        
        # Generate summary if not present
        if not content['frontmatter'].get('summary'):
            summary = generate_summary(content['body'])
            if summary:
                content['frontmatter']['summary'] = summary
                print(f"  ✓ Generated summary ({len(summary)} chars)")
        
        # Extract entities
        entities = self._extract_entities(content['body'])
        content['metadata']['entities'] = entities
        print(f"  ✓ Extracted {sum(len(v) for v in entities.values())} entities")
        
        # Classify content type and mode
        content_type = content['frontmatter'].get('type') or detect_content_type(filepath)
        mode = classify_ingest_mode(filepath, content['frontmatter'])
        content['content_type'] = content_type
        content['mode'] = mode
        print(f"  ✓ Classified as {content_type} ({mode})")
        
        # Generate embeddings (placeholder - would need embedding service)
        # content['metadata']['has_embedding'] = False
        
        # Detect related content (placeholder - would use semantic similarity)
        # related_items = self._find_related_content(content['body'])
        # content['metadata']['related'] = related_items
        
        # Word count
        word_count = len(content['body'].split())
        content['metadata']['word_count'] = word_count
        print(f"  ✓ Word count: {word_count}")
        
        return content
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities using simple heuristics.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dict with entity types as keys and lists of entities as values
        """
        entities = {
            'people': [],
            'companies': [],
            'emails': [],
            'urls': [],
            'money': [],
            'dates': []
        }
        
        if not text:
            return entities
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = list(set(re.findall(email_pattern, text)))
        
        # URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        entities['urls'] = list(set(re.findall(url_pattern, text)))
        
        # Money amounts
        money_pattern = r'\$[\d,]+(?:\.\d{2})?(?:\s?(?:million|billion|trillion|M|B|T))?'
        entities['money'] = list(set(re.findall(money_pattern, text, re.IGNORECASE)))
        
        # Date patterns (simple)
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
            r'\b\d{1,2}/\d{1,2}/\d{4}',
            r'\b\d{4}-\d{2}-\d{2}'
        ]
        for pattern in date_patterns:
            entities['dates'].extend(re.findall(pattern, text, re.IGNORECASE))
        entities['dates'] = list(set(entities['dates']))
        
        # Capitalized phrases (potential people/companies)
        # Simple heuristic: 2-3 consecutive capitalized words
        cap_pattern = r'\b(?:[A-Z][a-z]+\s+){1,2}[A-Z][a-z]+\b'
        cap_matches = re.findall(cap_pattern, text)
        
        # Simple classification based on common patterns
        known_companies = {'Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Tesla', 'OpenAI', 'Anthropic'}
        for match in cap_matches:
            match = match.strip()
            if any(company in match for company in known_companies):
                entities['companies'].append(match)
            elif len(match.split()) <= 3:  # Likely person names
                entities['people'].append(match)
        
        # Deduplicate and limit
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]  # Limit to 10 per category
        
        return entities
    
    def store(self, content: Dict[str, Any], filepath: Path, options: Dict[str, Any] = None) -> str:
        """Stage 4: Store enriched content in content library.
        
        Args:
            content: Enriched content dict
            filepath: Original source file path
            options: Storage options
        
        Returns:
            item_id: ID of the created content item
        """
        print("💾 Storing content in library")
        
        options = options or {}
        dry_run = options.get('dry_run', False)
        
        # Prepare item data
        title = content['frontmatter'].get('title') or self._extract_title_from_filename(filepath)
        content_type = content.get('content_type', 'article')
        body = content['body']
        entities = content['metadata'].get('entities', {})
        word_count = content['metadata'].get('word_count', 0)
        
        # Create tags from entities and frontmatter
        tags = []
        if content['frontmatter'].get('tags'):
            tags.extend(content['frontmatter']['tags'].split(','))
        
        # Add entity-based tags
        for entity_type, entity_list in entities.items():
            for entity in entity_list[:3]:  # Limit to top 3 per type
                tags.append(f"{entity_type}:{entity}")
        
        tags_str = ','.join(sorted(set(tag.strip() for tag in tags if tag.strip())))
        
        if dry_run:
            print(f"  🔍 Dry run: Would create '{title}' ({content_type}, {word_count} words)")
            return "dry_run_id"
        
        # Create database record
        conn = sqlite3.connect(self.db_path)
        try:
            record_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Store metadata as JSON
            metadata_json = json.dumps({
                'entities': entities,
                'extraction_method': content.get('extraction_method'),
                'mode': content.get('mode'),
                'cleaned_chars_removed': content.get('cleaned_chars_removed', 0),
            })
            
            conn.execute("""
                INSERT INTO items (
                    id, title, content_type, content, source_file_path,
                    tags, word_count, ingested_at, created_at, updated_at,
                    has_content, summary, media_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                title,
                content_type,
                body[:10000] if body else None,  # Store first 10k chars
                str(filepath.relative_to(Path('/home/workspace'))),
                tags_str,
                word_count,
                now,
                now,
                now,
                1 if body else 0,
                content['frontmatter'].get('summary'),
                metadata_json,
            ))
            conn.commit()
            
            print(f"  ✓ Created item {record_id}")
            return record_id
            
        finally:
            conn.close()
    
    def _extract_title_from_filename(self, filepath: Path) -> str:
        """Generate title from filename."""
        name = filepath.stem
        # Remove common suffixes like " :: domain.com"
        if " :: " in name:
            name = name.split(" :: ")[0]
        # Clean up
        name = name.replace("-", " ").replace("_", " ")
        return name.strip()
    
    def run_stage(self, stage: str, content: Dict[str, Any], filepath: Path = None) -> Dict[str, Any]:
        """Run a specific stage independently.
        
        Args:
            stage: Stage name ('extract', 'clean', 'enrich', 'store')
            content: Content dict (may be None for extract stage)
            filepath: Source file path
        
        Returns:
            Updated content dict
        """
        if stage == 'extract':
            if not filepath:
                raise ValueError("filepath required for extract stage")
            return self.extract(filepath)
        elif stage == 'clean':
            return self.clean(content)
        elif stage == 'enrich':
            if not filepath:
                raise ValueError("filepath required for enrich stage")
            return self.enrich(content, filepath)
        elif stage == 'store':
            if not filepath:
                raise ValueError("filepath required for store stage")
            return self.store(content, filepath)
        else:
            raise ValueError(f"Unknown stage: {stage}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Content Preprocessor Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process article.html
  %(prog)s process article.html --stages extract,clean
  %(prog)s process article.html --dry-run
        """
    )
    
    parser.add_argument(
        'command',
        choices=['process'],
        help='Command to run'
    )
    parser.add_argument(
        'file',
        type=Path,
        help='Path to file to process'
    )
    parser.add_argument(
        '--stages',
        type=str,
        default='extract,clean,enrich,store',
        help='Comma-separated list of stages to run (default: all)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would happen without making changes'
    )
    parser.add_argument(
        '--type',
        type=str,
        help='Override content type detection'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output'
    )
    
    args = parser.parse_args()
    
    # Resolve file path
    filepath = args.file.resolve()
    if not filepath.is_absolute():
        filepath = (Path('/home/workspace') / args.file).resolve()
    
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        return 1
    
    # Parse stages
    stages = [s.strip() for s in args.stages.split(',')]
    valid_stages = {'extract', 'clean', 'enrich', 'store'}
    if not all(stage in valid_stages for stage in stages):
        print(f"Error: Invalid stages. Valid stages: {', '.join(valid_stages)}")
        return 1
    
    # Set up options
    options = {
        'stages': stages,
        'dry_run': args.dry_run,
        'content_type': args.type,
    }
    
    if not args.quiet:
        print(f"🚀 Processing {filepath}")
        print(f"   Stages: {' → '.join(stages)}")
        if args.dry_run:
            print("   Mode: Dry run")
    
    # Run pipeline
    try:
        preprocessor = ContentPreprocessor()
        item_id = preprocessor.process(filepath, options)
        
        if not args.quiet:
            if args.dry_run:
                print("✅ Dry run completed")
            elif item_id:
                print(f"✅ Processing completed: {item_id}")
            else:
                print("⚠️  Processing completed without storing")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())