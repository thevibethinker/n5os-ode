import logging
# Cache System Integration (uncomment to use):
# from system_prep.cache_manager import CacheManager
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


def resolve_conflicts_and_suggest(validated_command: Dict[str, Any], 
                                 commands_file: str = "N5/commands.jsonl") -> Dict[str, Any]:
    """
    Scan for conflicts (e.g., duplicate commands), suggest adaptations.
    
    Args:
        validated_command: Validated command from enhancement layer
        commands_file: Path to commands.jsonl file
        
    Returns:
        Resolved command with suggestions
    """
    start_time = time.time()
    
    try:
        if 'error' in validated_command:
            logging.error(f"Cannot resolve conflicts for errored command: {validated_command['error']}")
            return validated_command
        
        # Perform preemptive scan
        scan_results = _preemptive_conflict_scan(validated_command, commands_file)
        
        # Apply conflict resolution
        resolution_results = _apply_conflict_resolution(validated_command, scan_results)
        
        # Generate suggestions
        suggestions = _generate_adaptation_suggestions(validated_command, scan_results)
        
        # Create resolved command
        resolved_command = validated_command.copy()
        resolved_command['conflict_resolution'] = {
            'timestamp': time.time(),
            'scan_results': scan_results,
            'resolution_applied': resolution_results,
            'suggestions': suggestions,
            'status': 'resolved' if not scan_results.get('critical_conflicts') else 'needs_attention',
            'processing_time': time.time() - start_time
        }
        
        # Apply automatic adaptations
        if resolution_results.get('auto_adaptations'):
            resolved_command = _apply_auto_adaptations(resolved_command, resolution_results['auto_adaptations'])
        
        # Telemetry logging
        processing_time = time.time() - start_time
        logging.info(f"Conflict resolution completed in {processing_time:.3f}s")
        
        if scan_results.get('conflicts_found', 0) > 0:
            logging.info(f"Found {scan_results['conflicts_found']} conflicts, applied {len(resolution_results.get('auto_adaptations', []))} auto-adaptations")
        
        if suggestions:
            logging.info(f"Generated {len(suggestions)} adaptation suggestions")
            for suggestion in suggestions[:3]:  # Log first 3 suggestions
                logging.debug(f"Suggestion: {suggestion.get('type', 'unknown')} - {suggestion.get('description', '')[:100]}")
        
        return resolved_command
        
    except Exception as e:
        logging.error(f"Conflict resolution failed: {e}")
        return {
            'error': str(e),
            'original_command': validated_command,
            'conflict_resolution_failed': True
        }


def _preemptive_conflict_scan(command: Dict[str, Any], commands_file: str) -> Dict[str, Any]:
    """Perform preemptive scan for conflicts."""
    scan_results = {
        'conflicts_found': 0,
        'duplicate_names': [],
        'similar_commands': [],
        'overlapping_functionality': [],
        'resource_conflicts': [],
        'dependency_conflicts': [],
        'critical_conflicts': [],
        'scan_time': 0
    }
    
    scan_start = time.time()
    
    try:
        # Load existing commands
        existing_commands = _load_existing_commands(commands_file)
        
        command_name = command.get('command', '')
        command_description = command.get('description', '').lower()
        command_steps = command.get('steps', [])
        
        # Check for duplicate names
        duplicate_names = _check_duplicate_names(command_name, existing_commands)
        scan_results['duplicate_names'] = duplicate_names
        if duplicate_names:
            scan_results['conflicts_found'] += len(duplicate_names)
            scan_results['critical_conflicts'].extend([
                {'type': 'duplicate_name', 'command': dup} for dup in duplicate_names
            ])
        
        # Check for similar functionality
        similar_commands = _check_similar_functionality(command, existing_commands)
        scan_results['similar_commands'] = similar_commands
        if similar_commands:
            scan_results['conflicts_found'] += len(similar_commands)
        
        # Check for overlapping functionality
        overlapping = _check_overlapping_functionality(command_steps, existing_commands)
        scan_results['overlapping_functionality'] = overlapping
        if overlapping:
            scan_results['conflicts_found'] += len(overlapping)
        
        # Check for resource conflicts
        resource_conflicts = _check_resource_conflicts(command, existing_commands)
        scan_results['resource_conflicts'] = resource_conflicts
        if resource_conflicts:
            scan_results['conflicts_found'] += len(resource_conflicts)
        
        # Check for dependency conflicts
        dependency_conflicts = _check_dependency_conflicts(command, existing_commands)
        scan_results['dependency_conflicts'] = dependency_conflicts
        if dependency_conflicts:
            scan_results['conflicts_found'] += len(dependency_conflicts)
        
        scan_results['scan_time'] = time.time() - scan_start
        
        logging.debug(f"Conflict scan completed: {scan_results['conflicts_found']} conflicts found")
        
        return scan_results
        
    except Exception as e:
        logging.error(f"Conflict scan failed: {e}")
        scan_results['error'] = str(e)
        return scan_results


