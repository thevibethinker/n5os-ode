#!/usr/bin/env python3
import os, sys, time, json, logging
from pathlib import Path
from urllib.parse import urljoin
import argparse
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger("zobridge-health")

ROOT = Path("/home/workspace/N5/services/zobridge")
CONFIG_PATH = ROOT / "zobridge.config.json"
STATUS_MD = ROOT / "HEALTH_STATUS.md"
STATUS_JSON = ROOT / "HEALTH_STATUS.json"

DEFAULT_CHILD_URL = "https://zobridge-vademonstrator.zocomputer.io"
DEFAULT_PARENT_URL = "https://zobridge-va.zocomputer.io"

class Health:
    def __init__(self):
        self.parent_ok = False
        self.child_outbox_ok = False
        self.last_parent_ok = None
        self.last_child_ok = None
        self.consec_fail_parent = 0
        self.consec_fail_child = 0
        self.total_checks = 0

    def snapshot(self):
        return {
            "parent_ok": self.parent_ok,
            "child_outbox_ok": self.child_outbox_ok,
            "last_parent_ok": self.last_parent_ok,
            "last_child_ok": self.last_child_ok,
            "consec_fail_parent": self.consec_fail_parent,
            "consec_fail_child": self.consec_fail_child,
            "total_checks": self.total_checks,
        }

def load_secret() -> str:
    try:
        data = json.loads(CONFIG_PATH.read_text())
        if data.get("secret"): return data["secret"]
    except Exception:
        pass
    return os.environ.get("ZOBRIDGE_SECRET", "")

def http_get(url: str, headers: dict | None = None, timeout: float = 8.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read()

def write_status(h: Health):
    snapshot = h.snapshot()
    STATUS_JSON.write_text(json.dumps(snapshot, indent=2))
    lines = [
        "# ZoBridge Health Status",
        "",
        f"- Parent health: {'OK' if h.parent_ok else 'FAIL'} (consec_fail={h.consec_fail_parent})",
        f"- Child outbox: {'OK' if h.child_outbox_ok else 'FAIL'} (consec_fail={h.consec_fail_child})",
        f"- Last parent OK: {h.last_parent_ok}",
        f"- Last child OK: {h.last_child_ok}",
        f"- Total checks: {h.total_checks}",
        "",
        "Notes: This file is updated by health_monitor.py."
    ]
    STATUS_MD.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    child_url = os.environ.get("CHILDZO_URL", DEFAULT_CHILD_URL)
    parent_url = os.environ.get("PARENTZO_URL", DEFAULT_PARENT_URL)
    secret = load_secret()

    if not secret:
        logger.warning("No secret found; health checks will run without auth headers")

    headers = {"Authorization": f"Bearer {secret}"} if secret else {}

    h = Health()
    logger.info(f"Starting health monitor interval={args.interval}s parent={parent_url} child={child_url}")

    while True:
        h.total_checks += 1
        # Parent health
        try:
            code, _ = http_get(urljoin(parent_url, "/api/zobridge/health"), timeout=6.0)
            if 200 <= code < 300:
                h.parent_ok = True
                h.consec_fail_parent = 0
                h.last_parent_ok = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            else:
                h.parent_ok = False
                h.consec_fail_parent += 1
                logger.warning(f"Parent health non-2xx: {code}")
        except Exception as e:
            h.parent_ok = False
            h.consec_fail_parent += 1
            logger.error(f"Parent health error: {e}")

        # Child outbox basic
        try:
            code, body = http_get(urljoin(child_url, "/api/zobridge/outbox?to=ParentZo"), headers=headers, timeout=8.0)
            if 200 <= code < 300:
                h.child_outbox_ok = True
                h.consec_fail_child = 0
                h.last_child_ok = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            else:
                h.child_outbox_ok = False
                h.consec_fail_child += 1
                logger.warning(f"Child outbox non-2xx: {code}")
        except Exception as e:
            h.child_outbox_ok = False
            h.consec_fail_child += 1
            logger.error(f"Child outbox error: {e}")

        write_status(h)

        # Soft alerting to logs on repeated failures (no external email/text without approval)
        if h.consec_fail_parent >= 3:
            logger.error("ALERT: Parent health failing 3+ consecutive checks")
        if h.consec_fail_child >= 3:
            logger.error("ALERT: Child outbox failing 3+ consecutive checks")

        time.sleep(args.interval)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Health monitor stopped")
        sys.exit(0)
