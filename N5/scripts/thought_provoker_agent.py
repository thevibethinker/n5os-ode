#!/usr/bin/env python3
"""
Thought Provoker Agent Wrapper

Runs the scan and notification logic in sequence.
"""

import subprocess
import os

def run():
    # 1. Run Scan
    print("Running Scan...")
    subprocess.run(["python3", "/home/workspace/N5/scripts/thought_provoker_scan.py"])
    
    # 2. Run Notify check
    print("Checking for notifications...")
    result = subprocess.run(["python3", "/home/workspace/N5/scripts/notify_thought_provoker.py"], capture_output=True, text=True)
    
    if "NOTIFICATION_READY:" in result.stdout:
        message = result.stdout.split("NOTIFICATION_READY:")[1].strip()
        print(f"Agent triggered notification: {message}")
        # The Zo-Agent running this task will see this and send the SMS if instructed.

if __name__ == "__main__":
    run()

