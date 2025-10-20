#!/usr/bin/env python3
"""
Automatic reflection ingestion - processes [Reflect] emails without manual invocation.
Can be run as a scheduled task or one-shot.
"""
import argparse, json, logging, subprocess, sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG = Path("/home/workspace/N5/config/reflection-sources.json")
INGEST_SCRIPT = Path("/home/workspace/N5/scripts/reflection_ingest.py")

def load_config() -> dict:
    if not CONFIG.exists():
        logger.error(f"Config not found: {CONFIG}")
        return {}
    return json.loads(CONFIG.read_text())

def check_and_process() -> int:
    """Check for new emails and process them."""
    try:
        config = load_config()
        if not config.get("auto_process_email", False):
            logger.info("Auto-processing disabled in config")
            return 0
        
        logger.info("Checking for new [Reflect] emails...")
        
        # Run the main ingest script with email source
        result = subprocess.run(
            [sys.executable, str(INGEST_SCRIPT), "--source", "email"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("✓ Email check complete")
            if config.get("notify_on_complete", False):
                # TODO: Add notification logic here if desired
                pass
        else:
            logger.error(f"Email check failed: {result.stderr}")
            
        return result.returncode
        
    except Exception as e:
        logger.error(f"Auto-ingest failed: {e}", exc_info=True)
        return 1

def main():
    parser = argparse.ArgumentParser(description="Automatic reflection ingestion")
    parser.add_argument("--enable", action="store_true", help="Enable auto-processing scheduled task")
    parser.add_argument("--disable", action="store_true", help="Disable auto-processing scheduled task")
    parser.add_argument("--status", action="store_true", help="Check auto-processing status")
    parser.add_argument("--interval", type=int, default=10, help="Check interval in minutes (default: 10)")
    parser.add_argument("--run-once", action="store_true", help="Run one-time check (for scheduled task)")
    
    args = parser.parse_args()
    
    if args.enable:
        logger.info(f"Setting up scheduled task (every {args.interval} minutes)...")
        logger.info("NOTE: Use Zo's create_scheduled_task tool to set this up:")
        logger.info(f"  Instruction: 'Run python3 {__file__} --run-once'")
        logger.info(f"  Schedule: Every {args.interval} minutes")
        
        # Update config
        config = load_config()
        config["auto_process_email"] = True
        CONFIG.write_text(json.dumps(config, indent=2))
        logger.info("✓ Config updated - auto_process_email: true")
        logger.info("⚠️  You still need to create the scheduled task via Zo")
        return 0
        
    elif args.disable:
        config = load_config()
        config["auto_process_email"] = False
        CONFIG.write_text(json.dumps(config, indent=2))
        logger.info("✓ Auto-processing disabled in config")
        logger.info("⚠️  Don't forget to delete the scheduled task via Zo if it exists")
        return 0
        
    elif args.status:
        config = load_config()
        enabled = config.get("auto_process_email", False)
        logger.info(f"Auto-processing: {'ENABLED' if enabled else 'DISABLED'}")
        return 0
        
    elif args.run_once:
        return check_and_process()
        
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
