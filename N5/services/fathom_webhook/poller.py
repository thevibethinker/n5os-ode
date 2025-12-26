"""
Webhook Poller Service
Periodically checks for pending webhooks and processes them
"""

import time
import logging
import signal
import sys
from typing import Optional

from .transcript_processor import TranscriptProcessor
from .config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

class WebhookPoller:
    """Polls for pending webhooks and processes them"""
    
    def __init__(
        self,
        interval_seconds: int = 60,
        batch_size: int = 10
    ):
        self.interval = interval_seconds
        self.batch_size = batch_size
        self.processor = TranscriptProcessor()
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def start(self):
        """Start polling loop"""
        logger.info(f"Starting Fathom webhook poller (interval={self.interval}s, batch={self.batch_size})")
        
        # Validate configuration
        valid, error = Config.validate()
        if not valid:
            logger.error(f"Configuration invalid: {error}")
            sys.exit(1)
        
        # Test Fathom API connection
        if not self.processor.fathom_client.test_connection():
            logger.error("Failed to connect to Fathom API")
            # We don't sys.exit(1) here in case it's a transient network issue, 
            # but we log it. Actually, for a service, we should probably keep trying.
        
        self.running = True
        
        while self.running:
            try:
                logger.info("Checking for pending webhooks...")
                stats = self.processor.process_pending_webhooks(limit=self.batch_size)
                
                if stats["processed"] > 0:
                    logger.info(f"Batch complete: {stats}")
                else:
                    logger.info("No pending webhooks")
                
                # Sleep until next interval
                if self.running:
                    time.sleep(self.interval)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(self.interval)
        
        logger.info("Webhook poller stopped")

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fathom Webhook Poller")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds")
    parser.add_argument("--batch", type=int, default=10, help="Batch size per poll")
    
    args = parser.parse_args()
    
    poller = WebhookPoller(
        interval_seconds=args.interval,
        batch_size=args.batch
    )
    
    poller.start()

if __name__ == "__main__":
    main()


