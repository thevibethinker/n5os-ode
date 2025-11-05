#!/usr/bin/env python3
"""
AI Response Handler v2 - With Quality Validation
Processes completed AI responses, validates quality, manages iteration
"""
import sqlite3
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from output_validator import OutputValidator
from quality_controller import QualityController

WORKSPACE_ROOT = Path("/home/workspace")
RESPONSE_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_responses"
REQUEST_QUEUE = WORKSPACE_ROOT / "N5/inbox/ai_requests"
PROCESSED_RESPONSES = RESPONSE_QUEUE / "processed"
PROCESSED_REQUESTS = REQUEST_QUEUE / "processed"
PIPELINE_DB = WORKSPACE_ROOT / "N5/data/meeting_pipeline.db"
MEETING_INBOX = WORKSPACE_ROOT / "Personal/Meetings/Inbox"
MEETINGS_ROOT = WORKSPACE_ROOT / "Personal/Meetings"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


def scan_responses():
    """Find all unprocessed responses."""
    if not RESPONSE_QUEUE.exists():
        return []
    
    responses = []
    for resp_file in RESPONSE_QUEUE.glob("*.json"):
        if resp_file.is_file():
            try:
                data = json.loads(resp_file.read_text())
                responses.append((resp_file, data))
            except Exception as e:
                logger.error(f"Error reading {resp_file.name}: {e}")
    
    return responses


def update_meeting_status(meeting_id, status, completed_at=None, notes=None, 
                         validation_attempts=None, quality_score=None, quality_issues=None):
    """Update meeting status in database with validation fields."""
    conn = sqlite3.connect(PIPELINE_DB)
    cursor = conn.cursor()
    
    updates = ["status = ?"]
    params = [status]
    
    if completed_at:
        updates.append("completed_at = ?")
        params.append(completed_at)
    
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    
    if validation_attempts is not None:
        updates.append("validation_attempts = ?")
        params.append(validation_attempts)
    
    if quality_score is not None:
        updates.append("quality_score = ?")
        params.append(quality_score)
    
    if quality_issues is not None:
        updates.append("quality_issues = ?")
        params.append(quality_issues)
    
    params.append(meeting_id)
    
    sql = f"UPDATE meetings SET {', '.join(updates)} WHERE meeting_id = ?"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()


def find_meeting_directory(meeting_id):
    """Find meeting directory by ID"""
    # Check both Inbox and main Meetings directory
    for root_dir in [MEETING_INBOX, MEETINGS_ROOT]:
        for meeting_dir in root_dir.iterdir():
            if meeting_dir.is_dir() and meeting_id in meeting_dir.name:
                return meeting_dir
    return None


def create_retry_request(meeting_id, attempt_number, feedback_prompt):
    """Create retry request for meeting processing"""
    request_id = f"{meeting_id}_retry_{attempt_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    request_file = REQUEST_QUEUE / f"{request_id}.json"
    
    request_data = {
        "request_id": request_id,
        "meeting_id": meeting_id,
        "prompt_name": "Meeting Process",
        "attempt": attempt_number,
        "retry": True,
        "feedback": feedback_prompt,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    request_file.write_text(json.dumps(request_data, indent=2))
    logger.info(f"Created retry request: {request_file.name}")
    return request_file


def process_response(resp_file, data):
    """
    Process AI response with validation and iteration
    
    Args:
        resp_file: Path to response JSON file
        data: Response data dict
    """
    meeting_id = data.get("meeting_id")
    if not meeting_id:
        logger.error(f"No meeting_id in {resp_file.name}")
        return
    
    logger.info(f"Processing response for meeting: {meeting_id}")
    
    # Find meeting directory
    meeting_dir = find_meeting_directory(meeting_id)
    if not meeting_dir:
        logger.error(f"Could not find meeting directory for: {meeting_id}")
        update_meeting_status(meeting_id, "error", notes="Meeting directory not found")
        return
    
    # Get current attempt number
    attempt = data.get("attempt", 1)
    
    # Validate output quality
    controller = QualityController(meeting_dir)
    validation_result = controller.check_quality()
    
    controller.log_attempt(attempt, validation_result)
    controller.save_attempt_log()
    
    logger.info(f"Validation result - Score: {validation_result.score:.2f}, Passed: {validation_result.passed}")
    
    # Update database with validation results
    issues_json = json.dumps(validation_result.issues) if validation_result.issues else None
    
    if validation_result.passed:
        # SUCCESS - Mark complete
        logger.info(f"✓ Meeting passed validation: {meeting_id}")
        update_meeting_status(
            meeting_id,
            status="completed",
            completed_at=datetime.now(timezone.utc).isoformat(),
            validation_attempts=attempt,
            quality_score=validation_result.score,
            quality_issues=issues_json
        )
        
        # Move processed files
        PROCESSED_RESPONSES.mkdir(exist_ok=True)
        resp_file.rename(PROCESSED_RESPONSES / resp_file.name)
        
    elif controller.should_retry(validation_result, attempt):
        # RETRY - Create new request with feedback
        logger.warning(f"Meeting failed validation, creating retry request (attempt {attempt + 1})")
        
        feedback = controller.generate_feedback_prompt(validation_result, attempt + 1)
        create_retry_request(meeting_id, attempt + 1, feedback)
        
        update_meeting_status(
            meeting_id,
            status="queued_for_ai",
            validation_attempts=attempt,
            quality_score=validation_result.score,
            quality_issues=issues_json,
            notes=f"Retry attempt {attempt + 1} queued"
        )
        
        # Move processed response
        PROCESSED_RESPONSES.mkdir(exist_ok=True)
        resp_file.rename(PROCESSED_RESPONSES / resp_file.name)
        
    else:
        # FAILED - Flag for human review
        logger.error(f"✗ Meeting failed validation after {attempt} attempts: {meeting_id}")
        update_meeting_status(
            meeting_id,
            status="needs_review",
            validation_attempts=attempt,
            quality_score=validation_result.score,
            quality_issues=issues_json,
            notes=f"Failed validation after {attempt} attempts"
        )
        
        # Move to processed
        PROCESSED_RESPONSES.mkdir(exist_ok=True)
        resp_file.rename(PROCESSED_RESPONSES / resp_file.name)


def main():
    """Main processing loop"""
    logger.info("Starting response handler v2 (with validation)")
    
    responses = scan_responses()
    if not responses:
        logger.info("No responses to process")
        return 0
    
    logger.info(f"Found {len(responses)} response(s) to process")
    
    for resp_file, data in responses:
        try:
            process_response(resp_file, data)
        except Exception as e:
            logger.error(f"Error processing {resp_file.name}: {e}", exc_info=True)
            # Move to processed anyway to avoid blocking queue
            PROCESSED_RESPONSES.mkdir(exist_ok=True)
            resp_file.rename(PROCESSED_RESPONSES / f"{resp_file.stem}_ERROR{resp_file.suffix}")
    
    logger.info("Response processing complete")
    return 0


if __name__ == '__main__':
    exit(main())
