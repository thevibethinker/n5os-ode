#!/usr/bin/env python3
"""
Block Registry Database Access Layer

Provides clean API for interacting with blocks.db
All operations are transaction-safe and return structured data.

Usage:
    from Intelligence.scripts import block_db
    
    # Get a block
    block = block_db.get_block("B01")
    
    # Log a generation
    gen_id = block_db.log_generation(
        block_id="B01",
        meeting_id="M123", 
        status="pending"
    )
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

# Database path
DB_PATH = Path("/home/workspace/Intelligence/blocks.db")


@contextmanager
def get_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ============================================================================
# BLOCKS TABLE OPERATIONS
# ============================================================================

def get_block(block_id: str) -> Optional[Dict]:
    """Get block metadata by ID"""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM blocks WHERE block_id = ?", 
            (block_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def list_blocks(
    category: Optional[str] = None, 
    status: str = "active"
) -> List[Dict]:
    """List blocks, optionally filtered by category/status"""
    with get_connection() as conn:
        if category:
            cursor = conn.execute(
                "SELECT * FROM blocks WHERE category = ? AND status = ? ORDER BY block_number",
                (category, status)
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM blocks WHERE status = ? ORDER BY block_number",
                (status,)
            )
        return [dict(row) for row in cursor.fetchall()]


def add_block(
    block_id: str,
    block_number: int,
    name: str,
    category: str,
    description: str = "",
    input_requirements: str = "",
    output_format: str = "",
    validation_rubric: Optional[Dict] = None,
    status: str = "active"
) -> bool:
    """Add a new block to registry"""
    with get_connection() as conn:
        rubric_json = json.dumps(validation_rubric) if validation_rubric else None
        conn.execute(
            """INSERT INTO blocks 
            (block_id, block_number, name, category, description, 
             input_requirements, output_format, validation_rubric, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (block_id, block_number, name, category, description,
             input_requirements, output_format, rubric_json, status)
        )
        return True


def update_block_stats(
    block_id: str,
    success: bool,
    generation_time: Optional[datetime] = None
) -> None:
    """Update block statistics after a generation"""
    with get_connection() as conn:
        # Get current stats
        cursor = conn.execute(
            "SELECT total_generations, success_rate FROM blocks WHERE block_id = ?",
            (block_id,)
        )
        row = cursor.fetchone()
        if not row:
            return
        
        total = row['total_generations']
        rate = row['success_rate']
        
        # Calculate new stats
        new_total = total + 1
        successes = int(total * (rate / 100.0))
        if success:
            successes += 1
        new_rate = (successes / new_total) * 100.0
        
        # Update
        update_time = generation_time or datetime.now()
        conn.execute(
            """UPDATE blocks 
            SET total_generations = ?, 
                success_rate = ?,
                last_generated_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE block_id = ?""",
            (new_total, new_rate, update_time.isoformat(), block_id)
        )


# ============================================================================
# GENERATION_HISTORY TABLE OPERATIONS
# ============================================================================

