import sqlite3
import json
import hmac
import hashlib
import logging
import base64
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from .config import Config
from .models import FathomWebhookPayload

logger = logging.getLogger(__name__)

class WebhookProcessor:
    def __init__(self, db_path: Path = Config.DATABASE_PATH):
        self.db_path = db_path
        self._ensure_schema()
    
    def _ensure_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fathom_webhooks (
                    webhook_id TEXT PRIMARY KEY,
                    recording_id INTEGER,
                    title TEXT,
                    received_at TEXT NOT NULL,
                    processed_at TEXT,
                    status TEXT DEFAULT 'pending',
                    payload TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fathom_status 
                ON fathom_webhooks(status)
            """)
            
            conn.commit()
            logger.info("Fathom database schema verified")
    
    def verify_fathom_signature(
        self, 
        raw_body: bytes, 
        signature_header: Optional[str]
    ) -> bool:
        """
        Verify Fathom webhook signature.
        Format: "v1,BKQR1BIFjiNPdfpqM3+FH/YckKhX7WIq4/KK6Cc5aDY="
        """
        webhook_secret = Config.get_webhook_secret()
        
        if not webhook_secret:
            logger.warning("FATHOM_WEBHOOK_SECRET not configured - skipping verification")
            return True
        
        if not signature_header:
            logger.error("No webhook-signature header provided")
            return False
        
        try:
            # signature_header format: "v1,signature1 signature2..."
            if ',' not in signature_header:
                return False
                
            version, signature_block = signature_header.split(',', 1)
            
            # Use webhook_secret to hash the request body with HMAC SHA-256
            expected_hash = hmac.new(
                webhook_secret.encode('utf-8'),
                raw_body,
                hashlib.sha256
            ).digest()
            
            expected_signature = base64.b64encode(expected_hash).decode('utf-8')
            
            provided_signatures = signature_block.strip().split(' ')
            
            for sig in provided_signatures:
                if hmac.compare_digest(expected_signature, sig):
                    return True
            
            logger.error(f"Fathom signature verification failed. Expected one of: {provided_signatures}, Got hash base64: {expected_signature}")
            return False
        except Exception as e:
            logger.error(f"Error verifying Fathom signature: {e}")
            return False
    
    def log_webhook(
        self,
        webhook_id: str,
        payload: FathomWebhookPayload,
        raw_payload: str
    ) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO fathom_webhooks 
                    (webhook_id, recording_id, title, received_at, status, payload)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    webhook_id,
                    payload.recording_id,
                    payload.title,
                    datetime.utcnow().isoformat(),
                    "pending",
                    raw_payload
                ))
                conn.commit()
            
            logger.info(f"Logged Fathom webhook {webhook_id} for recording {payload.recording_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log Fathom webhook {webhook_id}: {e}")
            return False

    def get_pending_webhooks(self, limit: int = 100) -> list[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM fathom_webhooks 
                    WHERE status = 'pending'
                    ORDER BY received_at ASC
                    LIMIT ?
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Failed to fetch pending Fathom webhooks: {e}")
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
                    UPDATE fathom_webhooks 
                    SET status = ?, processed_at = ?, error_message = ?
                    WHERE webhook_id = ?
                """, (status, processed_at, error_message, webhook_id))
                
                conn.commit()
            
            logger.info(f"Updated Fathom webhook {webhook_id} to status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Fathom webhook {webhook_id}: {e}")
            return False

