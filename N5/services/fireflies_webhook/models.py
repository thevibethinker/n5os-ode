from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FirefliesWebhookPayload(BaseModel):
    meetingId: str = Field(..., description="Fireflies meeting UUID")
    eventType: str = Field(..., description="Event type (e.g., 'Transcription completed')")
    clientReferenceId: Optional[str] = Field(None, description="Optional custom reference ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "meetingId": "ASxwZxCstx",
                "eventType": "Transcription completed",
                "clientReferenceId": "project-xyz"
            }
        }

class WebhookLogEntry(BaseModel):
    webhook_id: str
    event_type: str
    transcript_id: str
    received_at: str
    processed_at: Optional[str] = None
    status: str = "pending"
    payload: str
    error_message: Optional[str] = None
    created_at: Optional[str] = None

class WebhookResponse(BaseModel):
    status: str
    webhook_id: str
    message: str

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    database_connected: bool
    api_key_configured: bool

