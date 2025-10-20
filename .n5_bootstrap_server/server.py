#!/usr/bin/env python3
"""
N5 Bootstrap Support Server
Accepts status updates from new Zo (POST /status)
No command execution - logging only
"""

import http.server
import socketserver
import os
from pathlib import Path
from datetime import datetime, timezone

PORT = 8766
DIRECTORY = Path(__file__).parent
MONITOR_LOG = Path("/home/workspace/N5_BOOTSTRAP_MONITOR.log")

class MonitoringHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_POST(self):
        """Accept status updates - LOG ONLY, no execution"""
        if self.path == "/status":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                
                # Log to monitor file
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                with open(MONITOR_LOG, 'a') as f:
                    f.write(f"\n[{timestamp}] NEW ZO: {body}")
                
                print(f"[{timestamp}] Logged: {body}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "logged"}')
            except Exception as e:
                print(f"Error logging: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Unknown endpoint"}')
    
    def do_PUT(self):
        """Reject PUT"""
        self.send_error(405, "Method Not Allowed")
    
    def do_DELETE(self):
        """Reject DELETE"""
        self.send_error(405, "Method Not Allowed")
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    # Ensure monitor log exists
    MONITOR_LOG.touch(exist_ok=True)
    
    with socketserver.TCPServer(("", PORT), MonitoringHTTPRequestHandler) as httpd:
        print(f"🚀 N5 Bootstrap Support Server")
        print(f"📡 Port: {PORT}")
        print(f"📂 Serving: {DIRECTORY}")
        print(f"📝 Monitor log: {MONITOR_LOG}")
        print(f"✓ Accepts: GET (files) + POST /status (logging)")
        print(f"✗ No command execution")
        print(f"\n✓ Mobius Maneuver Active\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
