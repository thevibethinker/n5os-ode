import os
import json
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path


class CalendlyClient:
    BASE_URL = "https://api.calendly.com"
    TOKEN_FILE = Path.home() / ".config" / "calendly_tokens.json"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("CALENDLY_API_KEY") or os.environ.get("CALENDLY_PAT")
        self._using_oauth = False

        if not self.api_key:
            self.api_key = self._load_oauth_token()
            self._using_oauth = True

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
        """Load access token from OAuth token file, refreshing if expired."""
        try:
            if not self.TOKEN_FILE.exists():
                return None

            with open(self.TOKEN_FILE) as f:
                tokens = json.load(f)

            expires_at = tokens.get("expires_at", 0)
            now_ms = int(time.time() * 1000)
            buffer_ms = 5 * 60 * 1000  # 5 min buffer

            if now_ms >= (expires_at - buffer_ms):
                refreshed = self._refresh_token(tokens.get("refresh_token"))
                if refreshed:
                    return refreshed
                return None

            return tokens.get("access_token")
        except Exception as e:
            print(f"Warning: Failed to load OAuth tokens: {e}")
        return None

    def _refresh_token(self, refresh_token: str) -> Optional[str]:
        """Refresh an expired OAuth token using the refresh_token grant."""
        if not refresh_token:
            print("Warning: No refresh token available, cannot auto-refresh")
            return None

        client_id = (
            os.environ.get("CALENDLY_CLIENT_ID")
            or os.environ.get("Calendly-Client-ID")
            or ""
        ).strip()
        client_secret = (
            os.environ.get("CALENDLY_CLIENT_SECRET")
            or os.environ.get("Calendly-Client-Secret")
            or ""
        ).strip()

        if not client_id or not client_secret:
            print("Warning: CALENDLY_CLIENT_ID / CALENDLY_CLIENT_SECRET not set, cannot refresh")
            return None

        try:
            resp = requests.post(
                "https://auth.calendly.com/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15,
            )

            if not resp.ok:
                print(f"Warning: Token refresh failed ({resp.status_code}): {resp.text}")
                return None

            data = resp.json()
            tokens = {
                "access_token": data["access_token"],
                "refresh_token": data.get("refresh_token", refresh_token),
                "token_type": data.get("token_type", "Bearer"),
                "expires_at": int(time.time() * 1000) + (data.get("expires_in", 7200) * 1000),
                "created_at": self._read_existing_created_at(),
                "refreshed_at": __import__('datetime').datetime.now().isoformat(),
                "owner_uri": data.get("owner", self._read_existing_field("owner_uri")),
                "organization_uri": data.get("organization", self._read_existing_field("organization_uri")),
            }

            with open(self.TOKEN_FILE, 'w') as f:
                json.dump(tokens, f, indent=2)

            print(f"Token refreshed successfully (expires in {data.get('expires_in', '?')}s)")
            return tokens["access_token"]

        except Exception as e:
            print(f"Warning: Token refresh exception: {e}")
            return None

    def _read_existing_field(self, field: str) -> str:
        try:
            with open(self.TOKEN_FILE) as f:
                return json.load(f).get(field, "")
        except Exception:
            return ""

    def _read_existing_created_at(self) -> str:
        return self._read_existing_field("created_at") or __import__('datetime').datetime.now().isoformat()

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
