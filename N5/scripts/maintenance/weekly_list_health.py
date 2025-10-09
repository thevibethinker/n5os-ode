#!/usr/bin/env python3
"""
Weekly List Health Check - List Validation & Maintenance

Runs weekly on Sundays at 20:00 ET.
Model: Claude Sonnet 4.5
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Setup logging
log_dir = Path("/home/workspace/N5/logs/maintenance/weekly")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"lists_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

LISTS_DIR = Path("/home/workspace/Lists")
STALE_THRESHOLD_DAYS = 30


def load_jsonl_list(filepath):
    """Load a JSONL list file."""
    items = []
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        items.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON parse error in {filepath.name}, line {line_num}: {e}")
        return items
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return None


def validate_schema(filepath, items):
    """Validate JSONL schema compliance."""
    logger.info(f"Validating schema for {filepath.name}")
    issues = []
    
    for idx, item in enumerate(items, 1):
        # Check for required fields
        if 'id' not in item:
            issues.append(f"Line {idx}: Missing 'id' field")
        
        if 'title' not in item:
            issues.append(f"Line {idx}: Missing 'title' field")
        
        if 'status' not in item:
            issues.append(f"Line {idx}: Missing 'status' field")
        
        # Check created_at format if present
        if 'created_at' in item:
            try:
                datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                issues.append(f"Line {idx}: Invalid 'created_at' format")
    
    if issues:
        logger.warning(f"Schema issues in {filepath.name}:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info(f"✓ {filepath.name} schema valid")
    
    return issues


def find_stale_items(filepath, items):
    """Identify items that haven't been updated recently."""
    logger.info(f"Checking for stale items in {filepath.name}")
    
    cutoff_date = datetime.now() - timedelta(days=STALE_THRESHOLD_DAYS)
    stale_items = []
    
    for item in items:
        # Check updated_at or created_at
        date_field = item.get('updated_at') or item.get('created_at')
        
        if date_field:
            try:
                item_date = datetime.fromisoformat(date_field.replace('Z', '+00:00'))
                
                # Only flag open/pending items as stale
                status = item.get('status', '').lower()
                if status in ['open', 'pending', 'planned'] and item_date < cutoff_date:
                    age_days = (datetime.now() - item_date).days
                    stale_items.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'age_days': age_days,
                        'status': status
                    })
            except (ValueError, AttributeError):
                pass
    
    if stale_items:
        logger.warning(f"Found {len(stale_items)} stale item(s) in {filepath.name}:")
        for item in stale_items[:5]:  # Show first 5
            logger.warning(f"  - {item['id']}: {item['title']} ({item['age_days']} days old)")
        if len(stale_items) > 5:
            logger.warning(f"  ... and {len(stale_items) - 5} more")
    else:
        logger.info(f"✓ No stale items in {filepath.name}")
    
    return stale_items


def find_duplicates(filepath, items):
    """Detect potential duplicate items."""
    logger.info(f"Checking for duplicates in {filepath.name}")
    
    title_map = defaultdict(list)
    
    for item in items:
        title = item.get('title', '').lower().strip()
        if title:
            title_map[title].append(item.get('id'))
    
    duplicates = {title: ids for title, ids in title_map.items() if len(ids) > 1}
    
    if duplicates:
        logger.warning(f"Found {len(duplicates)} potential duplicate(s) in {filepath.name}:")
        for title, ids in list(duplicates.items())[:3]:  # Show first 3
            logger.warning(f"  - '{title}': {ids}")
        if len(duplicates) > 3:
            logger.warning(f"  ... and {len(duplicates) - 3} more")
    else:
        logger.info(f"✓ No duplicates detected in {filepath.name}")
    
    return duplicates


def calculate_health_score(schema_issues, stale_count, duplicate_count, total_items):
    """Calculate overall health score (0-100)."""
    if total_items == 0:
        return 100
    
    # Deduct points for issues
    score = 100
    score -= min(len(schema_issues) * 5, 30)  # Max -30 for schema issues
    score -= min(stale_count * 2, 40)  # Max -40 for stale items
    score -= min(duplicate_count * 3, 30)  # Max -30 for duplicates
    
    return max(0, score)


def check_list_health(filepath):
    """Run full health check on a list."""
    logger.info(f"=== Checking {filepath.name} ===")
    
    items = load_jsonl_list(filepath)
    
    if items is None:
        return {
            'filepath': filepath,
            'success': False,
            'error': 'Failed to load file'
        }
    
    schema_issues = validate_schema(filepath, items)
    stale_items = find_stale_items(filepath, items)
    duplicates = find_duplicates(filepath, items)
    
    health_score = calculate_health_score(
        schema_issues,
        len(stale_items),
        len(duplicates),
        len(items)
    )
    
    logger.info(f"Health Score: {health_score}/100")
    
    return {
        'filepath': filepath,
        'success': True,
        'total_items': len(items),
        'schema_issues': len(schema_issues),
        'stale_items': len(stale_items),
        'duplicates': len(duplicates),
        'health_score': health_score
    }


def generate_summary(results):
    """Generate overall summary."""
    logger.info("=== Weekly List Health Summary ===")
    
    total_lists = len(results)
    successful = sum(1 for r in results if r['success'])
    avg_health = sum(r.get('health_score', 0) for r in results) / total_lists if total_lists > 0 else 0
    
    logger.info(f"Lists checked: {total_lists}")
    logger.info(f"Successful checks: {successful}")
    logger.info(f"Average health score: {avg_health:.1f}/100")
    
    # Show list-by-list summary
    for result in results:
        if result['success']:
            logger.info(f"  {result['filepath'].name}: {result['health_score']}/100 "
                       f"({result['total_items']} items, "
                       f"{result['stale_items']} stale, "
                       f"{result['duplicates']} dupes)")
    
    if avg_health >= 90:
        logger.info("✅ All lists are in excellent health")
    elif avg_health >= 70:
        logger.info("⚠️  Lists are in good health with minor issues")
    else:
        logger.warning("⚠️  Lists need attention - several issues detected")


def main():
    """Run weekly list health checks."""
    logger.info("=== Weekly List Health Check Started ===")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Stale threshold: {STALE_THRESHOLD_DAYS} days")
    
    # Find all JSONL lists
    list_files = list(LISTS_DIR.glob("*.jsonl"))
    
    if not list_files:
        logger.warning("No list files found in Lists directory")
        return 0
    
    logger.info(f"Found {len(list_files)} list file(s)")
    
    results = []
    for list_file in list_files:
        result = check_list_health(list_file)
        results.append(result)
    
    generate_summary(results)
    
    logger.info(f"=== Weekly List Health Check Completed ===")
    logger.info(f"Log saved to: {log_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
