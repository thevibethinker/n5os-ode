import logging
import time
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


def generate_command_structure(scoped_draft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate structured command representation from scoped LLM draft.
    
    Args:
        scoped_draft: Scoped and clarified command draft from LLM agent
        
    Returns:
        Structured command dict with steps, retries, and wrapper patterns
    """
    start_time = time.time()
    
    try:
        if 'error' in scoped_draft:
            logging.error(f"Cannot generate structure from errored draft: {scoped_draft['error']}")
            return {'error': scoped_draft['error']}
        
        # Extract base information
        original_segments = scoped_draft.get('original_segments', [])
        scoped_steps = scoped_draft.get('scoped_steps', [])
        
        if not scoped_steps and not original_segments:
            raise ValueError("No steps or segments available for structure generation")
        
        # Generate command metadata
        command_id = str(uuid.uuid4())
        command_name = _generate_command_name(original_segments, scoped_steps)
        
        # Build structured command
        structured_command = {
            'id': command_id,
            'name': command_name,
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'source': 'conversation_authoring',
            'description': _generate_description(original_segments, scoped_steps),
            'category': _determine_category(original_segments, scoped_steps),
            'tags': _extract_tags(original_segments, scoped_steps),
            
            # Core execution structure
            'steps': _build_execution_steps(scoped_steps),
            'retries': _determine_retry_config(scoped_steps),
            'timeout': _determine_timeout(scoped_steps),
            'dependencies': _extract_dependencies(scoped_steps),
            
            # Wrapper patterns
            'logging': _build_logging_config(scoped_steps),
            'validation': _build_validation_config(scoped_steps),
            'error_handling': _build_error_handling_config(scoped_steps),
            'telemetry': _build_telemetry_config(),
            
            # Input/Output specification
            'inputs': _define_inputs(original_segments, scoped_steps),
            'outputs': _define_outputs(scoped_steps),
            
            # Integration metadata
            'integration': {
                'cli_compatible': True,
                'async_capable': _assess_async_needs(scoped_steps),
                'requires_llm': _requires_llm_integration(scoped_steps),
                'file_operations': _analyze_file_operations(scoped_steps)
            },
            
            # Quality metrics
            'confidence': scoped_draft.get('confidence', 0.7),
            'complexity': _assess_complexity(scoped_steps),
            'estimated_duration': _estimate_duration(scoped_steps)
        }
        
        # Telemetry logging
        generation_time = time.time() - start_time
        draft_size = len(str(structured_command))
        
        logging.info(f"Generated command structure in {generation_time:.3f}s")
        logging.debug(f"Draft size: {draft_size} bytes, steps: {len(structured_command['steps'])}")
        
        return structured_command
        
    except Exception as e:
        logging.error(f"Draft failed: {e}")
        return {
            'error': str(e),
            'fallback_structure': _generate_minimal_structure(scoped_draft)
        }


def _generate_command_name(segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> str:
    """Generate appropriate command name from segments and steps."""
    # Look for explicit command names in segments
    for segment in segments:
        if segment.get('type') == 'command':
            content = segment.get('content', '').strip()
            # Extract first word as potential command name
            words = content.split()
            if words and len(words[0]) > 2:
                return words[0].lower().replace(':', '').replace('-', '_')
    
    # Generate from steps
    if steps:
        first_step = steps[0].get('description', '')
        words = first_step.split()
        action_words = ['create', 'build', 'generate', 'process', 'analyze', 'parse', 'export']
        
        for word in words:
            word_lower = word.lower().strip('.,!?-')
            if word_lower in action_words:
                return f"{word_lower}_command"
    
    # Fallback
    return "custom_command"


def _generate_description(segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> str:
    """Generate command description from segments and steps."""
    # Try to extract from task segments
    for segment in segments:
        if segment.get('type') == 'task':
            content = segment.get('content', '').strip()
            if len(content) > 10:
                return content[:200] + ('...' if len(content) > 200 else '')
    
    # Generate from steps
    if steps:
        return f"Command with {len(steps)} steps: " + ', '.join(
            step.get('description', '')[:50] for step in steps[:3]
        )
    
    return "Auto-generated command from conversation"


def _determine_category(segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> str:
    """Determine command category based on content analysis."""
    content_text = ' '.join([
        seg.get('content', '') for seg in segments
    ] + [
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    categories = {
        'data_processing': ['process', 'transform', 'parse', 'analyze', 'extract'],
        'file_operations': ['file', 'write', 'read', 'export', 'import', 'save'],
        'system_admin': ['install', 'configure', 'setup', 'deploy', 'manage'],
        'automation': ['automate', 'schedule', 'batch', 'bulk', 'loop'],
        'integration': ['integrate', 'connect', 'sync', 'api', 'webhook'],
        'monitoring': ['monitor', 'track', 'log', 'alert', 'health'],
        'development': ['code', 'build', 'test', 'debug', 'compile']
    }
    
    for category, keywords in categories.items():
        if any(keyword in content_text for keyword in keywords):
            return category
    
    return 'general'


def _extract_tags(segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> List[str]:
    """Extract relevant tags from content."""
    content_text = ' '.join([
        seg.get('content', '') for seg in segments
    ] + [
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    tag_keywords = {
        'async': ['async', 'parallel', 'concurrent'],
        'llm': ['llm', 'ai', 'language model', 'gpt', 'claude'],
        'files': ['file', 'directory', 'path', 'write', 'read'],
        'network': ['http', 'api', 'request', 'url', 'download'],
        'database': ['db', 'database', 'sql', 'query'],
        'parsing': ['parse', 'extract', 'regex', 'pattern'],
        'validation': ['validate', 'check', 'verify', 'ensure'],
        'logging': ['log', 'trace', 'debug', 'telemetry']
    }
    
    tags = []
    for tag, keywords in tag_keywords.items():
        if any(keyword in content_text for keyword in keywords):
            tags.append(tag)
    
    return tags


def _build_execution_steps(scoped_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build execution steps with wrapper patterns."""
    execution_steps = []
    
    for i, step in enumerate(scoped_steps):
        exec_step = {
            'id': step.get('id', i + 1),
            'name': _clean_step_name(step.get('description', f'Step {i + 1}')),
            'description': step.get('description', ''),
            'type': step.get('type', 'action'),
            'action': _extract_action_from_step(step),
            'parameters': _extract_parameters_from_step(step),
            'prerequisites': _extract_prerequisites_from_step(step),
            'expected_output': _extract_expected_output_from_step(step),
            'on_failure': 'retry_with_backoff',
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout': 30.0,
            'logging': {
                'log_start': True,
                'log_completion': True,
                'log_parameters': True,
                'log_output': True
            }
        }
        
        execution_steps.append(exec_step)
    
    return execution_steps


def _determine_retry_config(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Determine retry configuration based on step complexity."""
    total_steps = len(steps)
    complexity_score = sum(len(step.get('details', [])) for step in steps)
    
    if complexity_score > 10 or total_steps > 5:
        return {
            'global_retries': 2,
            'backoff_strategy': 'exponential',
            'max_backoff': 60.0,
            'jitter': True
        }
    else:
        return {
            'global_retries': 1,
            'backoff_strategy': 'linear',
            'max_backoff': 30.0,
            'jitter': False
        }


def _determine_timeout(steps: List[Dict[str, Any]]) -> int:
    """Determine timeout based on step complexity."""
    base_timeout = 60  # 1 minute base
    step_timeout = len(steps) * 10  # 10 seconds per step
    
    # Check for complex operations
    complex_operations = ['llm', 'download', 'process', 'analyze', 'generate']
    content_text = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    complexity_bonus = sum(30 for op in complex_operations if op in content_text)
    
    return min(base_timeout + step_timeout + complexity_bonus, 600)  # Max 10 minutes


def _extract_dependencies(steps: List[Dict[str, Any]]) -> List[str]:
    """Extract dependencies from step descriptions."""
    dependencies = set()
    
    content_text = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    dep_patterns = {
        'python': ['python', 'pip', 'import'],
        'nodejs': ['npm', 'node', 'javascript'],
        'git': ['git', 'repository', 'commit'],
        'docker': ['docker', 'container', 'image'],
        'database': ['database', 'sql', 'postgres', 'mysql'],
        'web': ['http', 'requests', 'api', 'curl'],
        'files': ['filesystem', 'directory', 'file operations']
    }
    
    for dep, patterns in dep_patterns.items():
        if any(pattern in content_text for pattern in patterns):
            dependencies.add(dep)
    
    return list(dependencies)


def _build_logging_config(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build logging configuration."""
    return {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'handlers': ['console', 'file'],
        'file_path': 'logs/command_execution.log',
        'rotation': 'daily',
        'retention': 7,
        'structured': True
    }


def _build_validation_config(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build validation configuration."""
    return {
        'validate_inputs': True,
        'validate_outputs': True,
        'schema_validation': True,
        'type_checking': True,
        'range_checking': True,
        'custom_validators': []
    }


def _build_error_handling_config(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build error handling configuration."""
    return {
        'strategy': 'fail_fast_with_cleanup',
        'capture_stack_trace': True,
        'log_errors': True,
        'notify_on_failure': False,
        'cleanup_on_failure': True,
        'rollback_capability': True
    }


def _build_telemetry_config() -> Dict[str, Any]:
    """Build telemetry configuration."""
    return {
        'enabled': True,
        'metrics': ['execution_time', 'success_rate', 'error_count', 'retry_count'],
        'events': ['start', 'completion', 'error', 'retry'],
        'sampling_rate': 1.0,
        'export_format': 'jsonl'
    }


def _define_inputs(segments: List[Dict[str, Any]], steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Define input specification."""
    return {
        'required': ['input_text'],
        'optional': ['config', 'options'],
        'types': {
            'input_text': 'string',
            'config': 'object',
            'options': 'object'
        },
        'validation': {
            'input_text': {'min_length': 1, 'max_length': 10000},
            'config': {'type': 'object'},
            'options': {'type': 'object'}
        }
    }


def _define_outputs(steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Define output specification."""
    return {
        'format': 'json',
        'schema': {
            'success': 'boolean',
            'result': 'object',
            'metadata': 'object',
            'execution_time': 'number',
            'step_results': 'array'
        },
        'examples': [
            {
                'success': True,
                'result': {'processed': True},
                'metadata': {'steps_executed': len(steps)},
                'execution_time': 1.23,
                'step_results': []
            }
        ]
    }


# Helper functions for step processing
def _clean_step_name(description: str) -> str:
    """Clean step description to create a proper name."""
    import re
    name = re.sub(r'^[\d\.\-\s]+', '', description)
    name = re.sub(r'[^\w\s]', '', name)
    return '_'.join(name.split()[:4]).lower()


def _extract_action_from_step(step: Dict[str, Any]) -> str:
    """Extract action type from step."""
    description = step.get('description', '').lower()
    
    action_mapping = {
        'parse': 'parse_data',
        'process': 'process_data',
        'validate': 'validate_data',
        'generate': 'generate_output',
        'create': 'create_resource',
        'update': 'update_resource',
        'delete': 'delete_resource',
        'export': 'export_data',
        'import': 'import_data'
    }
    
    for keyword, action in action_mapping.items():
        if keyword in description:
            return action
    
    return 'execute'


def _extract_parameters_from_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """Extract parameters from step details."""
    return {
        'step_id': step.get('id'),
        'description': step.get('description', ''),
        'details': step.get('details', []),
        'type': step.get('type', 'action')
    }


def _extract_prerequisites_from_step(step: Dict[str, Any]) -> List[str]:
    """Extract prerequisites from step."""
    details = step.get('details', [])
    prereqs = []
    
    for detail in details:
        if 'require' in detail.lower() or 'need' in detail.lower():
            prereqs.append(detail)
    
    return prereqs


def _extract_expected_output_from_step(step: Dict[str, Any]) -> str:
    """Extract expected output from step."""
    step_type = step.get('type', 'action')
    
    output_mapping = {
        'validation': 'validation_result',
        'action': 'action_result',
        'output': 'formatted_output',
        'parse': 'parsed_data'
    }
    
    return output_mapping.get(step_type, 'step_result')


def _assess_async_needs(steps: List[Dict[str, Any]]) -> bool:
    """Assess if command needs async capabilities."""
    content_text = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    async_indicators = ['parallel', 'concurrent', 'multiple', 'batch', 'async', 'simultaneous']
    return any(indicator in content_text for indicator in async_indicators)


def _requires_llm_integration(steps: List[Dict[str, Any]]) -> bool:
    """Check if command requires LLM integration."""
    content_text = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    llm_indicators = ['llm', 'language model', 'ai', 'generate', 'analyze', 'interpret', 'understand']
    return any(indicator in content_text for indicator in llm_indicators)


def _analyze_file_operations(steps: List[Dict[str, Any]]) -> List[str]:
    """Analyze what file operations are needed."""
    content_text = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    operations = []
    if any(word in content_text for word in ['read', 'load', 'import']):
        operations.append('read')
    if any(word in content_text for word in ['write', 'save', 'export']):
        operations.append('write')
    if any(word in content_text for word in ['create', 'mkdir']):
        operations.append('create')
    if any(word in content_text for word in ['delete', 'remove']):
        operations.append('delete')
    
    return operations


def _assess_complexity(steps: List[Dict[str, Any]]) -> str:
    """Assess command complexity."""
    step_count = len(steps)
    detail_count = sum(len(step.get('details', [])) for step in steps)
    
    if step_count <= 2 and detail_count <= 5:
        return 'low'
    elif step_count <= 5 and detail_count <= 15:
        return 'medium'
    else:
        return 'high'


def _estimate_duration(steps: List[Dict[str, Any]]) -> int:
    """Estimate execution duration in seconds."""
    base_time = 5  # Base 5 seconds
    step_time = len(steps) * 2  # 2 seconds per step
    detail_time = sum(len(step.get('details', [])) for step in steps)  # 1 second per detail
    
    return base_time + step_time + detail_time


def _generate_minimal_structure(scoped_draft: Dict[str, Any]) -> Dict[str, Any]:
    """Generate minimal fallback structure."""
    return {
        'id': str(uuid.uuid4()),
        'command': 'fallback_command',
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'source': 'conversation_authoring_fallback',
        'description': 'Minimal fallback command structure',
        'steps': [
            {
                'id': 1,
                'name': 'execute',
                'description': 'Execute basic operation',
                'type': 'action',
                'action': 'execute'
            }
        ],
        'retries': {'global_retries': 1},
        'timeout': 60
    }