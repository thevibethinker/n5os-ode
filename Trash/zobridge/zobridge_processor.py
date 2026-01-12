#!/usr/bin/env python3
import argparse, json, logging, sqlite3, time, signal, sys, os
from pathlib import Path
from typing import Any, Dict, Tuple
import urllib.request, urllib.error
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("zobridge-processor")

CONFIG_PATH = Path("/home/workspace/N5/services/zobridge/zobridge.config.json")
DB_PATH = Path("/home/workspace/N5/data/zobridge.db")
PROPOSALS_DIR = Path("/home/workspace/Records/Company/Proposals")
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

# ---- HTTP helpers ----

def _post_json(url: str, payload: Dict[str, Any], token: str, timeout: float = 15.0) -> Tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "zobridge-processor/1.0")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            body = resp.read().decode("utf-8", errors="ignore")
            return code, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else str(e)
        return e.code, body
    except Exception as e:
        return 0, str(e)


def post_child_inbox(child_url: str, token: str, message: Dict[str, Any], max_retries: int = 4) -> Tuple[int, str]:
    url = child_url.rstrip("/") + "/api/zobridge/inbox"
    delay = 1.0
    for attempt in range(1, max_retries + 1):
        code, body = _post_json(url, message, token)
        if code and code < 400:
            logger.info(f"ACK posted to ChildZo inbox code={code} id={message.get('message_id')}")
            return code, body
        logger.warning(f"ACK post attempt {attempt} failed code={code} body={body[:180]}")
        if code in (429, 500, 502, 503, 504, 521):
            time.sleep(delay)
            delay = min(delay * 2, 12)
            continue
        break
    return code, body

# ---- DB helpers ----

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---- Processing ----

def write_proposal_files(base_id: str, title: str, details: Dict[str, Any]) -> Tuple[Path, Path]:
    md_path = PROPOSALS_DIR / f"proposal_{base_id}.md"
    meta_path = PROPOSALS_DIR / f"proposal_{base_id}.json"
    md = [
        f"# {title}\n",
        f"Message: {base_id}\n\n",
        "## Details\n",
        "```json\n",
        json.dumps(details, indent=2),
        "\n```\n",
    ]
    md_path.write_text("".join(md), encoding="utf-8")
    meta = {
        "message_id": base_id,
        "title": title,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paths": {"markdown": str(md_path)},
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return md_path, meta_path


def handle_message(row: sqlite3.Row, child_url: str, token: str, dry_run: bool = False) -> None:
    msg = {
        "message_id": row["message_id"],
        "timestamp": row["timestamp"],
        "from": row["from_system"],
        "to": row["to_system"],
        "type": row["type"],
        "thread_id": row["thread_id"],
        "content": json.loads(row["content_json"]) if "content_json" in row.keys() else json.loads(row["content_json"])  # minimal
    }
    content = msg.get("content") or {}
    action = content.get("action")
    title = content.get("title") or msg.get("type")

    if msg["type"] == "proposal" or action == "create_proposal":
        logger.info(f"Creating proposal for id={msg['message_id']} title={title}")
        if not dry_run:
            md_path, _ = write_proposal_files(msg["message_id"], title, content)

            # Build and post ACK to ChildZo with a fresh ID each attempt
            inbox_url = child_url.rstrip("/") + "/api/zobridge/inbox"
            delay, max_delay = 1.0, 12.0
            last_code, last_body = 0, ""
            for attempt in range(1, 6):
                ack_id = f"resp_{time.time_ns()}"
                resp = {
                    "message_id": ack_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "from": "ParentZo",
                    "to": "ChildZo",
                    "type": "response",
                    "thread_id": msg.get("thread_id"),
                    "content": {
                        "status": "proposal_created",
                        "for": msg["message_id"],
                        "proposal_path": str(md_path),
                    },
                }
                code, body = _post_json(inbox_url, resp, token)
                last_code, last_body = code, body
                logger.info(f"ACK attempt={attempt} id={ack_id} code={code}")
                if code and code < 400:
                    break
                # Retry on duplicate/5xx/Cloudflare
                if code in (409, 429, 500, 502, 503, 504, 521) or (isinstance(body, str) and ("UNIQUE constraint" in body or "duplicate" in body.lower())):
                    time.sleep(delay)
                    delay = min(delay * 1.8, max_delay)
                    continue
                else:
                    break
            logger.info(f"ACK result code={last_code} body_head={(last_body or '')[:120]}")
        # Mark processed regardless (idempotent upstream)
        with get_db() as c2:
            c2.execute("UPDATE messages SET processed=1 WHERE message_id=?", (msg["message_id"],))
        return

    logger.info(f"No handler for type={msg['type']} action={action}; marking processed")
    with get_db() as c3:
        c3.execute("UPDATE messages SET processed=1 WHERE message_id=?", (msg["message_id"],))


# ---- Main loop ----

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=5)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--replay-id", type=str, default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
    token = cfg.get("secret") or os.environ.get("ZOBRIDGE_SECRET", "")
    child_url = os.environ.get("CHILDZO_URL", "https://zobridge-vademonstrator.zocomputer.io")

    logger.info(f"ZoBridge processor started db={DB_PATH}")

    def cycle():
        with get_db() as conn:
            if args.replay_id:
                row = conn.execute("SELECT * FROM messages WHERE message_id=?", (args.replay_id,)).fetchone()
                if row:
                    handle_message(row, child_url, token, args.dry_run)
                return
            rows = conn.execute("SELECT * FROM messages WHERE processed=0 ORDER BY rowid ASC LIMIT 10").fetchall()
            if not rows:
                logger.info("No unprocessed messages.")
                return
            for r in rows:
                handle_message(r, child_url, token, args.dry_run)

    if args.once:
        cycle()
        return 0

    stop_flag = False
    def _sig(*_):
        nonlocal stop_flag
        stop_flag = True
    signal.signal(signal.SIGINT, _sig)
    signal.signal(signal.SIGTERM, _sig)

    while not stop_flag:
        cycle()
        for _ in range(args.interval):
            if stop_flag:
                break
            time.sleep(1)
    logger.info("Processor stopped.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
