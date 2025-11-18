#!/usr/bin/env python3
"""
Meeting Duplicate Manager - CANONICAL

Detects duplicate MEETINGS (same meeting recorded multiple times) using metadata fuzzy matching.
Integrates with meeting_pipeline.db and uses Google Drive IDs as stable identifiers.

Focus: Meeting duplicate detection (NOT transcript file duplicates)
- Duplicate meetings: Same meeting recorded by Zoom + Otter, re-uploaded, etc.
- Uses: Date/time, participants, title similarity
- Key: Google Drive file ID (stable identifier)

Separate agent handles: Physical transcript file deduplication

Usage:
    # Queue meetings for duplicate check
    python3 meeting_duplicate_manager.py queue [--all | --recent DAYS]
    
    # Scan for duplicate meetings using fuzzy matching
    python3 meeting_duplicate_manager.py scan [--limit N] [--threshold 0.85]
    
    # Show duplicate clusters
    python3 meeting_duplicate_manager.py report [--json]
    
    # Resolve duplicate cluster (mark canonical meeting)
    python3 meeting_duplicate_manager.py resolve <cluster_id> --keep <gdrive_id>
    
    # Check specific meeting
    python3 meeting_duplicate_manager.py check <gdrive_id>

Database Schema:
- duplicate_clusters: Groups of duplicate meetings
- duplicate_members: Individual meetings in each cluster
- duplicate_check_queue: Meetings queued for checking
- meeting_metadata: Extracted date, participants, title for fuzzy matching
"""

import argparse
import json
import logging
import re
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)sZ %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DB_PATH = Path("/home/workspace/N5/data/meeting_pipeline.db")
MEETINGS_ROOT = Path("/home/workspace/Personal/Meetings")


