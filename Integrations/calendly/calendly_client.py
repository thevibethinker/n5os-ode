import os
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

class CalendlyClient:
    BASE_URL = "https://api.calendly.com"
    TOKEN_FILE = Path.home() / ".config" / "calendly_tokens.json"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("CALENDLY_API_KEY") or os.environ.get("CALENDLY_PAT")
        
        # Try OAuth tokens if no PAT
        if not self.api_key:
            self.api_key = self._load_oauth_token()
        
        if not self.api_key:
            raise ValueError(
                "No Calendly credentials found. Either:\n"
                "  1. Set CALENDLY_API_KEY or CALENDLY_PAT environment variable, or\n"
                "  2. Complete OAuth flow at https://calendly-auth-va.zocomputer.io"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _load_oauth_token(self) -> Optional[str]:
        """Load access token from OAuth token file."""
        try:
            if self.TOKEN_FILE.exists():
                with open(self.TOKEN_FILE) as f:
                    tokens = json.load(f)
                    return tokens.get("access_token")
        except Exception as e:
            print(f"Warning: Failed to load OAuth tokens: {e}")
        return None

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def _delete(self, endpoint: str) -> bool:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True

    def get_current_user(self) -> Dict[str, Any]:
        return self._get("users/me")["resource"]

    def list_event_types(self, user_uri: str = None, organization_uri: str = None) -> List[Dict[str, Any]]:
        params = {}
        if user_uri:
            params["user"] = user_uri
        if organization_uri:
            params["organization"] = organization_uri
        
        return self._get("event_types", params=params).get("collection", [])

    def get_event_type(self, uuid: str) -> Dict[str, Any]:
        return self._get(f"event_types/{uuid}")["resource"]

    def list_scheduled_events(self, user_uri: str = None, organization_uri: str = None, 
                               min_start_time: str = None, max_start_time: str = None,
                               status: str = None, count: int = 20) -> List[Dict[str, Any]]:
        params = {"count": count}
        if user_uri:
            params["user"] = user_uri
        if organization_uri:
            params["organization"] = organization_uri
        if min_start_time:
            params["min_start_time"] = min_start_time
        if max_start_time:
            params["max_start_time"] = max_start_time
        if status:
            params["status"] = status
        
        return self._get("scheduled_events", params=params).get("collection", [])

    def get_scheduled_event(self, uuid: str) -> Dict[str, Any]:
        return self._get(f"scheduled_events/{uuid}")["resource"]

    def list_event_invitees(self, event_uuid: str) -> List[Dict[str, Any]]:
        return self._get(f"scheduled_events/{event_uuid}/invitees").get("collection", [])

    def list_webhook_subscriptions(self, organization_uri: str, scope: str = "organization") -> List[Dict[str, Any]]:
        params = {"organization": organization_uri, "scope": scope}
        return self._get("webhook_subscriptions", params=params).get("collection", [])

    def create_webhook_subscription(self, url: str, events: List[str], organization_uri: str, 
                                     scope: str = "organization", signing_key: str = None) -> Dict[str, Any]:
        data = {
            "url": url,
            "events": events,
            "organization": organization_uri,
            "scope": scope
        }
        if signing_key:
            data["signing_key"] = signing_key
        
        return self._post("webhook_subscriptions", data)["resource"]

    def delete_webhook_subscription(self, uuid: str) -> bool:
        return self._delete(f"webhook_subscriptions/{uuid}")
