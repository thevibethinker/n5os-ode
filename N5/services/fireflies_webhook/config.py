import os
from pathlib import Path
from typing import Optional

class Config:
    FIREFLIES_API_KEY: str = os.getenv("FIREFLIES_API_KEY", "")
    WEBHOOK_SECRET: str = os.getenv("FIREFLIES_WEBHOOK_SECRET", "")
    
    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "/home/workspace/N5/data/meeting_pipeline.db"))
    
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "/home/workspace/N5/logs/fireflies_webhook.log"))
    ERROR_LOG_FILE: Path = LOG_FILE.parent / (LOG_FILE.stem + "_err.log")
    
    PORT: int = int(os.getenv("PORT", "8767"))
    HOST: str = "0.0.0.0"
    
    RATE_LIMIT_PER_MINUTE: int = 100
    MAX_REQUEST_SIZE_BYTES: int = 10 * 1024 * 1024
    
    RESPONSE_TIMEOUT_MS: int = 500
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        if not cls.FIREFLIES_API_KEY:
            return False, "FIREFLIES_API_KEY environment variable not set"
        
        if not cls.DATABASE_PATH.exists():
            return False, f"Database not found at {cls.DATABASE_PATH}"
        
        return True, None
    
    @classmethod
    def get_api_key(cls) -> str:
        if not cls.FIREFLIES_API_KEY:
            raise ValueError("FIREFLIES_API_KEY not configured")
        return cls.FIREFLIES_API_KEY
    
    @classmethod
    def get_webhook_secret(cls) -> str:
        if not cls.WEBHOOK_SECRET:
            return ""
        return cls.WEBHOOK_SECRET