class MeetingDuplicateManager:
    """Manages meeting duplicate detection using metadata fuzzy matching"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()
    
    def _get_conn(self):
        """Get database connection"""
        return sqlite3.connect(str(self.db_path))
    
    def _ensure_tables(self):
        """Create duplicate tracking tables"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # Meeting metadata for fuzzy matching
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_metadata (
                    gdrive_id TEXT PRIMARY KEY,
                    meeting_folder TEXT,
                    transcript_path TEXT,
                    extracted_date TEXT,
                    extracted_time TEXT,
                    participants TEXT,
                    title_normalized TEXT,
                    metadata_json TEXT,
                    indexed_at TEXT NOT NULL,
                    UNIQUE(gdrive_id)
                )
            """)
            
            # Duplicate clusters
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_clusters (
                    cluster_id TEXT PRIMARY KEY,
                    primary_gdrive_id TEXT,
                    cluster_size INTEGER DEFAULT 0,
                    confidence_score REAL,
                    match_reason TEXT,
                    status TEXT DEFAULT 'active',
                    detected_at TEXT NOT NULL,
                    resolved_at TEXT,
                    resolution_action TEXT,
                    FOREIGN KEY (primary_gdrive_id) REFERENCES meeting_metadata(gdrive_id)
                )
            """)
            
            # Cluster members
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_members (
                    cluster_id TEXT NOT NULL,
                    gdrive_id TEXT NOT NULL,
                    is_primary INTEGER DEFAULT 0,
                    similarity_score REAL,
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (cluster_id, gdrive_id),
                    FOREIGN KEY (cluster_id) REFERENCES duplicate_clusters(cluster_id),
                    FOREIGN KEY (gdrive_id) REFERENCES meeting_metadata(gdrive_id)
                )
            """)
            
            # Check queue
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS duplicate_check_queue (
                    gdrive_id TEXT PRIMARY KEY,
                    queued_at TEXT NOT NULL,
                    check_status TEXT DEFAULT 'pending',
                    checked_at TEXT,
                    result TEXT,
                    FOREIGN KEY (gdrive_id) REFERENCES meeting_metadata(gdrive_id)
                )
            """)
            
            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_metadata_date ON meeting_metadata(extracted_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clusters_status ON duplicate_clusters(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_queue_status ON duplicate_check_queue(check_status)")
            
            conn.commit()
            logger.info("✓ Duplicate tracking tables ready")
        finally:
            conn.close()
    
    def extract_metadata(self, folder_path: Path) -> Optional[Dict]:
        """Extract meeting metadata from folder/transcript"""
        try:
            # Get Google Drive ID from .gdrive_id file (or use folder name as fallback)
            gdrive_id_file = folder_path / ".gdrive_id"
            if gdrive_id_file.exists():
                gdrive_id = gdrive_id_file.read_text().strip()
            else:
                # Fallback: use folder name as ID until Google Drive IDs are implemented
                gdrive_id = folder_path.name
                logger.debug(f"Using folder name as ID for {folder_path.name}")
            
            # Find transcript
            transcripts = list(folder_path.glob("*.transcript.md"))
            if not transcripts:
                logger.warning(f"No transcript in {folder_path.name}")
                return None
            
            transcript_path = transcripts[0]
            
            # Extract metadata from folder name (format: YYYY-MM-DD_participants_type)
            folder_name = folder_path.name
            parts = folder_name.split('_')
            
            date_str = parts[0] if len(parts) > 0 else ""
            participants = parts[1] if len(parts) > 1 else ""
            title = '_'.join(parts[2:]) if len(parts) > 2 else ""
            
            # Also try to extract from transcript filename
            transcript_name = transcript_path.stem.replace('.transcript', '')
            
            # Extract timestamp from transcript filename (e.g., "transcript-2025-10-31T17-38-30.268Z")
            time_match = re.search(r'(\d{4}-\d{2}-\d{2})T(\d{2}-\d{2}-\d{2})', transcript_name)
            extracted_date = time_match.group(1) if time_match else date_str
            extracted_time = time_match.group(2).replace('-', ':') if time_match else ""
            
            # Normalize title (remove common suffixes, lowercase, strip)
            title_normalized = re.sub(r'[_-]+', ' ', title.lower()).strip()
            title_normalized = re.sub(r'\s+', ' ', title_normalized)
            
            # Normalize participants
            participants_normalized = re.sub(r'[_-]+', ' ', participants.lower()).strip()
            
            metadata = {
                'gdrive_id': gdrive_id,
                'meeting_folder': str(folder_path),
                'transcript_path': str(transcript_path),
                'extracted_date': extracted_date,
                'extracted_time': extracted_time,
                'participants': participants_normalized,
                'title_normalized': title_normalized,
                'transcript_name': transcript_name,
                'folder_name': folder_name
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {folder_path}: {e}")
            return None
    
    def index_meeting(self, metadata: Dict) -> bool:
        """Store meeting metadata for duplicate checking"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO meeting_metadata
                (gdrive_id, meeting_folder, transcript_path, extracted_date, extracted_time,
                 participants, title_normalized, metadata_json, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata['gdrive_id'],
                metadata['meeting_folder'],
                metadata['transcript_path'],
                metadata['extracted_date'],
                metadata['extracted_time'],
                metadata['participants'],
                metadata['title_normalized'],
                json.dumps(metadata),
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to index meeting: {e}")
            return False
        finally:
            conn.close()
    
    def queue_for_check(self, gdrive_ids: List[str]) -> int:
        """Queue meetings for duplicate checking"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            queued = 0
            for gdrive_id in gdrive_ids:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO duplicate_check_queue
                        (gdrive_id, queued_at, check_status)
                        VALUES (?, ?, 'pending')
                    """, (gdrive_id, datetime.now(timezone.utc).isoformat()))
                    if cursor.rowcount > 0:
                        queued += 1
                except Exception as e:
                    logger.error(f"Failed to queue {gdrive_id}: {e}")
            
            conn.commit()
            return queued
        finally:
            conn.close()
    
    def compute_similarity(self, meta1: Dict, meta2: Dict) -> Tuple[float, str]:
        """Compute similarity between two meetings
        
        V's use case: Solo meeting recorder, so duplicates are ONLY when:
        - Fireflies uploads 2+ transcripts within MINUTES (not hours/days)
        - Same participants, same title
        
        Logic: Time proximity (within 30 min) is the PRIMARY signal.
        """
        scores = []
        reasons = []
        
        # PRIMARY CHECK: Time proximity
        # V records one meeting at a time, so if transcripts are uploaded minutes apart,
        # that's the duplicate pattern (Fireflies bug, re-upload, etc.)
        
        if meta1['extracted_date'] and meta2['extracted_date']:
            if meta1['extracted_date'] != meta2['extracted_date']:
                # Different dates = definitely different meetings
                return 0.0, "different_days"
            
            # Same date - check time proximity
            if meta1['extracted_time'] and meta2['extracted_time']:
                try:
                    # Parse times (format: "HH:MM:SS" or "HH:MM")
                    time1_parts = meta1['extracted_time'].split(':')
                    time2_parts = meta2['extracted_time'].split(':')
                    
                    hour1, min1 = int(time1_parts[0]), int(time1_parts[1])
                    hour2, min2 = int(time2_parts[0]), int(time2_parts[1])
                    
                    # Calculate minute difference
                    total_min1 = hour1 * 60 + min1
                    total_min2 = hour2 * 60 + min2
                    min_diff = abs(total_min1 - total_min2)
                    
                    if min_diff <= 5:
                        # Within 5 minutes - very likely duplicate upload
                        scores.append(1.0)
                        reasons.append("within_5_minutes")
                    elif min_diff <= 15:
                        # Within 15 minutes - likely duplicate
                        scores.append(0.95)
                        reasons.append("within_15_minutes")
                    elif min_diff <= 30:
                        # Within 30 minutes - possible duplicate
                        scores.append(0.85)
                        reasons.append("within_30_minutes")
                    else:
                        # More than 30 min apart on same day = different meetings
                        # V doesn't have overlapping meetings
                        return 0.0, "same_day_different_times"
                        
                except Exception as e:
                    # Can't parse time - fall back to same date only
                    scores.append(0.3)
                    reasons.append("same_date_no_time")
            else:
                # Same date but no time info - low confidence
                scores.append(0.3)
                reasons.append("same_date_no_time")
        else:
            # No date info - can't determine
            return 0.0, "missing_date"
        
        # SECONDARY: Participants (should be same for duplicates)
        if meta1['participants'] and meta2['participants']:
            participant_sim = SequenceMatcher(None, meta1['participants'], meta2['participants']).ratio()
            scores.append(participant_sim)
            if participant_sim > 0.9:
                reasons.append("same_participants")
            elif participant_sim > 0.7:
                reasons.append("similar_participants")
        
        # TERTIARY: Title (should be same/similar for duplicates)
        if meta1['title_normalized'] and meta2['title_normalized']:
            title_sim = SequenceMatcher(None, meta1['title_normalized'], meta2['title_normalized']).ratio()
            scores.append(title_sim)
            if title_sim > 0.9:
                reasons.append("same_title")
            elif title_sim > 0.7:
                reasons.append("similar_title")
        
        overall_score = sum(scores) / len(scores) if scores else 0.0
        reason = ", ".join(reasons) if reasons else "no_match"
        
        return overall_score, reason
    
    def find_duplicates(self, gdrive_id: str, threshold: float = 0.80) -> List[Dict]:
        """Find potential duplicates for a meeting"""
        conn = self._get_conn()
        try:
            # Get metadata for target meeting
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gdrive_id, extracted_date, extracted_time, participants, 
                       title_normalized, metadata_json
                FROM meeting_metadata
                WHERE gdrive_id = ?
            """, (gdrive_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Meeting {gdrive_id} not indexed")
                return []
            
            target_meta = {
                'gdrive_id': row[0],
                'extracted_date': row[1],
                'extracted_time': row[2],
                'participants': row[3],
                'title_normalized': row[4],
                'metadata_json': row[5]
            }
            
            # Get all other meetings (within date window for efficiency)
            date_window_start = None
            date_window_end = None
            
            if target_meta['extracted_date']:
                try:
                    target_date = datetime.fromisoformat(target_meta['extracted_date'])
                    date_window_start = (target_date - timedelta(days=7)).isoformat()
                    date_window_end = (target_date + timedelta(days=7)).isoformat()
                except:
                    pass
            
            if date_window_start and date_window_end:
                cursor.execute("""
                    SELECT gdrive_id, extracted_date, extracted_time, participants,
                           title_normalized, metadata_json
                    FROM meeting_metadata
                    WHERE gdrive_id != ?
                      AND extracted_date >= ?
                      AND extracted_date <= ?
                """, (gdrive_id, date_window_start, date_window_end))
            else:
                cursor.execute("""
                    SELECT gdrive_id, extracted_date, extracted_time, participants,
                           title_normalized, metadata_json
                    FROM meeting_metadata
                    WHERE gdrive_id != ?
                """, (gdrive_id,))
            
            candidates = []
            for row in cursor.fetchall():
                candidate_meta = {
                    'gdrive_id': row[0],
                    'extracted_date': row[1],
                    'extracted_time': row[2],
                    'participants': row[3],
                    'title_normalized': row[4],
                    'metadata_json': row[5]
                }
                
                similarity, reason = self.compute_similarity(target_meta, candidate_meta)
                
                if similarity >= threshold:
                    candidates.append({
                        'gdrive_id': candidate_meta['gdrive_id'],
                        'similarity': similarity,
                        'reason': reason,
                        'metadata': candidate_meta
                    })
            
            # Sort by similarity
            candidates.sort(key=lambda x: x['similarity'], reverse=True)
            return candidates
            
        finally:
            conn.close()
    
    def create_cluster(self, primary_gdrive_id: str, members: List[Dict]) -> str:
        """Create new duplicate cluster"""
        conn = self._get_conn()
        try:
            cluster_id = f"dup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{primary_gdrive_id[:8]}"
            cursor = conn.cursor()
            
            # Calculate average confidence
            avg_confidence = sum(m['similarity'] for m in members) / len(members) if members else 0.0
            match_reason = members[0]['reason'] if members else "unknown"
            
            # Create cluster
            cursor.execute("""
                INSERT INTO duplicate_clusters
                (cluster_id, primary_gdrive_id, cluster_size, confidence_score,
                 match_reason, status, detected_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?)
            """, (
                cluster_id,
                primary_gdrive_id,
                len(members) + 1,  # +1 for primary
                avg_confidence,
                match_reason,
                datetime.now(timezone.utc).isoformat()
            ))
            
            # Add primary member
            cursor.execute("""
                INSERT INTO duplicate_members
                (cluster_id, gdrive_id, is_primary, similarity_score, added_at)
                VALUES (?, ?, 1, 1.0, ?)
            """, (cluster_id, primary_gdrive_id, datetime.now(timezone.utc).isoformat()))
            
            # Add other members
            for member in members:
                cursor.execute("""
                    INSERT INTO duplicate_members
                    (cluster_id, gdrive_id, is_primary, similarity_score, added_at)
                    VALUES (?, ?, 0, ?, ?)
                """, (
                    cluster_id,
                    member['gdrive_id'],
                    member['similarity'],
                    datetime.now(timezone.utc).isoformat()
                ))
            
            conn.commit()
            logger.info(f"✓ Created cluster {cluster_id} with {len(members) + 1} members")
            return cluster_id
            
        except Exception as e:
            logger.error(f"Failed to create cluster: {e}")
            return None
        finally:
            conn.close()
    
    def scan_queue(self, limit: Optional[int] = None, threshold: float = 0.80) -> Dict:
        """Process duplicate check queue"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # Get pending items
            if limit:
                cursor.execute("""
                    SELECT gdrive_id FROM duplicate_check_queue
                    WHERE check_status = 'pending'
                    ORDER BY queued_at
                    LIMIT ?
                """, (limit,))
            else:
                cursor.execute("""
                    SELECT gdrive_id FROM duplicate_check_queue
                    WHERE check_status = 'pending'
                    ORDER BY queued_at
                """)
            
            pending = [row[0] for row in cursor.fetchall()]
            
            stats = {
                'processed': 0,
                'duplicates_found': 0,
                'new_clusters': 0,
                'added_to_existing': 0,
                'no_duplicates': 0,
                'errors': 0
            }
            
            for gdrive_id in pending:
                try:
                    logger.info(f"Checking {gdrive_id}...")
                    
                    # Check if already in a cluster
                    cursor.execute("""
                        SELECT cluster_id FROM duplicate_members
                        WHERE gdrive_id = ?
                    """, (gdrive_id,))
                    existing_cluster = cursor.fetchone()
                    
                    if existing_cluster:
                        logger.info(f"  Already in cluster {existing_cluster[0]}")
                        cursor.execute("""
                            UPDATE duplicate_check_queue
                            SET check_status = 'checked', checked_at = ?, result = 'existing_cluster'
                            WHERE gdrive_id = ?
                        """, (datetime.now(timezone.utc).isoformat(), gdrive_id))
                        stats['processed'] += 1
                        continue
                    
                    # Find duplicates
                    duplicates = self.find_duplicates(gdrive_id, threshold)
                    
                    if duplicates:
                        logger.info(f"  Found {len(duplicates)} potential duplicates")
                        cluster_id = self.create_cluster(gdrive_id, duplicates)
                        if cluster_id:
                            stats['new_clusters'] += 1
                            stats['duplicates_found'] += len(duplicates)
                            result = f"created_cluster:{cluster_id}"
                        else:
                            result = "error_creating_cluster"
                            stats['errors'] += 1
                    else:
                        logger.info(f"  No duplicates found")
                        result = "no_duplicates"
                        stats['no_duplicates'] += 1
                    
                    # Update queue status
                    cursor.execute("""
                        UPDATE duplicate_check_queue
                        SET check_status = 'checked', checked_at = ?, result = ?
                        WHERE gdrive_id = ?
                    """, (datetime.now(timezone.utc).isoformat(), result, gdrive_id))
                    
                    stats['processed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error checking {gdrive_id}: {e}")
                    cursor.execute("""
                        UPDATE duplicate_check_queue
                        SET check_status = 'error', checked_at = ?, result = ?
                        WHERE gdrive_id = ?
                    """, (datetime.now(timezone.utc).isoformat(), str(e), gdrive_id))
                    stats['errors'] += 1
                
                conn.commit()
            
            return stats
            
        finally:
            conn.close()
    
    def get_clusters(self, status: str = 'active') -> List[Dict]:
        """Get duplicate clusters"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cluster_id, primary_gdrive_id, cluster_size, confidence_score,
                       match_reason, status, detected_at
                FROM duplicate_clusters
                WHERE status = ?
                ORDER BY detected_at DESC
            """, (status,))
            
            clusters = []
            for row in cursor.fetchall():
                cluster_id = row[0]
                
                # Get members
                cursor.execute("""
                    SELECT dm.gdrive_id, dm.is_primary, dm.similarity_score,
                           mm.meeting_folder, mm.extracted_date, mm.participants
                    FROM duplicate_members dm
                    JOIN meeting_metadata mm ON dm.gdrive_id = mm.gdrive_id
                    WHERE dm.cluster_id = ?
                    ORDER BY dm.is_primary DESC, dm.similarity_score DESC
                """, (cluster_id,))
                
                members = []
                for member_row in cursor.fetchall():
                    members.append({
                        'gdrive_id': member_row[0],
                        'is_primary': bool(member_row[1]),
                        'similarity': member_row[2],
                        'folder': member_row[3],
                        'date': member_row[4],
                        'participants': member_row[5]
                    })
                
                clusters.append({
                    'cluster_id': cluster_id,
                    'primary_gdrive_id': row[1],
                    'size': row[2],
                    'confidence': row[3],
                    'reason': row[4],
                    'status': row[5],
                    'detected_at': row[6],
                    'members': members
                })
            
            return clusters
            
        finally:
            conn.close()
    
    def resolve_cluster(self, cluster_id: str, keep_gdrive_id: str, action: str = 'merged') -> bool:
        """Mark cluster as resolved"""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            # Update cluster
            cursor.execute("""
                UPDATE duplicate_clusters
                SET status = 'resolved',
                    resolved_at = ?,
                    resolution_action = ?,
                    primary_gdrive_id = ?
                WHERE cluster_id = ?
            """, (
                datetime.now(timezone.utc).isoformat(),
                action,
                keep_gdrive_id,
                cluster_id
            ))
            
            # Update primary flag
            cursor.execute("""
                UPDATE duplicate_members
                SET is_primary = 0
                WHERE cluster_id = ?
            """, (cluster_id,))
            
            cursor.execute("""
                UPDATE duplicate_members
                SET is_primary = 1
                WHERE cluster_id = ? AND gdrive_id = ?
            """, (cluster_id, keep_gdrive_id))
            
            conn.commit()
            logger.info(f"✓ Resolved cluster {cluster_id}, kept {keep_gdrive_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resolve cluster: {e}")
            return False
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Meeting Duplicate Manager")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Queue command
    queue_parser = subparsers.add_parser('queue', help='Queue meetings for duplicate checking')
    queue_group = queue_parser.add_mutually_exclusive_group()
    queue_group.add_argument('--all', action='store_true', help='Queue all meetings')
    queue_group.add_argument('--recent', type=int, metavar='DAYS', help='Queue meetings from last N days')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Process duplicate check queue')
    scan_parser.add_argument('--limit', type=int, help='Max meetings to check')
    scan_parser.add_argument('--threshold', type=float, default=0.80, help='Similarity threshold (0.0-1.0)')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Show duplicate clusters')
    report_parser.add_argument('--status', default='active', help='Cluster status filter')
    report_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check specific meeting')
    check_parser.add_argument('gdrive_id', help='Google Drive ID')
    check_parser.add_argument('--threshold', type=float, default=0.80, help='Similarity threshold')
    
    # Resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Resolve duplicate cluster')
    resolve_parser.add_argument('cluster_id', help='Cluster ID')
    resolve_parser.add_argument('--keep', required=True, help='Google Drive ID to keep')
    resolve_parser.add_argument('--action', default='merged', help='Resolution action')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MeetingDuplicateManager()
    
    if args.command == 'queue':
        # Index and queue meetings
        meeting_folders = [f for f in MEETINGS_ROOT.iterdir() if f.is_dir() and f.name.startswith('2025-')]
        
        if args.recent:
            cutoff = datetime.now(timezone.utc) - timedelta(days=args.recent)
            meeting_folders = [f for f in meeting_folders if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) > cutoff]
        
        indexed = 0
        queued_ids = []
        
        for folder in meeting_folders:
            metadata = manager.extract_metadata(folder)
            if metadata:
                if manager.index_meeting(metadata):
                    queued_ids.append(metadata['gdrive_id'])
                    indexed += 1
        
        queued = manager.queue_for_check(queued_ids)
        print(f"✓ Indexed {indexed} meetings, queued {queued} for checking")
    
    elif args.command == 'scan':
        print(f"Processing queue (limit: {args.limit or 'none'}, threshold: {args.threshold})...\n")
        stats = manager.scan_queue(args.limit, args.threshold)
        
        print("=== Duplicate Scan Results ===")
        print(f"Processed: {stats['processed']}")
        print(f"Duplicates found: {stats['duplicates_found']}")
        print(f"New clusters created: {stats['new_clusters']}")
        print(f"Added to existing clusters: {stats['added_to_existing']}")
        print(f"No duplicates: {stats['no_duplicates']}")
        print(f"Errors: {stats['errors']}")
    
    elif args.command == 'report':
        clusters = manager.get_clusters(args.status)
        
        if args.json:
            print(json.dumps(clusters, indent=2))
        else:
            print(f"\n=== Duplicate Clusters ({len(clusters)} total) ===\n")
            for cluster in clusters:
                print(f"Cluster: {cluster['cluster_id']}")
                print(f"  Status: {cluster['status']}")
                print(f"  Size: {cluster['size']} meetings")
                print(f"  Confidence: {cluster['confidence']:.1%}")
                print(f"  Reason: {cluster['reason']}")
                print(f"  Primary: {cluster['primary_gdrive_id']}")
                print(f"  Members:")
                for member in cluster['members']:
                    primary_mark = " [PRIMARY]" if member['is_primary'] else ""
                    print(f"    - {member['gdrive_id']}{primary_mark}")
                    print(f"      {Path(member['folder']).name}")
                    print(f"      Date: {member['date']}, Participants: {member['participants']}")
                print()
    
    elif args.command == 'check':
        duplicates = manager.find_duplicates(args.gdrive_id, args.threshold)
        result = {
            'gdrive_id': args.gdrive_id,
            'threshold': args.threshold,
            'duplicates_found': len(duplicates),
            'duplicates': duplicates
        }
        print(json.dumps(result, indent=2))
    
    elif args.command == 'resolve':
        success = manager.resolve_cluster(args.cluster_id, args.keep, args.action)
        if success:
            print(f"✓ Cluster {args.cluster_id} resolved, kept {args.keep}")
        else:
            print(f"✗ Failed to resolve cluster")


if __name__ == "__main__":
    main()





