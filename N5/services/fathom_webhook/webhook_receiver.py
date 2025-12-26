import logging
import uuid
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import JSONResponse

from .config import Config
from .models import FathomWebhookPayload, WebhookResponse, HealthResponse
from .webhook_processor import WebhookProcessor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

processor = WebhookProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Fathom webhook receiver service")
    is_valid, error = Config.validate()
    if not is_valid:
        logger.error(f"Configuration validation failed: {error}")
    else:
        logger.info("Configuration validated successfully")
    
    logger.info(f"Database: {Config.DATABASE_PATH}")
    logger.info(f"API Key configured: {bool(Config.FATHOM_API_KEY)}")
    logger.info(f"Webhook secret configured: {bool(Config.WEBHOOK_SECRET)}")
    
    yield
    
    logger.info("Shutting down Fathom webhook receiver service")

app = FastAPI(
    title="Fathom Webhook Receiver",
    description="Production webhook endpoint for Fathom transcript delivery",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="fathom_webhook",
        timestamp=datetime.utcnow().isoformat(),
        database_connected=Config.DATABASE_PATH.exists(),
        api_key_configured=bool(Config.FATHOM_API_KEY)
    )

@app.post("/webhook/fathom", response_model=WebhookResponse)
async def receive_webhook(
    request: Request,
    webhook_id: Optional[str] = Header(None, alias="webhook-id"),
    webhook_signature: Optional[str] = Header(None, alias="webhook-signature")
):
    # Fathom provides webhook-id in header, use it or generate one
    effective_id = webhook_id or str(uuid.uuid4())
    
    try:
        raw_body = await request.body()
        
        if len(raw_body) > Config.MAX_REQUEST_SIZE_BYTES:
            logger.error(f"Request size {len(raw_body)} exceeds limit")
            raise HTTPException(status_code=413, detail="Request too large")
        
        # Verification
        if not processor.verify_fathom_signature(raw_body, webhook_signature):
            logger.error(f"Signature verification failed for webhook {effective_id}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        raw_payload = raw_body.decode("utf-8")
        try:
            payload = FathomWebhookPayload.model_validate_json(raw_payload)
        except Exception as e:
            logger.error(f"Failed to parse Fathom payload for webhook {effective_id}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
        
        success = processor.log_webhook(effective_id, payload, raw_payload)
        
        if not success:
            logger.error(f"Failed to log Fathom webhook {effective_id}")
            raise HTTPException(status_code=500, detail="Failed to log webhook")
        
        logger.info(
            f"Fathom Webhook {effective_id} received: "
            f"recording={payload.recording_id}, title={payload.title}"
        )
        
        return WebhookResponse(
            status="received",
            webhook_id=effective_id,
            message=f"Webhook queued for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing Fathom webhook {effective_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {
        "service": "Fathom Webhook Receiver",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/fathom"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "webhook_receiver:app",
        host=Config.HOST,
        port=Config.PORT,
        log_level="info",
        access_log=True
    )

