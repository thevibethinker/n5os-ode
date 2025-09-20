#!/usr/bin/env python3
"""
Add and Launch Script for Temp Execution

This script adds items (commands or tasks) to a temporary execution queue file
and launches them asynchronously in new threads.

Usage:
    python3 add_and_launch.py "command1" "command2" ...

The commands are appended to execution_queue.txt in the same directory,
then each is executed in a separate background thread.
"""

import sys
import os
import subprocess
import threading
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to the execution queue file
QUEUE_FILE = Path(__file__).parent / "execution_queue.txt"

def add_to_queue(items):
    """Append items to the execution queue file."""
    with open(QUEUE_FILE, 'a') as f:
        for item in items:
            f.write(item + '\n')
    logger.info(f"Added {len(items)} items to {QUEUE_FILE}")

def launch_command(command):
    """Launch a single command asynchronously."""
    try:
        logger.info(f"Launching command: {command}")
        # Run the command in a subprocess
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logger.info(f"Command completed: {command}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        if result.stderr:
            logger.error(f"Error: {result.stderr}")
    except Exception as e:
        logger.error(f"Failed to launch command '{command}': {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 add_and_launch.py \"command1\" \"command2\" ...")
        sys.exit(1)

    items = sys.argv[1:]

    # Add items to queue
    add_to_queue(items)

    # Launch each command in a new thread
    threads = []
    for item in items:
        thread = threading.Thread(target=launch_command, args=(item,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete (optional, can be removed for fire-and-forget)
    for thread in threads:
        thread.join()

    logger.info("All commands launched.")

if __name__ == "__main__":
    main()