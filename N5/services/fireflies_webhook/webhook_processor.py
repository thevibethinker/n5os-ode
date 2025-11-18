import sqlite3
import json
import hmac
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from .config import Config
from .models import FirefliesWebhookPayload, WebhookLogEntry

logger = logging.getLogger(__name__)

class WebhookProcessor:
    def __init__(self, db_path: Path = Config.DATABASE_PATH):
        self.db_path = db_path
        self._ensure_schema()
    
    def _ensure_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fireflies_webhooks (
                    webhook_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    transcript_id TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    processed_at TEXT,
                    status TEXT DEFAULT 'pending',
                    payload TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fireflies_status 
                ON fireflies_webhooks(status)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fireflies_transcript 
                ON fireflies_webhooks(transcript_id)
            """)
            
            conn.commit()
            logger.info("Database schema verified")
    
    def verify_hmac_signature(
        self, 
        payload: str, 
        signature: Optional[str]
    ) -> bool:
        webhook_secret = Config.get_webhook_secret()
        
        if not webhook_secret:
            logger.warning("WEBHOOK_SECRET not configured - skipping HMAC verification")
            return True
        
        if not signature:
            logger.error("No signature provided but WEBHOOK_SECRET is configured")
            return False
        
        expected_signature = hmac.new(
            webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        signature_value = signature.replace("sha256=", "")
        
        is_valid = hmac.compare_digest(expected_signature, signature_value)
        
        if not is_valid:
            logger.error(f"HMAC verification failed. Expected: sha256={expected_signature}, Got: {signature}")
        
        return is_valid
    
    def log_webhook(
        self,
        webhook_id: str,
        payload: FirefliesWebhookPayload,
        raw_payload: str
    ) -> bool:
        try:
            entry = WebhookLogEntry(
                webhook_id=webhook_id,
                event_type=payload.eventType,
                transcript_id=payload.meetingId,
                received_at=datetime.utcnow().isoformat(),
                status="pending",
                payload=raw_payload
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO fireflies_webhooks 
                    (webhook_id, event_type, transcript_id, received_at, status, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    entry.webhook_id,
                    entry.event_type,
                    entry.transcript_id,
                    entry.received_at,
                    entry.status,
                    entry.payload
                ))
                conn.commit()
            
            logger.info(f"Logged webhook {webhook_id} for transcript {payload.meetingId}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log webhook {webhook_id}: {e}")
            return False
    
    def get_pending_webhooks(self, limit: int = 100) -> list[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM fireflies_webhooks 
                    WHERE status = 'pending'
                    ORDER BY received_at ASC
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to fetch pending webhooks: {e}")
            return []
    
    def update_webhook_status(
        self,
        webhook_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                processed_at = datetime.utcnow().isoformat() if status != "pending" else None
                
                conn.execute("""
                    UPDATE fireflies_webhooks 
                    SET status = ?, processed_at = ?, error_message = ?
                    WHERE webhook_id = ?
                """, (status, processed_at, error_message, webhook_id))
                
                conn.commit()
            
            logger.info(f"Updated webhook {webhook_id} to status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update webhook {webhook_id}: {e}")
            return False

