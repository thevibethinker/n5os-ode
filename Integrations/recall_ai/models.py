"""
Recall.ai Calendar Integration - SQLite Models
"""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

try:
    from .config import RECALL_DB_PATH
except ImportError:
    # For standalone execution
    from config import RECALL_DB_PATH

logger = logging.getLogger(__name__)

# Database path from config
DB_PATH = RECALL_DB_PATH

class RecallDatabase:
    """Database interface for Recall.ai calendar integration."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create schema."""
        self.db_path = db_path or DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create scheduled_bots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_bots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bot_id TEXT UNIQUE,
                    calendar_event_id TEXT NOT NULL,
                    meeting_url TEXT NOT NULL,
                    meeting_title TEXT,
                    meeting_start DATETIME NOT NULL,
                    join_at DATETIME NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    error TEXT,
                    
                    UNIQUE(calendar_event_id, meeting_start)
                )
            ''')
            
            # Create indexes for scheduled_bots
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_bots_status ON scheduled_bots(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_bots_join_at ON scheduled_bots(join_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_bots_event_id ON scheduled_bots(calendar_event_id)')
            
            # Create bot_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    bot_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    status_code TEXT,
                    sub_code TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    payload JSON,
                    processed BOOLEAN DEFAULT FALSE,
                    error TEXT,
                    
                    FOREIGN KEY (bot_id) REFERENCES scheduled_bots(bot_id)
                )
            ''')
            
            # Create indexes for bot_events
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_events_bot_id ON bot_events(bot_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_events_type ON bot_events(event_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bot_events_timestamp ON bot_events(timestamp)')
            
            # Create sync_state table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sync_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_sync DATETIME,
                    last_event_time DATETIME,
                    sync_token TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database schema initialized successfully")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _dict_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert sqlite3.Row to dictionary."""
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}
    
    # Scheduled Bots CRUD Operations
    
    def create_scheduled_bot(self, calendar_event_id: str, meeting_url: str, 
                           meeting_title: str, meeting_start: datetime, 
                           join_at: datetime) -> int:
        """Create a new scheduled bot entry."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO scheduled_bots 
                    (calendar_event_id, meeting_url, meeting_title, meeting_start, join_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (calendar_event_id, meeting_url, meeting_title, 
                      meeting_start.isoformat(), join_at.isoformat()))
                
                bot_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Created scheduled bot {bot_id} for event {calendar_event_id}")
                return bot_id
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"Duplicate scheduled bot for event {calendar_event_id} at {meeting_start}")
                raise ValueError(f"Bot already scheduled for this event at this time")
            raise
        except Exception as e:
            logger.error(f"Error creating scheduled bot: {e}")
            raise
    
    def update_scheduled_bot(self, id: int, **kwargs) -> bool:
        """Update scheduled bot with given fields."""
        if not kwargs:
            return False
            
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.now().isoformat()
        
        # Build SET clause
        set_clause = ', '.join(f"{key} = ?" for key in kwargs.keys())
        values = list(kwargs.values())
        values.append(id)
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'UPDATE scheduled_bots SET {set_clause} WHERE id = ?', values)
                
                affected = cursor.rowcount
                conn.commit()
                
                if affected:
                    logger.info(f"Updated scheduled bot {id} with {list(kwargs.keys())}")
                return affected > 0
                
        except Exception as e:
            logger.error(f"Error updating scheduled bot {id}: {e}")
            raise
    
    def get_scheduled_bot_by_event(self, calendar_event_id: str, meeting_start: datetime) -> Dict[str, Any]:
        """Get scheduled bot by calendar event ID and start time."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM scheduled_bots 
                    WHERE calendar_event_id = ? AND meeting_start = ?
                ''', (calendar_event_id, meeting_start.isoformat()))
                
                row = cursor.fetchone()
                return self._dict_from_row(row)
                
        except Exception as e:
            logger.error(f"Error getting scheduled bot by event: {e}")
            raise
    
    def get_scheduled_bot_by_bot_id(self, bot_id: str) -> Dict[str, Any]:
        """Get scheduled bot by Recall bot ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM scheduled_bots WHERE bot_id = ?', (bot_id,))
                
                row = cursor.fetchone()
                return self._dict_from_row(row)
                
        except Exception as e:
            logger.error(f"Error getting scheduled bot by bot_id {bot_id}: {e}")
            raise
    
    def get_pending_bots(self, before: datetime = None) -> List[Dict[str, Any]]:
        """Get pending bots that need to be scheduled."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if before:
                    cursor.execute('''
                        SELECT * FROM scheduled_bots 
                        WHERE status = 'pending' AND join_at <= ?
                        ORDER BY join_at
                    ''', (before.isoformat(),))
                else:
                    cursor.execute('''
                        SELECT * FROM scheduled_bots 
                        WHERE status = 'pending'
                        ORDER BY join_at
                    ''')
                
                rows = cursor.fetchall()
                return [self._dict_from_row(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting pending bots: {e}")
            raise
    
    def get_bots_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all bots with given status."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM scheduled_bots 
                    WHERE status = ?
                    ORDER BY created_at DESC
                ''', (status,))
                
                rows = cursor.fetchall()
                return [self._dict_from_row(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting bots by status {status}: {e}")
            raise
    
    def cancel_bot(self, id: int) -> bool:
        """Cancel a scheduled bot."""
        return self.update_scheduled_bot(id, status='cancelled')
    
    # Bot Events CRUD Operations
    
    def log_event(self, event_id: str, bot_id: str, event_type: str, 
                  status_code: str = None, sub_code: str = None, 
                  payload: Dict = None) -> int:
        """Log a bot lifecycle event."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO bot_events 
                    (event_id, bot_id, event_type, status_code, sub_code, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (event_id, bot_id, event_type, status_code, sub_code,
                      json.dumps(payload) if payload else None))
                
                event_pk = cursor.lastrowid
                conn.commit()
                logger.info(f"Logged event {event_id} for bot {bot_id}: {event_type}")
                return event_pk
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.warning(f"Duplicate event {event_id} ignored")
                return 0  # Event already exists
            raise
        except Exception as e:
            logger.error(f"Error logging event {event_id}: {e}")
            raise
    
    def get_events_for_bot(self, bot_id: str) -> List[Dict[str, Any]]:
        """Get all events for a bot."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM bot_events 
                    WHERE bot_id = ?
                    ORDER BY timestamp DESC
                ''', (bot_id,))
                
                rows = cursor.fetchall()
                events = []
                for row in rows:
                    event = self._dict_from_row(row)
                    # Parse JSON payload if present
                    if event['payload']:
                        try:
                            event['payload'] = json.loads(event['payload'])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in event {event['id']}")
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"Error getting events for bot {bot_id}: {e}")
            raise
    
    def mark_event_processed(self, event_id: str) -> bool:
        """Mark event as processed."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE bot_events SET processed = TRUE 
                    WHERE event_id = ?
                ''', (event_id,))
                
                affected = cursor.rowcount
                conn.commit()
                return affected > 0
                
        except Exception as e:
            logger.error(f"Error marking event {event_id} as processed: {e}")
            raise
    
    def event_exists(self, event_id: str) -> bool:
        """Check if event already exists."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM bot_events WHERE event_id = ?', (event_id,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            logger.error(f"Error checking if event {event_id} exists: {e}")
            raise
    
    # Sync State Operations
    
    def get_sync_state(self) -> Dict[str, Any]:
        """Get current sync state."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM sync_state WHERE id = 1')
                
                row = cursor.fetchone()
                if row:
                    return self._dict_from_row(row)
                else:
                    # Initialize empty sync state
                    cursor.execute('''
                        INSERT INTO sync_state (id, last_sync, last_event_time, sync_token)
                        VALUES (1, NULL, NULL, NULL)
                    ''')
                    conn.commit()
                    return {
                        'id': 1,
                        'last_sync': None,
                        'last_event_time': None,
                        'sync_token': None,
                        'updated_at': datetime.now().isoformat()
                    }
                
        except Exception as e:
            logger.error(f"Error getting sync state: {e}")
            raise
    
    def update_sync_state(self, last_sync: datetime = None, 
                         last_event_time: datetime = None,
                         sync_token: str = None) -> bool:
        """Update sync state."""
        updates = {}
        if last_sync is not None:
            updates['last_sync'] = last_sync.isoformat()
        if last_event_time is not None:
            updates['last_event_time'] = last_event_time.isoformat()
        if sync_token is not None:
            updates['sync_token'] = sync_token
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().isoformat()
        
        try:
            # Ensure sync state row exists
            self.get_sync_state()
            
            # Build SET clause
            set_clause = ', '.join(f"{key} = ?" for key in updates.keys())
            values = list(updates.values())
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'UPDATE sync_state SET {set_clause} WHERE id = 1', values)
                
                affected = cursor.rowcount
                conn.commit()
                
                if affected:
                    logger.info(f"Updated sync state with {list(updates.keys())}")
                return affected > 0
                
        except Exception as e:
            logger.error(f"Error updating sync state: {e}")
            raise
    
    # Utility Methods
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Count scheduled bots by status
                cursor.execute('''
                    SELECT status, COUNT(*) as count 
                    FROM scheduled_bots 
                    GROUP BY status
                ''')
                bot_counts = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # Count total events
                cursor.execute('SELECT COUNT(*) as count FROM bot_events')
                event_count = cursor.fetchone()['count']
                
                # Get sync state
                sync_state = self.get_sync_state()
                
                return {
                    'scheduled_bots': bot_counts,
                    'total_events': event_count,
                    'sync_state': sync_state
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            raise


# Convenience functions
def get_database(db_path: str = None) -> RecallDatabase:
    """Get a RecallDatabase instance."""
    return RecallDatabase(db_path)


# Initialize logging
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Test database creation
    db = get_database()
    print("Database initialized successfully")
    stats = db.get_stats()
    print(f"Database stats: {stats}")