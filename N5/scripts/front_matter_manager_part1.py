#!/usr/bin/env python3
"""
Front Matter Manager for N5 OS (Zo-LLM edition)
Programmatically applies, updates, and validates front matter using Zo’s local LLM.
"""

import yaml
import hashlib
import re
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SCHEMA_PATH = Path('/home/workspace/N5_mirror/config/front_matter_schema.yaml')
if not SCHEMA_PATH.exists():
    default_schema = {
        '.md': {
            'title': None,
            'date': None,
            'version': '1.0',
            'status': 'production-ready',
            'category': None,
            'tags': [],
            'related_files': [],
            'anchors': {},
            'validation': 'n5os-compliant',
            'last-tested': None
        },
        '.json': {
            'source': None,
            'generated_date': None,
            'priority': 'medium',
            'tags': [],
            'related_files': [],
            'voice_schema': {},
            'checksum': None
        }
    }
    SCHEMA_PATH.parent.mkdir(exist_ok=True)
    with open(SCHEMA_PATH, 'w') as f:
        yaml.dump(default_schema, f)
SCHEMA = yaml.safe_load(open(SCHEMA_PATH))
