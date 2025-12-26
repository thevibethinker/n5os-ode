import os
from pathlib import Path
from typing import Optional

class Config:
    FATHOM_API_KEY: str = os.getenv("FATHOM_API_KEY", "")
    WEBHOOK_SECRET: str = os.getenv("FATHOM_WEBHOOK_SECRET", "")
    
    # Use the same database as fireflies or a dedicated one? 
    # V said "works the same as fireflies", let's use a similar pattern.
    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "/home/workspace/N5/data/meeting_pipeline.db"))
    
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "/home/workspace/N5/logs/fathom_webhook.log"))
    ERROR_LOG_FILE: Path = LOG_FILE.parent / (LOG_FILE.stem + "_err.log")
    
    PORT: int = int(os.getenv("PORT", "8763")) # Different port from fireflies (8767)
    HOST: str = "0.0.0.0"
    
    MAX_REQUEST_SIZE_BYTES: int = 10 * 1024 * 1024
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        if not cls.FATHOM_API_KEY:
            return False, "FATHOM_API_KEY environment variable not set"
        
        # Ensure data directory exists
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        return True, None
    
    @classmethod
    def get_api_key(cls) -> str:
        if not cls.FATHOM_API_KEY:
            raise ValueError("FATHOM_API_KEY not configured")
        return cls.FATHOM_API_KEY
    
    @classmethod
    def get_webhook_secret(cls) -> str:
        return cls.WEBHOOK_SECRET


