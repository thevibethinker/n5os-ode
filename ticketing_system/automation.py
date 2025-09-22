#!/usr/bin/env python3
"""Simple directory watcher that auto-generates tickets."""
import json, time, os, pathlib, logging, sys
sys.path.append(str(pathlib.Path(__file__).parent))
from pipeline import generate_ticket

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
MEET_DIR = pathlib.Path("/home/workspace/ticketing_system/meetings")
PROCESSED = MEET_DIR / ".processed"
PROCESSED.touch(exist_ok=True)
processed = set(PROCESSED.read_text().splitlines())

while True:
    MEET_DIR.mkdir(parents=True, exist_ok=True)
    for p in MEET_DIR.glob("*.json"):
        if p.name in processed:
            continue
        try:
            meeting = json.loads(p.read_text())
            ticket = generate_ticket(meeting)
            logging.info("Generated ticket %s from %s", ticket["id"], p.name)
            processed.add(p.name)
            PROCESSED.write_text("\n".join(sorted(processed)))
        except Exception as e:
            logging.error("Failed processing %s: %s", p, e)
    time.sleep(60)
