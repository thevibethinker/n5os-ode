#!/usr/bin/env python3
"""
Google authentication helper using N5 secrets management.
Replaces direct file access to google_service_account.json.
"""
import json
import sys
from pathlib import Path

# Add N5 lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.secrets import get_secret_json

def get_google_credentials():
    """
    Get Google service account credentials from Zo secrets.
    
    Returns:
        dict: Service account credentials
        
    Example:
        >>> from N5.scripts.google_auth import get_google_credentials
        >>> creds = get_google_credentials()
        >>> project_id = creds["project_id"]
    """
    return get_secret_json("GOOGLE_SERVICE_ACCOUNT_JSON")

def get_google_client(service_name: str, version: str):
    """
    Get an authenticated Google API client.
    
    Args:
        service_name: API service name (e.g., 'sheets', 'drive')
        version: API version (e.g., 'v4', 'v3')
        
    Returns:
        Authenticated Google API client
        
    Example:
        >>> client = get_google_client('sheets', 'v4')
        >>> sheet = client.spreadsheets().get(spreadsheetId=id).execute()
    """
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    credentials_dict = get_google_credentials()
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive']
    )
    
    return build(service_name, version, credentials=credentials)

if __name__ == "__main__":
    # Self-test
    print("=" * 50)
    print("Google Authentication Helper - Self Test")
    print("=" * 50)
    
    try:
        creds = get_google_credentials()
        print(f"\n✓ Credentials loaded")
        print(f"  Project: {creds.get('project_id', 'Unknown')}")
        print(f"  Email: {creds.get('client_email', 'Unknown')}")
        
        print("\n✓ Self-test complete")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Self-test failed: {e}")
        sys.exit(1)
