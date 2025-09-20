#!/usr/bin/env python3
"""
Simple Test Data Generator
"""

import os
import json
from datetime import datetime

def create_test_conversations():
    """Create test conversation files"""
    
    test_dir = "/home/workspace/N5/tmp_execution/test_data"
    os.makedirs(test_dir, exist_ok=True)
    
    # Test conversation 1: File analysis
    conversation1 = """User: I need a command to analyze log files for errors.