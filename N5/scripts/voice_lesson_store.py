#!/usr/bin/env python3
"""
Voice Lesson Store - Store extracted lessons to semantic memory and voice library.

Usage:
  python3 N5/scripts/voice_lesson_store.py store \
    --lesson-json '{"lessons": [...], "candidate_primitives": [...]}' \
    --pair-id 5

  python3 N5/scripts/voice_lesson_store.py list \
    [--content-type "cold_email"] \
    [--global-only]
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add N5 to path
sys.path.insert(0, '/home/workspace')
from N5.cognition.n5_memory_client import N5MemoryClient
from N5.lib.paths import BRAIN_DB

# Paths
VOICE_DB = Path('/home/workspace/N5/data/voice_library.db')
VOICE_LESSONS_MD = Path('/home/workspace/N5/prefs/communication/voice-lessons.md')
REVIEW_QUEUE = Path('/home/workspace/N5/review/voice/primitives-from-edits.md')

# Lesson path prefix for semantic memory
LESSON_PATH_PREFIX = "voice://lessons/"


def get_voice_db() -> sqlite3.Connection:
    """Get connection to voice library database."""
    conn = sqlite3.connect(str(VOICE_DB))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_lesson_tables():
    """Ensure voice_lessons and candidate_primitives tables exist."""
    conn = get_voice_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_lessons (
            id TEXT PRIMARY KEY,
            content_type TEXT NOT NULL,
            lesson TEXT NOT NULL,
            anti_pattern TEXT,
            positive_pattern TEXT,
            confidence TEXT DEFAULT 'medium',
            global_candidate INTEGER DEFAULT 0,
            source_changes TEXT,
            source_pair_id INTEGER,
            content_hash TEXT UNIQUE,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (source_pair_id) REFERENCES feedback_pairs(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_primitives (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            type TEXT NOT NULL,
            function TEXT,
            source TEXT DEFAULT 'v_edit',
            source_pair_id INTEGER,
            approved INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (source_pair_id) REFERENCES feedback_pairs(id)
        )
    """)
    
    conn.commit()
    conn.close()


def hash_lesson(lesson: Dict) -> str:
    """Create content hash for deduplication."""
    content = (
        (lesson.get('lesson') or '') +
        (lesson.get('anti_pattern') or '') +
        (lesson.get('positive_pattern') or '')
    )
    return hashlib.md5(content.encode()).hexdigest()


def format_lesson_for_memory(lesson: Dict) -> str:
    """Format lesson for semantic memory storage."""
    content_type = lesson.get('content_type', 'general')
    text = lesson.get('lesson', '')
    anti = lesson.get('anti_pattern', '')
    positive = lesson.get('positive_pattern', '')
    
    parts = [f"Voice preference ({content_type}): {text}"]
    if anti:
        parts.append(f"Avoid: {anti}")
    if positive:
        parts.append(f"Prefer: {positive}")
    
    return "\n".join(parts)


def store_lesson_to_memory(memory_client: N5MemoryClient, lesson: Dict, pair_id: int) -> bool:
    """Store a single lesson to semantic memory."""
    lesson_id = lesson.get('id', f'lesson_{uuid.uuid4().hex[:8]}')
    content_type = lesson.get('content_type', 'general')
    is_global = lesson.get('global_candidate', False)
    
    # Create virtual path for this lesson
    path = f"{LESSON_PATH_PREFIX}{lesson_id}"
    
    # Check if already exists
    conn = memory_client._get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM resources WHERE path = ?", (path,))
    if cursor.fetchone():
        print(f"  ⏭️  Lesson {lesson_id} already in memory, skipping")
        return False
    
    # Format content
    content = format_lesson_for_memory(lesson)
    
    # Create file hash from content
    file_hash = hashlib.md5(content.encode()).hexdigest()
    
    # Store resource
    resource_id = memory_client.store_resource(path, file_hash)
    
    # Add block with lesson content
    block_id = memory_client.add_block(
        resource_id=resource_id,
        content=content,
        block_type="voice_preference",
        start_line=0,
        end_line=0
    )
    
    # Add tags
    cursor.execute("""
        INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)
    """, (resource_id, "voice_preference"))
    
    cursor.execute("""
        INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)
    """, (resource_id, f"content_type:{content_type}"))
    
    if is_global:
        cursor.execute("""
            INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)
        """, (resource_id, "global"))
    
    cursor.execute("""
        INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)
    """, (resource_id, f"confidence:{lesson.get('confidence', 'medium')}"))
    
    cursor.execute("""
        INSERT OR IGNORE INTO tags (resource_id, tag) VALUES (?, ?)
    """, (resource_id, f"pair:{pair_id}"))
    
    conn.commit()
    return True


