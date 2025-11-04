#!/usr/bin/env python3
"""
Meeting AI Request Manager
Idempotent request creation with deduplication built-in.
Provides single interface for creating or getting existing requests.
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/workspace")
AI_REQUESTS_DIR = WORKSPACE_ROOT / "N5/inbox/ai_requests"
AI_REQUESTS_PROCESSED = AI_REQUESTS_DIR / "processed"


def find_existing_request(meeting_id: str) -> Optional[Dict[str, Any]]:
    """
    Find any existing request (completed or pending) for this meeting.
    
    Args:
        meeting_id: Meeting identifier
        
    Returns:
        Existing request dict if found, None otherwise
    """
    # Check active queue
    for request_file in AI_REQUESTS_DIR.glob("*.json"):
        try:
            with open(request_file) as f:
                request = json.load(f)
                if request.get("inputs", {}).get("meeting_id") == meeting_id:
                    request["_source_file"] = str(request_file)
                    return request
        except Exception as e:
            logger.debug(f"Error reading {request_file}: {e}")
            continue
    
    # Check processed archive
    if AI_REQUESTS_PROCESSED.exists():
        for request_file in AI_REQUESTS_PROCESSED.glob("*.json"):
            try:
                with open(request_file) as f:
                    request = json.load(f)
                    if request.get("inputs", {}).get("meeting_id") == meeting_id:
                        request["_source_file"] = str(request_file)
                        return request
            except Exception as e:
                logger.debug(f"Error reading {request_file}: {e}")
                continue
    
    return None


def create_or_get_request(
    meeting_id: str,
    transcript_path: str,
    meeting_type: str,
    output_dir: str,
    reason: str = "Manual request",
    priority: int = 1,
    force_recreate: bool = False
) -> Dict[str, Any]:
    """
    Create AI request if not exists, or get existing request.
    Idempotent operation - safe to call multiple times.
    
    Args:
        meeting_id: Unique meeting identifier
        transcript_path: Path to transcript file
        meeting_type: Type of meeting (external, internal, etc.)
        output_dir: Where to write intelligence blocks
        reason: Reason for processing request
        priority: Request priority (1=high, 2=medium, 3=low)
        force_recreate: If True, create new even if completed exists
        
    Returns:
        Dict with request info and 'created' boolean indicating if new
        
    Raises:
        RuntimeError: If request creation fails verification
    """
    # Check for existing request
    existing = find_existing_request(meeting_id)
    
    if existing and not force_recreate:
        status = existing.get("status", "unknown")
        source = existing.get("_source_file", "unknown")
        logger.info(f"Found existing {status} request: {meeting_id}")
        logger.info(f"  Source: {source}")
        return {
            "request": existing,
            "created": False,
            "status": status,
            "reason": f"Existing {status} request found"
        }
    
    # Create new request
    AI_REQUESTS_DIR.mkdir(parents=True, exist_ok=True)
    
    request_id = f"meeting_{meeting_id}_{int(datetime.now(timezone.utc).timestamp())}"
    request = {
        "request_id": request_id,
        "request_type": "meeting_reprocess",
        "prompt_name": "Meeting Process",
        "inputs": {
            "transcript_path": transcript_path,
            "meeting_id": meeting_id,
            "meeting_type": meeting_type,
            "original_dir": output_dir,
            "reason": reason
        },
        "output_requirements": {
            "blocks": ["notes", "commitments", "key_quotes", "deliverables"],
            "output_dir": output_dir
        },
        "status": "pending",
        "priority": priority,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    request_path = AI_REQUESTS_DIR / f"{request_id}.json"
    
    # Write request
    with open(request_path, 'w') as f:
        json.dump(request, f, indent=2)
    
    # VERIFY creation succeeded (P18)
    if not request_path.exists():
        raise RuntimeError(f"Failed to create request file: {request_path}")
    
    # Verify content is readable
    try:
        with open(request_path) as f:
            verified = json.load(f)
            if verified.get("request_id") != request_id:
                raise RuntimeError(f"Request ID mismatch after write")
    except Exception as e:
        raise RuntimeError(f"Failed to verify request creation: {e}")
    
    logger.info(f"✓ Created new request: {request_id}")
    logger.info(f"  Meeting: {meeting_id}")
    logger.info(f"  Path: {request_path}")
    
    return {
        "request": request,
        "created": True,
        "status": "pending",
        "reason": "New request created",
        "path": str(request_path)
    }


def get_request_status(meeting_id: str) -> Optional[str]:
    """
    Quick status check for a meeting.
    
    Args:
        meeting_id: Meeting identifier
        
    Returns:
        Status string (pending, completed, error) or None if not found
    """
    existing = find_existing_request(meeting_id)
    return existing.get("status") if existing else None


def main():
    """Test/demo of request manager."""
    import sys
    
    if len(sys.argv) < 5:
        print("Usage: request_manager.py <meeting_id> <transcript_path> <meeting_type> <output_dir> [reason]")
        print("\nExample:")
        print("  python3 request_manager.py \\")
        print("    '2025-10-30_external-jake' \\")
        print("    '/home/workspace/Personal/Meetings/2025-10-30_external-jake/transcript.md' \\")
        print("    'external' \\")
        print("    '/home/workspace/Personal/Meetings/2025-10-30_external-jake' \\")
        print("    'Manual reprocess'")
        return 1
    
    meeting_id = sys.argv[1]
    transcript_path = sys.argv[2]
    meeting_type = sys.argv[3]
    output_dir = sys.argv[4]
    reason = sys.argv[5] if len(sys.argv) > 5 else "Manual request"
    
    result = create_or_get_request(
        meeting_id=meeting_id,
        transcript_path=transcript_path,
        meeting_type=meeting_type,
        output_dir=output_dir,
        reason=reason
    )
    
    print(f"\n{'='*60}")
    print(f"Meeting ID: {meeting_id}")
    print(f"Status: {result['status']}")
    print(f"Created: {result['created']}")
    print(f"Reason: {result['reason']}")
    if result['created']:
        print(f"Path: {result['path']}")
    print(f"{'='*60}\n")
    
    return 0


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
