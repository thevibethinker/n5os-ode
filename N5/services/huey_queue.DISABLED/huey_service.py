#!/usr/bin/env python3
import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

LOG_OUT = "/dev/shm/meeting-huey-worker.log"
LOG_ERR = "/dev/shm/meeting-huey-worker_err.log"

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/health') or self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"ok\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        # quiet
        return


def start_huey_consumer():
    # Ensure our services package is importable
    sys.path.insert(0, "/home/workspace/N5/services")
    env = os.environ.copy()
    env["PYTHONPATH"] = "/home/workspace/N5/services:" + env.get("PYTHONPATH", "")

    # Prepare logs
    out_f = open(LOG_OUT, 'a')
    err_f = open(LOG_ERR, 'a')

    # Start huey consumer
    proc = subprocess.Popen(
        ["huey_consumer", "huey_queue.config.huey", "-w", "3", "-k", "thread", "-l", LOG_OUT],
        stdout=out_f, stderr=err_f, env=env, cwd="/home/workspace/N5/services"
    )
    return proc, out_f, err_f


def run_http_server(port: int):
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()

    # Start Huey
    proc, out_f, err_f = start_huey_consumer()

    # HTTP server for health
    t = threading.Thread(target=run_http_server, args=(args.port,), daemon=True)
    t.start()

    # Handle signals
    stop = threading.Event()

    def handle_sigterm(signum, frame):
        stop.set()

    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    try:
        while not stop.is_set():
            if proc.poll() is not None:
                # consumer died; restart
                out_f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} consumer exited with {proc.returncode}, restarting...\n")
                out_f.flush()
                proc, out_f, err_f = start_huey_consumer()
            time.sleep(2)
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        out_f.close()
        err_f.close()

if __name__ == "__main__":
    sys.exit(main())
