#!/usr/bin/env python3
"""
Post-Tick Hook for Relationship Intelligence OS

Executes after meeting pipeline tick completion to process meetings through
the promotion gate and write approved intelligence to semantic memory and graph.

Key Features:
- Hooks into meeting tick() completion
- Idempotent processing with unique keys
- Single writer path to brain.db + graph
- Manifest state tracking with promotion transitions
- Error recovery and retry logic
"""

import json
import sqlite3
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import sys
import logging

# Add build artifacts to path
BUILD_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BUILD_DIR / "artifacts"))

from promotion_gate_engine import PromotionGateEngine, ScoringInput

logger = logging.getLogger(__name__)

# Database paths
BRAIN_DB = Path("/home/workspace/N5/cognition/brain.db")
MEETINGS_DB = Path("/home/workspace/N5/data/meeting_registry.db")
HOOK_STATE_DB = Path("/home/workspace/N5/data/promotion_hook_state.db")

class PromotionHookError(Exception):
    """Base exception for promotion hook errors."""
    pass

class IdempotencyManager:
    """Manages idempotency keys and duplicate processing prevention."""
    
    def __init__(self, state_db_path: Path):
        self.state_db_path = state_db_path
        self._ensure_state_db()
    
    def _ensure_state_db(self):
        """Ensure state database exists with required schema."""
        self.state_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS promotion_runs (
                    idempotency_key TEXT PRIMARY KEY,
                    meeting_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    result_summary TEXT,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS promotion_writes (
                    write_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL,
                    target_system TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    entity_id TEXT,
                    write_status TEXT NOT NULL DEFAULT 'pending',
                    write_timestamp TEXT,
                    error_message TEXT,
                    FOREIGN KEY (idempotency_key) REFERENCES promotion_runs(idempotency_key)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_promotion_runs_meeting_id 
                ON promotion_runs(meeting_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_promotion_writes_idem_key
                ON promotion_writes(idempotency_key)
            """)
    
    def generate_idempotency_key(self, meeting_id: str, run_context: str = "") -> str:
        """Generate unique idempotency key for a meeting processing run."""
        # Include meeting_id and run context (e.g., timestamp, tick ID)
        key_input = f"{meeting_id}:{run_context}:{datetime.now(timezone.utc).isoformat()}"
        return hashlib.sha256(key_input.encode()).hexdigest()[:16]
    
    def start_run(self, meeting_id: str, run_context: str = "") -> str:
        """Start a new promotion run, returning idempotency key."""
        idempotency_key = self.generate_idempotency_key(meeting_id, run_context)
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{idempotency_key[:8]}"
        
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                INSERT INTO promotion_runs 
                (idempotency_key, meeting_id, run_id, started_at, status)
                VALUES (?, ?, ?, ?, 'running')
            """, (idempotency_key, meeting_id, run_id, datetime.now(timezone.utc).isoformat()))
        
        logger.info(f"Started promotion run {run_id} for meeting {meeting_id}")
        return idempotency_key
    
    def is_already_processed(self, meeting_id: str, check_window_hours: int = 24) -> bool:
        """Check if meeting was successfully processed in recent window."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=check_window_hours)
        
        with sqlite3.connect(self.state_db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM promotion_runs 
                WHERE meeting_id = ? 
                  AND status = 'completed' 
                  AND datetime(completed_at) > ?
            """, (meeting_id, cutoff.isoformat()))
            
            return cursor.fetchone()[0] > 0
    
    def complete_run(self, idempotency_key: str, result_summary: str = ""):
        """Mark a promotion run as completed."""
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                UPDATE promotion_runs 
                SET completed_at = ?, status = 'completed', result_summary = ?
                WHERE idempotency_key = ?
            """, (datetime.now(timezone.utc).isoformat(), result_summary, idempotency_key))
        
        logger.info(f"Completed promotion run {idempotency_key}")
    
    def fail_run(self, idempotency_key: str, error_message: str):
        """Mark a promotion run as failed."""
        with sqlite3.connect(self.state_db_path) as conn:
            # Increment retry count and mark as failed
            conn.execute("""
                UPDATE promotion_runs 
                SET status = 'failed', error_message = ?, 
                    retry_count = retry_count + 1
                WHERE idempotency_key = ?
            """, (error_message, idempotency_key))
        
        logger.error(f"Failed promotion run {idempotency_key}: {error_message}")
    
    def record_write(self, idempotency_key: str, target_system: str, 
                    operation_type: str, entity_id: str = None) -> str:
        """Record a write operation for tracking."""
        write_id = f"write_{target_system}_{operation_type}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
        
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                INSERT INTO promotion_writes 
                (write_id, idempotency_key, target_system, operation_type, entity_id)
                VALUES (?, ?, ?, ?, ?)
            """, (write_id, idempotency_key, target_system, operation_type, entity_id))
        
        return write_id
    
    def complete_write(self, write_id: str, entity_id: str = None):
        """Mark a write operation as completed."""
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                UPDATE promotion_writes 
                SET write_status = 'completed', write_timestamp = ?, entity_id = ?
                WHERE write_id = ?
            """, (datetime.now(timezone.utc).isoformat(), entity_id, write_id))
    
    def fail_write(self, write_id: str, error_message: str):
        """Mark a write operation as failed."""
        with sqlite3.connect(self.state_db_path) as conn:
            conn.execute("""
                UPDATE promotion_writes 
                SET write_status = 'failed', error_message = ?
                WHERE write_id = ?
            """, (error_message, write_id))


class PromotionWriter:
    """Single writer path for semantic memory and graph writes."""
    
    def __init__(self, idempotency_manager: IdempotencyManager):
        self.idem_manager = idempotency_manager
        self._ensure_brain_db()
        self._ensure_graph_tables()
    
    def _ensure_brain_db(self):
        """Ensure brain.db exists and has required tables."""
        if not BRAIN_DB.exists():
            BRAIN_DB.parent.mkdir(parents=True, exist_ok=True)
            
        # Basic brain.db tables will be created by existing systems
        # We just ensure it exists
        with sqlite3.connect(BRAIN_DB) as conn:
            # Test connection and ensure basic functionality
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    
    def _ensure_graph_tables(self):
        """Ensure graph tables exist in brain.db."""
        with sqlite3.connect(BRAIN_DB) as conn:
            # Relationship edges
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationship_edges (
                    edge_id TEXT PRIMARY KEY,
                    source_person TEXT NOT NULL,
                    target_person TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    strength REAL DEFAULT 0.5,
                    confidence REAL DEFAULT 0.5,
                    evidence TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    source_meeting_id TEXT,
                    UNIQUE(source_person, target_person, relationship_type)
                )
            """)
            
            # Organization edges  
            conn.execute("""
                CREATE TABLE IF NOT EXISTS org_edges (
                    edge_id TEXT PRIMARY KEY,
                    person TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    role TEXT,
                    authority_level TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    confidence REAL DEFAULT 0.5,
                    evidence TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    source_meeting_id TEXT,
                    UNIQUE(person, organization, role)
                )
            """)
            
            # Commitment tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commitment_edges (
                    edge_id TEXT PRIMARY KEY,
                    person TEXT NOT NULL,
                    commitment_text TEXT NOT NULL,
                    due_date TEXT,
                    status TEXT DEFAULT 'open',
                    confidence REAL DEFAULT 0.5,
                    evidence TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    source_meeting_id TEXT
                )
            """)
    
    def write_promotion_event(self, idempotency_key: str, promotion_event: Dict[str, Any]) -> Dict[str, List[str]]:
        """Write promotion event to appropriate systems based on routing."""
        
        results = {
            'semantic_memory': [],
            'graph_edges': [],
            'crm_projection': [],
            'deliverables_db': []
        }
        
        routing = promotion_event.get('routing', {})
        candidate_type = promotion_event.get('candidate_type', '')
        candidate_data = promotion_event.get('candidate_data', {})
        
        # Write to semantic memory if routed
        if routing.get('semantic_memory', False):
            write_id = self.idem_manager.record_write(
                idempotency_key, 'semantic_memory', 'entity_upsert'
            )
            try:
                entity_id = self._write_to_semantic_memory(promotion_event)
                self.idem_manager.complete_write(write_id, entity_id)
                results['semantic_memory'].append(entity_id)
            except Exception as e:
                self.idem_manager.fail_write(write_id, str(e))
                raise PromotionHookError(f"Semantic memory write failed: {e}")
        
        # Write to graph edges if routed
        if routing.get('graph_edges', False):
            write_id = self.idem_manager.record_write(
                idempotency_key, 'graph_edges', f'{candidate_type}_edge'
            )
            try:
                edge_ids = self._write_to_graph(promotion_event)
                self.idem_manager.complete_write(write_id, ','.join(edge_ids))
                results['graph_edges'].extend(edge_ids)
            except Exception as e:
                self.idem_manager.fail_write(write_id, str(e))
                raise PromotionHookError(f"Graph write failed: {e}")
        
        # Write to CRM projection if routed
        if routing.get('crm_projection', False):
            write_id = self.idem_manager.record_write(
                idempotency_key, 'crm_projection', 'profile_update'
            )
            try:
                profile_ids = self._write_to_crm_projection(promotion_event)
                self.idem_manager.complete_write(write_id, ','.join(profile_ids))
                results['crm_projection'].extend(profile_ids)
            except Exception as e:
                self.idem_manager.fail_write(write_id, str(e))
                raise PromotionHookError(f"CRM projection write failed: {e}")
        
        # Write to deliverables DB if routed
        if routing.get('deliverables_db', False):
            write_id = self.idem_manager.record_write(
                idempotency_key, 'deliverables_db', 'deliverable_record'
            )
            try:
                deliverable_ids = self._write_to_deliverables_db(promotion_event)
                self.idem_manager.complete_write(write_id, ','.join(deliverable_ids))
                results['deliverables_db'].extend(deliverable_ids)
            except Exception as e:
                self.idem_manager.fail_write(write_id, str(e))
                raise PromotionHookError(f"Deliverables DB write failed: {e}")
        
        return results
    
    def _write_to_semantic_memory(self, promotion_event: Dict[str, Any]) -> str:
        """Write promotion event to semantic memory (brain.db resources)."""
        
        # For now, create a simple resource entry
        # In full implementation, this would integrate with existing semantic memory system
        candidate_data = promotion_event.get('candidate_data', {})
        candidate_type = promotion_event.get('candidate_type', '')
        
        resource_id = f"promoted_{candidate_type}_{promotion_event.get('event_id', 'unknown')}"
        
        with sqlite3.connect(BRAIN_DB) as conn:
            # Check if resources table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='resources'
            """)
            
            if cursor.fetchone():
                # Insert into existing resources table
                content = json.dumps(candidate_data)
                conn.execute("""
                    INSERT OR REPLACE INTO resources 
                    (id, content, created_at, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    resource_id,
                    content,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps({
                        'promotion_event_id': promotion_event.get('event_id'),
                        'candidate_type': candidate_type,
                        'tier': promotion_event.get('tier'),
                        'source_meeting_id': promotion_event.get('source_meeting_id')
                    })
                ))
            else:
                # Create a temporary promotion resources table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS promotion_resources (
                        id TEXT PRIMARY KEY,
                        candidate_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tier TEXT NOT NULL,
                        event_id TEXT NOT NULL,
                        source_meeting_id TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.execute("""
                    INSERT OR REPLACE INTO promotion_resources
                    (id, candidate_type, content, tier, event_id, source_meeting_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    resource_id,
                    candidate_type,
                    json.dumps(candidate_data),
                    promotion_event.get('tier', 'C'),
                    promotion_event.get('event_id', ''),
                    promotion_event.get('source_meeting_id', '')
                ))
        
        return resource_id
    
    def _write_to_graph(self, promotion_event: Dict[str, Any]) -> List[str]:
        """Write promotion event to graph edges."""
        
        candidate_type = promotion_event.get('candidate_type', '')
        candidate_data = promotion_event.get('candidate_data', {})
        source_meeting_id = promotion_event.get('source_meeting_id', '')
        edge_ids = []
        
        with sqlite3.connect(BRAIN_DB) as conn:
            if candidate_type == 'relationship_delta':
                # Write relationship edge
                edge_id = f"rel_{source_meeting_id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
                
                conn.execute("""
                    INSERT OR REPLACE INTO relationship_edges
                    (edge_id, source_person, target_person, relationship_type, 
                     strength, confidence, evidence, source_meeting_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    edge_id,
                    candidate_data.get('person', ''),
                    candidate_data.get('other_person', 'V'),  # Default to V as other person
                    candidate_data.get('delta_type', 'professional'),
                    candidate_data.get('strength', 0.5),
                    candidate_data.get('confidence', 0.5),
                    json.dumps(candidate_data.get('evidence', {})),
                    source_meeting_id
                ))
                edge_ids.append(edge_id)
            
            elif candidate_type == 'org_delta':
                # Write organization edge
                edge_id = f"org_{source_meeting_id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
                
                conn.execute("""
                    INSERT OR REPLACE INTO org_edges
                    (edge_id, person, organization, role, authority_level,
                     confidence, evidence, source_meeting_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    edge_id,
                    candidate_data.get('person', ''),
                    candidate_data.get('organization', ''),
                    candidate_data.get('role', ''),
                    candidate_data.get('authority_level', ''),
                    candidate_data.get('confidence', 0.5),
                    json.dumps(candidate_data.get('evidence', {})),
                    source_meeting_id
                ))
                edge_ids.append(edge_id)
            
            elif candidate_type == 'deliverable_record':
                # Write commitment edge if deliverable has commitment details
                commitment = candidate_data.get('commitment_details', {})
                if commitment:
                    edge_id = f"commit_{source_meeting_id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO commitment_edges
                        (edge_id, person, commitment_text, due_date, status,
                         confidence, evidence, source_meeting_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        edge_id,
                        commitment.get('owner', ''),
                        commitment.get('deliverable', candidate_data.get('deliverable', '')),
                        commitment.get('due_date', ''),
                        candidate_data.get('status', 'identified'),
                        candidate_data.get('confidence', 0.5),
                        json.dumps(candidate_data.get('evidence', {})),
                        source_meeting_id
                    ))
                    edge_ids.append(edge_id)
        
        return edge_ids
    
    def _write_to_crm_projection(self, promotion_event: Dict[str, Any]) -> List[str]:
        """Write promotion event to CRM projection."""
        
        # For now, create placeholder CRM projection entries
        # In full implementation, this would update the actual CRM system
        candidate_data = promotion_event.get('candidate_data', {})
        profile_ids = []
        
        with sqlite3.connect(BRAIN_DB) as conn:
            # Create CRM projection table if needed
            conn.execute("""
                CREATE TABLE IF NOT EXISTS crm_projections (
                    projection_id TEXT PRIMARY KEY,
                    person TEXT NOT NULL,
                    organization TEXT,
                    projection_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source_meeting_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(person, projection_type, source_meeting_id)
                )
            """)
            
            # Extract person and org information
            person = candidate_data.get('person', '')
            organization = candidate_data.get('organization', '')
            
            if person:
                projection_id = f"crm_person_{person}_{promotion_event.get('source_meeting_id', '')}"
                
                conn.execute("""
                    INSERT OR REPLACE INTO crm_projections
                    (projection_id, person, organization, projection_type, content, source_meeting_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    projection_id,
                    person,
                    organization,
                    'person_intelligence',
                    json.dumps(candidate_data),
                    promotion_event.get('source_meeting_id', '')
                ))
                profile_ids.append(projection_id)
        
        return profile_ids
    
    def _write_to_deliverables_db(self, promotion_event: Dict[str, Any]) -> List[str]:
        """Write promotion event to deliverables database."""
        
        candidate_data = promotion_event.get('candidate_data', {})
        deliverable_ids = []
        
        with sqlite3.connect(BRAIN_DB) as conn:
            # Create deliverables table if needed
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deliverables (
                    deliverable_id TEXT PRIMARY KEY,
                    client_scope TEXT,
                    deliverable_text TEXT NOT NULL,
                    status TEXT DEFAULT 'identified',
                    owner TEXT,
                    due_date TEXT,
                    similarity_score REAL,
                    content TEXT NOT NULL,
                    source_meeting_id TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Extract deliverable information
            deliverable_id = f"deliv_{promotion_event.get('source_meeting_id', '')}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
            
            commitment = candidate_data.get('commitment_details', {})
            
            conn.execute("""
                INSERT OR REPLACE INTO deliverables
                (deliverable_id, client_scope, deliverable_text, status, owner,
                 due_date, content, source_meeting_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deliverable_id,
                candidate_data.get('client_scope', ''),
                commitment.get('deliverable', candidate_data.get('deliverable', '')),
                candidate_data.get('status', 'identified'),
                commitment.get('owner', ''),
                commitment.get('due_date', ''),
                json.dumps(candidate_data),
                promotion_event.get('source_meeting_id', '')
            ))
            deliverable_ids.append(deliverable_id)
        
        return deliverable_ids


