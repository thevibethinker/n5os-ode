"""
Fathom.ai REST API Client
"""

import logging
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

class FathomClient:
    """REST client for Fathom.ai API"""
    
    BASE_URL = "https://api.fathom.video/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.get_api_key()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "X-Api-Key": self.api_key, # Documentation says X-Api-Key
            "Content-Type": "application/json"
        })
    
    def get_recording(self, recording_id: int) -> Optional[Dict[str, Any]]:
        """Fetch full recording data including transcript"""
        try:
            # Note: The webhook payload often includes the transcript already.
            # This client is for supplemental data if needed.
            response = self.session.get(f"{self.BASE_URL}/recordings/{recording_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch Fathom recording {recording_id}: {e}")
            return None
            
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            # Try to list recordings or get current user if endpoint exists
            # Using recordings list as a test
            response = self.session.get(f"{self.BASE_URL}/recordings", params={"limit": 1})
            response.raise_for_status()
            logger.info("Fathom API connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Fathom API connection test FAILED: {e}")
            return False