def store_lesson_to_db(lesson: Dict, pair_id: int) -> bool:
    """Store lesson to voice_lessons table."""
    conn = get_voice_db()
    cursor = conn.cursor()
    
    lesson_id = lesson.get('id', f'lesson_{uuid.uuid4().hex[:8]}')
    content_hash = hash_lesson(lesson)
    
    # Check for duplicate
    cursor.execute("SELECT id FROM voice_lessons WHERE content_hash = ?", (content_hash,))
    if cursor.fetchone():
        print(f"  ⏭️  Duplicate lesson (hash match), skipping")
        conn.close()
        return False
    
    try:
        cursor.execute("""
            INSERT INTO voice_lessons 
            (id, content_type, lesson, anti_pattern, positive_pattern, confidence, 
             global_candidate, source_changes, source_pair_id, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lesson_id,
            lesson.get('content_type', 'general'),
            lesson.get('lesson', ''),
            lesson.get('anti_pattern'),
            lesson.get('positive_pattern'),
            lesson.get('confidence', 'medium'),
            1 if lesson.get('global_candidate') else 0,
            json.dumps(lesson.get('source_changes', [])),
            pair_id,
            content_hash
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError as e:
        print(f"  ⚠️  Failed to insert lesson: {e}")
        conn.close()
        return False


def store_primitive_to_db(primitive: Dict, pair_id: int) -> Optional[str]:
    """Store candidate primitive to voice library (unapproved)."""
    conn = get_voice_db()
    cursor = conn.cursor()
    
    prim_id = f"vp-edit-{uuid.uuid4().hex[:8]}"
    text = primitive.get('text', '')
    
    # Check if similar primitive already exists
    cursor.execute("""
        SELECT id FROM primitives WHERE exact_text = ?
    """, (text,))
    existing = cursor.fetchone()
    if existing:
        print(f"  ⏭️  Primitive already exists: {existing['id']}")
        conn.close()
        return None
    
    # Also check candidate_primitives
    cursor.execute("""
        SELECT id FROM candidate_primitives WHERE text = ?
    """, (text,))
    if cursor.fetchone():
        print(f"  ⏭️  Candidate primitive already exists, skipping")
        conn.close()
        return None
    
    # Insert into candidate_primitives for HITL review
    cursor.execute("""
        INSERT INTO candidate_primitives (id, text, type, function, source, source_pair_id, approved)
        VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (
        prim_id,
        text,
        primitive.get('type', 'phrase'),
        primitive.get('function', ''),
        'v_edit',
        pair_id
    ))
    
    conn.commit()
    conn.close()
    return prim_id


