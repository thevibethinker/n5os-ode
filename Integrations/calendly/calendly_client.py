import os
import requests
from typing import Dict, Any, List

class CalendlyClient:
    BASE_URL = "https://api.calendly.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("CALENDLY_API_KEY")
        if not self.api_key:
            raise ValueError("CALENDLY_API_KEY environment variable not set")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

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

    def list_webhook_subscriptions(self, organization_uri: str, scope: str = "organization") -> List[Dict[str, Any]]:
        params = {"organization": organization_uri, "scope": scope}
        return self._get("webhook_subscriptions", params=params).get("collection", [])

    def create_webhook_subscription(self, url: str, events: List[str], organization_uri: str, scope: str = "organization") -> Dict[str, Any]:
        data = {
            "url": url,
            "events": events,
            "organization": organization_uri,
            "scope": scope
        }
        response = requests.post(f"{self.BASE_URL}/webhook_subscriptions", headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()["resource"]

