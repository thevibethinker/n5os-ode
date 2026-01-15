#!/bin/bash
cd /home/workspace/N5/builds/position-viz
exec python3 -m http.server ${PORT:-8790}


