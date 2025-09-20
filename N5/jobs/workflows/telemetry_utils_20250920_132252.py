#!/usr/bin/env python3
"""
N5 OS Jobs Workflow Telemetry Utilities
Utility functions for telemetry, logging, and workflow tracking.

This module provides reusable utilities for tracking workflow execution,
performance metrics, and error handling across job processing workflows.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class WorkflowTelemetry:
    """
    Centralized telemetry tracking for workflow operations.
    
    Provides structured logging, metrics collection, and performance tracking
    with minimal overhead for production workflows.
    """
    
    def __init__(self, workflow_type: str, workflow_id: Optional[str] = None):
        """
        Initialize telemetry tracker.
        
        Args:
            workflow_type: Type of workflow being tracked (e.g., 'scrape', 'review')
            workflow_id: Optional workflow identifier
        """
        self.workflow_type = workflow_type
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        
        self.telemetry_data = {
            'workflow_type': workflow_type,
            'workflow_id': self.workflow_id,
            'start_time': self.start_time.isoformat() + 'Z',
            'stages': {},
            'metrics': {},
            'errors': [],
            'warnings': [],
            'performance': {}
        }
        
        # Setup logger
        self.logger = logging.getLogger(f'{workflow_type}.{self.workflow_id[:8]}')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def start_stage(self, stage_name: str, metadata: Dict[str, Any] = None) -> None:
        """
        Mark the start of a workflow stage.
        
        Args:
            stage_name: Name of the stage being started
            metadata: Optional metadata for the stage
        """
        stage_data = {
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'status': 'in_progress'
        }
        
        if metadata:
            stage_data['metadata'] = metadata
        
        self.telemetry_data['stages'][stage_name] = stage_data
        self.logger.info(f"Stage started: {stage_name}")
    
    def complete_stage(self, stage_name: str, metrics: Dict[str, Any] = None) -> None:
        """
        Mark the completion of a workflow stage.
        
        Args:
            stage_name: Name of the stage being completed
            metrics: Optional metrics for the completed stage
        """
        if stage_name not in self.telemetry_data['stages']:
            self.logger.warning(f"Attempting to complete untracked stage: {stage_name}")
            return
        
        stage_data = self.telemetry_data['stages'][stage_name]
        stage_data['end_time'] = datetime.utcnow().isoformat() + 'Z'
        stage_data['status'] = 'completed'
        
        # Calculate stage duration
        start_time = datetime.fromisoformat(stage_data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(stage_data['end_time'].replace('Z', '+00:00'))
        stage_data['duration_seconds'] = (end_time - start_time).total_seconds()
        
        if metrics:
            stage_data['metrics'] = metrics
        
        self.logger.info(f"Stage completed: {stage_name} (Duration: {stage_data['duration_seconds']:.2f}s)")
    
    def fail_stage(self, stage_name: str, error: str) -> None:
        """
        Mark a stage as failed.
        
        Args:
            stage_name: Name of the failed stage
            error: Error description
        """
        if stage_name not in self.telemetry_data['stages']:
            self.logger.warning(f"Attempting to fail untracked stage: {stage_name}")
            return
        
        stage_data = self.telemetry_data['stages'][stage_name]
        stage_data['end_time'] = datetime.utcnow().isoformat() + 'Z'
        stage_data['status'] = 'failed'
        stage_data['error'] = error
        
        # Calculate stage duration
        start_time = datetime.fromisoformat(stage_data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(stage_data['end_time'].replace('Z', '+00:00'))
        stage_data['duration_seconds'] = (end_time - start_time).total_seconds()
        
        self.log_error(error, stage_name)
    
    def log_error(self, error: str, context: str = None) -> None:
        """
        Log an error with structured context.
        
        Args:
            error: Error message
            context: Optional context (e.g., stage name)
        """
        error_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': error,
            'context': context,
            'workflow_id': self.workflow_id
        }
        self.telemetry_data['errors'].append(error_entry)
        self.logger.error(f"Error in {context or 'unknown'}: {error}")
    
    def log_warning(self, warning: str, context: str = None) -> None:
        """
        Log a warning with structured context.
        
        Args:
            warning: Warning message
            context: Optional context (e.g., stage name)
        """
        warning_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'warning': warning,
            'context': context,
            'workflow_id': self.workflow_id
        }
        self.telemetry_data['warnings'].append(warning_entry)
        self.logger.warning(f"Warning in {context or 'unknown'}: {warning}")
    
    def record_metric(self, key: str, value: Any, category: str = 'general') -> None:
        """
        Record a custom metric.
        
        Args:
            key: Metric key
            value: Metric value
            category: Metric category for grouping
        """
        if category not in self.telemetry_data['metrics']:
            self.telemetry_data['metrics'][category] = {}
        
        self.telemetry_data['metrics'][category][key] = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def record_performance(self, operation: str, duration_seconds: float, metadata: Dict[str, Any] = None) -> None:
        """
        Record performance data for an operation.
        
        Args:
            operation: Name of the operation
            duration_seconds: Time taken for the operation
            metadata: Optional metadata about the operation
        """
        perf_data = {
            'duration_seconds': duration_seconds,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        if metadata:
            perf_data['metadata'] = metadata
        
        if operation not in self.telemetry_data['performance']:
            self.telemetry_data['performance'][operation] = []
        
        self.telemetry_data['performance'][operation].append(perf_data)
    
    def finalize(self) -> Dict[str, Any]:
        """
        Finalize telemetry data and return complete summary.
        
        Returns:
            Complete telemetry data with summary statistics
        """
        end_time = datetime.utcnow()
        total_duration = (end_time - self.start_time).total_seconds()
        
        self.telemetry_data['end_time'] = end_time.isoformat() + 'Z'
        self.telemetry_data['total_duration_seconds'] = total_duration
        
        # Generate summary statistics
        summary = {
            'total_stages': len(self.telemetry_data['stages']),
            'successful_stages': sum(1 for s in self.telemetry_data['stages'].values() if s.get('status') == 'completed'),
            'failed_stages': sum(1 for s in self.telemetry_data['stages'].values() if s.get('status') == 'failed'),
            'total_errors': len(self.telemetry_data['errors']),
            'total_warnings': len(self.telemetry_data['warnings']),
            'total_duration_seconds': total_duration
        }
        
        self.telemetry_data['summary'] = summary
        
        # Log final summary
        self.logger.info(f"Workflow completed: {self.workflow_type} "
                        f"(Duration: {total_duration:.2f}s, "
                        f"Stages: {summary['successful_stages']}/{summary['total_stages']}, "
                        f"Errors: {summary['total_errors']})")
        
        return self.telemetry_data
    
    def export_telemetry(self, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Export telemetry data to a JSON file.
        
        Args:
            output_path: Optional path to save telemetry data
            
        Returns:
            Path to the saved telemetry file, or None if saving failed
        """
        try:
            if not output_path:
                output_dir = Path('/tmp/n5_telemetry')
                output_dir.mkdir(exist_ok=True)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                output_path = output_dir / f"{self.workflow_type}_{timestamp}_{self.workflow_id[:8]}.json"
            
            with open(output_path, 'w') as f:
                json.dump(self.telemetry_data, f, indent=2)
            
            self.logger.info(f"Telemetry data exported to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export telemetry data: {str(e)}")
            return None


