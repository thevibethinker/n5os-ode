#!/usr/bin/env python3
"""
N5 Secrets Management Library

Baseline protocol for credential access in N5 OS.
All secrets are stored in Zo's secrets manager and accessed via environment variables.

**Usage:**
    from N5.lib.secrets import get_secret, get_secret_json
    
    # Simple secret
    api_key = get_secret("GITHUB_API_TOKEN")
    
    # Optional secret with default
    debug_mode = get_secret("DEBUG_MODE", required=False, default="false")
    
    # JSON secret (for service accounts)
    google_creds = get_secret_json("GOOGLE_SERVICE_ACCOUNT_JSON")

**Naming Convention:**
    <SERVICE>_<CREDENTIAL_TYPE>_<ENVIRONMENT>
    
    Examples:
    - SLACK_BOT_TOKEN
    - SLACK_WEBHOOK_URL
    - GOOGLE_SERVICE_ACCOUNT_JSON
    - GITHUB_API_TOKEN

**Security:**
    - Never log secret values
    - Never write secrets to filesystem
    - Always use required=True for critical secrets
    - Use specific error messages for debugging

**Version:** 1.0
**Created:** 2025-10-28
**Authority:** N5 Architectural Principles
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def get_secret(
    key: str, 
    required: bool = True, 
    default: Optional[str] = None
) -> Optional[str]:
    """
    Get a secret from environment variables.
    
    Args:
        key: Environment variable name (e.g., "SLACK_BOT_TOKEN")
        required: If True, raises ValueError when secret is missing
        default: Default value if secret not found (only used when required=False)
    
    Returns:
        Secret value as string, or default if not found and not required
    
    Raises:
        ValueError: If required=True and secret not found
    
    Examples:
        >>> token = get_secret("SLACK_BOT_TOKEN")
        >>> webhook = get_secret("WEBHOOK_URL", required=False, default="https://example.com")
    """
    value = os.getenv(key)
    
    if value is None:
        if required:
            logger.error(f"Required secret '{key}' not found in environment")
            logger.error(f"Add this secret to Zo settings: https://va.zo.computer/settings")
            raise ValueError(
                f"Required secret '{key}' not found. "
                f"Please add it to Zo secrets manager."
            )
        logger.debug(f"Optional secret '{key}' not found, using default")
        return default
    
    # Basic validation: non-empty
    if required and not value.strip():
        raise ValueError(f"Secret '{key}' is empty")
    
    logger.debug(f"✓ Secret '{key}' loaded (length: {len(value)})")
    return value


def get_secret_json(
    key: str, 
    required: bool = True
) -> Optional[dict[str, Any]]:
    """
    Get a JSON secret from environment variables and parse it.
    
    Useful for service account credentials, complex configs, etc.
    
    Args:
        key: Environment variable name containing JSON
        required: If True, raises ValueError when secret is missing or invalid
    
    Returns:
        Parsed JSON as dict, or None if not found and not required
    
    Raises:
        ValueError: If required=True and secret not found or invalid JSON
        json.JSONDecodeError: If value exists but is not valid JSON
    
    Examples:
        >>> creds = get_secret_json("GOOGLE_SERVICE_ACCOUNT_JSON")
        >>> project_id = creds["project_id"]
    """
    value = get_secret(key, required=required)
    
    if value is None:
        return None
    
    try:
        parsed = json.loads(value)
        logger.debug(f"✓ JSON secret '{key}' parsed successfully")
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Secret '{key}' is not valid JSON: {e}")
        if required:
            raise ValueError(f"Secret '{key}' must be valid JSON") from e
        return None


def validate_secrets(required_keys: list[str]) -> bool:
    """
    Validate that all required secrets are present.
    
    Useful for startup validation in scripts/services.
    
    Args:
        required_keys: List of required environment variable names
    
    Returns:
        True if all secrets present, False otherwise
    
    Examples:
        >>> if not validate_secrets(["SLACK_BOT_TOKEN", "SLACK_WEBHOOK_URL"]):
        ...     sys.exit(1)
    """
    missing = []
    for key in required_keys:
        if not os.getenv(key):
            missing.append(key)
    
    if missing:
        logger.error(f"Missing required secrets: {', '.join(missing)}")
        logger.error(f"Add these to Zo settings: https://va.zo.computer/settings")
        return False
    
    logger.info(f"✓ All {len(required_keys)} required secrets present")
    return True


def mask_secret(value: str, visible_chars: int = 4) -> str:
    """
    Mask a secret for safe logging/display.
    
    Args:
        value: Secret value to mask
        visible_chars: Number of characters to show at end
    
    Returns:
        Masked string (e.g., "xoxb-****-****-abc123")
    
    Examples:
        >>> masked = mask_secret("xoxb-REDACTED-EXAMPLE-TOKEN")
        >>> print(f"Token: {masked}")  # Token: ****cbZAd
    """
    if not value or len(value) <= visible_chars:
        return "****"
    
    return f"****{value[-visible_chars:]}"


# Convenience functions for common secrets

def get_slack_bot_token() -> str:
    """Get Slack bot token (convenience wrapper)."""
    return get_secret("SLACK_BOT_TOKEN")


def get_slack_webhook_url() -> str:
    """Get Slack webhook URL (convenience wrapper)."""
    return get_secret("SLACK_WEBHOOK_URL")


def get_slack_user_token() -> Optional[str]:
    """Get Slack user token (convenience wrapper, optional)."""
    return get_secret("SLACK_USER_TOKEN", required=False)


if __name__ == "__main__":
    # Self-test
    import sys
    logging.basicConfig(level=logging.INFO)
    
    print("N5 Secrets Management Library - Self Test")
    print("=" * 50)
    
    # Test environment
    print(f"\nZo user: {os.getenv('ZO_USER', 'not set')}")
    
    # Test available secrets
    test_keys = [
        "SLACK_BOT_TOKEN",
        "SLACK_WEBHOOK_URL", 
        "SLACK_USER_TOKEN",
        "GOOGLE_SERVICE_ACCOUNT_JSON"
    ]
    
    print("\nChecking secrets availability:")
    for key in test_keys:
        value = get_secret(key, required=False)
        status = "✓" if value else "✗"
        masked = mask_secret(value) if value else "not set"
        print(f"  {status} {key}: {masked}")
    
    print("\n" + "=" * 50)
    print("Self-test complete")
