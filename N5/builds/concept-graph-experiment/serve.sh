#!/bin/bash
# Serve the concept graph visualizer locally
cd "$(dirname "$0")/visualizer"
echo "Starting server at http://localhost:8890"
echo "Press Ctrl+C to stop"
python3 -m http.server 8890
