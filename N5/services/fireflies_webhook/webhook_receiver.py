import logging
import uuid
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Header
from fastapi.responses import JSONResponse

from .config import Config
from .models import FirefliesWebhookPayload, WebhookResponse, HealthResponse
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
    logger.info("Starting Fireflies webhook receiver service")
    is_valid, error = Config.validate()
    if not is_valid:
        logger.error(f"Configuration validation failed: {error}")
    else:
        logger.info("Configuration validated successfully")
    
    logger.info(f"Database: {Config.DATABASE_PATH}")
    logger.info(f"API Key configured: {bool(Config.FIREFLIES_API_KEY)}")
    logger.info(f"Webhook secret configured: {bool(Config.WEBHOOK_SECRET)}")
    
    yield
    
    logger.info("Shutting down Fireflies webhook receiver service")

app = FastAPI(
    title="Fireflies Webhook Receiver",
    description="Production webhook endpoint for Fireflies transcript delivery",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="fireflies_webhook",
        timestamp=datetime.utcnow().isoformat(),
        database_connected=Config.DATABASE_PATH.exists(),
        api_key_configured=bool(Config.FIREFLIES_API_KEY)
    )

@app.post("/webhook/fireflies", response_model=WebhookResponse)
async def receive_webhook(
    request: Request,
    x_fireflies_signature: Optional[str] = Header(None, alias="X-Fireflies-Signature"),
    x_hub_signature: Optional[str] = Header(None, alias="x-hub-signature")
):
    webhook_id = str(uuid.uuid4())
    
    try:
        raw_body = await request.body()
        raw_payload = raw_body.decode("utf-8")
        
        if len(raw_body) > Config.MAX_REQUEST_SIZE_BYTES:
            logger.error(f"Request size {len(raw_body)} exceeds limit")
            raise HTTPException(status_code=413, detail="Request too large")
        
        signature = x_fireflies_signature or x_hub_signature
        
        if not processor.verify_hmac_signature(raw_payload, signature):
            logger.error(f"HMAC verification failed for webhook {webhook_id}")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        try:
            payload = FirefliesWebhookPayload.model_validate_json(raw_payload)
        except Exception as e:
            logger.error(f"Failed to parse payload for webhook {webhook_id}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
        
        success = processor.log_webhook(webhook_id, payload, raw_payload)
        
        if not success:
            logger.error(f"Failed to log webhook {webhook_id}")
            raise HTTPException(status_code=500, detail="Failed to log webhook")
        
        logger.info(
            f"Webhook {webhook_id} received: "
            f"transcript={payload.meetingId}, event={payload.eventType}"
        )
        
        return WebhookResponse(
            status="received",
            webhook_id=webhook_id,
            message=f"Webhook queued for processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook {webhook_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def root():
    return {
        "service": "Fireflies Webhook Receiver",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook/fireflies"
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