def _load_existing_commands(commands_file: str) -> List[Dict[str, Any]]:
    """Load existing commands from commands.jsonl file."""
    commands = []
    commands_path = Path(commands_file)
    
    if not commands_path.exists():
        logging.info(f"Commands file {commands_file} does not exist - no conflicts to check")
        return commands
    
    try:
        with open(commands_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        command = json.loads(line)
                        commands.append(command)
                    except json.JSONDecodeError as e:
                        logging.warning(f"Invalid JSON at line {line_num} in {commands_file}: {e}")
        
        logging.debug(f"Loaded {len(commands)} existing commands for conflict checking")
        
    except Exception as e:
        logging.error(f"Failed to load commands from {commands_file}: {e}")
    
    return commands


def _check_duplicate_names(command_name: str, existing_commands: List[Dict[str, Any]]) -> List[str]:
    """Check for duplicate command names."""
    duplicates = []
    
    for existing in existing_commands:
        existing_name = existing.get('command', '')
        if existing_name.lower() == command_name.lower():
            duplicates.append(existing_name)
    
    return duplicates


def _check_similar_functionality(command: Dict[str, Any], existing_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for commands with similar functionality."""
    similar = []
    command_desc = command.get('description', '').lower()
    command_tags = set(command.get('tags', []))
    command_category = command.get('category', '')
    
    for existing in existing_commands:
        similarity_score = 0
        reasons = []
        
        # Check description similarity
        existing_desc = existing.get('description', '').lower()
        if command_desc and existing_desc:
            common_words = set(command_desc.split()) & set(existing_desc.split())
            if len(common_words) >= 3:
                similarity_score += len(common_words) * 0.1
                reasons.append(f"{len(common_words)} common words in description")
        
        # Check tag overlap
        existing_tags = set(existing.get('tags', []))
        tag_overlap = command_tags & existing_tags
        if tag_overlap:
            similarity_score += len(tag_overlap) * 0.2
            reasons.append(f"{len(tag_overlap)} common tags")
        
        # Check category match
        if command_category and command_category == existing.get('category'):
            similarity_score += 0.3
            reasons.append("same category")
        
        # If similarity score is high enough, consider it similar
        if similarity_score >= 0.5:
            similar.append({
                'command': existing.get('command', ''),
                'similarity_score': similarity_score,
                'reasons': reasons,
                'existing_command': existing
            })
    
    return similar


def _check_overlapping_functionality(command_steps: List[Dict[str, Any]], 
                                   existing_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for overlapping functionality in steps."""
    overlapping = []
    
    if not command_steps:
        return overlapping
    
    command_actions = set()
    for step in command_steps:
        action = step.get('action', '')
        if action:
            command_actions.add(action.lower())
    
    for existing in existing_commands:
        existing_steps = existing.get('steps', [])
        existing_actions = set()
        
        for step in existing_steps:
            action = step.get('action', '')
            if action:
                existing_actions.add(action.lower())
        
        # Calculate overlap
        overlap = command_actions & existing_actions
        if overlap and len(overlap) >= min(2, len(command_actions) * 0.5):
            overlapping.append({
                'command': existing.get('command', ''),
                'overlapping_actions': list(overlap),
                'overlap_percentage': len(overlap) / len(command_actions | existing_actions),
                'existing_command': existing
            })
    
    return overlapping


def _check_resource_conflicts(command: Dict[str, Any], existing_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for resource conflicts."""
    conflicts = []
    command_integration = command.get('integration', {})
    command_file_ops = command_integration.get('file_operations', [])
    
    # Check for file operation conflicts
    for existing in existing_commands:
        existing_integration = existing.get('integration', {})
        existing_file_ops = existing_integration.get('file_operations', [])
        
        # Check for conflicting write operations
        if 'write' in command_file_ops and 'write' in existing_file_ops:
            # This could indicate potential file conflicts
            conflicts.append({
                'type': 'file_write_conflict',
                'command': existing.get('command', ''),
                'description': 'Both commands perform write operations',
                'existing_command': existing
            })
    
    return conflicts


def _check_dependency_conflicts(command: Dict[str, Any], existing_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for dependency conflicts."""
    conflicts = []
    command_deps = set(command.get('dependencies', []))
    
    if not command_deps:
        return conflicts
    
    for existing in existing_commands:
        existing_deps = set(existing.get('dependencies', []))
        
        # Check for conflicting versions of same dependency
        # This is a simplified check - in practice, you'd parse version strings
        common_deps = command_deps & existing_deps
        if common_deps:
            # For now, just note that there are common dependencies
            # In a real system, you'd check version compatibility
            pass
    
    return conflicts


def _apply_conflict_resolution(command: Dict[str, Any], scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """Apply automatic conflict resolution where possible."""
    resolution_results = {
        'auto_adaptations': [],
        'manual_interventions_needed': [],
        'resolution_strategies': []
    }
    
    # Handle duplicate names
    if scan_results.get('duplicate_names'):
        original_name = command.get('command', '')
        new_name = _generate_unique_name(original_name, scan_results['duplicate_names'])
        
        resolution_results['auto_adaptations'].append({
            'type': 'rename_command',
            'original_name': original_name,
            'new_name': new_name,
            'reason': 'Resolve duplicate name conflict'
        })
        
        resolution_results['resolution_strategies'].append(
            f"Auto-renamed command from '{original_name}' to '{new_name}'"
        )
    
    # Handle similar functionality
    if scan_results.get('similar_commands'):
        for similar in scan_results['similar_commands']:
            if similar['similarity_score'] > 0.8:
                resolution_results['manual_interventions_needed'].append({
                    'type': 'high_similarity',
                    'similar_command': similar['command'],
                    'suggestion': 'Consider merging functionality or making more distinct'
                })
            else:
                resolution_results['auto_adaptations'].append({
                    'type': 'add_distinguishing_tag',
                    'reason': f"Distinguish from similar command: {similar['command']}",
                    'tag': 'variant'
                })
    
    return resolution_results


def _generate_adaptation_suggestions(command: Dict[str, Any], scan_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate adaptation suggestions based on scan results."""
    suggestions = []
    
    # Suggestions for duplicate names
    if scan_results.get('duplicate_names'):
        suggestions.append({
            'type': 'naming',
            'priority': 'high',
            'description': 'Consider using a more specific name to avoid conflicts',
            'specific_suggestion': f"Rename to include context or version (e.g., {command.get('command', '')}_v2)",
            'rationale': f"Conflicts with existing command(s): {', '.join(scan_results['duplicate_names'])}"
        })
    
    # Suggestions for similar functionality
    if scan_results.get('similar_commands'):
        high_similarity = [s for s in scan_results['similar_commands'] if s['similarity_score'] > 0.7]
        if high_similarity:
            suggestions.append({
                'type': 'functionality',
                'priority': 'medium',
                'description': 'Consider consolidating similar functionality',
                'specific_suggestion': 'Review if this command adds unique value or could be merged with existing commands',
                'rationale': f"High similarity with: {', '.join([s['command'] for s in high_similarity])}"
            })
    
    # Suggestions for overlapping functionality
    if scan_results.get('overlapping_functionality'):
        suggestions.append({
            'type': 'optimization',
            'priority': 'low',
            'description': 'Consider reusing existing functionality',
            'specific_suggestion': 'Look into calling existing commands as dependencies rather than reimplementing',
            'rationale': 'Several commands share similar steps'
        })
    
    # General suggestions
    suggestions.append({
        'type': 'documentation',
        'priority': 'low',
        'description': 'Document differences from similar commands',
        'specific_suggestion': 'Add clear documentation explaining when to use this vs similar commands',
        'rationale': 'Helps users choose the right command'
    })
    
    # Sort suggestions by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
    
    return suggestions


def _generate_unique_name(original_name: str, existing_names: List[str]) -> str:
    """Generate a unique name by appending suffix."""
    base_name = original_name
    counter = 2
    
    while True:
        new_name = f"{base_name}_v{counter}"
        if new_name.lower() not in [name.lower() for name in existing_names]:
            return new_name
        counter += 1
        
        # Prevent infinite loop
        if counter > 100:
            import uuid
            return f"{base_name}_{str(uuid.uuid4())[:8]}"


def _apply_auto_adaptations(command: Dict[str, Any], adaptations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply automatic adaptations to the command."""
    adapted_command = command.copy()
    
    for adaptation in adaptations:
        adaptation_type = adaptation.get('type')
        
        if adaptation_type == 'rename_command':
            adapted_command['command'] = adaptation['new_name']
            logging.info(f"Applied auto-adaptation: renamed command to {adaptation['new_name']}")
        
        elif adaptation_type == 'add_distinguishing_tag':
            if 'tags' not in adapted_command:
                adapted_command['tags'] = []
            adapted_command['tags'].append(adaptation['tag'])
            logging.info(f"Applied auto-adaptation: added tag '{adaptation['tag']}'")
        
        # Add adaptation record
        if 'adaptations_applied' not in adapted_command:
            adapted_command['adaptations_applied'] = []
        
        adapted_command['adaptations_applied'].append({
            'type': adaptation_type,
            'timestamp': time.time(),
            'reason': adaptation.get('reason', ''),
            'details': adaptation
        })
    
    return adapted_command


def validate_conflict_resolution(resolved_command: Dict[str, Any]) -> bool:
    """Validate that conflict resolution was successful."""
    try:
        conflict_resolution = resolved_command.get('conflict_resolution', {})
        
        # Check if critical conflicts were resolved
        scan_results = conflict_resolution.get('scan_results', {})
        critical_conflicts = scan_results.get('critical_conflicts', [])
        
        if critical_conflicts:
            # Check if adaptations were applied to resolve critical conflicts
            resolution_results = conflict_resolution.get('resolution_applied', {})
            auto_adaptations = resolution_results.get('auto_adaptations', [])
            
            # For now, consider it resolved if we have adaptations
            return len(auto_adaptations) > 0
        
        return True
        
    except Exception as e:
        logging.error(f"Conflict resolution validation failed: {e}")
        return False