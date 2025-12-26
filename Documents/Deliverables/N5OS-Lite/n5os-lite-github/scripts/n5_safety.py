#!/usr/bin/env python3
"""
N5 Safety Checker
Detects mock/placeholder/stub data in production code and artifacts.
Prevents development artifacts from polluting production systems.
"""
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

MOCK_PATTERNS = [
    (r'\b(MOCK|DEMO|STUB|PLACEHOLDER|FAKE|DUMMY|EXAMPLE|TEST_DATA)\b', 'Mock identifier'),
    (r'example\.com|test@example|fake_\w+', 'Placeholder data'),
    (r'TODO:|FIXME:|XXX:|HACK:', 'Unfinished code marker'),
    (r'lorem\s+ipsum', 'Lorem ipsum placeholder text'),
    (r'foo|bar|baz|qux', 'Generic placeholder variable'),
    (r'alice|bob|charlie(?!\w)', 'Generic test names'),
]

PRODUCTION_PATHS = [
    'N5/scripts',
    'N5/workflows',
    'Personal',
    'Knowledge',
    'Lists',
]

def check_file_for_mocks(filepath: Path) -> List[Dict]:
    """Scan single file for mock/placeholder patterns."""
    violations = []
    
    # Check filename
    fname_upper = filepath.name.upper()
    if any(keyword in fname_upper for keyword in ['MOCK', 'DEMO', 'STUB', 'TEST_', 'EXAMPLE']):
        violations.append({
            'file': str(filepath),
            'line': 0,
            'type': 'filename',
            'severity': 'high',
            'pattern': 'Mock identifier in filename',
            'match': filepath.name
        })
    
    # Check content for text files
    if filepath.suffix in ['.py', '.sh', '.md', '.txt', '.json', '.yaml', '.yml']:
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern, desc in MOCK_PATTERNS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip comments in Python
                        if filepath.suffix == '.py' and line.strip().startswith('#'):
                            continue
                        
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'content',
                            'severity': 'medium',
                            'pattern': desc,
                            'match': match.group(0),
                            'context': line.strip()[:80]
                        })
        except Exception as e:
            violations.append({
                'file': str(filepath),
                'line': 0,
                'type': 'error',
                'severity': 'low',
                'pattern': 'Read error',
                'match': str(e)
            })
    
    return violations

def scan_directory(directory: Path, recursive: bool = True) -> Dict:
    """Scan directory for mock data violations."""
    results = {
        'scanned': 0,
        'violations': [],
        'high_severity': 0,
        'medium_severity': 0,
        'low_severity': 0
    }
    
    pattern = '**/*' if recursive else '*'
    for filepath in directory.glob(pattern):
        if not filepath.is_file():
            continue
        if '.git' in filepath.parts:
            continue
        
        results['scanned'] += 1
        violations = check_file_for_mocks(filepath)
        
        for v in violations:
            results['violations'].append(v)
            if v['severity'] == 'high':
                results['high_severity'] += 1
            elif v['severity'] == 'medium':
                results['medium_severity'] += 1
            else:
                results['low_severity'] += 1
    
    return results

def check_production_paths(workspace: Path = Path('/home/workspace')) -> Dict:
    """Check all production paths for mock data."""
    overall_results = {
        'total_scanned': 0,
        'total_violations': 0,
        'by_path': {},
        'high_priority': []
    }
    
    for prod_path in PRODUCTION_PATHS:
        full_path = workspace / prod_path
        if not full_path.exists():
            continue
        
        results = scan_directory(full_path, recursive=True)
        overall_results['total_scanned'] += results['scanned']
        overall_results['total_violations'] += len(results['violations'])
        overall_results['by_path'][prod_path] = results
        
        # Collect high-severity violations
        for v in results['violations']:
            if v['severity'] == 'high':
                overall_results['high_priority'].append(v)
    
    return overall_results

def format_report(results: Dict) -> str:
    """Format scan results as readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("N5 SAFETY CHECK: MOCK DATA DETECTION")
    lines.append("=" * 70)
    lines.append(f"Total files scanned: {results['total_scanned']}")
    lines.append(f"Total violations found: {results['total_violations']}")
    lines.append("")
    
    if results['high_priority']:
        lines.append("🚨 HIGH PRIORITY VIOLATIONS (filename-level)")
        lines.append("-" * 70)
        for v in results['high_priority']:
            lines.append(f"  {v['file']}")
            lines.append(f"    Pattern: {v['pattern']}")
            lines.append("")
    
    for path, path_results in results['by_path'].items():
        if path_results['violations']:
            lines.append(f"📁 {path}")
            lines.append(f"   High: {path_results['high_severity']} | Medium: {path_results['medium_severity']} | Low: {path_results['low_severity']}")
            
            # Show first 5 violations for this path
            for v in path_results['violations'][:5]:
                if v['type'] != 'filename':
                    lines.append(f"   Line {v['line']}: {v['pattern']} → {v['match']}")
            
            if len(path_results['violations']) > 5:
                lines.append(f"   ... and {len(path_results['violations']) - 5} more")
            lines.append("")
    
    lines.append("=" * 70)
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='N5 Safety: Mock Data Detection')
    parser.add_argument('command', choices=['scan', 'check'], help='scan=full report, check=exit code only')
    parser.add_argument('--path', help='Specific path to check (default: all production paths)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}", file=sys.stderr)
            sys.exit(1)
        results = scan_directory(path)
        results_dict = {'by_path': {str(path): results}, 'total_scanned': results['scanned'], 'total_violations': len(results['violations']), 'high_priority': [v for v in results['violations'] if v['severity'] == 'high']}
    else:
        results_dict = check_production_paths()
    
    if args.json:
        print(json.dumps(results_dict, indent=2))
    else:
        report = format_report(results_dict)
        print(report)
    
    # Exit code: 0 if no high-severity, 1 if high-severity found
    sys.exit(1 if results_dict['high_priority'] else 0)

if __name__ == '__main__':
    main()