class PerformanceTimer:
    """
    Context manager for timing operations with automatic telemetry recording.
    
    Usage:
        telemetry = WorkflowTelemetry('scrape')
        with PerformanceTimer(telemetry, 'ats_detection'):
            # ... perform ATS detection
            pass
    """
    
    def __init__(self, telemetry: WorkflowTelemetry, operation: str, metadata: Dict[str, Any] = None):
        """
        Initialize performance timer.
        
        Args:
            telemetry: Telemetry instance to record to
            operation: Name of the operation being timed
            metadata: Optional metadata about the operation
        """
        self.telemetry = telemetry
        self.operation = operation
        self.metadata = metadata or {}
        self.start_time = None
    
    def __enter__(self):
        """Start timing the operation."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record the result."""
        if self.start_time:
            duration = time.time() - self.start_time
            
            # Include exception info in metadata if an error occurred
            if exc_type:
                self.metadata['exception_type'] = exc_type.__name__
                self.metadata['exception_message'] = str(exc_val)
                self.metadata['success'] = False
            else:
                self.metadata['success'] = True
            
            self.telemetry.record_performance(self.operation, duration, self.metadata)


# Convenience functions for common telemetry patterns
def create_workflow_telemetry(workflow_type: str, workflow_id: Optional[str] = None) -> WorkflowTelemetry:
    """
    Factory function to create workflow telemetry instance.
    
    Args:
        workflow_type: Type of workflow
        workflow_id: Optional workflow identifier
        
    Returns:
        New WorkflowTelemetry instance
    """
    return WorkflowTelemetry(workflow_type, workflow_id)


def setup_workflow_logging(workflow_type: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Set up standardized logging for a workflow.
    
    Args:
        workflow_type: Type of workflow for logger naming
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(workflow_type)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(getattr(logging, log_level.upper()))
    return logger