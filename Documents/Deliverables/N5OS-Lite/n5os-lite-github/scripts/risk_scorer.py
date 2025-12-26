#!/usr/bin/env python3
"""
Systemic Risk Scorer - Assess blast radius before operations
References: N5/prefs/system/risk-scoring-framework.yaml
"""

import sys
import json
import yaml
import subprocess
from pathlib import Path

FRAMEWORK_PATH = Path("/home/workspace/N5/prefs/system/risk-scoring-framework.yaml")
WORKSPACE = Path("/home/workspace")

def load_framework():
    with open(FRAMEWORK_PATH) as f:
        return yaml.safe_load(f)

def count_references(filepath):
    """Count how many files reference this one"""
    try:
        result = subprocess.run(
            ['grep', '-r', '-l', str(filepath), str(WORKSPACE)],
            capture_output=True, text=True, timeout=5
        )
        return len(result.stdout.strip().split('\n')) if result.stdout else 0
    except:
        return 0

def check_protection(filepath):
    """Check if file is protected"""
    try:
        result = subprocess.run(
            ['python3', '/home/workspace/N5/scripts/n5_protect.py', 'check', str(filepath)],
            capture_output=True, text=True
        )
        return 'protected' in result.stdout.lower()
    except:
        return False

def score_operation(operation, filepath, framework):
    """Calculate composite risk score"""
    scores = {}
    path = Path(filepath)
    
    # Dependency Risk
    refs = count_references(filepath)
    if refs == 0:
        scores['dependency'] = 1
    elif refs <= 5:
        scores['dependency'] = 3
    elif refs <= 15:
        scores['dependency'] = 5
    else:
        scores['dependency'] = 8
    
    # Protection Risk
    if check_protection(filepath):
        scores['protection'] = 10
    elif 'N5/prefs' in str(path):
        scores['protection'] = 9
    elif 'N5/scripts' in str(path):
        scores['protection'] = 8
    elif 'Knowledge' in str(path):
        scores['protection'] = 7
    else:
        scores['protection'] = 3
    
    # State Risk (simplified)
    if 'SESSION_STATE' in path.name:
        scores['state'] = 9
    elif 'recipes.jsonl' in path.name or 'executables.db' in path.name:
        scores['state'] = 8
    elif 'architectural' in str(path):
        scores['state'] = 8
    else:
        scores['state'] = 2
    
    # Reversibility Risk
    if operation in ['delete', 'overwrite']:
        scores['reversibility'] = 10
    elif 'schema' in str(path):
        scores['reversibility'] = 8
    else:
        scores['reversibility'] = 3
    
    # Simplified cross-persona and recovery
    scores['cross_persona'] = 4
    scores['recovery'] = 5 if scores['protection'] > 7 else 2
    
    # Weighted composite
    weights = framework['composite_score']['weights']
    composite = sum(scores[k] * weights.get(f'{k}_risk', 0.15) for k in scores.keys())
    
    # Determine threshold
    thresholds = framework['composite_score']['thresholds']
    if composite <= thresholds['low_risk'][1]:
        threshold = 'low_risk'
    elif composite <= thresholds['medium_risk'][1]:
        threshold = 'medium_risk'
    elif composite <= thresholds['high_risk'][1]:
        threshold = 'high_risk'
    else:
        threshold = 'critical_risk'
    
    return {
        'operation': operation,
        'filepath': str(filepath),
        'scores': scores,
        'composite': round(composite, 2),
        'threshold': threshold,
        'action': framework['operator_behavior'][threshold]['action']
    }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: risk_scorer.py <operation> <filepath>")
        sys.exit(1)
    
    operation = sys.argv[1]
    filepath = sys.argv[2]
    framework = load_framework()
    
    result = score_operation(operation, filepath, framework)
    print(json.dumps(result, indent=2))
