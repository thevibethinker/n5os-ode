#!/usr/bin/env python3
import argparse, logging, sqlite3, time, json
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CONFIG_PATH = Path("/home/workspace/N5/config/zobridge.config.json")

def load_db_path() -> Path:
    cfg = json.loads(CONFIG_PATH.read_text())
    return Path(cfg["database_path"])  # e.g., /home/workspace/N5/data/zobridge.db

def fetch_unprocessed(conn: sqlite3.Connection, limit: int = 20):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT message_id, thread_id, from_system, to_system, type, content_json, timestamp
        FROM messages
        WHERE processed = 0
        ORDER BY timestamp ASC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cur.fetchall()
    msgs = []
    for r in rows:
        msgs.append({
            "message_id": r[0],
            "thread_id": r[1],
            "from": r[2],
            "to": r[3],
            "type": r[4],
            "content": json.loads(r[5] or "{}"),
            "timestamp": r[6],
        })
    return msgs

def mark_processed(conn: sqlite3.Connection, message_id: str, response_id: str | None = None):
    cur = conn.cursor()
    cur.execute(
        "UPDATE messages SET processed = 1, response_id = ? WHERE message_id = ?",
        (response_id, message_id),
    )
    conn.commit()


def do_work(dry_run: bool = False, interval: float = 5.0) -> int:
    db_path = load_db_path()
    if not db_path.exists():
        logger.error(f"DB not found: {db_path}")
        return 1
    conn = sqlite3.connect(str(db_path))
    try:
        while True:
            msgs = fetch_unprocessed(conn, limit=20)
            if msgs:
                logger.info(f"Found {len(msgs)} unprocessed messages")
            for m in msgs:
                try:
                    logger.info(f"Processing message {m['message_id']} type={m['type']} from={m['from']} -> {m['to']}")
                    # Placeholder: execute instruction/route by type
                    # For now, just log the content summary length
                    logger.info(f"Content size={len(json.dumps(m['content']))} bytes")
                    if not dry_run:
                        mark_processed(conn, m["message_id"], None)
                        logger.info(f"Marked processed: {m['message_id']}")
                    else:
                        logger.info(f"[DRY RUN] Would mark processed: {m['message_id']}")
                except Exception as e:
                    logger.error(f"Error processing {m['message_id']}: {e}", exc_info=True)
            time.sleep(interval)
    finally:
        conn.close()
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    try:
        exit(do_work(dry_run=args.dry_run, interval=args.interval))
    except KeyboardInterrupt:
        logger.info("Shutting down")
        exit(0)

if __name__ == "__main__":
    main()