def update_voice_lessons_md(lessons: List[Dict], pair_id: int):
    """Append lessons to voice-lessons.md in human-readable format."""
    if not lessons:
        return
    
    # Read current file
    content = VOICE_LESSONS_MD.read_text() if VOICE_LESSONS_MD.exists() else ""
    
    # Group lessons by content_type
    by_type = {}
    for lesson in lessons:
        ct = lesson.get('content_type', 'general')
        if ct not in by_type:
            by_type[ct] = []
        by_type[ct].append(lesson)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # For each content type, find section and append
    for content_type, type_lessons in by_type.items():
        section_header = f"### {content_type.replace('_', ' ').title()}"
        
        for lesson in type_lessons:
            lesson_text = f"""
#### Lesson: {lesson.get('lesson', 'Untitled')[:50]}
**Learned:** {today} (from pair #{pair_id})
**Pattern:** {lesson.get('lesson', 'N/A')}
**Avoid:** {lesson.get('anti_pattern', 'N/A')}
**Prefer:** {lesson.get('positive_pattern', 'N/A')}
"""
            
            if section_header in content:
                # Find end of section content (before next ### or ## or end)
                section_start = content.index(section_header)
                section_content_start = section_start + len(section_header)
                
                # Find next section
                remaining = content[section_content_start:]
                next_section = len(content)
                for marker in ["\n### ", "\n## "]:
                    if marker in remaining:
                        next_section = min(next_section, section_content_start + remaining.index(marker))
                
                # Check if "(none yet)" exists in section
                section_content = content[section_content_start:next_section]
                if "(none yet)" in section_content:
                    # Replace "(none yet)" with lesson
                    content = content.replace(
                        content[section_start:next_section],
                        section_header + lesson_text
                    )
                else:
                    # Append before next section
                    content = content[:next_section] + lesson_text + content[next_section:]
            else:
                # Add new section before ## Global Lessons
                if "## Global Lessons" in content:
                    insert_point = content.index("## Global Lessons")
                    new_section = f"\n{section_header}\n{lesson_text}\n"
                    content = content[:insert_point] + new_section + content[insert_point:]
                else:
                    # Append at end
                    content += f"\n{section_header}\n{lesson_text}\n"
    
    # Update frontmatter
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('last_edited:'):
            lines[i] = f'last_edited: {today}'
            break
    
    VOICE_LESSONS_MD.write_text('\n'.join(lines))


def update_review_queue(primitives: List[Dict], pair_id: int):
    """Update the primitives review queue with new candidates."""
    if not primitives:
        return
    
    REVIEW_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Read or create
    if REVIEW_QUEUE.exists():
        content = REVIEW_QUEUE.read_text()
    else:
        content = f"""---
created: {today}
last_edited: {today}
version: 0.1
provenance: voice-optimization-loop
---

# Primitives from V's Edits

Candidate primitives extracted from V's edits to Zo-generated content.
Review and approve/reject these for inclusion in the voice library.

## Pending Review

"""
    
    # Add new primitives
    for prim in primitives:
        entry = f"""### [{prim.get('type', 'phrase')}] "{prim.get('text', '')}"
- **Function:** {prim.get('function', 'N/A')}
- **Source:** Pair #{pair_id}
- **Date:** {today}
- **Status:** ⏳ Pending

"""
        # Append before any ## Approved or ## Rejected sections
        if "## Approved" in content:
            insert_point = content.index("## Approved")
            content = content[:insert_point] + entry + content[insert_point:]
        elif "## Rejected" in content:
            insert_point = content.index("## Rejected")
            content = content[:insert_point] + entry + content[insert_point:]
        else:
            content += entry
    
    # Update last_edited in frontmatter
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('last_edited:'):
            lines[i] = f'last_edited: {today}'
            break
    
    REVIEW_QUEUE.write_text('\n'.join(lines))


def mark_pair_analyzed(pair_id: int):
    """Mark a feedback pair as analyzed."""
    conn = get_voice_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE feedback_pairs SET analyzed = 1 WHERE id = ?", (pair_id,))
    conn.commit()
    conn.close()


