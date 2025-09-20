import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


def validate_and_enhance_command(structured_command: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate command structure, enhance with defaults, simulate dry-run.
    
    Args:
        structured_command: Structured command from generator
        
    Returns:
        Validated and enhanced command dict
    """
    start_time = time.time()
    
    try:
        if 'error' in structured_command:
            logging.error(f"Cannot validate errored command: {structured_command['error']}")
            return structured_command
        
        # Create enhanced copy
        enhanced_command = structured_command.copy()
        validation_results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'enhancements': []
        }
        
        # Run validation checks
        _validate_required_fields(enhanced_command, validation_results)
        _validate_command_structure(enhanced_command, validation_results)
        _validate_steps(enhanced_command, validation_results)
        _validate_configuration(enhanced_command, validation_results)
        
        # Apply enhancements
        _enhance_with_defaults(enhanced_command, validation_results)
        _enhance_logging_config(enhanced_command, validation_results)
        _enhance_error_handling(enhanced_command, validation_results)
        _enhance_telemetry(enhanced_command, validation_results)
        
        # Perform dry-run simulation
        dry_run_results = _simulate_dry_run(enhanced_command)
        
        # Add validation metadata
        enhanced_command['validation'] = {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'results': validation_results,
            'dry_run': dry_run_results,
            'validation_time': time.time() - start_time,
            'status': 'passed' if not validation_results['errors'] else 'failed'
        }
        
        # Telemetry logging
        validation_time = time.time() - start_time
        logging.info(f"Validation completed in {validation_time:.3f}s")
        logging.debug(f"Validation results - Passed: {len(validation_results['passed'])}, "
                     f"Warnings: {len(validation_results['warnings'])}, "
                     f"Errors: {len(validation_results['errors'])}")
        
        if dry_run_results:
            logging.debug(f"Dry-run metrics - Success rate: {dry_run_results.get('success_rate', 0):.2f}, "
                         f"Estimated time: {dry_run_results.get('estimated_execution_time', 0):.2f}s")
        
        return enhanced_command
        
    except Exception as e:
        logging.error(f"Validation failed: {e}")
        return {
            'error': str(e),
            'original_command': structured_command,
            'validation_failed': True
        }


def _validate_required_fields(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Validate required fields are present."""
    required_fields = [
        'id', 'command', 'version', 'created_at', 'source',
        'description', 'steps', 'retries', 'timeout'
    ]
    
    for field in required_fields:
        if field not in command:
            results['errors'].append(f"Missing required field: {field}")
        else:
            results['passed'].append(f"Required field present: {field}")


def _validate_command_structure(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Validate overall command structure."""
    # Validate ID format
    if 'id' in command:
        if not isinstance(command['id'], str) or len(command['id']) < 10:
            results['errors'].append("Command ID must be a string with at least 10 characters")
        else:
            results['passed'].append("Command ID format valid")
    
    # Validate command name
    if 'command' in command:
        if not isinstance(command['command'], str) or not command['command']:
            results['errors'].append("Command name must be a non-empty string")
        elif not command['command'].replace('_', '').replace('-', '').isalnum():
            results['warnings'].append("Command name contains special characters")
        else:
            results['passed'].append("Command name format valid")
    
    # Validate version
    if 'version' in command:
        version = command['version']
        if not isinstance(version, str) or not version.count('.') >= 1:
            results['warnings'].append("Version should follow semantic versioning (e.g., 1.0.0)")
        else:
            results['passed'].append("Version format valid")
    
    # Validate timeout
    if 'timeout' in command:
        timeout = command['timeout']
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            results['errors'].append("Timeout must be a positive number")
        elif timeout > 3600:  # 1 hour
            results['warnings'].append("Timeout exceeds 1 hour - consider breaking into smaller commands")
        else:
            results['passed'].append("Timeout value valid")


def _validate_steps(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Validate command steps."""
    if 'steps' not in command:
        results['errors'].append("No steps defined")
        return
    
    steps = command['steps']
    if not isinstance(steps, list):
        results['errors'].append("Steps must be a list")
        return
    
    if not steps:
        results['errors'].append("Steps list is empty")
        return
    
    step_ids = set()
    for i, step in enumerate(steps):
        step_prefix = f"Step {i+1}"
        
        # Validate step structure
        required_step_fields = ['id', 'name', 'description', 'type', 'action']
        for field in required_step_fields:
            if field not in step:
                results['errors'].append(f"{step_prefix}: Missing required field '{field}'")
        
        # Validate step ID uniqueness
        step_id = step.get('id')
        if step_id in step_ids:
            results['errors'].append(f"{step_prefix}: Duplicate step ID '{step_id}'")
        else:
            step_ids.add(step_id)
        
        # Validate step type
        valid_types = ['action', 'validation', 'output', 'input', 'condition']
        step_type = step.get('type')
        if step_type not in valid_types:
            results['warnings'].append(f"{step_prefix}: Unusual step type '{step_type}'")
        
        # Validate retry configuration
        max_retries = step.get('max_retries', 0)
        if not isinstance(max_retries, int) or max_retries < 0:
            results['warnings'].append(f"{step_prefix}: Invalid max_retries value")
        
        # Validate timeout
        step_timeout = step.get('timeout', 30)
        if not isinstance(step_timeout, (int, float)) or step_timeout <= 0:
            results['warnings'].append(f"{step_prefix}: Invalid timeout value")
    
    results['passed'].append(f"Steps validation completed - {len(steps)} steps")


def _validate_configuration(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Validate configuration sections."""
    # Validate logging config
    if 'logging' in command:
        logging_config = command['logging']
        if not isinstance(logging_config, dict):
            results['errors'].append("Logging config must be a dictionary")
        else:
            required_log_fields = ['level', 'format']
            for field in required_log_fields:
                if field not in logging_config:
                    results['warnings'].append(f"Logging config missing recommended field: {field}")
    
    # Validate retry config
    if 'retries' in command:
        retry_config = command['retries']
        if not isinstance(retry_config, dict):
            results['errors'].append("Retry config must be a dictionary")
        else:
            if 'global_retries' in retry_config:
                global_retries = retry_config['global_retries']
                if not isinstance(global_retries, int) or global_retries < 0:
                    results['errors'].append("global_retries must be a non-negative integer")
    
    # Validate inputs/outputs
    if 'inputs' in command:
        inputs_config = command['inputs']
        if not isinstance(inputs_config, dict):
            results['warnings'].append("Inputs config should be a dictionary")
        elif 'required' not in inputs_config:
            results['warnings'].append("Inputs config missing 'required' field")
    
    if 'outputs' in command:
        outputs_config = command['outputs']
        if not isinstance(outputs_config, dict):
            results['warnings'].append("Outputs config should be a dictionary")


def _enhance_with_defaults(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Enhance command with default values where missing."""
    defaults_applied = []
    
    # Add missing metadata
    if 'metadata' not in command:
        command['metadata'] = {
            'created_by': 'command_authoring_system',
            'last_modified': datetime.now().isoformat(),
            'tags': command.get('tags', []),
            'category': command.get('category', 'general')
        }
        defaults_applied.append("Added metadata section")
    
    # Enhance retry configuration
    if 'retries' in command and isinstance(command['retries'], dict):
        retry_config = command['retries']
        if 'backoff_strategy' not in retry_config:
            retry_config['backoff_strategy'] = 'exponential'
            defaults_applied.append("Added default backoff strategy")
        
        if 'max_backoff' not in retry_config:
            retry_config['max_backoff'] = 60.0
            defaults_applied.append("Added default max backoff")
    
    # Enhance logging configuration
    if 'logging' not in command:
        command['logging'] = {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'handlers': ['console']
        }
        defaults_applied.append("Added default logging configuration")
    
    # Add performance monitoring
    if 'monitoring' not in command:
        command['monitoring'] = {
            'enabled': True,
            'metrics': ['execution_time', 'memory_usage', 'success_rate'],
            'alerts': {
                'slow_execution': {'threshold': command.get('timeout', 60) * 0.8},
                'high_failure_rate': {'threshold': 0.1}
            }
        }
        defaults_applied.append("Added performance monitoring")
    
    # Enhance security settings
    if 'security' not in command:
        command['security'] = {
            'input_sanitization': True,
            'output_filtering': True,
            'audit_logging': True,
            'access_control': 'default'
        }
        defaults_applied.append("Added security settings")
    
    results['enhancements'].extend(defaults_applied)


def _enhance_logging_config(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Enhance logging configuration."""
    if 'logging' not in command:
        return
    
    logging_config = command['logging']
    enhancements = []
    
    # Add structured logging
    if 'structured' not in logging_config:
        logging_config['structured'] = True
        enhancements.append("Enabled structured logging")
    
    # Add context fields
    if 'context_fields' not in logging_config:
        logging_config['context_fields'] = [
            'command_id', 'step_id', 'execution_id', 'timestamp'
        ]
        enhancements.append("Added context fields for logging")
    
    # Add log rotation
    if 'rotation' not in logging_config:
        logging_config['rotation'] = {
            'when': 'midnight',
            'backup_count': 7,
            'max_bytes': 10485760  # 10MB
        }
        enhancements.append("Added log rotation settings")
    
    results['enhancements'].extend(enhancements)


def _enhance_error_handling(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Enhance error handling configuration."""
    if 'error_handling' not in command:
        command['error_handling'] = {}
    
    error_config = command['error_handling']
    enhancements = []
    
    # Add error categories
    if 'error_categories' not in error_config:
        error_config['error_categories'] = {
            'recoverable': ['ConnectionError', 'TimeoutError', 'TemporaryFailure'],
            'non_recoverable': ['ValidationError', 'AuthenticationError', 'PermissionError'],
            'critical': ['SystemError', 'OutOfMemoryError', 'DiskFullError']
        }
        enhancements.append("Added error categorization")
    
    # Add error recovery strategies
    if 'recovery_strategies' not in error_config:
        error_config['recovery_strategies'] = {
            'recoverable': 'retry_with_backoff',
            'non_recoverable': 'fail_fast',
            'critical': 'emergency_shutdown'
        }
        enhancements.append("Added error recovery strategies")
    
    # Add notification settings
    if 'notifications' not in error_config:
        error_config['notifications'] = {
            'enabled': True,
            'channels': ['log'],
            'severity_threshold': 'error'
        }
        enhancements.append("Added error notification settings")
    
    results['enhancements'].extend(enhancements)


def _enhance_telemetry(command: Dict[str, Any], results: Dict[str, List[str]]) -> None:
    """Enhance telemetry configuration."""
    if 'telemetry' not in command:
        command['telemetry'] = {}
    
    telemetry_config = command['telemetry']
    enhancements = []
    
    # Add comprehensive metrics
    if 'metrics' not in telemetry_config:
        telemetry_config['metrics'] = [
            'execution_time', 'success_rate', 'error_count', 'retry_count',
            'memory_usage', 'cpu_usage', 'throughput', 'latency'
        ]
        enhancements.append("Added comprehensive metrics collection")
    
    # Add event tracking
    if 'events' not in telemetry_config:
        telemetry_config['events'] = [
            'command_start', 'command_complete', 'step_start', 'step_complete',
            'error_occurred', 'retry_attempted', 'validation_failed'
        ]
        enhancements.append("Added event tracking")
    
    # Add export configuration
    if 'export' not in telemetry_config:
        telemetry_config['export'] = {
            'format': 'jsonl',
            'destination': 'logs/telemetry.jsonl',
            'batch_size': 100,
            'flush_interval': 60
        }
        enhancements.append("Added telemetry export configuration")
    
    results['enhancements'].extend(enhancements)


def _simulate_dry_run(command: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate dry-run execution with logging."""
    start_time = time.time()
    
    dry_run_results = {
        'simulation_time': 0,
        'estimated_execution_time': 0,
        'success_probability': 0.0,
        'risk_factors': [],
        'resource_requirements': {},
        'step_analysis': []
    }
    
    try:
        steps = command.get('steps', [])
        total_estimated_time = 0
        success_probability = 1.0
        risk_factors = []
        
        for step in steps:
            step_analysis = _analyze_step_execution(step)
            dry_run_results['step_analysis'].append(step_analysis)
            
            # Accumulate estimated time
            step_time = step_analysis.get('estimated_time', 5)
            total_estimated_time += step_time
            
            # Calculate success probability (multiply probabilities)
            step_success_prob = step_analysis.get('success_probability', 0.9)
            success_probability *= step_success_prob
            
            # Collect risk factors
            step_risks = step_analysis.get('risk_factors', [])
            risk_factors.extend(step_risks)
        
        # Analyze resource requirements
        dry_run_results['resource_requirements'] = _analyze_resource_requirements(command)
        
        # Set results
        dry_run_results['estimated_execution_time'] = total_estimated_time
        dry_run_results['success_probability'] = success_probability
        dry_run_results['risk_factors'] = list(set(risk_factors))  # Remove duplicates
        
        # Add overall assessment
        dry_run_results['overall_assessment'] = _assess_execution_feasibility(
            success_probability, risk_factors, total_estimated_time
        )
        
        simulation_time = time.time() - start_time
        dry_run_results['simulation_time'] = simulation_time
        
        # Log dry-run metrics
        logging.info(f"Dry-run simulation completed in {simulation_time:.3f}s")
        logging.debug(f"Estimated execution time: {total_estimated_time:.2f}s, "
                     f"Success probability: {success_probability:.2f}")
        
        return dry_run_results
        
    except Exception as e:
        logging.error(f"Dry-run simulation failed: {e}")
        dry_run_results['error'] = str(e)
        return dry_run_results


def _analyze_step_execution(step: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze individual step for dry-run simulation."""
    step_type = step.get('type', 'action')
    action = step.get('action', 'execute')
    description = step.get('description', '').lower()
    
    analysis = {
        'step_id': step.get('id'),
        'estimated_time': 5,  # Base 5 seconds
        'success_probability': 0.9,  # Base 90% success
        'risk_factors': [],
        'resource_needs': []
    }
    
    # Adjust based on step type
    type_adjustments = {
        'validation': {'time': 2, 'success': 0.95},
        'action': {'time': 10, 'success': 0.85},
        'output': {'time': 3, 'success': 0.9},
        'input': {'time': 1, 'success': 0.95}
    }
    
    if step_type in type_adjustments:
        adj = type_adjustments[step_type]
        analysis['estimated_time'] = adj['time']
        analysis['success_probability'] = adj['success']
    
    # Adjust based on action complexity
    complex_actions = ['process', 'analyze', 'generate', 'transform']
    if any(action_word in description for action_word in complex_actions):
        analysis['estimated_time'] *= 2
        analysis['success_probability'] *= 0.9
        analysis['risk_factors'].append('complex_operation')
    
    # Check for external dependencies
    external_deps = ['api', 'network', 'file', 'database', 'service']
    if any(dep in description for dep in external_deps):
        analysis['estimated_time'] += 5
        analysis['success_probability'] *= 0.8
        analysis['risk_factors'].append('external_dependency')
        analysis['resource_needs'].append('network_access')
    
    # Check for file operations
    file_ops = ['read', 'write', 'create', 'delete', 'modify']
    if any(op in description for op in file_ops):
        analysis['resource_needs'].append('file_system_access')
        if 'write' in description or 'create' in description or 'delete' in description:
            analysis['risk_factors'].append('file_modification')
    
    return analysis


def _analyze_resource_requirements(command: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze overall resource requirements."""
    requirements = {
        'cpu': 'low',
        'memory': 'low',
        'disk': 'low',
        'network': False,
        'external_services': []
    }
    
    steps = command.get('steps', [])
    
    # Analyze based on step count and complexity
    if len(steps) > 10:
        requirements['cpu'] = 'medium'
        requirements['memory'] = 'medium'
    elif len(steps) > 5:
        requirements['cpu'] = 'low-medium'
    
    # Check for resource-intensive operations
    all_descriptions = ' '.join([
        step.get('description', '') + ' ' + ' '.join(step.get('details', []))
        for step in steps
    ]).lower()
    
    if any(word in all_descriptions for word in ['process', 'analyze', 'transform', 'generate']):
        requirements['cpu'] = 'medium'
        requirements['memory'] = 'medium'
    
    if any(word in all_descriptions for word in ['file', 'write', 'export', 'save']):
        requirements['disk'] = 'medium'
    
    if any(word in all_descriptions for word in ['api', 'http', 'download', 'upload', 'network']):
        requirements['network'] = True
    
    return requirements


def _assess_execution_feasibility(success_prob: float, risk_factors: List[str], exec_time: float) -> str:
    """Assess overall execution feasibility."""
    if success_prob > 0.9 and len(risk_factors) < 2 and exec_time < 60:
        return 'low_risk'
    elif success_prob > 0.7 and len(risk_factors) < 4 and exec_time < 300:
        return 'medium_risk'
    elif success_prob > 0.5:
        return 'high_risk'
    else:
        return 'very_high_risk'