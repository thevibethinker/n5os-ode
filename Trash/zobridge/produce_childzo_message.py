#!/usr/bin/env python3
import argparse, json, logging, time, uuid
from urllib.parse import urljoin
import sys
import os
import urllib.request

logging.basicConfig(level=logging.INFO, format='%(asctime)sZ %(levelname)s %(message)s')
logger = logging.getLogger("produce-childzo")

REQUIRED_FIELDS = ["message_id","timestamp","from","to","type","content"]

def build_message(msg_type: str, from_sys: str, to_sys: str, thread_id: str | None = None) -> dict:
    now = time.time()
    mid = f"{msg_type}_{int(now*1000)}_{uuid.uuid4().hex[:6]}"
    msg = {
        "message_id": mid,
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now)),
        "from": from_sys,
        "to": to_sys,
        "type": msg_type,
        "content": {"note": msg_type},
    }
    if thread_id:
        msg["thread_id"] = thread_id
    return msg

def validate_message(msg: dict) -> list[str]:
    errs = []
    for k in REQUIRED_FIELDS:
        if k not in msg:
            errs.append(f"missing {k}")
    return errs

def post_json(url: str, token: str, payload: dict) -> tuple[int, str]:
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type","application/json")
    req.add_header("Authorization", f"Bearer {token}")
    data = json.dumps(payload).encode("utf-8")
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return resp.getcode(), resp.read().decode("utf-8","ignore")
    except Exception as e:
        return 0, str(e)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--child-url", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--type", choices=["onboarding_created","status_update"], required=True)
    p.add_argument("--from-sys", default="ChildZo")
    p.add_argument("--to-sys", default="ParentZo")
    p.add_argument("--thread-id")
    args = p.parse_args()

    msg = build_message(args.type, args.from_sys, args.to_sys, args.thread_id)
    errs = validate_message(msg)
    if errs:
        logger.error(f"Invalid message: {errs}")
        return 1

    outbox_url = urljoin(args.child_url.rstrip('/')+'/', 'api/zobridge/outbox')
    code, body = post_json(outbox_url, args.token, msg)
    logger.info(f"POST {outbox_url} code={code} body={body[:300]}")
    print(json.dumps({"code": code, "response": body}))
    return 0 if code == 200 else 1

if __name__ == "__main__":
    sys.exit(main())