class PostTickHook:
    """Main post-tick hook that orchestrates promotion processing."""
    
    def __init__(self):
        self.idempotency_manager = IdempotencyManager(HOOK_STATE_DB)
        self.promotion_writer = PromotionWriter(self.idempotency_manager)
        self.promotion_engine = PromotionGateEngine()
    
    def process_meeting_batch(self, meeting_folders: List[Path], 
                            dry_run: bool = False) -> Dict[str, Any]:
        """Process a batch of meetings through the promotion pipeline."""
        
        results = {
            'processed': 0,
            'promoted': 0,
            'archived': 0,
            'errors': 0,
            'meetings': []
        }
        
        for meeting_folder in meeting_folders:
            try:
                result = self.process_single_meeting(meeting_folder, dry_run)
                results['meetings'].append(result)
                results['processed'] += 1
                
                if result.get('promoted_events', 0) > 0:
                    results['promoted'] += 1
                
                if result.get('status') == 'completed':
                    results['archived'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to process meeting {meeting_folder.name}: {e}")
                results['errors'] += 1
                results['meetings'].append({
                    'meeting_id': meeting_folder.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def process_single_meeting(self, meeting_folder: Path, 
                              dry_run: bool = False) -> Dict[str, Any]:
        """Process a single meeting through promotion pipeline."""
        
        meeting_id = meeting_folder.name
        logger.info(f"Processing meeting {meeting_id} (dry_run={dry_run})")
        
        # Check if already processed recently
        if self.idempotency_manager.is_already_processed(meeting_id):
            logger.info(f"Meeting {meeting_id} already processed recently, skipping")
            return {
                'meeting_id': meeting_id,
                'status': 'already_processed',
                'promoted_events': 0
            }
        
        # Read meeting manifest
        manifest_path = meeting_folder / "manifest.json"
        if not manifest_path.exists():
            raise PromotionHookError(f"No manifest.json found in {meeting_folder}")
        
        manifest = json.loads(manifest_path.read_text())
        
        # Check if meeting is in processed state
        if manifest.get('status') != 'processed':
            logger.info(f"Meeting {meeting_id} not in processed state, skipping promotion")
            return {
                'meeting_id': meeting_id,
                'status': 'not_ready',
                'promoted_events': 0
            }
        
        # Start idempotent run
        idempotency_key = self.idempotency_manager.start_run(
            meeting_id, f"post_tick_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
        )
        
        try:
            if dry_run:
                # Dry run: analyze what would be promoted
                candidates = self._extract_promotion_candidates(meeting_folder)
                promoted_count = len([c for c in candidates if self._would_promote(c)])
                
                self.idempotency_manager.complete_run(
                    idempotency_key, f"dry_run: {promoted_count} candidates would be promoted"
                )
                
                return {
                    'meeting_id': meeting_id,
                    'status': 'dry_run_completed',
                    'promoted_events': promoted_count,
                    'idempotency_key': idempotency_key
                }
            
            # Real run: extract candidates and process through promotion gate
            candidates = self._extract_promotion_candidates(meeting_folder)
            promoted_events = []
            
            for candidate in candidates:
                try:
                    # Process through promotion gate
                    scoring_input = self._create_scoring_input(candidate, manifest)
                    promotion_event = self.promotion_engine.process_candidate(scoring_input)
                    
                    # Write to systems if promoted
                    if promotion_event.get('tier') == 'A' or promotion_event.get('hard_override', {}).get('applied', False):
                        write_results = self.promotion_writer.write_promotion_event(
                            idempotency_key, promotion_event
                        )
                        promotion_event['write_results'] = write_results
                        promoted_events.append(promotion_event)
                
                except Exception as e:
                    logger.error(f"Failed to process candidate {candidate.get('type', 'unknown')}: {e}")
                    # Continue processing other candidates
            
            # Update meeting manifest with promotion state
            self._update_manifest_promotion_state(manifest_path, {
                'promotion_completed_at': datetime.now(timezone.utc).isoformat(),
                'promoted_events': len(promoted_events),
                'idempotency_key': idempotency_key,
                'status': 'promotion_completed'
            })
            
            # Mark run as completed
            self.idempotency_manager.complete_run(
                idempotency_key, f"promoted {len(promoted_events)} events"
            )
            
            return {
                'meeting_id': meeting_id,
                'status': 'completed',
                'promoted_events': len(promoted_events),
                'events': promoted_events,
                'idempotency_key': idempotency_key
            }
        
        except Exception as e:
            self.idempotency_manager.fail_run(idempotency_key, str(e))
            raise
    
    def _extract_promotion_candidates(self, meeting_folder: Path) -> List[Dict[str, Any]]:
        """Extract promotion candidates from meeting blocks."""
        
        candidates = []
        
        # Look for intelligence blocks that contain promotion candidates
        intelligence_blocks = [
            'B02_B05_COMMITMENTS_ACTIONS.md',
            'B03_DECISIONS.md', 
            'B08_STAKEHOLDER_INTELLIGENCE.md',
            'B06_BUSINESS_CONTEXT.md',
            'B32_THOUGHT_PROVOKING_IDEAS.md',
            'B33_DECISION_RATIONALE.md'
        ]
        
        for block_file in intelligence_blocks:
            block_path = meeting_folder / block_file
            if block_path.exists():
                block_content = block_path.read_text()
                
                # Extract candidates based on block type
                if 'B02_B05' in block_file:
                    candidates.extend(self._extract_deliverable_candidates(block_content, meeting_folder.name))
                elif 'B08' in block_file:
                    candidates.extend(self._extract_relationship_candidates(block_content, meeting_folder.name))
                elif 'B06' in block_file:
                    candidates.extend(self._extract_org_candidates(block_content, meeting_folder.name))
                elif 'B32' in block_file or 'B33' in block_file:
                    candidates.extend(self._extract_intelligence_candidates(block_content, meeting_folder.name))
        
        return candidates
    
    def _extract_deliverable_candidates(self, content: str, meeting_id: str) -> List[Dict[str, Any]]:
        """Extract deliverable candidates from commitments/actions block."""
        # Simplified extraction - real implementation would use LLM
        candidates = []
        
        lines = content.split('\n')
        current_deliverable = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                # This looks like a commitment/action
                deliverable_text = line[5:].strip()  # Remove checkbox
                
                candidate = {
                    'type': 'deliverable_record',
                    'data': {
                        'id': f"deliv_{meeting_id}_{len(candidates)}",
                        'deliverable': deliverable_text,
                        'status': 'committed' if '[x]' in line else 'identified',
                        'client_scope': meeting_id,  # Use meeting as scope
                        'commitment_details': {
                            'deliverable': deliverable_text,
                            'owner': 'V',  # Default owner
                            'due_date': ''  # Would extract from content
                        },
                        'confidence': 0.8,
                        'evidence': {
                            'quotes': [line],
                            'source_block': 'B02_B05_COMMITMENTS_ACTIONS'
                        }
                    },
                    'source_meeting_id': meeting_id
                }
                
                candidates.append(candidate)
        
        return candidates
    
    def _extract_relationship_candidates(self, content: str, meeting_id: str) -> List[Dict[str, Any]]:
        """Extract relationship candidates from stakeholder intelligence."""
        # Simplified extraction
        candidates = []
        
        # Look for relationship signals in content
        relationship_keywords = ['trust', 'rapport', 'relationship', 'connection', 'influence']
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if any(keyword in line.lower() for keyword in relationship_keywords):
                # Potential relationship delta
                
                # Try to extract person name (simplified)
                person = 'Unknown'
                for word in line.split():
                    if word.istitle() and len(word) > 2:
                        person = word
                        break
                
                candidate = {
                    'type': 'relationship_delta',
                    'data': {
                        'id': f"rel_{meeting_id}_{len(candidates)}",
                        'person': person,
                        'other_person': 'V',
                        'delta_type': 'professional',
                        'description': line,
                        'confidence': 0.6,
                        'evidence': {
                            'quotes': [line],
                            'source_block': 'B08_STAKEHOLDER_INTELLIGENCE'
                        }
                    },
                    'source_meeting_id': meeting_id
                }
                
                candidates.append(candidate)
        
        return candidates
    
    def _extract_org_candidates(self, content: str, meeting_id: str) -> List[Dict[str, Any]]:
        """Extract org candidates from business context."""
        # Simplified extraction
        candidates = []
        
        # Look for organization signals
        org_keywords = ['company', 'organization', 'team', 'department', 'priorities', 'strategy']
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if any(keyword in line.lower() for keyword in org_keywords):
                
                candidate = {
                    'type': 'org_delta',
                    'data': {
                        'id': f"org_{meeting_id}_{len(candidates)}",
                        'organization': 'Unknown',  # Would extract from content
                        'person': 'V',
                        'delta_type': 'strategic_context',
                        'description': line,
                        'confidence': 0.5,
                        'evidence': {
                            'quotes': [line],
                            'source_block': 'B06_BUSINESS_CONTEXT'
                        }
                    },
                    'source_meeting_id': meeting_id
                }
                
                candidates.append(candidate)
        
        return candidates
    
    def _extract_intelligence_candidates(self, content: str, meeting_id: str) -> List[Dict[str, Any]]:
        """Extract general intelligence candidates from idea blocks."""
        # Simplified extraction
        candidates = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 50:  # Substantial content
                candidate = {
                    'type': 'general_intelligence',
                    'data': {
                        'id': f"intel_{meeting_id}_{len(candidates)}",
                        'content': line,
                        'category': 'strategic_insight',
                        'confidence': 0.4,
                        'evidence': {
                            'quotes': [line],
                            'source_block': 'intelligence_block'
                        }
                    },
                    'source_meeting_id': meeting_id
                }
                
                candidates.append(candidate)
        
        return candidates
    
    def _would_promote(self, candidate: Dict[str, Any]) -> bool:
        """Check if candidate would be promoted (for dry run)."""
        # Simplified logic - deliverables are more likely to be promoted
        candidate_type = candidate.get('type', '')
        
        if candidate_type == 'deliverable_record':
            return True  # High probability of promotion
        elif candidate_type == 'relationship_delta':
            return candidate['data'].get('confidence', 0) > 0.7
        else:
            return candidate['data'].get('confidence', 0) > 0.8
    
    def _create_scoring_input(self, candidate: Dict[str, Any], manifest: Dict[str, Any]) -> ScoringInput:
        """Create scoring input for promotion gate."""
        
        return ScoringInput(
            candidate_type=candidate['type'],
            candidate_data=candidate['data'],
            source_meeting_id=candidate['source_meeting_id'],
            meeting_context={
                'participants': manifest.get('participants', []),
                'meeting_type': manifest.get('meeting_type', ''),
                'date': manifest.get('date', '')
            },
            conversation_id=f"con_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            processing_mode="production"
        )
    
    def _update_manifest_promotion_state(self, manifest_path: Path, promotion_data: Dict[str, Any]):
        """Update meeting manifest with promotion state."""
        
        manifest = json.loads(manifest_path.read_text())
        
        # Add promotion section
        manifest.setdefault('promotion', {}).update(promotion_data)
        
        # Add to timestamps
        manifest.setdefault('timestamps', {})['promotion_completed_at'] = promotion_data.get('promotion_completed_at')
        
        # Write back
        manifest_path.write_text(json.dumps(manifest, indent=2))


def execute_post_tick_hook(meeting_folders: List[str], dry_run: bool = False) -> Dict[str, Any]:
    """Execute the post-tick hook for a batch of meetings."""
    
    hook = PostTickHook()
    folder_paths = [Path(folder) for folder in meeting_folders]
    
    return hook.process_meeting_batch(folder_paths, dry_run)


# CLI interface for testing and integration
def main():
    """CLI interface for post-tick hook."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Post-Tick Promotion Hook')
    parser.add_argument('meetings', nargs='+', help='Meeting folder paths')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        result = execute_post_tick_hook(args.meetings, args.dry_run)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        logger.error(f"Hook execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())