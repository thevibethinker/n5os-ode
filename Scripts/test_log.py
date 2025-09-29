#!/usr/bin/env python3
import json
from pathlib import Path

AUDIT_LOG = Path("/home/workspace/runtime/audit/core_audit.log")

result = {"test": "hello"}
with AUDIT_LOG.open("a") as f:
    f.write(json.dumps(result) + "\n")

print("done")