def cmd_store(args):
    """Store lessons and primitives from JSON input."""
    ensure_lesson_tables()
    
    # Parse input JSON
    try:
        data = json.loads(args.lesson_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return 1
    
    lessons = data.get('lessons', [])
    primitives = data.get('candidate_primitives', [])
    
    print(f"\n{'='*60}")
    print(f"Voice Lesson Store")
    print(f"{'='*60}")
    print(f"\nPair ID: {args.pair_id}")
    print(f"Lessons: {len(lessons)}")
    print(f"Primitives: {len(primitives)}")
    
    # Initialize memory client
    memory_client = N5MemoryClient()
    
    # Store lessons
    stored_lessons = 0
    print(f"\n--- Storing Lessons ---")
    for lesson in lessons:
        lesson_id = lesson.get('id', 'unknown')
        print(f"\n  Processing: {lesson_id}")
        
        # Store to semantic memory
        if store_lesson_to_memory(memory_client, lesson, args.pair_id):
            print(f"    ✓ Stored to semantic memory")
        
        # Store to voice_lessons table
        if store_lesson_to_db(lesson, args.pair_id):
            print(f"    ✓ Stored to voice_lessons table")
            stored_lessons += 1
    
    # Update voice-lessons.md
    if lessons:
        update_voice_lessons_md(lessons, args.pair_id)
        print(f"\n  ✓ Updated voice-lessons.md")
    
    # Store primitives
    stored_primitives = []
    print(f"\n--- Storing Candidate Primitives ---")
    for prim in primitives:
        prim_text = prim.get('text', '')[:40]
        print(f"\n  Processing: \"{prim_text}...\"")
        
        prim_id = store_primitive_to_db(prim, args.pair_id)
        if prim_id:
            stored_primitives.append(prim)
            print(f"    ✓ Added as candidate: {prim_id}")
    
    # Update review queue
    if stored_primitives:
        update_review_queue(stored_primitives, args.pair_id)
        print(f"\n  ✓ Updated review queue")
    
    # Mark pair as analyzed
    mark_pair_analyzed(args.pair_id)
    print(f"\n  ✓ Marked pair #{args.pair_id} as analyzed")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Lessons stored: {stored_lessons}/{len(lessons)}")
    print(f"  Primitives queued: {len(stored_primitives)}/{len(primitives)}")
    print(f"{'='*60}\n")
    
    return 0


def cmd_list(args):
    """List stored lessons."""
    ensure_lesson_tables()
    
    conn = get_voice_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM voice_lessons WHERE 1=1"
    params = []
    
    if args.content_type:
        query += " AND content_type = ?"
        params.append(args.content_type)
    
    if args.global_only:
        query += " AND global_candidate = 1"
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    lessons = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"Stored Voice Lessons")
    print(f"{'='*60}\n")
    
    if not lessons:
        print("  No lessons found.")
    else:
        for row in lessons:
            glob = " 🌐" if row['global_candidate'] else ""
            conf = row['confidence'] or 'medium'
            print(f"[{row['id']}] ({conf}){glob}")
            print(f"  Type: {row['content_type']}")
            print(f"  Lesson: {row['lesson']}")
            if row['anti_pattern']:
                print(f"  ✗ Avoid: {row['anti_pattern']}")
            if row['positive_pattern']:
                print(f"  ✓ Instead: {row['positive_pattern']}")
            print(f"  Source: Pair #{row['source_pair_id']}")
            print()
    
    print(f"Total: {len(lessons)} lessons")
    conn.close()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Store voice lessons and primitives")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # store command
    store_parser = subparsers.add_parser('store', help='Store lessons from JSON')
    store_parser.add_argument('--lesson-json', required=True, help='JSON with lessons and primitives')
    store_parser.add_argument('--pair-id', type=int, required=True, help='Source pair ID')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List stored lessons')
    list_parser.add_argument('--content-type', help='Filter by content type')
    list_parser.add_argument('--global-only', action='store_true', help='Only show global lessons')
    
    args = parser.parse_args()
    
    if args.command == 'store':
        return cmd_store(args)
    elif args.command == 'list':
        return cmd_list(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
