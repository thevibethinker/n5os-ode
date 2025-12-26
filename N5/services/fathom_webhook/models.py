from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class FathomTranscriptEntry(BaseModel):
    speaker: Dict[str, Any]
    text: str
    timestamp: str

class FathomSummary(BaseModel):
    template_name: str
    markdown_formatted: str

class FathomActionItem(BaseModel):
    description: str
    user_generated: bool
    completed: bool
    recording_timestamp: Optional[str] = None
    recording_playback_url: Optional[str] = None
    assignee: Optional[Dict[str, Any]] = None

class FathomWebhookPayload(BaseModel):
    # Based on https://developers.fathom.ai/api-reference/webhook-payloads/new-meeting-content-ready
    title: str
    meeting_title: Optional[str] = None
    recording_id: int
    url: str
    share_url: str
    created_at: str
    scheduled_start_time: str
    scheduled_end_time: str
    recording_start_time: str
    recording_end_time: str
    calendar_invitees_domains_type: str
    transcript_language: Optional[str] = "en"
    transcript: Optional[List[FathomTranscriptEntry]] = None
    default_summary: Optional[FathomSummary] = None
    action_items: Optional[List[FathomActionItem]] = None
    calendar_invitees: Optional[List[Dict[str, Any]]] = None
    recorded_by: Optional[Dict[str, Any]] = None
    crm_matches: Optional[Dict[str, Any]] = None

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

