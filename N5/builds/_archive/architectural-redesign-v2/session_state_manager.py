#!/usr/bin/env python3
"""Session State Manager - Central state tracking for conversations"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path("/home/.z/workspaces")
USER_WORKSPACE = Path("/home/workspace")