def log_generation(
    block_id: str,
    meeting_id: str,
    status: str,
    attempt_number: int = 1,
    input_context: Optional[Dict] = None,
    output_path: Optional[str] = None,
    generation_time_ms: Optional[int] = None,
    model_used: Optional[str] = None,
    token_count: Optional[int] = None,
    error_message: Optional[str] = None
) -> int:
    """Log a generation attempt, returns generation_id"""
    with get_connection() as conn:
        context_json = json.dumps(input_context) if input_context else None
        cursor = conn.execute(
            """INSERT INTO generation_history
            (block_id, meeting_id, status, attempt_number, input_context,
             output_path, generation_time_ms, model_used, token_count, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (block_id, meeting_id, status, attempt_number, context_json,
             output_path, generation_time_ms, model_used, token_count, error_message)
        )
        return cursor.lastrowid


def update_generation(
    generation_id: int,
    status: Optional[str] = None,
    output_path: Optional[str] = None,
    generation_time_ms: Optional[int] = None,
    error_message: Optional[str] = None
) -> None:
    """Update an existing generation record"""
    with get_connection() as conn:
        updates = []
        params = []
        
        if status:
            updates.append("status = ?")
            params.append(status)
        if output_path:
            updates.append("output_path = ?")
            params.append(output_path)
        if generation_time_ms is not None:
            updates.append("generation_time_ms = ?")
            params.append(generation_time_ms)
        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)
        
        if status in ('success', 'failed'):
            updates.append("completed_at = CURRENT_TIMESTAMP")
        
        if updates:
            params.append(generation_id)
            conn.execute(
                f"UPDATE generation_history SET {', '.join(updates)} WHERE generation_id = ?",
                tuple(params)
            )


def get_generation(generation_id: int) -> Optional[Dict]:
    """Get generation record by ID"""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM generation_history WHERE generation_id = ?",
            (generation_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_generations_for_meeting(meeting_id: str) -> List[Dict]:
    """Get all generations for a meeting"""
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT * FROM generation_history 
            WHERE meeting_id = ? 
            ORDER BY created_at DESC""",
            (meeting_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# VALIDATION_RESULTS TABLE OPERATIONS
# ============================================================================

def log_validation(
    generation_id: int,
    block_id: str,
    validation_type: str,
    status: str,
    score: Optional[float] = None,
    criteria_checked: Optional[List] = None,
    failures: Optional[List] = None,
    warnings: Optional[List] = None,
    validator_version: str = "1.0"
) -> int:
    """Log a validation result, returns validation_id"""
    with get_connection() as conn:
        criteria_json = json.dumps(criteria_checked) if criteria_checked else None
        failures_json = json.dumps(failures) if failures else None
        warnings_json = json.dumps(warnings) if warnings else None
        
        cursor = conn.execute(
            """INSERT INTO validation_results
            (generation_id, block_id, validation_type, status, score,
             criteria_checked, failures, warnings, validator_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (generation_id, block_id, validation_type, status, score,
             criteria_json, failures_json, warnings_json, validator_version)
        )
        return cursor.lastrowid


def get_validation_results(generation_id: int) -> List[Dict]:
    """Get all validation results for a generation"""
    with get_connection() as conn:
        cursor = conn.execute(
            """SELECT * FROM validation_results 
            WHERE generation_id = ? 
            ORDER BY created_at""",
            (generation_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# QUALITY_SAMPLES TABLE OPERATIONS
# ============================================================================

def add_quality_sample(
    block_id: str,
    meeting_id: str,
    sample_type: str,
    input_snapshot: Dict,
    output_snapshot: str,
    generation_id: Optional[int] = None,
    validation_score: Optional[float] = None,
    notes: str = ""
) -> int:
    """Add a quality sample for regression testing"""
    with get_connection() as conn:
        input_json = json.dumps(input_snapshot)
        cursor = conn.execute(
            """INSERT INTO quality_samples
            (block_id, meeting_id, generation_id, sample_type,
             input_snapshot, output_snapshot, validation_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (block_id, meeting_id, generation_id, sample_type,
             input_json, output_snapshot, validation_score, notes)
        )
        return cursor.lastrowid


def get_quality_samples(
    block_id: str,
    sample_type: Optional[str] = None
) -> List[Dict]:
    """Get quality samples for a block"""
    with get_connection() as conn:
        if sample_type:
            cursor = conn.execute(
                """SELECT * FROM quality_samples 
                WHERE block_id = ? AND sample_type = ?
                ORDER BY validation_score DESC""",
                (block_id, sample_type)
            )
        else:
            cursor = conn.execute(
                """SELECT * FROM quality_samples 
                WHERE block_id = ?
                ORDER BY sample_type, validation_score DESC""",
                (block_id,)
            )
        return [dict(row) for row in cursor.fetchall()]


def update_sample_test_results(
    sample_id: int,
    passed: bool
) -> None:
    """Update regression test results for a sample"""
    with get_connection() as conn:
        field = "test_pass_count" if passed else "test_fail_count"
        conn.execute(
            f"""UPDATE quality_samples 
            SET {field} = {field} + 1,
                last_tested_at = CURRENT_TIMESTAMP
            WHERE sample_id = ?""",
            (sample_id,)
        )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_stats() -> Dict:
    """Get overall database statistics"""
    with get_connection() as conn:
        stats = {}
        
        # Block counts
        cursor = conn.execute("SELECT COUNT(*) as count FROM blocks")
        stats['total_blocks'] = cursor.fetchone()['count']
        
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM blocks WHERE status = 'active'"
        )
        stats['active_blocks'] = cursor.fetchone()['count']
        
        # Generation counts
        cursor = conn.execute("SELECT COUNT(*) as count FROM generation_history")
        stats['total_generations'] = cursor.fetchone()['count']
        
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM generation_history WHERE status = 'success'"
        )
        stats['successful_generations'] = cursor.fetchone()['count']
        
        # Quality samples
        cursor = conn.execute("SELECT COUNT(*) as count FROM quality_samples")
        stats['quality_samples'] = cursor.fetchone()['count']
        
        return stats


def verify_database() -> Dict:
    """Verify database structure and return info"""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row['name'] for row in cursor.fetchall()]
        
        result = {
            'database_path': str(DB_PATH),
            'database_exists': DB_PATH.exists(),
            'tables': tables,
            'expected_tables': ['blocks', 'generation_history', 'validation_results', 'quality_samples']
        }
        
        result['valid'] = set(result['expected_tables']).issubset(set(tables))
        
        return result


if __name__ == "__main__":
    # Quick verification when run directly
    info = verify_database()
    print("Database Verification:")
    print(f"  Path: {info['database_path']}")
    print(f"  Exists: {info['database_exists']}")
    print(f"  Tables: {', '.join(info['tables'])}")
    print(f"  Valid: {info['valid']}")
    
    if info['valid']:
        stats = get_stats()
        print("\nDatabase Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
