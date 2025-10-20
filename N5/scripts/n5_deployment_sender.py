#!/usr/bin/env python3
"""
N5 Deployment Sender (ParentZo)
Sends deployment manifest to ChildZo via ZoBridge.

Principles: P7 (Dry-Run), P11 (Failure Modes), P18 (State Verification), P19 (Error Handling)
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE = Path("/home/workspace")
CONFIG_PATH = WORKSPACE / "N5/services/zobridge/zobridge.config.json"
CHILDZO_URL = "https://zobridge-vademonstrator.zocomputer.io"


def load_config() -> dict:
    """Load ZoBridge configuration."""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {CONFIG_PATH}: {e}")
        raise


def send_deployment_message(
    manifest_path: Path,
    childzo_url: str,
    secret: str,
    dry_run: bool = False
) -> Tuple[bool, str]:
    """
    Send deployment manifest to ChildZo.
    Returns (success, message).
    """
    
    try:
        # Load manifest
        logger.info(f"Loading manifest: {manifest_path}")
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        deployment_id = manifest.get("deployment_id", "unknown")
        file_count = len(manifest.get("files", []))
        dir_count = len(manifest.get("directories", []))
        
        logger.info(f"Manifest loaded: {deployment_id}")
        logger.info(f"  Files: {file_count}")
        logger.info(f"  Directories: {dir_count}")
        
        # Calculate payload size
        manifest_json = json.dumps(manifest)
        payload_size_mb = len(manifest_json) / (1024 * 1024)
        logger.info(f"  Payload size: {payload_size_mb:.2f} MB")
        
        if payload_size_mb > 50:
            return False, f"Payload too large: {payload_size_mb:.2f} MB (max 50 MB)"
        
        # Create ZoBridge message
        message = {
            "message_id": f"msg_deploy_{deployment_id}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "from": "ParentZo",
            "to": "ChildZo",
            "thread_id": "n5_deployment",
            "type": "instruction",
            "content": {
                "objective": "Deploy N5 System",
                "deployment_type": "bulk_manifest",
                "manifest": manifest
            }
        }
        
        url = f"{childzo_url}/api/zobridge/inbox"
        
        if dry_run:
            logger.info(f"[DRY RUN] Would POST deployment to: {url}")
            logger.info(f"[DRY RUN] Message ID: {message['message_id']}")
            logger.info(f"[DRY RUN] Payload size: {payload_size_mb:.2f} MB")
            return True, "Dry run successful"
        
        # Send message
        logger.info(f"Sending deployment to: {url}")
        logger.info(f"  Message ID: {message['message_id']}")
        
        response = requests.post(
            url,
            json=message,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {secret}"
            },
            timeout=120  # Longer timeout for large payload
        )
        
        if response.status_code == 200:
            logger.info(f"✓ Deployment sent successfully")
            logger.info(f"  Response: {response.text}")
            return True, "Deployment sent successfully"
        else:
            error_msg = f"Failed: {response.status_code} {response.text}"
            logger.error(f"✗ {error_msg}")
            return False, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out after 120s"
        logger.error(f"✗ {error_msg}")
        return False, error_msg
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error: {e}"
        logger.error(f"✗ {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"✗ {error_msg}", exc_info=True)
        return False, error_msg


def main(
    manifest_file: str,
    childzo_url: str = CHILDZO_URL,
    dry_run: bool = False
) -> int:
    """Main entry point."""
    
    try:
        manifest_path = Path(manifest_file).resolve()
        
        # Validate manifest file
        if not manifest_path.exists():
            logger.error(f"Manifest file not found: {manifest_path}")
            return 1
        
        if manifest_path.stat().st_size == 0:
            logger.error(f"Manifest file is empty: {manifest_path}")
            return 1
        
        # Load config
        config = load_config()
        secret = config.get("secret")
        
        if not secret:
            logger.error("ZoBridge secret not found in config")
            return 1
        
        # Send deployment
        logger.info("=" * 60)
        logger.info("N5 DEPLOYMENT SENDER")
        logger.info("=" * 60)
        
        success, msg = send_deployment_message(
            manifest_path,
            childzo_url,
            secret,
            dry_run
        )
        
        if success:
            logger.info("=" * 60)
            logger.info("DEPLOYMENT SENT")
            logger.info("=" * 60)
            logger.info(f"Status: {msg}")
            logger.info("Next: Monitor ChildZo for deployment completion")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("=" * 60)
            logger.error("DEPLOYMENT FAILED")
            logger.error("=" * 60)
            logger.error(f"Error: {msg}")
            logger.error("=" * 60)
            return 1
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send N5 deployment manifest to ChildZo"
    )
    parser.add_argument(
        "manifest_file",
        help="Deployment manifest JSON file"
    )
    parser.add_argument(
        "--childzo-url",
        default=CHILDZO_URL,
        help=f"ChildZo ZoBridge URL (default: {CHILDZO_URL})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without sending"
    )
    
    args = parser.parse_args()
    
    exit(main(
        args.manifest_file,
        args.childzo_url,
        args.dry_run
    ))
